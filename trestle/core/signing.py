# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2026 The OSCAL Compass Authors. All rights reserved.
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
"""Helpers for detached JSON provenance signatures."""

from __future__ import annotations

import base64
import hmac
import json
import pathlib
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives import serialization
from securesystemslib.exceptions import UnverifiedSignatureError, VerificationError
from securesystemslib.signer import CryptoSigner, Key, SSlibKey, Signature, Signer

from trestle.common import const
from trestle.common.err import TrestleError
from trestle.core.canonicalization import canonicalize_json_text, load_canonical_json_file, sha256_digest_hex

DSSE_PAYLOAD_TYPE = 'application/vnd.in-toto+json'
IN_TOTO_STATEMENT_TYPE = 'https://in-toto.io/Statement/v1'
OSCAL_PREDICATE_TYPE = 'https://oscal-compass.github.io/compliance-trestle/predicates/oscal-signing/v1'
CANONICALIZATION_ALGORITHM = 'RFC8785'
DIGEST_ALGORITHM = 'sha256'
DIGEST_SOURCE = 'canonical-json'
MAX_SIGNATURES = 16


def _validate_json_path(path: pathlib.Path) -> None:
    if path.suffix.lower() != '.json':
        raise TrestleError('Signing is only supported for JSON files.')


def load_pem_private_key_signer(path: pathlib.Path, password: Optional[str] = None) -> Signer:
    """Load a local PEM private key as a securesystemslib signer."""
    password_bytes = password.encode(const.FILE_ENCODING) if password is not None else None
    try:
        private_key = serialization.load_pem_private_key(path.read_bytes(), password=password_bytes)
        return CryptoSigner(private_key)
    except Exception as error:
        raise TrestleError(f'Unable to load private key for signing: {path}') from error


def load_pem_public_key(path: pathlib.Path) -> Key:
    """Load a local PEM public key as a securesystemslib key."""
    try:
        public_key = serialization.load_pem_public_key(path.read_bytes())
        return SSlibKey.from_crypto(public_key)
    except Exception as error:
        raise TrestleError(f'Unable to load public key for verification: {path}') from error


def build_in_toto_statement(subject_name: str, digest: str) -> Dict[str, Any]:
    """Build the in-toto Statement payload for a JSON artifact digest."""
    return {
        '_type': IN_TOTO_STATEMENT_TYPE,
        'subject': [{'name': subject_name, 'digest': {DIGEST_ALGORITHM: digest}}],
        'predicateType': OSCAL_PREDICATE_TYPE,
        'predicate': {
            'canonicalization': CANONICALIZATION_ALGORITHM,
            'digestAlgorithm': DIGEST_ALGORITHM,
            'digestSource': DIGEST_SOURCE,
            'tool': 'compliance-trestle',
        },
    }


def dsse_pae(payload_type: str, payload: bytes) -> bytes:
    """Return DSSE pre-authentication encoding for a payload type and payload."""
    payload_type_bytes = payload_type.encode(const.FILE_ENCODING)
    return b' '.join(
        [
            b'DSSEv1',
            str(len(payload_type_bytes)).encode(const.FILE_ENCODING),
            payload_type_bytes,
            str(len(payload)).encode(const.FILE_ENCODING),
            payload,
        ]
    )


def create_oscal_provenance_envelope(
    input_path: pathlib.Path, signer: Signer, subject_name: Optional[str] = None
) -> Dict[str, Any]:
    """Create a DSSE envelope whose payload is an in-toto Statement for a JSON file."""
    _validate_json_path(input_path)
    _, canonical_bytes = load_canonical_json_file(input_path)
    digest = sha256_digest_hex(canonical_bytes)
    statement = build_in_toto_statement(subject_name or input_path.name, digest)
    return sign_in_toto_statement(statement, signer)


