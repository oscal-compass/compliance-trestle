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
"""Tests for trestle md command module."""
import pathlib
import sys
from unittest import mock

import pytest

import trestle.cli


def test_cidd_success_cli(tmp_trestle_dir: pathlib.Path) -> None:
    """Test happy path of md cidd subcommand from the cli."""
    command = 'trestle md cidd'
    with mock.patch.object(sys, 'argv', command.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            # FIXME: Needs to be changed once implemented.
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 1


def test_governed_docs_cli(tmp_trestle_dir: pathlib.Path) -> None:
    """Test happy path of md governed-docs subcommand."""
    command = 'trestle md governed-docs'
    with mock.patch.object(sys, 'argv', command.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            # FIXME: Needs to be changed once implemented.
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 1


def test_governed_folders_cli(tmp_trestle_dir: pathlib.Path) -> None:
    """Test happy path of md governed-folders subcommand."""
    command = 'trestle md governed-folders'
    with mock.patch.object(sys, 'argv', command.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            # FIXME: Needs to be changed once implemented.
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 1


def test_governed_projects_cli(tmp_trestle_dir: pathlib.Path) -> None:
    """Test happy path of md governed-projects subcommand."""
    command = 'trestle md governed-projects'
    with mock.patch.object(sys, 'argv', command.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            # FIXME: Needs to be changed once implemented.
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 1


@pytest.mark.parametrize(
    'command_string',
    [
        ('trestle md governed-docs setup -tn test'), ('trestle md governed-folders setup-tn test'),
        ('trestle md cidd setup')
    ]
)
def test_failure_not_trestle(command_string, tmp_path: pathlib.Path) -> None:
    """Test for failure based on not in trestle directory."""
    with mock.patch.object(sys, 'argv', command_string.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            # FIXME: Needs to be changed once implemented.
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 1
