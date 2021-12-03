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
"""Common file system utilities."""

import json
import logging
import os
import pathlib
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, Union, cast

from pydantic import create_model

from ruamel.yaml import YAML

from trestle.core import const
from trestle.core import err
from trestle.core import utils
from trestle.core.base_model import OscalBaseModel
from trestle.core.common_types import TopLevelOscalModel
from trestle.core.err import TrestleError
from trestle.core.models.file_content_type import FileContentType
from trestle.utils.load_distributed import load_distributed

if os.name == 'nt':  # pragma: no cover
    import win32api
    import win32con

logger = logging.getLogger(__name__)


def should_ignore(name: str) -> bool:
    """Check if the file or directory should be ignored or not."""
    return name[0] == '.' or name[0] == '_'


def is_valid_project_root(path: pathlib.Path) -> bool:
    """Check if the path is a valid trestle project root."""
    trestle_dir = path / const.TRESTLE_CONFIG_DIR
    return trestle_dir.exists() and trestle_dir.is_dir()


def get_trestle_project_root(path: pathlib.Path) -> Optional[pathlib.Path]:
    """Get the trestle project root folder in the path."""
    while len(path.parts) > 1:  # it must not be the system root directory
        if is_valid_project_root(path):
            return path
        path = path.parent
    return None


def is_valid_project_model_path(path: pathlib.Path) -> bool:
    """Check if the file/directory path is a valid trestle model project."""
    root_path = get_trestle_project_root(path)
    if root_path is None:
        return False

    relative_path = path.relative_to(str(root_path))
    if len(relative_path.parts) < 2 or relative_path.parts[0] not in const.MODEL_DIR_LIST:
        return False
    return True


def get_project_model_path(path: pathlib.Path) -> Optional[pathlib.Path]:
    """Get the base path of the trestle model project."""
    if len(path.parts) > 2:
        for i in range(2, len(path.parts)):
            current = pathlib.Path(path.parts[0]).joinpath(*path.parts[1:i + 1])
            if is_valid_project_model_path(current):
                return current
    return None


def has_parent_path(sub_path: pathlib.Path, parent_path: pathlib.Path) -> bool:
    """Check if sub_path has the specified parent_dir path."""
    # sub_path should be longer than parent path
    if len(sub_path.parts) < len(parent_path.parts):
        return False

    for i, part in enumerate(parent_path.parts):
        if part != sub_path.parts[i]:
            return False
    return True


def get_relative_model_type(relative_path: pathlib.Path) -> Tuple[Type[OscalBaseModel], str]:
    """
    Given the relative path of a file with respect to 'trestle_root' return the oscal model type.

    Args:
        relative_path: Relative path of the model of interest with respect to the root directory of the trestle project.

    Returns:
        Type of Oscal Model for the provided model
        Alias of that oscal model.

    """
    if len(relative_path.parts) < 2:
        raise TrestleError('Insufficient path length to be a valid relative path w.r.t Trestle project root directory.')
    model_dir = relative_path.parts[0]
    model_relative_path = pathlib.Path(*relative_path.parts[2:])  # catalogs, profiles, etc

    if model_dir in const.MODEL_DIR_LIST:
        module_name = const.MODEL_DIR_TO_MODEL_MODULE[model_dir]
    else:
        raise TrestleError(f'No valid trestle model type directory (e.g. catalogs) found for {model_dir}.')

    model_type, model_alias = utils.get_root_model(module_name)
    full_alias = model_alias

    for index, part in enumerate(model_relative_path.parts):
        alias = extract_alias(part)
        if index > 0 or model_alias != alias:
            model_alias = alias
            full_alias = f'{full_alias}.{model_alias}'
            if utils.is_collection_field_type(model_type):
                model_type = utils.get_inner_type(model_type)
            else:
                model_type = model_type.alias_to_field_map()[alias].outer_type_

    return model_type, full_alias


