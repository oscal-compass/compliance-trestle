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
"""Tests for trestle remove command."""
import pathlib
import re
import shutil
import sys

from _pytest.monkeypatch import MonkeyPatch

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


def test_remove(tmp_path: pathlib.Path):
    """Test RemoveCmd.remove() method for trestle remove: removing Roles and Responsible-Parties."""
    # 1. Remove responsible-parties
    # Note: minimal catalog does have responsible-parties but doesn't have Roles.
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_missing_roles.json')
    catalog_with_responsible_parties = Element(Catalog.oscal_read(file_path))

    # minimal catalog with responsible-parties (dict) removed
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_no_responsible-parties.json')
    expected_catalog_responsible_parties_removed = Element(Catalog.oscal_read(file_path))

    # Target path for removal:
    element_path = ElementPath('catalog.metadata.responsible-parties')
    expected_remove_action = RemoveAction(catalog_with_responsible_parties, element_path)

    # Call remove() method
    actual_remove_action, actual_catalog_removed_responsible_parties = RemoveCmd.remove(
        element_path, catalog_with_responsible_parties
    )

    # 1.1 Assertion about action
    assert expected_remove_action == actual_remove_action

    add_plan = Plan()
    add_plan.add_action(actual_remove_action)
    add_plan.execute()

    # 1.2 Assertion about resulting element after removal
    assert expected_catalog_responsible_parties_removed == actual_catalog_removed_responsible_parties

    # 2. Remove roles
    # Note: minimal catalog does have responsible-parties but doesn't have Roles.
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_missing_roles.json')
    catalog_without_roles = Element(Catalog.oscal_read(file_path))

    # minimal catalog with Roles
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles.json')
    catalog_with_roles = Element(Catalog.oscal_read(file_path))

    # Target path for removal:
    element_path = ElementPath('catalog.metadata.roles')
    expected_remove_action = RemoveAction(catalog_with_roles, element_path)

    # Call remove() method
    actual_remove_action, actual_catalog_removed_roles = RemoveCmd.remove(element_path, catalog_with_roles)

    # 2.1 Assertion about action
    assert expected_remove_action == actual_remove_action

    add_plan = Plan()
    add_plan.add_action(actual_remove_action)
    add_plan.execute()

    # 2.2 Assertion about resulting element after removal
    assert catalog_without_roles == actual_catalog_removed_roles


def test_remove_failure(tmp_path: pathlib.Path):
    """Test failure of RemoveCmd.remove() method for trestle remove."""
    # Note: minimal catalog does have responsible-parties but doesn't have Roles.
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_missing_roles.json')
    catalog_with_responsible_parties = Element(Catalog.oscal_read(file_path))

    # Supply nonexistent element Roles for removal:
    element_path = ElementPath('catalog.metadata.roles')
    try:
        actual_remove_action, actual_catalog_removed_responsible_parties = RemoveCmd.remove(
            element_path, catalog_with_responsible_parties
        )
    except Exception:
        assert True
    else:
        AssertionError()

    # Supply a wildcard element for removal:
    element_path = ElementPath('catalog.*')
    try:
        actual_remove_action, actual_catalog_removed_responsible_parties = RemoveCmd.remove(
            element_path, catalog_with_responsible_parties
        )
    except Exception:
        assert True
    else:
        AssertionError()


