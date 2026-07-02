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
"""Tests for trestle sign and verify commands."""

import json
import pathlib
import sys
from typing import Tuple

import pytest
from _pytest.monkeypatch import MonkeyPatch
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from tests import test_utils

import trestle.common.const as const
from trestle.cli import Trestle
from trestle.core.commands.common.return_codes import CmdReturnCodes


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
def enable_json_signing_beta(monkeypatch: MonkeyPatch) -> None:
    """Enable the JSON signing beta feature for sign/verify command tests."""
    monkeypatch.setenv('TRESTLE_BETA_FEATURES', 'json-signing')


def test_sign_and_verify_require_beta_feature(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign and verify commands should be blocked unless the beta feature is enabled."""
    monkeypatch.delenv('TRESTLE_BETA_FEATURES', raising=False)
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path / 'xdg-config'))
    input_path = tmp_path / 'catalog.json'
    key_path = tmp_path / 'key.pem'
    envelope_path = tmp_path / 'catalog.json.dsse'

    monkeypatch.setattr(
        sys, 'argv', ['trestle', 'sign', '-f', str(input_path), '--key', str(key_path), '-o', str(envelope_path)]
    )
    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value

    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'verify', '-f', str(input_path), '--signature', str(envelope_path), '--key', str(key_path)],
    )
    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value


def test_sign_and_verify_accept_one_time_beta_flag(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign and verify should run with --beta without persisting beta config."""
    monkeypatch.delenv('TRESTLE_BETA_FEATURES', raising=False)
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path / 'xdg-config'))
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    input_path = tmp_path / 'catalog.json'
    envelope_path = tmp_path / 'catalog.json.dsse'
    input_path.write_text('{"b":2,"a":1}', encoding=const.FILE_ENCODING)

    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'sign', '--beta', '-f', str(input_path), '--key', str(private_key_path), '-o', str(envelope_path)],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'verify',
            '--beta',
            '-f',
            str(input_path),
            '--signature',
            str(envelope_path),
            '--key',
            str(public_key_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value
    assert not (tmp_path / 'xdg-config').exists()


def test_sign_and_verify_round_trip(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign should write a DSSE sidecar that verify accepts."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    input_path = tmp_path / 'catalog.json'
    envelope_path = tmp_path / 'catalog.json.dsse'
    input_path.write_text('{"b":2,"a":1}', encoding=const.FILE_ENCODING)

    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'sign', '-f', str(input_path), '--key', str(private_key_path), '-o', str(envelope_path)],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value
    assert input_path.read_text(encoding=const.FILE_ENCODING) == '{"b":2,"a":1}'

    envelope = json.loads(envelope_path.read_text(encoding=const.FILE_ENCODING))
    assert envelope['payloadType'] == 'application/vnd.in-toto+json'

    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'verify', '-f', str(input_path), '--signature', str(envelope_path), '--key', str(public_key_path)],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value


def test_sign_and_verify_real_nist_800_53_catalog(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign and verify should support a real NIST 800-53 OSCAL catalog."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    input_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    envelope_path = tmp_path / 'nist-800-53-catalog.json.dsse'

    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'sign', '-f', str(input_path), '--key', str(private_key_path), '-o', str(envelope_path)],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value
    assert envelope_path.exists()

    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'verify', '-f', str(input_path), '--signature', str(envelope_path), '--key', str(public_key_path)],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value


def test_verify_rejects_missing_custom_subject_name(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Verify should require the same custom subject name used during signing."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    input_path = tmp_path / 'catalog.json'
    envelope_path = tmp_path / 'catalog.json.dsse'
    input_path.write_text('{"a":1}', encoding=const.FILE_ENCODING)

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'sign',
            '-f',
            str(input_path),
            '--key',
            str(private_key_path),
            '-o',
            str(envelope_path),
            '--subject-name',
            'custom/catalog.json',
        ],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value

    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'verify', '-f', str(input_path), '--signature', str(envelope_path), '--key', str(public_key_path)],
    )
    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'verify',
            '-f',
            str(input_path),
            '--signature',
            str(envelope_path),
            '--key',
            str(public_key_path),
            '--subject-name',
            'custom/catalog.json',
        ],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value


