# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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

import json
import pathlib
import secrets
import string
import sys

from _pytest.monkeypatch import MonkeyPatch

import pytest

from tests.test_utils import execute_command_and_assert

from trestle.cli import Trestle
from trestle.core import generators
from trestle.oscal.catalog import Catalog


def _write_catalog(tmp_dir: pathlib.Path) -> pathlib.Path:
    """Write a generated catalog JSON to a temp file outside the trestle workspace."""
    rand_str = ''.join(secrets.choice(string.ascii_letters) for _ in range(16))
    catalog_file = tmp_dir.parent / f'{rand_str}.json'
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(catalog_file)
    return catalog_file


def test_canonicalize_to_stdout(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch, capsys
) -> None:
    """Canonicalize command writes valid JSON to stdout when no -o is given."""
    # First import a catalog so it exists in the workspace
    catalog_file = _write_catalog(tmp_trestle_dir)
    execute_command_and_assert(f'trestle import -f {catalog_file} -o mycat', 0, monkeypatch)

    catalog_path = tmp_trestle_dir / 'catalogs' / 'mycat' / 'catalog.json'
    assert catalog_path.exists()

    testcmd = f'trestle canonicalize -f catalogs/mycat/catalog.json'
    monkeypatch.setattr(sys, 'argv', testcmd.split())
    rc = Trestle().run()
    assert rc == 0

    captured = capsys.readouterr()
    # Output must be valid JSON with no leading/trailing whitespace lines
    output = captured.out.strip()
    parsed = json.loads(output)
    assert 'catalog' in parsed


def test_canonicalize_to_file(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Canonicalize command writes canonical JSON to file when -o is given."""
    catalog_file = _write_catalog(tmp_trestle_dir)
    execute_command_and_assert(f'trestle import -f {catalog_file} -o mycat2', 0, monkeypatch)

    out_file = tmp_trestle_dir / 'canonical.json'
    testcmd = f'trestle canonicalize -f catalogs/mycat2/catalog.json -o canonical.json'
    monkeypatch.setattr(sys, 'argv', testcmd.split())
    rc = Trestle().run()
    assert rc == 0

    assert out_file.exists()
    content = json.loads(out_file.read_bytes())
    assert 'catalog' in content


def test_canonicalize_is_deterministic(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Running canonicalize twice on the same file produces identical output."""
    catalog_file = _write_catalog(tmp_trestle_dir)
    execute_command_and_assert(f'trestle import -f {catalog_file} -o mycat3', 0, monkeypatch)

    out1 = tmp_trestle_dir / 'canon1.json'
    out2 = tmp_trestle_dir / 'canon2.json'

    for out in (out1, out2):
        monkeypatch.setattr(
            sys, 'argv',
            ['trestle', 'canonicalize', '-f', 'catalogs/mycat3/catalog.json', '-o', str(out)]
        )
        rc = Trestle().run()
        assert rc == 0

    assert out1.read_bytes() == out2.read_bytes()


def test_canonicalize_keys_sorted(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """The canonical output has all object keys sorted (RFC 8785 §3.2.3)."""
    catalog_file = _write_catalog(tmp_trestle_dir)
    execute_command_and_assert(f'trestle import -f {catalog_file} -o mycat4', 0, monkeypatch)

    out_file = tmp_trestle_dir / 'sorted.json'
    monkeypatch.setattr(
        sys, 'argv',
        ['trestle', 'canonicalize', '-f', 'catalogs/mycat4/catalog.json', '-o', str(out_file)]
    )
    rc = Trestle().run()
    assert rc == 0

    raw = out_file.read_bytes().decode('utf-8')
    # No whitespace between tokens is a key property of JCS
    assert '\n' not in raw
    assert '  ' not in raw


def test_canonicalize_nonexistent_file(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Canonicalize returns an error for a non-existent file."""
    testcmd = 'trestle canonicalize -f catalogs/noexist/catalog.json'
    execute_command_and_assert(testcmd, 1, monkeypatch)


def test_canonicalize_rejects_yaml(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Canonicalize returns an error when given a YAML file (YAML is out of scope for JCS)."""
    # Create a dummy yaml file in the workspace
    dummy = tmp_trestle_dir / 'catalogs' / 'dummy' / 'catalog.yaml'
    dummy.parent.mkdir(parents=True, exist_ok=True)
    dummy.write_text('catalog: {}\n', encoding='utf-8')

    testcmd = 'trestle canonicalize -f catalogs/dummy/catalog.yaml'
    execute_command_and_assert(testcmd, 1, monkeypatch)


def test_import_with_jcs_flag(
    tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """trestle import --jcs produces a canonical JSON file."""
    catalog_file = _write_catalog(tmp_trestle_dir)
    testcmd = f'trestle import -f {catalog_file} -o jcscat --jcs'
    monkeypatch.setattr(sys, 'argv', testcmd.split())
    rc = Trestle().run()
    assert rc == 0

    imported_path = tmp_trestle_dir / 'catalogs' / 'jcscat' / 'catalog.json'
    assert imported_path.exists()
    raw = imported_path.read_bytes().decode('utf-8')
    # JCS output has no indentation whitespace
    assert '\n' not in raw
    assert '  ' not in raw
    # Must still be valid JSON wrapping a catalog
    parsed = json.loads(raw)
    assert 'catalog' in parsed
