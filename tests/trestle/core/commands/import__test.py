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
"""Tests for trestle import command."""
import os
import pathlib
import sys
from unittest.mock import patch

from tests import test_utils

from trestle.cli import Trestle

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


def test_import_cmd(tmp_dir: pathlib.Path) -> None:
    """Happy path test at the cli level."""
    # Input file, catalog:
    catalog_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH.absolute(), 'minimal_catalog.json')
    # Input file, profile:
    profile_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH.absolute(), 'good_profile.json')
    # Input file, target:
    target_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH.absolute(), 'sample-target-definition.json')
    # Temporary directory for trestle init to trestle import into
    os.chdir(tmp_dir.absolute())
    init_args = ['trestle', 'init']
    with patch.object(sys, 'argv', init_args):
        # Init tmp_dir
        Trestle().run()
        # Test
        test_args = ['trestle', 'import', '-f', str(catalog_file_path), '-o', 'imported']
        with patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 0
        # Test
        test_args = ['trestle', 'import', '-f', str(profile_file_path), '-o', 'imported']
        with patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 0
        # Test
        test_args = ['trestle', 'import', '-f', str(target_file_path), '-o', 'imported']
        with patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 0


def test_import_missing_input(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for missing input argument."""
    # Test
    # This can't be tested cleanly because the SystemExit:2 comes from cli.py
    pass


def test_import_bad_input_extension(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for bad input extension."""
    # Test
    test_args = ['trestle', 'import', '-f', 'random_named_file.txt', '-o', 'catalog']
    with patch.object(sys, 'argv', test_args):
        try:
            Trestle().run()
        except Exception:
            assert True
        else:
            AssertionError()


def test_import_success(tmp_dir):
    """Test for success across multiple models."""
    pass


def test_import_failure_invalid_model(tmp_dir):
    """Test model failures throw errors and exit badly."""
    pass


def test_failure_reference_inside_trestle_project(tmp_dir):
    """Ensure failure if a reference pulls in an object which is inside the current context."""
    pass


def test_failure_duplicate_output_key(tmp_dir):
    """Fail if output name and type is duplicated."""
    pass
