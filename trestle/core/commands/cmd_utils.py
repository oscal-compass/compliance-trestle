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
from typing import Any, List, Type

from trestle.core import const, utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.core.models.elements import ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.utils import fs


def get_model(file_path: str) -> OscalBaseModel:
    """Get the model specified by the file."""
    raise NotImplementedError()


def model_type_is_too_granular(model_type: Type[Any]) -> bool:
    """Is an model_type too fine to split."""
    if utils.is_collection_field_type(model_type):
        return False
    if hasattr(model_type, '__fields__') and '__root__' in model_type.__fields__:
        return True
    if model_type.__name__ in ['str', 'ConstrainedStrValue', 'int', 'float', 'datetime']:
        return True
    return False


def split_is_too_fine(split_paths: str, model_obj: OscalBaseModel) -> bool:
    """Determine if the element path list goes too fine, e.g. individual strings."""
    for split_path in split_paths.split(','):
        model_type = utils.get_target_model(split_path.split('.'), type(model_obj))
        if model_type_is_too_granular(model_type):
            return True
    return False


def parse_element_args(model: OscalBaseModel,
                       element_args: List[str],
                       contextual_mode: bool = True) -> List[ElementPath]:
    """Parse element args into a list of ElementPath.

    contextual_mode specifies if the path is a valid project model path or not. For example,
    if we are processing a metadata.parties.*, we need to know which metadata we are processing. If we pass
    contextual_mode=true, we can infer the root model by inspecting the file directory

    If contextual_mode=False, then the path must include the full path, e.g. catalog.metadata.parties.* instead of just
    metadata.parties.*

    One option for caller to utilize this utility function: fs.is_valid_project_model_path(pathlib.Path.cwd())
    """
    element_paths: List[ElementPath] = []
    for element_arg in element_args:
        paths = parse_element_arg(model, element_arg, contextual_mode)
        element_paths.extend(paths)

    return element_paths


def parse_element_arg(model_obj: OscalBaseModel, element_arg: str, contextual_mode: bool = True) -> List[ElementPath]:
    """Parse an element arg string into a list of ElementPath.

    contextual_mode specifies if the path is a valid project model path or not. For example,
    if we are processing a metadata.parties.*, we need to know which metadata we are processing. If we pass
    contextual_mode=True, we can infer the root model by inspecting the file directory

    If contextual_mode=False, then the path must include the full path, e.g. catalog.metadata.parties.* instead of just
    metadata.parties.*

    One option for caller to utilize this utility function: fs.is_valid_project_model_path(pathlib.Path.cwd())

    Originally this function did not allow wildcards for model objects rather than lists.  This was changed by passing
    in the model object and allowing inspection of its parts so the needed element paths can be created on the fly.
    """
    element_paths: List[ElementPath] = []
    element_arg = element_arg.strip()

    if element_arg == '*':
        raise TrestleError('Invalid element path containing only a single wildcard.')

    if element_arg == '':
        raise TrestleError('Invalid element path is empty string.')

    # search for wildcards and create paths with its parent path
    path_parts = element_arg.split(ElementPath.PATH_SEPARATOR)
    if len(path_parts) <= 1:
        raise TrestleError(f'Invalid element path "{element_arg}" with only one element and no wildcard')

    sub_model = model_obj

    prev_element_path = None
    parent_model = path_parts[0]
    i = 1
    while i < len(path_parts):
        p = path_parts[i]
        if p == ElementPath.WILDCARD and len(element_paths) > 0:
            # append wildcard to the latest element path
            latest_path = element_paths.pop()
            if latest_path.get_last() == ElementPath.WILDCARD:
                raise TrestleError(f'Invalid element path with consecutive {ElementPath.WILDCARD}')

            latest_path_str = ElementPath.PATH_SEPARATOR.join([latest_path.to_string(), p])
            element_path = ElementPath(latest_path_str, latest_path.get_parent())
        else:
            # create and append elment_path
            if p != ElementPath.WILDCARD:
                sub_model = getattr(sub_model, p, None)
            p = ElementPath.PATH_SEPARATOR.join([parent_model, p])
            element_path = ElementPath(p, parent_path=prev_element_path)

        # If the path has wildcard and there are more parts later,
        # Get the parent model for the alias path
        # If path has wildcard and it does not refer to a list, then there can be nothing after *
        if element_path.get_last() == ElementPath.WILDCARD:
            full_path_str = ElementPath.PATH_SEPARATOR.join(element_path.get_full_path_parts()[:-1])
            parent_model = fs.get_singular_alias(full_path_str, contextual_mode)
            # Does wildcard mean we need to inspect the sub_model to determine what can be split off from it?
            # If it has __root__ it may mean it contains a list of objects and should be split as a list
            if isinstance(sub_model, OscalBaseModel):
                root = getattr(sub_model, '__root__', None)
                if root is None or not isinstance(root, list):
                    # Cannot have parts beyond * if it isn't a list
                    if i < len(path_parts) - 1:
                        raise TrestleError(
                            f'Cannot split beyond * when the wildcard does not refer to a list.  Path: {element_arg}'
                        )
                    for key in sub_model.__fields__.keys():
                        new_path = full_path_str + '.' + utils.classname_to_alias(key, 'json')
                        if not split_is_too_fine(new_path, model_obj):
                            element_paths.append(ElementPath(new_path))
                    # Since wildcard is last in the chain when splitting an oscal model we are done
                    return element_paths
        else:
            parent_model = element_path.get_element_name()

        # store values for next cycle
        prev_element_path = element_path
        element_paths.append(element_path)
        i += 1

    if len(element_paths) <= 0:
        raise TrestleError(f'Invalid element path "{element_arg}" without any path separator')

    return element_paths


def to_model_file_name(model_obj: OscalBaseModel, file_prefix: str, content_type: FileContentType) -> str:
    """Return the file name for the item."""
    file_ext = FileContentType.to_file_extension(content_type)
    model_type = utils.classname_to_alias(type(model_obj).__name__, 'json')
    file_name = f'{file_prefix}{const.IDX_SEP}{model_type}{file_ext}'
    return file_name
