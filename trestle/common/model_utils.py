# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2022 IBM Corp. All rights reserved.
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
"""Common utilities for the OSCAL models and directories."""

import importlib
import json
import logging
import pathlib
import re
import types
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union, get_args, get_origin

from ruamel.yaml import YAML

from pydantic import BaseModel, ConfigDict, RootModel, create_model

import trestle.common
import trestle.common.common_types
from trestle.common import const, err, list_utils, str_utils, type_utils as utils
from trestle.common.common_types import TG, TopLevelOscalModel
from trestle.common.err import TrestleError, TrestleNotFoundError
from trestle.common.file_utils import extract_trestle_project_root, iterdir_without_hidden_files
from trestle.common.list_utils import as_filtered_list, none_if_empty
from trestle.common.str_utils import AliasMode, alias_to_classname
from trestle.core.base_model import OscalBaseModel
from trestle.core.models.file_content_type import FileContentType
from trestle.core.remote import cache
from trestle.oscal import assessment_plan, assessment_results, common, poam

logger = logging.getLogger(__name__)


def _get_model_type_from_union(model_type: Type[Any], field_name: Optional[str] = None) -> Type[Any]:
    """
    If model_type is a Union, return the appropriate concrete type.

    For Union types like Union[Group1, Group2], if field_name is provided,
    we check which variant has that field and return it.

    Note: For OSCAL 1.2.0 Union types (Group1|Group2, Parameter1|Parameter2),
    the generated models have smart validators that inspect the data at
    deserialization time to choose the correct variant. This function is
    mainly for type resolution in non-deserialization contexts.

    Args:
        model_type: The model type, which may be a Union
        field_name: Optional field name to check for in Union variants

    Returns:
        A concrete model type (not a Union)
    """
    origin = get_origin(model_type)
    # Handle both Union[A, B] and A | B syntax (types.UnionType in Python 3.10+)
    if origin is Union or (hasattr(types, 'UnionType') and origin is types.UnionType):
        union_args = get_args(model_type)
        logger.debug(f'Union type detected: {union_args}, looking for field: {field_name}')

        # If we have a field name, first prefer a Union variant whose own alias matches.
        if field_name:
            for union_type in union_args:
                if isinstance(union_type, type) and issubclass(union_type, OscalBaseModel):
                    try:
                        if str_utils.classname_to_alias(union_type.__name__, AliasMode.JSON) == field_name:
                            logger.debug(f'Found alias {field_name} matching union variant {union_type}')
                            return union_type
                    except Exception as e:
                        logger.debug(f'Union type {union_type} alias resolution failed: {e}')
                        continue

            # Otherwise, find the Union variant that has that field
            for union_type in union_args:
                if hasattr(union_type, 'alias_to_field_map'):
                    try:
                        field_map = union_type.alias_to_field_map()
                        if field_name in field_map:
                            logger.debug(f'Found field {field_name} in {union_type}')
                            return union_type
                    except Exception as e:
                        logger.debug(f'Union type {union_type} does not have alias_to_field_map: {e}')
                        continue

        # Fallback: return the first type that has alias_to_field_map
        # The smart validators in the generated models will handle choosing
        # the correct variant at deserialization time
        for union_type in union_args:
            if hasattr(union_type, 'alias_to_field_map'):
                logger.debug(f'Using {union_type} from Union (no field match)')
                return union_type

        # Last resort: return the first non-list type
        # Skip list types as they don't have model methods
        for union_type in union_args:
            origin = get_origin(union_type)
            if origin not in (list, List):
                logger.debug(f'No suitable type found in Union, using first non-list: {union_type}')
                return union_type

        # If all types are lists, return the first one (shouldn't happen in practice)
        logger.warning(f'All Union types are lists, using first: {union_args[0]}')
        return union_args[0]
    return model_type


def _pluralized_alias_to_singular(alias: str) -> str:
    """Convert a pluralized JSON field alias to its singular form.

    This is a last-resort fallback used only for OSCAL collection fields whose inner
    type is not an OscalBaseModel subclass (e.g. plain strings, UUIDs, enums).
    It covers every such field present in the OSCAL 1.x schemas using standard
    American English pluralization rules:

    Known OSCAL fields that reach this path:
      'props'                       -> 'property'   (irregular)
      'addr-lines', 'role-ids', ... -> strip trailing 's'
      'email-addresses'             -> strip trailing 's'
      'functions-performed'         -> strip trailing 's' (no plural suffix variant)
      (no '-ies' endings appear in current OSCAL schemas, but the rule is kept for safety)

    Assumption: OSCAL field aliases follow American English pluralization. If new fields
    are added that violate this assumption, this function must be updated explicitly.
    """
    if alias == 'props':
        return 'property'
    if alias.endswith('ies'):
        return alias[:-3] + 'y'
    if alias.endswith('s'):
        return alias[:-1]
    return alias


def _resolve_collection_item_alias(parent_model_type: Type[Any], field_alias: str, alias_path: str) -> str:
    """Resolve the singular alias for a collection item field."""
    try:
        if not (isinstance(parent_model_type, type) and issubclass(parent_model_type, OscalBaseModel)):
            raise err.TrestleError(f'Unable to resolve parent model type for alias {field_alias}')

        field_map = parent_model_type.alias_to_field_map()
        if field_alias not in field_map:
            return str_utils.classname_to_alias(parent_model_type.__name__, AliasMode.JSON)

        field = field_map[field_alias]
        outer_type = field.annotation

        if utils.is_collection_field_type(outer_type):
            inner_type = utils.get_inner_type(outer_type)
            # For Union types, just pick the first variant — they all share the same base alias.
            # e.g., Group1 and Group2 both become 'group' after stripping the trailing digit.
            inner_type = _get_model_type_from_union(inner_type, None)
            if isinstance(inner_type, type) and issubclass(inner_type, OscalBaseModel):
                return str_utils.classname_to_alias(inner_type.__name__, AliasMode.JSON)

        singular_type = _get_model_type_from_union(outer_type, field_alias)
        if isinstance(singular_type, type) and issubclass(singular_type, OscalBaseModel):
            return str_utils.classname_to_alias(singular_type.__name__, AliasMode.JSON)

        # Last resort: the field holds a collection of plain scalars (strings, UUIDs, enums).
        # Use English pluralization rules to derive the singular alias.
        return _pluralized_alias_to_singular(field_alias)
    except Exception as e:
        raise err.TrestleError(f'Error in json path {alias_path}: {e}') from e


