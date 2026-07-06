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

import logging
import types
from typing import Any, Dict, List, Optional, Tuple, Type, Union, get_args, get_origin as typing_get_origin

import trestle.common.err as err
from pydantic import BaseModel
from pydantic.fields import FieldInfo

import typing_extensions

logger = logging.getLogger(__name__)


def is_union_type(origin: Any) -> bool:
    """Return True if *origin* is any form of Union (typing.Union or Python 3.10+ X | Y).

    Replaces the fragile string comparison ``str(origin) == "<class 'types.UnionType'>"``
    with identity checks that are not tied to CPython string internals.

    Background:
        - ``get_origin(Union[A, B])``  → ``typing.Union``  (the special form)
        - ``get_origin(A | B)``        → ``types.UnionType`` (the class, Python 3.10+)
    """
    if origin is Union:
        return True
    # types.UnionType is available on Python 3.10+; guard with hasattr for 3.9 compatibility.
    return origin is getattr(types, 'UnionType', None)


def get_origin(field_type: Type[Any]) -> Optional[Type[Any]]:
    """Generalized and robust get_origin function.

    This function is derived from work by pydantic, however, avoids complications
    from various python versions.
    """
    # This executes a fallback that allows a list to be generated from a constrained list.
    return typing_extensions.get_origin(field_type) or getattr(field_type, '__origin__', None)


def _unwrap_optional_type(singular_type: Type[Any]) -> Type[Any]:
    """Unwrap Optional[T] to get T."""
    origin = typing_get_origin(singular_type)
    if is_union_type(origin):
        union_args = [arg for arg in typing_extensions.get_args(singular_type) if arg is not type(None)]
        if len(union_args) == 1:
            return union_args[0]
    return singular_type


def _get_root_type_name(singular_type: Type[Any]) -> Optional[str]:
    """Return a sentinel string identifying the collection kind of *singular_type*.

    Returns 'List' when the type is a list (e.g. ``list[Role]``), 'Dict' when it
    is a dict, and ``None`` for non-generic or unrecognized types.

    Callers compare the return value against the string literals 'List' and 'Dict'
    to decide whether a RootModel wraps a collection.  Using identity checks on the
    origin rather than ``origin.__name__.capitalize()`` avoids relying on CPython's
    internal string representation of built-in types.
    """
    origin = typing_get_origin(singular_type)
    if origin is list:
        return 'List'
    if origin is dict:
        return 'Dict'
    if origin is not None:
        # Non-list/dict generic — not a collection kind we handle
        return None
    # For non-generic types, return the type name as-is (e.g. 'str', 'Role')
    return getattr(singular_type, '__name__', None)


def _extract_root_model_info(field_type: Type[Any]) -> Tuple[Optional[FieldInfo], Optional[str], Optional[Type[Any]]]:
    """Extract root model information from a BaseModel type."""
    model_fields = field_type.model_fields
    # Check for RootModel (has 'root' field)
    if 'root' not in model_fields:
        return None, None, None

    root_field = model_fields['root']
    singular_type = root_field.annotation
    # Unwrap Optional[T] to get T
    singular_type = _unwrap_optional_type(singular_type)
    root_type = _get_root_type_name(singular_type)

    return root_field, root_type, singular_type


def _get_model_field_info(field_type: Type[Any]) -> Tuple[Optional[FieldInfo], Optional[str], Optional[Type[Any]]]:
    """Need special handling for pydantic RootModel objects.

    In Pydantic v2, RootModel has a 'root' field instead of the v1 '__root__' field.
    """
    try:
        # Check if this is a BaseModel with model_fields
        if isinstance(field_type, type) and issubclass(field_type, BaseModel):
            return _extract_root_model_info(field_type)
    except Exception:  # noqa S110
        pass
    return None, None, None


def is_collection_field_type(field_type: Type[Any]) -> bool:
    """Check whether a type hint is a collection type as used by OSCAL.

    Specifically this is whether the type is a list or not.

    Args:
        field_type: A type or a type alias of a field typically as served via pydantic introspection

    Returns:
        True if it is a collection type list.
    """
    # first check if it is a pydantic root object (RootModel in v2)
    _, root_type, _ = _get_model_field_info(field_type)
    if root_type == 'List':
        return True

    origin_type = get_origin(field_type)
    if origin_type == list:
        return True

    # Optional[list[T]] / Union[list[T], None] in Pydantic v2 annotations
    if is_union_type(origin_type):
        union_args = [arg for arg in typing_extensions.get_args(field_type) if arg is not type(None)]
        return len(union_args) == 1 and is_collection_field_type(union_args[0])

    return False


def get_inner_type(collection_field_type: Union[Type[List[Any]], Type[Dict[str, Any]]]) -> Type[Any]:
    """Get the inner model in a generic collection model such as a List or a Dict.

    For a dict the return type is of the value and not the key.

    Args:
        collection_field_type: Provided type annotation from a pydantic object

    Returns:
        The desired type.
    """
    try:
        origin_type = get_origin(collection_field_type)
        if is_union_type(origin_type):
            union_args = [arg for arg in typing_extensions.get_args(collection_field_type) if arg is not type(None)]
            if len(union_args) == 1:
                return get_inner_type(union_args[0])

        # Pydantic RootModel special cases must only unwrap collection roots.
        _, root_type, singular_type = _get_model_field_info(collection_field_type)
        if root_type in ('List', 'Dict') and singular_type is not None:
            return get_inner_type(singular_type)

        # Get type arguments - try both typing_extensions and typing.get_args
        # In Python 3.9+, list[...] creates types.GenericAlias which needs typing.get_args
        args = typing_extensions.get_args(collection_field_type)
        if not args:
            # Try with standard typing.get_args for types.GenericAlias
            args = get_args(collection_field_type)

        # Handle bare list or dict types without type arguments (e.g., list instead of List[str])
        # But only if they come from type annotations, not runtime instances
        if not args:
            # Check if this is actually a type annotation (has __origin__ or is a typing construct)
            # vs a runtime instance type (which would just be 'list' or 'dict')
            if origin_type is list:
                return Any
            if origin_type is dict:
                return Any
            # If no origin_type and no args, this is likely a runtime instance type, not a type annotation
            raise err.TrestleError('Model type is not a Dict or List type annotation')

        return args[-1]
    except Exception as e:
        logger.debug(e)
        raise err.TrestleError('Model type is not a Dict or List') from e
