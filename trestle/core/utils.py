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
from pathlib import Path
from typing import List, Tuple, no_type_check

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


def class_to_oscal(class_name: str, mode: str) -> str:
    """
    Return oscal json or field element name based on class name.

    This is applicable when asking for a singular element.
    """
    parts = pascal_case_split(class_name)
    if mode == 'json':
        return '-'.join(map(str.lower, parts))
    elif mode == 'field':
        return '_'.join(map(str.lower, parts))
    else:
        raise err.TrestleError('Bad option')


def pascal_case_split(pascal_str: str) -> List[str]:
    """Parse a pascal case string (e.g. a ClassName) and return a list of strings."""
    start_idx = [i for i, e in enumerate(pascal_str) if e.isupper()] + [len(pascal_str)]
    return [pascal_str[x:y] for x, y in zip(start_idx, start_idx[1:])]


def is_collection_model(model) -> bool:
    """Check if model is of generic type for handling List or Dict."""
    if hasattr(model, '__origin__') and hasattr(model, '__args__'):
        return True
    return False


def get_inner_model(collection_model) -> BaseModel:
    """Get the inner model in a generic model such as a List or a Dict."""
    if is_collection_model(collection_model):
        return collection_model.__args__[-1]
    else:
        raise err.TrestleError('Model type is not a Dict or List')


def get_singular_alias_from_collection_model(model) -> str:
    """Get the alias in the singular form of the collection model."""
    singular_model_class = get_inner_model(model)
    if isinstance(singular_model_class, type):
        singular_model_name = singular_model_class.__name__
    else:
        raise err.TrestleError('Cannot retrieve name of inner class')
    return camel_to_dash(singular_model_name)


def camel_to_dash(name: str) -> str:
    """Convert camelcase to dashcase."""
    return camel_to_snake(name).replace('_', '-')


@no_type_check
def get_root_model(module_name: str) -> Tuple[BaseModel, str]:
    """Get the root model class and alias based on the module."""
    module = importlib.import_module(module_name)
    if hasattr(module, 'Model'):
        model_metadata = next(iter(module.Model.__fields__.values()))
        return (model_metadata.type_, model_metadata.alias)
    else:
        raise err.TrestleError('Invalid module')


def get_contextual_path(path: str, contextual_path: List[str]) -> List[str]:
    """
    Return the contextual path relative to where the nearest .trestle directory is.

    If a .trestle directory is found, it breaks down the path starting with the path of the directory that contains the
    .trestle directory, followed by a subsequent list of items, each representing a sub-directory leading to the
    directory path that was passed it.
    This function allows the user to figure out the depth he/she is running a trestle command from in a trestle project
    as well as the type of model (by looking at the value stored in index 1 of the list) the command should be
    referring to.
    """
    p = Path(path)
    if p.name == '':
        return []
    config_dir = p / const.TRESTLE_CONFIG_DIR
    if not config_dir.is_dir():
        contextual_path.insert(0, p.name)
        contextual_path = get_contextual_path(str(p.parent), contextual_path)
    else:
        contextual_path.insert(0, str(path))
    return contextual_path


def get_contextual_model(contextual_path: list = None) -> Tuple[BaseModel, str]:
    """Get the contextual model class and alias based on the contextual path."""
    if contextual_path is None:
        contextual_path = []
        contextual_path = get_contextual_path(str(Path.cwd()), contextual_path)

    current_working_module_name = get_cwm(contextual_path)
    root_model, root_alias = get_root_model(current_working_module_name)

    current_model = root_model
    current_alias = root_alias

    if len(contextual_path) < 3:
        raise err.TrestleError('Not in a source directory of a model type')
    elif len(contextual_path) > 3:
        for index in range(3, len(contextual_path)):
            stripped_alias = contextual_path[index].split(sep=const.IDX_SEP)[-1]
            current_alias = stripped_alias

            # Find property by alias
            if is_collection_model(current_model):
                # Return the model class inside the collection
                current_model = get_inner_model(current_model)

            else:
                current_model = current_model.get_fields_by_alias()[current_alias].outer_type_

        return (current_model, current_alias)
    else:
        return (current_model, current_alias)


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
