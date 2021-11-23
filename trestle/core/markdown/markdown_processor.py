# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""A markdown processor."""
import logging
import pathlib
import traceback
from typing import Dict, Optional, Tuple

import cmarkgfm

import frontmatter

from trestle.core import const
from trestle.core.err import TrestleError
from trestle.core.markdown.markdown_node import MarkdownNode

from yaml.scanner import ScannerError

logger = logging.getLogger(__name__)


class MarkdownProcessor:
    """A markdown processor."""

    def __init__(self) -> None:
        """Initialize markdown processor."""
        self.governed_header = None

    def render_gfm_to_html(self, markdown_text: str) -> str:
        """Render given Github Flavored Markdown to HTML."""
        try:
            html = cmarkgfm.github_flavored_markdown_to_html(markdown_text)
            return html
        except ValueError as e:
            raise TrestleError(f'Not a valid Github Flavored markdown: {e}.')

    def process_markdown(self, md_path: pathlib.Path) -> Tuple[Dict, MarkdownNode]:
        """Parse the markdown and builds the tree to operate over it."""
        header, markdown_wo_header = self.read_markdown_wo_processing(md_path)

        _ = self.render_gfm_to_html(markdown_wo_header)

        lines = markdown_wo_header.split('\n')
        tree = MarkdownNode.build_tree_from_markdown(lines, self.governed_header)
        return header, tree

    def read_markdown_wo_processing(self, md_path: pathlib.Path) -> Tuple[Dict, str]:
        """Read markdown header to dictionary and body to string."""
        try:
            contents = frontmatter.loads(md_path.open('r', encoding=const.FILE_ENCODING).read())
            header = contents.metadata
            markdown_wo_header = contents.content

            return header, markdown_wo_header
        except UnicodeDecodeError as e:
            logger.debug(traceback.format_exc())
            raise TrestleError(f'Markdown cannot be decoded into {const.FILE_ENCODING}, error: {e}')
        except ScannerError as e:
            logger.debug(traceback.format_exc())
            raise TrestleError(f'Header is not in a valid YAML format: {e}')
        except FileNotFoundError as e:
            logger.debug(traceback.format_exc())
            raise TrestleError(f'Markdown with path {md_path}, not found: {e}')

    def fetch_value_from_header(self, md_path: pathlib.Path, key: str) -> Optional[str]:
        """Fetch value for the given key from the markdown header if exists."""
        header, _ = self.read_markdown_wo_processing(md_path)
        value = None

        if key in header.keys():
            value = header[key]

        return value
