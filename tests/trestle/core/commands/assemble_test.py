# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for trestle assemble command."""
import argparse
import pathlib
import sys
import shutil
from unittest import mock

import pytest

import trestle.core.err as err
from trestle.cli import Trestle
from trestle.core.commands import assemble
from trestle.oscal.catalog import Catalog
from trestle.utils.load_distributed import load_distributed

subcommand_list = [
    'catalog',
    'profile',
    'target-definition',
    'component-definition',
    'system-security-plan',
    'assessment-plan',
    'assessment-results',
    'plan-of-action-and-milestones'
]


def test_run_and_missing_model(tmp_trestle_dir: pathlib.Path) -> None:
    """Test _run and test it fails without top level model file"""
    testargs_root = ['trestle', 'assemble']
    for subcommand in subcommand_list:
        test_args = testargs_root + [subcommand] + ['-n', f'my_{subcommand}'] + ['-x', 'json']
        with mock.patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc != 0


def test_assemble_catalog(testdata_dir, tmp_trestle_dir: pathlib.Path) -> None:
    """Test assembling a catalog"""
    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'
    catalogs_dir = pathlib.Path('catalogs/')
    mycatalog_dir = catalogs_dir / 'mycatalog'
    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.rmtree(pathlib.Path('dist'))
    shutil.copytree(test_data_source, catalogs_dir)

    testargs = ['trestle', 'assemble', 'catalog', '-n', 'mycatalog', '-x', 'json']
    with mock.patch.object(sys, 'argv', testargs):
        rc = Trestle().run()
        assert rc == 0

    # Read assembled model
    actual_model = Catalog.oscal_read(pathlib.Path('dist/catalog.json'))
    _, _, expected_model = load_distributed(mycatalog_dir / 'catalog.json')

    assert actual_model == expected_model
