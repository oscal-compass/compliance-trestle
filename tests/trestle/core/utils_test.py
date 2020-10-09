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

import trestle.core.utils as mutils
import trestle.oscal.catalog as catalog
import trestle.oscal.target as ostarget

import yaml


def load_good_catalog():
    """Load nist 800-53 as a catalog example."""
    good_sample_path = pathlib.Path('nist-source/content/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json')

    assert (good_sample_path.exists())
    return catalog.Catalog.oscal_read(good_sample_path)


def test_get_elements():
    """Test getting flat list of elements."""
    good_sample = load_good_catalog()

    mdlist = mutils.get_elements_of_model_type(good_sample, catalog.Metadata)
    assert (type(mdlist) == list)
    # can only be 1 metadata
    assert (len(mdlist) == 1)
    assert (type(mdlist[0]) == catalog.Metadata)

    control_list = mutils.get_elements_of_model_type(good_sample, catalog.Control)
    assert (len(control_list) >= 1)
    group_list = mutils.get_elements_of_model_type(good_sample, catalog.Group)
    assert (len(group_list) >= 2)


def test_has_no_duplicate_values_generic():
    """Test presence of duplicate uuid."""
    # test with pydantic catalog
    cat = load_good_catalog()
    assert mutils.has_no_duplicate_values_generic(cat, 'uuid')

    yaml_path = pathlib.Path('tests/data/yaml')

    # test with valid pydantic target
    good_target_path = yaml_path / 'good_target.yaml'
    good_target = ostarget.TargetDefinition.oscal_read(good_target_path)
    loe = mutils.find_values_by_name(good_target, 'uuid')
    assert len(loe) == 5
    assert mutils.has_no_duplicate_values_by_name(good_target, 'uuid')

    # test with pydantic target containing duplicates
    bad_target_path = yaml_path / 'bad_target_dup_uuid.yaml'
    bad_target = ostarget.TargetDefinition.oscal_read(bad_target_path)
    assert not mutils.has_no_duplicate_values_by_name(bad_target, 'uuid')

    # test duplicates with raw yaml target, non-pydantic
    read_file = bad_target_path.open('r', encoding='utf8')
    bad_target_yaml = yaml.load(read_file, Loader=yaml.Loader)
    assert not mutils.has_no_duplicate_values_generic(bad_target_yaml, 'uuid')


def test_has_no_duplicate_values_pydantic():
    """Test presence of duplicate values in pydantic objects."""
    # test with pydantic catalog - only one instance of Metadata
    cat = load_good_catalog()
    assert mutils.has_no_duplicate_values_by_type(cat, catalog.Metadata)

    yaml_path = pathlib.Path('tests/data/yaml')

    # test presence of many duplicate properties
    good_target_path = yaml_path / 'good_target.yaml'
    good_target = ostarget.TargetDefinition.oscal_read(good_target_path)
    assert not mutils.has_no_duplicate_values_by_type(good_target, ostarget.Prop)
