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
import pathlib
import random
import string
import sys
from unittest.mock import patch
from uuid import uuid4

import pytest

from tests import test_utils

import trestle.core.generators as gens
import trestle.oscal.common as common
from trestle.cli import Trestle
from trestle.oscal.catalog import Catalog
from trestle.oscal.component import ComponentDefinition, DefinedComponent
from trestle.oscal.profile import Profile

TEST_CONFIG: dict = {}


@pytest.fixture(scope='function')
def rand_str():
    """Return a random string."""
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    return rand_str


@pytest.fixture(scope='function')
def tmp_file(tmp_path):
    """Return a path for a tmp yaml file."""
    return pathlib.Path(tmp_path) / f'{uuid4()}'


@pytest.fixture(scope='session')
def tmp_fixed_file(tmp_path):
    """Return a path for a tmp yaml file."""
    return pathlib.Path(tmp_path) / 'fixed_file'


@pytest.fixture(scope='function')
def tmp_yaml_file(tmp_path):
    """Return a path for a tmp yaml file."""
    return pathlib.Path(tmp_path) / f'{uuid4()}.yaml'


@pytest.fixture(scope='function')
def tmp_json_file(tmp_path):
    """Return a path for a tmp yaml file."""
    return pathlib.Path(tmp_path) / f'{uuid4()}.json'


@pytest.fixture(scope='function')
def tmp_xml_file(tmp_path):
    """Return a path for a tmp yaml file."""
    return pathlib.Path(tmp_path) / f'{uuid4()}.xml'


@pytest.fixture(scope='module')
def yaml_testdata_path() -> pathlib.Path:
    """Return a path for a tmp directory."""
    return pathlib.Path(test_utils.YAML_TEST_DATA_PATH)


@pytest.fixture(scope='module')
def json_testdata_path() -> pathlib.Path:
    """Return a path for a tmp directory."""
    return pathlib.Path(test_utils.JSON_TEST_DATA_PATH)


@pytest.fixture(scope='function')
def sample_nist_component_def() -> ComponentDefinition:
    """Return a rich component definition object, from the NIST content repository."""
    component_obj = ComponentDefinition.oscal_read(test_utils.NIST_SAMPLE_CD_JSON)
    return component_obj


@pytest.fixture(scope='function')
def sample_catalog():
    """Return a valid catalog object."""
    file_path = pathlib.Path(test_utils.JSON_NIST_DATA_PATH) / test_utils.JSON_NIST_CATALOG_NAME
    catalog_obj = Catalog.oscal_read(file_path)
    return catalog_obj


@pytest.fixture(scope='function')
def sample_profile():
    """Return a valid profile object."""
    file_path = pathlib.Path(test_utils.JSON_NIST_DATA_PATH) / test_utils.JSON_NIST_PROFILE_NAME
    profile_obj = Profile.oscal_read(file_path)
    return profile_obj


@pytest.fixture(scope='function')
def sample_catalog_minimal():
    """Return a valid catalog object with minimum fields necessary."""
    file_path = pathlib.Path(test_utils.JSON_TEST_DATA_PATH) / 'minimal_catalog.json'
    catalog_obj = Catalog.oscal_read(file_path)
    return catalog_obj


@pytest.fixture(scope='function')
def sample_catalog_missing_roles():
    """Return a catalog object missing roles."""
    file_path = pathlib.Path(test_utils.JSON_TEST_DATA_PATH) / 'minimal_catalog_missing_roles.json'
    catalog_obj = Catalog.oscal_read(file_path)
    return catalog_obj


@pytest.fixture(scope='function')
def sample_component_definition():
    """Return a valid ComponentDefinition object with some contents."""
    # one component has no properties - the other has two
    def_comp1: DefinedComponent = gens.generate_sample_model(DefinedComponent)
    def_comp2: DefinedComponent = gens.generate_sample_model(DefinedComponent)
    prop_1 = gens.generate_sample_model(common.Property)
    prop_2 = gens.generate_sample_model(common.Property)
    def_comp2.props = [prop_1, prop_2]
    comp_def: ComponentDefinition = gens.generate_sample_model(ComponentDefinition)
    comp_def.components = [def_comp1, def_comp2]
    return comp_def


@pytest.fixture(scope='function')
def tmp_trestle_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    """Create and return a new trestle project directory using std tmp_path fixture.

    Note that this fixture relies on the 'trestle init' command and therefore may
    misbehave if there are errors in trestle init.
    """
    pytest_cwd = pathlib.Path.cwd()
    os.chdir(tmp_path)
    testargs = ['trestle', 'init']
    with patch.object(sys, 'argv', testargs):
        # FIXME: Correctly capture return codes
        Trestle().run()
    yield tmp_path

    os.chdir(pytest_cwd)


@pytest.fixture(scope='function')
def tmp_empty_cwd(tmp_path: pathlib.Path) -> pathlib.Path:
    """Create a temporary directory and cd into that directory with fail out afterwards.

    The purpose of this is to provide a clean directory per unit test and ensure we get
    back to the base time.
    """
    pytest_cwd = pathlib.Path.cwd()
    os.chdir(tmp_path)

    yield tmp_path

    os.chdir(pytest_cwd)


@pytest.fixture(scope='function')
def testdata_dir() -> pathlib.Path:
    """Return absolute path to test data directory."""
    test_data_source = pathlib.Path('tests/data')
    return test_data_source.resolve()


@pytest.fixture(scope='function')
def keep_cwd() -> pathlib.Path:
    """Force test to return to orig directory if chdir's happen in test."""
    old_cwd = os.getcwd()
    yield old_cwd
    os.chdir(old_cwd)
