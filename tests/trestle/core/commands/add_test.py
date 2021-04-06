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
"""Tests for trestle add command."""
import os
import pathlib
import sys
from unittest.mock import patch

import pytest

from tests import test_utils

import trestle.core.err as err
from trestle.cli import Trestle
from trestle.core.commands.add import AddCmd
from trestle.core.models.actions import UpdateAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.catalog import BackMatter, Catalog
from trestle.utils.fs import get_stripped_contextual_model


def test_add(tmp_path, sample_catalog_minimal):
    """Test AddCmd.add() method for trestle add."""
    # expected catalog after first add of Role
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles.json')
    expected_catalog_roles1 = Element(Catalog.oscal_read(file_path))

    # expected catalog after second add of Role
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles_double.json')
    expected_catalog_roles2 = Element(Catalog.oscal_read(file_path))

    # expected catalog after add of Responsible-Party
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles_double_rp.json')
    expected_catalog_roles2_rp = Element(Catalog.oscal_read(file_path))

    content_type = FileContentType.JSON

    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )

    # Execute first _add
    element_path = ElementPath('catalog.metadata.roles')
    catalog_element = Element(sample_catalog_minimal)
    expected_update_action_1 = UpdateAction(expected_catalog_roles1.get_at(element_path), catalog_element, element_path)
    actual_update_action, actual_catalog_roles = AddCmd.add(element_path, Catalog, catalog_element)

    assert actual_catalog_roles == expected_catalog_roles1
    assert actual_update_action == expected_update_action_1

    # Execute second _add - this time roles already exists, so this adds a roles object to roles array
    catalog_element = actual_catalog_roles
    expected_update_action_2 = UpdateAction(expected_catalog_roles2.get_at(element_path), catalog_element, element_path)
    actual_update_action2, actual_catalog_roles2 = AddCmd.add(element_path, Catalog, catalog_element)
    assert actual_catalog_roles2 == expected_catalog_roles2
    assert actual_update_action2 == expected_update_action_2

    # Execute _add for responsible-parties to the same catalog
    element_path = ElementPath('catalog.metadata.responsible-parties')
    catalog_element = actual_catalog_roles2
    expected_update_action_3 = UpdateAction(
        expected_catalog_roles2_rp.get_at(element_path), catalog_element, element_path
    )
    actual_update_action3, actual_catalog_roles2_rp = AddCmd.add(element_path, Catalog, catalog_element)
    assert actual_catalog_roles2_rp == expected_catalog_roles2_rp
    assert actual_update_action3 == expected_update_action_3


def test_add_failure(tmp_path, sample_catalog_minimal):
    """Test AddCmd.add() method for trestle add."""
    content_type = FileContentType.JSON

    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )

    element_path = ElementPath('catalog.metadata.*')
    catalog_element = Element(sample_catalog_minimal)

    with pytest.raises(err.TrestleError):
        AddCmd.add(element_path, Catalog, catalog_element)

    element_path = ElementPath('catalog.metadata.title')
    with pytest.raises(err.TrestleError):
        AddCmd.add(element_path, Catalog, catalog_element)

    element_path = ElementPath('catalog.metadata.bad_path')
    with pytest.raises(err.TrestleError):
        AddCmd.add(element_path, Catalog, catalog_element)


def test_run_failure():
    """Test failure of _run for AddCmd."""
    testargs = ['trestle', 'add', '-e', 'catalog.metadata.roles']
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit) as e:
            Trestle().run()
        assert e.type == SystemExit
        assert e.value.code == 2

    testargs = ['trestle', 'add', '-f', './catalog.json']
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit) as e:
            Trestle().run()
        assert e.type == SystemExit
        assert e.value.code == 2


def test_run(tmp_path, sample_catalog_minimal):
    """Test _run for AddCmd."""
    # expected catalog after add of Responsible-Party
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles_double_rp.json')
    expected_catalog_roles2_rp = Catalog.oscal_read(file_path)

    content_type = FileContentType.YAML

    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )

    testargs = [
        'trestle',
        'add',
        '-f',
        str(catalog_def_file),
        '-e',
        'catalog.metadata.roles, catalog.metadata.roles, catalog.metadata.responsible-parties'
    ]

    with patch.object(sys, 'argv', testargs):
        assert Trestle().run() == 0

    actual_catalog = Catalog.oscal_read(catalog_def_file)
    assert expected_catalog_roles2_rp == actual_catalog


def test_striped_model(tmp_path, sample_catalog_minimal):
    """Test _run for AddCmd for stripped model."""
    cwd = os.getcwd()
    content_type = FileContentType.JSON
    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )
    os.chdir(catalog_def_dir)
    testargs = ['trestle', 'split', '-f', 'catalog.json', '-e', 'catalog.metadata']
    with patch.object(sys, 'argv', testargs):
        assert Trestle().run() == 0

    # Now that the metadata has been split, add of catalog.metadata.roles will error,
    # but add of catalog.back-matter will pass

    testargs = ['trestle', 'add', '-f', 'catalog.json', '-e', 'catalog.metadata.roles']

    with patch.object(sys, 'argv', testargs):
        assert Trestle().run() == 1

    testargs = ['trestle', 'add', '-f', 'catalog.json', '-e', 'catalog.back-matter']

    current_model, _ = get_stripped_contextual_model()
    current_catalog = current_model.oscal_read(pathlib.Path('catalog.json'))
    current_catalog.back_matter = BackMatter()
    expected_catalog = current_catalog

    with patch.object(sys, 'argv', testargs):
        assert Trestle().run() == 0

    actual_model, _ = get_stripped_contextual_model()
    actual_catalog = actual_model.oscal_read(pathlib.Path('catalog.json'))
    assert expected_catalog == actual_catalog

    os.chdir(cwd)