def test_run_failure_switches(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test failure of _run on bad switches for RemoveCmd."""
    # 1. Missing --file argument.
    testargs = ['trestle', 'remove', '-e', 'catalog.metadata.roles']
    monkeypatch.setattr(sys, 'argv', testargs)
    with pytest.raises(SystemExit) as e:
        Trestle().run()
    assert e.type == SystemExit
    assert e.value.code == 2

    # 2. Missing --element argument.
    testargs = ['trestle', 'remove', '-f', './catalog.json']
    monkeypatch.setattr(sys, 'argv', testargs)
    with pytest.raises(SystemExit) as e:
        Trestle().run()
    assert e.type == SystemExit
    assert e.value.code == 2


def test_run_failure_nonexistent_element(
    tmp_path: pathlib.Path, sample_catalog_minimal: Catalog, monkeypatch: MonkeyPatch
):
    """Test failure of _run on RemoveCmd in specifying nonexistent element for removal."""
    # Create a temporary catalog file with responsible-parties
    content_type = FileContentType.JSON
    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )

    # 1. self.remove() fails -- Should happen if wildcard is given, or nonexistent element.
    testargs = ['trestle', 'remove', '-f', str(catalog_def_file), '-e', 'catalog.blah']
    monkeypatch.setattr(sys, 'argv', testargs)
    exitcode = Trestle().run()
    assert exitcode == 5

    # 2. Corrupt json file
    source_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'bad_simple.json')
    shutil.copyfile(source_file_path, catalog_def_file)
    testargs = ['trestle', 'remove', '-f', str(catalog_def_file), '-e', 'catalog.metadata.roles']
    monkeypatch.setattr(sys, 'argv', testargs)
    exitcode = Trestle().run()
    assert exitcode == 5


def test_run_failure_wildcard(tmp_path: pathlib.Path, sample_catalog_minimal: Catalog, monkeypatch: MonkeyPatch):
    """Test failure of _run on RemoveCmd in specifying wildcard in element for removal."""
    # Create a temporary catalog file with responsible-parties
    content_type = FileContentType.JSON
    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )
    testargs = ['trestle', 'remove', '-f', str(catalog_def_file), '-e', 'catalog.*']
    monkeypatch.setattr(sys, 'argv', testargs)
    exitcode = Trestle().run()
    assert exitcode == 5


def test_run_failure_required_element(
    tmp_path: pathlib.Path, sample_catalog_minimal: Catalog, monkeypatch: MonkeyPatch
):
    """Test failure of _run on RemoveCmd in specifying a required element for removal."""
    # Create a temporary catalog file with responsible-parties
    content_type = FileContentType.JSON
    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )
    # 4. simulate() fails -- Should happen if required element is target for deletion
    monkeypatch.chdir(tmp_path)
    testargs = ['trestle', 'remove', '-f', str(catalog_def_file), '-e', 'catalog.metadata']
    monkeypatch.setattr(sys, 'argv', testargs)
    exitcode = Trestle().run()
    assert exitcode == 1


def test_run_failure_project_not_found(
    tmp_path: pathlib.Path, sample_catalog_minimal: Catalog, monkeypatch: MonkeyPatch
):
    """Test failure of _run on RemoveCmd in specifying file in non-initialized location."""
    # Create a temporary catalog file with responsible-parties
    content_type = FileContentType.JSON
    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )
    # 5. get_contextual_model_type() fails, i.e., "Trestle project not found"
    testargs = ['trestle', 'remove', '-f', '/dev/null', '-e', 'catalog.metadata']
    monkeypatch.setattr(sys, 'argv', testargs)
    exitcode = Trestle().run()
    assert exitcode == 5


def test_run_failure_filenotfounderror(
    tmp_path: pathlib.Path, sample_catalog_minimal: Catalog, monkeypatch: MonkeyPatch
):
    """Test failure of _run on RemoveCmd in specifying a nonexistent file."""
    # Create a temporary catalog file with responsible-parties
    content_type = FileContentType.JSON
    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )
    # 6. oscal_read fails because file is not found
    # Must specify catalogs/ location, not catalogs/my_test_model/.
    testargs = [
        'trestle', 'remove', '-f', re.sub('my_test_model/', '', str(catalog_def_file)), '-e', 'catalog.metadata'
    ]
    monkeypatch.setattr(sys, 'argv', testargs)
    exitcode = Trestle().run()
    assert exitcode == 5


def test_run_failure_plan_execute(
    tmp_path: pathlib.Path, sample_catalog_minimal: Catalog, monkeypatch: MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    """Test failure plan execute() in _run on RemoveCmd."""
    # Plant this specific logged error for failing execution in mock_execute:
    logged_error = 'fail_execute'

    def mock_execute(*args, **kwargs):
        raise err.TrestleError(logged_error)

    # Create a temporary file as a valid arg for trestle remove:
    content_type = FileContentType.JSON
    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )
    monkeypatch.chdir(tmp_path)
    # Add remarks here, so it is a valid removal target,
    testargs = ['trestle', 'add', '-f', str(catalog_def_file), '-e', 'catalog.metadata.remarks']
    monkeypatch.setattr(sys, 'argv', testargs)
    Trestle().run()
    # .. then attempt to remove it here, but mocking a failed execute:
    testargs = ['trestle', 'remove', '-f', str(catalog_def_file), '-e', 'catalog.metadata.remarks']
    monkeypatch.setattr(Plan, 'execute', mock_execute)
    monkeypatch.setattr(sys, 'argv', testargs)
    caplog.clear()
    rc = Trestle().run()
    assert rc > 0


def test_run(tmp_path: pathlib.Path, sample_catalog_missing_roles, monkeypatch: MonkeyPatch):
    """Test _run for RemoveCmd."""
    # 1. Test trestle remove for one element.
    # expected catalog after remove of Responsible-Party
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_no_responsible-parties.json')
    expected_catalog_no_rp = Catalog.oscal_read(file_path)

    content_type = FileContentType.JSON

    # Create a temporary file with responsible-parties to be removed.
    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog_missing_roles,
        test_utils.CATALOGS_DIR
    )

    testargs = [
        'trestle',
        'remove',
        '-tr',
        str(tmp_path),
        '-f',
        str(catalog_def_file),
        '-e',
        'catalog.metadata.responsible-parties'
    ]

    monkeypatch.setattr(sys, 'argv', testargs)
    assert Trestle().run() == 0

    actual_catalog = Catalog.oscal_read(catalog_def_file)
    assert expected_catalog_no_rp == actual_catalog

    # 2. Test trestle remove for multiple comma-separated elements.
    # minimal catalog with Roles and Resposibile-Parties.
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles.json')
    catalog_with_roles_responsible_parties = Catalog.oscal_read(file_path)

    # Create a temporary file with Roles and Responsible-Parties to be removed.
    catalog_def_dir, catalog_def_file_2 = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        catalog_with_roles_responsible_parties,
        test_utils.CATALOGS_DIR
    )

    testargs = [
        'trestle',
        'remove',
        '-tr',
        str(tmp_path),
        '-f',
        str(catalog_def_file_2),
        '-e',
        'catalog.metadata.responsible-parties,catalog.metadata.roles'
    ]

    monkeypatch.setattr(sys, 'argv', testargs)
    assert Trestle().run() == 0

    actual_catalog = Catalog.oscal_read(catalog_def_file_2)
    assert expected_catalog_no_rp == actual_catalog
