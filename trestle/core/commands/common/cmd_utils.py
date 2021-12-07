# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Trestle command related utilities."""
import pathlib
from typing import Any, List, Optional, Type, Union

from trestle.core import const, utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.core.models.elements import ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.utils import fs


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
        # find model type one level above if finishing with '.*'
        model_type = ElementPath(split_path.rstrip('.*')).get_type(type(model_obj))
        if model_type_is_too_granular(model_type):
            return True
    return False


def parse_element_args(
    model: Union[OscalBaseModel, None],
    element_args: List[str],
    relative_path: Optional[pathlib.Path] = None
) -> List[ElementPath]:
    """Parse element args into a list of ElementPath.

    The element paths are either simple links of two elements, or two elements followed by *.
    The * represents either a list of the items in that element, or a splitting of that element into its parts.
    The only parts split off are the non-trivial ones determined by the granularity check.

    contextual_mode specifies if the path is a valid project model path or not. For example,
    if we are processing a metadata.parties.*, we need to know which metadata we are processing. If we pass
    contextual_mode=true, we can infer the root model by inspecting the file directory

    If contextual_mode=False, then the path must include the full path, e.g. catalog.metadata.parties.* instead of just
    metadata.parties.*

    When the * represents splitting a model rather than a list, the model is inspected for what parts are available,
    and for each new part two element paths are created, one for the parent to the current element, and another from
    the current element to the child.

    A path may have multiple *'s, but only the final one can represent splitting a model.

    Args:
        model: The OscalBaseModel being inspected to determine available elements that can be split
        element_args: List of str representing links in the chain of element paths to be parsed
        relative_path: Optional relative path (from trestle root) used to validate element args are valid.
    Returns:
        The requested parsed list of ElementPath for use in split
    """
    # collect all paths
    element_paths: List[ElementPath] = []
    for element_arg in element_args:
        paths = parse_element_arg(model, element_arg, relative_path)
        element_paths.extend(paths)

    return element_paths


def parse_chain(
    model_obj: Union[OscalBaseModel, None],
    path_parts: List[str],
    relative_path: Optional[pathlib.Path] = None
) -> List[ElementPath]:
    """Parse the model chain starting from the beginning.

    Args:
        model_obj: Model to use for inspecting available elements, if available or none
        path_parts: list of string paths to parse including wildcards
        relative_path: Optional relative path (w.r.t trestle project root directory)

    Returns:
        List of ElementPath
    """
    element_paths: List[ElementPath] = []
    sub_model = model_obj
    have_model_to_parse = model_obj is not None

    prev_element_path = None
    latest_path = None
    parent_model = path_parts[0]
    i = 1
    while i < len(path_parts):
        p = path_parts[i]

        # if hit wildcard create element path up to this point
        if p == ElementPath.WILDCARD and len(element_paths) > 0:
            # append wildcard to the latest element path
            latest_path = element_paths.pop()
            if latest_path.get_last() == ElementPath.WILDCARD:
                raise TrestleError(f'Invalid element path with consecutive {ElementPath.WILDCARD}')

            latest_path_str = ElementPath.PATH_SEPARATOR.join([latest_path.to_string(), p])
            element_path = ElementPath(latest_path_str, latest_path.get_parent())
        else:
            # create and append element_path
            # at this point sub_model may be a list of items
            # new element path is needed only if any of the items contains the desired part
            if p != ElementPath.WILDCARD:
                new_attrib = utils.dash_to_underscore(p)
                if isinstance(sub_model, list):
                    for item in sub_model:
                        # go into the list and find one with requested part
                        sub_item = getattr(item, new_attrib, None)
                        if sub_item is not None:
                            sub_model = sub_item
                            break
                else:
                    sub_model = getattr(sub_model, new_attrib, None)
            if have_model_to_parse and sub_model is None:
                return element_paths
            p = ElementPath.PATH_SEPARATOR.join([parent_model, p])
            element_path = ElementPath(p, parent_path=prev_element_path)

        # If the path has wildcard and there are more parts later,
        # get the parent model for the alias path
        # If path has wildcard and it does not refer to a list, then there can be nothing after *
        if element_path.get_last() == ElementPath.WILDCARD:
            full_path_str = ElementPath.PATH_SEPARATOR.join(element_path.get_full_path_parts()[:-1])
            parent_model = fs.get_singular_alias(full_path_str, relative_path)
            # Does wildcard mean we need to inspect the sub_model to determine what can be split off from it?
            # If it has __root__ it may mean it contains a list of objects and should be split as a list
            if isinstance(sub_model, OscalBaseModel):
                root = getattr(sub_model, '__root__', None)
                if root is None or not isinstance(root, list):
                    # Cannot have parts beyond * if it isn't a list
                    if i < len(path_parts) - 1:
                        raise TrestleError(
                            f'Cannot split beyond * when the wildcard does not refer to a list.  Path: {path_parts}'
                        )
                    for key in sub_model.__fields__.keys():
                        # only create element path is item is present in the sub_model
                        if getattr(sub_model, key, None) is None:
                            continue
                        new_alias = utils.underscore_to_dash(key)
                        new_path = full_path_str + '.' + new_alias
                        if not split_is_too_fine(new_path, model_obj):
                            # to add parts of an element, need to add two links
                            # prev_element_path may be None, for example catalog.*
                            if prev_element_path is not None:
                                element_paths.append(prev_element_path)
                            element_paths.append(ElementPath(parent_model + '.' + new_alias, latest_path))
                    # Since wildcard is last in the chain when splitting an oscal model we are done
                    return element_paths
        else:
            parent_model = element_path.get_element_name()

        # store values for next cycle
        prev_element_path = element_path
        element_paths.append(element_path)
        i += 1
    return element_paths


def parse_element_arg(
    model_obj: Union[OscalBaseModel, None],
    element_arg: str,
    relative_path: Optional[pathlib.Path] = None
) -> List[ElementPath]:
    """Parse an element arg string into a list of ElementPath.

    Args:
        model_obj: The OscalBaseModel being inspected to determine available elements that can be split
        element_arg: Single element path, as a string.
        relative_path: Optional relative path (from trestle root) used to validate element args are valid.
    Returns:
        The requested parsed list of ElementPath for use in split
    """
    element_arg = element_arg.strip()

    if element_arg == '*':
        raise TrestleError('Invalid element path containing only a single wildcard.')

    if element_arg == '':
        raise TrestleError('Invalid element path is empty string.')

    # search for wildcards and create paths with its parent path
    path_parts = element_arg.split(ElementPath.PATH_SEPARATOR)
    if len(path_parts) <= 1:
        raise TrestleError(f'Invalid element path "{element_arg}" with only one element and no wildcard')

    element_paths = parse_chain(model_obj, path_parts, relative_path)

    if len(element_paths) <= 0:
        # don't complain if nothing to split
        pass

    return element_paths


def to_model_file_name(model_obj: OscalBaseModel, file_prefix: str, content_type: FileContentType) -> str:
    """Return the file name for the item."""
    file_ext = FileContentType.to_file_extension(content_type)
    model_type = utils.classname_to_alias(type(model_obj).__name__, 'json')
    file_name = f'{file_prefix}{const.IDX_SEP}{model_type}{file_ext}'
    return file_name
