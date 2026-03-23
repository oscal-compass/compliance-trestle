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
"""Tests for OSCAL signing, verification, and canonicalization.

Covers:
- trestle.core.oscal_sign (unit tests for each utility function)
- trestle sign  CLI command (happy path + error paths)
- trestle verify CLI command (happy path + error paths)
"""

import json
import pathlib
import sys

from _pytest.monkeypatch import MonkeyPatch

import pytest

from trestle.cli import Trestle
from trestle.common.err import TrestleError
from trestle.core import oscal_sign
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.oscal_sign import (
    ALG_ECDSA_P256_SHA256,
    ALG_RSA_PSS_SHA256,
    SIGNATURE_FILE_SUFFIX,
    canonicalize_json,
    digest_bytes,
    generate_keypair,
    sign_oscal_file,
    verify_oscal_file,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope='module')
def ecdsa_keypair(tmp_path_factory):
    """Return (private_pem, public_pem) byte strings for an ECDSA P-256 key pair."""
    priv, pub = generate_keypair(ALG_ECDSA_P256_SHA256)
    return priv, pub


@pytest.fixture(scope='module')
def rsa_keypair(tmp_path_factory):
    """Return (private_pem, public_pem) byte strings for an RSA-PSS 2048-bit key pair."""
    priv, pub = generate_keypair(ALG_RSA_PSS_SHA256)
    return priv, pub


@pytest.fixture()
def minimal_catalog_path(tmp_path) -> pathlib.Path:
    """Write a minimal OSCAL catalog JSON file and return its path."""
    catalog = {
        'catalog': {
            'uuid': 'f66ded6b-1234-5678-abcd-000000000001',
            'metadata': {
                'title': 'Test Catalog',
                'last-modified': '2024-01-01T00:00:00Z',
                'version': '1.0.0',
                'oscal-version': '1.1.2',
            },
        }
    }
    path = tmp_path / 'catalog.json'
    path.write_text(json.dumps(catalog), encoding='utf-8')
    return path


@pytest.fixture()
def ecdsa_key_files(tmp_path, ecdsa_keypair):
    """Write ECDSA key pair to PEM files and return (private_path, public_path)."""
    priv_pem, pub_pem = ecdsa_keypair
    priv_path = tmp_path / 'private.pem'
    pub_path = tmp_path / 'public.pem'
    priv_path.write_bytes(priv_pem)
    pub_path.write_bytes(pub_pem)
    return priv_path, pub_path


@pytest.fixture()
def rsa_key_files(tmp_path, rsa_keypair):
    """Write RSA key pair to PEM files and return (private_path, public_path)."""
    priv_pem, pub_pem = rsa_keypair
    priv_path = tmp_path / 'rsa_private.pem'
    pub_path = tmp_path / 'rsa_public.pem'
    priv_path.write_bytes(priv_pem)
    pub_path.write_bytes(pub_pem)
    return priv_path, pub_path


# ---------------------------------------------------------------------------
# canonicalize_json
# ---------------------------------------------------------------------------


class TestCanonicalizeJson:
    """Unit tests for canonicalize_json()."""

    def test_stable_key_ordering(self):
        """Keys must be sorted; different insertion orders yield identical bytes."""
        a = canonicalize_json({'z': 1, 'a': 2, 'm': 3})
        b = canonicalize_json({'m': 3, 'a': 2, 'z': 1})
        assert a == b

    def test_no_whitespace(self):
        """Output must contain no insignificant whitespace."""
        result = canonicalize_json({'key': 'value', 'num': 42})
        text = result.decode('utf-8')
        assert ' ' not in text
        assert '\n' not in text

    def test_nested_objects_sorted(self):
        """Nested object keys must also be sorted."""
        data = {'b': {'z': 1, 'a': 2}, 'a': {'z': 3, 'a': 4}}
        canonical = canonicalize_json(data).decode('utf-8')
        obj = json.loads(canonical)
        assert list(obj.keys()) == ['a', 'b']
        assert list(obj['a'].keys()) == ['a', 'z']
        assert list(obj['b'].keys()) == ['a', 'z']

    def test_utf8_encoding(self):
        """Non-ASCII characters must be preserved as UTF-8 (not escaped)."""
        data = {'title': 'Ünïcödé'}
        result = canonicalize_json(data)
        assert 'Ünïcödé'.encode() in result

    def test_empty_object(self):
        """Empty object canonicalizes to ``{}``."""
        assert canonicalize_json({}) == b'{}'

    def test_idempotent(self):
        """Canonicalizing twice gives the same result."""
        data = {'catalog': {'uuid': 'abc', 'metadata': {'title': 'X'}}}
        first = canonicalize_json(data)
        second = canonicalize_json(json.loads(first))
        assert first == second


