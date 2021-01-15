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
import pathlib
from typing import Any, Dict, List, Optional, Tuple, Type, cast

from pydantic import create_model

from trestle.core import const
from trestle.core import err
from trestle.core import utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.core.models.file_content_type import FileContentType

import yaml

logger = logging.getLogger(__name__)


def should_ignore(name: str) -> bool:
    """Check if the file or directory should be ignored or not."""
    return name[0] == '.' or name[0] == '_'


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
    if path is None or path == '' or len(path.parts) <= 0:
        return None

    current = path
    while len(current.parts) > 1:  # it must not be the system root directory
        if is_valid_project_root(current):
            return current
        current = current.parent

    return None


def is_valid_project_model_path(path: pathlib.Path) -> bool:
    """Check if the file/directory path is a valid trestle model project."""
    if path is None or path == '' or len(path.parts) <= 0:
        return False

    root_path = get_trestle_project_root(path)
    if root_path is None:
        return False

    relative_path = path.relative_to(str(root_path))
    if len(relative_path.parts) < 2 or relative_path.parts[0] not in const.MODELTYPE_TO_MODELMODULE:
        return False

    project_type = relative_path.parts[0]  # catalogs, profiles, etc

    if project_type not in const.MODELTYPE_TO_MODELMODULE.keys():
        return False

    return True


def get_project_model_path(path: pathlib.Path) -> Optional[pathlib.Path]:
    """Get the base path of the trestle model project."""
    if path is None or path == '' or len(path.parts) <= 2:
        return None

    for i in range(2, len(path.parts)):
        current = pathlib.Path(path.parts[0]).joinpath(*path.parts[1:i + 1])
        if is_valid_project_model_path(current):
            return current

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


def get_contextual_model_type(path: pathlib.Path = None) -> Tuple[Type[OscalBaseModel], str]:
    """Get the full contextual model class and full jsonpath for the alias based on the contextual path."""
    if path is None:
        path = pathlib.Path.cwd()

    if not is_valid_project_model_path(path):
        raise err.TrestleError(f'Trestle project not found at {path}')

    root_path = get_trestle_project_root(path)
    project_model_path = get_project_model_path(path)

    if root_path is None or project_model_path is None:
        raise err.TrestleError('Trestle project not found')

    relative_path = path.relative_to(str(root_path))
    project_type = relative_path.parts[0]  # catalogs, profiles, etc
    module_name = const.MODELTYPE_TO_MODELMODULE[project_type]

    model_relative_path = pathlib.Path(*relative_path.parts[2:])

    model_type, model_alias = utils.get_root_model(module_name)
    full_alias = model_alias

    for i in range(len(model_relative_path.parts)):
        tmp_path = root_path.joinpath(*relative_path.parts[:2], *model_relative_path.parts[:i + 1])

        alias = extract_alias(tmp_path)
        if i > 0 or model_alias != alias:
            model_alias = alias
            full_alias = f'{full_alias}.{model_alias}'
            if utils.is_collection_field_type(model_type):
                model_type = utils.get_inner_type(model_type)
            else:
                model_type = model_type.alias_to_field_map()[alias].outer_type_

    return model_type, full_alias


def get_stripped_contextual_model(path: pathlib.Path = None,
                                  aliases_not_to_be_stripped: List[str] = None) -> Tuple[Type[OscalBaseModel], str]:
    """
    Get the stripped contextual model class and alias based on the contextual path.

    This function relies on the directory structure of the trestle model being edited to determine, based on the
    existing files and folder, which fields should be stripped from the model type represented by the path passed in as
    a parameter.
    """
    if path is None:
        path = pathlib.Path.cwd()
    if aliases_not_to_be_stripped is None:
        aliases_not_to_be_stripped = []

    singular_model_type, model_alias = get_contextual_model_type(path)

    # Stripped models do not apply to collection types such as List[] and Dict{}
    # if model type is a list or dict, generate a new wrapping model for it
    if utils.is_collection_field_type(singular_model_type):
        malias = model_alias.split('.')[-1]
        class_name = utils.alias_to_classname(malias, 'json')
        model_type = create_model(class_name, __base__=OscalBaseModel, __root__=(singular_model_type, ...))
        model_type = cast(Type[OscalBaseModel], model_type)
        return model_type, model_alias

    malias = model_alias.split('.')[-1]

    if path.is_dir() and malias != extract_alias(path):
        split_subdir = path / malias
    else:
        split_subdir = path.parent / path.with_suffix('').name

    aliases_to_be_stripped = set()
    if split_subdir.exists():
        for f in split_subdir.iterdir():
            alias = extract_alias(f)
            if alias not in aliases_not_to_be_stripped:
                aliases_to_be_stripped.add(alias)

    if len(aliases_to_be_stripped) > 0:
        model_type = singular_model_type.create_stripped_model_type(
            stripped_fields_aliases=list(aliases_to_be_stripped)
        )
        return model_type, model_alias
    else:
        return singular_model_type, model_alias


