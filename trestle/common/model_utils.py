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
import logging
import pathlib
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

from pydantic import BaseModel, create_model

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


class ModelUtils:
    """Utilities for the OSCAL models input and output."""

    @staticmethod
    def load_distributed(
        abs_path: Path,
        abs_trestle_root: Path,
        collection_type: Optional[Type[Any]] = None
    ) -> Tuple[Type[OscalBaseModel],
               str,
               Optional[Union[OscalBaseModel, List[OscalBaseModel], Dict[str, OscalBaseModel]]]]:
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
            primary_model_instance = primary_model_type.oscal_read(abs_path)
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
                    #      __root__: List[Bar]    noqa: E800
                    # You need to test whether first a root key exists
                    # then whether the outer_type of root is a collection.
                    # Alternative is to do a try except to avoid the error for an unknown key.

                    if model_type.is_collection_container():
                        # This directory is a decomposed List or Dict
                        collection_type = model_type.get_collection_type()
                        model_type, model_alias, model_instance = ModelUtils.load_distributed(local_path,
                                                                                              abs_trestle_root,
                                                                                              collection_type)
                        aliases_not_to_be_stripped.append(model_alias.split('.')[-1])
                        instances_to_be_merged.append(model_instance)
            primary_model_dict = {}
            if primary_model_instance is not None:
                primary_model_dict = primary_model_instance.__dict__

            merged_model_type, merged_model_alias = ModelUtils.get_stripped_model_type(abs_path,
                                                                                       abs_trestle_root,
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

            merged_model_instance = merged_model_type(**primary_model_dict)
            return merged_model_type, merged_model_alias, merged_model_instance
        return primary_model_type, primary_model_alias, primary_model_instance

    @staticmethod
    def load_model_for_class(
        trestle_root: pathlib.Path,
        model_name: str,
        model_class: TG,
        file_content_type: Optional[FileContentType] = None
    ) -> Tuple[TG, pathlib.Path]:
        """Load a model by name and model class and infer file content type if not specified.

        If you need to load an existing model but its content type may not be known, use this method.
        But the file content type should be specified if it is somehow known.

        Note:  This does not validate the model.  If you want to validate the model use the load_validate utilities.
        """
        root_model_path = ModelUtils._root_path_for_top_level_model(
            trestle_root, model_name, model_class
        )  # type: ignore
        if file_content_type is None:
            file_content_type = FileContentType.path_to_content_type(root_model_path)
        if not FileContentType.is_readable_file(file_content_type):
            raise TrestleError(f'Unable to load model {model_name} without specifying json or yaml.')
        full_model_path = root_model_path.with_suffix(FileContentType.to_file_extension(file_content_type))
        _, _, model = ModelUtils.load_distributed(full_model_path, trestle_root)
        return model, full_model_path  # type: ignore

    @staticmethod
    def load_model_for_type(trestle_root: pathlib.Path, model_type: str,
                            model_name: str) -> Tuple[TopLevelOscalModel, pathlib.Path]:
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
    def get_relative_model_type(relative_path: pathlib.Path) -> Tuple[Type[OscalBaseModel], str]:
        """
        Given the relative path of a file with respect to 'trestle_root' return the oscal model type.

        Args:
            relative_path: Relative path of the model with respect to the root directory of the trestle workspace.
        Returns:
            Type of Oscal Model for the provided model
            Alias of that oscal model.
        """
        if len(relative_path.parts) < 2:
            raise TrestleError(
                'Insufficient path length to be a valid relative path w.r.t trestle workspace root directory.'
            )
        model_dir = relative_path.parts[0]
        model_relative_path = pathlib.Path(*relative_path.parts[2:])  # catalogs, profiles, etc

        if model_dir in const.MODEL_DIR_LIST:
            module_name = const.MODEL_DIR_TO_MODEL_MODULE[model_dir]
        else:
            raise TrestleError(f'No valid trestle model type directory (e.g. catalogs) found for {model_dir}.')

        model_type, model_alias = ModelUtils.get_root_model(module_name)
        full_alias = model_alias

        for index, part in enumerate(model_relative_path.parts):
            alias = ModelUtils._extract_alias(part)
            if index > 0 or model_alias != alias:
                model_alias = alias
                full_alias = f'{full_alias}.{model_alias}'
                if utils.is_collection_field_type(model_type):
                    model_type = utils.get_inner_type(model_type)
                else:
                    model_type = model_type.alias_to_field_map()[alias].outer_type_

        return model_type, full_alias

    @staticmethod
    def get_stripped_model_type(
        absolute_path: pathlib.Path,
        absolute_trestle_root: pathlib.Path,
        aliases_not_to_be_stripped: List[str] = None
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
            absolute_path.relative_to(absolute_trestle_root))
        logger.debug(f'singular model type {singular_model_type} model alias {model_alias}')

        # Stripped models do not apply to collection types such as List[] and Dict{}
        # if model type is a list or dict, generate a new wrapping model for it
        if utils.is_collection_field_type(singular_model_type):
            malias = model_alias.split('.')[-1]
            class_name = alias_to_classname(malias, AliasMode.JSON)
            logger.debug(f'collection field type class name {class_name} and alias {malias}')
            model_type = create_model(class_name, __base__=OscalBaseModel, __root__=(singular_model_type, ...))
            logger.debug(f'model_type created: {model_type}')
            return model_type, model_alias

        malias = model_alias.split('.')[-1]
        logger.debug(f'not collection field type, malias: {malias}')
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
        if len(aliases_to_be_stripped) > 0:
            model_type = singular_model_type.create_stripped_model_type(
                stripped_fields_aliases=list(aliases_to_be_stripped)
            )
            logger.debug(f'model_type: {model_type}')
            return model_type, model_alias
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
            # only look for proper json and yaml files
            if not ModelUtils._should_ignore(f.stem):
                if not f.is_dir():
                    logger.warning(
                        f'Ignoring validation of misplaced file {f.name} '
                        + f'found in the model directory, {model_dir_name}.'
                    )
                else:
                    model_list.append(f.stem)
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
        file_content_type: Optional[FileContentType] = None
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
            if utils.is_collection_field_type(model_type):
                # if it is a collection type and last part is * then break
                if i == len(path_parts) - 1 and path_parts[i] == '*':
                    break
                # otherwise get the inner type of items in the collection
                model_type = utils.get_inner_type(model_type)
                # and bump i
                i = i + 1
            else:
                path_part = path_parts[i]
                field_map = model_type.alias_to_field_map()
                if path_part not in field_map:
                    continue
                field = field_map[path_part]
                model_type = field.outer_type_
            model_types.append(model_type)

        last_alias = path_parts[-1]
        if last_alias == '*':
            last_alias = path_parts[-2]

        # generic model and not list, so return itself fixme doc
        if not utils.is_collection_field_type(model_type):
            return last_alias

        parent_model_type = model_types[-2]
        try:
            field_map = parent_model_type.alias_to_field_map()
            field = field_map[last_alias]
            outer_type = field.outer_type_
            inner_type = utils.get_inner_type(outer_type)
            inner_type_name = inner_type.__name__
            singular_alias = str_utils.classname_to_alias(inner_type_name, AliasMode.JSON)
        except Exception as e:
            raise err.TrestleError(f'Error in json path {alias_path}: {e}')

        return singular_alias

    @staticmethod
    def get_root_model(module_name: str) -> Tuple[Type[Any], str]:
        """Get the root model class and alias based on the module."""
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as e:
            raise err.TrestleError(str(e))

        if hasattr(module, 'Model'):
            model_metadata = next(iter(module.Model.__fields__.values()))
            return model_metadata.type_, model_metadata.alias
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
        alias = string_dir.split('.')[0].split(
            const.IDX_SEP
        )[-1]  # get suffix of file or directory name representing list or dict item
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

            # ASSUMPTION HERE: if it is a directory, there's a file that can not be decomposed further.
            if path.is_dir():
                continue
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
            return obj.__root__
        if isinstance(obj, common.HowMany):
            return obj.value
        # it is either a string already or we cast it to string
        if not hasattr(obj, const.FIELDS_SET):
            return str(obj)
        # it is an oscal object and we need to recurse within its attributes
        res = {}
        for field in obj.__fields_set__:
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
            The converted parameter as dictionary, with values as None if not present
        """
        res = ModelUtils._parameter_to_dict_recurse(obj, partial)
        if 'values' not in res:
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
                        logger.warning(f"Parameter {param_dict['id']} has value \"{value}\" not in choices: {choices}.")
        props = param_dict.get('props', [])
        if const.DISPLAY_NAME in param_dict:
            display_name = param_dict.pop(const.DISPLAY_NAME)
            props.append(common.Property(name=const.DISPLAY_NAME, value=display_name, ns=const.TRESTLE_GENERIC_NS))
        if const.AGGREGATES in param_dict:
            # removing aggregates as this is prop just informative in markdown
            param_dict.pop(const.AGGREGATES)
        if const.ALT_IDENTIFIER in param_dict:
            # removing alt-identifier as this is prop just informative in markdown
            param_dict.pop(const.ALT_IDENTIFIER)

        if 'ns' in param_dict:
            param_dict.pop('ns')
        param = common.Parameter(**param_dict)
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
            age_seconds = dt.seconds
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
                        object_of_interest.__dict__[field],
                        uuid_lut
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
                    object_of_interest.__dict__[field],
                    uuid_lut
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
        return set(as_filtered_list(list(obj.__fields_set__), lambda f: getattr(obj, f)))

    @staticmethod
    def _objects_differ(
        obj_a: Any, obj_b: Any, ignore_type_list: List[Any], ignore_name_list: List[str], ignore_all_uuid: bool
    ) -> bool:
        """
        Compare two objects with option to ignore given types.

        This does not check for tuples or other structures that won't be found in JSON.
        """
        obj_a_type = type(obj_a)
        obj_b_type = type(obj_b)
        if bool(obj_a) != bool(obj_b) or obj_a_type != obj_b_type:
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
                if ModelUtils._objects_differ(getattr(obj_a, field),
                                              getattr(obj_b, field),
                                              ignore_type_list,
                                              ignore_name_list,
                                              ignore_all_uuid):
                    return True
        elif obj_a_type is list:
            if len(obj_a) != len(obj_b):
                return True
            for item_a, item_b in zip(obj_a, obj_b):
                if ModelUtils._objects_differ(item_a, item_b, ignore_type_list, ignore_name_list, ignore_all_uuid):
                    return True
        elif obj_a_type is dict:
            if obj_a.keys() != obj_b.keys():
                return True
            for key, val in obj_a.items():
                if ignore_all_uuid and 'uuid' in key:
                    continue
                if key not in ignore_name_list and ModelUtils._objects_differ(
                        val, obj_b[key], ignore_type_list, ignore_name_list, ignore_all_uuid):
                    return True
        elif obj_a != obj_b:
            return True
        return False

    @staticmethod
    def models_are_equivalent(
        model_a: Optional[TopLevelOscalModel],
        model_b: Optional[TopLevelOscalModel],
        ignore_all_uuid: bool = False
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
            common.RelatedRisk,
            common.Source,
            assessment_plan.RelatedObservation,
            assessment_results.RelatedObservation,
            poam.RelatedObservation,
            poam.RelatedObservation1
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
