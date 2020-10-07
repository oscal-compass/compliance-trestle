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
"""Tests for trestle split command."""
from trestle.core.commands import cmd_utils
from trestle.core.commands.split import SplitCmd
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.plans import Plan


def test_split_model(tmp_dir, sample_target):
    """Test for split_model method."""
    # trestle split -f target.yaml -e target-definition.metadata
    element = Element(sample_target)
    element_args = ['target-definition.metadata']
    element_paths = cmd_utils.parse_element_args(element_args)

    # extract values
    metadata_file = element_paths[0].to_file_path()
    metadata = element.get_at(element_paths[0])

    root_file = element_paths[0].to_root_path()
    remaining_root = element.set_at(element_paths[0], None)

    # prepare the plan
    expected_plan = Plan()
    expected_plan.add_action(CreatePathAction(metadata_file))
    expected_plan.add_action(WriteFileAction(metadata_file, metadata))
    expected_plan.add_action(WriteFileAction(root_file, remaining_root))

    cmd = SplitCmd()
    split_plan = cmd.split_model(sample_target, element_paths)
    assert expected_plan == split_plan


def test_split_model_multiple_levels(tmp_dir, sample_target):
    """Test for split_model method."""
    # trestle split -f target.yaml -e target-definition.targets.*.target-control-implementations.*
