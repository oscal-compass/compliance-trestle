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
import argparse
import os
import pathlib
import sys
from typing import Dict
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
from trestle.oscal import catalog as oscatalog
from trestle.oscal import target as ostarget
from trestle.utils import trash


def test_split_model(tmp_path: pathlib.Path, sample_target_def: ostarget.TargetDefinition) -> None:
    """Test for split_model method."""
    # Assume we are running a command like below
    # trestle split -f target-definition.yaml -e target-definition.metadata
    content_type = FileContentType.YAML

    # prepare trestle project dir with the file
    target_def_dir, target_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_target_def,
        test_utils.TARGET_DEFS_DIR)

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
    expected_plan.add_action(CreatePathAction(root_file, True))
    expected_plan.add_action(WriteFileAction(root_file, Element(remaining_root), content_type))

    split_plan = SplitCmd.split_model(target_def, element_paths, target_def_dir, content_type)
    assert expected_plan == split_plan


def test_split_chained_sub_models(tmp_path: pathlib.Path, sample_catalog: oscatalog.Catalog) -> None:
    """Test for split_model method with chained sum models like catalog.metadata.parties.*."""
    # Assume we are running a command like below
    # trestle split -f catalog.json -e catalog.metadata.parties.*
    # see https://github.com/IBM/compliance-trestle/issues/172
    content_type = FileContentType.JSON

    # prepare trestle project dir with the file
    catalog_dir, catalog_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog,
        test_utils.CATALOGS_DIR)

    # read the model from file
    catalog = oscatalog.Catalog.oscal_read(catalog_file)
    element = Element(catalog)
    element_args = ['catalog.metadata.parties.*']
    element_paths = test_utils.prepare_element_paths(catalog_dir, element_args)
    assert 2 == len(element_paths)

    expected_plan = Plan()

    # prepare to extract metadata and parties
    metadata_file = catalog_dir / element_paths[0].to_file_path(content_type)
    metadata_field_alias = element_paths[0].get_element_name()
    metadata = element.get_at(element_paths[0])
    meta_element = Element(metadata, metadata_field_alias)

    # extract parties
    parties_dir = catalog_dir / 'catalog/metadata/parties'
    for i, party in enumerate(meta_element.get_at(element_paths[1], False)):
        prefix = str(i).zfill(const.FILE_DIGIT_PREFIX_LENGTH)
        sub_model_actions = SplitCmd.prepare_sub_model_split_actions(party, parties_dir, prefix, content_type)
        expected_plan.add_actions(sub_model_actions)

    # stripped metadata
    stripped_metadata = metadata.stripped_instance(stripped_fields_aliases=['parties'])
    expected_plan.add_action(CreatePathAction(metadata_file))
    expected_plan.add_action(
        WriteFileAction(metadata_file, Element(stripped_metadata, metadata_field_alias), content_type)
    )

    # stripped catalog
    root_file = catalog_dir / element_paths[0].to_root_path(content_type)
    remaining_root = element.get().stripped_instance(metadata_field_alias)
    expected_plan.add_action(CreatePathAction(root_file, True))
    expected_plan.add_action(WriteFileAction(root_file, Element(remaining_root), content_type))

    split_plan = SplitCmd.split_model(catalog, element_paths, catalog_dir, content_type)
    assert expected_plan == split_plan


def test_subsequent_split_model(tmp_path: pathlib.Path, sample_target_def: ostarget.TargetDefinition) -> None:
    """Test subsequent split of sub models."""
    # Assume we are running a command like below
    # trestle split -f target-definition.yaml -e target-definition.metadata

    content_type = FileContentType.YAML

    # prepare trestle project dir with the file
    target_def_dir, target_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_target_def,
        test_utils.TARGET_DEFS_DIR)

    # first split the target-def into metadata
    target_def = ostarget.TargetDefinition.oscal_read(target_def_file)
    element = Element(target_def, 'target-definition')
    element_args = ['target-definition.metadata']
    element_paths = test_utils.prepare_element_paths(target_def_dir, element_args)
    metadata_file = target_def_dir / element_paths[0].to_file_path(content_type)
    metadata: ostarget.Metadata = element.get_at(element_paths[0])
    root_file = target_def_dir / element_paths[0].to_root_path(content_type)
    metadata_field_alias = element_paths[0].get_element_name()
    stripped_root = element.get().stripped_instance(stripped_fields_aliases=[metadata_field_alias])
    root_wrapper_alias = utils.classname_to_alias(stripped_root.__class__.__name__, 'json')

    first_plan = Plan()
    first_plan.add_action(CreatePathAction(metadata_file))
    first_plan.add_action(WriteFileAction(metadata_file, Element(metadata, metadata_field_alias), content_type))
    first_plan.add_action(CreatePathAction(root_file, True))
    first_plan.add_action(WriteFileAction(root_file, Element(stripped_root, root_wrapper_alias), content_type))
    first_plan.execute()  # this will split the files in the temp directory

    # now, prepare the expected plan to split metadta at parties
    second_plan = Plan()
    metadata_file_dir = target_def_dir / element_paths[0].to_root_path()
    metadata2 = ostarget.Metadata.oscal_read(metadata_file)
    element = Element(metadata2, metadata_field_alias)

    element_args = ['metadata.parties.*']
    element_paths = test_utils.prepare_element_paths(target_def_dir, element_args)
    parties_dir = metadata_file_dir / element_paths[0].to_file_path()
    for i, party in enumerate(element.get_at(element_paths[0])):
        prefix = str(i).zfill(const.FILE_DIGIT_PREFIX_LENGTH)
        sub_model_actions = SplitCmd.prepare_sub_model_split_actions(party, parties_dir, prefix, content_type)
        second_plan.add_actions(sub_model_actions)

    # stripped metadata
    stripped_metadata = metadata2.stripped_instance(stripped_fields_aliases=['parties'])
    second_plan.add_action(CreatePathAction(metadata_file, True))
    second_plan.add_action(
        WriteFileAction(metadata_file, Element(stripped_metadata, metadata_field_alias), content_type)
    )

    # call the split command and compare the plans
    split_plan = SplitCmd.split_model(metadata, element_paths, metadata_file_dir, content_type)
    assert second_plan == split_plan


