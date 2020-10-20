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


def test_get_trash_file_path(tmp_dir):
    """Test get_trash_file_path method."""
    tmp_file = tmp_dir / 'tmp_file.md'
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    with pytest.raises(AssertionError):
        trash.get_trash_file_path(readme_file)

    test_utils.ensure_trestle_config_dir(tmp_dir)

    assert trash.get_trash_file_path(tmp_file) is not None
    assert trash.get_trash_file_path(tmp_file).parent.name == pathlib.Path(trash.TRESTLE_TRASH_DIR).name
    assert trash.get_trash_file_path(readme_file).parent.name == 'data'


def test_move_to_trash(tmp_dir):
    """Test move_to_trash command."""
    test_utils.ensure_trestle_config_dir(tmp_dir)
    data_dir: pathlib.Path = tmp_dir / 'data'
    fs.ensure_directory(data_dir)
    readme_file: pathlib.Path = data_dir / 'readme.md'
    readme_file.touch()

    assert not trash.get_trash_file_path(readme_file).exists()
    trash.move_to_trash(readme_file)
    assert readme_file.exists() is False
    assert trash.get_trash_file_path(readme_file).exists()
