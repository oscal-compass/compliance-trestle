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
"""Common fixtures."""
import os
from uuid import uuid4

import pytest

from trestle.oscal import target
from trestle.utils import fs

import yaml

TEST_CONFIG: dict = {}
TEST_CONFIG['yaml_testdata_path'] = 'tests/data/yaml/'
TEST_CONFIG['json_testdata_path'] = 'tests/data/json/'

TEST_DATA: dict = {}


@pytest.fixture(scope='session')
def tmp_dir():
    """Return a path for a tmp directory."""
    tmp_dir = 'tests/__tmp_dir'
    fs.ensure_directory(tmp_dir)
    return tmp_dir


@pytest.fixture(scope='function')
def tmp_file(tmp_dir):
    """Return a path for a tmp yaml file."""
    return os.path.join(tmp_dir, f'{uuid4()}')


@pytest.fixture(scope='session')
def tmp_fixed_file(tmp_dir):
    """Return a path for a tmp yaml file."""
    return os.path.join(tmp_dir, 'fixed_file')


@pytest.fixture(scope='function')
def tmp_yaml_file(tmp_dir):
    """Return a path for a tmp yaml file."""
    return os.path.join(tmp_dir, f'{uuid4()}.yaml')


@pytest.fixture(scope='function')
def tmp_json_file(tmp_dir):
    """Return a path for a tmp yaml file."""
    return os.path.join(tmp_dir, f'{uuid4()}.json')


@pytest.fixture(scope='function')
def tmp_xml_file(tmp_dir):
    """Return a path for a tmp yaml file."""
    return os.path.join(tmp_dir, f'{uuid4()}.xml')


@pytest.fixture(scope='module')
def yaml_testdata_path():
    """Return a path for a tmp directory."""
    return TEST_CONFIG['yaml_testdata_path']


@pytest.fixture(scope='module')
def json_testdata_path():
    """Return a path for a tmp directory."""
    return TEST_CONFIG['json_testdata_path']


@pytest.fixture(scope='function')
def sample_target():
    """Return a valid target object."""
    key = 'target-yaml'
    if TEST_DATA.get(key, None) is None:
        # load target yaml
        with open(os.path.join(TEST_CONFIG['yaml_testdata_path'], 'good_target.yaml'), 'r', encoding='utf8') as read_file:
            TEST_DATA[key] = yaml.load(read_file, Loader=yaml.Loader)

    yaml_data = TEST_DATA[key]
    assert yaml_data is not None

    # represent it internally as pydantic catalog model
    return target.TargetDefinition.parse_obj(yaml_data['target-definition'])
