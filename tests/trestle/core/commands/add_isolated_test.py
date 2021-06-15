# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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

from tests import test_utils

from trestle.cli import Trestle
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.catalog import Catalog


def test_run(tmp_path, sample_catalog_missing_roles, keep_cwd):
    """Test _run for AddCmd."""
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog_roles_double_rp.json')
    expected_catalog_roles2_rp = Catalog.oscal_read(file_path)

    content_type = FileContentType.YAML

    catalog_def_dir, catalog_def_file = test_utils.prepare_trestle_project_dir(
        tmp_path,
        content_type,
        sample_catalog_missing_roles,
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
