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
"""Create formatted markdown files with optional yaml header."""

import logging
import pathlib
from typing import Any, Dict, List, Optional

from ruamel.yaml import YAML

import trestle.common.const as const
from trestle.common import file_utils
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_dict
from trestle.core.markdown.markdown_api import MarkdownAPI

logger = logging.getLogger(__name__)


class MDWriter():
    """Simple class to create markdown files."""

    def __init__(self, file_path: pathlib.Path, header_comments_dict: Optional[Dict[str, str]] = None):
        """Initialize the class."""
        self._file_path = file_path
        self._lines = []
        self._indent_level = 0
        self._indent_size = 2
        self._yaml_header = None
        self._header_comments_dict = header_comments_dict

    def _current_indent_space(self):
        if self._indent_level <= 0:
            return ''
        return ' ' * (self._indent_level * self._indent_size)

    def _add_line_raw(self, line: str) -> None:
        out_line = '' if self._is_blank(line) else line
        self._lines.append(out_line)

    def _add_indent_level(self, delta: int) -> None:
        self._indent_level += delta

    def exists(self) -> bool:
        """Check if the file already exists."""
        return self._file_path.exists()

    def add_yaml_header(self, header: dict) -> None:
        """Add the yaml header."""
        self._yaml_header = header

    def set_indent_level(self, level: int) -> None:
        """Set the current indent level."""
        self._indent_level = level

    def set_indent_step_size(self, size: int) -> None:
        """Set the indent step size in spaces."""
        self._indent_size = size

    def _is_blank(self, line: str) -> bool:
        return line.strip() == ''

    def _prev_blank_line(self) -> bool:
        return len(self._lines) > 0 and self._is_blank(self._lines[-1])

    def new_line(self, line: str) -> None:
        """Add a line of text to the output."""
        # prevent double empty lines
        out_line = '' if self._is_blank(line) else self._current_indent_space() + line
        if self._prev_blank_line() and out_line == '':
            return
        self._add_line_raw(out_line)

    def new_paraline(self, line: str) -> None:
        """Add a paragraph and a line to output."""
        self.new_paragraph()
        self.new_line(line)

    def new_paragraph(self):
        """Start a new paragraph."""
        self.new_line('')

    def new_header(self, level: int, title: str, add_new_line_after_header: bool = True) -> None:
        """Add new header."""
        # headers might be separated by blank lines
        self.new_paragraph()
        self.new_line('#' * level + ' ' + title)
        if add_new_line_after_header:
            self.new_paragraph()

    def new_hr(self) -> None:
        """Add horizontal rule."""
        self.new_paragraph()
        self.new_line(const.SSP_MD_HRULE_LINE)
        self.new_paragraph()

    def new_list(self, list_: List[Any]) -> None:
        """Add a list to the markdown."""
        # in general this is a list of lists
        # if string just write it out
        if isinstance(list_, str):
            if self._is_blank(list_):
                self.new_paragraph()
            else:
                self.new_line('- ' + list_)
        # else it is a sublist so indent
        else:
            self._add_indent_level(1)
            self.new_paragraph()
            for item in list_:
                if self._indent_level <= 0:
                    self.new_paragraph()
                self.new_list(item)
            self._add_indent_level(-1)

    def new_table(self, table_list: List[List[str]], header: List[str]):
        """Add table to the markdown. All rows must be of equal length."""
        header_str = '| ' + ' | '.join(header) + ' |'
        sep_str = '|---' * len(header) + '|'
        self.new_line(header_str)
        self.new_line(sep_str)
        for row in table_list:
            row_str = '| ' + ' | '.join(row) + ' |'
            self.new_line(row_str)

    def _check_header(self) -> None:
        while len(self._lines) > 0 and self._lines[0] == '':
            self._lines = self._lines[1:]

    def write_out(self) -> None:
        """Write out the markdown file."""
        self._check_header()
        try:
            self._file_path.parent.mkdir(exist_ok=True, parents=True)
            with open(self._file_path, 'w', encoding=const.FILE_ENCODING) as f:
                # Make sure yaml header is written first
                if self._yaml_header:
                    f.write('---\n')
                    yaml = YAML()
                    yaml.indent(mapping=2, sequence=4, offset=2)
                    yaml.dump(self._yaml_header, f)
                    f.write('---\n\n')

                f.write('\n'.join(self._lines))
                # if last line has text it will need an extra \n at end
                if self._lines and self._lines[-1]:
                    f.write('\n')
            # insert helpful comments into the header happens after header is written out
            for tag, comment in as_dict(self._header_comments_dict).items():
                if tag in as_dict(self._yaml_header):
                    file_utils.insert_text_in_file(self._file_path, tag, comment)
        except IOError as e:
            logger.debug(f'md_writer error attempting to write out md file {self._file_path} {e}')
            raise TrestleError(f'Error attempting to write out md file {self._file_path} {e}')

    def get_lines(self) -> List[str]:
        """Return the current lines in the file."""
        return self._lines

    def get_text(self) -> str:
        """Get the text as currently written."""
        return '\n'.join(self._lines)

    def cull_headings(self, md_in: pathlib.Path, cull_list: List[str], strict_match: bool = False) -> None:
        """
        Cull headers from the lines of input markdown file with optional strict string match.

        Args:
            md_in: the path of the markdown file being edited
            cull_list: the list of strings in headers that are to be culled
            strict_match: whether to require an exact string match on header key or just a substring

        Returns None and creates new markdown at the path specified during MDWriter construction
        It is allowed to overwrite the original file
        """
        markdown_api = MarkdownAPI()
        header, content = markdown_api.processor.process_markdown(md_in)
        self._yaml_header = header
        self._lines = content.delete_nodes_text(cull_list, strict_match)
        self.write_out()
