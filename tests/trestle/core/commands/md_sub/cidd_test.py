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
"""Tests for trestle md cidd subcommand."""
import pathlib
import sys
from unittest import mock

import pytest

import trestle.cli


@pytest.mark.parametrize('command_string, return_code', [('trestle md cidd setup --pave', 0)])
def test_cidd_placeholder(tmp_trestle_dir: pathlib.Path, command_string: str, return_code: int) -> None:
    """Simple execution tests of trestle md cidd - as currently executing."""
    with mock.patch.object(sys, 'argv', command_string.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            # FIXME: Needs to be changed once implemented.
            assert wrapped_error == SystemExit
            assert wrapped_error.code == return_code
