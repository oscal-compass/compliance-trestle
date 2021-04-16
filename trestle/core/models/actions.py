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
"""Action wrapper of a command."""

import io
import pathlib
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

from trestle.core.err import TrestleError
from trestle.utils import fs, trash

from .elements import Element, ElementPath
from .file_content_type import FileContentType


class ActionType(Enum):
    """Action type enum for different action type.

    File system related actions have code like 1*
    Model processing related actions have code like 2*
    """

    # create a file or directory path
    CREATE_PATH = 10

    # remove a file or directory path
    REMOVE_PATH = 12

    # write element to a destination file or stream
    WRITE = 11

    # update or add the element at the path
    UPDATE = 20

    # remove the element at the path
    REMOVE = 21


class Action(ABC):
    """Action wrapper of a command."""

    def __init__(self, action_type: ActionType, has_rollback: bool) -> None:
        """Initialize an base action."""
        self._type: ActionType = action_type
        self._has_rollback: bool = has_rollback

        # child class must set this flag once it executes
        self._has_executed = False

    def to_string(self) -> str:
        """Return a string representation."""
        return self.__str__()

    def get_type(self) -> ActionType:
        """Return the action type."""
        return self._type

    def _mark_executed(self) -> None:
        """Set flag that the action has been executed."""
        self._has_executed = True

    def has_executed(self) -> bool:
        """Return if the action has been executed."""
        return self._has_executed

    def _mark_rollback(self) -> None:
        """Set flag that the action has been rollbacked."""
        self._has_executed = False

    def has_rollback(self) -> bool:
        """Return if rollback of the action is possible."""
        return self._has_rollback

    def __eq__(self, other: object) -> bool:
        """Check that two actions are equal."""
        if not isinstance(other, Action):
            return False
        if self.get_type() is not other.get_type():
            return False
        is_eq = self.__dict__ == other.__dict__
        return is_eq

    @abstractmethod
    def execute(self) -> None:
        """Execute the action."""

    @abstractmethod
    def rollback(self) -> None:
        """Rollback the action."""


class WriteAction(Action):
    """Write the element to a destination stream."""

    def __init__(self, writer: Optional[io.TextIOWrapper], element: Element, content_type: FileContentType) -> None:
        """Initialize an write file action."""
        super().__init__(ActionType.WRITE, True)

        if writer is not None and not issubclass(io.TextIOWrapper, writer.__class__):
            raise TrestleError(f'Writer must be of io.TextIOWrapper, given f{writer.__class__}')

        self._writer: Optional[io.TextIOWrapper] = writer
        self._element: Element = element
        self._content_type: FileContentType = content_type
        self._lastStreamPos = -1
        if self._writer is not None:
            self._lastStreamPos = self._writer.tell()

    def _is_writer_valid(self) -> bool:
        if self._writer is not None and isinstance(self._writer, io.TextIOWrapper) and not self._writer.closed:
            return True

        return False

    def _encode(self) -> str:
        """Encode the element to appropriate content type."""
        if self._content_type == FileContentType.YAML:
            return self._element.to_yaml()
        elif self._content_type == FileContentType.JSON:
            return self._element.to_json()

        raise TrestleError(f'Invalid content type {self._content_type}')

    def execute(self) -> None:
        """Execute the action."""
        if self._element is None:
            raise TrestleError('Element is empty and cannot write')

        if not self._is_writer_valid():
            raise TrestleError('Writer is not provided or closed')

        self._writer.write(self._encode())
        self._writer.flush()
        self._mark_executed()

    def rollback(self) -> None:
        """Rollback the action."""
        if not self._is_writer_valid():
            raise TrestleError('Writer is not provided or closed')

        if self._lastStreamPos < 0:
            raise TrestleError('Last stream position is not available to rollback to')

        if self.has_executed():
            self._writer.seek(self._lastStreamPos)
            self._writer.truncate()

        self._mark_rollback()

    def __str__(self) -> str:
        """Return string representation."""
        return f'{self.get_type()} {self._element}'


