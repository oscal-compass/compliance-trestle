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
from unittest.mock import patch

import pytest

from tests import test_utils

import trestle.cli
from trestle.cli import Trestle
from trestle.core import const
from trestle.core import utils
from trestle.core.commands import cmd_utils
from trestle.core.commands.merge import MergeCmd
from trestle.core.commands.split import SplitCmd
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.oscal import catalog as oscatalog
from trestle.oscal import common, component
from trestle.utils import trash


def test_split_model(tmp_path: pathlib.Path, sample_nist_component_def: component.ComponentDefinition) -> None:
    """Test for split_model method."""
    # Assume we are running a command like below
    # trestle split -f component-definition.yaml -e component-definition.metadata
    content_type = FileContentType.YAML

    # prepare trestle project dir with the file
    component_def_dir, component_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_nist_component_def,
        test_utils.COMPONENT_DEF_DIR)

    # read the model from file
    component_def = component.ComponentDefinition.oscal_read(component_def_file)
    element = Element(component_def)
    element_args = ['component-definition.metadata']
    element_paths = cmd_utils.parse_element_args(None, element_args)

    # extract values
    metadata_file = component_def_dir / element_paths[0].to_file_path(content_type)
    metadata = element.get_at(element_paths[0])

    root_file = component_def_dir / element_paths[0].to_root_path(content_type)
    remaining_root = element.get().stripped_instance(element_paths[0].get_element_name())

    # prepare the plan
    expected_plan = Plan()
    expected_plan.add_action(CreatePathAction(metadata_file))
    expected_plan.add_action(WriteFileAction(metadata_file, Element(metadata), content_type))
    expected_plan.add_action(CreatePathAction(root_file, True))
    expected_plan.add_action(WriteFileAction(root_file, Element(remaining_root), content_type))

    split_plan = SplitCmd.split_model(component_def, element_paths, component_def_dir, content_type)
    assert expected_plan == split_plan


def test_split_chained_sub_models(
    tmp_path: pathlib.Path, sample_catalog: oscatalog.Catalog, keep_cwd: pathlib.Path
) -> None:
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


def test_subsequent_split_model(
    tmp_path: pathlib.Path, sample_nist_component_def: component.ComponentDefinition, keep_cwd: pathlib.Path
) -> None:
    """Test subsequent split of sub models."""
    # Assume we are running a command like below
    # trestle split -f component-definition.yaml -e component-definition.metadata

    content_type = FileContentType.YAML

    # prepare trestle project dir with the file
    component_def_dir, component_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_nist_component_def,
        test_utils.COMPONENT_DEF_DIR)

    # first split the component-def into metadata
    component_def = component.ComponentDefinition.oscal_read(component_def_file)
    element = Element(component_def, 'component-definition')
    element_args = ['component-definition.metadata']
    element_paths = test_utils.prepare_element_paths(component_def_dir, element_args)
    metadata_file = component_def_dir / element_paths[0].to_file_path(content_type)
    metadata: common.Metadata = element.get_at(element_paths[0])
    root_file = component_def_dir / element_paths[0].to_root_path(content_type)
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
    metadata_file_dir = component_def_dir / element_paths[0].to_root_path()
    metadata2 = common.Metadata.oscal_read(metadata_file)
    element = Element(metadata2, metadata_field_alias)

    element_args = ['metadata.parties.*']
    element_paths = test_utils.prepare_element_paths(component_def_dir, element_args)
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


def test_split_multi_level_dict(
    tmp_path: pathlib.Path, sample_nist_component_def: component.ComponentDefinition, keep_cwd
) -> None:
    """Test for split_model method."""
    # Assume we are running a command like below
    # trestle split -f target.yaml -e component-definition.components.*.control-implementations.*

    content_type = FileContentType.YAML

    # prepare trestle project dir with the file
    component_def_dir, component_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_nist_component_def,
        test_utils.COMPONENT_DEF_DIR)

    file_ext = FileContentType.to_file_extension(content_type)

    # read the model from file
    component_def: component.ComponentDefinition = component.ComponentDefinition.oscal_read(component_def_file)
    element = Element(component_def)
    element_args = ['component-definition.components.*.control-implementations.*']
    element_paths = test_utils.prepare_element_paths(component_def_dir, element_args)

    expected_plan = Plan()

    # extract values
    components: list = element.get_at(element_paths[0])
    components_dir = component_def_dir / element_paths[0].to_file_path()

    # split every targets
    for index, comp_obj in enumerate(components):

        # individual target dir

        component_element = Element(comp_obj)
        model_type = utils.classname_to_alias(type(comp_obj).__name__, 'json')
        dir_prefix = str(index).zfill(const.FILE_DIGIT_PREFIX_LENGTH)
        component_dir_name = f'{dir_prefix}{const.IDX_SEP}{model_type}'
        component_file = components_dir / f'{component_dir_name}{file_ext}'

        # target control impl dir for the target
        component_ctrl_impls: list = component_element.get_at(element_paths[1])
        component_ctrl_dir = components_dir / element_paths[1].to_file_path(root_dir=component_dir_name)

        for i, component_ctrl_impl in enumerate(component_ctrl_impls):
            model_type = utils.classname_to_alias(type(component_ctrl_impl).__name__, 'json')
            file_prefix = str(i).zfill(const.FILE_DIGIT_PREFIX_LENGTH)
            file_name = f'{file_prefix}{const.IDX_SEP}{model_type}{file_ext}'
            file_path = component_ctrl_dir / file_name
            expected_plan.add_action(CreatePathAction(file_path))
            expected_plan.add_action(WriteFileAction(file_path, Element(component_ctrl_impl), content_type))

        # write stripped target model
        stripped_target = comp_obj.stripped_instance(stripped_fields_aliases=[element_paths[1].get_element_name()])
        expected_plan.add_action(CreatePathAction(component_file))
        expected_plan.add_action(WriteFileAction(component_file, Element(stripped_target), content_type))

    root_file = component_def_dir / f'component-definition{file_ext}'
    remaining_root = element.get().stripped_instance(stripped_fields_aliases=[element_paths[0].get_element_name()])
    expected_plan.add_action(CreatePathAction(root_file, True))
    expected_plan.add_action(WriteFileAction(root_file, Element(remaining_root), content_type))

    split_plan = SplitCmd.split_model(component_def, element_paths, component_def_dir, content_type)
    assert expected_plan == split_plan


