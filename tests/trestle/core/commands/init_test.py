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
import stat

from _pytest.monkeypatch import MonkeyPatch

from tests.test_utils import execute_command_and_assert

import trestle.common.const as const
from trestle.common import file_utils


def test_init(tmp_path: pathlib.Path, keep_cwd: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test init happy path and no flags."""
    os.chdir(tmp_path)
    command = 'trestle init -v'
    execute_command_and_assert(command, 0, monkeypatch)

    for directory in const.MODEL_DIR_LIST:
        assert os.path.isdir(directory)
        assert os.path.isdir(os.path.join(const.TRESTLE_DIST_DIR, directory))
        assert os.path.isfile(os.path.join(directory, const.TRESTLE_KEEP_FILE))
    assert os.path.isdir(const.TRESTLE_CONFIG_DIR)
    assert os.path.isfile(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE))


def test_directory_creation_error(tmp_path: pathlib.Path, keep_cwd: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test error during init when a directory cannot be created."""
    # Windows read-only on dir does not prevent file creation in dir
    if file_utils.is_windows():
        return
    os.chdir(tmp_path)
    config_dir = pathlib.Path(const.TRESTLE_CONFIG_DIR)
    config_dir.mkdir()
    config_dir.chmod(stat.S_IREAD)
    config_file = config_dir / const.TRESTLE_CONFIG_FILE

    command = 'trestle init -v'
    execute_command_and_assert(command, 1, monkeypatch)

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


def test_config_copy_error(tmp_path: pathlib.Path, keep_cwd: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test error during init when a contents of .trestle cannot be created."""
    os.chdir(tmp_path)
    config_dir = pathlib.Path(const.TRESTLE_CONFIG_DIR)
    config_dir.mkdir()
    config_file = config_dir / const.TRESTLE_CONFIG_FILE
    config_file.touch()
    config_file.chmod(stat.S_IREAD)

    command = 'trestle init'
    execute_command_and_assert(command, 1, monkeypatch)

    for directory in const.MODEL_DIR_LIST:
        assert os.path.isdir(directory)
        assert os.path.isdir(os.path.join(const.TRESTLE_DIST_DIR, directory))
    assert os.path.isdir(const.TRESTLE_CONFIG_DIR)
    assert os.path.isfile(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE))
    assert os.stat(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE)).st_size == 0


def test_init_local(tmp_path: pathlib.Path, keep_cwd: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test init for local usage only."""
    os.chdir(tmp_path)
    command = 'trestle init --local'
    execute_command_and_assert(command, 0, monkeypatch)

    for directory in const.MODEL_DIR_LIST:
        assert os.path.isdir(directory)
        assert not os.path.isdir(os.path.join(const.TRESTLE_DIST_DIR, directory))
        assert os.path.isfile(os.path.join(directory, const.TRESTLE_KEEP_FILE))
    assert os.path.isdir(const.TRESTLE_CONFIG_DIR)
    assert os.path.isfile(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE))


def test_init_govdocs(tmp_path: pathlib.Path, keep_cwd: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test init for governed document usage only."""
    os.chdir(tmp_path)
    command = 'trestle init --govdocs'
    execute_command_and_assert(command, 0, monkeypatch)

    for directory in const.MODEL_DIR_LIST:
        assert not os.path.isdir(directory)
        assert not os.path.isdir(os.path.join(const.TRESTLE_DIST_DIR, directory))
        assert not os.path.isfile(os.path.join(directory, const.TRESTLE_KEEP_FILE))
    assert os.path.isdir(const.TRESTLE_CONFIG_DIR)
    assert not os.path.isfile(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE))


def test_init_full(tmp_path: pathlib.Path, keep_cwd: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test init for full usage only."""
    os.chdir(tmp_path)
    command = 'trestle init --full'
    execute_command_and_assert(command, 0, monkeypatch)

    for directory in const.MODEL_DIR_LIST:
        assert os.path.isdir(directory)
        assert os.path.isdir(os.path.join(const.TRESTLE_DIST_DIR, directory))
        assert os.path.isfile(os.path.join(directory, const.TRESTLE_KEEP_FILE))
    assert os.path.isdir(const.TRESTLE_CONFIG_DIR)
    assert os.path.isfile(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE))


def test_init_govdocs_n_local(tmp_path: pathlib.Path, keep_cwd: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test init with multiple flags behave like mode of the highest hierarchy."""
    os.chdir(tmp_path)
    command = 'trestle init --govdocs --local'
    execute_command_and_assert(command, 0, monkeypatch)

    for directory in const.MODEL_DIR_LIST:
        assert os.path.isdir(directory)
        assert not os.path.isdir(os.path.join(const.TRESTLE_DIST_DIR, directory))
        assert os.path.isfile(os.path.join(directory, const.TRESTLE_KEEP_FILE))
    assert os.path.isdir(const.TRESTLE_CONFIG_DIR)
    assert os.path.isfile(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE))


def test_init_govdocs_n_full(tmp_path: pathlib.Path, keep_cwd: pathlib.Path, monkeypatch: MonkeyPatch):
    """Test init with multiple flags behave like mode of the highest hierarchy."""
    os.chdir(tmp_path)
    command = 'trestle init --govdocs --full'
    execute_command_and_assert(command, 0, monkeypatch)

    for directory in const.MODEL_DIR_LIST:
        assert os.path.isdir(directory)
        assert os.path.isdir(os.path.join(const.TRESTLE_DIST_DIR, directory))
        assert os.path.isfile(os.path.join(directory, const.TRESTLE_KEEP_FILE))
    assert os.path.isdir(const.TRESTLE_CONFIG_DIR)
    assert os.path.isfile(os.path.join(const.TRESTLE_CONFIG_DIR, const.TRESTLE_CONFIG_FILE))
