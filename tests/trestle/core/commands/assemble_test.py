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
"""Tests for trestle assemble command."""
import argparse
import os
import pathlib
import shutil
import sys

from _pytest.monkeypatch import MonkeyPatch

import trestle.core.err as err
from trestle.cli import Trestle
from trestle.core import const
from trestle.core.commands.assemble import AssembleCmd
from trestle.core.models.plans import Plan
from trestle.oscal.catalog import Catalog
from trestle.utils.load_distributed import load_distributed

subcommand_list = const.MODEL_TYPE_LIST


def test_run_and_missing_model(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test _run and test it fails without top level model file."""
    testargs_root = ['trestle', 'assemble']
    for subcommand in subcommand_list:
        test_args = testargs_root + [subcommand] + ['-n', f'my_{subcommand}'] + ['-x', 'json']
        monkeypatch.setattr(sys, 'argv', test_args)
        rc = Trestle().run()
        assert rc != 0


def test_assemble_catalog(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test assembling a catalog."""
    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'
    catalogs_dir = tmp_trestle_dir / 'catalogs'
    mycatalog_dir = catalogs_dir / 'mycatalog'
    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.rmtree(pathlib.Path('dist'))
    shutil.copytree(test_data_source, catalogs_dir)

    testargs = ['trestle', 'assemble', 'catalog', '-n', 'mycatalog', '-x', 'json']
    monkeypatch.setattr(sys, 'argv', testargs)
    rc = Trestle().run()
    assert rc == 0

    # Read assembled model
    actual_model = Catalog.oscal_read(pathlib.Path('dist/catalogs/mycatalog.json'))
    _, _, expected_model = load_distributed(mycatalog_dir / 'catalog.json', tmp_trestle_dir)

    assert actual_model == expected_model


def test_assemble_not_trestle_project(tmp_empty_cwd: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test failure if not trestle project."""
    testargs = ['trestle', 'assemble', 'catalog', '-n', 'mycatalog', '-x', 'json']
    monkeypatch.setattr(sys, 'argv', testargs)
    rc = Trestle().run()
    assert rc == 5


def test_assemble_not_trestle_root(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test execution of assemble from a folder that is not trestle root."""
    os.chdir(pathlib.Path.cwd() / 'catalogs')
    testargs = ['trestle', 'assemble', 'catalog', '-n', 'mycatalog', '-x', 'json']
    monkeypatch.setattr(sys, 'argv', testargs)
    rc = Trestle().run()
    assert rc == 1


def test_assemble_execution_failure(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test execution of assemble plan fails."""

    def execute_mock(*args, **kwargs):
        raise err.TrestleError('execution failed')

    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'
    catalogs_dir = pathlib.Path('catalogs/')
    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.rmtree(pathlib.Path('dist'))
    shutil.copytree(test_data_source, catalogs_dir)
    monkeypatch.setattr(Plan, 'execute', execute_mock)
    rc = AssembleCmd().assemble_model(
        'catalog', argparse.Namespace(trestle_root=tmp_trestle_dir, name='mycatalog', extension='json', verbose=1)
    )
    assert rc == 1


def test_assemble_missing_top_model(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test assembling a catalog."""
    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'
    catalogs_dir = pathlib.Path('catalogs/')
    mycatalog_dir = catalogs_dir / 'mycatalog'
    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.rmtree(pathlib.Path('dist'))
    shutil.copytree(test_data_source, catalogs_dir)
    (mycatalog_dir / 'catalog.json').unlink()

    testargs = ['trestle', 'assemble', 'catalog', '-n', 'mycatalog', '-x', 'json']
    monkeypatch.setattr(sys, 'argv', testargs)
    rc = Trestle().run()
    assert rc == 1


def test_assemble_catalog_all(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test assembling all catalogs in trestle dir."""
    shutil.rmtree(pathlib.Path('dist'))
    catalogs_dir = tmp_trestle_dir / 'catalogs'
    my_names = ['mycatalog1', 'mycatalog2', 'mycatalog3']
    for my_name in my_names:
        test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs/mycatalog'
        shutil.copytree(test_data_source, catalogs_dir / my_name)

    testargs = ['trestle', 'assemble', 'catalog', '-t', '-x', 'json']
    monkeypatch.setattr(sys, 'argv', testargs)
    rc = Trestle().run()
    assert rc == 0

    # Read assembled model
    for my_name in my_names:
        _, _, expected_model = load_distributed(catalogs_dir / f'{my_name}/catalog.json', tmp_trestle_dir)
        actual_model = Catalog.oscal_read(pathlib.Path(f'dist/catalogs/{my_name}.json'))
        assert actual_model == expected_model

    testargs = ['trestle', 'assemble', 'profile', '-t', '-x', 'json']
    # Tests should pass on empty set of directories.
    monkeypatch.setattr(sys, 'argv', testargs)
    rc = Trestle().run()
    assert rc == 0
