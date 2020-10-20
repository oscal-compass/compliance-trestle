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
"""Tests for trestle trash module."""

import pathlib

import pytest

from tests import test_utils

from trestle.utils import fs, trash


def test_get_trash_dir_path(tmp_dir):
    """Test get_trash_dir_path method."""
    tmp_file: pathlib.Path = tmp_dir / 'tmp_file.md'
    tmp_file.touch()

    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    with pytest.raises(AssertionError):
        trash.get_trash_file_path(readme_file)

    test_utils.ensure_trestle_config_dir(tmp_dir)

    # trestle root will use the trash root
    assert trash.get_trash_dir_path(tmp_dir).name == pathlib.Path(trash.TRESTLE_TRASH_DIR).name
    assert trash.get_trash_dir_path(tmp_dir).parent.name == pathlib.Path(trash.TRESTLE_TRASH_DIR).parent.name

    # any directory under trestle rool will have the trash as the parent
    assert trash.get_trash_dir_path(data_dir).parent.name == pathlib.Path(trash.TRESTLE_TRASH_DIR).name


def test_get_trash_file_path(tmp_dir):
    """Test get_trash_file_path method."""
    tmp_file: pathlib.Path = tmp_dir / 'tmp_file.md'
    tmp_file.touch()

    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    with pytest.raises(AssertionError):
        trash.get_trash_file_path(readme_file)

    test_utils.ensure_trestle_config_dir(tmp_dir)

    assert trash.get_trash_file_path(tmp_file) is not None
    assert trash.get_trash_file_path(tmp_file).parent == trash.get_trash_dir_path(tmp_dir)
    assert trash.get_trash_file_path(readme_file).parent.name == f'data{trash.TRESTLE_TRASH_EXT}'


def test_move_file_to_trash(tmp_dir):
    """Test moving file to trash."""
    test_utils.ensure_trestle_config_dir(tmp_dir)

    # trash a file
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    assert not trash.get_trash_file_path(readme_file).exists()
    trash.move_file_to_trash(readme_file, True)
    assert readme_file.exists() is False
    assert data_dir.exists()
    assert trash.get_trash_file_path(readme_file).exists()

    # trash using common tash method
    readme_file.touch()
    trash.move_to_trash(readme_file, True)
    assert readme_file.exists() is False
    assert data_dir.exists()
    assert trash.get_trash_dir_path(data_dir).exists()
    assert trash.get_trash_file_path(readme_file).exists()


def test_move_dir_to_trash(tmp_dir):
    """Test moving whole directory to trash."""
    test_utils.ensure_trestle_config_dir(tmp_dir)

    # trash whole directory
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    assert not trash.get_trash_dir_path(data_dir).exists()
    assert not trash.get_trash_file_path(readme_file).exists()
    trash.move_dir_to_trash(data_dir, True)
    assert data_dir.exists() is False
    assert readme_file.exists() is False
    assert trash.get_trash_dir_path(data_dir).exists()
    assert trash.get_trash_file_path(readme_file).exists()

    # trash whole directory
    fs.ensure_directory(data_dir)
    readme_file.touch()
    trash.move_to_trash(data_dir, True)
    assert data_dir.exists() is False
    assert readme_file.exists() is False
    assert trash.get_trash_dir_path(data_dir).exists()
    assert trash.get_trash_file_path(readme_file).exists()
