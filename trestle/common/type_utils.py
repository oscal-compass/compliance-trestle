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
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import trestle.common.err as err

import typing_extensions

logger = logging.getLogger(__name__)


def get_origin(field_type: Type[Any]) -> Optional[Type[Any]]:
    """Generalized and robust get_origin function.

    This function is derived from work by pydantic, however, avoids complications
    from various python versions.
    """
    # This executes a fallback that allows a list to be generated from a constrained list.
    return typing_extensions.get_origin(field_type) or getattr(field_type, '__origin__', None)


def _get_model_field_info(field_type: Type[Any]) -> Tuple[Optional[Type[Any]], Optional[str], Optional[Type[Any]]]:
    """Need special handling for pydantic wrapped __root__ objects."""
    # oscal_read of roles.json yields pydantic.Roles model with __root__ containing list of Role
    root: Optional[Type[Any]] = None
    root_type: Optional[str] = None
    singular_type: Optional[Type[Any]] = None
    try:
        fields = field_type.__fields__
        root = fields['__root__']
        singular_type = root.type_
        root_type = root.outer_type_._name
    except Exception:  # noqa S110
        pass
    return root, root_type, singular_type


def is_collection_field_type(field_type: Type[Any]) -> bool:
    """Check whether a type hint is a collection type as used by OSCAL.

    Specifically this is whether the type is a list or not.

    Args:
        field_type: A type or a type alias of a field typically as served via pydantic introspection

    Returns:
        True if it is a collection type list.
    """
    # first check if it is a pydantic __root__ object
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
        return typing_extensions.get_args(collection_field_type)[-1]
    except Exception as e:
        logger.debug(e)
        raise err.TrestleError('Model type is not a Dict or List') from e