# ---------------------------------------------------------------------------
# digest_bytes
# ---------------------------------------------------------------------------


class TestDigestBytes:
    """Unit tests for digest_bytes()."""

    def test_format(self):
        """Output must be prefixed with ``sha256:``."""
        result = digest_bytes(b'hello')
        assert result.startswith('sha256:')

    def test_known_value(self):
        """SHA-256 of b'' is the well-known empty-string digest."""
        empty_sha256 = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
        assert digest_bytes(b'') == f'sha256:{empty_sha256}'

    def test_deterministic(self):
        """Same input always yields the same digest."""
        d1 = digest_bytes(b'test')
        d2 = digest_bytes(b'test')
        assert d1 == d2

    def test_distinct_inputs(self):
        """Different inputs must yield different digests."""
        assert digest_bytes(b'a') != digest_bytes(b'b')


# ---------------------------------------------------------------------------
# generate_keypair
# ---------------------------------------------------------------------------


class TestGenerateKeypair:
    """Unit tests for generate_keypair()."""

    def test_generates_ecdsa_pem(self):
        """ECDSA keypair PEM bytes start with expected headers."""
        priv, pub = generate_keypair(ALG_ECDSA_P256_SHA256)
        assert b'BEGIN PRIVATE KEY' in priv
        assert b'BEGIN PUBLIC KEY' in pub

    def test_generates_rsa_pem(self):
        """RSA keypair PEM bytes start with expected headers."""
        priv, pub = generate_keypair(ALG_RSA_PSS_SHA256)
        assert b'BEGIN PRIVATE KEY' in priv
        assert b'BEGIN PUBLIC KEY' in pub

    def test_unsupported_algorithm_raises(self):
        """Unsupported algorithm label must raise TrestleError."""
        with pytest.raises(TrestleError, match='Unsupported algorithm'):
            generate_keypair('ed25519')

    def test_keypairs_are_unique(self):
        """Two generate_keypair calls must yield different keys."""
        priv1, _ = generate_keypair(ALG_ECDSA_P256_SHA256)
        priv2, _ = generate_keypair(ALG_ECDSA_P256_SHA256)
        assert priv1 != priv2


# ---------------------------------------------------------------------------
# sign_oscal_file / verify_oscal_file (unit)
# ---------------------------------------------------------------------------


