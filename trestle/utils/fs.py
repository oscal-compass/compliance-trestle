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


def load_file(file_name: str):
    """Load file content."""
    _, file_extension = os.path.splitext(file_name)

    with open(file_name) as f:
        if file_extension == '.yaml':
            return yaml.load(f, yaml.FullLoader)
        elif file_extension == '.json':
            return json.load(f)
        else:
            raise TrestleError(f'Invalid file extension "{file_extension}"')


def create_file(path: str, file_name: str, data: dict, root_key: str = None):
    """Create a file at the given path with the specified content."""
    _, file_extension = os.path.splitext(file_name)
    file_path = os.path.join(path, file_name)
    logger.debug(f'Creating file "{file_path}"')
    with open(file_path, 'w') as file:
        # wrap data with model name
        if root_key is not None:
            data = {root_key: data}

        if file_extension == '.yaml':
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)
        elif file_extension == '.json':
            json.dump(data, file, indent=2, sort_keys=False)
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
