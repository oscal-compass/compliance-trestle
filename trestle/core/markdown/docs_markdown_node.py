# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2023 IBM Corp. All rights reserved.
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
"""A docs markdown node."""
from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple

import trestle.core.markdown.markdown_const as md_const
from trestle.core.markdown.base_markdown_node import BaseMarkdownNode, BaseSectionContent

logger = logging.getLogger(__name__)


class DocsSectionContent(BaseSectionContent):
    """A content of the node."""

    def __init__(self):
        """Initialize section content."""
        super(DocsSectionContent, self).__init__()
        self.tables = []
        self.text = []
        self.code_lines = []
        self.html_lines = []
        self.blockquotes = []
        self.governed_document = []

    def union(self, node: DocsMarkdownNode) -> None:
        """Unites contents together."""
        super().union(node)
        self.code_lines.extend(node.content.code_lines)
        self.html_lines.extend(node.content.html_lines)
        self.tables.extend(node.content.tables)
        self.blockquotes.extend(node.content.blockquotes)


class DocsMarkdownNode(BaseMarkdownNode):
    """Markdown will be read to the tree."""

    def __init__(self, key: str, content: DocsSectionContent, starting_line: int):
        """Initialize markdown node."""
        super(DocsMarkdownNode, self).__init__(key, content, starting_line)
        self.content: DocsSectionContent = content

    @classmethod
    def build_tree_from_markdown(cls, lines: List[str], governed_header: Optional[str] = None):
        """Construct a tree out of the given markdown."""
        ob = cls.__new__(cls)
        start_level = ob._get_max_header_lvl(lines)
        ob, _ = ob._build_tree(lines, 'root', 0, start_level, governed_header)
        return ob

    def _build_tree(
        self,
        lines: List[str],
        root_key: str,
        starting_line: int,
        level: int,
        governed_header: Optional[str] = None
    ) -> Tuple[DocsMarkdownNode, int]:
        """
        Build a tree from the markdown recursively.

        The tree is contructed with valid headers as node's keys
        and node's content contains everything that is under that header.
        The subsections are placed into node's children with the same structure.

        A header is valid iff the line starts with # and it is not:
          1. Inside of the html blocks
          2. Inside single lined in the <> tags
          3. Inside the html comment
          4. Inside any table, code block or blockquotes
        """
        content = DocsSectionContent()
        node_children = []
        i = starting_line

        while True:
            if i >= len(lines):
                break
            line = lines[i].strip(' ')
            header_lvl = self._get_header_level_if_valid(line)

            if header_lvl is not None:
                if header_lvl >= level + 1:
                    # build subtree
                    subtree, i = self._build_tree(lines, line, i + 1, level + 1, governed_header)
                    node_children.append(subtree)
                    content.union(subtree)
                else:
                    break  # level of the header is above or equal to the current level, subtree is over
            elif self._does_start_with(line, md_const.CODEBLOCK_DEF):
                code_lines, i = self._read_code_lines(lines, line, i + 1)
                content.code_lines.extend(code_lines)
            elif self._does_start_with(line, md_const.HTML_COMMENT_START):
                html_lines, i = self._read_html_block(lines, line, i + 1, md_const.HTML_COMMENT_END_REGEX)
                content.html_lines.extend(html_lines)
            elif self._does_contain(line, md_const.HTML_TAG_REGEX_START):
                html_lines, i = self._read_html_block(lines, line, i + 1, md_const.HTML_TAG_REGEX_END)
                content.html_lines.extend(html_lines)
            elif self._does_start_with(line, md_const.TABLE_SYMBOL):
                table_block, i = self._read_table_block(lines, line, i + 1)
                content.tables.extend(table_block)
            elif self._does_start_with(line, md_const.BLOCKQUOTE_CHAR):
                content.blockquotes.append(line)
                i += 1
            elif governed_header is not None and self._does_contain(
                    root_key, fr'^[#]+ {governed_header}$') and self._does_contain(line, md_const.GOVERNED_DOC_REGEX):
                regexp = re.compile(md_const.GOVERNED_DOC_REGEX)
                match = regexp.search(line)
                header = match.group(0).strip('*').strip(':')
                content.governed_document.append(header)
                i += 1
            else:
                content.text.append(line)
                i += 1

        first_line_to_grab = starting_line - 1 if starting_line else 0
        content.raw_text = '\n'.join(lines[first_line_to_grab:i])
        md_node = DocsMarkdownNode(key=root_key, content=content, starting_line=first_line_to_grab)
        md_node.subnodes = node_children
        return md_node, i
