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
import os
import pathlib
import sys
from typing import List
from unittest.mock import patch

import pytest

from tests import test_utils

from trestle.cli import Trestle
from trestle.core import const
from trestle.core import utils
from trestle.core.commands import cmd_utils
from trestle.core.commands.split import SplitCmd
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.oscal import target as ostarget
from trestle.utils import fs


def prepare_trestle_project_dir(tmp_dir, content_type: FileContentType, sample_target: ostarget.TargetDefinition):
    """Prepare a temp directory with an example OSCAL model."""
    test_utils.ensure_trestle_config_dir(tmp_dir)
    file_ext = FileContentType.to_file_extension(content_type)
    target_def_dir = tmp_dir / 'target-definitions' / 'mytarget'
    target_def_file = target_def_dir / f'target-definition{file_ext}'
    fs.ensure_directory(target_def_dir)
    sample_target.oscal_write(target_def_file)

    return target_def_dir, target_def_file


def test_split_model(tmp_dir, sample_target: ostarget.TargetDefinition):
    """Test for split_model method."""
    # Assume we are running a command like below
    # trestle split -f target-definition.yaml -e target-definition.metadata

    content_type = FileContentType.YAML

    # prepare trestle project dir with the file
    target_def_dir, target_def_file = prepare_trestle_project_dir(tmp_dir, content_type, sample_target)

    # read the model from file
    target_def = ostarget.TargetDefinition.oscal_read(target_def_file)
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


def test_subsequent_split_model(tmp_dir, sample_target: ostarget.TargetDefinition):
    """Test subsequent split of sub models."""
    # Assume we are running a command like below
    # trestle split -f target-definition.yaml -e target-definition.metadata

    content_type = FileContentType.YAML

    # prepare trestle project dir with the file
    target_def_dir, target_def_file = prepare_trestle_project_dir(tmp_dir, content_type, sample_target)

    # first split the target-def into metadata
    target_def = ostarget.TargetDefinition.oscal_read(target_def_file)
    element = Element(target_def)
    element_args = ['target-definition.metadata']
    element_paths = cmd_utils.parse_element_args(element_args)
    metadata_file = target_def_dir / element_paths[0].to_file_path(content_type)
    metadata: ostarget.Metadata = element.get_at(element_paths[0])
    root_file = target_def_dir / element_paths[0].to_root_path(content_type)
    remaining_root = element.get().stripped_instance(element_paths[0].get_element_name())
    first_plan = Plan()
    first_plan.add_action(CreatePathAction(metadata_file))
    first_plan.add_action(WriteFileAction(metadata_file, Element(metadata), content_type))
    first_plan.add_action(CreatePathAction(root_file))
    first_plan.add_action(WriteFileAction(root_file, Element(remaining_root), content_type))
    first_plan.execute()  # this will split the files in the temp directory

    # now, prepare the expected plan to split metadta at parties
    second_plan = Plan()
    element_args = ['metadata.parties.*']
    element_paths = cmd_utils.parse_element_args(element_args)
    metadata2 = ostarget.Metadata.oscal_read(metadata_file)
    element = Element(metadata2)
    parties_dir = target_def_dir / 'metadata/parties'
    for i, party in enumerate(element.get_at(element_paths[0])):
        prefix = str(i).zfill(4)
        sub_model_actions = SplitCmd.prepare_sub_model_split_actions(party, parties_dir, prefix, content_type)
        second_plan.add_actions(sub_model_actions)

    # stripped metadata
    stripped_metadata = metadata2.stripped_instance(stripped_fields_aliases=['parties'])
    second_plan.add_action(CreatePathAction(metadata_file))
    second_plan.add_action(WriteFileAction(metadata_file, Element(stripped_metadata), content_type))

    # call the split command and compare the plans
    split_plan = SplitCmd.split_model(metadata, element_paths, target_def_dir, content_type)
    split_plan.execute()
    assert second_plan == split_plan


