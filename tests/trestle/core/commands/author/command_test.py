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
"""Tests for trestle author command module."""
import pathlib
import sys

from _pytest.monkeypatch import MonkeyPatch

import pytest

import trestle.cli


def test_governed_docs_cli(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test happy path of md governed-docs subcommand."""
    command = 'trestle author docs'
    monkeypatch.setattr(sys, 'argv', command.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
        # FIXME: Needs to be changed once implemented.
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == 2


def test_governed_folders_cli(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test happy path of author governed-folders subcommand."""
    command = 'trestle author folders'
    monkeypatch.setattr(sys, 'argv', command.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
        # FIXME: Needs to be changed once implemented.
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == 2


@pytest.mark.parametrize(
    'command_string', [('trestle author docs setup -tn test'), ('trestle author folders setup -tn test')]
)
def test_failure_not_trestle(command_string, tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test for failure based on not in trestle directory."""
    monkeypatch.setattr(sys, 'argv', command_string.split())
    with pytest.raises(SystemExit) as wrapped_error:
        trestle.cli.run()
        # FIXME: Needs to be changed once implemented.
    assert wrapped_error.type == SystemExit
    assert wrapped_error.value.code == 5
