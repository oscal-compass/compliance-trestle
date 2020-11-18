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
import pathlib
import sys
from unittest.mock import patch

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


def test_create_object(tmp_trestle_dir: pathlib.Path) -> None:
    """Happy path test at the cli level."""
    # Test
    testargs_root = ['trestle', 'create']
    for subcommand in subcommand_list:
        test_args = testargs_root + [subcommand] + ['-n', f'random_named_{subcommand}']
        with patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 0


def test_no_dir(tmpdir: pathlib.Path) -> None:
    """Test for no trestle directory."""
    pass


def test_broken_args(tmp_trestle_dir: pathlib.Path) -> None:
    """Test behaviour on broken arguments."""
    pass
