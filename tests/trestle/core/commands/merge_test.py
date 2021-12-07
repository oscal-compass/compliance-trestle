# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
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
import shutil
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

import pytest

from tests import test_utils
from tests.test_utils import execute_command_and_assert

import trestle.oscal.common as common
from trestle.core.commands.merge import MergeCmd
from trestle.core.commands.split import SplitCmd
from trestle.core.models.actions import CreatePathAction, RemovePathAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs
from trestle.utils.load_distributed import load_distributed


def test_merge_invalid_element_path(testdata_dir, tmp_trestle_dir):
    """Test to make sure each element in -e contains 2 parts at least, and no chained element paths."""
    cmd = MergeCmd()
    args = argparse.Namespace(verbose=1, element='catalog', trestle_root=tmp_trestle_dir)
    assert cmd._run(args) == 1

    args = argparse.Namespace(verbose=1, element='catalog.metadata', trestle_root=tmp_trestle_dir)
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)
    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'
    catalogs_dir = Path('catalogs/')
    mycatalog_dir = catalogs_dir / 'mycatalog'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    os.chdir(mycatalog_dir)
    assert cmd._run(args) == 0


def test_merge_plan_simple_case(testdata_dir, tmp_trestle_dir):
    """Test '$mycatalog$ trestle merge -e catalog.back-matter'."""
    # Assume we are running a command like below
    # trestle merge -e catalog.back-matter
    content_type = FileContentType.JSON
    fext = FileContentType.to_file_extension(content_type)

    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)

    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'

    catalogs_dir = Path('catalogs/')
    mycatalog_dir = catalogs_dir / 'mycatalog'
    catalog_dir = mycatalog_dir / 'catalog'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    os.chdir(mycatalog_dir)
    catalog_file = Path(f'catalog{fext}').resolve()
    catalog_dir = Path('catalog/')
    back_matter_file = (catalog_dir / f'back-matter{fext}').resolve()

    assert catalog_file.exists()
    assert back_matter_file.exists()

    # Read files

    # The destination file/model needs to be loaded in a stripped model
    stripped_catalog_type, _ = fs.get_stripped_model_type(catalog_file.resolve(), tmp_trestle_dir)
    stripped_catalog = stripped_catalog_type.oscal_read(catalog_file)

    # Back-matter model needs to be complete and if it is decomposed, needs to be merged recursively first
    back_matter = common.BackMatter.oscal_read(back_matter_file)

    # Back-matter needs to be inserted in a stripped Catalog that does NOT exclude the back-matter fields

    merged_catalog_type, merged_catalog_alias = fs.get_stripped_model_type(
        catalog_file.resolve(), tmp_trestle_dir, aliases_not_to_be_stripped=['back-matter'])
    merged_dict = stripped_catalog.__dict__
    merged_dict['back-matter'] = back_matter
    merged_catalog = merged_catalog_type(**merged_dict)

    element = Element(merged_catalog, merged_catalog_alias)

    # Create hand-crafter merge plan
    reset_destination_action = CreatePathAction(catalog_file, clear_content=True)
    write_destination_action = WriteFileAction(catalog_file, element, content_type=content_type)
    delete_element_action = RemovePathAction(back_matter_file)

    expected_plan: Plan = Plan()
    expected_plan.add_action(reset_destination_action)
    expected_plan.add_action(write_destination_action)
    expected_plan.add_action(delete_element_action)

    # Call merge()

    generated_plan = MergeCmd.merge(Path.cwd(), ElementPath('catalog.back-matter'), tmp_trestle_dir)

    # Assert the generated plan matches the expected plan'
    assert generated_plan == expected_plan


