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
import sys

from _pytest.monkeypatch import MonkeyPatch

import pytest

from trestle import cli


def test_version(monkeypatch: MonkeyPatch) -> None:
    """Test version output."""
    testcmd = 'trestle version'
    monkeypatch.setattr(sys, 'argv', testcmd.split())
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.run()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