class ModelUtils:
    """Utilities for the OSCAL models input and output."""

    @staticmethod
    def _get_primary_model_instance(
        primary_model_type: Type[Any], abs_path: pathlib.Path
    ) -> OscalBaseModel | List[OscalBaseModel] | Dict[str, OscalBaseModel] | Any | None:
        """
        Load primary model instance from file, handling both OscalBaseModel and Pydantic built-in types.

        Args:
            primary_model_type: The model type to load
            abs_path: Path to the file to load

        Returns:
            The loaded model instance, or None if file doesn't exist or can't be loaded
        """
        # Check if primary_model_type has oscal_read (is OscalBaseModel or RootModel)
        # Pydantic built-in types like AwareDatetime don't have oscal_read
        if hasattr(primary_model_type, 'oscal_read'):
            # Use the model type as-is (may be wrapped Union) for reading
            # The smart validators in generated models will choose the correct variant
            primary_model_instance = primary_model_type.oscal_read(abs_path)
            # If the instance has root (Pydantic v2 RootModel), unwrap it to get the actual model
            if hasattr(primary_model_instance, 'root'):
                root_val = primary_model_instance.root
                # Only unwrap if it's a single OscalBaseModel, not a list
                if isinstance(root_val, OscalBaseModel):
                    return root_val
            return primary_model_instance
        else:
            # For Pydantic built-in types (e.g., AwareDatetime), read the JSON/YAML file directly
            # Split files store fields as {"field-name": value}, so extract just the value
            content_type = FileContentType.path_to_content_type(abs_path)
            data = None
            if content_type == FileContentType.JSON:
                with abs_path.open('r', encoding='utf8') as f:
                    data = json.load(f)
            elif content_type == FileContentType.YAML:
                _yaml = YAML(typ='safe')
                with abs_path.open('r', encoding='utf8') as f:
                    data = _yaml.load(f)

            # Split files for simple fields are stored as {"field-name": value}
            # Extract just the value for Pydantic built-in types
            if isinstance(data, dict) and len(data) == 1:
                return next(iter(data.values()))
            return data

    @staticmethod
    def load_distributed(
        abs_path: Path, abs_trestle_root: Path, collection_type: Optional[Type[Any]] = None
    ) -> Tuple[
        Type[OscalBaseModel], str, Optional[Union[OscalBaseModel, List[OscalBaseModel], Dict[str, OscalBaseModel]]]
    ]:
        """
        Given path to a model, load the model.

        If the model is decomposed/split/distributed,the decomposed models are loaded recursively.

        Args:
            abs_path: The path to the file/directory to be loaded.
            abs_trestle_root: The trestle workspace root directory.
            collection_type: The type of collection model, if it is a collection model.
                typing.List is the only collection type handled or expected.
                Defaults to None.

        Returns:
            Return a tuple of Model Type (e.g. class 'trestle.oscal.catalog.Catalog'),
            Model Alias (e.g. 'catalog.metadata') and Instance of the Model.
            If the model is decomposed/split/distributed, the instance of the model contains
                the decomposed models loaded recursively.

        Note:
            This does not validate the model.  You must either validate the model separately or use the load_validate
            utilities.
        """
        # if trying to load file that does not exist, load path instead
        if not abs_path.exists():
            abs_path = abs_path.with_name(abs_path.stem)

        if not abs_path.exists():
            raise TrestleNotFoundError(f'File {abs_path} not found for load.')

        if collection_type:
            # If the path contains a list type model
            if collection_type is list:
                return ModelUtils._load_list(abs_path, abs_trestle_root)
            # the only other collection type in OSCAL is dict, and it only applies to include_all,
            # which is too granular ever to be loaded by this routine
            else:
                raise TrestleError(f'Collection type {collection_type} not recognized for distributed load.')

        # Get current model
        primary_model_type, primary_model_alias = ModelUtils.get_stripped_model_type(abs_path, abs_trestle_root)
        primary_model_instance: Optional[Union[OscalBaseModel, List[OscalBaseModel], Dict[str, OscalBaseModel]]] = None

        # is this an attempt to load an actual json or yaml file?
        content_type = FileContentType.path_to_content_type(abs_path)
        # if file is sought but it doesn't exist, ignore and load as decomposed model
        if FileContentType.is_readable_file(content_type) and abs_path.exists():
            primary_model_instance = ModelUtils._get_primary_model_instance(primary_model_type, abs_path)
        # Is model decomposed?
        decomposed_dir = abs_path.with_name(abs_path.stem)

        if decomposed_dir.exists():
            aliases_not_to_be_stripped = []
            instances_to_be_merged: List[OscalBaseModel] = []

            for local_path in sorted(trestle.common.file_utils.iterdir_without_hidden_files(decomposed_dir)):
                if local_path.is_file():
                    model_type, model_alias, model_instance = ModelUtils.load_distributed(local_path, abs_trestle_root)
                    aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
                    instances_to_be_merged.append(model_instance)

                elif local_path.is_dir():
                    model_type, model_alias = ModelUtils.get_stripped_model_type(local_path, abs_trestle_root)
                    # Only load the directory if it is a collection model. Otherwise do nothing - it gets loaded when
                    # iterating over the model file

                    # If a model is just a container for a list e.g.
                    # class Foo(OscalBaseModel):  noqa: E800
                    #      root: List[Bar]    noqa: E800  # Pydantic v2 RootModel
                    # You need to test whether first a root key exists
                    # then whether the outer_type of root is a collection.
                    # Alternative is to do a try except to avoid the error for an unknown key.

                    # Check if model_type is a collection type (either a RootModel container or a raw list/dict)
                    collection_type = None

                    # Check if it's a raw list or dict type (e.g., list[Control], dict[str, Role])
                    origin = get_origin(model_type)
                    if origin is list:
                        collection_type = list
                    elif origin is dict:
                        collection_type = dict
                    # Check if it's a RootModel (dynamically created wrapper)
                    elif isinstance(model_type, type) and issubclass(model_type, RootModel):
                        # Check the root field's type to determine collection type
                        if hasattr(model_type, 'model_fields') and 'root' in model_type.model_fields:
                            root_field = model_type.model_fields['root']
                            root_origin = get_origin(root_field.annotation)
                            if root_origin is list:
                                collection_type = list
                            elif root_origin is dict:
                                collection_type = dict
                    # Check if it's a BaseModel with collection container
                    elif isinstance(model_type, type) and issubclass(model_type, OscalBaseModel):
                        if model_type.is_collection_container():
                            collection_type = model_type.get_collection_type()

                    if collection_type is not None:
                        # This directory is a decomposed List or Dict
                        model_type, model_alias, model_instance = ModelUtils.load_distributed(
                            local_path, abs_trestle_root, collection_type
                        )
                        aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
                        instances_to_be_merged.append(model_instance)
            primary_model_dict = {}
            if primary_model_instance is not None:
                primary_model_dict = primary_model_instance.__dict__

            merged_model_type, merged_model_alias = ModelUtils.get_stripped_model_type(
                abs_path, abs_trestle_root, aliases_not_to_be_stripped
            )

            # The following use of top_level is to allow loading of a top level model by name only, e.g. MyCatalog
            # There may be a better overall way to approach this.
            top_level = len(merged_model_alias.split('.')) == 1

            for i in range(len(aliases_not_to_be_stripped)):
                alias = aliases_not_to_be_stripped[i]
                instance = instances_to_be_merged[i]
                # Unwrap RootModel instances to get the actual data
                # Check for RootModel (dynamically created wrappers) OR OscalBaseModel with root field
                if (
                    hasattr(instance, '__dict__')
                    and 'root' in instance.__dict__
                    and (isinstance(instance, (OscalBaseModel, RootModel)))
                ):
                    instance = instance.__dict__['root']
                # For top-level models, merge the instance's dict into primary_model_dict
                # But only if instance is an OscalBaseModel with __dict__
                if top_level and not primary_model_dict:
                    if hasattr(instance, '__dict__'):
                        primary_model_dict = instance.__dict__
                    else:
                        # If instance is not a model (e.g., a list or primitive), we can't use it as top-level
                        # This shouldn't happen in normal usage, but handle it gracefully
                        primary_model_dict[alias] = instance
                else:
                    primary_model_dict[alias] = instance

            # If merged_model_type is a wrapped Union (has 'root' field in RootModel), we need to unwrap it
            # to get the actual model type for instantiation
            actual_model_type = merged_model_type
            if hasattr(merged_model_type, 'model_fields') and 'root' in merged_model_type.model_fields:
                # This is a RootModel with Union - extract the Union type from 'root'
                root_field = merged_model_type.model_fields['root']
                root_type = root_field.annotation
                # Inspect primary_model_dict to determine which Union variant to use
                # Look for distinctive fields that indicate which variant
                # For Group1|Group2: 'groups' -> Group1, 'controls' -> Group2
                # For Parameter1|Parameter2: 'values' -> Parameter1, 'select' -> Parameter2
                field_hint = None
                distinctive_fields = ['controls', 'groups', 'values', 'select', 'insert-controls']
                for key in primary_model_dict.keys():
                    if key in distinctive_fields:
                        field_hint = key
                        break
                # If no distinctive field found, use any field
                if field_hint is None and primary_model_dict:
                    field_hint = next(iter(primary_model_dict.keys()))
                # Resolve the Union to get an actual model type based on the data
                actual_model_type = _get_model_type_from_union(root_type, field_hint)

            merged_model_instance = actual_model_type(**primary_model_dict)
            return merged_model_type, merged_model_alias, merged_model_instance
        return primary_model_type, primary_model_alias, primary_model_instance

    @staticmethod
    def load_model_for_class(
        trestle_root: pathlib.Path,
        model_name: str,
        model_class: TG,
        file_content_type: Optional[FileContentType] = None,
    ) -> Tuple[TG, pathlib.Path]:
        """Load a model by name and model class and infer file content type if not specified.

        If you need to load an existing model but its content type may not be known, use this method.
        But the file content type should be specified if it is somehow known.

        Note:
            This does not validate the model.  If you want to validate the model use the load_validate utilities.
        """
        root_model_path = ModelUtils._root_path_for_top_level_model(trestle_root, model_name, model_class)  # type: ignore
        if file_content_type is None:
            file_content_type = FileContentType.path_to_content_type(root_model_path)
        if not FileContentType.is_readable_file(file_content_type):
            raise TrestleError(f'Unable to load model {model_name} without specifying json or yaml.')
        full_model_path = root_model_path.with_suffix(FileContentType.to_file_extension(file_content_type))
        _, _, model = ModelUtils.load_distributed(full_model_path, trestle_root)
        return model, full_model_path  # type: ignore

    @staticmethod
    def load_model_for_type(
        trestle_root: pathlib.Path, model_type: str, model_name: str
    ) -> Tuple[TopLevelOscalModel, pathlib.Path]:
        """Load model for the given type and name."""
        dir_name = ModelUtils.model_type_to_model_dir(model_type)
        model_path = trestle_root / dir_name / model_name

        if not model_path.exists():
            raise TrestleError(f'No model is found at path: {model_path}.')

        _, _, oscal_object = ModelUtils.load_distributed(model_path, trestle_root)

        return oscal_object, model_path  # type: ignore

    @staticmethod
    def save_top_level_model(
        model: TopLevelOscalModel, trestle_root: pathlib.Path, model_name: str, file_content_type: FileContentType
    ) -> None:
        """Save a model by name and infer model type by inspection.

        You don't need to specify the model type (catalog, profile, etc.) but you must specify the file content type.
        If the model directory does not exist, it is created.
        """
        root_model_path = ModelUtils._root_path_for_top_level_model(trestle_root, model_name, model)
        full_model_path = root_model_path.with_suffix(FileContentType.to_file_extension(file_content_type))
        if not full_model_path.parent.exists():
            full_model_path.parent.mkdir(parents=True, exist_ok=True)
        model.oscal_write(full_model_path)

    @staticmethod
    def _is_union_type(model_type: Type[Any]) -> bool:
        """Check if a type is a Union type."""
        origin = get_origin(model_type)
        return origin is Union or (hasattr(types, 'UnionType') and origin is types.UnionType)

    @staticmethod
    def _handle_collection_field(model_type: Type[Any], alias: str, full_alias: str) -> Type[Any]:
        """Handle collection field type resolution."""
        inner_model = utils.get_inner_type(model_type)
        is_union = ModelUtils._is_union_type(inner_model)

        if alias.isdigit():
            # For numeric indices, keep Union types as-is for deserialization
            return inner_model if is_union else _get_model_type_from_union(inner_model, alias)

        # Try to match alias against Union variants
        resolved_inner_model = _get_model_type_from_union(inner_model, alias)
        if ModelUtils._is_matching_variant(resolved_inner_model, alias):
            # If alias matches a variant's class name, keep the Union for deserialization
            return inner_model if is_union else resolved_inner_model

        # Filesystem item paths use the singular collection alias
        singular_alias = ModelUtils.get_singular_alias(full_alias.rsplit('.', 1)[0])
        if alias == singular_alias:
            # Keep Union type for file paths that match the singular alias
            return inner_model if is_union else resolved_inner_model

        raise TrestleError(f'Model type {model_type} has no collection item for alias {alias}')

    @staticmethod
    def _is_matching_variant(resolved_model: Type[Any], alias: str) -> bool:
        """Check if resolved model matches the alias as a variant."""
        return (
            isinstance(resolved_model, type)
            and issubclass(resolved_model, OscalBaseModel)
            and alias == str_utils.classname_to_alias(resolved_model.__name__, AliasMode.JSON)
        )

    @staticmethod
    def _handle_non_collection_field(model_type: Type[Any], alias: str) -> Type[Any]:
        """Handle non-collection field type resolution."""
        resolved_model = _get_model_type_from_union(model_type, alias)
        if not (isinstance(resolved_model, type) and issubclass(resolved_model, OscalBaseModel)):
            raise TrestleError(f'Model type {model_type} does not support alias_to_field_map for alias {alias}')

        field_map = resolved_model.alias_to_field_map()
        if alias in field_map:
            return field_map[alias].annotation

        if alias == str_utils.classname_to_alias(resolved_model.__name__, AliasMode.JSON):
            return resolved_model

        raise TrestleError(f'Model type {model_type} does not support alias_to_field_map for alias {alias}')

    @staticmethod
    def _normalize_optional_type(model_type: Type[Any]) -> Type[Any]:
        """Normalize Optional[T] to T for terminal return values."""
        if not ModelUtils._is_union_type(model_type):
            return model_type

        args = get_args(model_type)
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            return non_none_args[0]

        return model_type

    @staticmethod
    def _validate_and_get_module(relative_path: pathlib.Path) -> Tuple[str, pathlib.Path]:
        """Validate path and get module name and relative path."""
        if len(relative_path.parts) < 2:
            raise TrestleError(
                'Insufficient path length to be a valid relative path w.r.t trestle workspace root directory.'
            )

        model_dir = relative_path.parts[0]
        model_relative_path = pathlib.Path(*relative_path.parts[2:])

        if model_dir not in const.MODEL_DIR_LIST:
            raise TrestleError(f'No valid trestle model type directory (e.g. catalogs) found for {model_dir}.')

        module_name = const.MODEL_DIR_TO_MODEL_MODULE[model_dir]
        return module_name, model_relative_path

    @staticmethod
    def get_relative_model_type(relative_path: pathlib.Path) -> Tuple[Type[OscalBaseModel], str]:
        """
        Given the relative path of a file with respect to 'trestle_root' return the oscal model type.

        Args:
            relative_path: Relative path of the model with respect to the root directory of the trestle workspace.
        Returns:
            Type of Oscal Model for the provided model
            Alias of that oscal model.
        """
        module_name, model_relative_path = ModelUtils._validate_and_get_module(relative_path)
        model_type, model_alias = ModelUtils.get_root_model(module_name)
        full_alias = model_alias

        for index, part in enumerate(model_relative_path.parts):
            alias = ModelUtils._extract_alias(part)
            if index > 0 or model_alias != alias:
                model_alias = alias
                full_alias = f'{full_alias}.{model_alias}'

                if utils.is_collection_field_type(model_type):
                    model_type = ModelUtils._handle_collection_field(model_type, alias, full_alias)
                else:
                    model_type = ModelUtils._handle_non_collection_field(model_type, alias)

        return ModelUtils._normalize_optional_type(model_type), full_alias

    @staticmethod
    def get_stripped_model_type(
        absolute_path: pathlib.Path, absolute_trestle_root: pathlib.Path, aliases_not_to_be_stripped: List[str] = None
    ) -> Tuple[Type[OscalBaseModel], str]:
        """
        Get the stripped contextual model class and alias based on the contextual path.

        This function relies on the directory structure of the trestle model being edited to determine, based on the
        existing files and folder, which fields should be stripped from the model type represented by the
        path passed in as a parameter.
        """
        if aliases_not_to_be_stripped is None:
            aliases_not_to_be_stripped = []
        singular_model_type, model_alias = ModelUtils.get_relative_model_type(
            absolute_path.relative_to(absolute_trestle_root)
        )
        logger.debug(f'singular model type {singular_model_type} model alias {model_alias}')

        # Stripped models do not apply to collection types such as List[] and Dict{}
        # if model type is a list or dict, generate a new wrapping model for it
        if utils.is_collection_field_type(singular_model_type):
            malias = model_alias.split('.')[-1]
            class_name = alias_to_classname(malias, AliasMode.JSON)
            logger.debug(f'collection field type class name {class_name} and alias {malias}')
            # In Pydantic v2, must use RootModel instead of v1's __root__ field
            # Create RootModel[singular_model_type] dynamically
            # We need to use type() to create the class dynamically with proper generic parameter
            from typing import get_args as typing_get_args

            # Create a RootModel subclass for the collection type
            # Use OscalRootModel which provides all necessary methods including stripped_instance
            from trestle.core.base_model import OscalRootModel

            class DynamicRootModel(OscalRootModel):
                root: singular_model_type  # type: ignore

            DynamicRootModel.__name__ = class_name
            DynamicRootModel.__qualname__ = class_name
            model_type = DynamicRootModel
            logger.debug(f'model_type created: {model_type}')
            return model_type, model_alias

        malias = model_alias.split('.')[-1]
        logger.debug(f'not collection field type, malias: {malias}')

        # Check if this is a Union type FIRST, before stripping logic
        origin = get_origin(singular_model_type)
        is_union = origin is Union or (hasattr(types, 'UnionType') and origin is types.UnionType)

        if absolute_path.is_dir() and malias != ModelUtils._extract_alias(absolute_path.name):
            split_subdir = absolute_path / malias
        else:
            split_subdir = absolute_path.parent / absolute_path.with_suffix('').name

        aliases_to_be_stripped = set()
        if split_subdir.exists():
            for f in iterdir_without_hidden_files(split_subdir):
                alias = ModelUtils._extract_alias(f.name)
                if alias not in aliases_not_to_be_stripped:
                    aliases_to_be_stripped.add(alias)

        logger.debug(f'aliases to be stripped: {aliases_to_be_stripped}')

        # For Union types, use subdirectories to SELECT variant, not strip fields
        if is_union and len(aliases_to_be_stripped) > 0:
            union_args = [arg for arg in get_args(singular_model_type) if isinstance(arg, type)]
            stripped_aliases = set(aliases_to_be_stripped)
            selected_model_type = singular_model_type
            selected_strip_aliases = list(aliases_to_be_stripped)
            best_match_size = -1

            for union_arg in union_args:
                if not issubclass(union_arg, OscalBaseModel):
                    continue
                field_aliases = set(union_arg.alias_to_field_map().keys())
                match_size = len(stripped_aliases.intersection(field_aliases))
                if match_size == 0:
                    continue
                if match_size > best_match_size or (
                    match_size == best_match_size
                    and len(field_aliases.symmetric_difference(stripped_aliases)) < 1_000_000
                ):
                    best_match_size = match_size
                    selected_model_type = union_arg
                    selected_strip_aliases = [alias for alias in aliases_to_be_stripped if alias in field_aliases]

            if isinstance(selected_model_type, type) and issubclass(selected_model_type, OscalBaseModel):
                model_type = selected_model_type.create_stripped_model_type(
                    stripped_fields_aliases=selected_strip_aliases
                )
                logger.debug(f'model_type: {model_type}')
                return model_type, model_alias
            logger.warning(f'Resolved Union type {selected_model_type} is not an OscalBaseModel, cannot strip fields')
            return selected_model_type, model_alias
        elif len(aliases_to_be_stripped) > 0:
            # Non-Union type: normal stripping logic
            # Ensure it's a model class before calling create_stripped_model_type
            if isinstance(singular_model_type, type) and issubclass(singular_model_type, OscalBaseModel):
                model_type = singular_model_type.create_stripped_model_type(
                    stripped_fields_aliases=list(aliases_to_be_stripped)
                )
                logger.debug(f'model_type: {model_type}')
                return model_type, model_alias
            else:
                logger.warning(f'Model type {singular_model_type} is not an OscalBaseModel, cannot strip fields')
                return singular_model_type, model_alias
        # Handle Union types even when no stripping is needed
        origin = get_origin(singular_model_type)
        if origin is Union or (hasattr(types, 'UnionType') and origin is types.UnionType):
            # Check if there are subdirectories that indicate which variant to use
            # If absolute_path is a directory, look inside it; otherwise look in parent
            if absolute_path.is_dir():
                split_subdir = absolute_path
            else:
                split_subdir = absolute_path.parent / absolute_path.with_suffix('').name
            field_hint = None
            if split_subdir.exists() and split_subdir.is_dir():
                # Check what subdirectories exist to determine which Union variant
                for item in split_subdir.iterdir():
                    if item.is_dir():
                        # Use the subdirectory name as a hint for which field exists
                        # controls -> catalog Group2, insert-controls -> profile Group2, groups -> Group1
                        field_hint = item.name
                        logger.debug(f'Using subdirectory {field_hint} to select Union variant')
                        break

            # If we have a field hint from subdirectories, resolve to specific variant
            # Otherwise, wrap the Union for file reading (smart validators will choose)
            if field_hint:
                singular_model_type = _get_model_type_from_union(singular_model_type, field_hint)
            else:
                # No subdirectory hint - wrap Union for reading
                # This allows smart validators to choose the correct variant at deserialization time
                malias = model_alias.split('.')[-1]
                class_name = alias_to_classname(malias, AliasMode.JSON)
                logger.debug(f'Wrapping Union type {singular_model_type} in RootModel')

                # In Pydantic v2, must use RootModel instead of v1's __root__ field
                class DynamicRootModel(RootModel):  # type: ignore
                    root: singular_model_type  # type: ignore

                    # RootModel doesn't support extra='forbid', so we create a custom config
                    model_config = ConfigDict(populate_by_name=True, validate_assignment=True)

                    @classmethod
                    def oscal_read(cls, path: pathlib.Path):
                        """Read from OSCAL JSON/YAML file."""
                        return OscalBaseModel.oscal_read.__func__(cls, path)

                    def oscal_write(self, path: pathlib.Path):
                        """Write to OSCAL JSON/YAML file."""
                        return OscalBaseModel.oscal_write(self, path)

                    @classmethod
                    def alias_to_field_map(cls):
                        """Get alias to field mapping."""
                        return OscalBaseModel.alias_to_field_map.__func__(cls)

                DynamicRootModel.__name__ = class_name
                DynamicRootModel.__qualname__ = class_name
                model_type = DynamicRootModel
                return model_type, model_alias
        else:
            singular_model_type = _get_model_type_from_union(singular_model_type)
        return singular_model_type, model_alias

    @staticmethod
    def model_type_to_model_dir(model_type: str) -> str:
        """Get plural model directory from model type."""
        if model_type not in const.MODEL_TYPE_LIST:
            raise err.TrestleError(f'Not a valid model type: {model_type}.')
        return const.MODEL_TYPE_TO_MODEL_DIR[model_type]

    @staticmethod
    def get_models_of_type(model_type: str, root: pathlib.Path) -> List[str]:
        """Get list of model names for requested type in trestle directory."""
        if model_type not in const.MODEL_TYPE_LIST:
            raise err.TrestleError(f'Model type {model_type} is not supported')
        # search relative to project root
        trestle_root = extract_trestle_project_root(root)
        if not trestle_root:
            logger.error(f'Given directory {root} is not within a trestle project.')
            raise err.TrestleError('Given directory is not within a trestle project.')

        # contruct path to the model file name
        model_dir_name = ModelUtils.model_type_to_model_dir(model_type)
        root_model_dir = trestle_root / model_dir_name
        model_list = []
        for f in root_model_dir.glob('*/'):
            # Use the full directory name; Path.stem would incorrectly strip dotted model names.
            if not ModelUtils._should_ignore(f.name):
                if not f.is_dir():
                    logger.warning(
                        f'Ignoring validation of misplaced file {f.name} '
                        + f'found in the model directory, {model_dir_name}.'
                    )
                else:
                    model_list.append(f.name)
        return model_list

    @staticmethod
    def get_all_models(root: pathlib.Path) -> List[Tuple[str, str]]:
        """Get list of all models in trestle directory as tuples (model_type, model_name)."""
        full_list = []
        for model_type in const.MODEL_TYPE_LIST:
            models = ModelUtils.get_models_of_type(model_type, root)
            for m in models:
                full_list.append((model_type, m))
        return full_list

    @staticmethod
    def get_model_path_for_name_and_class(
        trestle_root: pathlib.Path,
        model_name: str,
        model_class: Type[TopLevelOscalModel],
        file_content_type: Optional[FileContentType] = None,
    ) -> Optional[pathlib.Path]:
        """
        Find the full path of a model given its name, model type and file content type.

        If file_content_type is given it will not inspect the file system or confirm the needed path and file exists.
        """
        if file_content_type is None:
            root_model_path = ModelUtils._root_path_for_top_level_model(trestle_root, model_name, model_class)
            file_content_type = FileContentType.path_to_content_type(root_model_path)
            if not FileContentType.is_readable_file(file_content_type):
                return None

            return root_model_path.with_suffix(FileContentType.to_file_extension(file_content_type))

        root_path = ModelUtils._root_path_for_top_level_model(trestle_root, model_name, model_class)
        return root_path.with_suffix(FileContentType.to_file_extension(file_content_type))

    @staticmethod
    def get_singular_alias(alias_path: str, relative_path: Optional[pathlib.Path] = None) -> str:
        """
        Get the alias in the singular form from a jsonpath.

        If contextual_mode is True and contextual_path is None, it assumes alias_path
        is relative to the directory the user is running trestle from.

        Args:
            alias_path: The current alias element path as a string
            relative_path: Optional relative path (w.r.t. trestle_root) to cater for relative element paths.
        Returns:
            Alias as a string
        """
        if len(alias_path.strip()) == 0:
            raise err.TrestleError(f'Invalid jsonpath {alias_path}')

        singular_alias: str = ''

        full_alias_path = alias_path
        if relative_path:
            logger.debug(f'get_singular_alias contextual mode: {str}')
            _, full_model_alias = ModelUtils.get_relative_model_type(relative_path)
            first_alias_a = full_model_alias.split('.')[-1]
            first_alias_b = alias_path.split('.')[0]
            if first_alias_a == first_alias_b:
                full_model_alias = '.'.join(full_model_alias.split('.')[:-1])
            full_alias_path = '.'.join([full_model_alias, alias_path]).strip('.')

        path_parts = full_alias_path.split(const.ALIAS_PATH_SEPARATOR)
        logger.debug(f'path parts: {path_parts}')

        model_types = []

        root_model_alias = path_parts[0]
        found = False
        for module_name in const.MODEL_TYPE_TO_MODEL_MODULE.values():
            model_type, model_alias = ModelUtils.get_root_model(module_name)
            if root_model_alias == model_alias:
                found = True
                model_types.append(model_type)
                break

        if not found:
            raise err.TrestleError(f'{root_model_alias} is an invalid root model alias.')

        if len(path_parts) == 1:
            return root_model_alias

        model_type = model_types[0]
        # go through path parts skipping first one
        for i in range(1, len(path_parts)):
            path_part = path_parts[i]

            if utils.is_collection_field_type(model_type):
                if i == len(path_parts) - 1 and path_part == '*':
                    break

                inner_model = utils.get_inner_type(model_type)
                if path_part == '*' or path_part.isdigit():
                    # Look ahead to next path segment to help resolve Union types
                    next_segment = path_parts[i + 1] if i + 1 < len(path_parts) else None
                    model_type = _get_model_type_from_union(inner_model, next_segment)
                    model_types.append(model_type)
                    continue

                # Check if inner_model is a Union - if so, look ahead to determine which variant
                origin = get_origin(inner_model)
                is_union = origin is Union or (hasattr(types, 'UnionType') and origin is types.UnionType)

                if is_union:
                    # Look ahead to next segment to resolve Union
                    next_segment = path_parts[i + 1] if i + 1 < len(path_parts) else None
                    resolved_inner_model = _get_model_type_from_union(inner_model, next_segment)
                else:
                    resolved_inner_model = _get_model_type_from_union(inner_model, path_part)

                if isinstance(resolved_inner_model, type) and issubclass(resolved_inner_model, OscalBaseModel):
                    expected_alias = str_utils.classname_to_alias(resolved_inner_model.__name__, AliasMode.JSON)
                    if path_part == expected_alias:
                        model_type = resolved_inner_model
                        model_types.append(model_type)
                        continue

            if isinstance(model_type, type) and issubclass(model_type, OscalBaseModel):
                field_map = model_type.alias_to_field_map()
                if path_part in field_map:
                    model_type = field_map[path_part].annotation
                    model_types.append(model_type)
                    continue

            model_type = _get_model_type_from_union(model_type, path_part)

            if utils.is_collection_field_type(model_type) and path_part != '*':
                model_types.append(model_type)
                continue

            if path_part == '*':
                model_types.append(model_type)
                continue

            if isinstance(model_type, type) and issubclass(model_type, OscalBaseModel):
                expected_alias = str_utils.classname_to_alias(model_type.__name__, AliasMode.JSON)
                if path_part == expected_alias:
                    model_types.append(model_type)

        original_last_alias = path_parts[-1]
        last_alias = original_last_alias

        if last_alias == '*':
            if len(path_parts) >= 2:
                collection_alias = path_parts[-2]
                if len(model_types) >= 2:
                    parent_model_type = model_types[-2]
                    if isinstance(parent_model_type, type) and issubclass(parent_model_type, OscalBaseModel):
                        return _resolve_collection_item_alias(parent_model_type, collection_alias, alias_path)
            last_alias = path_parts[-2]

        # Terminal numeric indexes (e.g. "component-definition.components.0") refer to an item in the
        # preceding collection; resolve to that item's alias.
        if original_last_alias.isdigit():
            if len(path_parts) < 2:
                raise err.TrestleError(f'Error in json path {alias_path}: unable to resolve indexed collection alias')
            indexed_collection_alias = path_parts[-2]
            if len(model_types) < 3:
                raise err.TrestleError(f'Error in json path {alias_path}: unable to resolve indexed collection alias')
            parent_model_type = model_types[-3]
            return _resolve_collection_item_alias(parent_model_type, indexed_collection_alias, alias_path)

        # A terminal wildcard refers to the item type of the preceding collection field.
        if original_last_alias == '*':
            if len(path_parts) < 2 or len(model_types) < 2:
                raise err.TrestleError(f'Error in json path {alias_path}: unable to resolve terminal wildcard alias')
            collection_alias = path_parts[-2]
            if len(model_types) < 3:
                parent_model_type = model_types[-2]
                if isinstance(parent_model_type, type) and issubclass(parent_model_type, OscalBaseModel):
                    return _resolve_collection_item_alias(parent_model_type, collection_alias, alias_path)
                raise err.TrestleError(f'Error in json path {alias_path}: unable to resolve terminal wildcard alias')
            parent_model_type = model_types[-3]
            return _resolve_collection_item_alias(parent_model_type, collection_alias, alias_path)

        if (
            original_last_alias == 'control-implementations'
            and len(path_parts) >= 2
            and not path_parts[-2].isdigit()
            and path_parts[-2] != '*'
        ):
            return original_last_alias

        # Paths ending in ".*.<field>" should resolve the field from the wildcard item type.
        if len(path_parts) >= 2 and path_parts[-2] == '*':
            wildcard_item_type = None
            for candidate in reversed(model_types[:-1]):
                if isinstance(candidate, type) and issubclass(candidate, OscalBaseModel):
                    wildcard_item_type = candidate
                    break
            if wildcard_item_type is None:
                raise err.TrestleError(f'Error in json path {alias_path}: unable to resolve wildcard collection alias')
            return _resolve_collection_item_alias(wildcard_item_type, last_alias, alias_path)

        # If the terminal segment resolves to a collection field, return the collection item alias
        # defined by the parent model structure rather than the collection field alias itself.
        if utils.is_collection_field_type(model_type):
            parent_model_type = model_types[-2]
            return _resolve_collection_item_alias(parent_model_type, last_alias, alias_path)
        # generic model and not list, so return itself fixme doc
        if not utils.is_collection_field_type(model_type):
            if len(model_types) >= 2:
                parent_model_type = model_types[-2]
                try:
                    field_map = parent_model_type.alias_to_field_map()
                    if last_alias in field_map:
                        field_annotation = field_map[last_alias].annotation
                        if utils.is_collection_field_type(field_annotation):
                            return _resolve_collection_item_alias(parent_model_type, last_alias, alias_path)
                except Exception:
                    pass
            return _pluralized_alias_to_singular(last_alias)

        parent_model_type = model_types[-2]
        singular_alias = _resolve_collection_item_alias(parent_model_type, last_alias, alias_path)

        return singular_alias

    @staticmethod
    def get_root_model(module_name: str) -> Tuple[Type[Any], str]:
        """Get the root model class and alias based on the module."""
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as e:
            raise err.TrestleError(str(e))

        if hasattr(module, 'Model'):
            model_field_name, model_metadata = next(iter(module.Model.model_fields.items()))
            model_alias = model_metadata.alias or str_utils.underscore_to_dash(model_field_name)
            return model_metadata.annotation, model_alias
        raise err.TrestleError('Invalid module')

    @staticmethod
    def _root_path_for_top_level_model(
        trestle_root: pathlib.Path, model_name: str, model_class: Union[TopLevelOscalModel, Type[TopLevelOscalModel]]
    ) -> pathlib.Path:
        """
        Find the root path to a model given its name and class - with no suffix.

        This is a private method used only to construct the root filepath based on model name and type.
        It does not check for existence or content type and it does not create the directory if it does not exist.
        """
        if not hasattr(model_class, '__module__') or model_class.__module__ not in const.MODEL_MODULE_LIST:
            raise TrestleError(f'Unable to determine model type for model {model_name} with class {model_class}')
        model_alias = const.MODEL_MODULE_TO_MODEL_TYPE[model_class.__module__]
        model_dir = trestle_root / f'{const.MODEL_TYPE_TO_MODEL_DIR[model_alias]}/{model_name}'
        return model_dir / model_alias

    @staticmethod
    def _extract_alias(string_dir: str) -> str:
        """
        Extract alias from filename or directory name removing extensions and prefixes related to dict and list.

        As we need to do this for multiple parts of a path operating on strings is easier.
        """
        alias = string_dir.split('.')[0].split(const.IDX_SEP)[
            -1
        ]  # get suffix of file or directory name representing list or dict item
        return alias

    @staticmethod
    def _should_ignore(name: str) -> bool:
        """Check if the file or directory should be ignored or not."""
        return name[0] == '.' or name[0] == '_'

    @staticmethod
    def _load_list(abs_path: Path, abs_trestle_root: Path) -> Tuple[Type[OscalBaseModel], str, List[OscalBaseModel]]:
        """Given path to a directory of list(array) models, load the distributed models."""
        aliases_not_to_be_stripped = []
        instances_to_be_merged: List[OscalBaseModel] = []
        collection_model_type, collection_model_alias = ModelUtils.get_stripped_model_type(abs_path, abs_trestle_root)
        for path in sorted(trestle.common.file_utils.iterdir_without_hidden_files(abs_path)):
            # For directories in a list, we need to check if there's a corresponding file
            # If not, load the directory itself as a decomposed model
            if path.is_dir():
                # Check if there's a file with the same base name
                file_path = path.parent / f'{path.name}.json'
                if not file_path.exists():
                    file_path = path.parent / f'{path.name}.yaml'
                if not file_path.exists():
                    file_path = path.parent / f'{path.name}.yml'
                if file_path.exists():
                    # There's a file, skip the directory (it will be loaded when we process the file)
                    continue
                # No file found, this directory contains the decomposed model
                _, model_alias, model_instance = ModelUtils.load_distributed(path, abs_trestle_root)
            else:
                _, model_alias, model_instance = ModelUtils.load_distributed(path, abs_trestle_root)

            instances_to_be_merged.append(model_instance)
            aliases_not_to_be_stripped.append(model_alias.split('.')[-1])

        return collection_model_type, collection_model_alias, instances_to_be_merged

    @staticmethod
    def _parameter_to_dict_recurse(obj: Union[OscalBaseModel, str], partial: bool) -> Union[str, Dict[str, Any]]:
        """
        Convert obj to dict containing only string values with recursion.

        Args:
            obj: The parameter or its consituent parts in recursive calls
            partial: Whether to convert the entire param or just the parts needed for markdown header

        Returns:
            The converted parameter as dictionary
        """
        main_fields = ['id', 'label', 'values', 'select', 'choice', 'how_many', 'guidelines', 'prose']
        if isinstance(obj, common.Remarks):
            return obj.root
        if isinstance(obj, common.HowMany):
            return obj.value
        # it is either a string already or we cast it to string
        if not hasattr(obj, const.FIELDS_SET):
            return str(obj)
        # it is an oscal object and we need to recurse within its attributes
        res = {}
        # Pydantic v2: __fields_set__ → model_fields_set
        for field in obj.model_fields_set:
            if partial and field not in main_fields:
                continue
            attr = getattr(obj, field)
            if not attr:
                continue
            if isinstance(attr, list):
                new_list = []
                for item in attr:
                    new_list.append(ModelUtils._parameter_to_dict_recurse(item, partial))
                res[field] = new_list
            elif isinstance(attr, str):
                res[field] = attr
            else:
                res[field] = ModelUtils._parameter_to_dict_recurse(attr, partial)
        return res

    @staticmethod
    def parameter_to_dict(obj: Union[OscalBaseModel, str], partial: bool) -> Union[str, Dict[str, Any]]:
        """
        Convert obj to dict containing only string values, storing only the fields that have values set.

        Args:
            obj: The parameter or its consituent parts in recursive calls
            partial: Whether to convert the entire param or just the parts needed for markdown header

        Returns:
            The converted parameter as dictionary, with values as None if not present for Parameter1
        """
        res = ModelUtils._parameter_to_dict_recurse(obj, partial)
        # Only add values: None for Parameter1 (which doesn't have select)
        # Parameter2 has select and should not have values field
        if 'values' not in res and 'select' not in res:
            res['values'] = None  # type: ignore
        return res

    @staticmethod
    def _string_to_howmany(count_str: str) -> Optional[str]:
        clean_str = count_str.lower().strip().replace('-', ' ').replace('_', ' ')
        if clean_str == const.ONE:
            return common.HowMany.one  # type: ignore
        if clean_str == const.ONE_OR_MORE_SPACED:
            return common.HowMany.one_or_more  # type: ignore
        return None

    @staticmethod
    def dict_to_parameter(param_dict: Dict[str, Any]) -> common.Parameter:
        """
        Convert dict with only string values to Parameter with handling for HowMany and with validity checks.

        Args:
            param_dict: Dictionary of pure string values representing Parameter contents

        Returns:
            A valid OSCAL Parameter

        Notes:
            This handles both partial and full parameter dictionaries
            It checks for validity of the values if a select and HowMany is specified
            There is special handling for values: If it is a single string it is converted to list of one ParameterValue
            But if it is a list of strings is regarded as a list of values and is converted to a list of ParameterValues
        """
        values = param_dict.get('values', [])
        # special handling when only one value present - convert to list of 1
        if isinstance(values, str):
            values = [values]
            param_dict['values'] = values
        if 'select' in param_dict and 'how_many' in param_dict['select']:
            count_str = param_dict['select']['how_many']
            how_many = ModelUtils._string_to_howmany(count_str)
            if how_many is None:
                raise TrestleError(f'Unrecognized HowMany value {how_many} in Parameter: should be one-or-more or one.')
            param_dict['select']['how_many'] = how_many
            if how_many == const.ONE and len(values) > 1:
                logger.warning(f'Parameter specifies HowMany=1 but has {len(values)} values given.')
            choices = param_dict['select'].get('choice', [])
            if choices and values:
                for value in values:
                    if value not in choices:
                        logger.warning(f'Parameter {param_dict["id"]} has value "{value}" not in choices: {choices}.')
        props = param_dict.get('props', [])
        if const.DISPLAY_NAME in param_dict:
            display_name = param_dict.pop(const.DISPLAY_NAME)
            props.append(common.Property(name=const.DISPLAY_NAME, value=display_name, ns=const.TRESTLE_GENERIC_NS))
        if const.AGGREGATES in param_dict:
            # removing aggregates as this is prop just informative in markdown
            param_dict.pop(const.AGGREGATES)
        param_value_origin = None
        if const.PARAM_VALUE_ORIGIN in param_dict:
            param_value_origin = param_dict.pop(const.PARAM_VALUE_ORIGIN)
            if param_value_origin is not None:
                props.append(common.Property(name=const.PARAM_VALUE_ORIGIN, value=param_value_origin))
            else:
                raise TrestleError(
                    f'Parameter value origin property for parameter {param_dict["id"]}'
                    'is None and it should have a value'
                )
        if const.ALT_IDENTIFIER in param_dict:
            # removing alt-identifier as this is prop just informative in markdown
            param_dict.pop(const.ALT_IDENTIFIER)

        if 'ns' in param_dict:
            param_dict.pop('ns')

        # Choose Parameter1 (with values) or Parameter2 (with select) based on which field is present
        # Remove the field that doesn't belong to the chosen variant
        if 'select' in param_dict and param_dict.get('select') is not None:
            # Creating Parameter2 - remove values if present
            param_dict.pop('values', None)
            param = common.Parameter2(**param_dict)
        else:
            # Creating Parameter1 - remove select if present
            param_dict.pop('select', None)
            param = common.Parameter1(**param_dict)

        param.props = none_if_empty(props)
        return param

    @staticmethod
    def last_modified_at_time(timestamp: Optional[datetime] = None) -> datetime:
        """Generate a LastModified set to timestamp or now."""
        timestamp = timestamp if timestamp else datetime.now().astimezone()
        return timestamp

    @staticmethod
    def update_last_modified(model: TopLevelOscalModel, timestamp: Optional[datetime] = None) -> None:
        """Update the LastModified timestamp in top level model to now."""
        timestamp = timestamp if timestamp else datetime.now().astimezone()
        model.metadata.last_modified = timestamp

    @staticmethod
    def model_age(model: TopLevelOscalModel) -> int:
        """Find time in seconds since LastModified timestamp."""
        # default to one year if no last_modified
        age_seconds = const.DAY_SECONDS * 365
        if model.metadata.last_modified:
            dt = datetime.now().astimezone() - model.metadata.last_modified
            age_seconds = int(dt.total_seconds())
        return age_seconds

    @staticmethod
    def find_values_by_name(object_of_interest: Any, name_of_interest: str) -> List[Any]:
        """Traverse object and return list of values of specified name."""
        loe = []
        if isinstance(object_of_interest, BaseModel):
            value = getattr(object_of_interest, name_of_interest, None)
            if value is not None:
                loe.append(value)
            fields = getattr(object_of_interest, const.FIELDS_SET, None)
            if fields is not None:
                for field in fields:
                    loe.extend(
                        ModelUtils.find_values_by_name(getattr(object_of_interest, field, None), name_of_interest)
                    )
        elif type(object_of_interest) is list:
            for item in object_of_interest:
                loe.extend(ModelUtils.find_values_by_name(item, name_of_interest))
        elif type(object_of_interest) is dict:
            if name_of_interest in object_of_interest:
                loe.append(object_of_interest[name_of_interest])
            for item in object_of_interest.values():
                loe.extend(ModelUtils.find_values_by_name(item, name_of_interest))
        return loe

    @staticmethod
    def has_no_duplicate_values_by_name(object_of_interest: BaseModel, name_of_interest: str) -> bool:
        """Determine if duplicate values of type exist in object."""
        loe = ModelUtils.find_values_by_name(object_of_interest, name_of_interest)
        set_loe = set(loe)
        if len(loe) == len(set_loe):
            return True
        items: Dict[str, Any] = {}
        for item in loe:
            items[item] = items.get(item, 0) + 1
        # now print items
        for item, instances in items.items():
            if instances > 1:
                logger.warning(f'Duplicate detected of item {item} with {instances} instances.')
        return False

    @staticmethod
    def find_uuid_refs(object_of_interest: BaseModel) -> Set[str]:
        """Find uuid references made in prose and links."""
        # hrefs have form #foo or #uuid
        uuid_strs = ModelUtils.find_values_by_name(object_of_interest, 'href')

        # prose has uuid refs in markdown form: [foo](#bar) or [foo](#uuid)
        prose_list = ModelUtils.find_values_by_name(object_of_interest, 'prose')
        for prose in prose_list:
            matches = re.findall(const.MARKDOWN_URL_REGEX, prose)
            # the [1] is to extract the inner of 3 capture patterns
            new_uuids = [match[1] for match in matches]
            uuid_strs.extend(new_uuids)

        # collect the strings that start with # and are potential uuids
        uuid_strs = [uuid_str for uuid_str in uuid_strs if uuid_str and uuid_str[0] == '#']

        # go through all matches and build set of those that are uuids
        uuid_set = {uuid_match for uuid_str in uuid_strs for uuid_match in re.findall(const.UUID_REGEX, uuid_str[1:])}
        return uuid_set

    @staticmethod
    def _regenerate_uuids_in_place(object_of_interest: Any, uuid_lut: Dict[str, str]) -> Tuple[Any, Dict[str, str]]:
        """Update all uuids in model that require updating.

        Go through the model and replace all dicts with key == 'uuid' and replace the value with a new uuid4.
        Build a lookup table of the updates that were made.
        This function does not update the corresponding refs to those uuid's.  That is done by update_uuid_refs
        Note that this function needs to be started off with uuid_lut == {}, i.e. an empty dict.
        After that it recurses and grows the lut.

        Args:
            object_of_interest: pydantic.BaseModel, list, dict or str will be updated
            uuid_lut: dict of the growing lut of old:new uuid's.  First call must be made with value {}

        Returns:
            The updated object_of_interest with new uuid's (but refs to them are not updated)
            The final lookup table of old:new uuid's

        """
        uuid_str = 'uuid'
        # Certain types are known not to need updating and should not change
        # Resources are identified by uuid, and the corresponding href will have # in front of the uuid string
        # Neither of these should change
        # If other similar types are found they should be added to the FixedUuidModel typevar to prevent updating
        if isinstance(object_of_interest, common.Resource):
            pass
        elif isinstance(object_of_interest, BaseModel):
            # fields has names of all fields in model
            fields = getattr(object_of_interest, const.FIELDS_SET, None)
            for field in fields:
                new_object = None
                if field == uuid_str:
                    orig_uuid = getattr(object_of_interest, field)
                    if orig_uuid:
                        new_object = str(uuid.uuid4())
                        uuid_lut[orig_uuid] = new_object
                else:
                    new_object, uuid_lut = ModelUtils._regenerate_uuids_in_place(
                        object_of_interest.__dict__[field], uuid_lut
                    )
                object_of_interest.__dict__[field] = new_object
        elif type(object_of_interest) is list:
            new_list = []
            for item in object_of_interest:
                new_item, uuid_lut = ModelUtils._regenerate_uuids_in_place(item, uuid_lut)
                new_list.append(new_item)
            object_of_interest = new_list
        elif type(object_of_interest) is dict:
            new_dict = {}
            for key, value in object_of_interest.items():
                if key == uuid_str:
                    new_val = str(uuid.uuid4())
                    new_dict[uuid_str] = new_val
                    uuid_lut[value] = new_val
                else:
                    new_value, uuid_lut = ModelUtils._regenerate_uuids_in_place(value, uuid_lut)
                    new_dict[key] = new_value
            object_of_interest = new_dict
        return object_of_interest, uuid_lut

    @staticmethod
    def _update_new_uuid_refs(object_of_interest: Any, uuid_lut: Dict[str, str]) -> Tuple[Any, int]:
        """Update all refs to uuids that were changed."""
        n_refs_updated = 0
        if isinstance(object_of_interest, BaseModel):
            fields = getattr(object_of_interest, const.FIELDS_SET, None)
            for field in fields:
                new_object, n_new_updates = ModelUtils._update_new_uuid_refs(
                    object_of_interest.__dict__[field], uuid_lut
                )
                n_refs_updated += n_new_updates
                object_of_interest.__dict__[field] = new_object
        elif type(object_of_interest) is list:
            new_list = []
            for item in object_of_interest:
                new_item, n_new_updates = ModelUtils._update_new_uuid_refs(item, uuid_lut)
                n_refs_updated += n_new_updates
                new_list.append(new_item)
            object_of_interest = new_list
        elif type(object_of_interest) is dict:
            new_dict = {}
            for key, value in object_of_interest.items():
                if isinstance(value, str):
                    if value in uuid_lut:
                        new_dict[key] = uuid_lut[value]
                        n_refs_updated += 1
                    else:
                        new_dict[key] = value
                else:
                    new_value, n_new_updates = ModelUtils._update_new_uuid_refs(value, uuid_lut)
                    n_refs_updated += n_new_updates
                    new_dict[key] = new_value
            object_of_interest = new_dict
        elif isinstance(object_of_interest, str):
            if object_of_interest in uuid_lut:
                n_refs_updated += 1
                object_of_interest = uuid_lut[object_of_interest]
        return object_of_interest, n_refs_updated

    @staticmethod
    def regenerate_uuids(object_of_interest: Any) -> Tuple[Any, Dict[str, str], int]:
        """Regenerate all uuids in object and update corresponding references.

        Find all dicts with key == 'uuid' and replace the value with a new uuid4.
        Build a corresponding lookup table as you go, of old:new uuid values.
        Then make a second pass through the object and replace all string values
        present in the lookup table with the new value.

        Args:
            object_of_interest: pydantic.BaseModel, list, dict or str will be updated

        Returns:
            The updated object with new uuid's and refs
            The final lookup table of old:new uuid's
            A count of the number of refs that were updated
        """
        new_object, uuid_lut = ModelUtils._regenerate_uuids_in_place(object_of_interest, {})
        new_object, n_refs_updated = ModelUtils._update_new_uuid_refs(new_object, uuid_lut)
        return new_object, uuid_lut, n_refs_updated

    @staticmethod
    def fields_set_non_none(obj: BaseModel) -> Set[str]:
        """Find the fields set with Nones and empty items removed."""
        # Pydantic v2: __fields_set__ → model_fields_set
        return set(as_filtered_list(list(obj.model_fields_set), lambda f: getattr(obj, f)))

    @staticmethod
    def _objects_differ(
        obj_a: Any, obj_b: Any, ignore_type_list: List[Any], ignore_name_list: List[str], ignore_all_uuid: bool
    ) -> bool:
        """
        Compare two objects with option to ignore given types.

        This does not check for tuples or other structures that won't be found in JSON.
        """
        from enum import Enum

        obj_a_type = type(obj_a)
        obj_b_type = type(obj_b)

        # Check if both are falsy
        if bool(obj_a) != bool(obj_b):
            return True

        # For dynamically created wrapper classes (like Components, Props), compare by class name
        # These are created on-the-fly and may have different type identities but same structure
        if obj_a_type != obj_b_type:
            # Handle enum vs string comparison (enums get converted to strings after JSON round-trip)
            if isinstance(obj_a, Enum) and obj_b_type is str:
                # Compare enum value with string
                return obj_a.value != obj_b
            elif isinstance(obj_b, Enum) and obj_a_type is str:
                # Compare string with enum value
                return obj_a != obj_b.value
            # Handle root wrapper vs enum comparison (Pydantic v2 RootModel)
            elif hasattr(obj_a, 'root') and isinstance(obj_b, Enum):
                return obj_a.root != obj_b.value
            elif hasattr(obj_b, 'root') and isinstance(obj_a, Enum):
                return obj_a.value != obj_b.root
            # If both are BaseModel instances with same class name, treat as equivalent
            elif isinstance(obj_a, BaseModel) and isinstance(obj_b, BaseModel):
                if obj_a_type.__name__ == obj_b_type.__name__:
                    # Same class name, continue with field comparison below
                    pass
                else:
                    return True
            else:
                return True
        if not bool(obj_a):
            return False
        if obj_a_type in ignore_type_list:
            return False
        if obj_a_type is str:
            return obj_a != obj_b
        elif isinstance(obj_a, BaseModel):
            fields_a = ModelUtils.fields_set_non_none(obj_a)
            fields_b = ModelUtils.fields_set_non_none(obj_b)
            if fields_a != fields_b:
                return True
            for field in list_utils.as_filtered_list(fields_a, lambda f: f not in ignore_name_list):  # type: ignore
                if ignore_all_uuid and 'uuid' in field:
                    continue
                if ModelUtils._objects_differ(
                    getattr(obj_a, field), getattr(obj_b, field), ignore_type_list, ignore_name_list, ignore_all_uuid
                ):
                    return True
        elif obj_a_type is list:
            if len(obj_a) != len(obj_b):
                return True
            for item_a, item_b in zip(obj_a, obj_b, strict=True):
                if ModelUtils._objects_differ(item_a, item_b, ignore_type_list, ignore_name_list, ignore_all_uuid):
                    return True
        elif obj_a_type is dict:
            if obj_a.keys() != obj_b.keys():
                return True
            for key, val in obj_a.items():
                if ignore_all_uuid and 'uuid' in key:
                    continue
                if key not in ignore_name_list and ModelUtils._objects_differ(
                    val, obj_b[key], ignore_type_list, ignore_name_list, ignore_all_uuid
                ):
                    return True
        elif obj_a != obj_b:
            return True
        return False

    @staticmethod
    def models_are_equivalent(
        model_a: Optional[TopLevelOscalModel], model_b: Optional[TopLevelOscalModel], ignore_all_uuid: bool = False
    ) -> bool:
        """
        Test if models are equivalent except for last modified and possibly uuid.

        If a model has had uuids regenerated, then all uuids *and references to them* are updated.  This means that
        special handling is required if a model has had uuids regenerated - when checking equivalence.
        """
        uuid_type_list = [
            common.LastModified,
            common.LocationUuid,
            common.PartyUuid,
            assessment_plan.RelatedObservation,
            assessment_results.RelatedObservation,
            poam.RelatedObservation,
            poam.RelatedObservation1,
        ]
        type_list = uuid_type_list if ignore_all_uuid else [common.LastModified]
        return not ModelUtils._objects_differ(model_a, model_b, type_list, ['last_modified'], ignore_all_uuid)

    @staticmethod
    def get_title_from_model_uri(trestle_root: pathlib.Path, uri: str) -> str:
        """Get title from model at uri."""
        try:
            fetcher = cache.FetcherFactory.get_fetcher(trestle_root, uri)
            model, _ = fetcher.get_oscal()
            return model.metadata.title
        except TrestleError as e:
            logger.warning(f'Error finding title for model at uri {uri}: {e}')
            raise