class TestSignOscalFile:
    """Unit tests for sign_oscal_file()."""

    def test_creates_sig_file_default_path(self, minimal_catalog_path, ecdsa_key_files):
        """Default .sig path is <oscal_path>.sig."""
        priv, _ = ecdsa_key_files
        sig = sign_oscal_file(minimal_catalog_path, priv)
        expected = pathlib.Path(str(minimal_catalog_path) + SIGNATURE_FILE_SUFFIX)
        assert sig == expected
        assert sig.exists()

    def test_creates_sig_file_custom_path(self, minimal_catalog_path, ecdsa_key_files, tmp_path):
        """Custom sig_path is honoured."""
        priv, _ = ecdsa_key_files
        custom = tmp_path / 'my_custom.sig'
        sig = sign_oscal_file(minimal_catalog_path, priv, sig_path=custom)
        assert sig == custom
        assert custom.exists()

    def test_sig_envelope_structure(self, minimal_catalog_path, ecdsa_key_files):
        """Signature envelope must contain required fields."""
        priv, _ = ecdsa_key_files
        sig_path = sign_oscal_file(minimal_catalog_path, priv)
        envelope = json.loads(sig_path.read_text(encoding='utf-8'))
        assert 'payload_digest' in envelope
        assert 'signature_algorithm' in envelope
        assert 'signature' in envelope
        assert 'metadata' in envelope

    def test_sig_algorithm_label_ecdsa(self, minimal_catalog_path, ecdsa_key_files):
        """ECDSA key produces ecdsa-p256-sha256 algorithm label."""
        priv, _ = ecdsa_key_files
        sig_path = sign_oscal_file(minimal_catalog_path, priv)
        envelope = json.loads(sig_path.read_text(encoding='utf-8'))
        assert envelope['signature_algorithm'] == ALG_ECDSA_P256_SHA256

    def test_sig_algorithm_label_rsa(self, minimal_catalog_path, rsa_key_files):
        """RSA key produces rsa-pss-sha256 algorithm label."""
        priv, _ = rsa_key_files
        sig_path = sign_oscal_file(minimal_catalog_path, priv)
        envelope = json.loads(sig_path.read_text(encoding='utf-8'))
        assert envelope['signature_algorithm'] == ALG_RSA_PSS_SHA256

    def test_metadata_fields_populated(self, minimal_catalog_path, ecdsa_key_files):
        """Signature metadata must include tool, oscal_model, signed_at."""
        priv, _ = ecdsa_key_files
        sig_path = sign_oscal_file(minimal_catalog_path, priv, signer='test-signer')
        meta = json.loads(sig_path.read_text(encoding='utf-8'))['metadata']
        assert meta['tool'] == 'compliance-trestle'
        assert meta['oscal_model'] == 'catalog'
        assert meta['signed_at'].endswith('Z')
        assert meta['signer'] == 'test-signer'
        assert meta['signed_file'] == minimal_catalog_path.name

    def test_oscal_file_unmodified_after_sign(self, minimal_catalog_path, ecdsa_key_files):
        """Signing must NOT modify the original OSCAL file."""
        priv, _ = ecdsa_key_files
        original_bytes = minimal_catalog_path.read_bytes()
        sign_oscal_file(minimal_catalog_path, priv)
        assert minimal_catalog_path.read_bytes() == original_bytes

    def test_missing_oscal_file_raises(self, tmp_path, ecdsa_key_files):
        """Missing OSCAL file must raise TrestleError."""
        priv, _ = ecdsa_key_files
        with pytest.raises(TrestleError, match='not found'):
            sign_oscal_file(tmp_path / 'nonexistent.json', priv)

    def test_missing_key_file_raises(self, minimal_catalog_path, tmp_path):
        """Missing private key file must raise TrestleError."""
        with pytest.raises(TrestleError, match='Cannot read private key file'):
            sign_oscal_file(minimal_catalog_path, tmp_path / 'nope.pem')

    def test_invalid_json_raises(self, tmp_path, ecdsa_key_files):
        """Non-JSON OSCAL file must raise TrestleError."""
        priv, _ = ecdsa_key_files
        bad = tmp_path / 'bad.json'
        bad.write_text('not json', encoding='utf-8')
        with pytest.raises(TrestleError, match='valid JSON'):
            sign_oscal_file(bad, priv)

    def test_invalid_key_raises(self, minimal_catalog_path, tmp_path):
        """Corrupt PEM data must raise TrestleError."""
        bad_key = tmp_path / 'bad.pem'
        bad_key.write_bytes(b'-----BEGIN PRIVATE KEY-----\ngarbage\n-----END PRIVATE KEY-----\n')
        with pytest.raises(TrestleError, match='Failed to parse PEM private key'):
            sign_oscal_file(minimal_catalog_path, bad_key)


