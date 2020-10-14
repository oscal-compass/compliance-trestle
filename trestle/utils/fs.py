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
from typing import Optional, Tuple

from trestle.core import const
from trestle.core import err
from trestle.core import utils
from trestle.core.base_model import OscalBaseModel
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


def get_trestle_project_root(path: pathlib.Path) -> Optional[pathlib.Path]:
    """Get the trestle project root folder in the path."""
    if path is None or len(path.parts) <= 0:
        return None

    current = path
    while len(current.parts) > 1:  # it must not be the system root directory
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


def get_contextual_model_type(path: pathlib.Path = None) -> Tuple[OscalBaseModel, str]:
    """Get the full contextual model class and alias based on the contextual path."""
    if path is None:
        path = pathlib.Path.cwd()

    root_path = get_trestle_project_root(path)

    if root_path is None:
        raise err.TrestleError('Trestle root directory not found')

    relative_path = path.relative_to(str(root_path))
    if len(relative_path.parts) < 2 or relative_path.parts[0] not in const.MODELTYPE_TO_MODELMODULE:
        raise err.TrestleError('Trestle project not found')

    project_type = relative_path.parts[0]  # catalogs, profiles, etc
    module_name = const.MODELTYPE_TO_MODELMODULE[project_type]

    model_relative_path = relative_path.relative_to(pathlib.Path(*relative_path.parts[:2]))

    model_type, model_alias = utils.get_root_model(module_name)

    for i in range(len(model_relative_path.parts)):
        tmp_path = root_path.joinpath(*relative_path.parts[:2], *model_relative_path.parts[:i + 1])

        alias = extract_alias(tmp_path)
        if tmp_path.is_dir() or (tmp_path.is_file() and alias != extract_alias(tmp_path.parent)):
            if i > 0 or model_alias != alias:
                model_alias = alias
                if utils.is_collection_field_type(model_type):
                    model_type = utils.get_inner_type(model_type)
                else:
                    model_type = model_type.alias_to_field_map()[alias].outer_type_

    return model_type, model_alias


def get_stripped_contextual_model(path: pathlib.Path = None) -> Tuple[OscalBaseModel, str]:
    """
    Get the stripped contextual model class and alias based on the contextual path.

    This function relies on the directory structure of the trestle model being edited to determine, based on the
    existing files and folder, which fields should be stripped from the model type represented by the path passed in as
    a parameter.
    """
    if path is None:
        path = pathlib.Path.cwd()

    model_type, model_alias = get_contextual_model_type(path)

    # Stripped models do not apply to collection types such as List[] and Dict{}
    if utils.is_collection_field_type(model_type):
        return model_type, model_alias

    if path.is_dir():
        paths = list(path.glob(f'{model_alias}.*'))
        if len(paths) == 0:
            raise err.TrestleError(f'{model_alias}.json/yaml/yml not found in {path}')
        elif len(paths) > 1:
            raise err.TrestleError(f'There is more than one {model_alias}.json/yaml/yml file in {path}')
        path = paths[0]

    aliases_to_be_stripped = set()
    for f in path.parent.iterdir():
        alias = extract_alias(f)
        if alias != model_alias:
            aliases_to_be_stripped.add(alias)

    if len(aliases_to_be_stripped) > 0:
        model_type = model_type.create_stripped_model_type(stripped_fields_aliases=list(aliases_to_be_stripped))

    return model_type, model_alias


def extract_alias(path: pathlib.Path) -> str:
    """Extract alias from filename or directory name removing extensions and prefixes related to dict and list."""
    alias = path.with_suffix('').name  # remove suffix extension of file if it exists
    alias = alias.split(const.IDX_SEP)[-1]  # get suffix of file or directory name representing list or dict item
    return alias


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
