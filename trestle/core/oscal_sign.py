# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2024 The OSCAL Compass Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""OSCAL document signing and verification utilities.

This module provides canonicalization (RFC 8785 / JCS-style), signing, and
verification of OSCAL JSON documents via detached signature envelopes.

Supported signing algorithms:
  - ecdsa-p256-sha256  (ECDSA with NIST P-256 and SHA-256)
  - rsa-pss-sha256     (RSA-PSS with SHA-256)

Key formats accepted: PEM-encoded private/public keys (PKCS#8 / SubjectPublicKeyInfo).

Signature envelope format (JSON, written to a .sig file):
    {
      "payload_digest": "sha256:<hexdigest>",
      "signature_algorithm": "ecdsa-p256-sha256",
      "signature": "<base64url-encoded DER signature>",
      "metadata": {
        "tool": "compliance-trestle",
        "tool_version": "...",
        "oscal_model": "<top-level OSCAL model key>",
        "signed_file": "<basename of signed file>",
        "signed_at": "<ISO-8601 UTC timestamp>",
        "signer": "<optional identity string>"
      }
    }
"""

import base64
import datetime
import hashlib
import json
import logging
import pathlib
from typing import Optional, Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives.asymmetric.ec import ECDSA, EllipticCurvePrivateKey, EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

import trestle
from trestle.common.err import TrestleError

logger = logging.getLogger(__name__)

# File suffix appended to the original OSCAL filename to form the default sig path.
SIGNATURE_FILE_SUFFIX = '.sig'

# Algorithm identifiers used in the envelope.
ALG_ECDSA_P256_SHA256 = 'ecdsa-p256-sha256'
ALG_RSA_PSS_SHA256 = 'rsa-pss-sha256'
SUPPORTED_ALGORITHMS = {ALG_ECDSA_P256_SHA256, ALG_RSA_PSS_SHA256}


# ---------------------------------------------------------------------------
# Canonicalization
# ---------------------------------------------------------------------------


def canonicalize_json(data: dict) -> bytes:
    """Return canonical UTF-8 JSON bytes for an OSCAL document.

    Keys are sorted lexicographically at every nesting level and no
    insignificant whitespace is emitted.  This follows the spirit of RFC 8785
    (JSON Canonicalization Scheme) and guarantees that the same logical OSCAL
    document always produces the same byte sequence regardless of key insertion
    order or serialization tool.

    Args:
        data: A Python dict representing a parsed OSCAL JSON document.

    Returns:
        UTF-8-encoded canonical JSON bytes.
    """
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def digest_bytes(data: bytes) -> str:
    """Return a ``sha256:<hexdigest>`` string for *data*.

    Args:
        data: The bytes to hash.

    Returns:
        A string of the form ``sha256:<lowercase hex digest>``.
    """
    return 'sha256:' + hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Key I/O helpers
# ---------------------------------------------------------------------------


def _load_private_key(key_path: pathlib.Path):
    """Load a PEM private key from *key_path* (ECDSA or RSA only).

    Args:
        key_path: Filesystem path to the PEM private key file.

    Returns:
        A ``cryptography`` private key object.

    Raises:
        TrestleError: If the file cannot be read, parsed, or is an unsupported
            key type.
    """
    try:
        pem_data = key_path.read_bytes()
    except OSError as e:
        raise TrestleError(f'Cannot read private key file {key_path}: {e}')

    try:
        private_key = serialization.load_pem_private_key(pem_data, password=None)
    except Exception as e:
        raise TrestleError(f'Failed to parse PEM private key from {key_path}: {e}')

    if not isinstance(private_key, (EllipticCurvePrivateKey, RSAPrivateKey)):
        raise TrestleError(
            f'Unsupported private key type: {type(private_key).__name__}. '
            'Only ECDSA (P-256) and RSA keys are supported.'
        )
    return private_key


def _load_public_key(key_path: pathlib.Path):
    """Load a PEM public key from *key_path* (ECDSA or RSA only).

    Args:
        key_path: Filesystem path to the PEM public key file.

    Returns:
        A ``cryptography`` public key object.

    Raises:
        TrestleError: If the file cannot be read, parsed, or is an unsupported
            key type.
    """
    try:
        pem_data = key_path.read_bytes()
    except OSError as e:
        raise TrestleError(f'Cannot read public key file {key_path}: {e}')

    try:
        public_key = serialization.load_pem_public_key(pem_data)
    except Exception as e:
        raise TrestleError(f'Failed to parse PEM public key from {key_path}: {e}')

    if not isinstance(public_key, (EllipticCurvePublicKey, RSAPublicKey)):
        raise TrestleError(
            f'Unsupported public key type: {type(public_key).__name__}. Only ECDSA and RSA public keys are supported.'
        )
    return public_key


# ---------------------------------------------------------------------------
# Low-level sign / verify
# ---------------------------------------------------------------------------


def _sign_bytes(private_key, data: bytes) -> Tuple[str, str]:
    """Sign *data* with *private_key*.

    Args:
        private_key: A ``cryptography`` private key (ECDSA or RSA).
        data: Raw bytes to sign.

    Returns:
        A ``(algorithm_label, base64url_signature)`` tuple where
        *algorithm_label* is one of :data:`SUPPORTED_ALGORITHMS` and
        *base64url_signature* is the URL-safe base64-encoded signature bytes.
    """
    if isinstance(private_key, EllipticCurvePrivateKey):
        algorithm_label = ALG_ECDSA_P256_SHA256
        sig_bytes = private_key.sign(data, ECDSA(hashes.SHA256()))
    else:
        algorithm_label = ALG_RSA_PSS_SHA256
        sig_bytes = private_key.sign(
            data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256()
        )
    return algorithm_label, base64.urlsafe_b64encode(sig_bytes).decode('ascii')


def _verify_bytes(public_key, data: bytes, signature_b64: str, algorithm_label: str) -> None:
    """Verify *signature_b64* over *data* using *public_key*.

    Args:
        public_key: A ``cryptography`` public key (ECDSA or RSA).
        data: The raw bytes that were signed.
        signature_b64: URL-safe base64-encoded signature.
        algorithm_label: Algorithm identifier string (must be in
            :data:`SUPPORTED_ALGORITHMS`).

    Raises:
        TrestleError: On any verification failure (bad encoding, key type
            mismatch, unsupported algorithm, or invalid signature).
    """
    try:
        sig_bytes = base64.urlsafe_b64decode(signature_b64)
    except Exception as e:
        raise TrestleError(f'Invalid base64url signature encoding: {e}')

    try:
        if algorithm_label == ALG_ECDSA_P256_SHA256:
            if not isinstance(public_key, EllipticCurvePublicKey):
                raise TrestleError(
                    'Key type mismatch: signature used ECDSA but the supplied public key is not an EC key.'
                )
            public_key.verify(sig_bytes, data, ECDSA(hashes.SHA256()))

        elif algorithm_label == ALG_RSA_PSS_SHA256:
            if not isinstance(public_key, RSAPublicKey):
                raise TrestleError(
                    'Key type mismatch: signature used RSA-PSS but the supplied public key is not an RSA key.'
                )
            public_key.verify(
                sig_bytes,
                data,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )

        else:
            raise TrestleError(
                f'Unsupported signing algorithm "{algorithm_label}". '
                f'Supported algorithms: {sorted(SUPPORTED_ALGORITHMS)}'
            )

    except InvalidSignature:
        raise TrestleError(
            'Signature verification FAILED: the signature is invalid or the OSCAL document '
            'has been tampered with since it was signed.'
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def sign_oscal_file(
    oscal_path: pathlib.Path,
    key_path: pathlib.Path,
    sig_path: Optional[pathlib.Path] = None,
    signer: Optional[str] = None,
) -> pathlib.Path:
    """Sign an OSCAL JSON file and write a detached signature envelope.

    The signed file is *not* modified; a companion ``<file>.sig`` file is
    created containing the signature envelope (unless *sig_path* overrides the
    default location).

    Signing procedure:
      1. Parse the OSCAL JSON file into a Python dict.
      2. Canonicalize the dict (stable key ordering, no whitespace).
      3. Hash the canonical bytes with SHA-256.
      4. Sign the canonical bytes with *key_path*.
      5. Write a JSON signature envelope to *sig_path*.

    Args:
        oscal_path: Path to the OSCAL JSON file to sign.
        key_path: Path to the PEM private key file (ECDSA P-256 or RSA).
        sig_path: Destination path for the ``.sig`` file.  Defaults to
            ``<oscal_path>.sig`` (e.g. ``assessment-results.json.sig``).
        signer: Optional human-readable identity string to embed in metadata
            (e.g. ``"ci-pipeline"`` or a user email address).

    Returns:
        The path to the written signature file.

    Raises:
        TrestleError: If any step fails (missing file, bad key, I/O error).
    """
    if not oscal_path.exists():
        raise TrestleError(f'OSCAL file not found: {oscal_path}')

    # Parse OSCAL JSON
    try:
        raw = json.loads(oscal_path.read_bytes())
    except json.JSONDecodeError as e:
        raise TrestleError(f'OSCAL file does not contain valid JSON ({oscal_path}): {e}')

    if not isinstance(raw, dict):
        raise TrestleError(f'OSCAL file root must be a JSON object, got {type(raw).__name__}: {oscal_path}')

    # Canonicalize and hash
    canonical_bytes = canonicalize_json(raw)
    payload_digest = digest_bytes(canonical_bytes)

    # Infer OSCAL model type from the single top-level key (e.g. "catalog")
    oscal_model = next(iter(raw), 'unknown')

    # Sign
    private_key = _load_private_key(key_path)
    algorithm_label, signature_b64 = _sign_bytes(private_key, canonical_bytes)

    # Resolve trestle version
    tool_version = getattr(trestle, '__version__', 'unknown')

    # Build signature envelope
    envelope = {
        'payload_digest': payload_digest,
        'signature_algorithm': algorithm_label,
        'signature': signature_b64,
        'metadata': {
            'tool': 'compliance-trestle',
            'tool_version': tool_version,
            'oscal_model': oscal_model,
            'signed_file': oscal_path.name,
            'signed_at': datetime.datetime.utcnow().isoformat() + 'Z',
            'signer': signer or '',
        },
    }

    if sig_path is None:
        sig_path = pathlib.Path(str(oscal_path) + SIGNATURE_FILE_SUFFIX)

    try:
        sig_path.write_text(json.dumps(envelope, indent=2), encoding='utf-8')
    except OSError as e:
        raise TrestleError(f'Failed to write signature file {sig_path}: {e}')

    logger.info(f'Signed {oscal_path.name} -> {sig_path.name}  [{payload_digest}]')
    return sig_path


def verify_oscal_file(
    oscal_path: pathlib.Path, key_path: pathlib.Path, sig_path: Optional[pathlib.Path] = None
) -> dict:
    """Verify the detached signature on an OSCAL JSON file.

    Verification procedure:
      1. Load the signature envelope from *sig_path*.
      2. Canonicalize the current content of *oscal_path*.
      3. Compare the SHA-256 digest against the envelope's ``payload_digest``.
      4. Cryptographically verify the signature using *key_path*.

    Args:
        oscal_path: Path to the OSCAL JSON file whose signature to verify.
        key_path: Path to the PEM public key file corresponding to the signing
            private key.
        sig_path: Path to the ``.sig`` file.  Defaults to
            ``<oscal_path>.sig``.

    Returns:
        The ``metadata`` dict from the signature envelope (may be empty).

    Raises:
        TrestleError: If verification fails for any reason (missing files, bad
            JSON, digest mismatch, invalid signature, unsupported algorithm).
    """
    if not oscal_path.exists():
        raise TrestleError(f'OSCAL file not found: {oscal_path}')

    if sig_path is None:
        sig_path = pathlib.Path(str(oscal_path) + SIGNATURE_FILE_SUFFIX)

    if not sig_path.exists():
        raise TrestleError(
            f'Signature file not found: {sig_path}. '
            'Use "trestle sign" to create a signature or supply the correct path via --sig.'
        )

    # Load and validate envelope structure
    try:
        envelope = json.loads(sig_path.read_bytes())
    except json.JSONDecodeError as e:
        raise TrestleError(f'Signature file is not valid JSON ({sig_path}): {e}')

    if not isinstance(envelope, dict):
        raise TrestleError(f'Signature envelope root must be a JSON object: {sig_path}')

    for required_field in ('payload_digest', 'signature_algorithm', 'signature'):
        if required_field not in envelope:
            raise TrestleError(f'Signature envelope is missing required field "{required_field}" in {sig_path}.')

    # Canonicalize the current OSCAL content
    try:
        raw = json.loads(oscal_path.read_bytes())
    except json.JSONDecodeError as e:
        raise TrestleError(f'OSCAL file does not contain valid JSON ({oscal_path}): {e}')

    canonical_bytes = canonicalize_json(raw)
    computed_digest = digest_bytes(canonical_bytes)

    # Digest check (fast tamper detection before expensive crypto)
    if computed_digest != envelope['payload_digest']:
        raise TrestleError(
            'Digest mismatch — the OSCAL document has been modified since it was signed.\n'
            f'  Recorded digest : {envelope["payload_digest"]}\n'
            f'  Current digest  : {computed_digest}'
        )

    # Cryptographic signature verification
    public_key = _load_public_key(key_path)
    _verify_bytes(public_key, canonical_bytes, envelope['signature'], envelope['signature_algorithm'])

    logger.info(f'Signature verified successfully for {oscal_path.name}')
    return envelope.get('metadata', {})


def generate_keypair(algorithm: str = ALG_ECDSA_P256_SHA256) -> Tuple[bytes, bytes]:
    """Generate a new keypair and return PEM-encoded (private_key, public_key) bytes.

    This is a convenience helper for testing and bootstrapping.  In production
    environments, key generation and storage should be handled by dedicated
    key-management infrastructure (HSM, KMS, Vault, etc.).

    Args:
        algorithm: One of :data:`SUPPORTED_ALGORITHMS`.  Defaults to
            ``ecdsa-p256-sha256``.

    Returns:
        A ``(private_pem, public_pem)`` byte-string tuple.

    Raises:
        TrestleError: If *algorithm* is not in :data:`SUPPORTED_ALGORITHMS`.
    """
    if algorithm == ALG_ECDSA_P256_SHA256:
        private_key = ec.generate_private_key(ec.SECP256R1())
    elif algorithm == ALG_RSA_PSS_SHA256:
        from cryptography.hazmat.primitives.asymmetric import rsa as _rsa

        private_key = _rsa.generate_private_key(public_exponent=65537, key_size=2048)
    else:
        raise TrestleError(f'Unsupported algorithm "{algorithm}". Supported algorithms: {sorted(SUPPORTED_ALGORITHMS)}')

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_pem, public_pem
