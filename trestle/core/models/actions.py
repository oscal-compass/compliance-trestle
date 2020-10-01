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

from trestle.core.err import TrestleError
from trestle.utils import fs

from .elements import Element, ElementPath


class ActionType(Enum):
    """Action type enum for different action type.

    File system related actions starts with 1
    Model processing related actions starts with 2 or higher
    """

    # write element to a destination file or stream
    WRITE = 10

    # read element from a source file or stream
    READ = 11

    # append element to a source file or stream
    APPEND = 12

    # delete a source file, directory or stream
    DELETE = 13

    # add the element at the path in the destination
    ADD = 20

    # remove the element at the path in the destination
    REMOVE = 21

    # update the element at the path in the destination
    UPDATE = 22


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

    def to_string(self) -> str:
        """Return a string representation."""
        return self.__str__()

    def get_type(self) -> ActionType:
        """Return the action type."""
        return self._type

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


class ReadAction(Action):
    """Read the element from a destination stream."""

    def __init__(self, reader: io.BufferedReader, element: Element):
        """Initialize a read file action."""
        super().__init__(ActionType.READ, True)

        self._reader: str = reader
        self._element: Element = element

    def execute(self):
        """Execute the action."""

    def rollback(self):
        """Rollback the action."""
        raise NotImplementedError('Not implemented')

    def __str__(self):
        """Return string representation."""
        return f'{self._type} {self._element}'


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


class ReadFileAction(Action):
    """Read the element from a destination file."""

    def __init__(self, file_path: str, element: Element):
        """Initialize a read file action."""
        super().__init__(self, ActionType.READ, True)

        self._file_path: str = file_path
        self._element: Element = element

    def execute(self):
        """Execute the action."""

    def rollback(self):
        """Rollback the action."""
        raise NotImplementedError('Not implemented')

    def __str__(self):
        """Return string representation."""
        return f'{self._type} {self._element} to {self._file_path}'


class AddAction(Action):
    """Add element at the element path in the destination element from the source element."""

    def __init__(self, src_element: Element, dest_element: Element, element_path: ElementPath):
        """Initialize an add element action."""
        super().__init__(self, ActionType.ADD, True)

        self._src_element: Element = src_element
        self._dest_element: Element = dest_element
        self._element_path: ElementPath = element_path

    def execute(self):
        """Execute the action."""
        self._dest_element.set_at(self._src_element, self._element_path)

    def rollback(self):
        """Rollback the action."""
        self._dest_element.set_at(None, self._element_path)

    def __str__(self):
        """Return string representation."""
        return f'{self._type} {self._src_element} to {self._dest_element} at {self._element_path}'


class RemoveAction(Action):
    """Remove element at the element path in the source element and store into the destination."""

    def __init__(self, src_element: Element, dest_element: Element, element_path: ElementPath):
        """Initialize a remove element action."""
        super().__init__(self, ActionType.REMOVE, True)

        self._src_element: Element = src_element
        self._dest_element: Element = dest_element
        self._element_path: ElementPath = element_path

    def execute(self):
        """Execute the action."""

    def rollback(self):
        """Rollback the action."""
        raise NotImplementedError('Not implemented')

    def __str__(self):
        """Return string representation."""
        return f'{self._type} {self._src_element} from {self._dest_element} at {self._element_path}'


class UpdateAction(Action):
    """Update element at the element path in the destination element from the source element."""

    def __init__(self, src_element: Element, dest_element: Element, element_path: ElementPath):
        """Initialize an add element action."""
        super().__init__(self, ActionType.UPDATE, True)

        self._src_element: Element = src_element
        self._dest_element: Element = dest_element
        self._element_path: ElementPath = element_path

    def execute(self):
        """Execute the action."""

    def rollback(self):
        """Rollback the action."""
        raise NotImplementedError('Not implemented')

    def __str__(self):
        """Return string representation."""
        return f'{self._type} {self._src_element} in {self._dest_element} at {self._element_path}'
