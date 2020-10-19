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
"""Tests for trestle cmd utils module."""
import os
import pathlib
from typing import List

import pytest

from tests import test_utils

from trestle.core import const
from trestle.core.commands import cmd_utils
from trestle.core.err import TrestleError
from trestle.core.models.elements import ElementPath
from trestle.oscal import target
from trestle.utils import fs


def prepare_expected_element_paths(element_args: List[str]) -> List[ElementPath]:
    """Prepare a list of ElementPath from a list of path strings."""
    element_paths: List[ElementPath] = []
    for element_arg in element_args:
        element_paths.append(ElementPath(element_arg))

    return element_paths


def test_copy_values(sample_target: target.TargetDefinition):
    """Test copy_values function."""
    metadata_values = sample_target.metadata.__dict__
    metadata_values['title'] = 'TEST'
    sample_metadata2: target.Metadata = target.Metadata(**metadata_values)
    assert sample_metadata2 is not sample_target.metadata

    cmd_utils.copy_values(sample_target.metadata, sample_metadata2)
    assert sample_metadata2 == sample_target.metadata


def test_parse_element_arg(tmp_dir):
    """Unit test parse a single element arg."""
    element_arg = 'target-definition.targets'
    expected_paths: List[ElementPath] = prepare_expected_element_paths(['target-definition.targets'])
    element_paths: List[ElementPath] = cmd_utils.parse_element_arg(element_arg, False)
    assert expected_paths == element_paths

    element_arg = 'target-definition.targets.*'
    expected_paths: List[ElementPath] = prepare_expected_element_paths(['target-definition.targets.*'])
    element_paths: List[ElementPath] = cmd_utils.parse_element_arg(element_arg, False)
    assert expected_paths == element_paths

    element_arg = 'catalog.groups.*.controls.*.controls.*'
    p1 = ElementPath('catalog.groups.*')
    p2 = ElementPath('group.controls.*', parent_path=p1)
    p3 = ElementPath('control.controls.*', parent_path=p2)
    expected_paths: List[ElementPath] = [p1, p2, p3]
    element_paths: List[ElementPath] = cmd_utils.parse_element_arg(element_arg, False)
    assert expected_paths == element_paths

    element_arg = 'catalog.groups.*.controls'
    p1 = ElementPath('catalog.groups.*')
    p2 = ElementPath('group.controls', parent_path=p1)
    expected_paths: List[ElementPath] = [p1, p2]
    element_paths: List[ElementPath] = cmd_utils.parse_element_arg(element_arg, False)
    assert expected_paths == element_paths

    element_arg = 'target-definition.targets.*.target-control-implementations'
    p1 = ElementPath('target-definition.targets.*')
    p2 = ElementPath('target.target-control-implementations', parent_path=p1)
    expected_paths: List[ElementPath] = [p1, p2]
    element_paths: List[ElementPath] = cmd_utils.parse_element_arg(element_arg, False)
    assert expected_paths == element_paths

    element_arg = 'target-definition.targets.*.target-control-implementations.*'
    p1 = ElementPath('target-definition.targets.*')
    p2 = ElementPath('target.target-control-implementations.*', parent_path=p1)
    expected_paths: List[ElementPath] = [p1, p2]
    element_paths: List[ElementPath] = cmd_utils.parse_element_arg(element_arg, False)
    assert expected_paths == element_paths

    # use contextual path for parsing path
    test_utils.ensure_trestle_config_dir(tmp_dir)
    target_def_dir: pathlib.Path = tmp_dir / 'target-definitions/mytarget/'
    fs.ensure_directory(target_def_dir)
    cur_dir = pathlib.Path.cwd()
    os.chdir(target_def_dir)
    element_arg = 'metadata.parties.*'
    expected_paths: List[ElementPath] = prepare_expected_element_paths(['metadata.parties.*'])
    element_paths: List[ElementPath] = cmd_utils.parse_element_arg(element_arg, True)
    assert expected_paths == element_paths
    os.chdir(cur_dir)


def test_parse_element_args():
    """Unit test parse multiple element args."""
    element_args = ['catalog.metadata', 'catalog.groups', 'catalog.controls']
    p0 = ElementPath('catalog.metadata')
    p1 = ElementPath('catalog.groups')
    p2 = ElementPath('catalog.controls')
    expected_paths: List[ElementPath] = [p0, p1, p2]
    element_paths = cmd_utils.parse_element_args(element_args, False)
    assert expected_paths == element_paths

    # element args with wildcard
    element_args = ['catalog.metadata', 'catalog.groups.*.controls.*.controls.*', 'catalog.controls.*.controls.*']
    p0 = ElementPath('catalog.metadata')
    p1 = ElementPath('catalog.groups.*')
    p2 = ElementPath('group.controls.*', parent_path=p1)
    p3 = ElementPath('control.controls.*', parent_path=p2)
    p4 = ElementPath('catalog.controls.*')
    p5 = ElementPath('control.controls.*', parent_path=p4)
    expected: List[ElementPath] = [p0, p1, p2, p3, p4, p5]
    assert cmd_utils.parse_element_args(element_args, False) == expected


def test_get_trash_file_path(tmp_dir):
    """Test get_trash_file_path method."""
    tmp_file = tmp_dir / 'tmp_file.md'
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    with pytest.raises(TrestleError):
        cmd_utils.get_trash_file_path(readme_file)

    test_utils.ensure_trestle_config_dir(tmp_dir)

    assert cmd_utils.get_trash_file_path(tmp_file) is not None
    assert cmd_utils.get_trash_file_path(tmp_file).parent.name == pathlib.Path(const.TRESTLE_TRASH_DIR).name
    assert cmd_utils.get_trash_file_path(readme_file).parent.name == 'data'


def test_move_to_trash(tmp_dir):
    """Test move_to_trash command."""
    test_utils.ensure_trestle_config_dir(tmp_dir)
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    assert not cmd_utils.get_trash_file_path(readme_file).exists()
    cmd_utils.move_to_trash(readme_file)
    assert readme_file.exists() is False
    assert cmd_utils.get_trash_file_path(readme_file).exists()
