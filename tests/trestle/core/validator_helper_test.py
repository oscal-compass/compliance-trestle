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
"""Tests for validator helper functionality that was moved to model_utils."""

import pathlib
from uuid import uuid4

import tests.test_utils as test_utils

import trestle.oscal.catalog as catalog
import trestle.oscal.ssp as ssp
from trestle.common.model_utils import ModelUtils

ssp_path = pathlib.Path('nist-content/src/examples/ssp/json/ssp-example.json')
catalog_path = test_utils.JSON_TEST_DATA_PATH / test_utils.SIMPLIFIED_NIST_CATALOG_NAME


def test_regenerate_uuids_ssp() -> None:
    """Test regeneration of uuids with updated refs in ssp."""
    orig_ssp = ssp.SystemSecurityPlan.oscal_read(ssp_path)
    new_ssp, uuid_lut, n_refs_updated = ModelUtils.regenerate_uuids(orig_ssp)
    assert len(uuid_lut.items()) == 36
    assert n_refs_updated == 23


def test_regenerate_uuids_catalog() -> None:
    """Test regeneration of uuids with updated refs in catalog."""
    orig_cat = catalog.Catalog.oscal_read(catalog_path)
    _, uuid_lut, n_refs_updated = ModelUtils.regenerate_uuids(orig_cat)
    assert len(uuid_lut.items()) == 2
    assert n_refs_updated == 2


def test_validations_on_dict() -> None:
    """Test regen of uuid in dict."""
    my_uuid1 = str(uuid4())
    my_uuid2 = str(uuid4())
    my_dict = {'uuid': my_uuid1, 'ref': my_uuid1, 'my_inner_dict': {'uuid': my_uuid2, 'ref': my_uuid2}}
    new_dict, lut = ModelUtils._regenerate_uuids_in_place(my_dict, {})
    assert my_dict['uuid'] != new_dict['uuid']
    assert my_dict['my_inner_dict']['uuid'] != new_dict['my_inner_dict']['uuid']
    assert len(lut) == 2

    fixed_dict, count = ModelUtils._update_new_uuid_refs(new_dict, lut)
    assert fixed_dict['uuid'] == fixed_dict['ref']
    assert fixed_dict['my_inner_dict']['uuid'] == fixed_dict['my_inner_dict']['ref']
    assert count == 2


def test_find_by_name() -> None:
    """Test finding by name in dict."""
    my_dict = {'a': 'foo', 'b': 'bar', 'c': {'x': 1, 'a': 7, 'y': 'hello'}}
    result = ModelUtils.find_values_by_name(my_dict, 'a')
    assert result == ['foo', 7]