def sign_in_toto_statement(statement: Dict[str, Any], signer: Signer) -> Dict[str, Any]:
    """Sign an in-toto Statement as a DSSE envelope."""
    payload = _json_bytes(statement)
    signature = signer.sign(dsse_pae(DSSE_PAYLOAD_TYPE, payload))
    return {
        'payload': _b64_encode(payload),
        'payloadType': DSSE_PAYLOAD_TYPE,
        'signatures': [_dsse_signature(signature)],
    }


def write_dsse_envelope(envelope: Dict[str, Any], output_path: pathlib.Path) -> None:
    """Write a DSSE envelope as JSON."""
    if output_path.is_symlink():
        raise TrestleError(f'DSSE output path must not be a symlink: {output_path}')
    if output_path.exists():
        if output_path.is_dir():
            raise TrestleError(f'DSSE output path is a directory: {output_path}')
        raise TrestleError(f'DSSE output path already exists: {output_path}')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('x', encoding=const.FILE_ENCODING) as write_file:
        write_file.write(json.dumps(envelope, indent=2, sort_keys=True) + '\n')


def load_dsse_envelope(envelope_path: pathlib.Path) -> Dict[str, Any]:
    """Load a DSSE envelope from JSON."""
    envelope, _ = canonicalize_json_text(envelope_path.read_text(encoding=const.FILE_ENCODING))

    if not isinstance(envelope, dict):
        raise TrestleError('DSSE envelope must be a JSON object.')
    return envelope


def verify_oscal_provenance_envelope(
    input_path: pathlib.Path, envelope: Dict[str, Any], public_key: Key, subject_name: Optional[str] = None
) -> Dict[str, Any]:
    """Verify a DSSE in-toto Statement envelope against a JSON file."""
    _validate_json_path(input_path)
    _, canonical_bytes = load_canonical_json_file(input_path)
    expected_digest = sha256_digest_hex(canonical_bytes)
    payload = _verified_payload(envelope, public_key)
    statement = _load_statement(payload)
    _validate_statement(statement, subject_name or input_path.name, expected_digest)
    return statement


def verify_dsse_payload(envelope: Dict[str, Any], public_key: Key) -> bytes:
    """Verify a DSSE envelope signature and return its payload bytes."""
    return _verified_payload(envelope, public_key)


def load_in_toto_statement(payload: bytes) -> Dict[str, Any]:
    """Load a verified DSSE payload as an in-toto Statement object."""
    return _load_statement(payload)


def _verified_payload(envelope: Dict[str, Any], public_key: Key) -> bytes:
    payload_type = envelope.get('payloadType')
    if payload_type != DSSE_PAYLOAD_TYPE:
        raise TrestleError(f'Unsupported DSSE payload type: {payload_type}')

    payload = _b64_decode(envelope.get('payload'), 'payload')
    pae = dsse_pae(payload_type, payload)
    signatures = envelope.get('signatures')
    if not isinstance(signatures, list) or not signatures:
        raise TrestleError('DSSE envelope must contain at least one signature.')
    if len(signatures) > MAX_SIGNATURES:
        raise TrestleError(f'DSSE envelope contains more than {MAX_SIGNATURES} signatures.')

    verification_errors: List[str] = []
    for signature_entry in signatures:
        try:
            signature = _signature_from_dsse(signature_entry, public_key.keyid)
            public_key.verify_signature(signature, pae)
            return payload
        except (TrestleError, UnverifiedSignatureError, VerificationError) as error:
            verification_errors.append(str(error))

    raise TrestleError(f'DSSE envelope signature could not be verified: {"; ".join(verification_errors)}')


def _load_statement(payload: bytes) -> Dict[str, Any]:
    try:
        statement, _ = canonicalize_json_text(payload.decode(const.FILE_ENCODING))
    except UnicodeDecodeError as error:
        raise TrestleError(f'DSSE payload is not a valid JSON in-toto Statement: {error}') from error

    if not isinstance(statement, dict):
        raise TrestleError('DSSE payload must be a JSON in-toto Statement object.')
    return statement