def test_split_run(
    keep_cwd: pathlib.Path, tmp_path: pathlib.Path, sample_nist_component_def: component.ComponentDefinition
) -> None:
    """Test split run."""
    # common variables
    owd = keep_cwd
    component_def_dir: pathlib.Path = tmp_path / 'component-definitions' / 'mytarget'
    component_def_file: pathlib.Path = component_def_dir / 'component-definition.yaml'
    args = {}
    cmd = SplitCmd()

    # inner function for checking split files
    def check_split_files():
        assert component_def_dir.joinpath('component-definition/metadata.yaml').exists()
        assert component_def_dir.joinpath('component-definition.yaml').exists()
        assert component_def_dir.joinpath('component-definition/components').exists()
        assert component_def_dir.joinpath('component-definition/components').is_dir()
        # FIXME: This is not doign anything.
        components: list = Element(sample_nist_component_def).get_at(ElementPath('component-definition.components.*'))
        for index in range(len(components)):
            comp_fname = f'{str(index).zfill(const.FILE_DIGIT_PREFIX_LENGTH)}{const.IDX_SEP}defined-component.yaml'
            component_file = component_def_dir / 'component-definition' / 'components' / comp_fname
            assert component_file.exists()

        assert trash.to_trash_file_path(component_def_file).exists()

    # prepare trestle project dir with the file
    def prepare_component_def_file() -> None:
        test_utils.ensure_trestle_config_dir(tmp_path)
        component_def_dir.mkdir(exist_ok=True, parents=True)
        sample_nist_component_def.oscal_write(component_def_file)

    # test
    prepare_component_def_file()
    args = argparse.Namespace(
        file='component-definition.yaml',
        element='component-definition.components.*,component-definition.metadata',
        verbose=0
    )

    os.chdir(component_def_dir)
    assert cmd._run(args) == 0
    os.chdir(owd)
    check_split_files()

    # clean before the next test
    test_utils.clean_tmp_path(component_def_dir)

    # reverse order test
    prepare_component_def_file()
    args = argparse.Namespace(
        file='component-definition.yaml',
        element='component-definition.metadata,component-definition.components.*',
        verbose=0
    )
    os.chdir(component_def_dir)
    assert cmd._run(args) == 0
    os.chdir(owd)
    check_split_files()


def test_split_run_failure(
    keep_cwd: pathlib.Path, tmp_path: pathlib.Path, sample_nist_component_def: component.ComponentDefinition
) -> None:
    """Test split run failure."""
    # prepare trestle project dir with the file
    component_def_dir: pathlib.Path = tmp_path / 'component-definitions' / 'mytarget'
    component_def_file: pathlib.Path = component_def_dir / 'component-definition.yaml'
    component_def_dir.mkdir(exist_ok=True, parents=True)
    sample_nist_component_def.oscal_write(component_def_file)
    invalid_file = component_def_dir / 'invalid.file'
    invalid_file.touch()

    os.chdir(component_def_dir)

    # not a trestle project
    testargs = [
        'trestle',
        'split',
        '-tr',
        str(tmp_path),
        '-f',
        'component-definition.yaml',
        '-e',
        'component-definition.metadata, component-definition.components.*'
    ]
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit) as wrapped_error:
            trestle.cli.run()
        assert wrapped_error.value.code == 1

    # create trestle project
    test_utils.ensure_trestle_config_dir(tmp_path)

    # no file specified
    testargs = ['trestle', 'split', '-e', 'component-definition.metadata, component-definition.components.*']
    with patch.object(sys, 'argv', testargs):
        rc = Trestle().run()
        assert rc > 0
    # check with missing file
    testargs = [
        'trestle',
        'split',
        '-f',
        'missing.yaml',
        '-e',
        'component-definition.metadata, component-definition.components.*'
    ]
    with patch.object(sys, 'argv', testargs):
        rc = Trestle().run()
        assert rc > 0

    # check with incorrect file type
    testargs = [
        'trestle',
        'split',
        '-f',
        invalid_file.name,
        '-e',
        'component-definition.metadata, component-definition.components.*'
    ]
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(TrestleError):
            Trestle().run()


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

    # invalid model path should error
    element_paths = [ElementPath('catalog.meta')]
    cur_path_index = 0
    with pytest.raises(TrestleError):
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


