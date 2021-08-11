# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Tests for the partial-object-validate command."""
import pathlib
import sys

from _pytest.monkeypatch import MonkeyPatch

import pytest

from trestle.cli import Trestle
from trestle.core.commands.partial_object_validate import PartialObjectValidate


def test_missing_file(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test what happens when a file is missing."""
    fake_catalog_path = tmp_path / 'catalog.json'
    element_str = 'catalog'
    command_str = f'trestle partial-object-validate -f {str(fake_catalog_path)} -e {element_str}'
    monkeypatch.setattr(sys, 'argv', command_str.split())
    rc = Trestle().run()
    assert rc == 1


@pytest.mark.parametrize(
    ['sample_file', 'element_path', 'rc'],
    [
        (pathlib.Path('json/minimal_catalog.json'), 'catalog', 0),
        (pathlib.Path('json/minimal_catalog.json'), 'catalog.metadata', 1),
        (pathlib.Path('split_merge/load_distributed/groups.json'), 'catalog.groups', 0),
        (pathlib.Path('split_merge/load_distributed/groups.json'), 'catalog.groups.group.groups', 0),
        (pathlib.Path('split_merge/load_distributed/groups.json'), 'catalog.groups.group', 1),
        (pathlib.Path('json/minimal_catalog_missing_uuid.json'), 'catalog', 1)
    ]
)
def test_partial_object_validate(
    sample_file: pathlib.Path, element_path: str, rc: int, testdata_dir: pathlib.Path
) -> None:
    """Test partial object validation with various combinations."""
    full_path = testdata_dir / sample_file
    actual_rc = PartialObjectValidate.partial_object_validate(full_path, element_path)

    assert rc == actual_rc
