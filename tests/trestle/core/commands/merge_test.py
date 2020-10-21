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
import shutil
from pathlib import Path
from typing import List

import pytest

from tests import test_utils

import trestle.oscal.catalog as oscatalog
from trestle.core.base_model import OscalBaseModel
from trestle.core.commands.merge import MergeCmd
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, RemovePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs


def test_merge_invalid_element_path():
    """Test to make sure each element in -e contains 2 parts at least."""
    cmd = MergeCmd()
    parser = cmd.parser
    args = parser.parse_args(['-e', 'catalog'])

    with pytest.raises(TrestleError):
        cmd._run(args)

    args = parser.parse_args(['-e', 'catalog.metadata'])
    cmd._run(args)


def test_merge_plan_simple_case(tmp_dir):
    """Test '$mycatalog$ trestle merge -e catalog.back-matter'."""
    # Assume we are running a command like below
    # trestle merge -e catalog.back-matter
    content_type = FileContentType.JSON
    fext = FileContentType.to_file_extension(content_type)

    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_dir)

    test_data_source = Path('tests/data/split_merge/step4_split_groups_array/catalogs')
    catalogs_dir = tmp_dir / 'catalogs'
    mycatalog_dir = catalogs_dir / 'mycatalog'
    catalog_dir = mycatalog_dir / 'catalog'
    catalog_file = mycatalog_dir / f'catalog{fext}'
    back_matter_file = catalog_dir / f'back-matter{fext}'

    # Copy files from test/data/split_merge/step4
    shutil.copytree(test_data_source, catalogs_dir)

    assert catalog_file.exists()
    assert back_matter_file.exists()

    # Read files

    # The destination file/model needs to be loaded in a stripped model
    stripped_catalog_type, _ = fs.get_stripped_contextual_model(catalog_file)
    stripped_catalog = stripped_catalog_type.oscal_read(catalog_file)

    # Back-matter model needs to be complete and if it is decomposed, needs to be merged recursively first
    back_matter = oscatalog.BackMatter.oscal_read(back_matter_file)

    # Back-matter needs to be inserted in a stripped Catalog that does NOT exclude the back-matter fields

    merged_catalog_type, merged_catalog_alias = fs.get_stripped_contextual_model(
        catalog_file, aliases_not_to_be_stripped=['back-matter'])
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

    expected_plan.execute()

    # Assert the new file structure makes sense
    assert catalog_file.exists()
    new_catalog = merged_catalog_type.oscal_read(catalog_file)
    assert new_catalog.get_field_value_by_alias('back-matter') is not None
    assert not back_matter_file.exists()

    # Call generated_plan = mergeCmd.merge()
    # Assert the generated plan matches the expected plan


def test_merge_plan_complex_case(tmp_dir):
    """Test '$mycatalog$ trestle merge -e catalog.metadata' when metadata is already split."""
    # Assume we are running a command like below
    # trestle merge -e catalog.back-matter
    content_type = FileContentType.JSON
    fext = FileContentType.to_file_extension(content_type)

    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_dir)

    test_data_source = Path('tests/data/split_merge/step2-split_metadata_elements/catalogs')
    catalogs_dir = tmp_dir / 'catalogs'
    mycatalog_dir = catalogs_dir / 'mycatalog'
    catalog_dir = mycatalog_dir / 'catalog'
    catalog_file = mycatalog_dir / f'catalog{fext}'
    metadata_dir = catalog_dir / 'metadata'
    metadata_file = catalog_dir / f'metadata{fext}'

    # Copy files from test/data/split_merge/step4
    shutil.copytree(test_data_source, catalogs_dir)

    assert catalog_file.exists()
    assert metadata_dir.exists()
    assert metadata_file.exists()

    # Read files

    # Create hand-crafter merge plan
    expected_plan: Plan = Plan()

    #
    # Handle metadata first
    #
    # metatada model needs to be complete and if it is decomposed, needs to be merged recursively first
    if metadata_dir.exists():
        # First action: Reset the intermediate destination: metadata.json
        reset_destination_action = CreatePathAction(metadata_file, clear_content=True)
        expected_plan.add_action(reset_destination_action)

        aliases_not_to_be_stripped = []
        instances_to_be_merged: List[OscalBaseModel] = []
        for filepath in Path.iterdir(metadata_dir):
            if filepath.is_file():
                model_type, model_alias = fs.get_stripped_contextual_model(filepath)
                model_instance = model_type.oscal_read(filepath)

                if hasattr(model_instance, '__root__') and (isinstance(model_instance.__root__, dict)
                                                            or isinstance(model_instance.__root__, list)):
                    model_instance = model_instance.__root__

                instances_to_be_merged.append(model_instance)
                aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
            elif filepath.is_dir():
                pass

        stripped_metadata_type, _ = fs.get_stripped_contextual_model(metadata_file)
        stripped_metadata = stripped_metadata_type.oscal_read(metadata_file)

        # Create merged model and instance for writeaction
        merged_metadata_type, merged_metadata_alias = fs.get_stripped_contextual_model(
            metadata_file, aliases_not_to_be_stripped=aliases_not_to_be_stripped)
        merged_dict = stripped_metadata.__dict__
        for i in range(len(aliases_not_to_be_stripped)):
            alias = aliases_not_to_be_stripped[i]
            instance = instances_to_be_merged[i]
            merged_dict[alias] = instance
        merged_metadata = merged_metadata_type(**merged_dict)
        element = Element(merged_metadata, merged_metadata_alias)

        # Second action: Write new merged contents of metadata.json
        write_destination_action = WriteFileAction(metadata_file, element, content_type=content_type)
        expected_plan.add_action(write_destination_action)

        # Third action: Delete expanded metadata folder
        delete_element_action = RemovePathAction(metadata_dir)
        expected_plan.add_action(delete_element_action)

    #
    # Handle catalog now
    #
    aliases_not_to_be_stripped = ['metadata']
    instances_to_be_merged: List[OscalBaseModel] = [merged_metadata]

    # The destination file/model needs to be loaded in a stripped model
    stripped_catalog_type, _ = fs.get_stripped_contextual_model(catalog_file)
    stripped_catalog = stripped_catalog_type.oscal_read(catalog_file)

    reset_destination_action = CreatePathAction(catalog_file, clear_content=True)
    expected_plan.add_action(reset_destination_action)

    # Create merged model and instance for writeaction
    merged_catalog_type, merged_catalog_alias = fs.get_stripped_contextual_model(
        catalog_file, aliases_not_to_be_stripped=aliases_not_to_be_stripped)
    merged_dict = stripped_catalog.__dict__
    for i in range(len(aliases_not_to_be_stripped)):
        alias = aliases_not_to_be_stripped[i]
        instance = instances_to_be_merged[i]
        merged_dict[alias] = instance
    merged_catalog = merged_catalog_type(**merged_dict)
    element = Element(merged_catalog, merged_catalog_alias)
    write_destination_action = WriteFileAction(catalog_file, element, content_type=content_type)
    expected_plan.add_action(write_destination_action)
    delete_element_action = RemovePathAction(catalog_dir)
    expected_plan.add_action(delete_element_action)

    # Execute plan
    expected_plan.execute()

    # Assert the new file structure makes sense
    assert catalog_file.exists()
    assert not catalog_dir.exists()
    assert not metadata_dir.exists()
    assert not metadata_file.exists()

    # Call generated_plan = mergeCmd.merge()
    # Assert the generated plan matches the expected plan'
