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

from _pytest.monkeypatch import MonkeyPatch
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from tests import test_utils

import trestle.common.const as const
from trestle.cli import Trestle
from trestle.core.commands.common.return_codes import CmdReturnCodes


def write_ed25519_key_pair(tmp_path: pathlib.Path, prefix: str = 'test-key') -> Tuple[pathlib.Path, pathlib.Path]:
    """Write a temporary Ed25519 private/public key pair."""
    private_key = ed25519.Ed25519PrivateKey.generate()
    private_key_path = tmp_path / f'{prefix}.pem'
    public_key_path = tmp_path / f'{prefix}.pub.pem'
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


def test_sign_rejects_output_that_matches_input(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Sign should not overwrite the OSCAL JSON input with a DSSE envelope."""
    private_key_path, _ = write_ed25519_key_pair(tmp_path)
    input_path = tmp_path / 'catalog.json'
    original_text = '{"a":1}'
    input_path.write_text(original_text, encoding=const.FILE_ENCODING)
    monkeypatch.setattr(
        sys, 'argv', ['trestle', 'sign', '-f', str(input_path), '--key', str(private_key_path), '-o', str(input_path)]
    )

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value
    assert input_path.read_text(encoding=const.FILE_ENCODING) == original_text


def test_verify_rejects_tampered_document(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Verify should fail if the OSCAL JSON changes after signing."""
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