def get_stripped_model_type(
    absolute_path: pathlib.Path,
    absolute_trestle_root: pathlib.Path,
    aliases_not_to_be_stripped: List[str] = None
) -> Tuple[Type[OscalBaseModel], str]:
    """
    Get the stripped contextual model class and alias based on the contextual path.

    This function relies on the directory structure of the trestle model being edited to determine, based on the
    existing files and folder, which fields should be stripped from the model type represented by the path passed in as
    a parameter.
    """
    if aliases_not_to_be_stripped is None:
        aliases_not_to_be_stripped = []
    singular_model_type, model_alias = get_relative_model_type(absolute_path.relative_to(absolute_trestle_root))
    logger.debug(f'singular model type {singular_model_type} model alias {model_alias}')

    # Stripped models do not apply to collection types such as List[] and Dict{}
    # if model type is a list or dict, generate a new wrapping model for it
    if utils.is_collection_field_type(singular_model_type):
        malias = model_alias.split('.')[-1]
        class_name = utils.alias_to_classname(malias, 'json')
        logger.debug(f'collection field type class name {class_name} and alias {malias}')
        model_type = create_model(class_name, __base__=OscalBaseModel, __root__=(singular_model_type, ...))
        logger.debug(f'model_type created: {model_type}')
        model_type = cast(Type[OscalBaseModel], model_type)
        return model_type, model_alias

    malias = model_alias.split('.')[-1]
    logger.debug(f'not collection field type, malias: {malias}')
    if absolute_path.is_dir() and malias != extract_alias(absolute_path.name):
        split_subdir = absolute_path / malias
    else:
        split_subdir = absolute_path.parent / absolute_path.with_suffix('').name

    aliases_to_be_stripped = set()
    if split_subdir.exists():
        for f in iterdir_without_hidden_files(split_subdir):
            alias = extract_alias(f.name)
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


def extract_alias(string_dir: str) -> str:
    """
    Extract alias from filename or directory name removing extensions and prefixes related to dict and list.

    As we need to do this for multiple parts of a path operating on strings is easier.
    """
    alias = string_dir.split('.')[0].split(const.IDX_SEP
                                           )[-1]  # get suffix of file or directory name representing list or dict item
    return alias


def clean_project_sub_path(sub_path: pathlib.Path) -> None:
    """Clean all directories and files in a project top level subdir.

    It ensures the sub_path is a child path in the project root.
    """
    if sub_path.exists():
        sub_path = sub_path.resolve()
        project_root = sub_path.parent
        if not get_trestle_project_root(project_root):
            raise TrestleError('Path to be cleaned is not a under valid Trestle project root')

        # clean all files/directories under sub_path
        if sub_path.is_dir():
            for item in pathlib.Path.iterdir(sub_path):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    clean_project_sub_path(item)
            sub_path.rmdir()
        # delete the sub_path
        elif sub_path.is_file():
            sub_path.unlink()


def load_file(file_path: pathlib.Path) -> Dict[str, Any]:
    """
    Load JSON or YAML file content into a dict.

    This is not intended to be the default load mechanism. It should only be used
    if a OSCAL object type is unknown but the context a user is in.
    """
    content_type = FileContentType.to_content_type(file_path.suffix)
    with file_path.open('r', encoding=const.FILE_ENCODING) as f:
        if content_type == FileContentType.YAML:
            yaml = YAML(typ='safe')
            return yaml.load(f)
        if content_type == FileContentType.JSON:
            return json.load(f)


def get_singular_alias(alias_path: str, relative_path: Optional[pathlib.Path] = None) -> str:
    """
    Get the alias in the singular form from a jsonpath.

    If contextual_mode is True and contextual_path is None, it assumes alias_path is relative to the directory the user
    is running trestle from.

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
        _, full_model_alias = get_relative_model_type(relative_path)
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
        model_type, model_alias = utils.get_root_model(module_name)
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
        singular_alias = utils.classname_to_alias(inner_type_name, 'json')
    except Exception as e:
        raise err.TrestleError(f'Error in json path {alias_path}: {e}')

    return singular_alias


def model_type_to_model_dir(model_type: str) -> str:
    """Get plural model directory from model type."""
    if model_type not in const.MODEL_TYPE_LIST:
        raise err.TrestleError(f'Not a valid model type: {model_type}.')
    return const.MODEL_TYPE_TO_MODEL_DIR[model_type]


def get_contextual_file_type(path: pathlib.Path) -> FileContentType:
    """Return the file content type for files in the given directory, if it's a trestle project."""
    if not is_valid_project_model_path(path):
        raise err.TrestleError(f'Trestle project not found at path {path}')

    for file_or_directory in iterdir_without_hidden_files(path):
        if file_or_directory.is_file():
            return FileContentType.to_content_type(file_or_directory.suffix)

    for file_or_directory in path.iterdir():
        if file_or_directory.is_dir():
            return get_contextual_file_type(file_or_directory)

    raise err.TrestleError('No files found in the project.')


