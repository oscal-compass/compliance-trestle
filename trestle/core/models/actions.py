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
import os
import pathlib
from abc import ABC, abstractmethod
from enum import Enum
from typing import List

from trestle.core.err import TrestleError
from trestle.utils import fs

from .elements import Element, ElementPath


class ActionType(Enum):
    """Action type enum for different action type.

    File system related actions have code like 1*
    Model processing related actions have code like 2*
    """

    # write element to a destination file or stream
    WRITE = 10

    # append element to a source file or stream
    APPEND = 11

    # create a file or directory path
    CREATE_PATH = 16

    # update or add the element at the path
    UPDATE = 20

    # remove the element at the path
    REMOVE = 21


class FileContentType(Enum):
    """File Content type for read/write."""

    # JSON formatted content
    JSON = 1

    # YAML formatted content
    YAML = 2


class Action(ABC):
    """Action wrapper of a command."""

    def __init__(self, action_type: ActionType, has_rollback: bool):
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

    def _mark_executed(self):
        """Set flag that the action has been executed."""
        self._has_executed = True

    def has_executed(self):
        """Return if the action has been executed."""
        return self._has_executed

    def _mark_rollback(self):
        """Set flag that the action has been rollbacked."""
        self._has_executed = False

    def has_rollback(self) -> bool:
        """Return if rollback of the action is possible."""
        return self._has_rollback

    @abstractmethod
    def execute(self):
        """Execute the action."""

    @abstractmethod
    def rollback(self):
        """Rollback the action."""


class WriteAction(Action):
    """Write the element to a destination stream."""

    def __init__(self, writer: io.BufferedWriter, element: Element, content_type: FileContentType):
        """Initialize an write file action."""
        super().__init__(ActionType.WRITE, True)

        self._writer: io.BufferedWriter = writer
        self._element: Element = element
        self._content_type: FileContentType = content_type
        self._lastStreamPos = self._writer.tell()

    def _encode(self) -> str:
        """Encode the element to appropriate content type."""
        if self._content_type == FileContentType.YAML:
            return self._element.to_yaml()
        elif self._content_type == FileContentType.JSON:
            return self._element.to_json()

        raise TrestleError(f'Invalid content type {self._content_type}')

    def execute(self):
        """Execute the action."""
        if self._element is None:
            raise TrestleError('Element is empty and cannot write')

        if self._writer is None or self._writer.closed:
            raise TrestleError('Writer is not provided or closed')

        self._writer.write(self._encode())
        self._writer.flush()

    def rollback(self):
        """Rollback the action."""
        if self._writer is None or self._writer.closed:
            raise TrestleError('Writer is not provided or closed')

        if self._lastStreamPos is None:
            raise TrestleError('Last stream position is not available to rollback to')

        self._writer.seek(self._lastStreamPos)
        self._writer.truncate()

    def __str__(self):
        """Return string representation."""
        return f'{self.get_type()} {self._element}'


class WriteFileAction(WriteAction):
    """Write the element to a destination file."""

    def __init__(self, file_path: str, element: Element, content_type: FileContentType):
        """Initialize a write file action.

        It will create a new file to write to
        """
        self._file_path = self._fix_file_extension(file_path, content_type)

        self._created_file = False
        if os.path.isfile(self._file_path) is False:
            self._created_file = True
            fs.ensure_directory(pathlib.Path(self._file_path).parent.absolute())

        with open(self._file_path, 'a+') as writer:
            super().__init__(writer, element, content_type)

    def _fix_file_extension(self, file_path: str, content_type: FileContentType) -> str:
        file_name, file_extension = os.path.splitext(file_path)
        if content_type == FileContentType.JSON:
            if file_extension != '.json':
                file_path = file_name + '.json'
        elif content_type == FileContentType.YAML:
            if file_extension != '.yaml':
                file_path = file_name + '.yaml'
        else:
            raise TrestleError(f'Unsupported content type {content_type}')

        return file_path

    def execute(self):
        """Execute the action."""
        with open(self._file_path, 'a+') as writer:
            writer.seek(self._lastStreamPos)
            self._writer = writer
            super().execute()

    def rollback(self):
        """Execute the rollback action."""
        if self._created_file and os.path.isfile(self._file_path):
            # if it was a new file, just delete the file
            os.remove(self._file_path)
        else:
            with open(self._file_path, 'a+') as writer:
                self._writer = writer
                super().rollback()

    def __str__(self):
        """Return string representation."""
        return f'{self._type} {self._element} to "{self._file_path}"'


