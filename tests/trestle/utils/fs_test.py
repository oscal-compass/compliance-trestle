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
"""Tests for fs module."""

from os import PathLike
import os
import pathlib
from pathlib import Path
from trestle.core.err import TrestleError

import pytest

from tests import test_utils

from trestle.core import const
from trestle.utils import fs


def ensure_trestle_config_dir(sub_dir: pathlib.Path):
    """Ensure that the sub_dir has trestle config dir."""
    trestle_dir = pathlib.Path.joinpath(sub_dir, const.TRESTLE_CONFIG_DIR)
    fs.ensure_directory(trestle_dir)


def test_ensure_directory(tmpdir):
    """Test ensure_directory function."""
    # Happy path
    fs.ensure_directory(tmpdir)

    # Unhappy path
    with pytest.raises(AssertionError):
        fs.ensure_directory(__file__)


def test_should_ignore():
    """Test should_ignore method."""
    assert fs.should_ignore('.test') is True
    assert fs.should_ignore('_test') is True
    assert fs.should_ignore('__test') is True
    assert fs.should_ignore('test') is False


def test_is_valid_project_root(tmp_dir):
    """Test is_valid_project_root method."""
    assert fs.is_valid_project_root(None) is False
    assert fs.is_valid_project_root('') is False
    assert fs.is_valid_project_root(tmp_dir) is False

    ensure_trestle_config_dir(tmp_dir)
    assert fs.is_valid_project_root(tmp_dir) is True


def test_has_parent_path(tmp_dir):
    """Test has_parent_path method."""
    assert fs.has_parent_path(tmp_dir, pathlib.Path('')) is False
    assert fs.has_parent_path(tmp_dir, None) is False
    assert fs.has_parent_path(pathlib.Path('tests'), test_utils.BASE_TMP_DIR) is False
    assert fs.has_parent_path(pathlib.Path('/invalid/path'), test_utils.BASE_TMP_DIR) is False

    assert fs.has_parent_path(tmp_dir, test_utils.BASE_TMP_DIR) is True


def test_has_trestle_project_in_path(tmp_dir, rand_str):
    """Test has_trestle_project_in_path method."""
    project_path: pathlib.Path = pathlib.Path.joinpath(tmp_dir, rand_str)
    sub_path: pathlib.Path = project_path.joinpath('samples2')
    fs.ensure_directory(sub_path)
    assert sub_path.exists() and sub_path.is_dir()

    # create a file
    with open(sub_path.joinpath('readme.md'), 'w+'):
        pass

    # create a data-dir and a file
    sub_data_dir = pathlib.Path.joinpath(sub_path, 'data')
    fs.ensure_directory(sub_data_dir)
    with open(sub_data_dir.joinpath('readme.md'), 'w+'):
        pass

    assert fs.has_trestle_project_in_path(sub_data_dir) is False

    ensure_trestle_config_dir(project_path)
    assert fs.has_trestle_project_in_path(sub_data_dir) is True
    assert fs.has_trestle_project_in_path(sub_data_dir.joinpath('readme.md')) is True
    assert fs.has_trestle_project_in_path(sub_path.joinpath('readme.md')) is True
    assert fs.has_trestle_project_in_path(sub_path) is True
    assert fs.has_trestle_project_in_path(tmp_dir) is False


def test_clean_project_sub_path(tmp_dir, rand_str):
    """Test clean_project_sub_path method."""
    project_path: pathlib.Path = pathlib.Path.joinpath(tmp_dir, rand_str)
    sub_path: pathlib.Path = project_path.joinpath('samples')
    fs.ensure_directory(sub_path)
    assert sub_path.exists() and sub_path.is_dir()

    # create a file
    with open(pathlib.Path.joinpath(sub_path, 'readme.md'), 'w+'):
        pass

    # create a data-dir and a file
    sub_data_dir = pathlib.Path.joinpath(sub_path, 'data')
    sub_data_dir_file = sub_data_dir.joinpath('readme.md')
    fs.ensure_directory(sub_data_dir)
    with open(sub_data_dir_file, 'w+'):
        pass

    try:
        # not having .trestle directory at the project root or tmp_dir should fail
        fs.clean_project_sub_path(sub_path)
    except TrestleError:
        pass

    ensure_trestle_config_dir(project_path)

    fs.clean_project_sub_path(sub_data_dir_file)
    assert not sub_data_dir_file.exists()

    # create the file again
    with open(sub_data_dir_file, 'w+'):
        pass

    # clean the sub_path in the trestle project
    fs.clean_project_sub_path(sub_path)
    assert not sub_path.exists()


def test_load_file(tmp_dir):
    """Test load file."""
    json_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH, 'sample-target-definition.json')
    yaml_file_path = pathlib.Path.joinpath(test_utils.YAML_TEST_DATA_PATH, 'good_target.yaml')

    assert fs.load_file(json_file_path) is not None
    assert fs.load_file(yaml_file_path) is not None

    try:
        sample_file_path = tmp_dir.joinpath('sample.txt')
        with open(sample_file_path, 'w'):
            fs.load_file(sample_file_path)
    except TrestleError:
        pass