@pytest.mark.parametrize('direct', [True, False])
def test_split_comp_def(
    direct, tmp_trestle_dir, keep_cwd: pathlib.Path, sample_component_definition: component.ComponentDefinition
) -> None:
    """Test splitting of component definition and its dictionary."""
    my_comp_dir = tmp_trestle_dir / 'component-definitions/my_comp'
    my_comp_dir.mkdir()
    my_comp_path = my_comp_dir / 'component-definition.json'
    sample_component_definition.oscal_write(my_comp_path)
    os.chdir(my_comp_dir)
    # do the split either directly or in two steps - then re-merge
    if direct:
        args = argparse.Namespace(file='component-definition.json', element='component.components.*', verbose=1)
        assert SplitCmd()._run(args) == 0
    else:
        args = argparse.Namespace(file='component-definition.json', element='component.components', verbose=1)
        assert SplitCmd()._run(args) == 0
        os.chdir('component-definition')
        args = argparse.Namespace(file='components.json', element='components.*', verbose=1)
        assert SplitCmd()._run(args) == 0
    os.chdir(my_comp_dir)
    args = argparse.Namespace(element='component-definition.*', verbose=1)
    assert MergeCmd()._run(args) == 0


def test_split_stop_at_string(tmp_path, keep_cwd: pathlib.Path, sample_catalog: oscatalog.Catalog):
    """Test prevention of split at string level."""
    # prepare trestle project dir with the file
    catalog_dir, catalog_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        FileContentType.JSON,
        sample_catalog,
        test_utils.CATALOGS_DIR)

    os.chdir(catalog_dir)
    args = argparse.Namespace(file='catalog.json', element='catalog.groups.*.controls.*.controls.*.id', verbose=1)
    assert SplitCmd()._run(args) == 1
    args = argparse.Namespace(file='catalog.json', element='catalog.metadata.version', verbose=1)
    assert SplitCmd()._run(args) == 1
    args = argparse.Namespace(file='catalog.json', element='catalog.groups.*.controls.*.controls.*', verbose=1)
    assert SplitCmd()._run(args) == 0


def test_split_workflow(tmp_path, keep_cwd: pathlib.Path, sample_catalog: oscatalog.Catalog):
    """Test split operations and final re-merge in workflow tutorial."""
    # prepare trestle project dir with the file
    catalog_dir, catalog_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        FileContentType.JSON,
        sample_catalog,
        test_utils.CATALOGS_DIR)

    # step0
    os.chdir(catalog_dir)
    args = argparse.Namespace(
        file='catalog.json', element='catalog.metadata,catalog.groups,catalog.back-matter', verbose=1
    )
    assert SplitCmd()._run(args) == 0

    # step1
    os.chdir('catalog')
    args = argparse.Namespace(
        file='metadata.json', element='metadata.roles,metadata.parties,metadata.responsible-parties', verbose=1
    )
    assert SplitCmd()._run(args) == 0

    # step2
    os.chdir('metadata')
    args = argparse.Namespace(file='roles.json', element='roles.*', verbose=1)
    assert SplitCmd()._run(args) == 0
    args = argparse.Namespace(file='responsible-parties.json', element='responsible-parties.*', verbose=1)
    assert SplitCmd()._run(args) == 0

    # step3
    os.chdir('..')
    args = argparse.Namespace(file='./groups.json', element='groups.*.controls.*', verbose=1)
    assert SplitCmd()._run(args) == 0

    # step4
    os.chdir(catalog_dir)
    args = argparse.Namespace(element='catalog.*', verbose=1)
    assert MergeCmd()._run(args) == 0


@pytest.mark.parametrize('split_path', ['catalog.metadata.roles', 'catalog.*', 'catalog.metadata.*'])
def test_split_catalog_star(
    split_path: str, tmp_path: pathlib.Path, keep_cwd: pathlib.Path, sample_catalog: oscatalog.Catalog
):
    """Test extended depth split operations and split of dicts."""
    # prepare trestle project dir with the file
    catalog_dir, catalog_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        FileContentType.JSON,
        sample_catalog,
        test_utils.CATALOGS_DIR)

    os.chdir(catalog_dir)
    args = argparse.Namespace(file='catalog.json', element=split_path, verbose=1)
    assert SplitCmd()._run(args) == 0