def test_split_multi_level_dict(tmp_dir, sample_target: ostarget.TargetDefinition):
    """Test for split_model method."""
    # Assume we are running a command like below
    # trestle split -f target.yaml -e target-definition.targets.*.target-control-implementations.*

    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_dir)
    target_def_dir = tmp_dir / 'target-definitions' / 'mytarget'
    target_def_file = target_def_dir / 'target-definition.yaml'
    fs.ensure_directory(target_def_dir)
    sample_target.oscal_write(target_def_file)

    content_type = FileContentType.YAML
    file_ext = FileContentType.to_file_extension(content_type)

    # read the model from file
    target_def: ostarget.TargetDefinition = ostarget.TargetDefinition.oscal_read(target_def_file)
    element = Element(target_def)
    element_args = ['target-definition.targets.*.target-control-implementations.*']
    element_paths: List[ElementPath] = cmd_utils.parse_element_args(element_args)

    expected_plan = Plan()

    # extract values
    targets: dict = element.get_at(element_paths[0])
    targets_dir = target_def_dir / element_paths[0].get_element_name()

    # create targets.yaml under targets dir
    element_name = element_paths[0].get_element_name()
    base_element = cmd_utils.get_dir_base_file_element(targets, element_name)
    dir_base_file = targets_dir / f'{element_name}{file_ext}'
    expected_plan.add_action(CreatePathAction(dir_base_file))
    expected_plan.add_action(WriteFileAction(dir_base_file, base_element, content_type))

    # split every targets
    for key in targets:
        # individual target dir
        target: ostarget.Target = targets[key]
        target_element = Element(targets[key])
        model_type = utils.classname_to_alias(type(target).__name__, 'json')
        dir_prefix = key
        dir_name = f'{dir_prefix}{const.IDX_SEP}{model_type}'
        target_dir = targets_dir / dir_name

        # target control impl dir for the target
        target_ctrl_impls: dict = target_element.get_at(element_paths[1])
        targets_ctrl_dir = target_dir / element_paths[1].to_file_path()

        # create target-control-implementations.yaml under target-control-implementations dir
        element_name = element_paths[1].get_element_name()
        base_element = cmd_utils.get_dir_base_file_element(target_ctrl_impls, element_name)
        file_name = f'{element_name}{file_ext}'
        dir_base_file = targets_ctrl_dir / file_name
        expected_plan.add_action(CreatePathAction(dir_base_file))
        expected_plan.add_action(WriteFileAction(dir_base_file, base_element, content_type))

        for i, target_ctrl_impl in enumerate(target_ctrl_impls):
            model_type = utils.classname_to_alias(type(target_ctrl_impl).__name__, 'json')
            file_prefix = str(i).zfill(4)
            file_name = f'{file_prefix}{const.IDX_SEP}{model_type}{file_ext}'
            file_path = targets_ctrl_dir / file_name
            expected_plan.add_action(CreatePathAction(file_path))
            expected_plan.add_action(WriteFileAction(file_path, Element(target_ctrl_impl), content_type))

        # write stripped target model
        model_type = utils.classname_to_alias(type(target).__name__, 'json')
        target_file = target_dir / f'{model_type}{file_ext}'
        stripped_target = target.stripped_instance(stripped_fields_aliases=[element_paths[1].get_element_name()])
        expected_plan.add_action(CreatePathAction(target_file))
        expected_plan.add_action(WriteFileAction(target_file, Element(stripped_target), content_type))

    root_file = target_def_dir / element_paths[0].to_root_path(content_type)
    remaining_root = element.get().stripped_instance(stripped_fields_aliases=[element_paths[0].get_element_name()])
    expected_plan.add_action(CreatePathAction(root_file))
    expected_plan.add_action(WriteFileAction(root_file, Element(remaining_root), content_type))

    split_plan = SplitCmd.split_model(target_def, element_paths, target_def_dir, content_type)
    assert expected_plan == split_plan


def test_split_run(tmp_dir, sample_target: ostarget.TargetDefinition):
    """Test split run."""
    # common variables
    target_def_dir: pathlib.Path = tmp_dir / 'target-definitions' / 'mytarget'
    target_def_file: pathlib.Path = target_def_dir / 'target-definition.yaml'
    cwd = os.getcwd()
    args = {}
    cmd = SplitCmd()
    parser = cmd.parser

    # inner function for checking split files
    def check_split_files():
        assert target_def_dir.joinpath('metadata.yaml').exists()
        assert target_def_dir.joinpath('target-definition.yaml').exists()
        assert target_def_dir.joinpath('targets').exists()
        assert target_def_dir.joinpath('targets').is_dir()
        assert target_def_dir.joinpath('targets/targets.yaml').exists()

        targets: dict = Element(sample_target).get_at(ElementPath('target-definition.targets.*'))
        for uuid in targets:
            target_file = target_def_dir / f'targets/{uuid}{const.IDX_SEP}target.yaml'
            assert target_file.exists()

        assert cmd_utils.get_trash_file_path(target_def_file).exists()

    # prepare trestle project dir with the file
    def prepare_target_def_file():
        test_utils.ensure_trestle_config_dir(tmp_dir)
        fs.ensure_directory(target_def_dir)
        sample_target.oscal_write(target_def_file)

    # test
    prepare_target_def_file()
    args = parser.parse_args(
        ['-f', 'target-definition.yaml', '-e', 'target-definition.targets.*,target-definition.metadata']
    )
    os.chdir(target_def_dir)
    cmd._run(args)
    os.chdir(cwd)
    check_split_files()

    # clean before the next test
    test_utils.clean_tmp_dir(target_def_dir)

    # reverse order test
    prepare_target_def_file()
    args = parser.parse_args(
        ['-f', 'target-definition.yaml', '-e', 'target-definition.metadata,target-definition.targets.*']
    )
    os.chdir(target_def_dir)
    cmd._run(args)
    os.chdir(cwd)
    check_split_files()


def test_split_run_failure(tmp_dir, sample_target: ostarget.TargetDefinition):
    """Test split run failure."""
    # prepare trestle project dir with the file
    target_def_dir: pathlib.Path = tmp_dir / 'target-definitions' / 'mytarget'
    target_def_file: pathlib.Path = target_def_dir / 'target-definition.yaml'
    fs.ensure_directory(target_def_dir)
    sample_target.oscal_write(target_def_file)
    invalid_file = target_def_dir / 'invalid.file'
    invalid_file.touch()

    cwd = os.getcwd()
    os.chdir(target_def_dir)

    # not a trestle project
    testargs = [
        'trestle',
        'split',
        '-f',
        'target-definition.yaml',
        '-e',
        'target-definition.metadata, target-definition.targets.*'
    ]
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(TrestleError):
            Trestle().run()

    # create trestle project
    test_utils.ensure_trestle_config_dir(tmp_dir)

    # check with missing file
    testargs = [
        'trestle', 'split', '-f', 'missing.yaml', '-e', 'target-definition.metadata, target-definition.targets.*'
    ]
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(TrestleError):
            Trestle().run()

    # check with incorrect file type
    testargs = [
        'trestle', 'split', '-f', invalid_file.name, '-e', 'target-definition.metadata, target-definition.targets.*'
    ]
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(TrestleError):
            Trestle().run()

    os.chdir(cwd)
