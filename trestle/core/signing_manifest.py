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
"""Helpers for signed JSON package manifests."""

from __future__ import annotations

import hmac
import pathlib
from dataclasses import dataclass
from typing import Any, Dict, List, Set
from urllib.parse import urlparse

from securesystemslib.signer import Key, Signer

from trestle.common.err import TrestleError
from trestle.core.canonicalization import load_canonical_json_file, sha256_digest_hex
from trestle.core.signing import (
    DIGEST_ALGORITHM,
    IN_TOTO_STATEMENT_TYPE,
    load_in_toto_statement,
    sign_in_toto_statement,
    verify_dsse_payload,
)

PACKAGE_PREDICATE_TYPE = 'https://oscal-compass.github.io/compliance-trestle/predicates/oscal-package/v1'
MANIFEST_VERSION = 'v1'
PACKAGE_TOOL = 'compliance-trestle'
MANIFEST_FIELDS = {'primaryArtifact', 'artifacts'}
ARTIFACT_FIELDS = {'name', 'uri', 'mediaType'}


@dataclass(frozen=True)
class ManifestArtifact:
    """An artifact listed in a package manifest."""

    name: str
    uri: str
    media_type: str
    path: pathlib.Path

    def to_predicate(self) -> Dict[str, str]:
        """Return the stable predicate representation for the artifact."""
        return {'name': self.name, 'uri': self.uri, 'mediaType': self.media_type}


@dataclass(frozen=True)
class SigningManifest:
    """A validated JSON signing manifest."""

    path: pathlib.Path
    primary_artifact: str
    artifacts: List[ManifestArtifact]

    def predicate_artifacts(self) -> List[Dict[str, str]]:
        """Return the stable predicate artifact list."""
        return [artifact.to_predicate() for artifact in self.artifacts]


def load_signing_manifest(manifest_path: pathlib.Path) -> SigningManifest:
    """Load and validate a JSON signing manifest."""
    manifest_path = manifest_path.resolve()
    if manifest_path.suffix.lower() != '.json':
        raise TrestleError(f'Signing manifest must be a JSON file: {manifest_path}')
    if not manifest_path.exists() or not manifest_path.is_file():
        raise TrestleError(f'Signing manifest path does not exist or is not a file: {manifest_path}')

    try:
        manifest_data, _ = load_canonical_json_file(manifest_path)
    except TrestleError as error:
        raise TrestleError(f'Unable to load signing manifest JSON: {manifest_path}: {error}') from error

    if not isinstance(manifest_data, dict):
        raise TrestleError('Signing manifest must be a JSON object.')

    _reject_unknown_fields(manifest_data, MANIFEST_FIELDS, 'Signing manifest')
    primary_artifact = _required_string(manifest_data, 'primaryArtifact', 'Signing manifest')
    artifacts_data = manifest_data.get('artifacts')
    if not isinstance(artifacts_data, list) or not artifacts_data:
        raise TrestleError('Signing manifest artifacts must be a non-empty list.')

    artifacts: List[ManifestArtifact] = []
    artifact_names = set()
    for index, artifact_data in enumerate(artifacts_data):
        if not isinstance(artifact_data, dict):
            raise TrestleError(f'Signing manifest artifact at index {index} must be a mapping.')
        _reject_unknown_fields(artifact_data, ARTIFACT_FIELDS, f'Signing manifest artifact at index {index}')
        name = _required_string(artifact_data, 'name', f'Signing manifest artifact at index {index}')
        uri = _required_string(artifact_data, 'uri', f'Signing manifest artifact {name}')
        media_type = _required_string(artifact_data, 'mediaType', f'Signing manifest artifact {name}')
        if name in artifact_names:
            raise TrestleError(f'Signing manifest contains a duplicate artifact name: {name}')
        artifact_names.add(name)
        artifact_path = _artifact_path(manifest_path.parent, uri)
        _validate_artifact_path(artifact_path)
        artifacts.append(ManifestArtifact(name, uri, media_type, artifact_path))

    if primary_artifact not in artifact_names:
        raise TrestleError(f'Signing manifest primaryArtifact is not listed in artifacts: {primary_artifact}')

    return SigningManifest(manifest_path, primary_artifact, artifacts)


def create_manifest_envelope(manifest: SigningManifest, signer: Signer) -> Dict[str, Any]:
    """Create a DSSE envelope for a validated signing manifest."""
    return sign_in_toto_statement(build_manifest_statement(manifest), signer)


def build_manifest_statement(manifest: SigningManifest) -> Dict[str, Any]:
    """Build the in-toto Statement payload for a signing manifest."""
    return {
        '_type': IN_TOTO_STATEMENT_TYPE,
        'subject': _manifest_subjects(manifest),
        'predicateType': PACKAGE_PREDICATE_TYPE,
        'predicate': {
            'tool': PACKAGE_TOOL,
            'manifestVersion': MANIFEST_VERSION,
            'primaryArtifact': manifest.primary_artifact,
            'artifacts': manifest.predicate_artifacts(),
        },
    }


