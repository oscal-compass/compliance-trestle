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
"""Tests for models module."""

import pathlib
from datetime import datetime
from uuid import uuid4

from trestle.core import const
from trestle.core import parser
from trestle.oscal import catalog
from trestle.oscal import target

import yaml

yaml_path = pathlib.Path('tests/data/yaml/')
encoding = 'utf8'


def test_parse_dict():
    """Test parse_dict."""
    file_name = 'good_target.yaml'

    with open(pathlib.Path.joinpath(yaml_path, file_name), 'r', encoding=encoding) as f:
        data = yaml.load(f, yaml.FullLoader)
        target = parser.parse_dict(data['target-definition'], 'trestle.oscal.target.TargetDefinition')
        assert target is not None


def test_to_class_name():
    """Test to_class_name."""
    tests = [
        {
            'name': 'catalog',
            'expected': 'Catalog',
        },
        {
            'name': 'target-definition',
            'expected': 'TargetDefinition',
        },
    ]

    for test in tests:
        assert parser.to_class_name(test['name']) == test['expected']


def test_to_full_model_name():
    """Test to_full_model_name."""
    tests = [
        {
            'root_key': 'catalog',
            'name': None,
            'expected': f'{const.PACKAGE_OSCAL}.catalog.Catalog',
        }, {
            'root_key': 'catalog',
            'name': 'group',
            'expected': f'{const.PACKAGE_OSCAL}.catalog.Group',
        }, {
            'root_key': 'target-definition',
            'name': None,
            'expected': f'{const.PACKAGE_OSCAL}.target.TargetDefinition',
        },
        {
            'root_key': 'target',
            'name': 'target-definition',
            'expected': f'{const.PACKAGE_OSCAL}.target.TargetDefinition',
        }, {
            'root_key': 'invalid',
            'name': None,
            'expected': None,
        }
    ]

    for test in tests:
        model_name = parser.to_full_model_name(test['root_key'], test['name'])
        assert model_name == test['expected']


def test_parse_file():
    """Test parse_file."""
    file_name = 'good_target.yaml'

    tests = [
        {
            'model_name': f'{const.PACKAGE_OSCAL}.target.TargetDefinition', 'expected': 'TargetDefinition'
        }, {
            'model_name': None, 'expected': 'TargetDefinition'
        }
    ]

    for test in tests:
        target = parser.parse_file(pathlib.Path.joinpath(yaml_path, file_name), model_name=test['model_name'])

        assert type(target).__name__ == test['expected']


def test_class_to_oscal_json():
    """Pydantic makes classes in PascalCase. All Oscal names are in lowercase-hyphenated."""
    class_name_1 = 'Catalog'
    oscal_name_1 = 'catalog'
    class_name_2 = 'ComponentDefinition'
    oscal_name_2 = 'component-definition'
    class_name_3 = 'SecurityImpactLevel'
    oscal_name_3 = 'security-impact-level'

    assert (oscal_name_1 == parser.class_to_oscal(class_name_1, 'json'))
    assert (oscal_name_2 == parser.class_to_oscal(class_name_2, 'json'))
    assert (oscal_name_3 == parser.class_to_oscal(class_name_3, 'json'))


def test_class_to_oscal_field():
    """Pydantic makes classes in PascalCase. All Oscal names are in lowercase-hyphenated."""
    class_name_1 = 'Catalog'
    oscal_name_1 = 'catalog'
    class_name_2 = 'ComponentDefinition'
    oscal_name_2 = 'component_definition'
    class_name_3 = 'SecurityImpactLevel'
    oscal_name_3 = 'security_impact_level'

    assert (oscal_name_1 == parser.class_to_oscal(class_name_1, 'field'))
    assert (oscal_name_2 == parser.class_to_oscal(class_name_2, 'field'))
    assert (oscal_name_3 == parser.class_to_oscal(class_name_3, 'field'))


def test_wrap_for_output():
    """Test that an output object is wrapped and contains the appropriate content."""
    m = catalog.Metadata(
        **{
            'title': 'my cool catalog', 'last-modified': datetime.now(), 'version': '0.0.1', 'oscal-version': '1.0.0'
        }
    )

    c = catalog.Catalog(metadata=m, uuid=str(uuid4()))

    wrapped = parser.wrap_for_output(c)
    assert (wrapped.catalog.metadata.title == c.metadata.title)

    # Test with target definition
    t_m = target.Metadata(
        **{
            'title': 'my cool target definition',
            'last-modified': datetime.now(),
            'version': '0.0.1',
            'oscal-version': '1.0.0'
        }
    )

    t = target.TargetDefinition(metadata=t_m)
    wrapped = parser.wrap_for_output(t)
    assert (wrapped.target_definition.metadata.title == t.metadata.title)


def test_wrap_for_input():
    """Test input for object that has a hyphen it it's name."""
    json_path = pathlib.Path('tests/data/json/sample-target-definition.json')
    parser.wrap_for_input(target.TargetDefinition).parse_file(json_path).target_definition


def test_pascal_case_split():
    """Test whether PascalCase objects are getting split correctly."""
    one = 'One'
    two = 'TwoTwo'
    three = 'ThreeThreeThree'
    assert (len(parser.pascal_case_split(one)) == 1)
    assert (len(parser.pascal_case_split(two)) == 2)
    assert (len(parser.pascal_case_split(three)) == 3)
    # TODO: Add negative test cases.