def test_sign_supports_encrypted_private_key(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign should accept an encrypted PEM private key password from an environment variable."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path, password=b'test-password')
    input_path = tmp_path / 'catalog.json'
    envelope_path = tmp_path / 'catalog.json.dsse'
    input_path.write_text('{"a":1}', encoding=const.FILE_ENCODING)
    monkeypatch.setenv('TRESTLE_KEY_PASSWORD', 'test-password')

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'sign',
            '-f',
            str(input_path),
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
        ['trestle', 'verify', '-f', str(input_path), '--signature', str(envelope_path), '--key', str(public_key_path)],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value


def test_sign_rejects_missing_key_password_env(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign should fail when the requested key password environment variable is unset."""
    private_key_path, _ = write_ed25519_key_pair(tmp_path, password=b'test-password')
    input_path = tmp_path / 'catalog.json'
    envelope_path = tmp_path / 'catalog.json.dsse'
    input_path.write_text('{"a":1}', encoding=const.FILE_ENCODING)
    monkeypatch.delenv('TRESTLE_KEY_PASSWORD', raising=False)

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'sign',
            '-f',
            str(input_path),
            '--key',
            str(private_key_path),
            '--key-password-env',
            'TRESTLE_KEY_PASSWORD',
            '-o',
            str(envelope_path),
        ],
    )

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value
    assert not envelope_path.exists()


def test_sign_rejects_output_that_matches_input(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign should not overwrite the JSON input with a DSSE envelope."""
    private_key_path, _ = write_ed25519_key_pair(tmp_path)
    input_path = tmp_path / 'catalog.json'
    original_text = '{"a":1}'
    input_path.write_text(original_text, encoding=const.FILE_ENCODING)
    monkeypatch.setattr(
        sys, 'argv', ['trestle', 'sign', '-f', str(input_path), '--key', str(private_key_path), '-o', str(input_path)]
    )

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value
    assert input_path.read_text(encoding=const.FILE_ENCODING) == original_text


def test_sign_rejects_output_that_matches_private_key(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign should not overwrite the private key with a DSSE envelope."""
    private_key_path, _ = write_ed25519_key_pair(tmp_path)
    original_key = private_key_path.read_bytes()
    input_path = tmp_path / 'catalog.json'
    input_path.write_text('{"a":1}', encoding=const.FILE_ENCODING)
    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'sign', '-f', str(input_path), '--key', str(private_key_path), '-o', str(private_key_path)],
    )

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value
    assert private_key_path.read_bytes() == original_key


def test_sign_rejects_output_symlink(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign should not follow output symlinks when writing a DSSE envelope."""
    private_key_path, _ = write_ed25519_key_pair(tmp_path)
    input_path = tmp_path / 'catalog.json'
    target_path = tmp_path / 'target.dsse'
    output_path = tmp_path / 'catalog.json.dsse'
    input_path.write_text('{"a":1}', encoding=const.FILE_ENCODING)
    try:
        output_path.symlink_to(target_path)
    except OSError as error:
        pytest.skip(f'Symlinks are not available in this environment: {error}')

    monkeypatch.setattr(
        sys, 'argv', ['trestle', 'sign', '-f', str(input_path), '--key', str(private_key_path), '-o', str(output_path)]
    )

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value
    assert not target_path.exists()


def test_verify_rejects_tampered_document(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Verify should fail if the JSON changes after signing."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    input_path = tmp_path / 'catalog.json'
    envelope_path = tmp_path / 'catalog.json.dsse'
    input_path.write_text('{"a":1}', encoding=const.FILE_ENCODING)
    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'sign', '-f', str(input_path), '--key', str(private_key_path), '-o', str(envelope_path)],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value

    input_path.write_text('{"a":2}', encoding=const.FILE_ENCODING)
    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'verify', '-f', str(input_path), '--signature', str(envelope_path), '--key', str(public_key_path)],
    )
    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value


def test_verify_rejects_wrong_key(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Verify should fail if the public key does not match the signing key."""
    private_key_path, _ = write_ed25519_key_pair(tmp_path, 'signing-key')
    _, wrong_public_key_path = write_ed25519_key_pair(tmp_path, 'wrong-key')
    input_path = tmp_path / 'catalog.json'
    envelope_path = tmp_path / 'catalog.json.dsse'
    input_path.write_text('{"a":1}', encoding=const.FILE_ENCODING)
    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'sign', '-f', str(input_path), '--key', str(private_key_path), '-o', str(envelope_path)],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'verify',
            '-f',
            str(input_path),
            '--signature',
            str(envelope_path),
            '--key',
            str(wrong_public_key_path),
        ],
    )
    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value


def test_sign_rejects_duplicate_json_keys(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign should fail before signing ambiguous JSON."""
    private_key_path, _ = write_ed25519_key_pair(tmp_path)
    input_path = tmp_path / 'catalog.json'
    envelope_path = tmp_path / 'catalog.json.dsse'
    input_path.write_text('{"a":1,"a":2}', encoding=const.FILE_ENCODING)
    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'sign', '-f', str(input_path), '--key', str(private_key_path), '-o', str(envelope_path)],
    )

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value
    assert not envelope_path.exists()


def test_sign_rejects_non_json_input(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign should reject non-JSON file extensions."""
    private_key_path, _ = write_ed25519_key_pair(tmp_path)
    input_path = tmp_path / 'catalog.txt'
    envelope_path = tmp_path / 'catalog.txt.dsse'
    input_path.write_text('{"a":1}', encoding=const.FILE_ENCODING)
    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'sign', '-f', str(input_path), '--key', str(private_key_path), '-o', str(envelope_path)],
    )

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value
    assert not envelope_path.exists()


def test_verify_rejects_non_json_input(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Verify should reject non-JSON file extensions."""
    private_key_path, public_key_path = write_ed25519_key_pair(tmp_path)
    input_path = tmp_path / 'catalog.json'
    non_json_input_path = tmp_path / 'catalog.txt'
    envelope_path = tmp_path / 'catalog.json.dsse'
    input_path.write_text('{"a":1}', encoding=const.FILE_ENCODING)
    non_json_input_path.write_text('{"a":1}', encoding=const.FILE_ENCODING)
    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'sign', '-f', str(input_path), '--key', str(private_key_path), '-o', str(envelope_path)],
    )
    assert Trestle().run() == CmdReturnCodes.SUCCESS.value

    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'verify',
            '-f',
            str(non_json_input_path),
            '--signature',
            str(envelope_path),
            '--key',
            str(public_key_path),
            '--subject-name',
            input_path.name,
        ],
    )
    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value
