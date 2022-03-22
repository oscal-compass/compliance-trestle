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

from ruamel.yaml import YAML

from trestle.common import const
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