def extract_alias(path: pathlib.Path) -> str:
    """Extract alias from filename or directory name removing extensions and prefixes related to dict and list."""
    alias = path.with_suffix('').name  # remove suffix extension of file if it exists
    alias = alias.split(const.IDX_SEP)[-1]  # get suffix of file or directory name representing list or dict item
    return alias


def clean_project_sub_path(sub_path: pathlib.Path) -> None:
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


def load_file(file_name: pathlib.Path) -> Dict[str, Any]:
    """
    Load JSON or YAML file content into a dict.

    This is not intended to be the default load mechanism. It should only be used
    if a OSCAL object type is unknown but the context a user is in.
    """
    content_type = FileContentType.to_content_type(file_name.suffix)
    with file_name.open('r', encoding=const.FILE_ENCODING) as f:
        if content_type == FileContentType.YAML:
            return yaml.load(f, yaml.FullLoader)
        elif content_type == FileContentType.JSON:
            return json.load(f)


def get_singular_alias(alias_path: str, contextual_mode: bool = False) -> str:
    """
    Get the alias in the singular form from a jsonpath.

    If contextual_mode is True and contextual_path is None, it assumes alias_path is relative to the directory the user
    is running trestle from.
    """
    if len(alias_path.strip()) == 0:
        raise err.TrestleError('Invalid jsonpath.')

    singular_alias: str = ''

    full_alias_path = alias_path
    if contextual_mode:
        _, full_model_alias = get_contextual_model_type()
        first_alias_a = full_model_alias.split('.')[-1]
        first_alias_b = alias_path.split('.')[0]
        if first_alias_a == first_alias_b:
            full_model_alias = '.'.join(full_model_alias.split('.')[:-1])
        full_alias_path = '.'.join([full_model_alias, alias_path]).strip('.')

    path_parts = full_alias_path.split(const.ALIAS_PATH_SEPARATOR)
    if len(path_parts) < 2:
        raise err.TrestleError('Invalid jsonpath.')

    model_types = []

    root_model_alias = path_parts[0]
    found = False
    for module_name in const.MODELTYPE_TO_MODELMODULE.values():
        model_type, model_alias = utils.get_root_model(module_name)
        if root_model_alias == model_alias:
            found = True
            model_types.append(model_type)
            break

    if not found:
        raise err.TrestleError(f'{root_model_alias} is an invalid root model alias.')

    model_type = model_types[0]
    for i in range(1, len(path_parts)):
        if utils.is_collection_field_type(model_type):
            if i == len(path_parts) - 1 and path_parts[i] == '*':
                break
            model_type = utils.get_inner_type(model_type)
            i = i + 1
        else:
            model_type = model_type.alias_to_field_map()[path_parts[i]].outer_type_
        model_types.append(model_type)

    last_alias = path_parts[-1]
    if last_alias == '*':
        last_alias = path_parts[-2]
    if not utils.is_collection_field_type(model_type):
        raise err.TrestleError('Not a valid generic collection model.')

    parent_model_type = model_types[-2]
    singular_alias = utils.classname_to_alias(
        utils.get_inner_type(parent_model_type.alias_to_field_map()[last_alias].outer_type_).__name__, 'json'
    )

    return singular_alias