def verify_manifest_envelope(manifest: SigningManifest, envelope: Dict[str, Any], public_key: Key) -> Dict[str, Any]:
    """Verify a DSSE package Statement envelope against a signing manifest."""
    payload = verify_dsse_payload(envelope, public_key)
    statement = load_in_toto_statement(payload)
    _validate_manifest_statement(statement, manifest)
    return statement


def _validate_manifest_statement(statement: Dict[str, Any], manifest: SigningManifest) -> None:
    if statement.get('_type') != IN_TOTO_STATEMENT_TYPE:
        raise TrestleError('DSSE payload is not an in-toto Statement v1.')
    if statement.get('predicateType') != PACKAGE_PREDICATE_TYPE:
        raise TrestleError(f'Unsupported in-toto package predicate type: {statement.get("predicateType")}')

    predicate = statement.get('predicate')
    if not isinstance(predicate, dict):
        raise TrestleError('in-toto package Statement predicate must be a JSON object.')
    expected_predicate = {
        'tool': PACKAGE_TOOL,
        'manifestVersion': MANIFEST_VERSION,
        'primaryArtifact': manifest.primary_artifact,
        'artifacts': manifest.predicate_artifacts(),
    }
    if predicate != expected_predicate:
        raise TrestleError('in-toto package Statement predicate does not match the signing manifest.')

    _validate_manifest_subjects(statement.get('subject'), manifest)


def _validate_manifest_subjects(subjects: Any, manifest: SigningManifest) -> None:
    if not isinstance(subjects, list):
        raise TrestleError('in-toto package Statement subject must be an array.')

    expected_subjects = {
        subject['name']: subject['digest'][DIGEST_ALGORITHM] for subject in _manifest_subjects(manifest)
    }
    actual_subjects: Dict[str, str] = {}
    for subject in subjects:
        if not isinstance(subject, dict):
            raise TrestleError('in-toto package Statement subject entries must be JSON objects.')
        name = subject.get('name')
        if not isinstance(name, str):
            raise TrestleError('in-toto package Statement subject name must be a string.')
        if name in actual_subjects:
            raise TrestleError(f'in-toto package Statement contains a duplicate subject: {name}')
        digest = subject.get('digest')
        if not isinstance(digest, dict) or not isinstance(digest.get(DIGEST_ALGORITHM), str):
            raise TrestleError(f'in-toto package Statement subject does not contain a SHA-256 digest: {name}')
        actual_subjects[name] = digest[DIGEST_ALGORITHM]

    if set(actual_subjects) != set(expected_subjects):
        raise TrestleError('in-toto package Statement subjects do not match the signing manifest artifacts.')

    for name, expected_digest in expected_subjects.items():
        if not hmac.compare_digest(actual_subjects[name], expected_digest):
            raise TrestleError(f'in-toto package Statement digest does not match artifact: {name}')


def _manifest_subjects(manifest: SigningManifest) -> List[Dict[str, Any]]:
    return [
        {'name': artifact.name, 'digest': {DIGEST_ALGORITHM: _artifact_digest(artifact.path)}}
        for artifact in manifest.artifacts
    ]


def _artifact_digest(path: pathlib.Path) -> str:
    _, canonical_bytes = load_canonical_json_file(path)
    return sha256_digest_hex(canonical_bytes)


def _required_string(data: Dict[str, Any], key: str, context: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise TrestleError(f'{context} requires a non-empty string field: {key}')
    return value


def _reject_unknown_fields(data: Dict[str, Any], allowed_fields: Set[str], context: str) -> None:
    unknown_fields = sorted(str(field) for field in set(data) - allowed_fields)
    if unknown_fields:
        raise TrestleError(f'{context} contains unsupported field(s): {", ".join(unknown_fields)}')


def _artifact_path(manifest_dir: pathlib.Path, uri: str) -> pathlib.Path:
    manifest_dir = manifest_dir.resolve()
    parsed_uri = urlparse(uri)
    if parsed_uri.scheme or pathlib.Path(uri).is_absolute():
        raise TrestleError(f'Signing manifest artifact uri must be a relative local path: {uri}')
    artifact_path = (manifest_dir / uri).resolve()
    try:
        artifact_path.relative_to(manifest_dir)
    except ValueError:
        raise TrestleError(f'Signing manifest artifact uri must stay within the manifest directory: {uri}')
    return artifact_path


def _validate_artifact_path(path: pathlib.Path) -> None:
    if path.suffix.lower() != '.json':
        raise TrestleError(f'Signing manifest artifacts must be JSON files: {path}')
    if not path.exists() or not path.is_file():
        raise TrestleError(f'Signing manifest artifact path does not exist or is not a file: {path}')
