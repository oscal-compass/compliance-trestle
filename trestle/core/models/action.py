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

import enum
import io
from abc import ABC, abstractmethod

from .element import Element, ElementPath


class ActionType(enum):
    """Action type enum for different action type."""

    # write element to a destination file or stream
    WRITE = 1

    # read element from a source file or stream
    READ = 2

    # add the element at the path in the destination
    ADD = 3

    # remove the element at the path in the destination
    REMOVE = 4

    # update the element at the path in the destination
    UPDATE = 5


class Action(ABC):
    """Action wrapper of a command."""

    def __init__(self, action_type: ActionType):
        """Initialize an base action."""
        self._type: ActionType = action_type

    def get_type(self) -> ActionType:
        """Return the action type."""
        return self._type

    @abstractmethod
    def execute(self):
        """Execute the action."""

    @abstractmethod
    def rollback(self):
        """Rollback the action."""


class WriteAction(Action):
    """Write the element to a destination stream."""

    def __init__(self, writer: io.BufferedWriter, element: Element):
        """Initialize an write file action."""
        super.__init__(self, ActionType.WRITE)

        self._writer: str = writer
        self._element: Element = element

    def execute(self):
        """Execute the action."""

    def rollback(self):
        """Rollback the action."""
        raise NotImplementedError('Not implemented')


class ReadAction(Action):
    """Read the element from a destination stream."""

    def __init__(self, reader: io.BufferedReader, element: Element):
        """Initialize a read file action."""
        super.__init__(self, ActionType.READ)

        self._reader: str = reader
        self._element: Element = element

    def execute(self):
        """Execute the action."""

    def rollback(self):
        """Rollback the action."""
        raise NotImplementedError('Not implemented')


class WriteFileAction(Action):
    """Write the element to a destination file."""

    def __init__(self, file_path: str, element: Element):
        """Initialize an write file action."""
        super.__init__(self, ActionType.WRITE)

        self._file_path: str = file_path
        self._element: Element = element

    def execute(self):
        """Execute the action."""

    def rollback(self):
        """Rollback the action."""
        raise NotImplementedError('Not implemented')


class ReadFileAction(Action):
    """Read the element from a destination file."""

    def __init__(self, file_path: str, element: Element):
        """Initialize a read file action."""
        super.__init__(self, ActionType.READ)

        self._file_path: str = file_path
        self._element: Element = element

    def execute(self):
        """Execute the action."""

    def rollback(self):
        """Rollback the action."""
        raise NotImplementedError('Not implemented')


class AddAction(Action):
    """Add element at the element path in the destination element from the source element."""

    def __init__(self, src_element: Element, dest_element: Element, element_path: ElementPath):
        """Initialize an add element action."""
        super.__init__(self, ActionType.ADD)

        self._src_element: Element = src_element
        self._dest_element: Element = dest_element
        self._element_path: ElementPath = element_path

    def execute(self):
        """Execute the action."""

    def rollback(self):
        """Rollback the action."""
        raise NotImplementedError('Not implemented')


class RemoveAction(Action):
    """Remove element at the element path in the source element and store into the destination."""

    def __init__(self, src_element: Element, dest_element: Element, element_path: ElementPath):
        """Initialize a remove element action."""
        super.__init__(self, ActionType.REMOVE)

        self._src_element: Element = src_element
        self._dest_element: Element = dest_element
        self._element_path: ElementPath = element_path

    def execute(self):
        """Execute the action."""

    def rollback(self):
        """Rollback the action."""
        raise NotImplementedError('Not implemented')


class UpdateAction(Action):
    """Update element at the element path in the destination element from the source element."""

    def __init__(self, src_element: Element, dest_element: Element, element_path: ElementPath):
        """Initialize an add element action."""
        super.__init__(self, ActionType.UPDATE)

        self._src_element: Element = src_element
        self._dest_element: Element = dest_element
        self._element_path: ElementPath = element_path

    def execute(self):
        """Execute the action."""

    def rollback(self):
        """Rollback the action."""
        raise NotImplementedError('Not implemented')
