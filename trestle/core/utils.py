# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utilities for dealing with models."""
import importlib
import warnings
from typing import Any, List, Tuple, Type, no_type_check

from datamodel_code_generator.parser.base import camel_to_snake

from pydantic import BaseModel

import trestle.core.const as const
import trestle.core.err as err


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
        return camel_to_dash(suffix)
    elif mode == 'field':
        return camel_to_snake(suffix)
    else:
        raise err.TrestleError('Bad option')


def camel_to_dash(name: str) -> str:
    """Convert camelcase to dashcase."""
    return camel_to_snake(name).replace('_', '-')


def pascal_case_split(pascal_str: str) -> List[str]:
    """Parse a pascal case string (e.g. a ClassName) and return a list of strings."""
    warnings.warn('trestle.utils.pascal_case_split function is deprecated', DeprecationWarning)
    start_idx = [i for i, e in enumerate(pascal_str) if e.isupper()] + [len(pascal_str)]
    return [pascal_str[x:y] for x, y in zip(start_idx, start_idx[1:])]


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
    else:
        raise err.TrestleError('Invalid module')


def is_collection_field_type(field_type) -> bool:
    """Check if model type is a generic collection model such as a typed list or a typed dict."""
    if hasattr(field_type, '__origin__') and hasattr(field_type, '__args__') and (list in field_type.mro()
                                                                                  or dict in field_type.mro()):
        return True

    return False


def get_inner_type(collection_field_type) -> Type[Any]:
    """Get the inner model in a generic collection model such as a List or a Dict."""
    if is_collection_field_type(collection_field_type):
        return collection_field_type.__args__[-1]
    else:
        raise err.TrestleError('Model type is not a Dict or List')


def get_singular_alias(alias_fullpath: str) -> str:
    """Get the alias in the singular form from a jsonpath."""
    singular_alias: str = ''

    path_parts = alias_fullpath.split(const.ALIAS_PATH_SEPARATOR)
    if len(path_parts) < 2:
        raise err.TrestleError('Invalid jsonpath.')

    model_types = []

    root_model_alias = path_parts[0]
    found = False
    for module_name in const.MODELTYPE_TO_MODELMODULE.values():
        model_type, model_alias = get_root_model(module_name)
        if root_model_alias == model_alias:
            found = True
            model_types.append(model_type)
            break

    if not found:
        raise err.TrestleError(f'{root_model_alias} is an invalid root model alias.')

    model_type = model_types[0]
    for i in range(1, len(path_parts)):
        if is_collection_field_type(model_type):
            model_type = get_inner_type(model_type)
            i = i + 1
        else:
            model_type = model_type.alias_to_field_map()[path_parts[i]].outer_type_
        model_types.append(model_type)

    if not is_collection_field_type(model_type):
        raise err.TrestleError('Not a valid generic collection model.')

    last_alias = path_parts[-1]
    parent_model_type = model_types[-2]
    singular_alias = classname_to_alias(
        get_inner_type(parent_model_type.alias_to_field_map()[last_alias].outer_type_).__name__, 'json'
    )

    return singular_alias


def get_cwm(contextual_path: list) -> str:
    """
    Get current working module name based on the contextual path.

    If the directory the user is running the trestle command from is not a source folder of a model type, this function
    will not return anything. Otherwise, it will return the module representing the context.
    """
    if len(contextual_path) > 1:
        plural_model_type = contextual_path[1]
        model_type_module_name = const.MODELTYPE_TO_MODELMODULE[plural_model_type]
        return model_type_module_name

    return ''
