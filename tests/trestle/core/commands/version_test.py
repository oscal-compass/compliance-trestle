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
"""Test for cli module command version."""
import pathlib

from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils
from tests.test_utils import execute_command_and_assert

from trestle import __version__
from trestle.oscal import OSCAL_VERSION


def test_version(monkeypatch: MonkeyPatch) -> None:
    """Test version output."""
    testcmd = 'trestle version'
    execute_command_and_assert(testcmd, 0, monkeypatch)


def test_oscal_obj_version(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch, capsys) -> None:
    """Test OSCAL object version output."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, True)
    testcmd = 'trestle version -n test_profile_c -t profile'
    execute_command_and_assert(testcmd, 0, monkeypatch)
    output, _ = capsys.readouterr()
    assert 'Version of OSCAL object of test_profile_c profile is: 2021-01-01' in output

    testcmd = 'trestle version -n test_profile_c'
    execute_command_and_assert(testcmd, 1, monkeypatch)

    testcmd = 'trestle version -n test_profile_c -t nonexisting'
    execute_command_and_assert(testcmd, 1, monkeypatch)

    testcmd = 'trestle version'
    execute_command_and_assert(testcmd, 0, monkeypatch)
    output, _ = capsys.readouterr()
    assert f'Trestle version v{__version__} based on OSCAL version {OSCAL_VERSION}' in output

    testcmd = 'trestle version -n complex_cat -t catalog'
    execute_command_and_assert(testcmd, 0, monkeypatch)
    output, _ = capsys.readouterr()
    assert 'Version of OSCAL object of complex_cat catalog is: REPLACE_ME' in output

    comp_name = test_utils.setup_for_component_definition(tmp_trestle_dir, monkeypatch)
    testcmd = f'trestle version -n {comp_name} -t component-definition'
    execute_command_and_assert(testcmd, 0, monkeypatch)
    output, _ = capsys.readouterr()
    assert f'Version of OSCAL object of {comp_name} component-definition is: 0.21.0' in output
