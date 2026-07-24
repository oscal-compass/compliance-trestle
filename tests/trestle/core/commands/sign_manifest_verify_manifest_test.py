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
"""Tests for trestle sign-manifest and verify-manifest commands."""

import base64
import json
import pathlib
import sys
from typing import Tuple

import pytest
from _pytest.monkeypatch import MonkeyPatch
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

import trestle.common.const as const
from trestle.common.err import TrestleError
from trestle.cli import Trestle
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.commands.sign_manifest import SignManifestCmd


def write_ed25519_key_pair(
    tmp_path: pathlib.Path, prefix: str = 'test-key', password: bytes = b''
) -> Tuple[pathlib.Path, pathlib.Path]:
    """Write a temporary Ed25519 private/public key pair."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    private_key_path = tmp_path / f'{prefix}.pem'
    public_key_path = tmp_path / f'{prefix}.pub.pem'
    encryption_algorithm = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()
    private_key_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm,
        )
    )
    public_key_path.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    return private_key_path, public_key_path


@pytest.fixture(autouse=True)
def enable_json_manifest_signing_beta(monkeypatch: MonkeyPatch) -> None:
    """Enable the manifest signing beta feature for command tests."""
    monkeypatch.setenv('TRESTLE_BETA_FEATURES', 'json-manifest-signing')


def write_package_manifest(tmp_path: pathlib.Path) -> pathlib.Path:
    """Write a sample package manifest and JSON artifacts."""
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


def test_sign_manifest_and_verify_manifest_require_beta_feature(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Manifest sign and verify commands should be blocked unless the beta feature is enabled."""
    monkeypatch.delenv('TRESTLE_BETA_FEATURES', raising=False)
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path / 'xdg-config'))
    manifest_path = tmp_path / 'package.json'
    key_path = tmp_path / 'key.pem'
    envelope_path = tmp_path / 'package.dsse'

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'sign-manifest',
            '--manifest',
            str(manifest_path),
            '--key',
            str(key_path),
            '-o',
            str(envelope_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'verify-manifest',
            '--manifest',
            str(manifest_path),
            '--signature',
            str(envelope_path),
            '--public-key',
            str(key_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value


def test_sign_manifest_and_verify_manifest_accept_one_time_beta_flag(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Manifest commands should run with --beta without persisting beta config."""
    monkeypatch.delenv('TRESTLE_BETA_FEATURES', raising=False)
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path / 'xdg-config'))
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    manifest_path = write_package_manifest(tmp_path)
    envelope_path = tmp_path / 'package.dsse'

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'sign-manifest',
            '--beta',
            '--manifest',
            str(manifest_path),
            '--key',
            str(private_key_path),
            '-o',
            str(envelope_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'verify-manifest',
            '--beta',
            '--manifest',
            str(manifest_path),
            '--signature',
            str(envelope_path),
            '--public-key',
            str(public_key_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value
    assert not (tmp_path / 'xdg-config').exists()


def test_sign_manifest_and_verify_manifest_round_trip(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign-manifest should write a DSSE envelope that verify-manifest accepts."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    manifest_path = write_package_manifest(tmp_path)
    envelope_path = tmp_path / 'package.dsse'

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'sign-manifest',
            '--manifest',
            str(manifest_path),
            '--key',
            str(private_key_path),
            '-o',
            str(envelope_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value
    assert envelope_path.exists()

    envelope = json.loads(envelope_path.read_text(encoding=const.FILE_ENCODING))
    statement = json.loads(base64.b64decode(envelope['payload']).decode(const.FILE_ENCODING))
    assert envelope['payloadType'] == 'application/vnd.in-toto+json'
    assert (
        statement['predicateType'] == 'https://oscal-compass.github.io/compliance-trestle/predicates/oscal-package/v1'
    )
    assert {subject['name'] for subject in statement['subject']} == {'ssp.json', 'profile.json', 'catalog.json'}

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'verify-manifest',
            '--manifest',
            str(manifest_path),
            '--signature',
            str(envelope_path),
            '--public-key',
            str(public_key_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value


def test_sign_manifest_supports_encrypted_private_key(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign-manifest should accept an encrypted PEM private key password from an environment variable."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path, password=b'test-password')
    manifest_path = write_package_manifest(tmp_path)
    envelope_path = tmp_path / 'package.dsse'
    monkeypatch.setenv('TRESTLE_KEY_PASSWORD', 'test-password')

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'sign-manifest',
            '--manifest',
            str(manifest_path),
            '--key',
            str(private_key_path),
            '--key-password-env',
            'TRESTLE_KEY_PASSWORD',
            '-o',
            str(envelope_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'verify-manifest',
            '--manifest',
            str(manifest_path),
            '--signature',
            str(envelope_path),
            '--public-key',
            str(public_key_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value


@pytest.mark.parametrize(
    'output_target, expected_error',
    [('manifest', 'different from package manifest'), ('key', 'different from private key')],
)
def test_sign_manifest_rejects_unsafe_output_paths(
    tmp_path: pathlib.Path, output_target: str, expected_error: str
) -> None:
    """Sign-manifest should reject output paths that would overwrite important inputs."""
    private_key_path, _ = write_ed25519_key_pair(tmp_path)
    manifest_path = write_package_manifest(tmp_path)
    output_path = manifest_path if output_target == 'manifest' else private_key_path

    with pytest.raises(TrestleError, match=expected_error):
        SignManifestCmd.sign_manifest(manifest_path, private_key_path, output_path)


def test_sign_manifest_rejects_missing_key_password_env(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign-manifest should fail before writing output when the password env var is missing."""
    private_key_path, _ = write_ed25519_key_pair(tmp_path)
    manifest_path = write_package_manifest(tmp_path)
    monkeypatch.delenv('MISSING_TRESTLE_KEY_PASSWORD', raising=False)

    with pytest.raises(TrestleError, match='Key password environment variable is not set'):
        SignManifestCmd.sign_manifest(
            manifest_path, private_key_path, tmp_path / 'package.dsse', 'MISSING_TRESTLE_KEY_PASSWORD'
        )


def test_verify_manifest_rejects_changed_artifact(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Verify-manifest should fail if a package artifact changes after signing."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    manifest_path = write_package_manifest(tmp_path)
    envelope_path = tmp_path / 'package.dsse'

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'sign-manifest',
            '--manifest',
            str(manifest_path),
            '--key',
            str(private_key_path),
            '-o',
            str(envelope_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value
    (tmp_path / 'ssp/ssp.json').write_text('{"ssp":{"changed":true}}', encoding=const.FILE_ENCODING)

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'verify-manifest',
            '--manifest',
            str(manifest_path),
            '--signature',
            str(envelope_path),
            '--public-key',
            str(public_key_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value


def test_verify_manifest_rejects_wrong_public_key(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Verify-manifest should fail if the public key does not match the signing key."""
    private_key_path, _ = write_ed25519_key_pair(tmp_path, 'signing-key')
    _, wrong_public_key_path = write_ed25519_key_pair(tmp_path, 'wrong-key')
    manifest_path = write_package_manifest(tmp_path)
    envelope_path = tmp_path / 'package.dsse'

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'sign-manifest',
            '--manifest',
            str(manifest_path),
            '--key',
            str(private_key_path),
            '-o',
            str(envelope_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'verify-manifest',
            '--manifest',
            str(manifest_path),
            '--signature',
            str(envelope_path),
            '--public-key',
            str(wrong_public_key_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value


def test_verify_manifest_rejects_tampered_envelope(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Verify-manifest should fail when the package DSSE envelope is tampered."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    manifest_path = write_package_manifest(tmp_path)
    envelope_path = tmp_path / 'package.dsse'

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'sign-manifest',
            '--manifest',
            str(manifest_path),
            '--key',
            str(private_key_path),
            '-o',
            str(envelope_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value
    envelope = json.loads(envelope_path.read_text(encoding=const.FILE_ENCODING))
    envelope['payload'] = base64.b64encode(b'{"tampered":true}').decode('ascii')
    envelope_path.write_text(json.dumps(envelope), encoding=const.FILE_ENCODING)

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'verify-manifest',
            '--manifest',
            str(manifest_path),
            '--signature',
            str(envelope_path),
            '--public-key',
            str(public_key_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value
