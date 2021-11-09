# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utilities for dealing with models."""
import importlib
import logging
import string
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union, no_type_check

from pydantic import BaseModel

import trestle.core.err as err

import typing_extensions

logger = logging.getLogger(__name__)

# Generic typevar
TG = TypeVar('TG')


def camel_to_snake(camel: str) -> str:
    """Convert camel case to snake."""
    if not camel:
        return camel
    snake = camel[0].lower()
    for c in camel[1:]:
        if c.isupper():
            snake = snake + '_'
        snake = snake + c.lower()
    return snake


def snake_to_upper_camel(snake: str) -> str:
    """Convert snake to upper camel, ignoring start/end underscores."""
    if not snake:
        return snake
    snake = snake.lower()
    camel = ''
    lift = True
    for s in snake:
        if s == '_':
            lift = True
            continue
        if lift:
            camel = camel + s.upper()
            lift = False
        else:
            camel = camel + s
    return camel


def spaces_and_caps_to_snake(spaced_str: str) -> str:
    """Convert caps and spaces to snake."""
    underscored = spaced_str.strip().replace(' ', '_')
    return underscored.lower()


def get_elements_of_model_type(object_of_interest, type_of_interest):
    """
    Return a flat list of a given type of pydantic object based on a presumed encompasing root object.

    One warning. This object preserves the underlying object tree. So when you use this function do NOT recurse on the
    results or you will end up with duplication errors.
    """
    loi = []
    if type(object_of_interest) == type_of_interest:
        loi.append(object_of_interest)
        # keep going
    if type(object_of_interest) is list:
        for item in object_of_interest:
            loi.extend(get_elements_of_model_type(item, type_of_interest))

    if isinstance(object_of_interest, BaseModel):
        for field in object_of_interest.__fields_set__:
            if field == '__root__':
                continue
            loi.extend(get_elements_of_model_type(getattr(object_of_interest, field), type_of_interest))
    return loi


def classname_to_alias(classname: str, mode: str) -> str:
    """
    Return oscal key name or field element name based on class name.

    This is applicable when asking for a singular element.
    """
    suffix = classname.split('.')[-1]

    if mode == 'json':
        # things like class_ should just be class
        if suffix[-1] == '_':
            suffix = suffix[:-1]
        return camel_to_dash(suffix).rstrip(string.digits)
    if mode == 'field':
        return camel_to_snake(suffix).rstrip(string.digits)
    raise err.TrestleError('Bad option')


def alias_to_classname(alias: str, mode: str) -> str:
    """
    Return class name based dashed or snake alias.

    This is applicable creating dynamic wrapper model for a list or dict field.
    """
    if mode == 'json':
        return snake_to_upper_camel(alias.replace('-', '_'))
    if mode == 'field':
        return snake_to_upper_camel(alias)
    raise err.TrestleError('Bad option')


def camel_to_dash(name: str) -> str:
    """Convert camelcase to dashcase."""
    return camel_to_snake(name).replace('_', '-')


def dash_to_underscore(name: str) -> str:
    """Convert dash to underscore."""
    return name.replace('-', '_')


def underscore_to_dash(name: str) -> str:
    """Convert underscore to dash and drop final dash if present."""
    converted = name.replace('_', '-')
    return converted if converted[-1] != '-' else converted[:-1]


@no_type_check
def get_root_model(module_name: str) -> Tuple[Type[Any], str]:
    """Get the root model class and alias based on the module."""
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        raise err.TrestleError(str(e))

    if hasattr(module, 'Model'):
        model_metadata = next(iter(module.Model.__fields__.values()))
        return (model_metadata.type_, model_metadata.alias)
    raise err.TrestleError('Invalid module')


def get_origin(field_type: Type[Any]) -> Optional[Type[Any]]:
    """Generalized and robust get_origin function.

    This function is derived from work by pydantic, however, avoids complications
    from various python versions.
    """
    # This executes a fallback that allows a list to be generated from a constrained list.
    return typing_extensions.get_origin(field_type) or getattr(field_type, '__origin__', None)


def _get_model_field_info(field_type: Type[Any]) -> Union[Type[Any], str, Type[Any]]:
    """Need special handling for pydantic wrapped __root__ objects."""
    # oscal_read of roles.json yields pydantic.Roles model with __root__ containing list of Role
    root: Type[Any] = None
    root_type: str = None
    singular_type: Type[Any] = None
    try:
        fields = field_type.__fields__
        root = fields['__root__']
        singular_type = root.type_
        root_type = root.outer_type_._name
    except Exception:  # noqa S110
        pass
    return root, root_type, singular_type


# FIXME: Typing issues here
# FIXME: This method has diverged significantly from expectations:


def is_collection_field_type(field_type: Type[Any]) -> bool:
    """Check whether a type hint is a collection type as used by OSCAL.

    Specifically this is whether the type is a list or string.

    Args:
        field_type: A type or a type alias of a field typically as served via pydantic introspection

    Returns:
        Status if if it is a list or dict return type as used by oscal.
    """
    # first check if it is a pydantic __root__ object
    _, root_type, _ = _get_model_field_info(field_type)
    if root_type is not None:
        return root_type in ['List', 'Dict']
    # Retrieves type from a type annotation
    origin_type = get_origin(field_type)
    # dict in fact may not be possible
    return origin_type in [list, dict]


# Type annotation is incorrect.
def get_inner_type(collection_field_type: Union[Type[List[TG]], Type[Dict[str, TG]]]) -> Type[TG]:
    """Get the inner model in a generic collection model such as a List or a Dict.

    For a dict the return type is of the value and not the key.

    Args:
        collection_field_type: Provided type annotation from a pydantic object

    Returns:
        The desired type.
    """
    try:
        # Pydantic special cases must be dealt with here:
        _, _, singular_type = _get_model_field_info(collection_field_type)
        if singular_type is not None:
            return singular_type
        return typing_extensions.get_args(collection_field_type)[-1]
    except Exception as e:
        logger.debug(e)
        raise err.TrestleError('Model type is not a Dict or List') from e


def as_list(list_or_none: Optional[List[Any]]) -> List[Any]:
    """Convert list or None object to itself or an empty list if none."""
    return list_or_none if list_or_none else []


def none_if_empty(list_: List[Any]) -> Optional[List[Any]]:
    """Convert to None if empty list."""
    return list_ if list_ else None
