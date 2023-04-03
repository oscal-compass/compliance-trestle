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
"""A control markdown node."""
from __future__ import annotations

import logging
import re
import string
from enum import Enum
from typing import Dict, List, Optional, Tuple

from trestle.common import const
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_filtered_list, as_list, none_if_empty
from trestle.common.str_utils import spaces_and_caps_to_snake
from trestle.core.control_interface import ControlInterface
from trestle.core.markdown.base_markdown_node import BaseMarkdownNode, BaseSectionContent
from trestle.core.markdown.markdown_const import CODEBLOCK_DEF, HTML_COMMENT_END_REGEX, HTML_COMMENT_START
from trestle.oscal import common

logger = logging.getLogger(__name__)


class ControlSectionType(Enum):
    """A type of the section in the markdown.

    Supported types:
    1 - Control Statement
    2 - Control Objective
    3 - Control Guidance
    4 - ## Part foo
    5 - Control foo
    6 - ### foo
    7 - # Editable content

    Matching is case-insensitive.
    """

    STATEMENT = 1
    OBJECTIVE = 2
    GUIDANCE = 3
    EDITABLE_BY_ID_PART = 4
    GENERIC_CONTROL_PART = 5
    GENERIC_SUBPART = 6
    EDITABLE_CONTENT = 7
    UNDEFINED = 8


class TreeContext:
    """A shared singleton tree context."""

    def __init__(self):
        """Initialize tree context."""
        self.control_id = ''
        self.control_group = ''
        self.control_title = ''
        self.part_label_to_id_map = None
        self.section_to_part_name_map = None

    def reset(self):
        """Reset global control tree context."""
        self.control_id = ''
        self.control_group = ''
        self.control_title = ''
        self.part_label_to_id_map = None
        self.section_to_part_name_map = None


tree_context = TreeContext()


class ControlSectionContent(BaseSectionContent):
    """A content of the node."""

    def __init__(self):
        """Initialize section content.

        Attributes:
            part: A part that is found in markdown. A part is defined in markdown by two or more # symbols
            by_id_name: Required for parts defined as ## Part a in a markdown
        """
        super(ControlSectionContent, self).__init__()
        self.part = None
        self.by_id_name = ''

    def union(self, node: ControlMarkdownNode) -> None:
        """Unites contents together."""
        super().union(node)


