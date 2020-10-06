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


def test_parse_element_args():
    """Unit test parse element args method."""
#     element_args = ['target-definition.targets']
#     expected: List[ElementPath] = [ElementPath('target-definition.targets')]
#     assert cmd_utils.parse_element_args(element_args) == expected

#     element_args = ['target-definition.targets.*']
#     expected: List[ElementPath] = [
#         ElementPath('target-definition.targets.56666738-0f9a-4e38-9aac-c0fad00a5821'),
#         ElementPath('target-definition.targets.89cfe7a7-ce6b-4699-aa7b-2f5739c72001'),
#     ]
#     assert cmd_utils.parse_element_args(element_args) == expected
#     assert cmd_utils.parse_element_args(element_args) == expected

#     element_args = ['target-definition.metadata', 'target-definition.targets.*']
#     expected: List[ElementPath] = [
#         ElementPath('target-definition.metadata'),
#         ElementPath('target-definition.targets.*')
#     ]
#     assert cmd_utils.parse_element_args(element_args) == expected

#     element_args = ['target-definition.metadata', 'target-definition.targets.*.target-control-implementations.*']
#     expected: List[ElementPath] = [
#         ElementPath('target-definition.metadata'),
#         ElementPath('target-definition.targets.*'),
#         ElementPath('target.target-control-implementations.*'),
#     ]
#     assert cmd_utils.parse_element_args(element_args) == expected

#     # split element args
#     element_args = ['catalog.metadata', 'catalog.groups.*.controls.*.controls.*', 'catalog.controls.*.controls.*']
#     expected: List[ElementPath] = []
#     p0 = ElementPath(None, 'catalog.metadata')
#     p1 = ElementPath(None, 'catalog.groups.*')
#     p2 = ElementPath(p1, 'controls.*')
#     p3 = ElementPath(p2, 'controls.*')
#     p4 = ElementPath(None, 'catalog.controls.*')
#     p5 = ElementPath(p4, 'controls.*')
#     expected.append(p0, p1, p2, p3, p4, p5)
#     assert cmd_utils.parse_element_args(element_args) == expected

#     # merge
#     element_args = ['catalog.metadata', 'catalog.groups', 'catalog.controls']
#     expected: List[ElementPath] = []
#     p0 = ElementPath(None, 'catalog.metadata')
#     p1 = ElementPath(None, 'catalog.groups')
#     p2 = ElementPath(None, 'catalog.controls')
#     expected.append(p0, p1, p2)
#     assert cmd_utils.parse_element_args(element_args) == expected
