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
"""Handle writing of controls to markdown."""
import copy
import logging
import pathlib
from typing import Dict, List, Optional

import trestle.oscal.catalog as cat
from trestle.common import const
from trestle.common.err import TrestleError
from trestle.core.control_interface import CompDict, ComponentImpInfo, ControlInterface, ParameterRep
from trestle.core.control_reader import ControlReader
from trestle.core.markdown.md_writer import MDWriter
from trestle.oscal import component as comp
from trestle.oscal import profile as prof

logger = logging.getLogger(__name__)


class ControlWriter():
    """Class to write controls as markdown."""

    def __init__(self):
        """Initialize the class."""
        self._md_file: Optional[MDWriter] = None

    def _add_part_and_its_items(self, control: cat.Control, name: str, item_type: str) -> None:
        """For a given control add its one statement and its items to the md file after replacing params."""
        items = []
        if control.parts:
            for part in control.parts:
                if part.name == name:
                    # If the part has prose write it as a raw line and not list element
                    skip_id = part.id
                    if part.prose:
                        # need to avoid split lines in statement items
                        self._md_file.new_line(part.prose.replace('\n', '  '))
                    items.append(ControlInterface.get_part(part, item_type, skip_id))
            # unwrap the list if it is many levels deep
            while not isinstance(items, str) and len(items) == 1:
                items = items[0]
            self._md_file.new_paragraph()
            self._md_file.new_list(items)

    def _add_yaml_header(self, yaml_header: Optional[Dict]) -> None:
        if yaml_header:
            self._md_file.add_yaml_header(yaml_header)

    def _add_control_statement(
        self,
        control: cat.Control,
        group_title: str,
        sections_dict: Optional[Dict[str, str]] = None,
        capitalize_title=False,
        print_group_title=True
    ) -> None:
        """Add the control statement and items to the md file."""
        self._md_file.new_paragraph()
        control_id = control.id
        group_name = ''
        control_title = control.title

        if print_group_title:
            group_name = ' \[' + group_title + '\]'

        if capitalize_title:
            control_id = control_id.upper()
            group_name = group_name.title()
            control_title = control_title.upper()

        title = f'{control_id} -{group_name} {control_title}'

        header_title = 'Control Statement'
        if sections_dict and sections_dict['statement']:
            header_title = sections_dict['statement']
        self._md_file.new_header(level=1, title=title)
        self._md_file.new_header(level=2, title=header_title)
        self._md_file.set_indent_level(-1)
        self._add_part_and_its_items(control, 'statement', 'item')
        self._md_file.set_indent_level(-1)

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

    def _add_control_objective(self, control: cat.Control, sections_dict: Optional[Dict[str, str]] = None) -> None:
        if control.parts:
            for part in control.parts:
                if part.name == 'objective':
                    self._md_file.new_paragraph()
                    heading_title = 'Control Objective'
                    if sections_dict and sections_dict['objective']:
                        heading_title = sections_dict['objective']
                    self._md_file.new_header(level=2, title=heading_title)
                    self._md_file.set_indent_level(-1)
                    self._add_part_and_its_items(control, 'objective', 'objective')
                    self._md_file.set_indent_level(-1)
                    return

    def _add_sections(self, control: cat.Control, allowed_sections: Optional[List[str]]) -> None:
        """Add the extra control sections after the main ones."""
        skip_section_list = ['statement', 'item', 'objective']
        while True:
            _, name, title, prose = ControlInterface.get_section(control, skip_section_list)
            if not name:
                return
            if allowed_sections and name not in allowed_sections:
                skip_section_list.append(name)
                continue
            if prose:
                # section title will be from the section_dict, the part title, or the part name in that order
                # this way the user-provided section title can override the part title
                section_title = self._sections_dict.get(name, title) if self._sections_dict else title
                section_title = section_title if section_title else name
                skip_section_list.append(name)
                self._md_file.new_header(level=2, title=f'Control {section_title}')
                self._md_file.new_line(prose)
                self._md_file.new_paragraph()

    def _add_one_section(self, control: cat.Control, section: str) -> None:
        """Add specific control section."""
        prose = ControlInterface._get_control_section_prose(control, section)
        if prose:
            section_title = self._sections_dict.get(section) if self._sections_dict else section
            section_title = section_title if section_title else section
            self._md_file.new_header(level=2, title=f'Control {section_title}')
            self._md_file.new_line(prose)
            self._md_file.new_paragraph()

    def _insert_comp_info(self, part_label: str, comp_info: Dict[str, ComponentImpInfo]) -> None:
        """Insert prose from the component info."""
        if part_label in comp_info:
            info = comp_info[part_label]
            self._md_file.new_paragraph()
            self._md_file.new_line(info.prose)
            if info.implementation_status != const.STATUS_TRESTLE_UNKNOWN:
                self._md_file.new_header(
                    level=4, title=f'{const.IMPLEMENTATION_STATUS_HEADER}: {info.implementation_status}'
                )

    def _add_component_control_prompts(self, comp_dict: CompDict, comp_def_format=False) -> bool:
        """Add prompts to the markdown for the control itself, per component."""
        did_write = False
        level = 3 if comp_def_format else 4
        for dic in comp_dict.values():
            for statement_id, comp_info in dic.items():
                # is this control-level guidance for this component
                if statement_id == '':
                    # create new heading for this component and add guidance
                    self._md_file.new_paraline(comp_info.prose)
                    if comp_info.implementation_status != const.STATUS_TRESTLE_UNKNOWN:
                        self._md_file.new_header(
                            level=level,
                            title=f'{const.IMPLEMENTATION_STATUS_HEADER}: {comp_info.implementation_status}'
                        )
                    did_write = True
        return did_write

    def _add_implementation_response_prompts(
        self, control: cat.Control, comp_dict: CompDict, comp_def_format=False
    ) -> None:
        """Add the response request text for all parts to the markdown along with the header."""
        self._md_file.new_hr()
        self._md_file.new_paragraph()
        self._md_file.new_header(level=2, title=f'{const.SSP_MD_IMPLEMENTATION_QUESTION}')
        did_write_part = self._add_component_control_prompts(comp_dict, comp_def_format)

        # The comp_dict looks like:
        # This System:
        #    a.: guidance for part a, imp_status
        #    b.: guidance for part b, imp_status
        # OSCO:
        #    '': OSCO guidance for entire control, imp_status
        #    a.: OSCO guidance for part a, imp_status

        # if the control has no parts written out then enter implementation in the top level entry
        # but if it does have parts written out, leave top level blank and provide details in the parts
        # Note that parts corresponding to sections don't get written out here so a check is needed
        # If we have responses per component then enter them in separate ### sections
        if control.parts:
            for part in control.parts:
                if part.parts:
                    if part.name == 'statement':
                        for prt in part.parts:
                            if prt.name != 'item':
                                continue
                            if not did_write_part:
                                self._md_file.new_line(const.SSP_MD_LEAVE_BLANK_TEXT)
                                # insert extra line to make mdformat happy
                                self._md_file._add_line_raw('')
                            self._md_file.new_hr()
                            # if no label guess the label from the sub-part id
                            part_label = ControlInterface.get_label(prt)
                            part_label = prt.id.split('.')[-1] if not part_label else part_label
                            self._md_file.new_header(level=2, title=f'Implementation {part_label}')
                            added_content = False
                            for comp_name, dic in comp_dict.items():
                                if part_label in dic:
                                    if comp_name != const.SSP_MAIN_COMP_NAME:
                                        # insert the component name for ssp but not for comp_def
                                        # because there should only be one component in generated comp_def markdown
                                        if not comp_def_format:
                                            self._md_file.new_header(level=3, title=comp_name)
                                    self._insert_comp_info(part_label, dic)
                                    added_content = True
                            self._md_file.new_paragraph()
                            if not added_content:
                                self._md_file.new_line(f'{const.SSP_ADD_IMPLEMENTATION_FOR_ITEM_TEXT} {prt.id}')
                            did_write_part = True
        # if we loaded nothing for this control yet then it must need a fresh prompt for the control statement
        if not comp_dict and not did_write_part:
            self._md_file.new_line(f'{const.SSP_ADD_IMPLEMENTATION_FOR_CONTROL_TEXT} {control.id}')
        part_label = 'Statement'
        for comp_name, dic in comp_dict.items():
            if part_label in dic:
                if comp_name != const.SSP_MAIN_COMP_NAME:
                    self._md_file.new_header(level=3, title=comp_name)
                self._insert_comp_info(part_label, dic)
        self._md_file.new_hr()

    def _add_additional_content(self, control: cat.Control, profile: prof.Profile) -> List[str]:
        adds = ControlInterface.get_adds(control.id, profile)
        has_content = len(adds) > 0

        self._md_file.new_header(level=1, title=const.EDITABLE_CONTENT)
        self._md_file.new_line('<!-- Make additions and edits below -->')
        self._md_file.new_line(
            '<!-- The above represents the contents of the control as received by the profile, prior to additions. -->'  # noqa E501
        )
        self._md_file.new_line(
            '<!-- If the profile makes additions to the control, they will appear below. -->'  # noqa E501
        )
        self._md_file.new_line(
            '<!-- The above markdown may not be edited but you may edit the content below, and/or introduce new additions to be made by the profile. -->'  # noqa E501
        )
        self._md_file.new_line(
            '<!-- If there is a yaml header at the top, parameter values may be edited. Use --set-parameters to incorporate the changes during assembly. -->'  # noqa E501
        )
        self._md_file.new_line(
            '<!-- The content here will then replace what is in the profile for this control, after running profile-assemble. -->'  # noqa E501
        )
        if has_content:
            self._md_file.new_line(
                '<!-- The added parts in the profile for this control are below.  You may edit them and/or add new ones. -->'  # noqa E501
            )
        else:
            self._md_file.new_line(
                '<!-- The current profile has no added parts for this control, but you may add new ones here. -->'
            )
        self._md_file.new_line('<!-- Each addition must have a heading of the form ## Control my_addition_name -->')
        self._md_file.new_line(
            '<!-- See https://ibm.github.io/compliance-trestle/tutorials/ssp_profile_catalog_authoring/ssp_profile_catalog_authoring for guidance. -->'  # noqa E501
        )
        # next is to make mdformat happy
        self._md_file._add_line_raw('')

        added_sections: List[str] = []

        for add in adds:
            name, prose = add
            title = self._sections_dict.get(name, name) if self._sections_dict else name
            self._md_file.new_header(level=2, title=f'Control {title}')
            self._md_file.new_paraline(prose)
            added_sections.append(name)
        return added_sections

    def _prompt_required_sections(self, required_sections: List[str], added_sections: List[str]) -> None:
        """Add prompts for any required sections that haven't already been written out."""
        missing_sections = set(required_sections).difference(added_sections)
        for section in missing_sections:
            section_title = self._sections_dict.get(section, section)
            self._md_file.new_header(2, f'Control {section_title}')
            self._md_file.new_line(f'{const.PROFILE_ADD_REQUIRED_SECTION_FOR_CONTROL_TEXT}: {section_title}')

    def write_control_for_editing(
        self,
        dest_path: pathlib.Path,
        control: cat.Control,
        group_title: str,
        yaml_header: Optional[Dict],
        sections_dict: Optional[Dict[str, str]],
        additional_content: bool,
        prompt_responses: bool,
        profile: Optional[prof.Profile],
        overwrite_header_values: bool,
        required_sections: Optional[List[str]],
        allowed_sections: Optional[List[str]],
        component_def: Optional[comp.ComponentDefinition] = None,
        component_name: Optional[str] = None
    ) -> None:
        """
        Write out the control in markdown format into the specified directory.

        Args:
            dest_path: Path to the directory where the control will be written
            control: The control to write as markdown
            group_title: Title of the group containing the control
            yaml_header: Optional dict to be written as markdown yaml header
            sections_dict: Optional dict mapping short section names to long
            additional_content: Should the additional content be printed corresponding to profile adds
            prompt_responses: Should the markdown include prompts for implementation detail responses
            profile: Profile containing the adds making up additional content
            overwrite_header_values: Overwrite existing values in markdown header content but add new content
            required_sections: List of required sections that may need prompting for content
            allowed_sections: List of allowed sections that will appear in markdown
            component_def: Optional component definition containing imp req responses to be added to control markdown
            component_name: name of component to write out

        Returns:
            None

        Notes:
            The filename is constructed from the control's id, so only the markdown directory is required.
            If a yaml header is present in the file, new values in provided header will not replace those in the
            markdown header unless overwrite_header_values is true.  If it is true then overwrite any existing values,
            but in all cases new items from the provided header will be added to the markdown header.
            If the markdown file already exists, its current header and prose are read.
            Controls are checked if they are marked withdrawn, and if so they are not written out.
        """
        if ControlInterface.is_withdrawn(control):
            logger.debug(f'Not writing out control {control.id} since it is marked Withdrawn.')
            return
        control_file = dest_path / (control.id + '.md')
        # first read the existing markdown header and content if it exists
        existing_text, header = ControlReader.read_all_implementation_prose_and_header(
            control_file,
            component_def,
            component_name
        )
        self._md_file = MDWriter(control_file)
        self._sections_dict = sections_dict

        merged_header = copy.deepcopy(header)
        # if the control has an explicitly defined sort-id and there is none in the yaml_header, then insert it
        # in the yaml header and allow overwrite_header_values to control whether it overwrites an existing one
        # in the markdown header
        yaml_header = yaml_header if yaml_header else {}
        sort_id = ControlInterface.get_sort_id(control, True)
        if sort_id and const.SORT_ID not in yaml_header:
            yaml_header[const.SORT_ID] = sort_id
        ControlInterface.merge_dicts_deep(merged_header, yaml_header, overwrite_header_values)

        # merge any provided sections with sections in the header, with overwrite
        header_sections_dict = merged_header.get(const.SECTIONS_TAG, {})
        if sections_dict:
            header_sections_dict.update(sections_dict)
        if header_sections_dict:
            merged_header[const.SECTIONS_TAG] = header_sections_dict

        self._add_yaml_header(merged_header)

        self._add_control_statement(control, group_title)

        self._add_control_objective(control)

        # add allowed sections to the markdown
        self._add_sections(control, allowed_sections)

        # prompt responses for imp reqs
        if prompt_responses:
            self._add_implementation_response_prompts(control, existing_text, component_def is not None)

        # only used for profile-generate
        # add sections corresponding to added parts in the profile
        added_sections: List[str] = []
        if additional_content:
            added_sections = self._add_additional_content(control, profile)

        if required_sections:
            self._prompt_required_sections(required_sections, added_sections)

        self._md_file.write_out()

    def write_control_with_sections(
        self,
        control: cat.Control,
        group_title: str,
        sections: List[str],
        sections_dict: Optional[Dict[str, str]] = None,
        label_column: bool = True,
        add_group_to_title: bool = False
    ) -> str:
        """Write the control into markdown file with specified sections."""
        self._md_file = MDWriter(None)
        self._sections_dict = sections_dict
        if not isinstance(group_title, str):
            raise TrestleError(f'Group title must be provided and be a string, instead received: {group_title}')

        for section in sections:
            if 'statement' == section:
                self._add_control_statement(control, group_title, sections_dict, True, add_group_to_title)

            elif 'objective' == section:
                self._add_control_objective(control, sections_dict)

            elif 'table_of_parameters' == section:
                self.get_params(control, label_column, self._md_file)
            else:
                self._add_one_section(control, section)

        return '\n'.join(self._md_file._lines)

    def get_control_statement(self, control: cat.Control) -> List[str]:
        """Get the control statement as formatted markdown from a control."""
        self._md_file = MDWriter(None)
        self._add_control_statement_ssp(control)
        return self._md_file.get_lines()

    def get_params(self, control: cat.Control, label_column=False, md_file=None) -> List[str]:
        """Get parameters of a control as a markdown table for ssp_io, with optional third label column."""
        reader = ControlReader()
        param_dict = reader.get_control_param_dict(control, False)

        if param_dict:
            if md_file:
                self._md_file = md_file
            else:
                self._md_file = MDWriter(None)
            self._md_file.new_paragraph()
            self._md_file.set_indent_level(-1)
            if label_column:
                self._md_file.new_table(
                    [
                        [
                            key,
                            ControlReader.param_to_str(param_dict[key], ParameterRep.VALUE_OR_EMPTY_STRING),
                            ControlReader.param_to_str(param_dict[key], ParameterRep.LABEL_OR_CHOICES, True),
                        ] for key in param_dict.keys()
                    ], ['Parameter ID', 'Values', 'Label or Choices']
                )
            else:
                self._md_file.new_table(
                    [
                        [key, ControlReader.param_to_str(param_dict[key], ParameterRep.VALUE_OR_LABEL_OR_CHOICES)]
                        for key in param_dict.keys()
                    ], ['Parameter ID', 'Values']
                )
            self._md_file.set_indent_level(-1)
            return self._md_file.get_lines()

        return []
