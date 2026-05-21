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
from typing import Any, Dict, List, Optional, Tuple, Type, Union, get_args, get_origin as typing_get_origin

import trestle.common.err as err
from pydantic import BaseModel
from pydantic.fields import FieldInfo

import typing_extensions

logger = logging.getLogger(__name__)


def get_origin(field_type: Type[Any]) -> Optional[Type[Any]]:
    """Generalized and robust get_origin function.

    This function is derived from work by pydantic, however, avoids complications
    from various python versions.
    """
    # This executes a fallback that allows a list to be generated from a constrained list.
    return typing_extensions.get_origin(field_type) or getattr(field_type, '__origin__', None)


def _get_model_field_info(field_type: Type[Any]) -> Tuple[Optional[FieldInfo], Optional[str], Optional[Type[Any]]]:
    """Need special handling for pydantic RootModel objects.

    In Pydantic v2, RootModel has a 'root' field instead of the v1 '__root__' field.
    """
    root_field: Optional[FieldInfo] = None
    root_type: Optional[str] = None
    singular_type: Optional[Type[Any]] = None
    try:
        # Check if this is a BaseModel with model_fields
        if isinstance(field_type, type) and issubclass(field_type, BaseModel):
            model_fields = field_type.model_fields
            # Check for RootModel (has 'root' field)
            if 'root' in model_fields:
                root_field = model_fields['root']
                singular_type = root_field.annotation
                # Get the origin type name (e.g., 'list', 'dict')
                origin = typing_get_origin(singular_type)
                if origin is not None:
                    root_type = origin.__name__.capitalize()
                elif singular_type is not None:
                    # For non-generic types, get the type name
                    root_type = getattr(singular_type, '__name__', None)
    except Exception:  # noqa S110
        pass
    return root_field, root_type, singular_type


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
    # Retrieves type from a type annotation
    origin_type = get_origin(field_type)
    return origin_type == list


def get_inner_type(collection_field_type: Union[Type[List[Any]], Type[Dict[str, Any]]]) -> Type[Any]:
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

        origin_type = get_origin(collection_field_type)
        if str(origin_type) == "<class 'types.UnionType'>" or origin_type == Union:
            union_args = [arg for arg in typing_extensions.get_args(collection_field_type) if arg is not type(None)]
            if len(union_args) == 1:
                return get_inner_type(union_args[0])

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
                return Any  # type: ignore
            if origin_type is dict:
                return Any  # type: ignore
            # If no origin_type and no args, this is likely a runtime instance type, not a type annotation
            raise err.TrestleError('Model type is not a Dict or List type annotation')

        return args[-1]
    except Exception as e:
        logger.debug(e)
        raise err.TrestleError('Model type is not a Dict or List') from e
