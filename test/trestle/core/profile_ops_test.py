# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Profile operations - allows operations from profiles."""

import os
import pathlib

import trestle.core.parser as parser
import trestle.oscal.target as target


def test_profile_ops_init():
    """Stuff."""
    pass


def test_profile_naive_copy():
    """Create a target and copy across file."""
    target_path = pathlib.Path('test' + os.sep + 'data' + os.sep + 'json' + os.sep + 'sample-target-definition.json')
    # Test failure if file does not exist
    assert (target_path.exists())
    sample_td = parser.wrap_for_input(target.TargetDefinition).parse_file(target_path).target_definition
    assert (type(sample_td) == target.TargetDefinition)


def test_for_copy_behaviour():
    """Demonstrate how code will behave during tests."""
    target_path = pathlib.Path('test' + os.sep + 'data' + os.sep + 'json' + os.sep + 'sample-target-definition.json')
    # Test failure if file does not exist
    assert (target_path.exists())
    sample_td = parser.wrap_for_input(target.TargetDefinition).parse_file(target_path).target_definition
    assert (type(sample_td) == target.TargetDefinition)
