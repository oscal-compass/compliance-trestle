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
"""Testing of core settings module."""

import json
import os
import pathlib
from uuid import uuid4

import pytest
from tests import test_utils

# import trestle.core.err as err
from trestle.core.settings import Settings


def test_settings_class():
    """Test as a class variable."""
    env_file_path = pathlib.Path(test_utils.ENV_TEST_DATA_PATH / 'good_env_bad_token').absolute()
    assert (env_file_path.is_file())

    settings = Settings(_env_file=env_file_path)
    # file_path = pathlib.Path.joinpath(test_utils.ENV_TEST_DATA_PATH, 'minimal_catalog_roles.json')
    # stripped_catalog_object = oscatalog.Catalog.create_stripped_model_type(['metadata'])
    # if 'metadata' in stripped_catalog_object.__fields__.keys():
    #     raise Exception('Test failure')

    # if 'controls' not in stripped_catalog_object.__fields__.keys():
    #     raise Exception('Test failure')

    # # Create instance.
    # sc_instance = stripped_catalog_object(uuid=str(uuid4()))
    # if 'metadata' in sc_instance.__fields__.keys():
    #     raise Exception('Test failure')
    pass


def test_settings_env_file():
    """Test ability to read .env file."""
    env_file_path = pathlib.Path(test_utils.ENV_TEST_DATA_PATH / 'good_env_bad_token').absolute()
    assert (env_file_path.is_file())

    settings = Settings(_env_file=env_file_path)
    assert (len(settings.GITHUB_TOKENS) == 1)


def test_settings_env_variable():
    """Test ability to override .env file settings with environment variable."""
    env_file_path = pathlib.Path(test_utils.ENV_TEST_DATA_PATH / 'good_env_bad_token').absolute()
    assert (env_file_path.is_file())

    token = str(uuid4())
    os.environ["TRESTLE_GITHUB_TOKENS"] = f'{{ "github.com": "{token}" }}'
    settings = Settings(_env_file=env_file_path)
    assert (settings.GITHUB_TOKENS["github.com"] == token)
