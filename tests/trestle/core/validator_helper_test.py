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
"""Tests for models util module."""

import pathlib
from uuid import uuid4

from ruamel.yaml import YAML

import tests.test_utils as test_utils

import trestle.core.const as const
import trestle.core.validator_helper as validator_helper
import trestle.oscal.catalog as catalog
import trestle.oscal.common as common
import trestle.oscal.component as component
import trestle.oscal.ssp as ssp

ssp_path = pathlib.Path('nist-content/src/examples/ssp/json/ssp-example.json')
catalog_path = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME


def test_has_no_duplicate_values_generic() -> None:
    """Test presence of duplicate uuid."""
    # test with pydantic catalog
    cat = catalog.Catalog.oscal_read(catalog_path)
    assert validator_helper.has_no_duplicate_values_generic(cat, 'uuid')

    # test with valid pydantic target
    good_component_path = test_utils.YAML_TEST_DATA_PATH / 'good_component.yaml'
    good_component = component.ComponentDefinition.oscal_read(good_component_path)
    validator_helper.find_values_by_name(good_component, 'uuid')
    assert validator_helper.has_no_duplicate_values_by_name(good_component, 'uuid')

    # test with pydantic target containing duplicates
    bad_component_path = test_utils.YAML_TEST_DATA_PATH / 'bad_component_dup_uuid.yaml'
    bad_component = component.ComponentDefinition.oscal_read(bad_component_path)
    assert not validator_helper.has_no_duplicate_values_by_name(bad_component, 'uuid')

    # test duplicates with raw yaml target, non-pydantic
    read_file = bad_component_path.open('r', encoding=const.FILE_ENCODING)
    yaml = YAML(typ='safe')
    bad_component_yaml = yaml.load(read_file)
    assert not validator_helper.has_no_duplicate_values_generic(bad_component_yaml, 'uuid')


def test_has_no_duplicate_values_pydantic() -> None:
    """Test presence of duplicate values in pydantic objects."""
    # test with pydantic catalog - only one instance of Metadata
    cat = catalog.Catalog.oscal_read(catalog_path)
    assert validator_helper.has_no_duplicate_values_by_type(cat, common.Metadata)

    # test presence of many duplicate properties
    good_component_path = test_utils.YAML_TEST_DATA_PATH / 'good_component.yaml'
    good_component = component.ComponentDefinition.oscal_read(good_component_path)
    assert not validator_helper.has_no_duplicate_values_by_type(good_component, common.Property)


def test_regenerate_uuids_ssp() -> None:
    """Test regeneration of uuids with updated refs in ssp."""
    orig_ssp = ssp.SystemSecurityPlan.oscal_read(ssp_path)
    new_ssp, uuid_lut, n_refs_updated = validator_helper.regenerate_uuids(orig_ssp)
    assert len(uuid_lut.items()) == 36
    assert n_refs_updated == 23


def test_regenerate_uuids_catalog() -> None:
    """Test regeneration of uuids with updated refs in catalog."""
    orig_cat = catalog.Catalog.oscal_read(catalog_path)
    new_cat, uuid_lut, n_refs_updated = validator_helper.regenerate_uuids(orig_cat)
    assert len(uuid_lut.items()) == 2
    assert n_refs_updated == 2


def test_find_all_attribs_by_regex() -> None:
    """Test finding attribs by regex."""
    cat = catalog.Catalog.oscal_read(catalog_path)
    attrs = validator_helper.find_all_attribs_by_regex(cat, r'party.uuid')
    assert len(attrs) == 2


def test_validations_on_dict() -> None:
    """Test regen of uuid in dict."""
    my_uuid1 = str(uuid4())
    my_uuid2 = str(uuid4())
    my_dict = {'uuid': my_uuid1, 'ref': my_uuid1, 'my_inner_dict': {'uuid': my_uuid2, 'ref': my_uuid2}}
    new_dict, lut = validator_helper.regenerate_uuids_in_place(my_dict, {})
    assert my_dict['uuid'] != new_dict['uuid']
    assert my_dict['my_inner_dict']['uuid'] != new_dict['my_inner_dict']['uuid']
    assert len(lut) == 2

    fixed_dict, count = validator_helper.update_new_uuid_refs(new_dict, lut)
    assert fixed_dict['uuid'] == fixed_dict['ref']
    assert fixed_dict['my_inner_dict']['uuid'] == fixed_dict['my_inner_dict']['ref']
    assert count == 2

    attrs = validator_helper.find_all_attribs_by_regex(fixed_dict, 'uuid')
    assert len(attrs) == 2
    assert attrs[0] == ('uuid', fixed_dict['uuid'])


def test_find_in_dict() -> None:
    """Test finding values in dict."""
    my_dict = {'a': 'foo', 'b': 'bar', 'c': {'x': 1, 'y': 'hello'}}
    result = validator_helper.find_values_by_type(my_dict, str)
    assert result == ['foo', 'bar', 'hello']

    ints = validator_helper.find_values_by_type(my_dict, int)
    assert ints == [1]


def test_find_by_name() -> None:
    """Test finding by name in dict."""
    my_dict = {'a': 'foo', 'b': 'bar', 'c': {'x': 1, 'a': 7, 'y': 'hello'}}
    result = validator_helper.find_values_by_name(my_dict, 'a')
    assert result == ['foo', 7]