def _validate_statement(statement: Dict[str, Any], subject_name: str, expected_digest: str) -> None:
    if statement.get('_type') != IN_TOTO_STATEMENT_TYPE:
        raise TrestleError('DSSE payload is not an in-toto Statement v1.')
    if statement.get('predicateType') != OSCAL_PREDICATE_TYPE:
        raise TrestleError(f'Unsupported in-toto predicate type: {statement.get("predicateType")}')

    predicate = statement.get('predicate')
    if not isinstance(predicate, dict):
        raise TrestleError('in-toto Statement predicate must be a JSON object.')
    if predicate.get('canonicalization') != CANONICALIZATION_ALGORITHM:
        raise TrestleError('in-toto Statement does not describe RFC 8785 canonicalization.')
    if predicate.get('digestAlgorithm') != DIGEST_ALGORITHM:
        raise TrestleError('in-toto Statement does not describe a SHA-256 digest.')
    if predicate.get('digestSource') != DIGEST_SOURCE:
        raise TrestleError('in-toto Statement does not describe a canonical JSON digest source.')

    subjects = statement.get('subject')
    if not isinstance(subjects, list):
        raise TrestleError('in-toto Statement subject must be an array.')
    if len(subjects) != 1:
        raise TrestleError('in-toto Statement must contain exactly one subject for JSON signing.')

    subject = subjects[0]
    if not isinstance(subject, dict):
        raise TrestleError(f'in-toto Statement does not contain expected subject: {subject_name}')

    actual_subject_name = subject.get('name')
    if actual_subject_name != subject_name:
        if isinstance(actual_subject_name, str):
            raise TrestleError(
                f'in-toto Statement does not contain expected subject: {subject_name}. '
                f'Found subject: {actual_subject_name}. '
                'If signing used --subject-name, pass the same value during verification.'
            )
        raise TrestleError(f'in-toto Statement does not contain expected subject: {subject_name}')

    digest = subject.get('digest')
    if not isinstance(digest, dict):
        raise TrestleError(f'in-toto Statement subject does not contain a digest for: {subject_name}')
    if hmac.compare_digest(str(digest.get(DIGEST_ALGORITHM)), expected_digest):
        return

    raise TrestleError(f'in-toto Statement digest does not match JSON file: {subject_name}')


def _json_bytes(value: Dict[str, Any]) -> bytes:
    return json.dumps(value, separators=(',', ':'), sort_keys=True).encode(const.FILE_ENCODING)


def _dsse_signature(signature: Signature) -> Dict[str, str]:
    return {'keyid': signature.keyid, 'sig': _b64_encode(bytes.fromhex(signature.signature))}


def _signature_from_dsse(signature_entry: Any, verification_keyid: str = '') -> Signature:
    if not isinstance(signature_entry, dict):
        raise TrestleError('DSSE signature entry must be a JSON object.')
    if 'keyid' in signature_entry and not isinstance(signature_entry['keyid'], str):
        raise TrestleError('DSSE signature entry keyid must be a string.')
    return Signature(verification_keyid, _b64_decode(signature_entry.get('sig'), 'signature sig').hex())


def _b64_encode(data: bytes) -> str:
    return base64.b64encode(data).decode('ascii')


def _b64_decode(value: Any, field_name: str) -> bytes:
    if not isinstance(value, str):
        raise TrestleError(f'DSSE {field_name} must be a base64 string.')
    try:
        encoded = value.encode('ascii')
    except UnicodeEncodeError as error:
        raise TrestleError(f'DSSE {field_name} is not valid base64.') from error

    try:
        return base64.b64decode(encoded, validate=True)
    except Exception:
        try:
            return base64.b64decode(encoded, altchars=b'-_', validate=True)
        except Exception as error:
            raise TrestleError(f'DSSE {field_name} is not valid base64.') from error
