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
from trestle.core.commands.remove import RemoveCmd
from trestle.core.models.actions import RemoveAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.oscal.catalog import Catalog


def test_remove(tmp_dir, sample_catalog_minimal):
    """Test RemoveCmd.remove() method for trestle remove: removing Roles and Responsible-Parties."""
    # 1. Remove responsible-parties
    # Note: minimal catalog does have responsible-parties but doesn't have Roles.
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog.json')
    catalog_with_responsible_parties = Element(Catalog.oscal_read(file_path))

    # minimal catalog with responsible-parties (dict) removed
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_no_responsible-parties.json')
    expected_catalog_responsible_parties_removed = Element(Catalog.oscal_read(file_path))

    # Target path for removal:
    element_path = ElementPath('catalog.metadata.responsible-parties')
    expected_remove_action = RemoveAction(catalog_with_responsible_parties, element_path)

    # Call remove() method
    actual_remove_action, actual_catalog_removed_responsible_parties = RemoveCmd.remove(
        element_path, Catalog, catalog_with_responsible_parties
    )

    # 1.1 Assertion about action
    assert expected_remove_action == actual_remove_action

    add_plan = Plan()
    add_plan.add_action(actual_remove_action)
    add_plan.simulate()
    add_plan.execute()

    # 1.2 Assertion about resulting element after removal
    assert expected_catalog_responsible_parties_removed == actual_catalog_removed_responsible_parties

    # 2. Remove roles
    # Note: minimal catalog does have responsible-parties but doesn't have Roles.
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog.json')
    catalog_without_roles = Element(Catalog.oscal_read(file_path))

    # minimal catalog with Roles
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles.json')
    catalog_with_roles = Element(Catalog.oscal_read(file_path))

    # Target path for removal:
    element_path = ElementPath('catalog.metadata.roles')
    expected_remove_action = RemoveAction(catalog_with_roles, element_path)

    # Call remove() method
    actual_remove_action, actual_catalog_removed_roles = RemoveCmd.remove(element_path, Catalog, catalog_with_roles)

    # 2.1 Assertion about action
    assert expected_remove_action == actual_remove_action

    add_plan = Plan()
    add_plan.add_action(actual_remove_action)
    add_plan.simulate()
    add_plan.execute()

    # 2.2 Assertion about resulting element after removal
    assert catalog_without_roles == actual_catalog_removed_roles


def test_remove_failure(tmp_dir, sample_catalog_minimal):
    """Test failure of RemoveCmd.remove() method for trestle remove."""
    # Remove metadata -- should raise an error

    content_type = FileContentType.JSON

    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_dir,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )

    # Note: minimal catalog just has uuid and metadata, both required.
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog.json')
    minimal_catalog = Element(Catalog.oscal_read(file_path))

    # 1. Remove a required element:
    element_path = ElementPath('catalog.metadata')
    with pytest.raises(err.TrestleError):
        remove_action, remove_results = RemoveCmd.remove(element_path, Catalog, minimal_catalog)
        add_plan = Plan()
        add_plan.add_action(remove_action)
        add_plan.simulate()
        add_plan.execute()

    # 2. Remove an element that is not there:
    element_path = ElementPath('catalog.metadata.roles')
    with pytest.raises(err.TrestleError):
        remove_action, remove_results = RemoveCmd.remove(element_path, Catalog, minimal_catalog)
        add_plan = Plan()
        add_plan.add_action(remove_action)
        add_plan.simulate()
        add_plan.execute()

    # 3. Remove an element with a wildcard:
    element_path = ElementPath('catalog.metadata.*')
    with pytest.raises(err.TrestleError):
        remove_action, remove_results = RemoveCmd.remove(element_path, Catalog, minimal_catalog)
        add_plan = Plan()
        add_plan.add_action(remove_action)
        add_plan.simulate()
        add_plan.execute()


def test_run_failure():
    """Test failure of _run for RemoveCmd."""
    testargs = ['trestle', 'remove', '-e', 'catalog.metadata.roles']
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit) as e:
            Trestle().run()
        assert e.type == SystemExit
        assert e.value.code == 2

    testargs = ['trestle', 'remove', '-f', './catalog.json']
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit) as e:
            Trestle().run()
        assert e.type == SystemExit
        assert e.value.code == 2


def test_run(tmp_dir, sample_catalog_minimal):
    """Test _run for RemoveCmd."""
    # 1. Test trestle remove for one element.
    # expected catalog after remove of Responsible-Party
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_no_responsible-parties.json')
    expected_catalog_no_rp = Catalog.oscal_read(file_path)

    content_type = FileContentType.JSON

    # Create a temporary file with responsible-parties to be removed.
    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_dir,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )

    testargs = ['trestle', 'remove', '-f', str(catalog_def_file), '-e', 'catalog.metadata.responsible-parties']

    with patch.object(sys, 'argv', testargs):
        Trestle().run()

    actual_catalog = Catalog.oscal_read(catalog_def_file)
    assert expected_catalog_no_rp == actual_catalog

    # 2. Test trestle remove for multiple comma-separated elements.
    # minimal catalog with Roles and Resposibile-Parties.
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles.json')
    catalog_with_roles_responsible_parties = Catalog.oscal_read(file_path)

    # Create a temporary file with Roles and Responsible-Parties to be removed.
    catalog_def_dir, catalog_def_file_2 = test_utils.prepare_trestle_project_dir(
        tmp_dir,
        content_type,
        catalog_with_roles_responsible_parties,
        test_utils.CATALOGS_DIR
    )

    testargs = [
        'trestle',
        'remove',
        '-f',
        str(catalog_def_file_2),
        '-e',
        'catalog.metadata.responsible-parties,catalog.metadata.roles'
    ]

    with patch.object(sys, 'argv', testargs):
        Trestle().run()

    actual_catalog = Catalog.oscal_read(catalog_def_file_2)
    assert expected_catalog_no_rp == actual_catalog
