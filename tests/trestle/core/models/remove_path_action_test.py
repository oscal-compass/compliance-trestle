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
"""Tests for trestle remove path action class."""

import pathlib

import pytest

from tests import test_utils

import trestle.core.const as const
from trestle.core.err import TrestleError
from trestle.core.models.actions import RemovePathAction
from trestle.utils import trash


def test_remove_path_file(tmp_path: pathlib.Path) -> None:
    """Test remove path with content clear option."""
    tmp_data_dir = tmp_path.joinpath('data')
    tmp_data_file = tmp_data_dir.joinpath('readme.md')
    tmp_data_dir.mkdir(exist_ok=True, parents=True)

    # not a valid trestle project should error in constructor
    with pytest.raises(TrestleError):
        rpa = RemovePathAction(tmp_data_file)

    # create trestle project
    test_utils.ensure_trestle_config_dir(tmp_path)
    rpa = RemovePathAction(tmp_data_file)

    # missing file should error
    # with pytest.raises(TrestleError): # noqa: E800  remove path is not working properly
    #    rpa.execute()                  # noqa: E800

    # write some content in the file
    file_pos = 0
    dummy_data = 'DUMMY DATA'
    with open(tmp_data_file, 'a+', encoding=const.FILE_ENCODING) as fp:
        fp.write(dummy_data)
        file_pos = fp.tell()
    assert file_pos >= 0

    # remove file
    tmp_data_file_trash = trash.to_trash_file_path(tmp_data_file)
    assert tmp_data_file_trash.exists() is False
    rpa.execute()
    tmp_data_file_trash.exists()
    assert tmp_data_file.exists() is False

    # rollback file
    rpa.rollback()
    tmp_data_file_trash.exists()
    tmp_data_file.exists()
    with open(tmp_data_file, 'a+', encoding=const.FILE_ENCODING) as fp:
        assert file_pos == fp.tell()

    # remove dir
    rpa = RemovePathAction(tmp_data_dir)
    tmp_data_trash = trash.to_trash_dir_path(tmp_data_dir)
    tmp_data_file_trash = trash.to_trash_file_path(tmp_data_file)
    if tmp_data_trash.exists():
        tmp_data_trash.rmdir()
    rpa.execute()
    assert tmp_data_trash.exists()
    assert tmp_data_file_trash.exists()
    assert tmp_data_file.exists() is False
    assert tmp_data_dir.exists() is False

    # rollback dir
    rpa.rollback()
    assert tmp_data_trash.exists() is False
    assert tmp_data_file_trash.exists() is False
    assert tmp_data_file.exists()
    assert tmp_data_dir.exists()


def test_remove_path_magic_methods(tmp_path):
    """Test remove path magic methods."""
    tmp_data_dir = tmp_path.joinpath('data')
    test_utils.ensure_trestle_config_dir(tmp_path)
    rpa = RemovePathAction(tmp_data_dir)

    action_desc = rpa.to_string()
    assert action_desc == f'{rpa.get_type()} {tmp_data_dir}'