def get_models_of_type(model_type: str, root: pathlib.Path) -> List[str]:
    """Get list of model names for requested type in trestle directory."""
    if model_type not in const.MODEL_TYPE_LIST:
        raise err.TrestleError(f'Model type {model_type} is not supported')
    # search relative to project root
    trestle_root = get_trestle_project_root(root)
    if not trestle_root:
        logger.error(f'Given directory {root} is not within a trestle project.')
        raise err.TrestleError('Given directory is not within a trestle project.')

    # contruct path to the model file name
    model_dir_name = model_type_to_model_dir(model_type)
    root_model_dir = trestle_root / model_dir_name
    model_list = []
    for f in root_model_dir.glob('*/'):
        # only look for proper json and yaml files
        if not should_ignore(f.stem):
            if not f.is_dir():
                logger.warning(
                    f'Ignoring validation of misplaced file {f.name} '
                    + f'found in the model directory, {model_dir_name}.'
                )
            else:
                model_list.append(f.stem)
    return model_list


def get_all_models(root: pathlib.Path) -> List[Tuple[str, str]]:
    """Get list of all models in trestle directory as tuples (model_type, model_name)."""
    full_list = []
    for model_type in const.MODEL_TYPE_LIST:
        models = get_models_of_type(model_type, root)
        for m in models:
            full_list.append((model_type, m))
    return full_list


def iterdir_without_hidden_files(directory_path: pathlib.Path) -> Iterable[pathlib.Path]:
    """
    Get iterator over all paths in the given directory_path excluding hidden files.

    Args:
        directory_path: The directory to iterate through.

    Returns:
        Iterator over the files in the directory excluding hidden files.
    """
    filtered_paths = list(filter(lambda p: not is_hidden(p) or p.is_dir(), pathlib.Path.iterdir(directory_path)))

    return filtered_paths.__iter__()


def is_hidden(file_path: pathlib.Path) -> bool:
    """
    Determine whether a file is hidden based on the appropriate os attributes.

    This function will only work for the current file path only (e.g. not if a parent is hidden).

    Args:
        file_path: The file path for which we are testing whether the file / directory is hidden.

    Returns:
        Whether or not the file is file/directory is hidden.
    """
    # Handle windows
    if os.name == 'nt':  # pragma: no cover
        attribute = win32api.GetFileAttributes(str(file_path))
        return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
    # Handle unix
    return file_path.stem.startswith('.')


def is_symlink(file_path: pathlib.Path) -> bool:
    """Is the file path a symlink."""
    if os.name == 'nt':
        return file_path.suffix == '.lnk'
    return file_path.is_symlink()


def local_and_visible(file_path: pathlib.Path) -> bool:
    """Is the file or dir local (not a symlink) and not hidden."""
    return not (is_hidden(file_path) or is_symlink(file_path))


def allowed_task_name(name: str) -> bool:
    """Determine whether a task, which is a 'non-core-OSCAL activity/directory is allowed.

    args:
        name: the task name which is assumed may take the form of a relative path for task/subtasks.

    Returns:
        Whether the task name is allowed or not allowed (interferes with assumed project directories such as catalogs).
    """
    # Task must not use an OSCAL directory
    # Task must not self-interfere with a project
    pathed_name = pathlib.Path(name)

    root_path = pathed_name.parts[0]
    if root_path in const.MODEL_TYPE_TO_MODEL_DIR.values():
        logger.error('Task name is the same as an OSCAL schema name.')
        return False
    if root_path[0] == '.':
        logger.error('Task name must not start with "."')
        return False
    if pathed_name.suffix != '':
        # Does it look like a file
        logger.error('tasks name must not look like a file path (e.g. contain a suffix')
        return False
    if '__global__' in pathed_name.parts:
        logger.error('Task name cannot contain __global__')
        return False
    return True


