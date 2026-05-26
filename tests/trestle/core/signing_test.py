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
"""Tests for OSCAL provenance signing helpers."""

import base64
import copy
import json
import pathlib
from typing import Any, Dict, Tuple

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

import trestle.common.const as const
from trestle.common.err import TrestleError
from trestle.core.canonicalization import sha256_digest_hex
from trestle.core.signing import (
    CANONICALIZATION_ALGORITHM,
    DIGEST_ALGORITHM,
    DSSE_PAYLOAD_TYPE,
    IN_TOTO_STATEMENT_TYPE,
    OSCAL_PREDICATE_TYPE,
    build_in_toto_statement,
    create_oscal_provenance_envelope,
    dsse_pae,
    load_dsse_envelope,
    load_pem_private_key_signer,
    load_pem_public_key,
    sign_in_toto_statement,
    verify_oscal_provenance_envelope,
    write_dsse_envelope,
)


def write_ed25519_key_pair(tmp_path: pathlib.Path) -> Tuple[pathlib.Path, pathlib.Path]:
    """Write a temporary Ed25519 private/public key pair."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    private_key_path = tmp_path / 'test-key.pem'
    public_key_path = tmp_path / 'test-key.pub.pem'
    private_key_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public_key_path.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    return private_key_path, public_key_path


def sign_payload(payload: bytes, signer: Any) -> Dict[str, Any]:
    """Sign arbitrary DSSE payload bytes for validation tests."""
    signature = signer.sign(dsse_pae(DSSE_PAYLOAD_TYPE, payload))
    return {
        'payload': base64.b64encode(payload).decode('ascii'),
        'payloadType': DSSE_PAYLOAD_TYPE,
        'signatures': [
            {'keyid': signature.keyid, 'sig': base64.b64encode(bytes.fromhex(signature.signature)).decode('ascii')}
        ],
    }


def signing_context(tmp_path: pathlib.Path) -> Tuple[pathlib.Path, Any, Any, Dict[str, Any], Dict[str, Any]]:
    """Create an input file, signer, public key, envelope, and Statement for validation tests."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    input_path = tmp_path / 'catalog.json'
    input_path.write_text('{"a":1}', encoding=const.FILE_ENCODING)
    signer = load_pem_private_key_signer(private_key_path)
    public_key = load_pem_public_key(public_key_path)
    envelope = create_oscal_provenance_envelope(input_path, signer)
    statement = build_in_toto_statement(input_path.name, sha256_digest_hex(b'{"a":1}'))
    return input_path, signer, public_key, envelope, statement


def test_dsse_pae_returns_expected_encoding() -> None:
    """DSSE PAE should bind payload type and payload bytes."""
    assert dsse_pae('test/type', b'payload') == b'DSSEv1 9 test/type 7 payload'


