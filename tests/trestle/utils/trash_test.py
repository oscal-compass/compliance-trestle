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


def test_to_trash_dir_path(tmp_dir: pathlib.Path):
    """Test to_trash_dir_path method."""
    tmp_file: pathlib.Path = tmp_dir / 'tmp_file.md'
    tmp_file.touch()

    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    with pytest.raises(AssertionError):
        trash.to_trash_file_path(readme_file)

    test_utils.ensure_trestle_config_dir(tmp_dir)

    # trestle root will use the trash root
    assert trash.to_trash_dir_path(tmp_dir).name == pathlib.Path(trash.TRESTLE_TRASH_DIR).name
    assert trash.to_trash_dir_path(tmp_dir).parent.name == pathlib.Path(trash.TRESTLE_TRASH_DIR).parent.name

    # any directory under trestle rool will have the trash as the parent
    assert trash.to_trash_dir_path(data_dir).parent.name == pathlib.Path(trash.TRESTLE_TRASH_DIR).name


def test_to_trash_file_path(tmp_dir: pathlib.Path):
    """Test to_trash_file_path method."""
    tmp_file: pathlib.Path = tmp_dir / 'tmp_file.md'
    tmp_file.touch()

    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    with pytest.raises(AssertionError):
        trash.to_trash_file_path(readme_file)

    test_utils.ensure_trestle_config_dir(tmp_dir)

    assert trash.to_trash_file_path(tmp_file) is not None
    assert trash.to_trash_file_path(tmp_file).parent == trash.to_trash_dir_path(tmp_dir)
    assert trash.to_trash_file_path(readme_file).parent.name == f'data{trash.TRESTLE_TRASH_DIR_EXT}'


def test_to_trash_path(tmp_dir: pathlib.Path):
    """Test to trash path function."""
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    test_utils.ensure_trestle_config_dir(tmp_dir)

    assert trash.to_trash_file_path(readme_file) == trash.to_trash_path(readme_file)
    assert trash.to_trash_dir_path(readme_file.parent) == trash.to_trash_path(readme_file.parent)


def test_get_trash_root(tmp_dir: pathlib.Path):
    """Test get trash root function."""
    assert trash.get_trash_root(pathlib.Path('')) is None

    readme_file: pathlib.Path = tmp_dir / 'data/readme.md'
    assert trash.get_trash_root(readme_file) is None

    test_utils.ensure_trestle_config_dir(tmp_dir)
    trash_root = tmp_dir / trash.TRESTLE_TRASH_DIR
    fs.ensure_directory(trash_root)

    trash_file_path = trash.to_trash_file_path(readme_file)
    found_root = trash.get_trash_root(trash_file_path)
    assert trash_root.absolute() == found_root.absolute()


def test_to_origin_dir_path(tmp_dir: pathlib.Path):
    """Test to origin dir path function."""
    # invalid trestle project would error
    with pytest.raises(AssertionError):
        trash.to_origin_dir_path(tmp_dir)

    test_utils.ensure_trestle_config_dir(tmp_dir)
    trash_dir_path = trash.to_trash_dir_path(tmp_dir)

    # missing trash path would error
    with pytest.raises(AssertionError):
        trash.to_origin_dir_path(trash_dir_path)

    fs.ensure_directory(tmp_dir / trash.TRESTLE_TRASH_DIR)
    origin_dir = trash.to_origin_dir_path(trash_dir_path)
    assert tmp_dir.absolute() == origin_dir.absolute()

    data_dir = tmp_dir / 'data'
    trash_dir_path = trash.to_trash_dir_path(data_dir)
    origin_dir = trash.to_origin_dir_path(trash_dir_path)
    assert data_dir.absolute() == origin_dir.absolute()

    # invalid trash path should error
    with pytest.raises(AssertionError):
        trash.to_origin_dir_path(data_dir)

    # trash file path should error
    tmp_file = tmp_dir / 'temp_file.md'
    trash_file_path = trash.to_trash_file_path(tmp_file)
    with pytest.raises(AssertionError):
        trash.to_origin_dir_path(trash_file_path)


def test_to_origin_file_path(tmp_dir: pathlib.Path):
    """Test to origin file path function."""
    test_utils.ensure_trestle_config_dir(tmp_dir)
    fs.ensure_directory(tmp_dir / trash.TRESTLE_TRASH_DIR)

    tmp_file = tmp_dir / 'temp_file.md'
    trash_file_path = trash.to_trash_file_path(tmp_file)
    origin_file_path = trash.to_origin_file_path(trash_file_path)
    assert tmp_file.absolute() == origin_file_path.absolute()

    with pytest.raises(AssertionError):
        trash.to_origin_file_path(tmp_file)