def test_split_multi_level_dict(tmp_path: pathlib.Path, sample_target_def: ostarget.TargetDefinition) -> None:
    """Test for split_model method."""
    # Assume we are running a command like below
    # trestle split -f target.yaml -e target-definition.targets.*.target-control-implementations.*

    content_type = FileContentType.YAML

    # prepare trestle project dir with the file
    target_def_dir, target_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_target_def,
        test_utils.TARGET_DEFS_DIR)

    file_ext = FileContentType.to_file_extension(content_type)

    # read the model from file
    target_def: ostarget.TargetDefinition = ostarget.TargetDefinition.oscal_read(target_def_file)
    element = Element(target_def)
    element_args = ['target-definition.targets.*.target-control-implementations.*']
    element_paths = test_utils.prepare_element_paths(target_def_dir, element_args)

    expected_plan = Plan()

    # extract values
    targets: dict = element.get_at(element_paths[0])
    targets_dir = target_def_dir / element_paths[0].to_file_path()

    # split every targets
    for key in targets:
        # individual target dir
        target: ostarget.Target = targets[key]
        target_element = Element(targets[key])
        model_type = utils.classname_to_alias(type(target).__name__, 'json')
        dir_prefix = key
        target_dir_name = f'{dir_prefix}{const.IDX_SEP}{model_type}'
        target_file = targets_dir / f'{target_dir_name}{file_ext}'

        # target control impl dir for the target
        target_ctrl_impls: dict = target_element.get_at(element_paths[1])
        targets_ctrl_dir = targets_dir / element_paths[1].to_file_path(root_dir=target_dir_name)

        for i, target_ctrl_impl in enumerate(target_ctrl_impls):
            model_type = utils.classname_to_alias(type(target_ctrl_impl).__name__, 'json')
            file_prefix = str(i).zfill(const.FILE_DIGIT_PREFIX_LENGTH)
            file_name = f'{file_prefix}{const.IDX_SEP}{model_type}{file_ext}'
            file_path = targets_ctrl_dir / file_name
            expected_plan.add_action(CreatePathAction(file_path))
            expected_plan.add_action(WriteFileAction(file_path, Element(target_ctrl_impl), content_type))

        # write stripped target model
        stripped_target = target.stripped_instance(stripped_fields_aliases=[element_paths[1].get_element_name()])
        expected_plan.add_action(CreatePathAction(target_file))
        expected_plan.add_action(WriteFileAction(target_file, Element(stripped_target), content_type))

    root_file = target_def_dir / f'target-definition{file_ext}'
    remaining_root = element.get().stripped_instance(stripped_fields_aliases=[element_paths[0].get_element_name()])
    expected_plan.add_action(CreatePathAction(root_file, True))
    expected_plan.add_action(WriteFileAction(root_file, Element(remaining_root), content_type))

    split_plan = SplitCmd.split_model(target_def, element_paths, target_def_dir, content_type)
    assert expected_plan == split_plan


