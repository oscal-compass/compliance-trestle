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
from typing import List, Optional

from . import fs

TRESTLE_TRASH_DIR = '.trestle/_trash/'
TRESTLE_TRASH_FILE_EXT = '.bk'  # should start with a dot
TRESTLE_TRASH_DIR_EXT = '__bk'


def to_trash_dir_path(dir_path: pathlib.Path) -> pathlib.Path:
    """Construct the path to the trashed file."""
    absolute_path = dir_path.resolve()
    root_path = fs.get_trestle_project_root(absolute_path)
    if root_path is None:
        raise AssertionError(f'Directory path "{absolute_path}" is not in a valid trestle project')

    trestle_trash_path = root_path / TRESTLE_TRASH_DIR

    relative_path = absolute_path.relative_to(str(root_path))
    if len(relative_path.parts) == 0:
        trash_dir = trestle_trash_path
    else:
        trash_dir = trestle_trash_path / f'{relative_path}{TRESTLE_TRASH_DIR_EXT}'

    return trash_dir


def to_trash_file_path(file_path: pathlib.Path) -> pathlib.Path:
    """Construct the path to the trashed file."""
    trash_file_dir = to_trash_dir_path(file_path.parent)
    trash_file_path = trash_file_dir / f'{file_path.name}{TRESTLE_TRASH_FILE_EXT}'

    return trash_file_path


def to_trash_path(path: pathlib.Path) -> pathlib.Path:
    """Convert the dir or file path to apporpriate trash file or dir path."""
    if path.suffix != '':
        return to_trash_file_path(path)
    else:
        return to_trash_dir_path(path)


def get_trash_root(path: pathlib.Path) -> Optional[pathlib.Path]:
    """Find the trestle trash root path."""
    if path is None or len(path.parts) <= 0:
        return None

    current = path
    while len(current.parts) > 1:  # it must not be the system root directory
        trash_dir = pathlib.Path.joinpath(current, TRESTLE_TRASH_DIR)
        if trash_dir.exists() and trash_dir.is_dir():
            return trash_dir
        current = current.parent

    return None


def to_origin_dir_path(trash_dir_path: pathlib.Path) -> pathlib.Path:
    """Convert trash content path to origin path."""
    if trash_dir_path.suffix != '' and trash_dir_path.suffix.endswith(TRESTLE_TRASH_FILE_EXT):
        raise AssertionError(f'Given path "{trash_dir_path}" is a trash file, not a valid trash directory')

    trestle_root = fs.get_trestle_project_root(trash_dir_path)
    if trestle_root is None:
        raise AssertionError(f'Directory path "{trash_dir_path}" is not in a valid trestle project path')

    trash_root = get_trash_root(trash_dir_path)
    if trash_root is None:
        raise AssertionError(f'Directory path "{trash_dir_path}" is not in a valid trestle trash path')

    if not fs.has_parent_path(trash_dir_path, trash_root):
        raise AssertionError(f'Directory path "{trash_dir_path}" is not a valid trash dir path')

    relative_path = trash_dir_path.relative_to(str(trash_root))

    origin_path_parts: List[str] = []
    for item in relative_path.parts:
        parts = item.split(TRESTLE_TRASH_DIR_EXT)
        origin_path_parts.append(parts[0])

    origin_relative_path = pathlib.Path('/'.join(origin_path_parts))
    origin_path = trestle_root / origin_relative_path
    return origin_path


def to_origin_file_path(trash_file_path: pathlib.Path) -> pathlib.Path:
    """Convert trash file path to origin file path."""
    if trash_file_path.suffix != TRESTLE_TRASH_FILE_EXT:
        raise AssertionError(f'File path "{trash_file_path}" is not a valid trash file path')

    origin_dir = to_origin_dir_path(trash_file_path.parent)
    file_parts = trash_file_path.name.split(TRESTLE_TRASH_FILE_EXT)
    origin_file_path = origin_dir / file_parts[0]

    return origin_file_path


def to_origin_path(trash_content_path: pathlib.Path) -> pathlib.Path:
    """Convert the trash path to origin path."""
    if trash_content_path.suffix == TRESTLE_TRASH_FILE_EXT:
        return to_origin_file_path(trash_content_path)
    else:
        return to_origin_dir_path(trash_content_path)


def store_file(file_path: pathlib.Path, delete_source: bool = False) -> None:
    """Move the specified file to the trash directory.

    It overwrites the previous file if exists
    """
    if not file_path.is_file():
        raise AssertionError(f'Specified path "{file_path}" is not a file')

    trash_file_path = to_trash_file_path(file_path)
    trash_file_path.parent.mkdir(exist_ok=True, parents=True)
    copyfile(file_path, trash_file_path)

    if delete_source:
        file_path.unlink()


def store_dir(dir_path: pathlib.Path, delete_source: bool = False) -> None:
    """Move the specified dir to the trash directory.

    It overwrites the previous directory and contents if exists
    """
    if not dir_path.is_dir():
        raise AssertionError(f'Specified path "{dir_path}" is not a dir')

    # move all files/directories under sub_path
    for item_path in pathlib.Path.iterdir(dir_path):
        if item_path.is_file():
            store_file(item_path, delete_source)
        elif item_path.is_dir():
            store_dir(item_path, delete_source)

    if delete_source:
        dir_path.rmdir()


def store(content_path: pathlib.Path, delete_content: bool = False) -> None:
    """Move the specified file or directory to the trash directory.

    It overwrites the previous file or directory if exists
    """
    if content_path.is_file():
        return store_file(content_path, delete_content)
    elif content_path.is_dir():
        return store_dir(content_path, delete_content)


def recover_file(file_path: pathlib.Path, delete_trash: bool = False) -> None:
    """Recover the specified file from the trash directory.

    It recovers the latest file from trash if exists
    """
    trash_file_path = to_trash_file_path(file_path)
    if not trash_file_path.exists():
        raise AssertionError(f'Specified path "{file_path}" could not be found in trash')

    file_path.parent.mkdir(exist_ok=True, parents=True)
    copyfile(trash_file_path, file_path)

    if delete_trash:
        trash_file_path.unlink()


def recover_dir(dest_dir_path: pathlib.Path, delete_trash: bool = False) -> None:
    """Move the specified dir from the trash directory.

    dest_dir_path: destination path of the directory inside a trestle project

    It recovers the latest directory and contents from trash if exists
    """
    trash_dir_path = to_trash_dir_path(dest_dir_path)
    if not (trash_dir_path.exists() and trash_dir_path.is_dir()):
        raise AssertionError(f'Specified path "{dest_dir_path}" could not be found in trash')

    # move all files/directories under sub_path
    for item_path in pathlib.Path.iterdir(trash_dir_path):
        if item_path.is_file():
            recover_file(to_origin_file_path(item_path), delete_trash)
        elif item_path.is_dir():
            recover_dir(to_origin_dir_path(item_path), delete_trash)

    if delete_trash:
        trash_dir_path.rmdir()


def recover(dest_content_path: pathlib.Path, delete_trash: bool = False) -> None:
    """Recover the specified file or directory from the trash directory.

    dest_content_path: destination content path that needs to be recovered from trash
    It recovers the latest path content from trash if exists
    """
    if dest_content_path.suffix != '':
        return recover_file(dest_content_path, delete_trash)
    else:
        return recover_dir(dest_content_path, delete_trash)
