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
TRESTLE_TRASH_EXT = '__bk'


def get_trash_dir_path(dir_path: pathlib.Path):
    """Construct the path to the trashed file."""
    absolute_path = dir_path.absolute()
    root_path = fs.get_trestle_project_root(absolute_path)
    if root_path is None:
        raise AssertionError(f'Directory path "{absolute_path}" is not in a valid trestle project')

    trestle_trash_path = root_path / TRESTLE_TRASH_DIR

    relative_path = absolute_path.relative_to(str(root_path))
    if len(relative_path.parts) == 0:
        trash_dir = trestle_trash_path
    else:
        trash_dir = trestle_trash_path / f'{relative_path}{TRESTLE_TRASH_EXT}'

    return trash_dir


def get_trash_file_path(file_path: pathlib.Path):
    """Construct the path to the trashed file."""
    trash_file_dir = get_trash_dir_path(file_path.parent)
    trash_file_path = trash_file_dir / f'{file_path.name}{TRESTLE_TRASH_EXT}'

    return trash_file_path


def move_file_to_trash(file_path: pathlib.Path, delete_file: bool = True):
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


def move_dir_to_trash(dir_path: pathlib.Path, delete_all: bool = True):
    """Move the specified dir to the trash directory.

    It overwrites the previous directory and contents if exists
    """
    if not dir_path.is_dir():
        raise AssertionError(f'Specified path "{dir_path}" is not a dir')

    # move all files/directories under sub_path
    for item_path in pathlib.Path.iterdir(dir_path):
        if item_path.is_file():
            move_file_to_trash(item_path, delete_all)
        elif item_path.is_dir():
            move_dir_to_trash(item_path, delete_all)

    if delete_all:
        dir_path.rmdir()


def move_to_trash(content_path: pathlib.Path, delete_content: bool = True):
    """Move the specified file or directory to the trash directory.

    It overwrites the previous file or directory if exists
    """
    if content_path.is_file():
        return move_file_to_trash(content_path, delete_content)
    elif content_path.is_dir():
        return move_dir_to_trash(content_path, delete_content)
