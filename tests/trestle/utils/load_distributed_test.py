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
from typing import Dict

import pytest

from tests import test_utils

from trestle.common.err import TrestleError
from trestle.common.model_utils import ModelUtils
from trestle.oscal.catalog import Catalog
from trestle.oscal.common import Role


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

    actual_model_type, actual_model_alias, actual_roles = ModelUtils._load_list(
        catalog_dir / 'metadata' / 'roles', tmp_trestle_dir
    )

    expected_roles = [
        Role.oscal_read(catalog_dir / 'metadata/roles/00000__role.json'),
        Role.oscal_read(catalog_dir / 'metadata/roles/00001__role.json'),
    ]
    expected_model_type, _ = ModelUtils.get_stripped_model_type(
        (catalog_dir / 'metadata/roles').resolve(), tmp_trestle_dir
    )

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

    actual_model_type, _, actual_groups = ModelUtils._load_list(catalog_dir / 'groups', tmp_trestle_dir)

    # load_list is expected to return a list of array, instead of an instance of Groups class
    expected_groups = actual_model_type.oscal_read(testdata_dir / 'split_merge/load_distributed/groups.json')

    # Pydantic v2: RootModel uses 'root' instead of '__root__'
    # FIXME confirm this is correct.  root was not needed prior to updating oscal to dev branch
    assert actual_groups == expected_groups.root


def test_load_distributed(testdata_dir, tmp_trestle_dir):
    """Test massive distributed load, that includes recursive load and list."""
    # prepare trestle project dir with the file
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)

    test_data_source = testdata_dir / 'split_merge/step4_split_groups_array/catalogs'

    catalogs_dir = tmp_trestle_dir / 'catalogs'
    mycatalog_dir = catalogs_dir / 'mycatalog'
    catalog_file = mycatalog_dir / 'catalog.json'

    # Copy files from test/data/split_merge/step4
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    actual_model_type, actual_model_alias, actual_model_instance = ModelUtils.load_distributed(
        catalog_file, tmp_trestle_dir
    )

    expected_model_instance = Catalog.oscal_read(testdata_dir / 'split_merge/load_distributed/catalog.json')

    assert actual_model_type == Catalog
    assert actual_model_alias == 'catalog'
    assert ModelUtils.models_are_equivalent(expected_model_instance, actual_model_instance)

    # confirm it fails attempting to load collection type that is not a list
    with pytest.raises(TrestleError):
        actual_model_type, actual_model_alias, actual_model_instance = ModelUtils.load_distributed(
            catalog_file, tmp_trestle_dir, Dict
        )


def test_get_primary_model_instance_json(tmp_path):
    """_get_primary_model_instance reads a plain JSON value for non-OscalBaseModel types."""
    import json
    from trestle.common.model_utils import ModelUtils

    # Write a split-file style JSON: {"field-name": value}
    json_file = tmp_path / 'field.json'
    json_file.write_text(json.dumps({'last-modified': '2024-01-01T00:00:00+00:00'}), encoding='utf8')

    # AwareDatetime has no oscal_read — the else branch is taken
    from pydantic import AwareDatetime

    result = ModelUtils._get_primary_model_instance(AwareDatetime, json_file)

    assert result == '2024-01-01T00:00:00+00:00'


def test_get_primary_model_instance_yaml(tmp_path):
    """_get_primary_model_instance reads a plain YAML value for non-OscalBaseModel types."""
    from trestle.common.model_utils import ModelUtils

    yaml_file = tmp_path / 'field.yaml'
    yaml_file.write_text('last-modified: "2024-06-15T12:00:00+00:00"\n', encoding='utf8')

    from pydantic import AwareDatetime

    result = ModelUtils._get_primary_model_instance(AwareDatetime, yaml_file)

    assert result == '2024-06-15T12:00:00+00:00'


def test_pluralized_alias_to_singular_irregular() -> None:
    """'props' maps to its irregular singular 'property'."""
    from trestle.common.model_utils import _pluralized_alias_to_singular

    assert _pluralized_alias_to_singular('props') == 'property'


def test_pluralized_alias_to_singular_ies() -> None:
    """Aliases ending in '-ies' have the suffix replaced with '-y'."""
    from trestle.common.model_utils import _pluralized_alias_to_singular

    assert _pluralized_alias_to_singular('parties') == 'party'
    assert _pluralized_alias_to_singular('capabilities') == 'capability'


def test_pluralized_alias_to_singular_s() -> None:
    """Aliases ending in 's' have the trailing 's' stripped."""
    from trestle.common.model_utils import _pluralized_alias_to_singular

    assert _pluralized_alias_to_singular('role-ids') == 'role-id'
    assert _pluralized_alias_to_singular('addr-lines') == 'addr-line'
    assert _pluralized_alias_to_singular('values') == 'value'


def test_pluralized_alias_to_singular_no_suffix() -> None:
    """Aliases with no recognized plural suffix are returned unchanged."""
    from trestle.common.model_utils import _pluralized_alias_to_singular

    assert _pluralized_alias_to_singular('select') == 'select'
    assert _pluralized_alias_to_singular('method') == 'method'
