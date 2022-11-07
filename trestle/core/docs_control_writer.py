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
"""Handle writing of controls to markdown for docs purposes."""
import logging
import re
from typing import Dict, List, Optional

import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.common import const
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_filtered_list, as_list
from trestle.core.control_interface import ControlInterface, ParameterRep, PartInfo
from trestle.core.control_writer import ControlWriter
from trestle.core.markdown.md_writer import MDWriter

logger = logging.getLogger(__name__)


class DocsControlWriter(ControlWriter):
    """Class to write controls as markdown for docs purposes."""

    def write_control_with_sections(
        self,
        control: cat.Control,
        profile: prof.Profile,
        group_title: str,
        sections: List[str],
        sections_dict: Optional[Dict[str, str]] = None,
        label_column: bool = True,
        add_group_to_title: bool = False
    ) -> str:
        """Write the control into markdown file with specified sections."""
        self._md_file = MDWriter(None)
        self._sections_dict = sections_dict if sections_dict else {}
        tag_pattern = '{: #[.]}'  # noqa: FS003 - not f string but tag
        if not isinstance(group_title, str):
            raise TrestleError(f'Group title must be provided and be a string, instead received: {group_title}')

        for section in sections:
            if 'statement' == section:
                self._add_control_statement(control, group_title, add_group_to_title, tag_pattern=tag_pattern)

            elif const.OBJECTIVE_PART == section:
                self._add_control_objective(control, tag_pattern=tag_pattern)

            elif 'table_of_parameters' == section:
                self.get_param_table(
                    control, label_column, section_dict=sections_dict, tag_pattern=tag_pattern, md_file=self._md_file
                )
            else:
                self._add_one_section(control, profile, section, tag_pattern=tag_pattern)

        return '\n'.join(self._md_file._lines)

    def get_control_statement_ssp(self, control: cat.Control) -> List[str]:
        """Get the control statement as formatted markdown from a control formatted for SSP."""
        self._md_file = MDWriter(None)
        self._add_control_statement_ssp(control)
        return self._md_file.get_lines()

    def get_param_table(
        self,
        control: cat.Control,
        label_column: bool = False,
        section_dict: Optional[Dict[str, str]] = None,
        tag_pattern: str = None,
        md_file: MDWriter = None
    ) -> List[str]:
        """Get parameters of a control as a markdown table for ssp_io, with optional third label column."""

        def _get_displayname_if_exists(param_id: str) -> str:
            for param in as_filtered_list(control.params, lambda p: p.id == param_id):
                for prop in as_filtered_list(param.props, lambda p: p.name == const.DISPLAY_NAME):
                    return prop.value
            return param_id

        param_dict = ControlInterface.get_control_param_dict(control, False)

        if param_dict:
            if md_file:
                self._md_file = md_file
            else:
                self._md_file = MDWriter(None)
            header_title = 'Table of Parameters'
            if section_dict:
                header_title = section_dict.get(const.TABLE_OF_PARAMS_PART, 'Table of Parameters')
            self._md_file.new_paragraph()
            self._md_file.new_header(level=2, title=header_title, add_new_line_after_header=not tag_pattern)
            if tag_pattern:
                self._md_file.new_line(tag_pattern.replace('[.]', header_title.replace(' ', '-').lower()))
                self._md_file.new_paragraph()
            self._md_file.set_indent_level(-1)
            if label_column:
                self._md_file.new_table(
                    [
                        [
                            _get_displayname_if_exists(key),
                            ControlInterface.param_to_str(param_dict[key], ParameterRep.VALUE_OR_EMPTY_STRING),
                            ControlInterface.param_to_str(param_dict[key], ParameterRep.LABEL_OR_CHOICES, True),
                        ] for key in param_dict.keys()
                    ], ['Parameter ID', 'Values', 'Label or Choices']
                )
            else:
                self._md_file.new_table(
                    [
                        [
                            _get_displayname_if_exists(key),
                            ControlInterface.param_to_str(param_dict[key], ParameterRep.VALUE_OR_LABEL_OR_CHOICES)
                        ] for key in param_dict.keys()
                    ], ['Parameter ID', 'Values']
                )
            self._md_file.set_indent_level(-1)
            if tag_pattern:
                bottom_tag_pattern = '{: #\"Parameters for [.]\" caption-side=\"top\"}'  # noqa: FS003 - not f string
                control_id = self._get_pretty_control_id_if_exists(control)
                self._md_file.new_line(bottom_tag_pattern.replace('[.]', control_id))
                self._md_file.new_paragraph()
            return self._md_file.get_lines()

        return []

    def _add_control_statement(
        self, control: cat.Control, group_title: str, print_group_title=True, tag_pattern: str = None
    ) -> None:
        """Add the control statement and items to the md file."""
        self._md_file.new_paragraph()

        group_name = ''
        control_title = control.title

        if print_group_title:
            group_name = ' \[' + group_title + '\]'

        control_id = self._get_pretty_control_id_if_exists(control)

        title = f'{control_id} -{group_name} {control_title}'

        header_title = self._sections_dict.get(const.STATEMENT, 'Control Statement')
        self._md_file.new_header(level=1, title=title, add_new_line_after_header=not tag_pattern)
        if tag_pattern:
            self._md_file.new_line(tag_pattern.replace('[.]', control.id))
            self._md_file.new_paragraph()

        self._md_file.new_header(level=2, title=header_title, add_new_line_after_header=not tag_pattern)
        if tag_pattern:
            self._md_file.new_line(tag_pattern.replace('[.]', header_title.replace(' ', '-').lower()))
            self._md_file.new_paragraph()

        self._md_file.set_indent_level(-1)
        self._add_part_and_its_items(control, 'statement', 'item')
        self._md_file.set_indent_level(-1)

    def _add_control_objective(self, control: cat.Control, tag_pattern: str = None) -> None:
        if control.parts:
            for part in control.parts:
                if part.name == const.OBJECTIVE_PART:
                    self._md_file.new_paragraph()
                    heading_title = self._sections_dict.get(const.OBJECTIVE_PART, 'Control Objective')
                    self._md_file.new_header(level=2, title=heading_title, add_new_line_after_header=not tag_pattern)
                    if tag_pattern:
                        self._md_file.new_line(tag_pattern.replace('[.]', heading_title.replace(' ', '-').lower()))
                        self._md_file.new_paragraph()
                    self._md_file.set_indent_level(-1)
                    self._add_part_and_its_items(control, const.OBJECTIVE_PART, const.OBJECTIVE_PART)
                    self._md_file.set_indent_level(-1)
                    return

    def _add_one_section(
        self, control: cat.Control, profile: prof.Profile, section: str, tag_pattern: Optional[str] = None
    ) -> None:
        """Add specific control section."""
        prose = ControlInterface.get_control_section_prose(control, section)
        if prose:
            section_title = self._sections_dict.get(section, section)
            heading_title = f'{section_title}'
            self._md_file.new_header(level=2, title=heading_title, add_new_line_after_header=not tag_pattern)
            if tag_pattern:
                self._md_file.new_line(tag_pattern.replace('[.]', heading_title.replace(' ', '-').lower()))
                self._md_file.new_paragraph()
            self._md_file.new_line(prose)
            self._md_file.new_paragraph()
        else:
            # write parts and subparts if exist
            part_infos = ControlInterface.get_all_add_info(control.id, profile)
            for part_info in part_infos:
                if part_info.name == section:
                    self._write_part_info(part_info, section, tag_pattern)
                    break

    def _write_part_info(
        self,
        part_info: PartInfo,
        section_name: str,
        tag_pattern: Optional[str] = None,
        section_prefix: str = '',
        heading_level: int = 2
    ):
        section_title = self._sections_dict.get(section_name, part_info.name)

        heading_title = f'{section_title}'
        tag_section_name = section_prefix + f'{section_title}'
        tag_section_name = re.sub(const.MATCH_ALL_EXCEPT_LETTERS_UNDERSCORE_SPACE_REGEX, '', tag_section_name)
        tag_section_name = tag_section_name.replace(' ', '-').replace('_', '-').lower()
        self._md_file.new_header(level=heading_level, title=heading_title, add_new_line_after_header=not tag_pattern)
        if tag_pattern:
            self._md_file.new_line(tag_pattern.replace('[.]', tag_section_name))
            self._md_file.new_paragraph()
        self._md_file.new_line(part_info.prose)
        self._md_file.new_paragraph()

        for subpart_info in as_list(part_info.parts):
            self._write_part_info(
                subpart_info, subpart_info.name, tag_pattern, tag_section_name + '-', heading_level + 1
            )

    def _get_pretty_control_id_if_exists(self, control: cat.Control) -> str:
        control_id = control.id.upper()
        if control.props:
            # Take control id from the properties
            for prop in control.props:
                if prop.name == 'label':
                    control_id = prop.value
                    break
        return control_id

    def _add_control_statement_ssp(self, control: cat.Control) -> None:
        """Add the control statement and items to the markdown SSP."""
        self._md_file.new_paragraph()
        label = ControlInterface.get_label(control)
        label = label if label else control.id.upper()
        title = f'{label} - {control.title}'
        self._md_file.new_header(level=1, title=title)
        self._md_file.new_header(level=2, title='Control Statement')
        self._md_file.set_indent_level(-1)
        self._add_part_and_its_items(control, 'statement', 'item')
        self._md_file.set_indent_level(-1)