def relative_resolve(candidate: pathlib.Path, cwd: pathlib.Path) -> pathlib.Path:
    """Resolve a candidate file path relative to a provided cwd.

    This is to circumvent bad behaviour for resolve on windows platforms where the path must exist.

    If a relative dir is passed it presumes the directory is relative to the PROVIDED cwd.
    If relative expansions exist (e.g. ../) the final result must still be within the cwd.

    If an absolute path is provided it tests whether the path is within the cwd or not.

    """
    # Expand user first if applicable.
    candidate = candidate.expanduser()

    if not cwd.is_absolute():
        raise TrestleError('Error handling current working directory. CWD is expected to be absolute.')

    if not candidate.is_absolute():
        new = pathlib.Path(cwd / candidate).resolve()
    else:
        new = candidate.resolve()
    try:
        new.relative_to(cwd)
    except ValueError:
        raise TrestleError(f'Provided dir {candidate} is not relative to {cwd}')
    return new


def _root_path_for_top_level_model(
    trestle_root: pathlib.Path, model_name: str, model_class: Union[TopLevelOscalModel, Type[TopLevelOscalModel]]
) -> pathlib.Path:
    """Find the root path to a model given its name and class - with no suffix.

    This is a private method used only to construct the root filepath based on model name and type.
    It does not check for existence or content type and it does not create the directory if it does not exist.
    """
    if not hasattr(model_class, '__module__') or model_class.__module__ not in const.MODEL_MODULE_LIST:
        raise TrestleError(f'Unable to determine model type for model {model_name} with class {model_class}')
    model_alias = const.MODEL_MODULE_TO_MODEL_TYPE[model_class.__module__]
    model_dir = trestle_root / f'{const.MODEL_TYPE_TO_MODEL_DIR[model_alias]}/{model_name}'
    return model_dir / model_alias


def path_for_top_level_model(
    trestle_root: pathlib.Path,
    model_name: str,
    model_class: Type[TopLevelOscalModel],
    file_content_type: FileContentType
) -> pathlib.Path:
    """Find the full path of a model given its name, model type and file content type.

    This does not inspect the file system or confirm the needed path and file exists.
    """
    root_path = _root_path_for_top_level_model(trestle_root, model_name, model_class)
    return root_path.with_suffix(FileContentType.to_file_extension(file_content_type))


def full_path_for_top_level_model(
    trestle_root: pathlib.Path,
    model_name: str,
    model_class: Type[TopLevelOscalModel],
) -> pathlib.Path:
    """Find the full path of an existing model given its name and model type but no file content type.

    Use this method when you need the path of a model but you don't know the file content type.
    This method should only be called if the model needs to exist already in the trestle directory.
    If you do know the file content type, use path_for_top_level_model instead.
    """
    root_model_path = _root_path_for_top_level_model(trestle_root, model_name, model_class)
    file_content_type = FileContentType.path_to_content_type(root_model_path)
    if not FileContentType.is_readable_file(file_content_type):
        raise TrestleError(f'Unable to load model {model_name} as json or yaml.')
    return root_model_path.with_suffix(FileContentType.to_file_extension(file_content_type))


def load_top_level_model(
    trestle_root: pathlib.Path,
    model_name: str,
    model_class: Type[TopLevelOscalModel],
    file_content_type: Optional[FileContentType] = None
) -> Tuple[TopLevelOscalModel, pathlib.Path]:
    """Load a model by name and model class and infer file content type if not specified.

    If you need to load an existing model but its content type may not be known, use this method.
    But the file content type should be specified if it is somehow known.
    """
    root_model_path = _root_path_for_top_level_model(trestle_root, model_name, model_class)
    if file_content_type is None:
        file_content_type = FileContentType.path_to_content_type(root_model_path)
    if not FileContentType.is_readable_file(file_content_type):
        raise TrestleError(f'Unable to load model {model_name} without specifying json or yaml.')
    full_model_path = root_model_path.with_suffix(FileContentType.to_file_extension(file_content_type))
    _, _, model = load_distributed(full_model_path, trestle_root)
    return model, full_model_path


def save_top_level_model(
    model: TopLevelOscalModel, trestle_root: pathlib.Path, model_name: str, file_content_type: FileContentType
) -> None:
    """Save a model by name and infer model type by inspection.

    You don't need to specify the model type (catalog, profile, etc.) but you must specify the file content type.
    If the model directory does not exist, it is created.
    """
    root_model_path = _root_path_for_top_level_model(trestle_root, model_name, model)
    full_model_path = root_model_path.with_suffix(FileContentType.to_file_extension(file_content_type))
    if not full_model_path.parent.exists():
        full_model_path.parent.mkdir(parents=True, exist_ok=True)
    model.oscal_write(full_model_path)