class WriteFileAction(WriteAction):
    """Write the element to a destination file."""

    def __init__(self, file_path: pathlib.Path, element: Element, content_type: FileContentType) -> None:
        """Initialize a write file action.

        It opens the file in append mode. Therefore the file needs to exist even if it is a new file.
        """
        if not isinstance(file_path, pathlib.Path):
            raise TrestleError('file_path should be of type pathlib.Path')

        inferred_content_type = FileContentType.to_content_type(file_path.suffix)
        if inferred_content_type != content_type:
            raise TrestleError(f'Mismatch between stated content type {content_type.name} and file path {file_path}')

        self._file_path = file_path

        # initialize super without writer for now
        # Note, execute and rollback sets the writer as appropriate
        super().__init__(None, element, content_type)

    def execute(self) -> None:
        """Execute the action."""
        if not self._file_path.exists():
            raise TrestleError(f'File at {self._file_path} does not exist')

        with open(self._file_path, 'a+') as writer:
            if self._lastStreamPos < 0:
                self._lastStreamPos = writer.tell()
            else:
                writer.seek(self._lastStreamPos)

            self._writer = writer
            super().execute()

    def rollback(self) -> None:
        """Execute the rollback action."""
        if not self._file_path.exists():
            raise TrestleError(f'File at {self._file_path} does not exist')

        with open(self._file_path, 'a+') as writer:
            self._writer = writer
            super().rollback()

    def __str__(self) -> str:
        """Return string representation."""
        return f'{self._type} {self._element} to "{self._file_path}"'


class CreatePathAction(Action):
    """Create a file or directory path."""

    def __init__(self, sub_path: pathlib.Path, clear_content: bool = False) -> None:
        """Initialize a create path action.

        It creates all the missing directories in the path.
        If it is a file, then it also creates an empty file with the name provided

        Arguments:
            sub_path: this is the desired file or directory path that needs to be created under the project root
        """
        if not isinstance(sub_path, pathlib.Path):
            raise TrestleError('Sub path must be of type pathlib.Path')

        sub_path = sub_path.resolve()

        self._trestle_project_root = fs.get_trestle_project_root(sub_path)
        if self._trestle_project_root is None:
            raise TrestleError(f'Sub path "{sub_path}" should be child of a valid trestle project')

        self._sub_path = sub_path
        self._created_paths: List[pathlib.Path] = []

        # variables for handling with file content
        self._clear_content = clear_content
        self._old_file_content = None

        super().__init__(ActionType.CREATE_PATH, True)

    def get_trestle_project_root(self) -> pathlib.Path:
        """Return the trestle project root path."""
        return self._trestle_project_root

    def get_created_paths(self) -> List[pathlib.Path]:
        """Get the list of paths that were created after being executed."""
        return self._created_paths

    def execute(self) -> None:
        """Execute the action."""
        # find the start of the sub_path relative to trestle project root
        cur_index = len(self._trestle_project_root.parts)

        # loop through the sub_path parts and create as necessary
        cur_path = self._trestle_project_root
        while cur_index < len(self._sub_path.parts):
            part = self._sub_path.parts[cur_index]

            # create a path relative to the current
            # it starts with the project root, so we shall always create
            # sub directories or files relative to the project root
            cur_path = cur_path.joinpath(part)

            # create the sub_path file or directory if it does not exists already
            if cur_path.suffix != '':  # suffix will denote a file
                if not cur_path.exists():
                    # create file
                    cur_path.touch()

                    # add in the list for rollback
                    self._created_paths.append(cur_path)
                elif self._clear_content:
                    # read file content for rollback
                    with open(cur_path, 'r+') as fp:
                        # read all content
                        self._old_file_content = fp.read()

                        # clear file content
                        fp.truncate(0)
            else:
                if not cur_path.exists():
                    # create directory
                    cur_path.mkdir()

                    # add in the list for rollback
                    self._created_paths.append(cur_path)

            # move to the next part of the sub_path parts
            cur_index = cur_index + 1

        self._mark_executed()

    def rollback(self) -> None:
        """Rollback the action."""
        if self.has_executed():
            if len(self._created_paths) > 0:
                for cur_path in reversed(self._created_paths):
                    if cur_path.exists():
                        if cur_path.is_file():
                            cur_path.unlink()
                        elif cur_path.is_dir():
                            cur_path.rmdir()

                self._created_paths.clear()

            # rollback the content of a file if required
            # we should be here only if there were no path created and the sub_part already existed
            elif self._sub_path.is_file() and self._sub_path.exists() and self._clear_content is True:
                if self._old_file_content is not None:
                    with open(self._sub_path, 'w') as fp:
                        fp.write(self._old_file_content)

        self._mark_rollback()

    def __str__(self) -> str:
        """Return string representation."""
        return f'{self._type} {self._sub_path}'