def test_merge_expanded_metadata_into_catalog(testdata_dir, tmp_trestle_dir):
    """Test '$mycatalog$ trestle merge -e catalog.metadata' when metadata is already split."""
    # Assume we are running a command like below
    # trestle merge -e catalog.back-matter
    content_type = FileContentType.JSON
    fext = FileContentType.to_file_extension(content_type)

    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)

    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'
    catalogs_dir = Path('catalogs/')
    mycatalog_dir = catalogs_dir / 'mycatalog'
    catalog_dir = mycatalog_dir / 'catalog'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    # Change directory to mycatalog_dir
    os.chdir(mycatalog_dir)
    catalog_file = Path(f'catalog{fext}').resolve()
    catalog_dir = Path('catalog/')
    metadata_dir = catalog_dir / 'metadata'
    metadata_file = (catalog_dir / f'metadata{fext}').resolve()

    assert catalog_file.exists()
    assert metadata_dir.exists()
    assert metadata_file.exists()

    # Read files

    # Create hand-crafter merge plan
    expected_plan: Plan = Plan()

    reset_destination_action = CreatePathAction(catalog_file, clear_content=True)
    expected_plan.add_action(reset_destination_action)

    _, _, merged_metadata_instance = load_distributed(metadata_file, tmp_trestle_dir)
    merged_catalog_type, _ = fs.get_stripped_model_type(
        catalog_file.resolve(), tmp_trestle_dir, aliases_not_to_be_stripped=['metadata'])
    stripped_catalog_type, _ = fs.get_stripped_model_type(catalog_file, tmp_trestle_dir)
    stripped_catalog = stripped_catalog_type.oscal_read(catalog_file)
    merged_catalog_dict = stripped_catalog.__dict__
    merged_catalog_dict['metadata'] = merged_metadata_instance
    merged_catalog = merged_catalog_type(**merged_catalog_dict)
    element = Element(merged_catalog)
    write_destination_action = WriteFileAction(catalog_file, element, content_type=content_type)
    expected_plan.add_action(write_destination_action)
    delete_element_action = RemovePathAction(metadata_file)
    expected_plan.add_action(delete_element_action)

    # Call merge()
    generated_plan = MergeCmd.merge(Path.cwd(), ElementPath('catalog.metadata'), tmp_trestle_dir)

    # Assert the generated plan matches the expected plan'
    assert generated_plan == expected_plan


def test_merge_everything_into_catalog(testdata_dir, tmp_trestle_dir):
    """Test '$mycatalog$ trestle merge -e catalog.*' when metadata and catalog is already split."""
    # Assume we are running a command like below
    # trestle merge -e catalog.*
    content_type = FileContentType.JSON
    fext = FileContentType.to_file_extension(content_type)

    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)

    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'
    catalogs_dir = Path('catalogs/')
    mycatalog_dir = catalogs_dir / 'mycatalog'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    # Change directory to mycatalog_dir
    os.chdir(mycatalog_dir)
    catalog_file = Path(f'catalog{fext}').resolve()

    assert catalog_file.exists()

    # Read files

    # Create hand-crafter merge plan
    expected_plan: Plan = Plan()

    reset_destination_action = CreatePathAction(catalog_file, clear_content=True)
    expected_plan.add_action(reset_destination_action)

    _, _, merged_catalog_instance = load_distributed(catalog_file, tmp_trestle_dir)

    element = Element(merged_catalog_instance)
    write_destination_action = WriteFileAction(catalog_file, element, content_type=content_type)
    expected_plan.add_action(write_destination_action)
    delete_element_action = RemovePathAction(Path('catalog').resolve())
    expected_plan.add_action(delete_element_action)

    # Call merge()
    generated_plan = MergeCmd.merge(Path.cwd(), ElementPath('catalog.*'), tmp_trestle_dir)

    # Assert the generated plan matches the expected plan'
    assert generated_plan == expected_plan