class TestVerifyOscalFile:
    """Unit tests for verify_oscal_file()."""

    def test_valid_ecdsa_signature(self, minimal_catalog_path, ecdsa_key_files):
        """Valid ECDSA signature must verify without error."""
        priv, pub = ecdsa_key_files
        sig_path = sign_oscal_file(minimal_catalog_path, priv)
        meta = verify_oscal_file(minimal_catalog_path, pub, sig_path=sig_path)
        assert isinstance(meta, dict)
        assert meta['oscal_model'] == 'catalog'

    def test_valid_rsa_signature(self, minimal_catalog_path, rsa_key_files):
        """Valid RSA-PSS signature must verify without error."""
        priv, pub = rsa_key_files
        sig_path = sign_oscal_file(minimal_catalog_path, priv)
        meta = verify_oscal_file(minimal_catalog_path, pub, sig_path=sig_path)
        assert isinstance(meta, dict)

    def test_tampered_document_raises(self, minimal_catalog_path, ecdsa_key_files):
        """Modifying the OSCAL file after signing must trigger a digest mismatch error."""
        priv, pub = ecdsa_key_files
        sig_path = sign_oscal_file(minimal_catalog_path, priv)
        # Tamper: change a field in the OSCAL file
        data = json.loads(minimal_catalog_path.read_text(encoding='utf-8'))
        data['catalog']['metadata']['title'] = 'TAMPERED'
        minimal_catalog_path.write_text(json.dumps(data), encoding='utf-8')

        with pytest.raises(TrestleError, match='Digest mismatch'):
            verify_oscal_file(minimal_catalog_path, pub, sig_path=sig_path)

    def test_wrong_public_key_raises(self, minimal_catalog_path, ecdsa_key_files, tmp_path):
        """A different ECDSA key must fail signature verification."""
        priv, _ = ecdsa_key_files
        sig_path = sign_oscal_file(minimal_catalog_path, priv)

        # Generate a different key pair
        _, different_pub_pem = generate_keypair(ALG_ECDSA_P256_SHA256)
        different_pub = tmp_path / 'different_public.pem'
        different_pub.write_bytes(different_pub_pem)

        with pytest.raises(TrestleError, match='Signature verification FAILED'):
            verify_oscal_file(minimal_catalog_path, different_pub, sig_path=sig_path)

    def test_missing_oscal_file_raises(self, tmp_path, ecdsa_key_files):
        """Missing OSCAL file must raise TrestleError."""
        _, pub = ecdsa_key_files
        with pytest.raises(TrestleError, match='not found'):
            verify_oscal_file(tmp_path / 'ghost.json', pub)

    def test_missing_sig_file_raises(self, minimal_catalog_path, ecdsa_key_files):
        """Missing .sig file must raise TrestleError with helpful message."""
        _, pub = ecdsa_key_files
        with pytest.raises(TrestleError, match='Signature file not found'):
            verify_oscal_file(minimal_catalog_path, pub)

    def test_missing_public_key_raises(self, minimal_catalog_path, ecdsa_key_files, tmp_path):
        """Missing public key file must raise TrestleError."""
        priv, _ = ecdsa_key_files
        sig_path = sign_oscal_file(minimal_catalog_path, priv)
        with pytest.raises(TrestleError, match='Cannot read public key file'):
            verify_oscal_file(minimal_catalog_path, tmp_path / 'missing.pem', sig_path=sig_path)

    def test_malformed_sig_file_raises(self, minimal_catalog_path, ecdsa_key_files, tmp_path):
        """Non-JSON .sig file must raise TrestleError."""
        _, pub = ecdsa_key_files
        bad_sig = tmp_path / 'bad.sig'
        bad_sig.write_text('this is not json', encoding='utf-8')
        with pytest.raises(TrestleError, match='not valid JSON'):
            verify_oscal_file(minimal_catalog_path, pub, sig_path=bad_sig)

    def test_missing_required_envelope_field_raises(self, minimal_catalog_path, ecdsa_key_files, tmp_path):
        """Sig file missing a required field must raise TrestleError."""
        _, pub = ecdsa_key_files
        incomplete_sig = tmp_path / 'incomplete.sig'
        incomplete_sig.write_text(json.dumps({'payload_digest': 'sha256:abc'}), encoding='utf-8')
        with pytest.raises(TrestleError, match='missing required field'):
            verify_oscal_file(minimal_catalog_path, pub, sig_path=incomplete_sig)

    def test_cross_algorithm_key_type_mismatch_raises(self, minimal_catalog_path, ecdsa_key_files, rsa_key_files):
        """Attempting to verify an ECDSA signature with an RSA public key must fail."""
        ecdsa_priv, _ = ecdsa_key_files
        _, rsa_pub = rsa_key_files
        sig_path = sign_oscal_file(minimal_catalog_path, ecdsa_priv)
        with pytest.raises(TrestleError):
            verify_oscal_file(minimal_catalog_path, rsa_pub, sig_path=sig_path)

    def test_default_sig_path_convention(self, minimal_catalog_path, ecdsa_key_files):
        """Default sig path is <oscal_path>.sig; verify picks it up automatically."""
        priv, pub = ecdsa_key_files
        sign_oscal_file(minimal_catalog_path, priv)  # writes <path>.sig by default
        # verify without explicit sig_path — must find it automatically
        meta = verify_oscal_file(minimal_catalog_path, pub)
        assert meta['oscal_model'] == 'catalog'

    def test_sign_verify_roundtrip_preserves_metadata(self, minimal_catalog_path, ecdsa_key_files):
        """Metadata returned by verify must match what was written during sign."""
        priv, pub = ecdsa_key_files
        sig_path = sign_oscal_file(minimal_catalog_path, priv, signer='roundtrip-test')
        meta = verify_oscal_file(minimal_catalog_path, pub, sig_path=sig_path)
        assert meta['signer'] == 'roundtrip-test'
        assert meta['tool'] == 'compliance-trestle'
        assert meta['signed_file'] == minimal_catalog_path.name


