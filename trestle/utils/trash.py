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
"""Trestle trash module."""

import pathlib
from shutil import copyfile

from . import fs

TRESTLE_TRASH_DIR = '.trestle/_trash/'
TRESTLE_TRASH_FILE_EXT = '.bk'


def get_trash_file_path(file_path: pathlib.Path):
    """Construct the path to the trashed file."""
    absolute_path = file_path.absolute()
    root_path = fs.get_trestle_project_root(absolute_path)

    if root_path is None:
        raise AssertionError(f'File path "{absolute_path}" is not in a valid trestle project')

    trash_dir = root_path / TRESTLE_TRASH_DIR

    trash_file_dir = trash_dir / absolute_path.relative_to(str(root_path)).parent
    trash_file_path = trash_file_dir / f'{file_path.name}{TRESTLE_TRASH_FILE_EXT}'

    return trash_file_path


def move_to_trash(file_path: pathlib.Path, delete_file: bool = True):
    """Move the specified file to the trash directory.

    It overwrites the previous file if exists
    """
    if not file_path.is_file():
        raise AssertionError(f'Specified path "{file_path}" is not a file')
    trash_file_path = get_trash_file_path(file_path)
    fs.ensure_directory(trash_file_path.parent)
    copyfile(file_path, trash_file_path)

    if delete_file:
        file_path.unlink()
