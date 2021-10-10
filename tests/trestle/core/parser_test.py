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
"""Tests for models module."""

import pathlib

import pytest

from ruamel.yaml import YAML

from trestle.core import const
from trestle.core import parser

yaml_path = pathlib.Path('tests/data/yaml/')


def test_parse_dict() -> None:
    """Test parse_dict."""
    file_name = 'good_component.yaml'

    with open(pathlib.Path.joinpath(yaml_path, file_name), 'r', encoding=const.FILE_ENCODING) as f:
        yaml = YAML(typ='safe')
        data = yaml.load(f)
        target = parser.parse_dict(data['component-definition'], 'trestle.oscal.component.ComponentDefinition')
        assert target is not None


def test_to_full_model_name() -> None:
    """Test to_full_model_name."""
    tests = [
        {
            'root_key': 'catalog',
            'expected': f'{const.PACKAGE_OSCAL}.catalog.Catalog',
        }, {
            'root_key': 'component-definition',
            'expected': f'{const.PACKAGE_OSCAL}.component.ComponentDefinition',
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


@pytest.mark.parametrize(
    'model_name, expected',
    [(f'{const.PACKAGE_OSCAL}.component.ComponentDefinition', 'ComponentDefinition'), (None, 'ComponentDefinition')]
)
def test_parse_file(model_name: str, expected: str) -> None:
    """Test parse_file."""
    file_name = 'good_component.yaml'
    component_obj = parser.parse_file(yaml_path / file_name, model_name=test_to_full_model_name())
    assert type(component_obj).__name__ == expected
