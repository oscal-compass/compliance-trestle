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
"""Tests for trestle create command."""
import argparse
import pathlib
import sys
from unittest import mock

import pytest

import trestle.core.err as err
from trestle.cli import Trestle
from trestle.core.commands import create
from trestle.oscal.catalog import Catalog

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


def test_create_cmd(tmp_trestle_dir: pathlib.Path) -> None:
    """Happy path test at the cli level."""
    # Test
    testargs_root = ['trestle', 'create']
    for subcommand in subcommand_list:
        test_args = testargs_root + [subcommand] + ['-n', f'random_named_{subcommand}']
        with mock.patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 0


def test_create_object_directly(tmp_trestle_dir: pathlib.Path) -> None:
    """Simple test of create object only."""
    pass


def test_no_dir(tmp_empty_cwd: pathlib.Path) -> None:
    """Test for no trestle directory."""
    # Setup argparse
    args = argparse.Namespace(extension='json', name='catalog', verbose=0)
    rc = create.CreateCmd.create_object('catalog', Catalog, args)
    # check for non zero return code.
    assert rc > 0


def test_fail_overwrite(tmp_trestle_dir: pathlib.Path) -> None:
    """Test that a failure occurs when doubling up a create."""
    args = argparse.Namespace(extension='json', name='my_catalog', verbose=0)
    rc = create.CreateCmd.create_object('catalog', Catalog, args)
    assert rc == 0
    rc = create.CreateCmd.create_object('catalog', Catalog, args)
    assert rc > 0


def test_broken_args(tmp_trestle_dir: pathlib.Path) -> None:
    """Test behaviour on broken arguments."""
    # must be done using sys patching.
    testargs_root = ['trestle', 'create']
    with mock.patch.object(sys, 'argv', testargs_root):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            Trestle().run()
            assert pytest_wrapped_e.type == SystemExit
            assert pytest_wrapped_e.value.code > 0
    testargs = testargs_root + ['catalog']
    # missing command
    with mock.patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            Trestle().run()
            assert pytest_wrapped_e.type == SystemExit
            assert pytest_wrapped_e.value.code > 0
    # missing mandatory args
    testargs = testargs + ['-x', 'json']
    with mock.patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            Trestle().run()
            assert pytest_wrapped_e.type == SystemExit
            assert pytest_wrapped_e.value.code > 0
    testargs = testargs + ['-n', 'name']
    # correct behavior
    with mock.patch.object(sys, 'argv', testargs):
        rc = Trestle().run()
    assert rc == 0
    # correct behavior
    testargs[2] = 'bad_name'
    with mock.patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            Trestle().run()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code > 0


def test_execute_failure(tmp_trestle_dir: pathlib.Path) -> None:
    """Ensure create plan failure will return clean return codes from run."""
    args = argparse.Namespace(extension='json', name='my_catalog', verbose=0)

    with mock.patch('trestle.core.models.plans.Plan.simulate') as simulate_mock:
        simulate_mock.side_effect = err.TrestleError('stuff')
        rc = create.CreateCmd.create_object('catalog', Catalog, args)
        assert rc == 1