# ---------------------------------------------------------------------------
# CLI integration tests — trestle sign
# ---------------------------------------------------------------------------


class TestSignCmd:
    """Integration tests for the ``trestle sign`` CLI command."""

    def test_sign_cmd_happy_path_ecdsa(self, tmp_path, minimal_catalog_path, ecdsa_key_files, monkeypatch):
        """``trestle sign`` exits 0 and creates a .sig file."""
        priv, _ = ecdsa_key_files
        expected_sig = pathlib.Path(str(minimal_catalog_path) + SIGNATURE_FILE_SUFFIX)

        args = ['trestle', 'sign', '-f', str(minimal_catalog_path), '-k', str(priv)]
        monkeypatch.setattr(sys, 'argv', args)
        rc = Trestle().run()
        assert rc == CmdReturnCodes.SUCCESS.value
        assert expected_sig.exists()

    def test_sign_cmd_happy_path_rsa(self, tmp_path, minimal_catalog_path, rsa_key_files, monkeypatch):
        """``trestle sign`` works with RSA keys."""
        priv, _ = rsa_key_files
        args = ['trestle', 'sign', '-f', str(minimal_catalog_path), '-k', str(priv)]
        monkeypatch.setattr(sys, 'argv', args)
        rc = Trestle().run()
        assert rc == CmdReturnCodes.SUCCESS.value

    def test_sign_cmd_custom_output(self, tmp_path, minimal_catalog_path, ecdsa_key_files, monkeypatch):
        """``-o`` flag controls where the .sig file is written."""
        priv, _ = ecdsa_key_files
        custom_sig = tmp_path / 'custom_output.sig'
        args = ['trestle', 'sign', '-f', str(minimal_catalog_path), '-k', str(priv), '-o', str(custom_sig)]
        monkeypatch.setattr(sys, 'argv', args)
        rc = Trestle().run()
        assert rc == CmdReturnCodes.SUCCESS.value
        assert custom_sig.exists()

    def test_sign_cmd_with_signer(self, tmp_path, minimal_catalog_path, ecdsa_key_files, monkeypatch):
        """``--signer`` is embedded in the signature envelope metadata."""
        priv, _ = ecdsa_key_files
        custom_sig = tmp_path / 'with_signer.sig'
        args = [
            'trestle',
            'sign',
            '-f',
            str(minimal_catalog_path),
            '-k',
            str(priv),
            '-o',
            str(custom_sig),
            '--signer',
            'ci-pipeline',
        ]
        monkeypatch.setattr(sys, 'argv', args)
        rc = Trestle().run()
        assert rc == CmdReturnCodes.SUCCESS.value
        envelope = json.loads(custom_sig.read_text(encoding='utf-8'))
        assert envelope['metadata']['signer'] == 'ci-pipeline'

    def test_sign_cmd_missing_file(self, tmp_path, ecdsa_key_files, monkeypatch):
        """Non-existent OSCAL file must cause a non-zero exit code."""
        priv, _ = ecdsa_key_files
        args = ['trestle', 'sign', '-f', str(tmp_path / 'ghost.json'), '-k', str(priv)]
        monkeypatch.setattr(sys, 'argv', args)
        rc = Trestle().run()
        assert rc != CmdReturnCodes.SUCCESS.value

    def test_sign_cmd_missing_key(self, tmp_path, minimal_catalog_path, monkeypatch):
        """Non-existent private key must cause a non-zero exit code."""
        args = ['trestle', 'sign', '-f', str(minimal_catalog_path), '-k', str(tmp_path / 'nope.pem')]
        monkeypatch.setattr(sys, 'argv', args)
        rc = Trestle().run()
        assert rc != CmdReturnCodes.SUCCESS.value


# ---------------------------------------------------------------------------
# CLI integration tests — trestle verify
# ---------------------------------------------------------------------------


