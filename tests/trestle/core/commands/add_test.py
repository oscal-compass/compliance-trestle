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
import pathlib
import sys
from unittest.mock import patch

import pytest

from tests import test_utils

import trestle.core.err as err
from trestle.cli import Trestle
from trestle.core.commands.add import AddCmd
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.catalog import Catalog


def test_add(tmp_dir, sample_catalog_minimal):
    """Test AddCmd.add() method for trestle add."""
    # expected catalog after first add of Role
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles.json')
    expected_catalog_roles1 = Catalog.oscal_read(file_path)

    # expected catalog after second add of Role
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles_double.json')
    expected_catalog_roles2 = Catalog.oscal_read(file_path)

    # expected catalog after add of Responsible-Party
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles_double_rp.json')
    expected_catalog_roles2_rp = Catalog.oscal_read(file_path)

    content_type = FileContentType.JSON

    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_dir,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )

    # Execute first _add
    element_path = ElementPath('catalog.metadata.roles')
    catalog_element = Element(sample_catalog_minimal)
    AddCmd.add(catalog_def_dir / catalog_def_file, element_path, Catalog, catalog_element)

    actual_catalog_roles = Catalog.oscal_read(catalog_def_dir / catalog_def_file)
    assert actual_catalog_roles == expected_catalog_roles1

    # Execute second _add - this time roles already exists, so this adds a roles object to roles array
    catalog_element = Element(actual_catalog_roles)
    AddCmd.add(catalog_def_dir / catalog_def_file, element_path, Catalog, catalog_element)
    actual_catalog_roles2 = Catalog.oscal_read(catalog_def_dir / catalog_def_file)
    assert actual_catalog_roles2 == expected_catalog_roles2

    # Execute _add for responsible-parties to the same catalog
    element_path = ElementPath('catalog.metadata.responsible-parties')
    catalog_element = Element(actual_catalog_roles2)
    AddCmd.add(catalog_def_dir / catalog_def_file, element_path, Catalog, catalog_element)
    actual_catalog_roles2_rp = Catalog.oscal_read(catalog_def_dir / catalog_def_file)
    assert actual_catalog_roles2_rp == expected_catalog_roles2_rp


def test_add_failure(tmp_dir, sample_catalog_minimal):
    """Test AddCmd.add() method for trestle add."""
    content_type = FileContentType.JSON

    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_dir,
        content_type,
        sample_catalog_minimal,
        test_utils.CATALOGS_DIR
    )

    element_path = ElementPath('catalog.metadata.*')
    catalog_element = Element(sample_catalog_minimal)

    with pytest.raises(err.TrestleError):
        AddCmd.add(catalog_def_dir / catalog_def_file, element_path, Catalog, catalog_element)

    element_path = ElementPath('catalog.metadata.title')
    with pytest.raises(err.TrestleError):
        AddCmd.add(catalog_def_dir / catalog_def_file, element_path, Catalog, catalog_element)

    element_path = ElementPath('catalog.metadata.bad_path')
    with pytest.raises(err.TrestleError):
        AddCmd.add(catalog_def_dir / catalog_def_file, element_path, Catalog, catalog_element)


def test_run_failure():
    """Test failure of _run for AddCmd."""
    testargs = ['trestle', 'add', '-e', 'catalog.metadata.roles']
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(err.TrestleError):
            Trestle().run()

    testargs = ['trestle', 'add', '-f', './catalog.json']
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(err.TrestleError):
            Trestle().run()


def test_run(tmp_dir, sample_catalog_minimal):
    """Test _run for AddCmd."""
    # expected catalog after add of Responsible-Party
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles_double_rp.json')
    expected_catalog_roles2_rp = Catalog.oscal_read(file_path)

    content_type = FileContentType.YAML

    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_dir,
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
        Trestle().run()

    actual_catalog = Catalog.oscal_read(catalog_def_file)
    assert expected_catalog_roles2_rp == actual_catalog