def test_merge_everything_into_catalog_with_hidden_files_in_folders(testdata_dir, tmp_trestle_dir):
    """Test trestle merge -e 'catalog.*' when metadata and catalog are split and hidden files are present."""
    # Assume we are running a command like below
    # trestle merge -e catalog.*
    content_type = FileContentType.JSON
    fext = FileContentType.to_file_extension(content_type)

    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)

    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'
    catalogs_dir = Path('catalogs/')
    mycatalog_dir = catalogs_dir / 'mycatalog'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    # Change directory to mycatalog_dir
    os.chdir(mycatalog_dir)
    catalog_file = Path(f'catalog{fext}').resolve()

    assert catalog_file.exists()

    # Read files

    # Create hand-crafter merge plan
    expected_plan: Plan = Plan()

    reset_destination_action = CreatePathAction(catalog_file, clear_content=True)
    expected_plan.add_action(reset_destination_action)

    _, _, merged_catalog_instance = load_distributed(catalog_file, tmp_trestle_dir)

    element = Element(merged_catalog_instance)
    write_destination_action = WriteFileAction(catalog_file, element, content_type=content_type)
    expected_plan.add_action(write_destination_action)
    delete_element_action = RemovePathAction(Path('catalog').resolve())
    expected_plan.add_action(delete_element_action)

    test_utils.make_hidden_file(tmp_trestle_dir / 'catalogs/mycatalog/.DS_Store')
    test_utils.make_hidden_file(tmp_trestle_dir / 'catalogs/mycatalog/catalog/.DS_Store')
    test_utils.make_hidden_file(tmp_trestle_dir / 'catalogs/mycatalog/catalog/metadata/.DS_Store')
    test_utils.make_hidden_file(tmp_trestle_dir / 'catalogs/mycatalog/catalog/groups/.DS_Store')

    # Call merge()
    generated_plan = MergeCmd.merge(Path.cwd(), ElementPath('catalog.*'), tmp_trestle_dir)

    # Assert the generated plan matches the expected plan'
    assert generated_plan == expected_plan


def test_bad_merge(testdata_dir, tmp_trestle_dir):
    """Test a bad merge element path."""
    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)

    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'

    catalogs_dir = Path('catalogs/')
    mycatalog_dir = catalogs_dir / 'mycatalog'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    os.chdir(mycatalog_dir)
    cmd = MergeCmd()
    args = argparse.Namespace(verbose=1, element='catalog.roles', trestle_root=tmp_trestle_dir)
    assert cmd._run(args) == 1

    # test from outside trestle project
    os.chdir(testdata_dir)
    assert cmd._run(args) == 1


def test_merge_plan_simple_list(testdata_dir, tmp_trestle_dir):
    """Test '$mycatalog$ trestle merge -e metadata.roles'."""
    # Assume we are running a command like below
    # trestle merge -e catalog.back-matter
    content_type = FileContentType.JSON
    fext = FileContentType.to_file_extension(content_type)

    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)

    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'

    catalogs_dir = Path('catalogs/')
    mycatalog_dir = catalogs_dir / 'mycatalog'
    catalog_dir = mycatalog_dir / 'catalog'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    os.chdir(mycatalog_dir)
    catalog_dir = Path('catalog/')
    os.chdir(catalog_dir)
    metadata_dir = Path('metadata/')
    metadata_file = Path(f'metadata{fext}').resolve()
    roles_dir = (metadata_dir / 'roles').resolve()

    # Read files

    # The destination file/model needs to be loaded in a stripped model
    stripped_metadata_type, _ = fs.get_stripped_model_type(metadata_file, tmp_trestle_dir)
    stripped_metadata = stripped_metadata_type.oscal_read(metadata_file)

    # Back-matter model needs to be complete and if it is decomposed, needs to be merged recursively first
    roles = [
        common.Role.oscal_read(roles_dir / '00000__role.json'), common.Role.oscal_read(roles_dir / '00001__role.json')
    ]

    # Back-matter needs to be inserted in a stripped Catalog that does NOT exclude the back-matter fields

    merged_metadata_type, merged_metadata_alias = fs.get_stripped_model_type(
        metadata_file, tmp_trestle_dir, aliases_not_to_be_stripped=['roles'])
    merged_dict = stripped_metadata.__dict__
    merged_dict['roles'] = roles
    merged_metadata = merged_metadata_type(**merged_dict)

    element = Element(merged_metadata, merged_metadata_alias)

    # Create hand-crafter merge plan
    reset_destination_action = CreatePathAction(metadata_file, clear_content=True)
    write_destination_action = WriteFileAction(metadata_file, element, content_type=content_type)
    delete_element_action = RemovePathAction(roles_dir)

    expected_plan: Plan = Plan()
    expected_plan.add_action(reset_destination_action)
    expected_plan.add_action(write_destination_action)
    expected_plan.add_action(delete_element_action)

    # Call merge()

    generated_plan = MergeCmd.merge(Path.cwd(), ElementPath('metadata.roles'), tmp_trestle_dir)

    # Assert the generated plan matches the expected plan'
    assert generated_plan == expected_plan