def test_create_oscal_provenance_envelope_contains_in_toto_statement(tmp_path: pathlib.Path) -> None:
    """Signing should create a DSSE envelope with an in-toto Statement payload."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    input_path = tmp_path / 'catalog.json'
    input_path.write_text('{"b":2,"a":1}', encoding=const.FILE_ENCODING)

    signer = load_pem_private_key_signer(private_key_path)
    envelope = create_oscal_provenance_envelope(input_path, signer)

    assert envelope['payloadType'] == DSSE_PAYLOAD_TYPE
    assert len(envelope['signatures']) == 1
    statement = json.loads(base64.b64decode(envelope['payload']).decode(const.FILE_ENCODING))
    assert statement['_type'] == IN_TOTO_STATEMENT_TYPE
    assert statement['predicateType'] == OSCAL_PREDICATE_TYPE
    assert statement['predicate']['canonicalization'] == CANONICALIZATION_ALGORITHM
    assert statement['predicate']['digestAlgorithm'] == DIGEST_ALGORITHM
    assert statement['subject'][0]['name'] == 'catalog.json'
    assert statement['subject'][0]['digest']['sha256'] == sha256_digest_hex(b'{"a":1,"b":2}')

    public_key = load_pem_public_key(public_key_path)
    verify_oscal_provenance_envelope(input_path, envelope, public_key)


def test_key_loaders_reject_invalid_pem(tmp_path: pathlib.Path) -> None:
    """Key loaders should surface invalid PEM files as trestle errors."""
    key_path = tmp_path / 'invalid.pem'
    key_path.write_text('not a pem key', encoding=const.FILE_ENCODING)

    with pytest.raises(TrestleError):
        load_pem_private_key_signer(key_path)
    with pytest.raises(TrestleError):
        load_pem_public_key(key_path)


def test_write_dsse_envelope_rejects_output_directory(tmp_path: pathlib.Path) -> None:
    """DSSE envelope writing should reject directory output paths."""
    with pytest.raises(TrestleError):
        write_dsse_envelope({}, tmp_path)


def test_load_dsse_envelope_rejects_invalid_json_and_non_object(tmp_path: pathlib.Path) -> None:
    """DSSE envelope loading should require a JSON object."""
    invalid_json_path = tmp_path / 'invalid.dsse'
    invalid_json_path.write_text('{', encoding=const.FILE_ENCODING)
    with pytest.raises(TrestleError):
        load_dsse_envelope(invalid_json_path)

    non_object_path = tmp_path / 'non-object.dsse'
    non_object_path.write_text('[]', encoding=const.FILE_ENCODING)
    with pytest.raises(TrestleError):
        load_dsse_envelope(non_object_path)


def test_load_dsse_envelope_rejects_duplicate_keys(tmp_path: pathlib.Path) -> None:
    """DSSE envelope loading should reject duplicate JSON object keys."""
    duplicate_key_path = tmp_path / 'duplicate-key.dsse'
    duplicate_key_path.write_text('{"payload":"one","payload":"two"}', encoding=const.FILE_ENCODING)

    with pytest.raises(TrestleError):
        load_dsse_envelope(duplicate_key_path)


def test_verify_rejects_malformed_dsse_fields(tmp_path: pathlib.Path) -> None:
    """Verification should reject malformed DSSE envelope fields before accepting a payload."""
    input_path, _, public_key, envelope, _ = signing_context(tmp_path)
    bad_envelopes = []

    unsupported_payload_type = copy.deepcopy(envelope)
    unsupported_payload_type['payloadType'] = 'bad/type'
    bad_envelopes.append(unsupported_payload_type)

    no_signatures = copy.deepcopy(envelope)
    no_signatures['signatures'] = []
    bad_envelopes.append(no_signatures)

    non_string_payload = copy.deepcopy(envelope)
    non_string_payload['payload'] = 1
    bad_envelopes.append(non_string_payload)

    invalid_payload_base64 = copy.deepcopy(envelope)
    invalid_payload_base64['payload'] = 'not base64!!'
    bad_envelopes.append(invalid_payload_base64)

    non_object_signature = copy.deepcopy(envelope)
    non_object_signature['signatures'] = ['bad']
    bad_envelopes.append(non_object_signature)

    missing_keyid = copy.deepcopy(envelope)
    del missing_keyid['signatures'][0]['keyid']
    bad_envelopes.append(missing_keyid)

    invalid_signature_base64 = copy.deepcopy(envelope)
    invalid_signature_base64['signatures'][0]['sig'] = 'not base64!!'
    bad_envelopes.append(invalid_signature_base64)

    for bad_envelope in bad_envelopes:
        with pytest.raises(TrestleError):
            verify_oscal_provenance_envelope(input_path, bad_envelope, public_key)


def test_verify_rejects_invalid_statement_payloads(tmp_path: pathlib.Path) -> None:
    """Verification should reject signed payloads that are not JSON Statement objects."""
    input_path, signer, public_key, _, _ = signing_context(tmp_path)
    for payload in [b'\xff', b'{', b'[]', b'{"_type":"one","_type":"two"}']:
        with pytest.raises(TrestleError):
            verify_oscal_provenance_envelope(input_path, sign_payload(payload, signer), public_key)


def test_verify_rejects_invalid_statement_fields(tmp_path: pathlib.Path) -> None:
    """Verification should reject signed Statements with unsupported provenance fields."""
    input_path, signer, public_key, _, statement = signing_context(tmp_path)
    bad_statements = []

    bad_type = copy.deepcopy(statement)
    bad_type['_type'] = 'bad-type'
    bad_statements.append(bad_type)

    bad_predicate_type = copy.deepcopy(statement)
    bad_predicate_type['predicateType'] = 'bad-predicate-type'
    bad_statements.append(bad_predicate_type)

    non_object_predicate = copy.deepcopy(statement)
    non_object_predicate['predicate'] = []
    bad_statements.append(non_object_predicate)

    bad_canonicalization = copy.deepcopy(statement)
    bad_canonicalization['predicate']['canonicalization'] = 'bad-canonicalization'
    bad_statements.append(bad_canonicalization)

    bad_digest_algorithm = copy.deepcopy(statement)
    bad_digest_algorithm['predicate']['digestAlgorithm'] = 'sha512'
    bad_statements.append(bad_digest_algorithm)

    bad_digest_source = copy.deepcopy(statement)
    bad_digest_source['predicate']['digestSource'] = 'original-file-bytes'
    bad_statements.append(bad_digest_source)

    non_array_subject = copy.deepcopy(statement)
    non_array_subject['subject'] = {}
    bad_statements.append(non_array_subject)

    missing_subject = copy.deepcopy(statement)
    missing_subject['subject'] = ['bad-subject']
    bad_statements.append(missing_subject)

    for bad_statement in bad_statements:
        with pytest.raises(TrestleError):
            verify_oscal_provenance_envelope(input_path, sign_in_toto_statement(bad_statement, signer), public_key)
