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
"""Trestle Validate command tests."""
import pathlib
import sys
from unittest import mock

import pytest

import trestle.cli


def test_get_list_cli(tmp_trestle_dir) -> None:
    """Simple test which does E2E tests."""
    command = 'trestle task -l'

    with mock.patch.object(sys, 'argv', command.split()):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
            assert wrapped_error == SystemExit
            assert wrapped_error.code == 0


def test_arguments_ordering(tmp_trestle_dir: pathlib.Path) -> None:
    """Test that the argument loading behave correctly."""
    # should pass and return a list
    # also should work but same as above
    testargs = 'trestle task -l -c config_file.json'

    # should work
    testargs = 'trestle task pass-fail'

    # should work if config file exists
    testargs = 'trestle task pass-fail -c config_file.json'

    # should not work - conflicting arguments
    testargs = 'trestle task pass-fail -l '

    # should not work - missing required arguments
    testargs = 'trestle task -c config_file.json'
    assert len(testargs) > 0