class TestVerifyCmd:
    """Integration tests for the ``trestle verify`` CLI command."""

    def test_verify_cmd_happy_path_ecdsa(self, tmp_path, minimal_catalog_path, ecdsa_key_files, monkeypatch):
        """Valid signature verifies and exits 0."""
        priv, pub = ecdsa_key_files
        sign_oscal_file(minimal_catalog_path, priv)

        args = ['trestle', 'verify', '-f', str(minimal_catalog_path), '-k', str(pub)]
        monkeypatch.setattr(sys, 'argv', args)
        rc = Trestle().run()
        assert rc == CmdReturnCodes.SUCCESS.value

    def test_verify_cmd_happy_path_rsa(self, tmp_path, minimal_catalog_path, rsa_key_files, monkeypatch):
        """Valid RSA-PSS signature verifies and exits 0."""
        priv, pub = rsa_key_files
        sign_oscal_file(minimal_catalog_path, priv)

        args = ['trestle', 'verify', '-f', str(minimal_catalog_path), '-k', str(pub)]
        monkeypatch.setattr(sys, 'argv', args)
        rc = Trestle().run()
        assert rc == CmdReturnCodes.SUCCESS.value

    def test_verify_cmd_explicit_sig_path(self, tmp_path, minimal_catalog_path, ecdsa_key_files, monkeypatch):
        """``-s`` flag can be used to specify the .sig path explicitly."""
        priv, pub = ecdsa_key_files
        custom_sig = tmp_path / 'explicit.sig'
        sign_oscal_file(minimal_catalog_path, priv, sig_path=custom_sig)

        args = ['trestle', 'verify', '-f', str(minimal_catalog_path), '-k', str(pub), '-s', str(custom_sig)]
        monkeypatch.setattr(sys, 'argv', args)
        rc = Trestle().run()
        assert rc == CmdReturnCodes.SUCCESS.value

    def test_verify_cmd_tampered_document(self, tmp_path, minimal_catalog_path, ecdsa_key_files, monkeypatch):
        """Modified OSCAL document must cause verification failure (non-zero exit)."""
        priv, pub = ecdsa_key_files
        sign_oscal_file(minimal_catalog_path, priv)

        # Tamper after signing
        data = json.loads(minimal_catalog_path.read_text(encoding='utf-8'))
        data['catalog']['metadata']['title'] = 'TAMPERED'
        minimal_catalog_path.write_text(json.dumps(data), encoding='utf-8')

        args = ['trestle', 'verify', '-f', str(minimal_catalog_path), '-k', str(pub)]
        monkeypatch.setattr(sys, 'argv', args)
        rc = Trestle().run()
        assert rc != CmdReturnCodes.SUCCESS.value

    def test_verify_cmd_no_sig_file(self, tmp_path, minimal_catalog_path, ecdsa_key_files, monkeypatch):
        """Missing .sig file must cause non-zero exit."""
        _, pub = ecdsa_key_files
        args = ['trestle', 'verify', '-f', str(minimal_catalog_path), '-k', str(pub)]
        monkeypatch.setattr(sys, 'argv', args)
        rc = Trestle().run()
        assert rc != CmdReturnCodes.SUCCESS.value

    def test_verify_cmd_wrong_key(self, tmp_path, minimal_catalog_path, ecdsa_key_files, monkeypatch):
        """Wrong public key must cause non-zero exit."""
        priv, _ = ecdsa_key_files
        sign_oscal_file(minimal_catalog_path, priv)

        wrong_priv_pem, wrong_pub_pem = generate_keypair(ALG_ECDSA_P256_SHA256)
        wrong_pub = tmp_path / 'wrong_pub.pem'
        wrong_pub.write_bytes(wrong_pub_pem)

        args = ['trestle', 'verify', '-f', str(minimal_catalog_path), '-k', str(wrong_pub)]
        monkeypatch.setattr(sys, 'argv', args)
        rc = Trestle().run()
        assert rc != CmdReturnCodes.SUCCESS.value

    def test_sign_then_verify_full_roundtrip(self, tmp_path, minimal_catalog_path, ecdsa_key_files, monkeypatch):
        """Full sign → verify round-trip succeeds end-to-end via CLI."""
        priv, pub = ecdsa_key_files

        sign_args = ['trestle', 'sign', '-f', str(minimal_catalog_path), '-k', str(priv)]
        monkeypatch.setattr(sys, 'argv', sign_args)
        assert Trestle().run() == CmdReturnCodes.SUCCESS.value

        verify_args = ['trestle', 'verify', '-f', str(minimal_catalog_path), '-k', str(pub)]
        monkeypatch.setattr(sys, 'argv', verify_args)
        assert Trestle().run() == CmdReturnCodes.SUCCESS.value
