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
"""A markdown node."""
from __future__ import annotations

import logging
import math
import re
from typing import Dict, Iterable, List, Optional, Tuple

import trestle.core.markdown.markdown_const as md_const
from trestle.core.err import TrestleError

logger = logging.getLogger(__name__)


class SectionContent:
    """A content of the node."""

    def __init__(self):
        """Initialize section content."""
        self.tables = []
        self.text = []
        self.code_lines = []
        self.html_lines = []
        self.blockquotes = []
        self.raw_text = ''
        self.subnodes_keys = []
        self.governed_document = []

    def union(self, node: MarkdownNode) -> None:
        """Unites contents together."""
        self.subnodes_keys.append(node.key)
        self.subnodes_keys.extend(node.content.subnodes_keys)
        self.code_lines.extend(node.content.code_lines)
        self.html_lines.extend(node.content.html_lines)
        self.tables.extend(node.content.tables)
        self.blockquotes.extend(node.content.blockquotes)


class MarkdownNode:
    """Markdown will be read to the tree."""

    def __init__(self, key: str, content: SectionContent):
        """Initialize markdown node."""
        self.subnodes: List[MarkdownNode] = []
        self.key = key
        self.content = content

    @classmethod
    def build_tree_from_markdown(cls, lines: List[str], governed_header: Optional[str] = None):
        """Construct a tree out of the given markdown."""
        ob = cls.__new__(cls)
        start_level = ob._get_max_header_lvl(lines)
        ob, _ = ob._build_tree(lines, 'root', 0, start_level, governed_header)
        return ob

    def get_all_headers_for_level(self, level: int) -> Iterable[str]:
        """Return all headers per specified level of heirarchy."""
        return list(
            filter(lambda header: self._get_header_level_if_valid(header) == level, self.content.subnodes_keys)
        ).__iter__()

    def get_node_for_key(self, key: str, strict_matching: bool = True) -> Optional[MarkdownNode]:
        """Return a node for the given key, substring matching is supported."""
        if not strict_matching:
            if not any([key in el for el in self.content.subnodes_keys]):
                return None
        elif key not in self.content.subnodes_keys:
            return None

        return self._rec_traverse(self, key, strict_matching)

    def get_all_headers_for_key(self, key: str, strict_matching: bool = True) -> Iterable[str]:
        """Return all headers contained in the node with a given key."""
        if strict_matching:
            return list(filter(lambda header: key == header, self.content.subnodes_keys)).__iter__()
        else:
            return list(filter(lambda header: key in header, self.content.subnodes_keys)).__iter__()

    def get_node_header_lvl(self) -> Optional[int]:
        """Return current node header level."""
        return self._get_header_level_if_valid(self.key)

    def change_header_level_by(self, delta_level: int) -> None:
        """
        Change all headers in the tree by specified level up or down.

        All children nodes will be modified by specified level as well.

        Args:
            delta_level: each header will be modified by this number, can be negative.
        """
        # construct a map
        header_map = {}
        if self.key != 'root':
            new_key = self._modify_header_level(self.key, delta_level)
            header_map[self.key] = new_key
        for key in self.content.subnodes_keys:
            new_key = self._modify_header_level(key, delta_level)
            header_map[key] = new_key

        # go through all contents and modify headers
        self._rec_traverse_header_update(self, header_map)

    def _build_tree(
        self,
        lines: List[str],
        root_key: str,
        starting_line: int,
        level: int,
        governed_header: Optional[str] = None
    ) -> Tuple[MarkdownNode, int]:
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
        content = SectionContent()
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

        if starting_line == 0:
            starting_line = 1
        content.raw_text = '\n'.join(lines[starting_line - 1:i])
        md_node = MarkdownNode(key=root_key, content=content)
        md_node.subnodes = node_children
        return (md_node, i)

    def _modify_header_level(self, header: str, delta_level: int) -> str:
        """Modify header level by specified level."""
        if delta_level == 0:
            logger.debug('Nothing to modify in header, level 0 is given.')
            return header

        current_level = self._get_header_level_if_valid(header)
        if current_level is None:
            current_level = 0
        if current_level + delta_level < 0:
            logger.warning(
                f'Cannot substract {delta_level} as level of {header} is {current_level}. All `#` will be removed.'
            )
            delta_level = current_level * -1

        if current_level + delta_level == 0:
            replacement = ''
        else:
            replacement = '#' * (current_level + delta_level)
        header = header.replace('#' * current_level, replacement)

        return header.strip(' ')

    def _get_header_level_if_valid(self, line: str) -> Optional[int]:
        """
        Return a level of the header if the given line is indeed a header.

        Level of the header is determined by the number of # symbols.
        """
        header_symbols = re.match(md_const.HEADER_REGEX, line)
        # Header is valid only if it line starts with header
        if header_symbols is not None and header_symbols.regs[0][0] == 0:
            return header_symbols.regs[0][1]
        return None

    def _does_start_with(self, line: str, start_chars: str) -> bool:
        """Determine whether the line starts with given characters."""
        return line.startswith(start_chars)

    def _does_contain(self, line: str, reg: str) -> bool:
        """Determine if the line matches regex."""
        if len(line) == 0 and reg != r'':
            return False
        regexp = re.compile(reg)
        return regexp.search(line) is not None

    def _read_code_lines(self, lines: List[str], line: str, i: int) -> Tuple[str, int]:
        """Read code block."""
        code_lines = [line]
        while True:
            if i >= len(lines):
                raise TrestleError(f'Code block is not closed: {code_lines}')

            line = lines[i]
            code_lines.append(line)
            i += 1
            if self._does_contain(line, md_const.CODEBLOCK_DEF):
                break
        return code_lines, i

    def _read_html_block(self, lines: List[str], line: str, i: int, ending_regex: str) -> Tuple[str, int]:
        """Read html block."""
        html_block = [line]
        if self._does_contain(line, r'<br[ /]*>'):
            return html_block, i
        if self._does_contain(line, ending_regex):
            return html_block, i
        while True:
            if i >= len(lines):
                raise TrestleError(f'HTML block is not closed: {html_block}')

            line = lines[i]
            html_block.append(line)
            i += 1
            if self._does_contain(line, ending_regex):
                break
        return html_block, i

    def _read_table_block(self, lines: List[str], line: str, i: int) -> Tuple[str, int]:
        """Read table."""
        table_block = [line]
        while True:
            if i >= len(lines):
                return table_block, i

            line = lines[i]
            if not self._does_contain(line, md_const.TABLE_REGEX):
                table_block.append(line)
                break
            table_block.append(line)
            i += 1
        return table_block, i

    def _rec_traverse(self, node, key: str, strict_matching: bool) -> Optional[MarkdownNode]:
        """
        Recursevely traverses the tree and searches for the given key.

        If strict matching is turned off, node will be matched if key is a substring of the node's header.
        """
        if key == node.key or (not strict_matching and key in node.key):
            return node
        if (not strict_matching and any([key in el
                                         for el in node.content.subnodes_keys])) or (key in node.content.subnodes_keys):
            for subnode in node.subnodes:
                matched_node = self._rec_traverse(subnode, key, strict_matching)
                if matched_node is not None:
                    return matched_node

        return None

    def _rec_traverse_header_update(self, node: MarkdownNode, header_map: Dict[str, str]) -> None:
        """Recursively traverse tree and update the contents."""
        if node:
            if node.key != 'root':
                new_key = header_map[node.key]
                node.key = new_key

            # update text
            lines = node.content.raw_text.split('\n')
            if lines:
                for i in range(0, len(lines)):
                    line = lines[i]
                    if line in header_map.keys():
                        new_key = header_map[line]
                        lines[i] = new_key
                    elif line.strip(' ') in header_map.keys():
                        # keep spaces if any
                        new_key = header_map[line.strip(' ')]
                        lines[i] = line.replace(line.strip(' '), new_key)

                node.content.raw_text = '\n'.join(lines)

            # update subnodes
            if node.content.subnodes_keys:
                for i in range(0, len(node.content.subnodes_keys)):
                    subnode_key = node.content.subnodes_keys[i]
                    if subnode_key in header_map.keys():
                        new_key = header_map[subnode_key]
                        node.content.subnodes_keys[i] = new_key

        for subnode in node.subnodes:
            self._rec_traverse_header_update(subnode, header_map)

    def _get_max_header_lvl(self, lines: List[str]):
        """Go through all lines to determine highest header level. Less # means higher."""
        min_lvl = math.inf
        for line in lines:
            line = line.strip(' ')
            header_lvl = self._get_header_level_if_valid(line)

            if header_lvl is not None and header_lvl < min_lvl:
                min_lvl = header_lvl

        return min_lvl - 1
