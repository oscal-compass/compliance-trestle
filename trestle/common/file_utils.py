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
"""Trestle file system utils."""
import glob
import json
import logging
import os
import pathlib
import platform
import shutil
from typing import Any, Dict, Iterable, List, Optional, Set

from ruamel.yaml import YAML

from trestle.common import const, err
from trestle.common.const import MODEL_DIR_LIST
from trestle.common.err import TrestleError
from trestle.core.models.file_content_type import FileContentType

if platform.system() == const.WINDOWS_PLATFORM_STR:  # pragma: no cover
    import win32api
    import win32con

logger = logging.getLogger(__name__)


def is_windows() -> bool:
    """Check if current operating system is Windows."""
    return platform.system() == const.WINDOWS_PLATFORM_STR


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
    # as far as trestle is concerned all .* files are hidden even on windows, regardless of attributes
    if file_path.stem.startswith('.'):
        return True
    # Handle windows
    if is_windows():  # pragma: no cover
        attribute = win32api.GetFileAttributes(str(file_path))
        return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
    return False


def is_symlink(file_path: pathlib.Path) -> bool:
    """Is the file path a symlink."""
    if is_windows():
        return file_path.suffix == '.lnk'
    return file_path.is_symlink()


def is_local_and_visible(file_path: pathlib.Path) -> bool:
    """Is the file or dir local (not a symlink) and not hidden."""
    return not (is_hidden(file_path) or is_symlink(file_path))


def is_directory_name_allowed(name: str) -> bool:
    """Determine whether a directory name, which is a 'non-core-OSCAL activity/directory is allowed.

    args:
        name: the name which is assumed may take the form of a relative path for task/subtasks.

    Returns:
        Whether the name is allowed or not allowed (interferes with assumed project directories such as catalogs).
    """
    # Task must not use an OSCAL directory
    # Task must not self-interfere with a project
    pathed_name = pathlib.Path(name)

    root_path = pathed_name.parts[0]
    if root_path in const.MODEL_TYPE_TO_MODEL_DIR.values():
        logger.warning('Task name is the same as an OSCAL schema name.')
        return False
    if root_path[0] == '.':
        logger.warning('Task name must not start with "."')
        return False
    if pathed_name.suffix != '':
        # Does it look like a file
        logger.warning('Task name must not look like a file path (e.g. contain a suffix')
        return False
    if '__global__' in pathed_name.parts:
        logger.warning('Task name cannot contain __global__')
        return False
    return True


def make_hidden_file(file_path: pathlib.Path) -> None:
    """Make hidden file."""
    if not file_path.name.startswith('.') and not is_windows():
        file_path = file_path.parent / ('.' + file_path.name)

    file_path.touch()
    if is_windows():
        atts = win32api.GetFileAttributes(str(file_path))
        win32api.SetFileAttributes(str(file_path), win32con.FILE_ATTRIBUTE_HIDDEN | atts)


def _verify_oscal_folder(path: pathlib.Path) -> bool:
    """OSCAL folder should not have any files other than readme and models."""
    is_valid = True
    for file_path in path.rglob('*'):
        if file_path.is_file():
            if not is_local_and_visible(file_path) and file_path.name != const.TRESTLE_KEEP_FILE:
                logger.warning(
                    f'Hidden files (.* files and, on windows, files with hidden attribute) and symlinks are not allowed'
                    f' in OSCAL directories.  Please remove the file {file_path}.'
                )
            elif is_local_and_visible(file_path) and file_path.suffix not in {'.json', '.xml', '.yaml', '.yml', '.md'}:
                logger.warning(
                    f'Files of type {file_path.suffix} are not allowed in the OSCAL directories '
                    f'and can cause the issues. Please remove the file {file_path}'
                )
                is_valid = False

    return is_valid


