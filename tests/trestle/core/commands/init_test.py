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
"""Tests for trestle init module."""

import os
import platform
import stat
import sys
from unittest.mock import patch

import pytest

import trestle.core.const as const
from trestle import cli


def test_init(tmp_path):
    """Test init happy path."""
    owd = os.getcwd()
    os.chdir(tmp_path)
    testargs = ['trestle', 'init']
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0
        for directory in const.MODEL_TYPE_TO_MODEL_MODULE.keys():
            assert os.path.isdir(directory)
            assert os.path.isdir(os.path.join(const.TRESTLE_DIST_DIR, directory))
            assert os.path.isfile(os.path.join(directory, const.TRESTLE_KEEP_FILE))
        assert os.path.isdir(const.TRESTLE_CONFIG_DIR)
        assert os.path.isfile(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE))
    os.chdir(owd)


def test_directory_creation_error(tmp_path):
    """Test error during init when a directory cannot be created."""
    # Windows read-only on dir does not prevent file creation in dir
    if platform.system() == 'Windows':
        return
    owd = os.getcwd()
    os.chdir(tmp_path)
    os.mkdir(const.TRESTLE_CONFIG_DIR)
    os.chmod(const.TRESTLE_CONFIG_DIR, stat.S_IREAD)
    testargs = ['trestle', 'init']
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
        for directory in const.MODEL_TYPE_TO_MODEL_MODULE.keys():
            assert os.path.isdir(directory)
            assert os.path.isdir(os.path.join(const.TRESTLE_DIST_DIR, directory))
        assert os.path.isdir(const.TRESTLE_CONFIG_DIR)
        assert not os.path.isfile(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE))
    os.chdir(owd)


def test_config_copy_error(tmp_path):
    """Test error during init when a contents of .trestle cannot be created."""
    owd = os.getcwd()
    os.chdir(tmp_path)
    os.mkdir(const.TRESTLE_CONFIG_DIR)
    open(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE), 'a').close()
    os.chmod(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE), stat.S_IREAD)
    testargs = ['trestle', 'init']
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
        for directory in const.MODEL_TYPE_TO_MODEL_MODULE.keys():
            assert os.path.isdir(directory)
            assert os.path.isdir(os.path.join(const.TRESTLE_DIST_DIR, directory))
        assert os.path.isdir(const.TRESTLE_CONFIG_DIR)
        assert os.path.isfile(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE))
        assert os.stat(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE)).st_size == 0
    os.chdir(owd)
