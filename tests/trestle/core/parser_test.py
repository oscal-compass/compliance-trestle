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

from trestle.core import const
from trestle.core import parser

import yaml

yaml_path = pathlib.Path('tests/data/yaml/')
encoding = 'utf8'


def test_parse_dict() -> None:
    """Test parse_dict."""
    file_name = 'good_target.yaml'

    with open(pathlib.Path.joinpath(yaml_path, file_name), 'r', encoding=encoding) as f:
        data = yaml.load(f, yaml.FullLoader)
        target = parser.parse_dict(data['target-definition'], 'trestle.oscal.target.TargetDefinition')
        assert target is not None


def test_to_class_name() -> None:
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


def test_to_full_model_name() -> None:
    """Test to_full_model_name."""
    tests = [
        {
            'root_key': 'catalog',
            'expected': f'{const.PACKAGE_OSCAL}.catalog.Catalog',
        }, {
            'root_key': 'target-definition',
            'expected': f'{const.PACKAGE_OSCAL}.target.TargetDefinition',
        }, {
            'root_key': 'system-security-plan',
            'expected': f'{const.PACKAGE_OSCAL}.ssp.SystemSecurityPlan',
        }, {
            'root_key': 'invalid',
            'expected': None,
        }
    ]

    for test in tests:
        model_name = parser.to_full_model_name(test['root_key'])
        assert model_name == test['expected']


def test_parse_file() -> None:
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
