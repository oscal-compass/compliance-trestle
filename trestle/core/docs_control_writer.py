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
from typing import Dict, List, Optional

import trestle.oscal.catalog as cat
from trestle.common.err import TrestleError
from trestle.core.control_interface import ControlInterface, ParameterRep
from trestle.core.control_writer import ControlWriter
from trestle.core.markdown.md_writer import MDWriter

logger = logging.getLogger(__name__)


class DocsControlWriter(ControlWriter):
    """Class to write controls as markdown for docs purposes."""

    def write_control_with_sections(
        self,
        control: cat.Control,
        group_title: str,
        sections: List[str],
        sections_dict: Optional[Dict[str, str]] = None,
        label_column: bool = True,
        add_group_to_title: bool = False,
        param_dict: Dict[str, str] = None
    ) -> str:
        """Write the control into markdown file with specified sections."""
        self._md_file = MDWriter(None)
        self._sections_dict = sections_dict
        tag_pattern = '{: #[.]}'  # noqa: FS003 - not f string but tag
        if not isinstance(group_title, str):
            raise TrestleError(f'Group title must be provided and be a string, instead received: {group_title}')

        for section in sections:
            if 'statement' == section:
                self._add_control_statement(
                    control, group_title, sections_dict, add_group_to_title, tag_pattern=tag_pattern
                )

            elif 'objective' == section:
                self._add_control_objective(control, sections_dict, tag_pattern=tag_pattern)

            elif 'table_of_parameters' == section:
                header_title = None
                if sections_dict and sections_dict['table_of_parameters']:
                    header_title = sections_dict['table_of_parameters']
                self.get_param_table(
                    control,
                    label_column,
                    header_title,
                    add_tag=True,
                    param_displayname=param_dict,
                    md_file=self._md_file
                )
            else:
                self._add_one_section(control, section, tag_pattern=tag_pattern)

        return '\n'.join(self._md_file._lines)

    def get_control_statement_ssp(self, control: cat.Control) -> List[str]:
        """Get the control statement as formatted markdown from a control formatted for SSP."""
        self._md_file = MDWriter(None)
        self._add_control_statement_ssp(control)
        return self._md_file.get_lines()

    def get_param_table(
        self,
        control: cat.Control,
        label_column=False,
        header='Table of Parameters',
        add_tag=False,
        param_displayname=None,
        md_file=None
    ) -> List[str]:
        """Get parameters of a control as a markdown table for ssp_io, with optional third label column."""

        def _get_displayname_if_exists(param_id: str) -> str:
            if param_displayname:
                if param_id in param_displayname:
                    return param_displayname[param_id]
            return param_id

        param_dict = ControlInterface.get_control_param_dict(control, False)

        if param_dict:
            if md_file:
                self._md_file = md_file
            else:
                self._md_file = MDWriter(None)
            self._md_file.new_paragraph()
            self._md_file.new_header(level=2, title=header)
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
            if add_tag:
                tag_pattern = '{: #Parameters for [.] caption-side=\"top\"}'  # noqa: FS003 - not f string
                control_id = self._get_pretty_control_id_if_exists(control)
                self._md_file.new_line(tag_pattern.replace('[.]', control_id))
            return self._md_file.get_lines()

        return []

    def _add_control_statement(
        self,
        control: cat.Control,
        group_title: str,
        sections_dict: Optional[Dict[str, str]] = None,
        print_group_title=True,
        tag_pattern: str = None
    ) -> None:
        """Add the control statement and items to the md file."""
        self._md_file.new_paragraph()

        group_name = ''
        control_title = control.title

        if print_group_title:
            group_name = ' \[' + group_title + '\]'

        control_id = self._get_pretty_control_id_if_exists(control)

        title = f'{control_id} -{group_name} {control_title}'

        header_title = 'Control Statement'
        if sections_dict and sections_dict['statement']:
            header_title = sections_dict['statement']
        self._md_file.new_header(level=1, title=title)
        if tag_pattern:
            self._md_file.new_line(tag_pattern.replace('[.]', control.id))

        self._md_file.new_header(level=2, title=header_title)
        if tag_pattern:
            self._md_file.new_line(tag_pattern.replace('[.]', header_title.replace(' ', '-').lower()))

        self._md_file.set_indent_level(-1)
        self._add_part_and_its_items(control, 'statement', 'item')
        self._md_file.set_indent_level(-1)

    def _add_control_objective(
        self, control: cat.Control, sections_dict: Optional[Dict[str, str]] = None, tag_pattern: str = None
    ) -> None:
        if control.parts:
            for part in control.parts:
                if part.name == 'objective':
                    self._md_file.new_paragraph()
                    heading_title = 'Control Objective'
                    if sections_dict and sections_dict['objective']:
                        heading_title = sections_dict['objective']
                    self._md_file.new_header(level=2, title=heading_title)
                    if tag_pattern:
                        self._md_file.new_line(tag_pattern.replace('[.]', heading_title.replace(' ', '-').lower()))
                    self._md_file.set_indent_level(-1)
                    self._add_part_and_its_items(control, 'objective', 'objective')
                    self._md_file.set_indent_level(-1)
                    return

    def _add_one_section(self, control: cat.Control, section: str, tag_pattern: str = None) -> None:
        """Add specific control section."""
        prose = ControlInterface._get_control_section_prose(control, section)
        if prose:
            section_title = self._sections_dict.get(section) if self._sections_dict else section
            section_title = section_title if section_title else section
            heading_title = f'Control {section_title}'
            self._md_file.new_header(level=2, title=heading_title)
            if tag_pattern:
                self._md_file.new_line(tag_pattern.replace('[.]', heading_title.replace(' ', '-').lower()))
            self._md_file.new_line(prose)
            self._md_file.new_paragraph()

    def _get_pretty_control_id_if_exists(self, control) -> str:
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
