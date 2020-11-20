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
"""Tests for trestle remove command."""
import pathlib
import sys
from unittest.mock import patch

import pytest

from tests import test_utils

import trestle.core.err as err
from trestle.cli import Trestle
from trestle.core.commands.add import AddCmd
from trestle.core.commands.remove import RemoveCmd
from trestle.core.models.actions import RemoveAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.oscal.catalog import Catalog


def test_remove(tmp_dir, sample_catalog_minimal):
    """Test RemoveCmd.remove() method for trestle remove: removing Roles."""
    # minimal catalog, no Roles
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog.json')
    minimal_catalog = Element(Catalog.oscal_read(file_path))
#    minimal_catalog_model = Catalog.oscal_read(file_path)

    # minimal catalog with Roles
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles.json')
    catalog_with_roles = Element(Catalog.oscal_read(file_path))

    # minimal catalog with responsible-parties (dict) removed
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_no_responsible-parties.json')
    expected_catalog_responsible_parties_removed = Element(Catalog.oscal_read(file_path))

    content_type = FileContentType.JSON

    # catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
    #     tmp_dir,
    #     content_type,
    #     sample_catalog_minimal,
    #     test_utils.CATALOGS_DIR
    # )

    element_path = ElementPath('catalog.metadata.responsible-parties')
    catalog_element = Element(sample_catalog_minimal)
    expected_remove_action = RemoveAction(catalog_element, element_path)

    actual_remove_action, actual_catalog_removed_responsible_parties = RemoveCmd.remove(element_path, Catalog, catalog_element)

    assert expected_remove_action == actual_remove_action
#    assert expected_catalog_responsible_parties_removed == actual_catalog_removed_responsible_parties

    add_plan = Plan()
    add_plan.add_action(actual_remove_action)
    add_plan.simulate()
    add_plan.execute()

    assert catalog_element == actual_catalog_removed_responsible_parties
