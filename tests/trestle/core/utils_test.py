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


def test_pascal_case_split():
    """Test whether PascalCase objects are getting split correctly."""
    one = 'One'
    two = 'TwoTwo'
    three = 'ThreeThreeThree'
    assert (len(mutils.pascal_case_split(one)) == 1)
    assert (len(mutils.pascal_case_split(two)) == 2)
    assert (len(mutils.pascal_case_split(three)) == 3)
    # TODO: Add negative test cases.


def test_class_to_oscal_json():
    """Pydantic makes classes in PascalCase. All Oscal names are in lowercase-hyphenated."""
    class_name_1 = 'Catalog'
    oscal_name_1 = 'catalog'
    class_name_2 = 'ComponentDefinition'
    oscal_name_2 = 'component-definition'
    class_name_3 = 'SecurityImpactLevel'
    oscal_name_3 = 'security-impact-level'

    assert (oscal_name_1 == mutils.class_to_oscal(class_name_1, 'json'))
    assert (oscal_name_2 == mutils.class_to_oscal(class_name_2, 'json'))
    assert (oscal_name_3 == mutils.class_to_oscal(class_name_3, 'json'))


def test_class_to_oscal_field():
    """Pydantic makes classes in PascalCase. All Oscal names are in lowercase-hyphenated."""
    class_name_1 = 'Catalog'
    oscal_name_1 = 'catalog'
    class_name_2 = 'ComponentDefinition'
    oscal_name_2 = 'component_definition'
    class_name_3 = 'SecurityImpactLevel'
    oscal_name_3 = 'security_impact_level'

    assert (oscal_name_1 == mutils.class_to_oscal(class_name_1, 'field'))
    assert (oscal_name_2 == mutils.class_to_oscal(class_name_2, 'field'))
    assert (oscal_name_3 == mutils.class_to_oscal(class_name_3, 'field'))
