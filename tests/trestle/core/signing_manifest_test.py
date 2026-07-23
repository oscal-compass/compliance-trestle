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
"""Tests for signed package manifest helpers."""

import base64
import json
import pathlib
from typing import Any, Callable, Dict, Optional, Tuple

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

import trestle.common.const as const
from trestle.common.err import TrestleError
from trestle.core.signing import (
    DIGEST_ALGORITHM,
    IN_TOTO_STATEMENT_TYPE,
    load_pem_private_key_signer,
    load_pem_public_key,
    sign_in_toto_statement,
)
from trestle.core.signing_manifest import (
    MANIFEST_VERSION,
    PACKAGE_PREDICATE_TYPE,
    PACKAGE_TOOL,
    build_manifest_statement,
    create_manifest_envelope,
    load_signing_manifest,
    verify_manifest_envelope,
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


def write_package_manifest(tmp_path: pathlib.Path) -> pathlib.Path:
    """Write a sample package manifest and its JSON artifacts."""
    (tmp_path / 'ssp').mkdir()
    (tmp_path / 'profiles').mkdir()
    (tmp_path / 'catalogs').mkdir()
    (tmp_path / 'ssp/ssp.json').write_text('{"ssp":{"b":2,"a":1}}', encoding=const.FILE_ENCODING)
    (tmp_path / 'profiles/profile.json').write_text('{"profile":{"id":"test-profile"}}', encoding=const.FILE_ENCODING)
    (tmp_path / 'catalogs/catalog.json').write_text('{"catalog":{"id":"test-catalog"}}', encoding=const.FILE_ENCODING)
    manifest_path = tmp_path / 'package.json'
    manifest_path.write_text(
        json.dumps(
            {
                'primaryArtifact': 'ssp.json',
                'artifacts': [
                    {'name': 'ssp.json', 'uri': 'ssp/ssp.json', 'mediaType': 'application/oscal+json'},
                    {'name': 'profile.json', 'uri': 'profiles/profile.json', 'mediaType': 'application/oscal+json'},
                    {'name': 'catalog.json', 'uri': 'catalogs/catalog.json', 'mediaType': 'application/oscal+json'},
                ],
            }
        ),
        encoding=const.FILE_ENCODING,
    )
    return manifest_path


def test_create_manifest_envelope_contains_package_statement(tmp_path: pathlib.Path) -> None:
    """Manifest signing should create a package Statement with all artifact subjects."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    manifest = load_signing_manifest(write_package_manifest(tmp_path))
    signer = load_pem_private_key_signer(private_key_path)

    envelope = create_manifest_envelope(manifest, signer)
    statement = json.loads(base64.b64decode(envelope['payload']).decode(const.FILE_ENCODING))

    assert statement['_type'] == IN_TOTO_STATEMENT_TYPE
    assert statement['predicateType'] == PACKAGE_PREDICATE_TYPE
    assert statement['predicate'] == {
        'tool': PACKAGE_TOOL,
        'manifestVersion': MANIFEST_VERSION,
        'primaryArtifact': 'ssp.json',
        'artifacts': [
            {'name': 'ssp.json', 'uri': 'ssp/ssp.json', 'mediaType': 'application/oscal+json'},
            {'name': 'profile.json', 'uri': 'profiles/profile.json', 'mediaType': 'application/oscal+json'},
            {'name': 'catalog.json', 'uri': 'catalogs/catalog.json', 'mediaType': 'application/oscal+json'},
        ],
    }
    assert {subject['name'] for subject in statement['subject']} == {'ssp.json', 'profile.json', 'catalog.json'}
    assert all(DIGEST_ALGORITHM in subject['digest'] for subject in statement['subject'])

    public_key = load_pem_public_key(public_key_path)
    verify_manifest_envelope(manifest, envelope, public_key)


def test_build_manifest_statement_matches_create_manifest_payload(tmp_path: pathlib.Path) -> None:
    """The explicit builder should produce the same Statement payload shape used by signing."""
    manifest = load_signing_manifest(write_package_manifest(tmp_path))

    statement = build_manifest_statement(manifest)

    assert statement['predicateType'] == PACKAGE_PREDICATE_TYPE
    assert statement['predicate']['primaryArtifact'] == 'ssp.json'
    assert len(statement['subject']) == 3


@pytest.mark.parametrize(
    'manifest_name, manifest_text, expected_error',
    [
        ('package.yml', '{}', 'JSON file'),
        ('missing.json', None, 'does not exist'),
        ('package.json', '{"artifacts": [', 'Unable to load signing manifest JSON'),
        (
            'package.json',
            '{"artifacts":["ssp.json"],"primaryArtifact":"ssp.json"}',
            'artifact at index 0 must be a mapping',
        ),
        (
            'package.json',
            '{"artifacts":[{"uri":"ssp/ssp.json","mediaType":"application/oscal+json"}],"primaryArtifact":"ssp.json"}',
            'requires a non-empty string field: name',
        ),
        (
            'package.json',
            '{"primaryArtifact":"ssp.json","primaryArtifact":"other.json","artifacts":[]}',
            'Duplicate JSON object key',
        ),
    ],
)
def test_load_signing_manifest_rejects_manifest_file_and_artifact_errors(
    tmp_path: pathlib.Path, manifest_name: str, manifest_text: Optional[str], expected_error: str
) -> None:
    """Manifest loading should reject malformed paths, JSON, and artifact entries."""
    (tmp_path / 'ssp').mkdir()
    (tmp_path / 'ssp/ssp.json').write_text('{"ssp":{}}', encoding=const.FILE_ENCODING)
    manifest_path = tmp_path / manifest_name
    if manifest_text is not None:
        manifest_path.write_text(manifest_text, encoding=const.FILE_ENCODING)

    with pytest.raises(TrestleError, match=expected_error):
        load_signing_manifest(manifest_path)


def test_verify_manifest_rejects_changed_artifact(tmp_path: pathlib.Path) -> None:
    """Verification should fail when any signed artifact digest changes."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    manifest_path = write_package_manifest(tmp_path)
    manifest = load_signing_manifest(manifest_path)
    envelope = create_manifest_envelope(manifest, load_pem_private_key_signer(private_key_path))
    (tmp_path / 'profiles/profile.json').write_text('{"profile":{"id":"changed"}}', encoding=const.FILE_ENCODING)

    with pytest.raises(TrestleError, match='digest does not match artifact'):
        verify_manifest_envelope(load_signing_manifest(manifest_path), envelope, load_pem_public_key(public_key_path))


def test_verify_manifest_rejects_changed_manifest(tmp_path: pathlib.Path) -> None:
    """Verification should fail when the manifest metadata no longer matches the signed predicate."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    manifest_path = write_package_manifest(tmp_path)
    manifest = load_signing_manifest(manifest_path)
    envelope = create_manifest_envelope(manifest, load_pem_private_key_signer(private_key_path))
    manifest_path.write_text(
        manifest_path.read_text(encoding=const.FILE_ENCODING).replace('application/oscal+json', 'application/json', 1),
        encoding=const.FILE_ENCODING,
    )

    with pytest.raises(TrestleError, match='predicate does not match'):
        verify_manifest_envelope(load_signing_manifest(manifest_path), envelope, load_pem_public_key(public_key_path))


@pytest.mark.parametrize(
    'statement_update, expected_error',
    [
        (lambda statement: statement.update({'_type': 'wrong-type'}), 'not an in-toto Statement'),
        (
            lambda statement: statement.update({'predicateType': 'wrong-predicate'}),
            'Unsupported in-toto package predicate',
        ),
        (lambda statement: statement.update({'predicate': []}), 'predicate must be a JSON object'),
        (lambda statement: statement.update({'subject': {}}), 'subject must be an array'),
        (lambda statement: statement.update({'subject': ['ssp.json']}), 'subject entries must be JSON objects'),
        (lambda statement: statement['subject'][0].update({'name': 10}), 'subject name must be a string'),
        (lambda statement: statement['subject'].append(statement['subject'][0]), 'duplicate subject'),
        (
            lambda statement: statement['subject'][0].update({'digest': {'sha512': 'missing-sha256'}}),
            'does not contain a SHA-256 digest',
        ),
        (lambda statement: statement['subject'].pop(), 'subjects do not match'),
    ],
)
def test_verify_manifest_rejects_malformed_package_statements(
    tmp_path: pathlib.Path, statement_update: Callable[[Dict[str, Any]], None], expected_error: str
) -> None:
    """Package Statement validation should reject malformed or inconsistent signed payloads."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    manifest = load_signing_manifest(write_package_manifest(tmp_path))
    statement = build_manifest_statement(manifest)
    statement_update(statement)
    envelope = sign_in_toto_statement(statement, load_pem_private_key_signer(private_key_path))

    with pytest.raises(TrestleError, match=expected_error):
        verify_manifest_envelope(manifest, envelope, load_pem_public_key(public_key_path))


@pytest.mark.parametrize(
    'manifest_text, expected_error',
    [
        ('[]', 'JSON object'),
        ('{"primaryArtifact":"ssp.json","artifacts":[]}', 'non-empty list'),
        (
            '{"primaryArtifact":"missing.json","artifacts":['
            '{"name":"ssp.json","uri":"ssp/ssp.json","mediaType":"application/oscal+json"}]}',
            'primaryArtifact is not listed',
        ),
        (
            '{"primaryArtifact":"ssp.json","artifacts":['
            '{"name":"ssp.json","uri":"ssp/ssp.json","mediaType":"application/oscal+json"},'
            '{"name":"ssp.json","uri":"ssp/other.json","mediaType":"application/oscal+json"}]}',
            'duplicate artifact name',
        ),
        (
            '{"primaryArtifact":"ssp.json","artifacts":['
            '{"name":"ssp.json","uri":"ssp/ssp.json","mediaType":"application/oscal+json"}],'
            '"policy":"strict"}',
            'unsupported field',
        ),
        (
            '{"primaryArtifact":"ssp.json","artifacts":['
            '{"name":"ssp.json","uri":"ssp/ssp.json","mediaType":"application/oscal+json",'
            '"signatureRequired":true}]}',
            'unsupported field',
        ),
        (
            '{"primaryArtifact":"ssp.json","artifacts":['
            '{"name":"ssp.json","uri":"ssp/ssp.json","mediaType":"application/oscal+json"}],'
            '"1":"unexpected"}',
            'unsupported field',
        ),
    ],
)
def test_load_signing_manifest_rejects_invalid_shapes(
    tmp_path: pathlib.Path, manifest_text: str, expected_error: str
) -> None:
    """Manifest loading should reject invalid JSON shape and identifiers."""
    (tmp_path / 'ssp').mkdir()
    (tmp_path / 'ssp/ssp.json').write_text('{"ssp":{}}', encoding=const.FILE_ENCODING)
    (tmp_path / 'ssp/other.json').write_text('{"ssp":{}}', encoding=const.FILE_ENCODING)
    manifest_path = tmp_path / 'package.json'
    manifest_path.write_text(manifest_text, encoding=const.FILE_ENCODING)

    with pytest.raises(TrestleError, match=expected_error):
        load_signing_manifest(manifest_path)


@pytest.mark.parametrize(
    'uri, expected_error',
    [
        ('ssp/ssp.txt', 'JSON files'),
        ('ssp/missing.json', 'does not exist'),
        ('https://example.com/ssp.json', 'relative local path'),
        ('../outside.json', 'within the manifest directory'),
    ],
)
def test_load_signing_manifest_rejects_unsupported_artifact_paths(
    tmp_path: pathlib.Path, uri: str, expected_error: str
) -> None:
    """Manifest loading should reject unsupported or unavailable artifact paths."""
    (tmp_path / 'ssp').mkdir()
    (tmp_path / 'ssp/ssp.txt').write_text('not json', encoding=const.FILE_ENCODING)
    (tmp_path.parent / 'outside.json').write_text('{"outside":true}', encoding=const.FILE_ENCODING)
    manifest_path = tmp_path / 'package.json'
    manifest_path.write_text(
        json.dumps(
            {'primaryArtifact': 'ssp.json', 'artifacts': [{'name': 'ssp.json', 'uri': uri, 'mediaType': 'text/plain'}]}
        ),
        encoding=const.FILE_ENCODING,
    )

    with pytest.raises(TrestleError, match=expected_error):
        load_signing_manifest(manifest_path)


@pytest.mark.parametrize(
    'artifact_text, expected_error', [('{', 'Input is not valid JSON'), ('{"a":1,"a":2}', 'Duplicate JSON object key')]
)
def test_create_manifest_envelope_rejects_invalid_json_artifacts(
    tmp_path: pathlib.Path, artifact_text: str, expected_error: str
) -> None:
    """Manifest signing should fail before signing invalid or ambiguous JSON artifacts."""
    private_key_path, _ = write_ed25519_key_pair(tmp_path)
    manifest_path = write_package_manifest(tmp_path)
    (tmp_path / 'ssp/ssp.json').write_text(artifact_text, encoding=const.FILE_ENCODING)

    with pytest.raises(TrestleError, match=expected_error):
        create_manifest_envelope(load_signing_manifest(manifest_path), load_pem_private_key_signer(private_key_path))
