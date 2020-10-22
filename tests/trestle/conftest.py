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
import pathlib
import random
import string
from uuid import uuid4

import pytest

from tests import test_utils

from trestle.oscal.catalog import Catalog
from trestle.oscal.target import TargetDefinition
from trestle.utils import fs

TEST_CONFIG: dict = {}


@pytest.fixture(scope='function')
def rand_str():
    """Return a random string."""
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    return rand_str


@pytest.fixture(scope='function')
def tmp_dir(rand_str) -> pathlib.Path:
    """Return a path for a tmp directory."""
    tmp_dir = pathlib.Path.joinpath(test_utils.BASE_TMP_DIR, rand_str)
    assert tmp_dir.parent == test_utils.BASE_TMP_DIR
    fs.ensure_directory(tmp_dir)
    yield tmp_dir

    # tear down
    test_utils.clean_tmp_dir(tmp_dir)


@pytest.fixture(scope='function')
def tmp_file(tmp_dir):
    """Return a path for a tmp yaml file."""
    return pathlib.Path.joinpath(tmp_dir, f'{uuid4()}')


@pytest.fixture(scope='session')
def tmp_fixed_file(tmp_dir):
    """Return a path for a tmp yaml file."""
    return pathlib.Path.joinpath(tmp_dir, 'fixed_file')


@pytest.fixture(scope='function')
def tmp_yaml_file(tmp_dir):
    """Return a path for a tmp yaml file."""
    return pathlib.Path.joinpath(tmp_dir, f'{uuid4()}.yaml')


@pytest.fixture(scope='function')
def tmp_json_file(tmp_dir):
    """Return a path for a tmp yaml file."""
    return pathlib.Path.joinpath(tmp_dir, f'{uuid4()}.json')


@pytest.fixture(scope='function')
def tmp_xml_file(tmp_dir):
    """Return a path for a tmp yaml file."""
    return pathlib.Path.joinpath(tmp_dir, f'{uuid4()}.xml')


@pytest.fixture(scope='module')
def yaml_testdata_path() -> pathlib.Path:
    """Return a path for a tmp directory."""
    return test_utils.YAML_TEST_DATA_PATH


@pytest.fixture(scope='module')
def json_testdata_path() -> pathlib.Path:
    """Return a path for a tmp directory."""
    return test_utils.JSON_TEST_DATA_PATH


@pytest.fixture(scope='function')
def sample_target_def():
    """Return a valid target definition object."""
    file_path = pathlib.Path.joinpath(test_utils.YAML_TEST_DATA_PATH, 'good_target.yaml')
    target_obj = TargetDefinition.oscal_read(file_path)
    return target_obj


@pytest.fixture(scope='function')
def sample_catalog():
    """Return a valid catalog object."""
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'good_catalog.json')
    catalog_obj = Catalog.oscal_read(file_path)
    return catalog_obj


@pytest.fixture(scope='function')
def sample_catalog_minimal():
    """Return a valid catalog object with minimum fields necessary."""
    file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'minimal_catalog.json')
    catalog_obj = Catalog.oscal_read(file_path)
    return catalog_obj