def test_split_merge(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path) -> None:
    """Test merging data that has been split using the split command- to ensure symmetry."""
    # trestle split -f catalog.json -e catalog.groups.*.controls.*

    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)

    test_data_source = testdata_dir / 'split_merge/step0-merged_catalog/catalogs'

    catalogs_dir = Path('catalogs/')
    mycatalog_dir = catalogs_dir / 'mycatalog'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    os.chdir(mycatalog_dir)
    catalog_file = Path('catalog.json')

    # Read and store the catalog before split
    stripped_catalog_type, _ = fs.get_stripped_model_type(catalog_file.resolve(), tmp_trestle_dir)
    pre_split_catalog = stripped_catalog_type.oscal_read(catalog_file)
    assert 'groups' in pre_split_catalog.__fields__.keys()

    # Split the catalog
    args = argparse.Namespace(
        name='split',
        file='catalog.json',
        verbose=1,
        element='catalog.groups.*.controls.*',
        trestle_root=tmp_trestle_dir
    )
    split = SplitCmd()._run(args)

    assert split == 0

    interim_catalog_type, _ = fs.get_stripped_model_type(catalog_file.resolve(), tmp_trestle_dir)
    interim_catalog = interim_catalog_type.oscal_read(catalog_file.resolve())
    assert 'groups' not in interim_catalog.__fields__.keys()

    # Merge everything back into the catalog
    # Equivalent to trestle merge -e catalog.*
    args = argparse.Namespace(name='merge', element='catalog.*', verbose=1, trestle_root=tmp_trestle_dir)
    rc = MergeCmd()._run(args)
    assert rc == 0

    # Check both the catalogs are the same.
    post_catalog_type, _ = fs.get_stripped_model_type(catalog_file.resolve(), tmp_trestle_dir)
    post_merge_catalog = post_catalog_type.oscal_read(catalog_file)
    assert post_merge_catalog == pre_split_catalog


