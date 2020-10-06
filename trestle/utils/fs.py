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
"""Common file system utilities."""

import json
import logging
import os
import pathlib

from trestle.core import const
from trestle.core.err import TrestleError

import yaml

logger = logging.getLogger(__name__)


def should_ignore(name) -> bool:
    """Check if the file or directory should be ignored or not."""
    return name[0] == '.' or name[0] == '_'


def ensure_directory(path):
    """
    Ensure the directory ```path``` exists.

    It creates the directories along the path if they do not exist.
    Arguments:
        path(str): The path to the directory

    Raises:
        AssertionError: If the directory path exists but is not a directory

    Returns: None
    """
    path = os.path.abspath(path)

    if not os.path.exists(path):
        os.makedirs(path)
    elif not os.path.isdir(path):
        raise AssertionError(f'Path `{path}` exists but is not a directory')


def is_valid_project_root(project_root: pathlib.Path) -> bool:
    """Check if the project root is a valid trestle project root."""
    if project_root is None or project_root == '' or len(project_root.parts) <= 0:
        return False

    trestle_dir = pathlib.Path.joinpath(project_root, const.TRESTLE_CONFIG_DIR)
    if trestle_dir.exists() and trestle_dir.is_dir():
        return True

    return False


def get_trestle_project_root(path: pathlib.Path) -> pathlib.Path:
    """Get the trestle project root folder in the path."""
    if path is None or len(path.parts) <= 0:
        return None

    current = path
    while len(current.parts) > 0:
        if is_valid_project_root(current):
            return current
        current = current.parent

    return None


def has_parent_path(sub_path: pathlib.Path, parent_path: pathlib.Path) -> bool:
    """Check if sub_path has the specified parent_dir path."""
    if parent_path is None or len(parent_path.parts) <= 0:
        return False

    # sub_path should be longer than parent path
    if len(sub_path.parts) < len(parent_path.parts):
        return False

    matched = True
    for i, part in enumerate(parent_path.parts):
        if part is not sub_path.parts[i]:
            matched = False
            break

    return matched


def has_trestle_project_in_path(path: pathlib.Path) -> bool:
    """Check if path has a valid trestle project among the parents."""
    trestle_project_root = get_trestle_project_root(path)
    return trestle_project_root is not None


def clean_project_sub_path(sub_path: pathlib.Path):
    """Clean all directories and files in the project sub sub.

    It ensures the sub_path is a child path in the project root.
    """
    if sub_path.exists():
        project_root = sub_path.parent
        if not has_trestle_project_in_path(project_root):
            raise TrestleError('Path to be cleaned is not a under valid Trestle project root')

        # clean all files/directories under sub_path
        if sub_path.is_dir():
            for item in pathlib.Path.iterdir(sub_path):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    clean_project_sub_path(item)
            sub_path.rmdir()
        # delete the sub_path
        elif sub_path.is_file():
            sub_path.unlink()


def load_file(file_name: str):
    """Load JSON or YAML file content."""
    _, file_extension = os.path.splitext(file_name)

    with open(file_name) as f:
        if file_extension == '.yaml':
            return yaml.load(f, yaml.FullLoader)
        elif file_extension == '.json':
            return json.load(f)
        else:
            raise TrestleError(f'Invalid file extension "{file_extension}"')


def find_node(data: dict, key: str, depth: int = 0, max_depth: int = 1, instance_type: type = list):
    """Find a node of an instance_type in the data recursively."""
    if depth > max_depth:
        return

    if key in data and isinstance(data[key], instance_type):
        yield data[key]

    for _, v in data.items():
        if isinstance(v, dict):
            for i in find_node(v, key, depth + 1, max_depth, instance_type):
                yield i
        elif isinstance(v, list):
            for item in v:
                for i in find_node(item, key, depth + 1, max_depth, instance_type):
                    yield i
