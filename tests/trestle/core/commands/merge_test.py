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

from tests import test_utils

import trestle.oscal.catalog as oscatalog
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs


def test_merge_plan_simple_case(tmp_dir):
    """Test $mycatalog$ trestle merge -e catalog.back-matter."""
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
    merged_dict = stripped_catalog.dict()
    merged_dict['back-matter'] = back_matter.dict()
    merged_catalog = merged_catalog_type(**merged_dict)

    element = Element(merged_catalog, merged_catalog_alias)

    # Create hand-crafter merge plan
    reset_destination_action = CreatePathAction(catalog_file, clear_content=True)
    write_destination_action = WriteFileAction(catalog_file, element, content_type=content_type)
    # To be added: remove_merged_model_action = None

    expected_plan: Plan = Plan()
    expected_plan.add_action(reset_destination_action)
    expected_plan.add_action(write_destination_action)
    # To be added: expected_plan.add_action(remove_merged_model_action)

    expected_plan.execute()

    # Assert the new file structure makes sense
    assert catalog_file.exists()
    new_catalog = merged_catalog_type.oscal_read(catalog_file)
    assert new_catalog.get_field_value_by_alias('back-matter') is not None
    # To be added: assert not back_matter_file.exists()

    # Call generated_plan = mergeCmd.merge()
    # Assert the generated plan matches the expected plan
