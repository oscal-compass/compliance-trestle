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
"""Module to load distributed model."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleNotFoundError
from trestle.core.models.file_content_type import FileContentType
from trestle.utils import fs


def _load_list(abs_path: Path, abs_trestle_root: Path) -> Tuple[Type[OscalBaseModel], str, List[OscalBaseModel]]:
    """Given path to a directory of list(array) models, load the distributed models."""
    aliases_not_to_be_stripped = []
    instances_to_be_merged: List[OscalBaseModel] = []
    collection_model_type, collection_model_alias = fs.get_stripped_model_type(abs_path, abs_trestle_root)
    for path in sorted(fs.iterdir_without_hidden_files(abs_path)):

        # ASSUMPTION HERE: if it is a directory, there's a file that can not be decomposed further.
        if path.is_dir():
            continue
        _, model_alias, model_instance = load_distributed(path, abs_trestle_root)

        instances_to_be_merged.append(model_instance)
        aliases_not_to_be_stripped.append(model_alias.split('.')[-1])

    return collection_model_type, collection_model_alias, instances_to_be_merged


def _load_dict(abs_path: Path, abs_trestle_root: Path) -> Tuple[Type[OscalBaseModel], str, Dict[str, OscalBaseModel]]:
    """Given path to a directory of additionalProperty(dict) models, load the distributed models."""
    model_dict: Dict[str, OscalBaseModel] = {}
    collection_model_type, collection_model_alias = fs.get_stripped_model_type(abs_path, abs_trestle_root)
    for path in sorted(fs.iterdir_without_hidden_files(abs_path)):
        model_type, model_alias, model_instance = load_distributed(path, abs_trestle_root)
        field_name = path.parts[-1].split('__')[0].split('.')[0]
        model_dict[field_name] = model_instance

    return collection_model_type, collection_model_alias, model_dict


def load_distributed(
    abs_path: Path,
    abs_trestle_root: Path,
    collection_type: Optional[Type[Any]] = None
) -> Tuple[Type[OscalBaseModel], str, Union[OscalBaseModel, List[OscalBaseModel], Dict[str, OscalBaseModel]]]:
    """
    Given path to a model, load the model.

    If the model is decomposed/split/distributed,the decomposed models are loaded recursively.

    Args:
        abs_path: The path to the file/directory to be loaded.
        abs_trestle_root: The trestle project root directory.
        collection_type: The type of collection model, if it is a collection model.
            typing.List if the model is a list, typing.Dict if the model is additionalProperty.
            Defaults to None.

    Returns:
        Return a tuple of Model Type (e.g. class 'trestle.oscal.catalog.Catalog'), Model Alias (e.g. 'catalog.metadata')
        and Instance of the Model. If the model is decomposed/split/distributed, the instance of the model contains
        the decomposed models loaded recursively.
    """
    # if trying to load file that does not exist, load path instead
    if not abs_path.exists():
        abs_path = abs_path.with_name(abs_path.stem)

    if not abs_path.exists():
        raise TrestleNotFoundError(f'File {abs_path} not found for load.')

    # If the path contains a list type model
    if collection_type is list:
        return _load_list(abs_path, abs_trestle_root)

    # If the path contains a dict type model
    if collection_type is dict:
        return _load_dict(abs_path, abs_trestle_root)

    # Get current model
    primary_model_type, primary_model_alias = fs.get_stripped_model_type(abs_path, abs_trestle_root)
    primary_model_instance: OscalBaseModel = None

    # is this an attempt to load an actual json or yaml file?
    content_type = FileContentType.path_to_content_type(abs_path)
    # if file is sought but it doesn't exist, ignore and load as decomposed model
    if FileContentType.is_readable_file(content_type) and abs_path.exists():
        primary_model_instance = primary_model_type.oscal_read(abs_path)
    # Is model decomposed?
    decomposed_dir = abs_path.with_name(abs_path.stem)

    if decomposed_dir.exists():
        aliases_not_to_be_stripped = []
        instances_to_be_merged: List[OscalBaseModel] = []

        for local_path in sorted(fs.iterdir_without_hidden_files(decomposed_dir)):
            if local_path.is_file():
                model_type, model_alias, model_instance = load_distributed(local_path, abs_trestle_root)
                aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
                instances_to_be_merged.append(model_instance)

            elif local_path.is_dir():
                model_type, model_alias = fs.get_stripped_model_type(local_path, abs_trestle_root)
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
                    model_type, model_alias, model_instance = load_distributed(local_path, abs_trestle_root,
                                                                               collection_type)
                    aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
                    instances_to_be_merged.append(model_instance)
        primary_model_dict = {}
        if primary_model_instance is not None:
            primary_model_dict = primary_model_instance.__dict__

        merged_model_type, merged_model_alias = fs.get_stripped_model_type(abs_path, abs_trestle_root,
                                                                           aliases_not_to_be_stripped)

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
    return primary_model_type, primary_model_alias, primary_model_instance
