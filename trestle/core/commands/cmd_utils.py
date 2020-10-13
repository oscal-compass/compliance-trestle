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

from trestle.core import const, utils
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


def move_to_trash(file_path: pathlib.Path):
    """Move the specified file to the trash directory.

    It overwrites the previous file if exists
    """
    if not file_path.is_file():
        raise TrestleError(f'Specified path "{file_path}" is not a file')
    trash_file_path = get_trash_file_path(file_path)
    fs.ensure_directory(trash_file_path.parent)
    copyfile(file_path, trash_file_path)
    file_path.unlink()


def get_model(file_path: str) -> OscalBaseModel:
    """Get the model specified by the file."""
    raise NotImplementedError()


def copy_values(src: OscalBaseModel, dest: OscalBaseModel) -> OscalBaseModel:
    """Copy available attribute values from source element to destination."""
    for raw_field in dest.__dict__.keys():
        if hasattr(src, raw_field):
            dest.__dict__[raw_field] = src.__dict__[raw_field]

    return dest


def parse_element_args(element_args: List[str]) -> List[ElementPath]:
    """Parse element args into a list of ElementPath."""
    if not isinstance(element_args, list):
        raise TrestleError(f'Input element_paths must be a list, but found {element_args.__class__}')

    element_paths: List[ElementPath] = []
    for element_arg in element_args:
        paths = parse_element_arg(element_arg)
        element_paths.extend(paths)

    return element_paths


def parse_element_arg(element_arg: str) -> List[ElementPath]:
    """Parse an element arg string into a list of ElementPath."""
    element_paths: List[ElementPath] = []
    element_arg = element_arg.strip()

    # search for wildcards and create paths with its parent path
    last_pos: int = -1
    prev_element_path = None
    parent_model = None
    for cur_pos, c in enumerate(element_arg):
        if c == ElementPath.WILDCARD:
            # extract the path string including wildcard
            start = last_pos + 1
            end = cur_pos + 1
            p = element_arg[start:end]
            if parent_model is not None:
                p = ElementPath.PATH_SEPARATOR.join([parent_model, p])

            # create and append elment_path
            element_path = ElementPath(p, parent_path=prev_element_path)
            element_paths.append(element_path)

            # get full path without the wildcard
            full_path = element_path.get_full_path_parts()
            path_str = ElementPath.PATH_SEPARATOR.join(full_path[:-1])

            # get the parent model for the full path
            parent_model = utils.get_singular_alias(path_str)

            # store values for next cycle
            prev_element_path = element_path
            last_pos = end

    if last_pos + 1 < len(element_arg):
        p = element_arg[last_pos + 1:]
        if parent_model is not None:
            p = ElementPath.PATH_SEPARATOR.join([parent_model, p])
        element_path = ElementPath(p)
        element_paths.append(element_path)

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
