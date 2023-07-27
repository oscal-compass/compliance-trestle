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
"""Handle writing of inherited statements to markdown."""
import logging
import pathlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import trestle.common.const as const
from trestle.core.markdown.md_writer import MDWriter

logger = logging.getLogger(__name__)


class LeveragedStatements(ABC):
    """Abstract class for managing leveraged statements."""

    def __init__(self):
        """Initialize the class."""
        self._md_file: Optional[MDWriter] = None
        self.header_comment_dict: Dict[str, str] = {}
        self.header_comment_dict[const.TRESTLE_LEVERAGING_COMP_TAG] = const.YAML_LEVERAGING_COMP_COMMENT
        self.header_comment_dict[const.TRESTLE_STATEMENT_TAG] = const.YAML_LEVERAGED_COMMENT
        self.merged_header_dict: Dict[str, Any] = {}
        self.merged_header_dict[const.TRESTLE_STATEMENT_TAG] = ''
        self.merged_header_dict[const.TRESTLE_LEVERAGING_COMP_TAG] = {const.NAME: const.REPLACE_ME}

    @abstractmethod
    def write_statement_md(self, leveraged_statement_file: pathlib.Path) -> None:
        """Write inheritance information to a single markdown file."""


class StatementTree(LeveragedStatements):
    """Concrete class for managing provided and responsibility statements."""

    def __init__(
        self,
        provided_uuid: str,
        provided_description: str,
        responsibility_uuid: str,
        responsibility_description: str,
    ):
        """Initialize the class."""
        self.provided_uuid = provided_uuid
        self.provided_description = provided_description
        self.responsibility_uuid = responsibility_uuid
        self.responsibility_description = responsibility_description
        self.satisfied_description = const.REPLACE_ME
        super().__init__()

    def write_statement_md(self, leveraged_statement_file: pathlib.Path) -> None:
        """Write a provided and responsibility statements to a markdown file."""
        self._md_file = MDWriter(leveraged_statement_file, self.header_comment_dict)

        statement_dict: Dict[str, str] = {}
        statement_dict[const.PROVIDED_UUID] = self.provided_uuid
        statement_dict[const.RESPONSIBILITY_UUID] = self.responsibility_uuid

        self.merged_header_dict[const.TRESTLE_STATEMENT_TAG] = statement_dict
        self._md_file.add_yaml_header(self.merged_header_dict)

        self._md_file.new_header(level=1, title=const.PROVIDED_STATEMENT_DESCRIPTION)
        self._md_file.new_line(self.provided_description)
        self._md_file.new_header(level=1, title=const.RESPONSIBILITY_STATEMENT_DESCRIPTION)
        self._md_file.new_line(self.responsibility_description)
        self._md_file.new_header(level=1, title=const.SATISFIED_STATEMENT_DESCRIPTION)
        self._md_file.new_line(const.SATISFIED_STATEMENT_COMMENT)
        self._md_file.new_line(self.satisfied_description)

        self._md_file.write_out()


class StatementProvided(LeveragedStatements):
    """Concrete class for managing provided statements."""

    def __init__(self, provided_uuid: str, provided_description: str):
        """Initialize the class."""
        self.provided_uuid = provided_uuid
        self.provided_description = provided_description
        super().__init__()

    def write_statement_md(self, leveraged_statement_file: pathlib.Path) -> None:
        """Write provided statements to a markdown file."""
        self._md_file = MDWriter(leveraged_statement_file, self.header_comment_dict)

        self.merged_header_dict[const.TRESTLE_STATEMENT_TAG] = {const.PROVIDED_UUID: self.provided_uuid}
        self._md_file.add_yaml_header(self.merged_header_dict)

        self._md_file.new_header(level=1, title=const.PROVIDED_STATEMENT_DESCRIPTION)
        self._md_file.new_line(self.provided_description)
        self._md_file.write_out()


class StatementResponsibility(LeveragedStatements):
    """Concrete class for managing responsibility statements."""

    def __init__(self, responsibility_uuid: str, responsibility_description: str):
        """Initialize the class."""
        self.responsibility_uuid = responsibility_uuid
        self.responsibility_description = responsibility_description
        self.satisfied_description = const.REPLACE_ME

        super().__init__()

    def write_statement_md(self, leveraged_statement_file: pathlib.Path) -> None:
        """Write responsibility statements to a markdown file."""
        self._md_file = MDWriter(leveraged_statement_file, self.header_comment_dict)

        self.merged_header_dict[const.TRESTLE_STATEMENT_TAG] = {const.RESPONSIBILITY_UUID: self.responsibility_uuid}
        self._md_file.add_yaml_header(self.merged_header_dict)

        self._md_file.new_header(level=1, title=const.RESPONSIBILITY_STATEMENT_DESCRIPTION)
        self._md_file.new_line(self.responsibility_description)
        self._md_file.new_header(level=1, title=const.SATISFIED_STATEMENT_DESCRIPTION)
        self._md_file.new_line(const.SATISFIED_STATEMENT_COMMENT)
        self._md_file.new_line(self.satisfied_description)

        self._md_file.write_out()