class AppendFileAction(WriteFileAction):
    """Append the element to a destination file."""

    def __init__(self, file_path: str, element: Element, content_type: FileContentType):
        """Initialize a write file action.

        If the file exists, it will append otherwise it will raise exception
        """
        if os.path.isfile(file_path) is False:
            raise TrestleError(f'The file {file_path} does not exists')

        super().__init__(file_path, element, content_type)


class CreatePathAction(Action):
    """Create a file or directory path."""

    def __init__(self, sub_path: pathlib.Path):
        """Initialize a create path action.

        It creates all the missing directories in the path.
        If it is a file, then it also creates an empty file with the name provided

        Arguments:
            sub_path: this is the desired file or directory path that needs to be created under the project root
        """
        if not isinstance(sub_path, pathlib.Path):
            raise TrestleError('Sub path must be of type pathlib.Path')

        self._trestle_project_root = fs.get_trestle_project_root(sub_path)
        if self._trestle_project_root is None:
            raise TrestleError('Sub path should be child of a valid trestle project')

        self._sub_path = sub_path
        self._created_paths: List[pathlib.Path] = []
        super().__init__(ActionType.CREATE_PATH, True)

    def get_trestle_project_root(self):
        """Return the trestle project root path."""
        return self._trestle_project_root

    def get_created_paths(self) -> List[pathlib.Path]:
        """Get the list of paths that were created after being executed."""
        return self._created_paths

    def execute(self):
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

            # create the sub_path if it does not exists already
            if not cur_path.exists():
                if cur_path.suffix != '':
                    # create file
                    cur_path.touch()
                else:
                    # create directory
                    cur_path.mkdir()

                # add in the list for rollback
                self._created_paths.append(cur_path)

            # move to the next part of the sub_path parts
            cur_index = cur_index + 1

        self._mark_executed()

    def rollback(self):
        """Rollback the action."""
        if self.has_executed() and len(self._created_paths) > 0:
            for cur_path in reversed(self._created_paths):
                if cur_path.exists():
                    if cur_path.is_file():
                        cur_path.unlink()
                    elif cur_path.is_dir():
                        cur_path.rmdir()
            self._created_paths.clear()
        self._mark_rollback()

    def __str__(self):
        """Return string representation."""
        return f'{self._type} {self._sub_path}'


class UpdateAction(Action):
    """Update element at the element path in the destination element with the source element."""

    def __init__(self, sub_element, dest_element: Element, sub_element_path: ElementPath):
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

    def execute(self):
        """Execute the action."""
        self._prev_sub_element = self._dest_element.get_at(self._sub_element_path)
        self._dest_element.set_at(self._sub_element_path, self._sub_element)
        self._mark_executed()

    def rollback(self):
        """Rollback the action."""
        if self.has_executed():
            self._dest_element.set_at(self._sub_element_path, self._prev_sub_element)
        self._mark_rollback()

    def __str__(self):
        """Return string representation."""
        return f'{self._type} {self._model_obj.__class__} to {self._dest_element} at {self._sub_element_path}'


class RemoveAction(Action):
    """Remove sub element at the element path in the source element."""

    def __init__(self, src_element: Element, sub_element_path: ElementPath):
        """Initialize a remove element action."""
        super().__init__(ActionType.REMOVE, True)

        self._src_element: Element = src_element
        self._sub_element_path: ElementPath = sub_element_path
        self._prev_sub_element = None

    def execute(self):
        """Execute the action."""
        self._prev_sub_element = self._src_element.get_at(self._sub_element_path)
        self._src_element.set_at(self._sub_element_path, None)
        self._mark_executed()

    def rollback(self):
        """Rollback the action."""
        if self.has_executed():
            self._src_element.set_at(self._sub_element_path, self._prev_sub_element)
        self._mark_rollback()

    def __str__(self):
        """Return string representation."""
        return f'{self._type} element at {self._sub_element_path} from {self._src_element}'
