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
from tests import test_utils

from trestle.core import const
from trestle.core import utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.commands import cmd_utils
from trestle.core.commands.split import SplitCmd
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.oscal.target import TargetDefinition
from trestle.utils import fs


def test_split_model(tmp_dir, sample_target: OscalBaseModel):
    """Test for split_model method."""
    # Assume we are running a command like below
    # trestle split -f target-definition.yaml -e target-definition.metadata

    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_dir)
    target_def_dir = tmp_dir / 'target-definitions' / 'mytarget'
    target_def_file = target_def_dir / 'target-definition.yaml'
    fs.ensure_directory(target_def_dir)
    sample_target.oscal_write(target_def_file)

    content_type = FileContentType.YAML

    # read the model from file
    target_def = TargetDefinition.oscal_read(target_def_file)
    element = Element(target_def)
    element_args = ['target-definition.metadata']
    element_paths = cmd_utils.parse_element_args(element_args)

    # extract values
    metadata_file = target_def_dir / element_paths[0].to_file_path(content_type)
    metadata = element.get_at(element_paths[0])

    root_file = target_def_dir / element_paths[0].to_root_path(content_type)
    remaining_root = element.get().stripped_instance(element_paths[0].get_element_name())

    # prepare the plan
    expected_plan = Plan()
    expected_plan.add_action(CreatePathAction(metadata_file))
    expected_plan.add_action(WriteFileAction(metadata_file, Element(metadata), content_type))
    expected_plan.add_action(CreatePathAction(root_file))
    expected_plan.add_action(WriteFileAction(root_file, Element(remaining_root), content_type))

    split_plan = SplitCmd.split_model(target_def, element_paths, target_def_dir, content_type)
    assert expected_plan == split_plan


def test_split_multiple_item_dict(tmp_dir, sample_target):
    """Test for split_model method."""
    # Assume we are running a command like below
    # trestle split -f target.yaml -e target-definition.targets.*

    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_dir)
    target_def_dir = tmp_dir / 'target-definitions' / 'mytarget'
    target_def_file = target_def_dir / 'target-definition.yaml'
    fs.ensure_directory(target_def_dir)
    sample_target.oscal_write(target_def_file)

    content_type = FileContentType.YAML
    file_ext = FileContentType.to_file_extension(content_type)

    # read the model from file
    target_def = TargetDefinition.oscal_read(target_def_file)
    element = Element(target_def)
    element_args = ['target-definition.targets.*']
    element_paths = cmd_utils.parse_element_args(element_args)

    expected_plan = Plan()

    # extract values
    sub_models: dict = element.get_at(element_paths[0])
    sub_model_dir = target_def_dir / element_paths[0].to_file_path()
    for key in sub_models:
        sub_model_item = sub_models[key]
        model_type = utils.classname_to_alias(type(sub_model_item).__name__, 'json')
        file_name = f'{key}{const.IDX_SEP}{model_type}{file_ext}'
        file_path = sub_model_dir / file_name
        expected_plan.add_action(CreatePathAction(file_path))
        expected_plan.add_action(WriteFileAction(file_path, Element(sub_model_item), content_type))

    root_file = target_def_dir / element_paths[0].to_root_path(content_type)
    remaining_root = element.get().stripped_instance(element_paths[0].get_element_name())
    expected_plan.add_action(CreatePathAction(root_file))
    expected_plan.add_action(WriteFileAction(root_file, Element(remaining_root), content_type))

    split_plan = SplitCmd.split_model(target_def, element_paths, target_def_dir, content_type)
    assert expected_plan == split_plan
