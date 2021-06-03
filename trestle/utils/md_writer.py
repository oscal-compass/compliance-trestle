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
"""Create formatted markdown files with optional yaml header."""

import logging
import pathlib
from typing import Any, List

from trestle.core.err import TrestleError

import yaml

logger = logging.getLogger(__name__)


class MDWriter():
    """Simple class to create markdown files."""

    def __init__(self, file_path: pathlib.Path):
        """Initialize the class."""
        self._file_path = file_path
        self._lines = []
        self._indent_level = 0
        self._indent_size = 2
        self._yaml_header = None

    def _current_indent_space(self):
        if self._indent_level <= 0:
            return ''
        return ' ' * (self._indent_level * self._indent_size + 2)

    def _add_line_raw(self, line: str) -> None:
        self._lines.append(line)

    def _add_indent_level(self, delta: int) -> None:
        self._indent_level += delta

    def add_yaml_header(self, header: dict) -> None:
        """Add the yaml header."""
        self._yaml_header = header

    def set_indent_level(self, level: int) -> None:
        """Set the current indent level."""
        self._indent_level = level

    def set_indent_step_size(self, size: int) -> None:
        """Set the indent step size in spaces."""
        self._indent_size = size

    def new_line(self, line: str) -> None:
        """Add a line of text to the output."""
        self._add_line_raw(self._current_indent_space() + line)

    def new_paragraph(self):
        """Start a new paragraph."""
        self._lines.append('')

    def new_header(self, level: int, title: str) -> None:
        """Add new header."""
        self.new_line('#' * level + ' ' + title)

    def new_hr(self) -> None:
        """Add horizontal rule."""
        self.new_line('---')

    def new_list(self, list_: List[Any], show=True) -> None:
        """Add a list to the markdown."""
        # if string just write it out
        if isinstance(list_, str):
            self.new_line(list_)
        # it is a list with more than one item
        else:
            self._add_indent_level(1)
            self.new_paragraph()
            for item in list_:
                self.new_list(item, show)
            self._add_indent_level(-1)

    def write_out(self) -> None:
        """Write out the markdown file."""
        try:
            with open(self._file_path, 'w', encoding='utf-8') as f:
                # Make sure yaml header is written first
                if self._yaml_header is not None:
                    f.write('---\n')
                    header_str = yaml.dump(self._yaml_header, default_flow_style=False)
                    f.write(header_str)
                    f.write('---\n\n')

                f.write('\n'.join(self._lines))
        except IOError as e:
            logger.debug(f'md_writer error attempting to write out md file {self._file_path} {e}')
            raise TrestleError(f'Error attempting to write out md file {self._file_path} {e}')