class RemovePathAction(Action):
    """Remove a file or directory path."""

    def __init__(self, sub_path: pathlib.Path) -> None:
        """Initialize a remove path action.

        It removes the file or directory recursively into trash.

        Arguments:
            sub_path: this is the desired file or directory path that needs to be removed under the project root
        """
        if not isinstance(sub_path, pathlib.Path):
            raise TrestleError('Sub path must be of type pathlib.Path')

        self._trestle_project_root = fs.get_trestle_project_root(sub_path)
        if self._trestle_project_root is None:
            raise TrestleError(f'Sub path "{sub_path}" should be child of a valid trestle project')

        self._sub_path = sub_path

        super().__init__(ActionType.REMOVE_PATH, True)

    def get_trestle_project_root(self) -> Optional[pathlib.Path]:
        """Return the trestle project root path."""
        return self._trestle_project_root

    def execute(self) -> None:
        """Execute the action."""
        if not self._sub_path.exists():
            raise FileNotFoundError(f'Path "{self._sub_path}" does not exist')

        trash.store(self._sub_path, True)
        self._mark_executed()

    def rollback(self) -> None:
        """Rollback the action."""
        if self.has_executed():
            trash_path = trash.to_trash_path(self._sub_path)
            if trash_path is None or trash_path.exists() is False:
                # FIXME suppress file contents not found message til trash/rollback behavior is fixed.  # issue 412
                return
            trash.recover(self._sub_path, True)

        self._mark_rollback()

    def __str__(self) -> str:
        """Return string representation."""
        return f'{self._type} {self._sub_path}'


class UpdateAction(Action):
    """Update element at the element path in the destination element with the source element."""

    def __init__(self, sub_element, dest_element: Element, sub_element_path: ElementPath) -> None:
        """Initialize an add element action.

        Sub element can be OscalBaseModel, Element, list or None
        """
        super().__init__(ActionType.UPDATE, True)

        if not Element.is_allowed_sub_element_type(sub_element):
            allowed_types = Element.get_allowed_sub_element_types()
            raise TrestleError(
                f'Sub element "{sub_element.__class__} is not a allowed sub element types in "{allowed_types}"'
            )

        self._sub_element = sub_element
        self._dest_element: Element = dest_element
        self._sub_element_path: ElementPath = sub_element_path
        self._prev_sub_element = None

    def execute(self) -> None:
        """Execute the action."""
        self._prev_sub_element = self._dest_element.get_at(self._sub_element_path)
        self._dest_element.set_at(self._sub_element_path, self._sub_element)
        self._mark_executed()

    def rollback(self) -> None:
        """Rollback the action."""
        if self.has_executed():
            self._dest_element.set_at(self._sub_element_path, self._prev_sub_element)
        self._mark_rollback()

    def __str__(self) -> str:
        """Return string representation."""
        return f'{self._type} {self._model_obj.__class__} to {self._dest_element} at {self._sub_element_path}'


class RemoveAction(Action):
    """Remove sub element at the element path in the source element."""

    def __init__(self, src_element: Element, sub_element_path: ElementPath) -> None:
        """Initialize a remove element action."""
        super().__init__(ActionType.REMOVE, True)

        self._src_element: Element = src_element
        self._sub_element_path: ElementPath = sub_element_path
        self._prev_sub_element = None

    def execute(self) -> None:
        """Execute the action."""
        self._prev_sub_element = self._src_element.get_at(self._sub_element_path)
        self._src_element.set_at(self._sub_element_path, None)
        self._mark_executed()

    def rollback(self) -> None:
        """Rollback the action."""
        if self.has_executed():
            self._src_element.set_at(self._sub_element_path, self._prev_sub_element)
        self._mark_rollback()

    def __str__(self) -> str:
        """Return string representation."""
        return f'{self._type} element at {self._sub_element_path} from {self._src_element}'
