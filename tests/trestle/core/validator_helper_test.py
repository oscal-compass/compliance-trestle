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
"""Tests for models util module."""

import pathlib

import trestle.core.validator_helper as validator_helper
import trestle.oscal.catalog as catalog
# import trestle.oscal.ssp as ssp  # noqa: E800
import trestle.oscal.target as ostarget

import yaml

catalog_path = pathlib.Path('nist-content/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json')
ssp_path = pathlib.Path('nist-content/src/examples/ssp/json/ssp-example.json')


def test_has_no_duplicate_values_generic() -> None:
    """Test presence of duplicate uuid."""
    # test with pydantic catalog
    cat = catalog.Catalog.oscal_read(catalog_path)
    assert validator_helper.has_no_duplicate_values_generic(cat, 'uuid')

    yaml_path = pathlib.Path('tests/data/yaml')

    # test with valid pydantic target
    good_target_path = yaml_path / 'good_target.yaml'
    good_target = ostarget.TargetDefinition.oscal_read(good_target_path)
    validator_helper.find_values_by_name(good_target, 'uuid')
    assert validator_helper.has_no_duplicate_values_by_name(good_target, 'uuid')

    # test with pydantic target containing duplicates
    bad_target_path = yaml_path / 'bad_target_dup_uuid.yaml'
    bad_target = ostarget.TargetDefinition.oscal_read(bad_target_path)
    assert not validator_helper.has_no_duplicate_values_by_name(bad_target, 'uuid')

    # test duplicates with raw yaml target, non-pydantic
    read_file = bad_target_path.open('r', encoding='utf8')
    bad_target_yaml = yaml.load(read_file, Loader=yaml.Loader)
    assert not validator_helper.has_no_duplicate_values_generic(bad_target_yaml, 'uuid')


def test_has_no_duplicate_values_pydantic() -> None:
    """Test presence of duplicate values in pydantic objects."""
    # test with pydantic catalog - only one instance of Metadata
    cat = catalog.Catalog.oscal_read(catalog_path)
    assert validator_helper.has_no_duplicate_values_by_type(cat, catalog.Metadata)

    yaml_path = pathlib.Path('tests/data/yaml')

    # test presence of many duplicate properties
    good_target_path = yaml_path / 'good_target.yaml'
    good_target = ostarget.TargetDefinition.oscal_read(good_target_path)
    assert not validator_helper.has_no_duplicate_values_by_type(good_target, ostarget.Property)


def test_regenerate_uuids_ssp() -> None:
    """Test regeneration of uuids with updated refs in ssp."""
    # FIXME nist issue: https://github.com/usnistgov/oscal-content/issues/65
    # orig_ssp = ssp.SystemSecurityPlan.oscal_read(ssp_path) # noqa: E800
    # new_ssp, uuid_lut, n_refs_updated = validator_helper.regenerate_uuids(orig_ssp) # noqa: E800
    # assert len(uuid_lut.items()) == 28 # noqa: E800
    # assert n_refs_updated == 9 # noqa: E800
    pass


def test_regenerate_uuids_catalog() -> None:
    """Test regeneration of uuids with updated refs in catalog."""
    orig_cat = catalog.Catalog.oscal_read(catalog_path)
    new_cat, uuid_lut, n_refs_updated = validator_helper.regenerate_uuids(orig_cat)
    assert len(uuid_lut.items()) == 121
    assert n_refs_updated == 0


def test_find_all_attribs_by_regex() -> None:
    """Test finding attribs by regex."""
    cat = catalog.Catalog.oscal_read(catalog_path)
    attrs = validator_helper.find_all_attribs_by_regex(cat, r'party.uuid')
    assert len(attrs) == 2
