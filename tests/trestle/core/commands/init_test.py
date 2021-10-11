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
"""Tests for trestle init module."""

import os
import pathlib
import platform
import stat
import sys

from _pytest.monkeypatch import MonkeyPatch

import pytest

import trestle.core.const as const
from trestle import cli


def test_init(tmp_path, keep_cwd, monkeypatch: MonkeyPatch):
    """Test init happy path."""
    os.chdir(tmp_path)
    testargs = ['trestle', 'init']
    monkeypatch.setattr(sys, 'argv', testargs)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.run()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    for directory in const.MODEL_DIR_LIST:
        assert os.path.isdir(directory)
        assert os.path.isdir(os.path.join(const.TRESTLE_DIST_DIR, directory))
        assert os.path.isfile(os.path.join(directory, const.TRESTLE_KEEP_FILE))
    assert os.path.isdir(const.TRESTLE_CONFIG_DIR)
    assert os.path.isfile(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE))


def test_directory_creation_error(tmp_path, keep_cwd, monkeypatch: MonkeyPatch):
    """Test error during init when a directory cannot be created."""
    # Windows read-only on dir does not prevent file creation in dir
    if platform.system() == const.WINDOWS_PLATFORM_STR:
        return
    os.chdir(tmp_path)
    config_dir = pathlib.Path(const.TRESTLE_CONFIG_DIR)
    config_dir.mkdir()
    config_dir.chmod(stat.S_IREAD)
    config_file = config_dir / const.TRESTLE_CONFIG_FILE
    testargs = ['trestle', 'init']
    monkeypatch.setattr(sys, 'argv', testargs)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.run()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    for directory in const.MODEL_DIR_LIST:
        dir_path = pathlib.Path(directory)
        assert not dir_path.exists()
        dist_dir_path = pathlib.Path(const.TRESTLE_DIST_DIR) / directory
        assert not dist_dir_path.exists()
    assert config_dir.exists()
    assert config_dir.is_dir()
    config_exists = False
    try:
        config_exists = config_file.exists()
    except Exception:
        pass
    assert not config_exists


def test_config_copy_error(tmp_path, keep_cwd, monkeypatch: MonkeyPatch):
    """Test error during init when a contents of .trestle cannot be created."""
    os.chdir(tmp_path)
    config_dir = pathlib.Path(const.TRESTLE_CONFIG_DIR)
    config_dir.mkdir()
    config_file = config_dir / const.TRESTLE_CONFIG_FILE
    config_file.touch()
    config_file.chmod(stat.S_IREAD)
    testargs = ['trestle', 'init']
    monkeypatch.setattr(sys, 'argv', testargs)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.run()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    for directory in const.MODEL_DIR_LIST:
        assert os.path.isdir(directory)
        assert os.path.isdir(os.path.join(const.TRESTLE_DIST_DIR, directory))
    assert os.path.isdir(const.TRESTLE_CONFIG_DIR)
    assert os.path.isfile(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE))
    assert os.stat(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE)).st_size == 0
