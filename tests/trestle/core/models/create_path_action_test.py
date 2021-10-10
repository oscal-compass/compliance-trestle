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
"""Tests for trestle create path actions class."""

import pathlib

import pytest

from tests import test_utils

import trestle.core.const as const
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction


def test_create_path_execute(tmp_path: pathlib.Path):
    """Test create path execute."""
    tmp_data_dir = tmp_path.joinpath('data')

    with pytest.raises(TrestleError):
        # no trestle project should error
        cpa = CreatePathAction(tmp_data_dir)

    test_utils.ensure_trestle_config_dir(tmp_path)

    # create directories
    cpa = CreatePathAction(tmp_data_dir)

    assert tmp_data_dir.exists() is False
    cpa.execute()
    assert len(cpa.get_created_paths()) == 1
    assert tmp_data_dir.exists()

    cpa.rollback()
    assert tmp_data_dir.exists() is False

    # create directories and a file
    tmp_data_dir_file = tmp_data_dir.joinpath('readme.md')
    cpa = CreatePathAction(tmp_data_dir_file)
    assert cpa.get_trestle_project_root() == tmp_path

    assert tmp_data_dir.exists() is False
    assert tmp_data_dir_file.exists() is False
    cpa.execute()
    assert len(cpa.get_created_paths()) == 2
    assert tmp_data_dir.exists()
    assert tmp_data_dir_file.exists()

    cpa.rollback()
    assert tmp_data_dir.exists() is False
    assert tmp_data_dir_file.exists() is False


def test_create_path_with_content_clear_option(tmp_path: pathlib.Path):
    """Test create path with content clear option."""
    # create trestle project
    test_utils.ensure_trestle_config_dir(tmp_path)

    # create directories and a file
    tmp_data_dir = tmp_path.joinpath('data')
    tmp_data_dir_file = tmp_data_dir.joinpath('readme.md')
    cpa = CreatePathAction(tmp_data_dir_file)
    cpa.execute()
    assert len(cpa.get_created_paths()) == 2
    assert tmp_data_dir.exists()
    assert tmp_data_dir_file.exists()

    # write some content in the file
    file_pos = 0
    dummy_data = ''
    with open(tmp_data_dir_file, 'a+', encoding=const.FILE_ENCODING) as fp:
        fp.write(dummy_data)
        file_pos = fp.tell()
    assert file_pos >= 0

    # create action to create a file without clearing content
    cpa = CreatePathAction(tmp_data_dir_file, clear_content=False)
    cpa.execute()
    assert len(cpa.get_created_paths()) == 0
    assert tmp_data_dir_file.exists()
    with open(tmp_data_dir_file, 'a+', encoding=const.FILE_ENCODING) as fp:
        assert file_pos == fp.tell()

    # create action to create a file with clearing content
    cpa = CreatePathAction(tmp_data_dir_file, clear_content=True)
    cpa.execute()
    assert len(cpa.get_created_paths()) == 0
    assert tmp_data_dir_file.exists()
    with open(tmp_data_dir_file, 'a+', encoding=const.FILE_ENCODING) as fp:
        assert 0 == fp.tell()
        data = fp.readline()
        assert data == ''

    # rollback should bring back the cleared content
    cpa.rollback()
    assert tmp_data_dir.exists()
    assert tmp_data_dir_file.exists()
    with open(tmp_data_dir_file, 'a+', encoding=const.FILE_ENCODING) as fp:
        assert file_pos == fp.tell()
        fp.readline()

    # clearing content on direction should have no effect of the flag
    tmp_data_dir2 = tmp_path / 'data2'
    tmp_data_dir2.mkdir()
    cpa = CreatePathAction(tmp_data_dir2, clear_content=True)
    cpa.execute()
    assert len(cpa.get_created_paths()) == 0
    assert tmp_data_dir2.exists()
    cpa.rollback()
    assert tmp_data_dir2.exists()


def test_create_path_magic_methods(tmp_path):
    """Test create path magic methods."""
    tmp_data_dir = tmp_path.joinpath('data')
    test_utils.ensure_trestle_config_dir(tmp_path)
    cpa = CreatePathAction(tmp_data_dir)

    action_desc = cpa.to_string()
    assert action_desc == f'{cpa.get_type()} {tmp_data_dir}'
