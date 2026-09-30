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
"""Tests for trestle generate-manifest command."""

import json
import pathlib
import sys
from typing import Any, Dict, Tuple

import pytest
from _pytest.monkeypatch import MonkeyPatch
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from tests import test_utils

from trestle.cli import Trestle
from trestle.common import const
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.commands.generate_manifest import GenerateManifestCmd
from trestle.core.commands.sign_manifest import SignManifestCmd
from trestle.core.commands.verify_manifest import VerifyManifestCmd
from trestle.core.signing_manifest import load_signing_manifest


@pytest.fixture(autouse=True)
def enable_json_manifest_signing_beta(monkeypatch: MonkeyPatch) -> None:
    """Enable automatic package generation for command tests."""
    monkeypatch.setenv('TRESTLE_BETA_FEATURES', 'json-manifest-signing')


def _read_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding=const.FILE_ENCODING))


def _write_json(path: pathlib.Path, data: Dict[str, Any]) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding=const.FILE_ENCODING)
    return path


def _write_test_package(package_root: pathlib.Path) -> Tuple[pathlib.Path, pathlib.Path]:
    catalog = _read_json(test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json')
    _write_json(package_root / 'catalogs/catalog.json', catalog)

    profile = _read_json(test_utils.JSON_TEST_DATA_PATH / 'simple_test_profile.json')
    profile['profile']['imports'] = [{'href': '../catalogs/catalog.json', 'include-all': {}}]
    profile['profile'].pop('back_matter', None)
    _write_json(package_root / 'profiles/profile.json', profile)

    ssp = _read_json(test_utils.TEST_DIR / 'data/author/ssp/ssp_example.json')
    ssp['system-security-plan']['import-profile']['href'] = '../../profiles/profile.json'
    ssp_path = _write_json(package_root / 'system-security-plans/acme/ssp.json', ssp)

    component = _read_json(test_utils.TEST_DIR / 'data/validate/component-definitions/x1/component-definition.json')
    component_path = _write_json(package_root / 'component-definitions/web/component-definition.json', component)
    return ssp_path, component_path


def _write_ed25519_key_pair(tmp_path: pathlib.Path) -> Tuple[pathlib.Path, pathlib.Path]:
    private_key = ed25519.Ed25519PrivateKey.generate()
    private_key_path = tmp_path / 'private.pem'
    public_key_path = tmp_path / 'public.pem'
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


def test_generate_manifest_requires_beta_feature(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Generate-manifest should be blocked unless its beta feature is enabled."""
    monkeypatch.delenv('TRESTLE_BETA_FEATURES', raising=False)
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path / 'xdg-config'))
    monkeypatch.setattr(
        sys,
        'argv',
        ['trestle', 'generate-manifest', '-f', str(tmp_path / 'ssp.json'), '-o', str(tmp_path / 'package.json')],
    )

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value


def test_generate_manifest_accepts_one_time_beta_and_explicit_include(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """The command should generate valid JSON with a one-time beta flag and explicit include."""
    monkeypatch.delenv('TRESTLE_BETA_FEATURES', raising=False)
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path / 'xdg-config'))
    package_root = tmp_path / 'package'
    ssp_path, component_path = _write_test_package(package_root)
    output_path = package_root / 'package.json'
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'generate-manifest',
            '--beta',
            '-f',
            str(ssp_path),
            '--include',
            str(component_path),
            '--allow-private-uris',
            '-o',
            str(output_path),
        ],
    )

    assert Trestle().run() == CmdReturnCodes.SUCCESS.value
    manifest = load_signing_manifest(output_path)
    assert manifest.primary_artifact == 'system-security-plans/acme/ssp.json'
    assert [artifact.name for artifact in manifest.artifacts] == [
        'system-security-plans/acme/ssp.json',
        'profiles/profile.json',
        'catalogs/catalog.json',
        'component-definitions/web/component-definition.json',
    ]
    assert not (tmp_path / 'xdg-config').exists()


def test_generate_manifest_parses_comma_separated_includes(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """The CLI should pass each comma-separated explicit artifact to discovery."""
    package_root = tmp_path / 'package'
    ssp_path, first_component = _write_test_package(package_root)
    second_component = package_root / 'component-definitions/database/component-definition.json'
    second_component.parent.mkdir(parents=True)
    second_component.write_text(first_component.read_text(encoding=const.FILE_ENCODING), encoding=const.FILE_ENCODING)
    output_path = package_root / 'package.json'
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'trestle',
            'generate-manifest',
            '-f',
            str(ssp_path),
            '--include',
            f'{first_component},{second_component}',
            '-o',
            str(output_path),
        ],
    )

    assert Trestle().run() == CmdReturnCodes.SUCCESS.value
    assert _artifact_names(output_path)[-2:] == [
        'component-definitions/web/component-definition.json',
        'component-definitions/database/component-definition.json',
    ]


def test_generate_manifest_overwrites_existing_output(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """The command should replace an existing output only when explicitly requested."""
    package_root = tmp_path / 'package'
    ssp_path, _ = _write_test_package(package_root)
    output_path = package_root / 'package.json'
    output_path.write_text('{"old":true}', encoding=const.FILE_ENCODING)
    monkeypatch.setattr(
        sys, 'argv', ['trestle', 'generate-manifest', '-f', str(ssp_path), '--overwrite', '-o', str(output_path)]
    )

    assert Trestle().run() == CmdReturnCodes.SUCCESS.value
    assert _artifact_names(output_path) == [
        'system-security-plans/acme/ssp.json',
        'profiles/profile.json',
        'catalogs/catalog.json',
    ]


def _artifact_names(manifest_path: pathlib.Path) -> list[str]:
    return [artifact.name for artifact in load_signing_manifest(manifest_path).artifacts]


def test_generate_sign_verify_real_nist_package(tmp_path: pathlib.Path) -> None:
    """A discovered real NIST SSP, profile, and catalog package should sign and verify."""
    package_root = tmp_path / 'package'
    ssp_data = _read_json(test_utils.NIST_EXAMPLES / 'ssp/json/ssp-example.json')
    ssp_data['system-security-plan']['import-profile']['href'] = '../../profiles/nist-low/profile.json'
    ssp_path = _write_json(package_root / 'system-security-plans/acme/ssp.json', ssp_data)

    profile_data = _read_json(test_utils.JSON_NIST_DATA_PATH / 'NIST_SP-800-53_rev5_LOW-baseline_profile.json')
    profile_data['profile']['imports'][0]['href'] = '../../catalogs/nist/catalog.json'
    _write_json(package_root / 'profiles/nist-low/profile.json', profile_data)
    catalog_data = _read_json(test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME)
    _write_json(package_root / 'catalogs/nist/catalog.json', catalog_data)

    manifest_path = package_root / 'package.json'
    envelope_path = package_root / 'package.dsse'
    private_key_path, public_key_path = _write_ed25519_key_pair(tmp_path)

    GenerateManifestCmd.generate_manifest(ssp_path, manifest_path)
    SignManifestCmd.sign_manifest(manifest_path, private_key_path, envelope_path)
    VerifyManifestCmd.verify_manifest(manifest_path, envelope_path, public_key_path)

    assert _artifact_names(manifest_path) == [
        'system-security-plans/acme/ssp.json',
        'profiles/nist-low/profile.json',
        'catalogs/nist/catalog.json',
    ]
    assert envelope_path.is_file()