# Note this is EXPENSIVE
@pytest.mark.parametrize(
    'rel_context_dir, use_absolutes, split_elem, merge_elem, use_effective_cwd',
    [
        ('catalogs/mycatalog', False, 'catalog.groups.*.controls.*', 'catalog.*', False),
        ('catalogs/mycatalog', True, 'catalog.groups.*.controls.*', 'catalog.*', False),
        ('', False, 'catalog.groups.*.controls.*', 'catalog.*', True),
        ('catalogs', False, 'catalog.groups.*.controls.*', 'catalog.*', True),
        ('catalogs/mycatalog', True, 'catalog.groups.*.controls.*', 'catalog.*', True)
    ],
    ids=[
        'In expected working directory',
        'In expected, using absolute paths',
        'out of expected relative paths using trestle root',
        'out of expected using something other than trestle root',
        'out of expected absolute paths'
    ]
)
def test_split_merge_out_of_context(
    testdata_dir,
    tmp_trestle_dir,
    rel_context_dir: str,
    use_absolutes: bool,
    split_elem: str,
    merge_elem: str,
    use_effective_cwd: bool
):
    """Test merging data that has been split using the split command- to ensure symmetry."""
    # trestle split -f catalog.json -e catalog.groups.*.controls.*

    # prepare trestle project dir with the file - could e cleaned up.
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)
    test_data_source = testdata_dir / 'split_merge/step0-merged_catalog/catalogs/'  # Pontentially change to NIST DIR
    catalogs_dir = Path('catalogs/')
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    full_path_to_model_dir = tmp_trestle_dir / 'catalogs' / 'mycatalog'
    full_path_to_model = full_path_to_model_dir / 'catalog.json'
    full_context_dir = tmp_trestle_dir / rel_context_dir

    if use_absolutes:
        model_file = full_path_to_model
    else:
        model_file = full_path_to_model.relative_to(full_context_dir)

    # Always use full context dir for safety
    os.chdir(full_context_dir)

    # Read and store the catalog before split
    stripped_catalog_type, _ = fs.get_stripped_model_type(full_path_to_model.resolve(), tmp_trestle_dir)
    pre_split_catalog = stripped_catalog_type.oscal_read(full_path_to_model)
    assert 'groups' in pre_split_catalog.__fields__.keys()

    # Split the catalog
    args = argparse.Namespace(
        name='split', file=model_file, verbose=0, element=split_elem, trestle_root=tmp_trestle_dir
    )
    split = SplitCmd()._run(args)

    assert split == 0

    interim_catalog_type, _ = fs.get_stripped_model_type(full_path_to_model.resolve(), tmp_trestle_dir)
    interim_catalog = interim_catalog_type.oscal_read(full_path_to_model.resolve())
    assert 'groups' not in interim_catalog.__fields__.keys()

    # Merge everything back into the catalog
    # Equivalent to trestle merge -e catalog.*
    if use_effective_cwd:
        plan = MergeCmd.merge(full_path_to_model_dir, ElementPath(merge_elem), trestle_root=tmp_trestle_dir)

    else:
        os.chdir(full_path_to_model_dir)
        plan = MergeCmd.merge(pathlib.Path.cwd(), ElementPath(merge_elem), trestle_root=tmp_trestle_dir)
    plan.execute()

    # Check both the catalogs are the same.
    post_catalog_type, _ = fs.get_stripped_model_type(full_path_to_model.resolve(), tmp_trestle_dir)
    post_merge_catalog = post_catalog_type.oscal_read(full_path_to_model)
    assert post_merge_catalog == pre_split_catalog


def test_merge_deletes_folders(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test merge all components deletes empty folders."""
    catalog = testdata_dir / 'json/minimal_catalog_with_groups.json'

    command_import = f'trestle import -f {catalog} -o mycatalog'
    execute_command_and_assert(command_import, 0, monkeypatch)

    os.chdir(tmp_trestle_dir / 'catalogs/mycatalog')
    command_split = "trestle split -f ./catalog.json -e 'catalog.metadata,catalog.groups,catalog.back-matter'"
    execute_command_and_assert(command_split, 0, monkeypatch)

    command_merge = "trestle merge -e 'catalog.metadata,catalog.groups,catalog.back-matter'"
    execute_command_and_assert(command_merge, 0, monkeypatch)
    assert not (tmp_trestle_dir / 'catalogs/mycatalog/catalog').exists()

    command_split = "trestle split -f ./catalog.json -e 'catalog.metadata,catalog.groups,catalog.back-matter'"
    execute_command_and_assert(command_split, 0, monkeypatch)

    command_merge = "trestle merge -e 'catalog.*'"
    execute_command_and_assert(command_merge, 0, monkeypatch)
    assert not (tmp_trestle_dir / 'catalogs/mycatalog/catalog').exists()

    # Merge subdir
    command_split = "trestle split -f ./catalog.json -e 'catalog.metadata,catalog.groups,catalog.back-matter'"
    execute_command_and_assert(command_split, 0, monkeypatch)

    os.chdir(tmp_trestle_dir / 'catalogs/mycatalog/catalog')
    command_split = "trestle split -f ./metadata.json -e 'metadata.roles,metadata.responsible-parties'"
    execute_command_and_assert(command_split, 0, monkeypatch)

    command_merge = "trestle merge -e 'metadata.roles,metadata.responsible-parties'"
    execute_command_and_assert(command_merge, 0, monkeypatch)
    assert (tmp_trestle_dir / 'catalogs/mycatalog/catalog').exists()
    assert not (tmp_trestle_dir / 'catalogs/mycatalog/catalog/metadata').exists()