def test_split_run(tmp_path: pathlib.Path, sample_target_def: ostarget.TargetDefinition) -> None:
    """Test split run."""
    # common variables
    target_def_dir: pathlib.Path = tmp_path / 'target-definitions' / 'mytarget'
    target_def_file: pathlib.Path = target_def_dir / 'target-definition.yaml'
    cwd = os.getcwd()
    args = {}
    cmd = SplitCmd()

    # inner function for checking split files
    def check_split_files():
        assert target_def_dir.joinpath('target-definition/metadata.yaml').exists()
        assert target_def_dir.joinpath('target-definition.yaml').exists()
        assert target_def_dir.joinpath('target-definition/targets').exists()
        assert target_def_dir.joinpath('target-definition/targets').is_dir()

        targets: Dict = Element(sample_target_def).get_at(ElementPath('target-definition.targets.*'))
        for uuid in targets:
            target_file = target_def_dir / f'target-definition/targets/{uuid}{const.IDX_SEP}defined-target.yaml'
            assert target_file.exists()

        assert trash.to_trash_file_path(target_def_file).exists()

    # prepare trestle project dir with the file
    def prepare_target_def_file() -> None:
        test_utils.ensure_trestle_config_dir(tmp_path)
        target_def_dir.mkdir(exist_ok=True, parents=True)
        sample_target_def.oscal_write(target_def_file)

    # test
    prepare_target_def_file()
    args = argparse.Namespace(
        file='target-definition.yaml', element='target-definition.targets.*,target-definition.metadata', verbose=0
    )

    os.chdir(target_def_dir)
    assert cmd._run(args) == 0
    os.chdir(cwd)
    check_split_files()

    # clean before the next test
    test_utils.clean_tmp_path(target_def_dir)

    # reverse order test
    prepare_target_def_file()
    args = argparse.Namespace(
        file='target-definition.yaml', element='target-definition.metadata,target-definition.targets.*', verbose=0
    )
    os.chdir(target_def_dir)
    assert cmd._run(args) == 0
    os.chdir(cwd)
    check_split_files()


def test_split_run_failure(tmp_path: pathlib.Path, sample_target_def: ostarget.TargetDefinition) -> None:
    """Test split run failure."""
    # prepare trestle project dir with the file
    target_def_dir: pathlib.Path = tmp_path / 'target-definitions' / 'mytarget'
    target_def_file: pathlib.Path = target_def_dir / 'target-definition.yaml'
    target_def_dir.mkdir(exist_ok=True, parents=True)
    sample_target_def.oscal_write(target_def_file)
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
    test_utils.ensure_trestle_config_dir(tmp_path)

    # no file specified
    testargs = ['trestle', 'split', '-e', 'target-definition.metadata, target-definition.targets.*']
    with patch.object(sys, 'argv', testargs):
        rc = Trestle().run()
        assert rc > 0
    # check with missing file
    testargs = [
        'trestle', 'split', '-f', 'missing.yaml', '-e', 'target-definition.metadata, target-definition.targets.*'
    ]
    with patch.object(sys, 'argv', testargs):
        rc = Trestle().run()
        assert rc > 0

    # check with incorrect file type
    testargs = [
        'trestle', 'split', '-f', invalid_file.name, '-e', 'target-definition.metadata, target-definition.targets.*'
    ]
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(TrestleError):
            Trestle().run()

    os.chdir(cwd)


def test_split_model_at_path_chain_failures(tmp_path, sample_catalog: oscatalog.Catalog):
    """Test for split_model_at_path_chain method failure scenarios."""
    content_type = FileContentType.JSON

    # prepare trestle project dir with the file
    catalog_dir, catalog_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog,
        test_utils.CATALOGS_DIR)

    split_plan = Plan()
    element_paths = [ElementPath('catalog.metadata.parties.*')]

    # long chain of path should error
    with pytest.raises(TrestleError):
        SplitCmd.split_model_at_path_chain(
            sample_catalog, element_paths, catalog_dir, content_type, 0, split_plan, False
        )

    # no plan should error
    with pytest.raises(TrestleError):
        SplitCmd.split_model_at_path_chain(sample_catalog, element_paths, catalog_dir, content_type, 0, None, False)

    # negative path index should error
    with pytest.raises(TrestleError):
        SplitCmd.split_model_at_path_chain(
            sample_catalog, element_paths, catalog_dir, content_type, -1, split_plan, False
        )

    # too large path index should return the path index
    cur_path_index = len(element_paths) + 1
    SplitCmd.split_model_at_path_chain(
        sample_catalog, element_paths, catalog_dir, content_type, cur_path_index, split_plan, False
    )

    # invalid model path should return withour doing anything
    element_paths = [ElementPath('catalog.meta')]
    cur_path_index = 0
    SplitCmd.split_model_at_path_chain(
        sample_catalog, element_paths, catalog_dir, content_type, cur_path_index, split_plan, False
    )

    # invalid path for multi item sub-model
    p0 = ElementPath('catalog.uuid.*')  # uuid exists, but it is not a multi-item sub-model object
    p1 = ElementPath('uuid.metadata.*', p0)  # this is invalid but we just need a path with the p0 as the parent
    element_paths = [p0, p1]
    with pytest.raises(TrestleError):
        SplitCmd.split_model_at_path_chain(
            sample_catalog, element_paths, catalog_dir, content_type, 0, split_plan, False
        )