class ControlMarkdownNode(BaseMarkdownNode):
    """Markdown will be read to the tree."""

    def __init__(self, key: str, content: ControlSectionContent, starting_line: int):
        """Initialize markdown node."""
        super(ControlMarkdownNode, self).__init__(key, content, starting_line)
        self.content: ControlSectionContent = content

    def _build_tree(self,
                    lines: List[str],
                    root_key: str,
                    starting_line: int,
                    level: int,
                    parent_part_id: str = '') -> Tuple[ControlMarkdownNode, int]:
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

        Specific Control Rules:
          1. If we are in control statement or objective, no subsections are allowed.
        """
        content = ControlSectionContent()
        node_children = []
        i = starting_line

        section_heading_type = self._get_section_heading_type(root_key)

        part_id, part_name, part_title, by_id_part = self._get_part_info_from_section_name(root_key, parent_part_id,
                                                                                           section_heading_type)

        current_key_lvl = self._get_header_level_if_valid(root_key)

        if section_heading_type == ControlSectionType.UNDEFINED and tree_context.control_id:
            logger.warning(
                f'Undefined section {root_key} is found in the markdown for control {tree_context.control_id}. '
                f'This section will be ignored. Please make sure the spelling is correct.'
            )

        if current_key_lvl and current_key_lvl == 1 and section_heading_type != ControlSectionType.EDITABLE_CONTENT:
            # Parse control title
            if tree_context.control_id:
                logger.debug(
                    f'Duplicate control_id is found for the markdown {root_key}, '
                    f'make sure you have reset tree context before reading another markdown.'
                    f'Use markdown processor to avoid this error.'
                )
                raise TrestleError(
                    f'Multiple top-level headers are found but only one header is allowed. See line {root_key} '
                    f'for control {tree_context.control_id}.'
                )
            tree_context.control_id, tree_context.control_group, tree_context.control_title = ControlMarkdownNode._parse_control_title_line(root_key)  # noqa: E501
            content.control_id = tree_context.control_id
            content.control_group = tree_context.control_group
            content.control_title = tree_context.control_title

        def _strip_prose_or_none(part: Optional[common.Part]):
            if part and part.prose:
                part.prose = part.prose.strip() if part.prose.strip() else None

        def _add_child_prose_if_need(part: common.Part, text: str, should_add: bool):
            if should_add:
                part.prose += text

        while i < len(lines):
            line = lines[i].strip(' ')
            header_lvl = self._get_header_level_if_valid(line)

            if header_lvl is not None:
                if header_lvl >= level + 1:
                    if section_heading_type in [ControlSectionType.STATEMENT, ControlSectionType.OBJECTIVE]:
                        raise TrestleError(
                            f'Control Statement or Objective sections cannot contain subsections but found: {line}.'
                            f'Please delete this subsection and refer to docs on the required format.'
                        )
                    # build subtree
                    subtree, i = self._build_tree(lines, line, i + 1, level + 1, part_id)
                    node_children.append(subtree)
                    content.union(subtree)
                    if content.part and subtree.content.part and section_heading_type not in [
                            ControlSectionType.STATEMENT, ControlSectionType.OBJECTIVE, ControlSectionType.GUIDANCE
                    ]:
                        # Control statement, objective and guidance have special treatment
                        # in those sections any subsections go to the prose rather than subparts.
                        content.part.parts = as_list(content.part.parts)
                        content.part.parts.append(subtree.content.part)
                    # Control parts can have general markdown in the prose, if we are in the control part
                    # add its contents under the prose of a parent
                    _add_child_prose_if_need(
                        content.part,
                        subtree.content.raw_text,
                        section_heading_type
                        in [ControlSectionType.STATEMENT, ControlSectionType.OBJECTIVE, ControlSectionType.GUIDANCE]
                    )
                    continue
                else:
                    i -= 1  # need to revert back one line to properly handle next heading
                    break  # level of the header is above or equal to the current level, subtree is over

            if section_heading_type not in [ControlSectionType.UNDEFINED, ControlSectionType.EDITABLE_CONTENT]:
                # Read part
                content.part = self._create_part_if_needed(content.part, part_name, part_id)
                content.part.title = part_title
                read_parts = section_heading_type in [ControlSectionType.STATEMENT, ControlSectionType.OBJECTIVE]
                if by_id_part and section_heading_type == ControlSectionType.EDITABLE_BY_ID_PART:
                    content.by_id_name = by_id_part
                i = self._process_part_line(i, line, lines, content.part, read_parts=read_parts)
                continue

            # Nothing to do, simply increment
            i += 1

        first_line_to_grab = starting_line - 1 if starting_line else 0
        content.raw_text = '\n'.join(lines[first_line_to_grab:i])

        _strip_prose_or_none(content.part)

        md_node = ControlMarkdownNode(key=root_key, content=content, starting_line=first_line_to_grab)
        md_node.subnodes = node_children
        return md_node, i

    def get_control_statement(self) -> Optional[ControlMarkdownNode]:
        """Get control statement node."""
        return self.get_node_for_key('## Control Statement')

    def get_control_objective(self) -> Optional[ControlMarkdownNode]:
        """Get control objective node."""
        return self.get_node_for_key(const.CONTROL_OBJECTIVE_HEADER)

    def get_control_guidance(self) -> Optional[ControlMarkdownNode]:
        """Get control guidance node."""
        return self.get_node_for_key('## Control Guidance')

    def get_by_id_parts(self) -> Dict[str, List[common.Part]]:
        """Get by id editable parts."""
        part_id_to_parts_map = {}
        for node_key in as_filtered_list(self.content.subnodes_keys, lambda k: re.match(const.PART_REGEX, k)):
            # A by id part section
            part_node = self.get_node_for_key(node_key)
            if not part_node.content.part:
                raise TrestleError(f'Error no part was found in section {part_node.key}.')
            if part_node.content.by_id_name not in part_id_to_parts_map:
                part_id_to_parts_map[part_node.content.by_id_name] = []
            for subpart in part_node.subnodes:
                # We only care about subsections of ## Part section
                if subpart.content.part:
                    part_id_to_parts_map[part_node.content.by_id_name].append(subpart.content.part)

        return part_id_to_parts_map

    def get_editable_parts_and_subparts(self) -> Optional[List[common.Part]]:
        """Get editable parts and subparts if exist."""
        by_id_parts = self.get_by_id_parts()
        exclude_parts_id = list(by_id_parts.keys())
        editable_node = self.get_node_for_key(f'# {const.EDITABLE_CONTENT}')
        parts = self._get_subparts(editable_node, exclude_parts_id)
        return parts

    def _get_subparts(self,
                      control_node: ControlMarkdownNode,
                      exclude_ids: List[str] = None) -> Optional[List[common.Part]]:
        """Get subparts of the control part node if exists."""
        if not control_node:
            raise TrestleError(
                'No control node was provided to extract subparts. '
                'Please make sure your markdown contains # Editable Content section.'
            )
        parts = []
        for editable_part in as_filtered_list(control_node.subnodes, lambda p: p.content.part is not None):
            if editable_part.content.part.id not in exclude_ids:
                parts.append(editable_part.content.part)
        return parts

    def _get_section_heading_type(self, root_key: str) -> ControlSectionType:
        """Determine the section type based on the heading."""
        if root_key.lower() == '## control statement':
            return ControlSectionType.STATEMENT
        elif root_key.lower() == '## control objective':
            return ControlSectionType.OBJECTIVE
        elif root_key.lower() == '## control guidance':
            return ControlSectionType.GUIDANCE
        elif self._does_contain(root_key, const.PART_REGEX):
            return ControlSectionType.EDITABLE_BY_ID_PART
        elif f'# {const.EDITABLE_CONTENT}'.lower() in root_key.lower():
            return ControlSectionType.EDITABLE_CONTENT
        elif self._does_contain(root_key, const.CONTROL_REGEX):
            return ControlSectionType.GENERIC_CONTROL_PART
        elif '### ' in root_key.lower():
            return ControlSectionType.GENERIC_SUBPART

        return ControlSectionType.UNDEFINED

    def _get_part_info_from_section_name(self, root_key: str, parent_id: str,
                                         section_heading_type: ControlSectionType) -> Tuple[str, str, str, str]:
        """Get part information such as id, name and title based on the section heading."""
        part_id = ''
        part_name = ''
        part_title = None
        by_part_id = None  # special case used for ## Part

        if section_heading_type in [ControlSectionType.GUIDANCE, ControlSectionType.GENERIC_CONTROL_PART]:
            prefix = const.CONTROL_HEADER + ' '
            control_md_heading_label = root_key[len(prefix):].strip()
            control_md_heading_label_ncname = ControlInterface.strip_to_make_ncname(control_md_heading_label)
            control_md_heading_label_snakename = spaces_and_caps_to_snake(control_md_heading_label)

        if section_heading_type == ControlSectionType.STATEMENT:
            part_id = ControlInterface.create_statement_id(tree_context.control_id)
            part_name = const.STATEMENT

        if section_heading_type == ControlSectionType.OBJECTIVE:
            part_id = f'{tree_context.control_id}_obj'
            part_name = 'objective'

        if section_heading_type == ControlSectionType.GUIDANCE:
            # Read control guidance to a part object
            part_id = ControlInterface.strip_to_make_ncname(tree_context.control_id + '_gdn')
            part_name = control_md_heading_label_ncname

        if section_heading_type == ControlSectionType.EDITABLE_BY_ID_PART:
            # Read editable part
            by_part_label = re.match(const.PART_REGEX, root_key.lower()).groups(0)[0]
            control_label_map = tree_context.part_label_to_id_map.get(tree_context.control_id, None)
            if control_label_map is None:
                raise TrestleError(f'No label map found for control {tree_context.control_id}')
            by_part_id = control_label_map.get(by_part_label, None)
            if by_part_id is None:
                raise TrestleError(f'No part id found for label {by_part_label} in control {tree_context.control_id}')

            part_name = spaces_and_caps_to_snake(root_key.replace('#', '').replace('.', '').strip())
            part_id = f'{by_part_id}'
            part_title = root_key.replace('#', '').strip()

        if section_heading_type == ControlSectionType.GENERIC_CONTROL_PART:
            # Read other control parts to a part objects
            part_name = control_md_heading_label_snakename
            if tree_context.section_to_part_name_map:
                if control_md_heading_label in tree_context.section_to_part_name_map:
                    part_name = tree_context.section_to_part_name_map[control_md_heading_label]

                part_id = f'{tree_context.control_id}_{part_name}'
                part_title = control_md_heading_label
            else:
                part_id = spaces_and_caps_to_snake(tree_context.control_id + '_' + control_md_heading_label)

        if section_heading_type == ControlSectionType.GENERIC_SUBPART:
            # Read other control parts to a part objects
            match = re.match(const.AFTER_HASHES_REGEX, root_key)
            if not match:
                raise TrestleError(f'Unexpected editable header {root_key} found in part {part_id}')
            part_name_raw = match.groups(0)[0]
            part_name = spaces_and_caps_to_snake(part_name_raw)
            parent_suffix = parent_id + '.' if parent_id else ''
            part_id = parent_suffix + part_name

        return part_id, part_name, part_title, by_part_id

    def get_other_control_parts(self) -> List[Optional[ControlMarkdownNode]]:
        """Get all other control parts that are not statement, guidance or objective."""
        all_other_nodes = []
        all_control_sections = self.get_all_headers_for_key(const.CONTROL_HEADER, False)
        control_statement = self.get_control_statement()
        control_objective = self.get_control_objective()
        control_guidance = self.get_control_guidance()
        control_statement_heading = control_statement.key if control_statement else ''
        control_objective_heading = control_objective.key if control_objective else ''
        control_guidance_heading = control_guidance.key if control_guidance else ''
        for heading_key in all_control_sections:
            if heading_key not in {control_statement_heading, control_objective_heading, control_guidance_heading}:
                section_node = self.get_node_for_key(heading_key)
                all_other_nodes.append(section_node)

        return all_other_nodes

    def _create_part_if_needed(self, content_part: common.Part, part_name: str, part_id: str, prose: str = ''):
        """Create a new part if does not exist or return existing part."""
        if not content_part:
            if not tree_context.control_id:
                raise TrestleError(
                    f'Unexpected error, control id, group and title should be before ## Control {part_name}.'
                    'However, none was found.'
                )

            content_part = common.Part(name=part_name, id=part_id, prose=prose)

        return content_part

    def _process_part_line(
        self, line_idx: int, line: str, lines: List[str], part: common.Part, read_parts: bool = True
    ) -> int:
        """
        Process line for the part.

        If the read_parts is given and the line starts with '-' then
        the markdown list will be read to the subparts of the given part.
        """
        if self._does_start_with(line, HTML_COMMENT_START):
            comment_lines, line_idx = self._read_html_block(lines, line, line_idx + 1, HTML_COMMENT_END_REGEX)
            if line_idx >= len(lines):
                return line_idx
            line = lines[line_idx]

        if self._does_start_with(line, CODEBLOCK_DEF):
            code_lines, line_idx = self._read_code_lines(lines, line, line_idx + 1)
            if line_idx >= len(lines):
                return line_idx
            line = lines[line_idx]
            part.prose += '\n'.join(code_lines)

        if not line:
            # Empty line
            part.prose += '\n'
            line_idx += 1
            return line_idx

        if line.lstrip()[0] != '-' or not read_parts:
            # Line of text in prose
            part.prose += line + '\n'
            line_idx += 1
        else:
            # A part of inside of statement part
            if read_parts:
                end_idx, parts = self._read_parts(0, line_idx, lines, part.id, [])
                part.parts = none_if_empty(parts)
                line_idx = end_idx
            else:
                logger.warning(
                    f'{part.name} does not support subparts, ignoring {line} in control {tree_context.control_id}.'
                )
                line_idx += 1

        return line_idx

    def _read_parts(self, indent: int, ii: int, lines: List[str], parent_id: str,
                    parts: List[common.Part]) -> Tuple[int, List[common.Part]]:
        """If indentation level goes up or down, create new list or close current one."""
        while True:
            ii, new_indent, line = ControlMarkdownNode._get_next_indent(ii, lines)
            if new_indent < 0:
                # we are done reading control statement
                return ii, parts
            if new_indent == indent:
                # create new item part and add to current list of parts
                id_text, prose = ControlMarkdownNode._read_part_id_prose(line)
                # id_text is the part id and needs to be as a label property value
                # if none is there then create one from previous part, or use default
                if not id_text:
                    prev_label = ControlInterface.get_label(parts[-1]) if parts else ''
                    id_text = ControlMarkdownNode._create_next_label(prev_label, indent)
                id_ = ControlInterface.strip_to_make_ncname(parent_id.rstrip('.') + '.' + id_text.strip('.'))
                name = 'objective' if id_.find('_obj') > 0 else 'item'
                prop = common.Property(name='label', value=id_text)
                part = common.Part(name=name, id=id_, prose=prose, props=[prop])
                parts.append(part)
                ii += 1
            elif new_indent > indent:
                # add new list of parts to last part and continue
                if len(parts) == 0:
                    raise TrestleError(f'Improper indentation structure: {line}')
                ii, new_parts = self._read_parts(new_indent, ii, lines, parts[-1].id, [])
                if new_parts:
                    parts[-1].parts = new_parts
            else:
                # return list of sub-parts
                return ii, parts

    @staticmethod
    def _indent(line: str) -> int:
        """Measure indent of non-empty line."""
        if not line:
            raise TrestleError('Empty line queried for indent.')
        if line[0] not in [' ', '-']:
            return -1
        for ii in range(len(line)):
            if line[ii] == '-':
                return ii
            # if line is indented it must start with -
            if line[ii] != ' ':
                break
        raise TrestleError(f'List elements must start with -: {line}')

    @staticmethod
    def _parse_control_title_line(line: str) -> Tuple[str, str, str]:
        """Process the title line and extract the control id, group title (in brackets) and control title."""
        if line.count('-') == 0:
            raise TrestleError(f'Markdown control title format error, missing - after control id: {line}')
        split_line = line.split()
        if len(split_line) < 3 or split_line[2] != '-':
            raise TrestleError(f'Cannot parse control markdown title for control_id group and title: {line}')
        # first token after the #
        control_id = split_line[1]
        group_title_start = line.find('\[')
        group_title_end = line.find('\]')
        if group_title_start < 0 or group_title_end < 0 or group_title_start > group_title_end:
            raise TrestleError(f'unable to read group title for control {control_id}')
        group_title = line[group_title_start + 2:group_title_end].strip()
        control_title = line[group_title_end + 2:].strip()
        return control_id, group_title, control_title

    @staticmethod
    def _read_part_id_prose(line: str) -> Tuple[str, str]:
        """Extract the part id letter or number and prose from line."""
        start = line.find('\\[')
        end = line.find('\\]')
        prose = line.strip() if start < 0 else line[end + 2:].strip()
        id_ = '' if start < 0 or end < 0 else line[start + 2:end]
        return id_, prose

    @staticmethod
    def _create_next_label(prev_label: str, indent: int) -> str:
        """
        Create new label at indent level based on previous label if available.

        If previous label is available, make this the next one in the sequence.
        Otherwise start with a or 1 on alternate levels of indentation.
        If alphabetic label reaches z, next one is aa.
        Numeric ranges from 1 to 9, then 10 etc.
        """
        if not prev_label:
            # assume indent goes in steps of 2
            return ['a', '1'][(indent // 2) % 2]
        label_prefix = ''
        label_suffix = prev_label
        is_char = prev_label[-1] in string.ascii_letters
        # if it isn't ending in letter or digit just append 'a' to end
        if not is_char and prev_label[-1] not in string.digits:
            return prev_label + 'a'
        # break in middle of string if mixed types
        if len(prev_label) > 1:
            ii = len(prev_label) - 1
            while ii >= 0:
                if prev_label[ii] not in string.ascii_letters + string.digits:
                    break
                if (prev_label[ii] in string.ascii_letters) != is_char:
                    break
                ii -= 1
            if ii >= 0:
                label_prefix = prev_label[:(ii + 1)]
                label_suffix = prev_label[(ii + 1):]

        return label_prefix + ControlMarkdownNode._bump_label(label_suffix)

    @staticmethod
    def _bump_label(label: str) -> str:
        """
        Find next label given a string of 1 or more pure letters or digits.

        The input must be either a string of digits or a string of ascii letters - or empty string.
        """
        if not label:
            return 'a'
        if label[0] in string.digits:
            return str(int(label) + 1)
        if len(label) == 1 and label[0].lower() < 'z':
            return chr(ord(label[0]) + 1)
        # if this happens to be a string of letters, force it lowercase and bump
        label = label.lower()
        factor = 1
        value = 0
        # delta is needed because a counts as 0 when first value on right, but 1 for all others
        delta = 0
        for letter in label[::-1]:
            value += (ord(letter) - ord('a') + delta) * factor
            factor *= 26
            delta = 1

        value += 1

        new_label = ''
        delta = 0
        while value > 0:
            new_label += chr(ord('a') + value % 26 - delta)
            value = value // 26
            delta = 1
        return new_label[::-1]

    @staticmethod
    def _get_next_indent(ii: int, lines: List[str], skip_empty_lines: bool = True) -> Tuple[int, int, str]:
        """Seek to next content line.  ii remains at line read."""
        while 0 <= ii < len(lines):
            line = lines[ii]
            if line and not line.isspace():
                if line[0] == '#':
                    return ii, -1, line
                indent = ControlMarkdownNode._indent(line)
                if indent >= 0:
                    # extract text after -
                    start = indent + 1
                    while start < len(line) and line[start] == ' ':
                        start += 1
                    if start >= len(line):
                        raise TrestleError(f'Invalid line {line}')
                    return ii, indent, line[start:]
                return ii, indent, line
            elif not skip_empty_lines:
                return ii, -1, line
            ii += 1
        return ii, -1, ''