def test_to_origin_path(tmp_dir: pathlib.Path):
    """Test to origin path function."""
    test_utils.ensure_trestle_config_dir(tmp_dir)
    fs.ensure_directory(tmp_dir / trash.TRESTLE_TRASH_DIR)

    tmp_file = tmp_dir / 'temp_file.md'
    trash_file_path = trash.to_trash_file_path(tmp_file)
    origin_file_path = trash.to_origin_path(trash_file_path)
    assert tmp_file.absolute() == origin_file_path.absolute()

    data_dir = tmp_dir / 'data'
    trash_dir_path = trash.to_trash_dir_path(data_dir)
    origin_dir = trash.to_origin_path(trash_dir_path)
    assert data_dir.absolute() == origin_dir.absolute()


def test_trash_store_file(tmp_dir: pathlib.Path):
    """Test moving file to trash."""
    test_utils.ensure_trestle_config_dir(tmp_dir)

    # trash a file
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'

    # trash with deleting original
    readme_file.touch()
    assert not trash.to_trash_file_path(readme_file).exists()
    trash.store_file(readme_file, True)
    assert readme_file.exists() is False
    assert data_dir.exists()
    assert trash.to_trash_file_path(readme_file).exists()

    # trash without deleting original
    readme_file.touch()
    trash.store_file(readme_file, False)
    assert readme_file.exists()
    assert data_dir.exists()
    assert trash.to_trash_file_path(readme_file).exists()


def test_trash_store_dir(tmp_dir: pathlib.Path):
    """Test moving whole directory to trash."""
    test_utils.ensure_trestle_config_dir(tmp_dir)

    # trash whole directory
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    # trash with deleting original
    assert not trash.to_trash_dir_path(data_dir).exists()
    assert not trash.to_trash_file_path(readme_file).exists()
    trash.store_dir(data_dir, True)
    assert data_dir.exists() is False
    assert readme_file.exists() is False
    assert trash.to_trash_dir_path(data_dir).exists()
    assert trash.to_trash_file_path(readme_file).exists()

    # trash without deleting original
    fs.ensure_directory(data_dir)
    readme_file.touch()
    trash.store_dir(data_dir, False)
    assert data_dir.exists()
    assert readme_file.exists()
    assert trash.to_trash_dir_path(data_dir).exists()
    assert trash.to_trash_file_path(readme_file).exists()


def test_trash_store(tmp_dir):
    """Test trash store function."""
    test_utils.ensure_trestle_config_dir(tmp_dir)
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    # trash using common trash method
    trash.store(readme_file, True)
    assert readme_file.exists() is False
    assert data_dir.exists()
    assert trash.to_trash_dir_path(data_dir).exists()
    assert trash.to_trash_file_path(readme_file).exists()

    # trash whole directory
    fs.ensure_directory(data_dir)
    readme_file.touch()
    trash.store(data_dir, True)
    assert data_dir.exists() is False
    assert readme_file.exists() is False
    assert trash.to_trash_dir_path(data_dir).exists()
    assert trash.to_trash_file_path(readme_file).exists()


def test_trash_recover_dir(tmp_dir):
    """Test recover trashed directory and contents."""
    test_utils.ensure_trestle_config_dir(tmp_dir)
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    trash.store_dir(data_dir, True)
    assert data_dir.exists() is False
    assert readme_file.exists() is False

    trash.recover_dir(data_dir)
    assert data_dir.exists()
    assert readme_file.exists()


def test_trash_recover_file(tmp_dir):
    """Test recover trashed file."""
    test_utils.ensure_trestle_config_dir(tmp_dir)
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    trash.store_file(readme_file, True)
    assert data_dir.exists()
    assert readme_file.exists() is False

    trash.recover_file(readme_file)
    assert data_dir.exists()
    assert readme_file.exists()


def test_trash_recover(tmp_dir):
    """Test recover trashed file or directory."""
    test_utils.ensure_trestle_config_dir(tmp_dir)
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    trash.store(readme_file, True)
    assert data_dir.exists()
    assert readme_file.exists() is False

    trash.recover(readme_file)
    assert data_dir.exists()
    assert readme_file.exists()

    trash.store(data_dir, True)
    assert data_dir.exists() is False
    assert readme_file.exists() is False

    trash.recover(data_dir)
    assert data_dir.exists()
    assert readme_file.exists()
