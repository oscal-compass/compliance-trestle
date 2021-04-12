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
"""Module to load distributed model."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from trestle.core.base_model import OscalBaseModel
from trestle.core.models.file_content_type import FileContentType
from trestle.utils import fs


def _load_list(filepath: Path) -> Tuple[Type[OscalBaseModel], str, List[OscalBaseModel]]:
    """Given path to a directory of list(array) models, load the distributed models."""
    aliases_not_to_be_stripped = []
    instances_to_be_merged: List[OscalBaseModel] = []
    # TODO: FIXME: fs.get_stripped_contextual_model fails without absolute file path!!! FIX IT!!
    collection_model_type, collection_model_alias = fs.get_stripped_contextual_model(filepath.resolve())

    for path in sorted(Path.iterdir(filepath)):

        # ASSUMPTION HERE: if it is a directory, there's a file that can not be decomposed further.
        if path.is_dir():
            continue
        model_type, model_alias, model_instance = load_distributed(path)

        instances_to_be_merged.append(model_instance)
        aliases_not_to_be_stripped.append(model_alias.split('.')[-1])

    return collection_model_type, collection_model_alias, instances_to_be_merged


def _load_dict(filepath: Path) -> Tuple[Type[OscalBaseModel], str, Dict[str, OscalBaseModel]]:
    """Given path to a directory of additionalProperty(dict) models, load the distributed models."""
    model_dict: Dict[str, OscalBaseModel] = {}
    collection_model_type, collection_model_alias = fs.get_stripped_contextual_model(filepath.resolve())
    for path in sorted(Path.iterdir(filepath)):
        model_type, model_alias, model_instance = load_distributed(path)
        field_name = path.parts[-1].split('__')[0]
        model_dict[field_name] = model_instance

    return collection_model_type, collection_model_alias, model_dict


def load_distributed(
    file_path: Path,
    collection_type: Optional[Type[Any]] = None
) -> Tuple[Type[OscalBaseModel], str, Union[OscalBaseModel, List[OscalBaseModel], Dict[str, OscalBaseModel]]]:
    """
    Given path to a model, load the model.

    If the model is decomposed/split/distributed,the decomposed models are loaded recursively.

    Args:
        file_path (pathlib.Path): The path to the file/directory to be loaded.
        collection_type (Type[Any], optional): The type of collection model, if it is a collection model.
            typing.List if the model is a list, typing.Dict if the model is additionalProperty.
            Defaults to None.

    Returns:
        Tuple[Type[OscalBaseModel], str, Union[OscalBaseModel, List[OscalBaseModel], Dict[str, OscalBaseModel]]]: Return
            a tuple of Model Type (e.g. class 'trestle.oscal.catalog.Catalog'), Model Alias (e.g. 'catalog.metadata'),
            and Instance of the Model. If the model is decomposed/split/distributed, the instance of the model contains
            the decomposed models loaded recursively.
    """
    # if trying to load file that does not exist, load path instead
    if not file_path.exists():
        file_path = file_path.with_name(file_path.stem)

    # If the path contains a list type model
    if collection_type is list:
        return _load_list(file_path)

    # If the path contains a dict type model
    if collection_type is dict:
        return _load_dict(file_path)

    # Get current model
    primary_model_type, primary_model_alias = fs.get_stripped_contextual_model(file_path.resolve())
    primary_model_instance: Type[OscalBaseModel] = None

    # is this an attempt to load an actual json or yaml file?
    content_type = FileContentType.path_to_content_type(file_path)
    # if file is sought but it doesn't exist, ignore and load as decomposed model
    if FileContentType.is_readable_file(content_type) and file_path.exists():
        primary_model_instance = primary_model_type.oscal_read(file_path)
    # Is model decomposed?
    decomposed_dir = file_path.with_name(file_path.stem)

    if decomposed_dir.exists():
        aliases_not_to_be_stripped = []
        instances_to_be_merged: List[OscalBaseModel] = []

        for path in sorted(Path.iterdir(decomposed_dir)):

            if path.is_file():
                model_type, model_alias, model_instance = load_distributed(path)
                aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
                instances_to_be_merged.append(model_instance)

            elif path.is_dir():
                model_type, model_alias = fs.get_stripped_contextual_model(path.resolve())
                # Only load the directory if it is a collection model. Otherwise do nothing - it gets loaded when
                # iterating over the model file

                # If a model is just a container for a list e.g.
                # class Foo(OscalBaseModel):  noqa: E800
                #      __root__: List[Bar]    noqa: E800
                # You need to test whether first a root key exists
                # then whether the outer_type of root is a collection.
                # Alternative is to do a try except to avoid the error for an unknown key.

                if model_type.is_collection_container():
                    # This directory is a decomposed List or Dict
                    collection_type = model_type.get_collection_type()
                    model_type, model_alias, model_instance = load_distributed(path, collection_type)
                    aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
                    instances_to_be_merged.append(model_instance)
        primary_model_dict = {}
        if primary_model_instance is not None:
            primary_model_dict = primary_model_instance.__dict__

        merged_model_type, merged_model_alias = fs.get_stripped_contextual_model(
            file_path.resolve(), aliases_not_to_be_stripped)

        # The following use of top_level is to allow loading of a top level model by name only, e.g. MyCatalog
        # There may be a better overall way to approach this.
        top_level = len(merged_model_alias.split('.')) == 1

        for i in range(len(aliases_not_to_be_stripped)):
            alias = aliases_not_to_be_stripped[i]
            instance = instances_to_be_merged[i]
            if hasattr(instance, '__dict__') and '__root__' in instance.__dict__ and isinstance(instance,
                                                                                                OscalBaseModel):
                instance = instance.__dict__['__root__']
            if top_level and not primary_model_dict:
                primary_model_dict = instance.__dict__
            else:
                primary_model_dict[alias] = instance

        merged_model_instance = merged_model_type(**primary_model_dict)  # type: ignore
        return merged_model_type, merged_model_alias, merged_model_instance

    else:
        return primary_model_type, primary_model_alias, primary_model_instance
