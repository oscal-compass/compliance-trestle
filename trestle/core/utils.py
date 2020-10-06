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
from types import ModuleType
from typing import Optional, Tuple

from datamodel_code_generator.parser.base import camel_to_snake

import pydantic

import trestle.core.const as const
from trestle.core.base_model import OscalBaseModel


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

    if isinstance(object_of_interest, pydantic.BaseModel):
        for field in object_of_interest.__fields_set__:
            if field == '__root__':
                continue
            loi.extend(get_elements_of_model_type(getattr(object_of_interest, field), type_of_interest))
    return loi


def get_contextual_path(path: str, contextual_path: list) -> list:
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
        contextual_path = get_contextual_path(p.parent, contextual_path)
    else:
        contextual_path.insert(0, str(path))
    return contextual_path


def get_cwm(contextual_path: list) -> ModuleType:
    """
    Get current working module based on the contextual path.

    If the directory the user is running the trestle command from is not a source folder of a model type, this function
    will not return anything. Otherwise, it will return the module representing the context.
    """
    if len(contextual_path) > 1:
        plural_model_type = contextual_path[1]
        model_type_module_name = const.MODELTYPE_TO_MODELMODULE[plural_model_type]
        module = importlib.import_module(model_type_module_name)
        return module


def get_root_model(module: ModuleType) -> (OscalBaseModel, str):
    """Get the root model class and alias based on the module."""
    model_metadata = next(iter(module.Model.__fields__.values()))
    return (model_metadata.type_, model_metadata.alias)


def get_contextual_model(contextual_path: list) -> Optional[Tuple[OscalBaseModel, str]]:
    """Get the contextual model class and alias based on the contextual path."""
    current_working_module = get_cwm(contextual_path)
    root_model, root_alias = get_root_model(current_working_module)

    current_model = root_model
    current_alias = root_alias

    if len(contextual_path) < 3:
        return None
    elif len(contextual_path) > 3:
        for index in range(3, len(contextual_path)):
            stripped_alias = contextual_path[index].split(sep=const.IDX_SEP)[-1]
            current_alias = stripped_alias

            # Find property by alias
            if is_collection_model(current_model):
                # Return the model class inside the collection
                current_model = get_inner_model(current_model)

            else:
                current_model = get_field_model_by_alias(current_model, current_alias)

            # If last index
            if index == len(contextual_path) - 1:
                return (current_model, current_alias)
    else:
        return (current_model, current_alias)


def is_collection_model(model) -> bool:
    """Check if model is of generic type for handling List or Dict."""
    if hasattr(model, '__origin__') and hasattr(model, '__args__'):
        return True
    return False


def get_inner_model(model) -> OscalBaseModel:
    """Get the inner model in a generic model such as a List or a Dict."""
    return model.__args__[-1]


def get_field_model_by_alias(model, alias) -> Optional[OscalBaseModel]:
    """Iterate through the fields of model and retrieve the one associated with the provided alias."""
    for field_value in model.__fields__.values():
        if field_value.alias == alias:
            return field_value.outer_type_
    return None


def get_singular_collection_model_alias(model) -> str:
    """Get the alias in the singular form of the collection model."""
    singular_model_class = get_inner_model(model)
    singular_model_name = singular_model_class.__name__
    return camel_to_snake(singular_model_name).replace('_', '-')
