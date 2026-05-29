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
"""Tests for trestle canonicalize command."""

import argparse
import pathlib
import sys

from _pytest.monkeypatch import MonkeyPatch

import pytest

from tests import test_utils

import trestle.common.const as const
import trestle.core.commands.import_ as importcmd
from trestle.cli import Trestle
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.canonicalize import CanonicalizeCmd
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.oscal.catalog import Catalog


class StdoutWithoutBuffer:
    """Test stdout object that only supports text writes."""

    def __init__(self) -> None:
        self.value = ''

    def write(self, text: str) -> int:
        """Write text to the test stdout object."""
        self.value += text
        return len(text)


def test_canonicalize_writes_output_file(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Canonicalize should write RFC 8785 bytes to the specified output file."""
    input_path = tmp_path / 'artifact.json'
    output_path = tmp_path / 'artifact.canonical.json'
    input_path.write_text('{"b":2,"a":1}', encoding=const.FILE_ENCODING)

    monkeypatch.setattr(sys, 'argv', ['trestle', 'canonicalize', '-f', str(input_path), '-o', str(output_path)])

    assert Trestle().run() == CmdReturnCodes.SUCCESS.value
    assert output_path.read_bytes() == b'{"a":1,"b":2}'


def test_canonicalize_imported_nist_800_53_catalog_remains_oscal_readable(tmp_trestle_dir: pathlib.Path) -> None:
    """A real imported NIST 800-53 catalog should still load after canonicalization."""
    source_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    import_args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=str(source_path), output='nist_800_53', verbose=1, regenerate=False
    )

    assert importcmd.ImportCmd()._run(import_args) == CmdReturnCodes.SUCCESS.value

    imported_path = tmp_trestle_dir / 'catalogs/nist_800_53/catalog.json'
    imported_catalog = Catalog.oscal_read(imported_path)
    assert imported_catalog is not None

    canonical_path = tmp_trestle_dir / 'catalogs/nist_800_53/catalog.canonical.json'
    CanonicalizeCmd.canonicalize(imported_path, canonical_path)

    canonical_catalog = Catalog.oscal_read(canonical_path)
    assert canonical_catalog is not None
    assert ModelUtils.models_are_equivalent(imported_catalog, canonical_catalog)
    assert b'\n' not in canonical_path.read_bytes()


def test_canonicalize_writes_stdout(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Canonicalize should write canonical JSON to stdout when output is omitted."""
    input_path = tmp_path / 'artifact.json'
    input_path.write_text('{"b":2,"a":1}', encoding=const.FILE_ENCODING)

    monkeypatch.setattr(sys, 'argv', ['trestle', 'canonicalize', '-f', str(input_path)])

    assert Trestle().run() == CmdReturnCodes.SUCCESS.value
    output, _ = capsys.readouterr()
    assert output == '{"a":1,"b":2}'


def test_canonicalize_rejects_non_json_input(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Canonicalize should reject non-JSON file extensions."""
    input_path = tmp_path / 'artifact.yaml'
    input_path.write_text('a: 1', encoding=const.FILE_ENCODING)
    monkeypatch.setattr(sys, 'argv', ['trestle', 'canonicalize', '-f', str(input_path)])

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value


def test_canonicalize_rejects_output_directory(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Canonicalize should reject output paths that are directories."""
    input_path = tmp_path / 'artifact.json'
    input_path.write_text('{"a":1}', encoding=const.FILE_ENCODING)
    monkeypatch.setattr(sys, 'argv', ['trestle', 'canonicalize', '-f', str(input_path), '-o', str(tmp_path)])

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value


def test_canonicalize_rejects_missing_file(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Canonicalize should fail clearly if the input path is missing."""
    monkeypatch.setattr(sys, 'argv', ['trestle', 'canonicalize', '-f', str(tmp_path / 'missing.json')])

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value


def test_canonicalize_rejects_invalid_json(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Canonicalize should reject invalid JSON."""
    input_path = tmp_path / 'artifact.json'
    input_path.write_text('{"a":', encoding=const.FILE_ENCODING)
    monkeypatch.setattr(sys, 'argv', ['trestle', 'canonicalize', '-f', str(input_path)])

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value


def test_canonicalize_rejects_duplicate_keys(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Canonicalize should reject duplicate JSON object keys."""
    input_path = tmp_path / 'artifact.json'
    input_path.write_text('{"a":1,"a":2}', encoding=const.FILE_ENCODING)
    monkeypatch.setattr(sys, 'argv', ['trestle', 'canonicalize', '-f', str(input_path)])

    assert Trestle().run() == CmdReturnCodes.COMMAND_ERROR.value


def test_write_stdout_falls_back_to_text_stdout(monkeypatch: MonkeyPatch) -> None:
    """Canonicalize should support stdout objects without a buffer attribute."""
    stdout = StdoutWithoutBuffer()
    monkeypatch.setattr(sys, 'stdout', stdout)

    CanonicalizeCmd._write_stdout(b'{"a":1}')

    assert stdout.value == '{"a":1}'
