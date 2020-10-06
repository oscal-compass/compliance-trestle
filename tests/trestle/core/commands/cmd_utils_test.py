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
from typing import List

from trestle.core.commands import cmd_utils
from trestle.core.models.elements import ElementPath


def prepare_expected_element_paths(element_args: List[str]) -> List[ElementPath]:
    """Prepare a list of ElementPath from a list of path strings."""
    element_paths: List[ElementPath] = []
    for element_arg in element_args:
        element_paths.append(ElementPath(element_arg))

    return element_paths


def test_parse_element_arg():
    """Unit test parse a single element arg."""
    element_arg = 'target-definition.targets'
    expected_paths: List[ElementPath] = prepare_expected_element_paths(['target-definition.targets'])
    element_paths: List[ElementPath] = cmd_utils.parse_element_arg(element_arg)
    assert expected_paths == element_paths

    element_arg = 'target-definition.targets.*'
    expected_paths: List[ElementPath] = prepare_expected_element_paths(['target-definition.targets.*'])
    element_paths: List[ElementPath] = cmd_utils.parse_element_arg(element_arg)
    assert expected_paths == element_paths

    element_arg = 'catalog.groups.*.controls.*.controls.*'
    p1 = ElementPath('catalog.groups.*')
    p2 = ElementPath('controls.*', parent_path=p1)
    p3 = ElementPath('controls.*', parent_path=p2)
    expected_paths: List[ElementPath] = [p1, p2, p3]
    element_paths: List[ElementPath] = cmd_utils.parse_element_arg(element_arg)
    assert expected_paths == element_paths


def test_parse_element_args():
    """Unit test parse multiple element args."""
    element_args = ['catalog.metadata', 'catalog.groups', 'catalog.controls']
    p0 = ElementPath('catalog.metadata')
    p1 = ElementPath('catalog.groups')
    p2 = ElementPath('catalog.controls')
    expected_paths: List[ElementPath] = [p0, p1, p2]
    element_paths = cmd_utils.parse_element_args(element_args)
    assert expected_paths == element_paths

    # element args with wildcard
    element_args = ['catalog.metadata', 'catalog.groups.*.controls.*.controls.*', 'catalog.controls.*.controls.*']
    p0 = ElementPath('catalog.metadata')
    p1 = ElementPath('catalog.groups.*')
    p2 = ElementPath('controls.*', parent_path=p1)
    p3 = ElementPath('controls.*', parent_path=p2)
    p4 = ElementPath('catalog.controls.*')
    p5 = ElementPath('controls.*', parent_path=p4)
    expected: List[ElementPath] = [p0, p1, p2, p3, p4, p5]
    assert cmd_utils.parse_element_args(element_args) == expected