def check_oscal_directories(root_path: pathlib.Path) -> bool:
    """
    Identify the state of the trestle workspace.

    Traverses trestle workspace and looks for unexpected files or directories.
    Additional files are allowed in the Trestle root but not inside the model folders.
    """
    trestle_dir_walk = os.walk(root_path)
    is_valid = True

    for _, dirs, _ in trestle_dir_walk:
        for d in dirs:
            if d in MODEL_DIR_LIST:
                is_valid = _verify_oscal_folder(root_path / d)
                if not is_valid:
                    break
    return is_valid


def is_valid_project_root(path: pathlib.Path) -> bool:
    """Check if the path is a valid trestle workspace root."""
    trestle_dir = path / const.TRESTLE_CONFIG_DIR
    return trestle_dir.exists() and trestle_dir.is_dir()


def extract_trestle_project_root(path: pathlib.Path) -> Optional[pathlib.Path]:
    """Get the trestle workspace root folder in the path."""
    while len(path.parts) > 1:  # it must not be the system root directory
        if is_valid_project_root(path):
            return path
        path = path.parent
    return None


def _is_valid_project_model_path(path: pathlib.Path) -> bool:
    """Check if the file/directory path is a valid trestle model project."""
    root_path = extract_trestle_project_root(path)
    if root_path is None:
        return False

    relative_path = path.relative_to(str(root_path))
    if len(relative_path.parts) < 2 or relative_path.parts[0] not in const.MODEL_DIR_LIST:
        return False
    return True


def extract_project_model_path(path: pathlib.Path) -> Optional[pathlib.Path]:
    """Get the base path of the trestle model project."""
    if len(path.parts) > 2:
        for i in range(2, len(path.parts)):
            current = pathlib.Path(path.parts[0]).joinpath(*path.parts[1:i + 1])
            if _is_valid_project_model_path(current):
                return current
    return None


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


def get_contextual_file_type(path: pathlib.Path) -> FileContentType:
    """Return the file content type for files in the given directory, if it's a trestle workspace."""
    if not _is_valid_project_model_path(path):
        raise err.TrestleError(f'Trestle workspace not found at path {path}')

    for file_or_directory in iterdir_without_hidden_files(path):
        if file_or_directory.is_file():
            return FileContentType.to_content_type(file_or_directory.suffix)

    for file_or_directory in path.iterdir():
        if file_or_directory.is_dir():
            return get_contextual_file_type(file_or_directory)

    raise err.TrestleError('No files found in the project.')


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


def insert_text_in_file(file_path: pathlib.Path, tag: Optional[str], text: str) -> bool:
    r"""Insert text lines after line containing tag.

    Return True on success, False tag not found.
    Text is a string with appropriate \n line endings.
    If tag is none just add at end of file.
    This will only open file once if tag is not found.
    """
    if not file_path.exists():
        raise TrestleError(f'Test file {file_path} not found.')
    if tag:
        lines: List[str] = []
        with file_path.open('r', encoding=const.FILE_ENCODING) as f:
            lines = f.readlines()
        for ii, line in enumerate(lines):
            if line.find(tag) >= 0:
                lines.insert(ii + 1, text)
                with file_path.open('w', encoding=const.FILE_ENCODING) as f:
                    f.writelines(lines)
                return True
    else:
        with file_path.open('a', encoding=const.FILE_ENCODING) as f:
            f.writelines(text)
        return True
    return False


def prune_empty_dirs(file_path: pathlib.Path, pattern: str) -> None:
    """Remove directories with no subdirs and with no files matching pattern."""
    deleted: Set[str] = set()
    # this traverses from leaf nodes upward so only needs one traversal
    for current_dir, subdirs, _ in os.walk(str(file_path), topdown=False):
        true_dirs = [subdir for subdir in subdirs if os.path.join(current_dir, subdir) not in deleted]
        if not true_dirs and not any(glob.glob(f'{current_dir}/{pattern}')):
            shutil.rmtree(current_dir)
            deleted.add(current_dir)
