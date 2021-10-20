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
"""Tests for trestle load_distributed module."""

import shutil

from tests import test_utils

from trestle.oscal.catalog import Catalog
from trestle.oscal.common import Role
from trestle.utils import fs
from trestle.utils.load_distributed import _load_list, load_distributed


def test_load_list(testdata_dir, tmp_trestle_dir):
    """Test loading a list recursively."""
    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)

    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'

    catalogs_dir = tmp_trestle_dir / 'catalogs'
    mycatalog_dir = catalogs_dir / 'mycatalog'
    catalog_dir = mycatalog_dir / 'catalog'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    actual_model_type, actual_model_alias, actual_roles = _load_list(catalog_dir / 'metadata' / 'roles',
                                                                     tmp_trestle_dir)

    expected_roles = [
        Role.oscal_read(catalog_dir / 'metadata/roles/00000__role.json'),
        Role.oscal_read(catalog_dir / 'metadata/roles/00001__role.json')
    ]
    expected_model_type, _ = fs.get_stripped_model_type((catalog_dir / 'metadata/roles').resolve(), tmp_trestle_dir)

    assert actual_model_type.__signature__ == expected_model_type.__signature__
    assert actual_model_alias == 'catalog.metadata.roles'
    assert test_utils.list_unordered_equal(actual_roles, expected_roles)


def test_load_list_group(testdata_dir, tmp_trestle_dir):
    """Test more complicated list loading."""
    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)

    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'

    catalogs_dir = tmp_trestle_dir / 'catalogs'
    mycatalog_dir = catalogs_dir / 'mycatalog'
    catalog_dir = mycatalog_dir / 'catalog'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    actual_model_type, _, actual_groups = _load_list(catalog_dir / 'groups', tmp_trestle_dir)

    # load_list is expected to return a list of array, instead of an instance of Groups class
    expected_groups = (actual_model_type.oscal_read(testdata_dir / 'split_merge/load_distributed/groups.json')).__root__

    assert actual_groups == expected_groups


def test_load_distributed(testdata_dir, tmp_trestle_dir):
    """Test massive distributed load, that includes recusive load, list and dict."""
    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)

    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'

    catalogs_dir = tmp_trestle_dir / 'catalogs'
    mycatalog_dir = catalogs_dir / 'mycatalog'
    catalog_file = mycatalog_dir / 'catalog.json'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    actual_model_type, actual_model_alias, actual_model_instance = load_distributed(catalog_file, tmp_trestle_dir)

    expected_model_instance = Catalog.oscal_read(testdata_dir / 'split_merge/load_distributed/catalog.json')

    assert actual_model_type == Catalog
    assert actual_model_alias == 'catalog'
    assert test_utils.models_are_equivalent(expected_model_instance, actual_model_instance)
