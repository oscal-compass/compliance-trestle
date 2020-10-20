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
"""Trestle command related utilities."""
import pathlib
from shutil import copyfile
from typing import List

from trestle.core import const
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.core.models.elements import Element, ElementPath
from trestle.utils import fs


def get_trash_file_path(file_path: pathlib.Path):
    """Construct the path to the trashed file."""
    absolute_path = file_path.absolute()
    root_path = fs.get_trestle_project_root(absolute_path)

    if root_path is None:
        raise TrestleError(f'File path "{absolute_path}" is not in a valid trestle project')

    trash_dir = root_path / const.TRESTLE_TRASH_DIR

    trash_file_dir = trash_dir / absolute_path.relative_to(str(root_path)).parent
    trash_file_path = trash_file_dir / f'{file_path.name}{const.TRESTLE_TRASH_FILE_EXT}'

    return trash_file_path


def move_to_trash(file_path: pathlib.Path, delete_file: bool = True):
    """Move the specified file to the trash directory.

    It overwrites the previous file if exists
    """
    if not file_path.is_file():
        raise TrestleError(f'Specified path "{file_path}" is not a file')
    trash_file_path = get_trash_file_path(file_path)
    fs.ensure_directory(trash_file_path.parent)
    copyfile(file_path, trash_file_path)

    if delete_file:
        file_path.unlink()


def get_model(file_path: str) -> OscalBaseModel:
    """Get the model specified by the file."""
    raise NotImplementedError()


def parse_element_args(element_args: List[str], contextual_mode: bool = True) -> List[ElementPath]:
    """Parse element args into a list of ElementPath.

    contextual_mode specifies if the path is a valid project model path or not. For example,
    if we are processing a metadata.parties.*, we need to know which metadata we are processing. If we pass
    contextual_mode=true, we can infer the root model by inspecting the file directory

    If contextual_mode=False, then the path must include the full path, e.g. catalog.metadata.parties.* instead of just
    metadata.parties.*

    One option for caller to utilize this utility function: fs.is_valid_project_model_path(pathlib.Path.cwd())
    """
    if not isinstance(element_args, list):
        raise TrestleError(f'Input element_paths must be a list, but found {element_args.__class__}')

    element_paths: List[ElementPath] = []
    for element_arg in element_args:
        paths = parse_element_arg(element_arg, contextual_mode)
        element_paths.extend(paths)

    return element_paths


def parse_element_arg(element_arg: str, contextual_mode: bool = True) -> List[ElementPath]:
    """Parse an element arg string into a list of ElementPath.

    contextual_mode specifies if the path is a valid project model path or not. For example,
    if we are processing a metadata.parties.*, we need to know which metadata we are processing. If we pass
    contextual_mode=True, we can infer the root model by inspecting the file directory

    If contextual_mode=False, then the path must include the full path, e.g. catalog.metadata.parties.* instead of just
    metadata.parties.*

    One option for caller to utilize this utility function: fs.is_valid_project_model_path(pathlib.Path.cwd())
    """
    element_paths: List[ElementPath] = []
    element_arg = element_arg.strip()

    # search for wildcards and create paths with its parent path
    path_parts = element_arg.split(ElementPath.PATH_SEPARATOR)
    if len(path_parts) <= 0:
        raise TrestleError(f'Invalid element path "{element_arg}" without any path separator')

    prev_element_path = None
    parent_model = path_parts[0]
    i = 1
    while i < len(path_parts):
        p = path_parts[i]
        if p == ElementPath.WILDCARD:
            # * cannot be the second part in the path
            if len(element_paths) <= 0:
                raise TrestleError(f'Invalid element path "{element_arg}" with {ElementPath.WILDCARD}')

            # append wildcard to the latest element path
            latest_path = element_paths.pop()
            if latest_path.get_last() == ElementPath.WILDCARD:
                raise TrestleError(f'Invalid element path with consecutive {ElementPath.WILDCARD}')

            latest_path_str = ElementPath.PATH_SEPARATOR.join([latest_path.to_string(), p])
            element_path = ElementPath(latest_path_str, latest_path.get_parent())
        else:
            # create and append elment_path
            p = ElementPath.PATH_SEPARATOR.join([parent_model, p])
            element_path = ElementPath(p, parent_path=prev_element_path)

        # if the path has wildcard and there is more parts later,
        # get the parent model for the alias path
        if element_path.get_last() == ElementPath.WILDCARD:
            full_path_str = ElementPath.PATH_SEPARATOR.join(element_path.get_full_path_parts()[:-1])
            parent_model = fs.get_singular_alias(full_path_str, contextual_mode)
        else:
            parent_model = element_path.get_element_name()

        # store values for next cycle
        prev_element_path = element_path
        element_paths.append(element_path)
        i += 1

    if len(element_paths) <= 0:
        raise TrestleError(f'Invalid element path "{element_arg}" without any path separator')

    return element_paths


def get_dir_base_file_element(item, name: str) -> Element:
    """Get an wrapped element for the base file in a split directory.

    If the item is a list, it will return a dict like `{"name": []`
    If the item is a dict, it will return a dict like `{"name": {}}`
    """
    if isinstance(item, list):
        base_model: dict = {name: []}
    else:
        base_model = {name: {}}

    return Element(base_model)
