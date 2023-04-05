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
from typing import Any, Dict, List, Optional

import trestle.oscal.catalog as cat
from trestle.common import const
from trestle.common.list_utils import as_dict, as_list, deep_set, merge_dicts, set_or_pop
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.core.control_interface import CompDict, ComponentImpInfo, ControlInterface, PartInfo
from trestle.core.control_reader import ControlReader
from trestle.core.markdown.md_writer import MDWriter
from trestle.oscal import profile as prof
from trestle.oscal.common import ImplementationStatus, Part

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
                        self._md_file.new_line(part.prose)
                    items.append(ControlInterface.get_part(part, item_type, skip_id))
            # unwrap the list if it is many levels deep
            while not isinstance(items, str) and len(items) == 1:
                items = items[0]
            self._md_file.new_paragraph()
            self._md_file.new_list(items)

    def _add_yaml_header(self, yaml_header: Optional[Dict]) -> None:
        if yaml_header:
            self._md_file.add_yaml_header(yaml_header)

    def _add_control_statement(self, control: cat.Control, group_title: str, print_group_title=True) -> None:
        """Add the control statement and items to the md file."""
        self._md_file.new_paragraph()
        control_id = control.id
        group_name = ''
        control_title = control.title

        if print_group_title:
            group_name = ' \[' + group_title + '\]'

        title = f'{control_id} -{group_name} {control_title}'

        header_title = 'Control Statement'
        self._md_file.new_header(level=1, title=title)
        self._md_file.new_header(level=2, title=header_title)
        self._md_file.set_indent_level(-1)
        self._add_part_and_its_items(control, const.STATEMENT, 'item')
        self._md_file.set_indent_level(-1)

    def _add_control_objective(self, control: cat.Control) -> None:
        if control.parts:
            for part in control.parts:
                if part.name == 'objective':
                    self._md_file.new_paragraph()
                    heading_title = 'Control Objective'
                    self._md_file.new_header(level=2, title=heading_title)
                    self._md_file.set_indent_level(-1)
                    self._add_part_and_its_items(control, 'objective', 'objective')
                    self._md_file.set_indent_level(-1)
                    return

    def _add_sections(self, control: cat.Control, allowed_sections: Optional[List[str]]) -> None:
        """Add the extra control sections after the main ones."""
        skip_section_list = [const.STATEMENT, 'item', 'objective']
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

    def _insert_status(self, status: ImplementationStatus, level: int) -> None:
        self._md_file.new_header(level=level, title=f'{const.IMPLEMENTATION_STATUS_HEADER}: {status.state}')
        # this used to output remarks also

    def _insert_rules(self, rules: List[str], level: int) -> None:
        if rules:
            self._md_file.new_header(level=level, title='Rules:')
            self._md_file.set_indent_level(0)
            self._md_file.new_list(rules)
            self._md_file.set_indent_level(-1)

    def _insert_comp_info(
        self, part_label: str, comp_info: Dict[str, ComponentImpInfo], context: ControlContext
    ) -> None:
        """Insert prose and status from the component info."""
        level = 3 if context.purpose == ContextPurpose.COMPONENT else 4
        if part_label in comp_info:
            info = comp_info[part_label]
            if context.purpose in [ContextPurpose.COMPONENT, ContextPurpose.SSP] and not info.rules:
                return
            self._md_file.new_paragraph()
            if info.prose:
                self._md_file.new_line(info.prose)
            else:
                self._md_file.new_line(f'{const.SSP_ADD_IMPLEMENTATION_FOR_ITEM_TEXT} {part_label} -->')

            self._insert_rules(info.rules, level)
            self._insert_status(info.status, level)
        else:
            self._insert_status(ImplementationStatus(state=const.STATUS_PLANNED), level)

    def _add_component_control_prompts(self, control_id: str, comp_dict: CompDict, context: ControlContext) -> bool:
        """Add prompts to the markdown for the control itself, per component."""
        if context.purpose not in [ContextPurpose.COMPONENT, ContextPurpose.SSP]:
            return False
        self._md_file.new_paraline(const.STATUS_PROMPT)
        self._md_file.new_paraline(const.RULES_WARNING)
        did_write = False
        # do special handling for This System
        if context.purpose == ContextPurpose.SSP:
            self._md_file.new_paragraph()
            self._md_file.new_header(3, const.SSP_MAIN_COMP_NAME)
            self._md_file.new_paragraph()
            prose = f'{const.SSP_ADD_THIS_SYSTEM_IMPLEMENTATION_FOR_CONTROL_TEXT}: {control_id} -->'
            status = ImplementationStatus(state=const.STATUS_PLANNED)
            if const.SSP_MAIN_COMP_NAME in comp_dict:
                comp_info = list(comp_dict[const.SSP_MAIN_COMP_NAME].values())[0]
                if comp_info.prose:
                    prose = comp_info.prose
                status = comp_info.status
            self._md_file.new_paraline(prose)
            self._insert_status(status, 4)
            did_write = True
        sorted_comp_names = sorted(comp_dict.keys())
        for comp_name in sorted_comp_names:
            dic = comp_dict[comp_name]
            # This System already handled
            if comp_name == const.SSP_MAIN_COMP_NAME:
                continue
            for comp_info in [val for key, val in dic.items() if key == '']:
                # don't output component name for component markdown since only one component
                if context.purpose != ContextPurpose.COMPONENT:
                    self._md_file.new_header(3, comp_name)
                prose = comp_info.prose if comp_info.prose != control_id else ''
                if not prose:
                    prose = f'{const.SSP_ADD_IMPLEMENTATION_FOR_CONTROL_TEXT}: {control_id} -->'
                self._md_file.new_paraline(prose)
                level = 3 if context.purpose == ContextPurpose.COMPONENT else 4
                self._insert_rules(comp_info.rules, level)
                self._insert_status(comp_info.status, level)
                did_write = True
        return did_write

    def _add_implementation_response_prompts(
        self, control: cat.Control, comp_dict: CompDict, context: ControlContext
    ) -> None:
        """Add the response request text for all parts to the markdown along with the header."""
        self._md_file.new_hr()
        self._md_file.new_paragraph()
        # top level request for implementation details
        self._md_file.new_header(level=2, title=f'{const.SSP_MD_IMPLEMENTATION_QUESTION}')

        # write out control level prose and status
        did_write_part = self._add_component_control_prompts(control.id, comp_dict, context)

        # if the control has no parts written out then enter implementation in the top level entry
        # but if it does have parts written out, leave top level blank and provide details in the parts
        # Note that parts corresponding to sections don't get written out here so a check is needed
        # If we have responses per component then enter them in separate ### sections
        if control.parts:
            for part in control.parts:
                if part.parts and part.name == const.STATEMENT:
                    for prt in part.parts:
                        if prt.name != 'item':
                            continue
                        # if no label guess the label from the sub-part id
                        part_label = ControlInterface.get_label(prt)
                        part_label = prt.id.split('.')[-1] if not part_label else part_label
                        # only write out part if rules apply to it
                        rules_apply = False
                        for _, dic in comp_dict.items():
                            if part_label in dic and dic[part_label].rules:
                                rules_apply = True
                                break
                        if not rules_apply:
                            continue
                        if not did_write_part:
                            self._md_file.new_line(const.SSP_MD_LEAVE_BLANK_TEXT)
                            # insert extra line to make mdformat happy
                            self._md_file._add_line_raw('')
                        self._md_file.new_hr()
                        self._md_file.new_header(level=2, title=f'Implementation for part {part_label}')
                        wrote_label_content = False
                        sorted_comp_names = sorted(comp_dict.keys())
                        for comp_name in sorted_comp_names:
                            dic = comp_dict[comp_name]
                            if comp_name == const.SSP_MAIN_COMP_NAME:
                                continue
                            if part_label in dic:
                                # insert the component name for ssp but not for comp_def
                                # because there should only be one component in generated comp_def markdown
                                if context.purpose != ContextPurpose.COMPONENT:
                                    self._md_file.new_header(level=3, title=comp_name)
                                self._insert_comp_info(part_label, dic, context)
                                wrote_label_content = True
                        if not wrote_label_content:
                            level = 3 if context.purpose == ContextPurpose.COMPONENT else 4
                            self._insert_status(ImplementationStatus(state=const.STATUS_PLANNED), level)
                        self._md_file.new_paragraph()
                        did_write_part = True
        # if we loaded nothing for this control yet then it must need a fresh prompt for the control statement
        if not comp_dict and not did_write_part:
            self._md_file.new_line(f'{const.SSP_ADD_IMPLEMENTATION_FOR_CONTROL_TEXT}: {control.id} -->')
            if context.purpose in [ContextPurpose.COMPONENT, ContextPurpose.SSP]:
                status = ControlInterface.get_status_from_props(control)
                self._insert_status(status, 3)
        if not did_write_part:
            part_label = ''
            for comp_name, dic in comp_dict.items():
                if part_label in dic:
                    if comp_name != const.SSP_MAIN_COMP_NAME:
                        self._md_file.new_header(level=3, title=comp_name)
                    self._insert_comp_info(part_label, dic, context)
        self._md_file.new_hr()

    def _dump_subpart_infos(self, level: int, part: Dict[str, Any]) -> None:
        name = part['name']
        title = self._sections_dict.get(name, name) if self._sections_dict else name
        self._md_file.new_header(level=level, title=title)
        if 'prose' in part:
            self._md_file.new_paraline(part['prose'])
        for subpart in as_list(part.get('parts', None)):
            self._dump_subpart_infos(level + 1, subpart)

    def _dump_subparts(self, level: int, part: Part) -> None:
        name = part.name
        title = self._sections_dict.get(name, name) if self._sections_dict else name
        self._md_file.new_header(level=level, title=title)
        if part.prose:
            self._md_file.new_paraline(part.prose)
        for subpart in as_list(part.parts):
            self._dump_subparts(level + 1, subpart)

    def _dump_section(self, level: int, part: Part, added_sections: List[str], prefix: str) -> None:
        title = self._sections_dict.get(part.name, part.name) if self._sections_dict else part.name
        title = f'{prefix} {title}' if prefix else title
        self._md_file.new_header(level=level, title=title)
        if part.prose:
            self._md_file.new_paraline(part.prose)
        for subpart in as_list(part.parts):
            self._dump_subparts(level + 1, subpart)
        added_sections.append(part.name)

    def _dump_section_info(self, level: int, part: Dict[str, Any], added_sections: List[str], prefix: str) -> None:
        part_prose = part.get('prose', None)
        part_subparts = part.get('parts', None)
        name = part['name']
        title = self._sections_dict.get(name, name) if self._sections_dict else name
        title = f'{prefix} {title}' if prefix else title
        self._md_file.new_header(level=level, title=title)
        if part_prose:
            self._md_file.new_paraline(part_prose)
        for subpart in as_list(part_subparts):
            self._dump_subpart_infos(level + 1, subpart)
        added_sections.append(name)

    def _add_additional_content(
        self,
        control: cat.Control,
        profile: prof.Profile,
        header: Dict[str, Any],
        part_id_map: Dict[str, str],
        found_alters: List[prof.Alter]
    ) -> List[str]:
        # get part and subpart info from adds of the profile
        part_infos = ControlInterface.get_all_add_info(control.id, profile)
        has_content = len(part_infos) > 0

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
        self._md_file.new_line(
            '<!-- Each addition must have a heading either of the form ## Control my_addition_name -->'
        )
        self._md_file.new_line('<!-- or ## Part a. (where the a. refers to one of the control statement labels.) -->')
        self._md_file.new_line('<!-- "## Control" parts are new parts added after the statement part. -->')
        self._md_file.new_line(
            '<!-- "## Part" parts are new parts added into the top-level statement part with that label. -->'
        )
        self._md_file.new_line('<!-- Subparts may be added with nested hash levels of the form ### My Subpart Name -->')
        self._md_file.new_line('<!-- underneath the parent ## Control or ## Part being added -->')
        self._md_file.new_line(
            '<!-- See https://ibm.github.io/compliance-trestle/tutorials/ssp_profile_catalog_authoring/ssp_profile_catalog_authoring for guidance. -->'  # noqa E501
        )
        # next is to make mdformat happy
        self._md_file._add_line_raw('')

        added_sections: List[str] = []

        control_part_id_map = part_id_map.get(control.id, {})
        statement_id = ControlInterface.get_statement_id(control)

        # if the file already has markdown content, read its alters
        if self._md_file.exists():
            if const.TRESTLE_ADD_PROPS_TAG in header:
                header.pop(const.TRESTLE_ADD_PROPS_TAG)
            for alter in found_alters:
                for add in as_list(alter.adds):
                    # by_id could refer to statement (Control) or part (Part)
                    if add.by_id:
                        # is this a part that goes after the control statement
                        if add.by_id == statement_id:
                            for part in as_list(add.parts):
                                if part.prose or part.parts:
                                    self._dump_section(2, part, added_sections, 'Control')
                        else:
                            # or is it a sub-part of a statement part
                            part_label = control_part_id_map.get(add.by_id, add.by_id)
                            if add.parts:
                                self._md_file.new_header(level=2, title=f'Part {part_label}')
                                for part in as_list(add.parts):
                                    if part.prose or part.parts:
                                        name = part.name
                                        # need special handling for statement parts because their name is 'item'
                                        # get the short name as last piece of the part id after the '.'
                                        if name == 'item':
                                            name = part.id.split('.')[-1]
                                        title = self._sections_dict.get(name, name) if self._sections_dict else name
                                        self._md_file.new_header(level=3, title=title)
                                        if part.prose:
                                            self._md_file.new_paraline(part.prose)
                                        for subpart in as_list(part.parts):
                                            self._dump_subparts(3, subpart)
                                        added_sections.append(name)
                    else:
                        # if not by_id just add at end of control's parts
                        for part in as_list(add.parts):
                            if part.prose or part.parts:
                                self._dump_section(2, part, added_sections, 'Control')
                    if add.props:
                        if const.TRESTLE_ADD_PROPS_TAG not in header:
                            header[const.TRESTLE_ADD_PROPS_TAG] = []
                        by_id = add.by_id
                        part_info = PartInfo(name='', prose='', props=add.props, smt_part=by_id)
                        _, prop_list = part_info.to_dicts(part_id_map.get(control.id, {}))
                        header[const.TRESTLE_ADD_PROPS_TAG].extend(prop_list)
        else:
            # md does not already exist so fill in directly
            in_part = ''
            for part_info in part_infos:
                part, prop_list = part_info.to_dicts(part_id_map.get(control.id, {}))
                # is this part of a statement part
                if part_info.smt_part and part_info.prose and part_info.smt_part in control_part_id_map:
                    # avoid outputting ## Part again if in same part
                    if not part_info.smt_part == in_part:
                        in_part = part_info.smt_part
                        part_label = control_part_id_map.get(part_info.smt_part, part_info.smt_part)
                        self._md_file.new_header(level=2, title=f'Part {part_label}')
                    self._dump_section_info(3, part, added_sections, '')
                # is it a control part
                elif part_info.prose or part_info.parts:
                    in_part = ''
                    self._dump_section_info(2, part, added_sections, 'Control')
                elif prop_list:
                    in_part = ''
                    if const.TRESTLE_ADD_PROPS_TAG not in header:
                        header[const.TRESTLE_ADD_PROPS_TAG] = []
                    header[const.TRESTLE_ADD_PROPS_TAG].extend(prop_list)
        return added_sections

    def _prompt_required_sections(self, required_sections: List[str], added_sections: List[str]) -> None:
        """Add prompts for any required sections that haven't already been written out."""
        missing_sections = set(required_sections).difference(added_sections)
        for section in sorted(missing_sections):
            section_title = self._sections_dict.get(section, section)
            self._md_file.new_header(2, f'Control {section_title}')
            self._md_file.new_line(f'{const.PROFILE_ADD_REQUIRED_SECTION_FOR_CONTROL_TEXT}: {section_title} -->')

    @staticmethod
    def _merge_headers(memory_header: Dict[str, Any], md_header: Dict[str, Any],
                       context: ControlContext) -> Dict[str, Any]:
        merged_header = copy.deepcopy(md_header)
        ControlInterface.merge_dicts_deep(merged_header, memory_header, False, 1)
        return merged_header

    def write_control_for_editing(
        self,
        context: ControlContext,
        control: cat.Control,
        dest_path: pathlib.Path,
        group_title: str,
        part_id_map: Dict[str, str],
        found_alters: List[prof.Alter]
    ) -> None:
        """
        Write out the control in markdown format into the specified directory.

        Args:
            context: The context of the control usage
            control: The control to write as markdown
            dest_path: Path to the directory where the control will be written
            group_title: Title of the group containing the control
            part_id_map: Mapping of part_id to label
            found_alters: List of alters read from the markdown file - if it exists

        Returns:
            None

        Notes:
            The filename is constructed from the control's id and created in the dest_path.
            If a yaml header is present in the file, new values in provided header will not replace those in the
            markdown header unless overwrite_header_values is true.  If it is true then overwrite any existing values,
            but in all cases new items from the provided header will be added to the markdown header.
            If the markdown file already exists, its current header and prose are read.
            Controls are checked if they are marked withdrawn, and if so they are not written out.
        """
        if ControlInterface.is_withdrawn(control):
            logger.debug(f'Not writing out control {control.id} since it is marked Withdrawn.')
            return

        control_file = dest_path / (control.id + const.MARKDOWN_FILE_EXT)
        # read the existing markdown header and content if it exists
        md_header, comp_dict = ControlReader.read_control_info_from_md(control_file, context)
        # replace the memory comp_dict with the md one if control exists
        if comp_dict:
            context.comp_dict = comp_dict

        header_comment_dict = {const.TRESTLE_ADD_PROPS_TAG: const.YAML_PROPS_COMMENT}
        if context.to_markdown:
            if context.purpose == ContextPurpose.PROFILE:
                header_comment_dict[const.SET_PARAMS_TAG] = const.YAML_PROFILE_VALUES_COMMENT
            elif context.purpose == ContextPurpose.SSP:
                header_comment_dict[const.SET_PARAMS_TAG] = const.YAML_SSP_VALUES_COMMENT
                header_comment_dict[const.COMP_DEF_RULES_PARAM_VALS_TAG] = const.YAML_RULE_PARAM_VALUES_SSP_COMMENT
            elif context.purpose == ContextPurpose.COMPONENT:
                header_comment_dict[const.COMP_DEF_RULES_PARAM_VALS_TAG
                                    ] = const.YAML_RULE_PARAM_VALUES_COMPONENT_COMMENT

        # begin adding info to the md file
        self._md_file = MDWriter(control_file, header_comment_dict)
        self._sections_dict = context.sections_dict

        context.merged_header = ControlWriter._merge_headers(context.merged_header, md_header, context)
        # if the control has an explicitly defined sort-id and there is none in the yaml_header, then insert it
        # in the yaml header and allow overwrite_header_values to control whether it overwrites an existing one
        # in the markdown header
        context.cli_yaml_header = as_dict(context.cli_yaml_header)
        if context.purpose != ContextPurpose.PROFILE:
            ControlInterface.merge_dicts_deep(
                context.merged_header, context.cli_yaml_header, context.overwrite_header_values
            )
        # the global contents are special and get overwritten on generate
        set_or_pop(
            context.merged_header,
            const.TRESTLE_GLOBAL_TAG,
            context.cli_yaml_header.get(const.TRESTLE_GLOBAL_TAG, None)
        )
        sort_id = ControlInterface.get_sort_id(control, True)
        if sort_id:
            deep_set(context.merged_header, [const.TRESTLE_GLOBAL_TAG, const.SORT_ID], sort_id)

        # merge any provided sections with sections in the header, with priority to the one from context (e.g. CLI)
        header_sections_dict = context.merged_header.get(const.SECTIONS_TAG, {})
        merged_sections_dict = merge_dicts(header_sections_dict, context.sections_dict)
        set_or_pop(context.merged_header, const.SECTIONS_TAG, merged_sections_dict)

        # now begin filling in content from the control in memory
        self._add_control_statement(control, group_title)

        self._add_control_objective(control)

        # add allowed sections to the markdown
        self._add_sections(control, context.allowed_sections)

        # prompt responses for imp reqs using special format if comp_def mode
        if context.prompt_responses:
            self._add_implementation_response_prompts(control, context.comp_dict, context)

        # for profile generate
        # add sections corresponding to added parts in the profile
        added_sections: List[str] = []
        if context.purpose == ContextPurpose.PROFILE:
            added_sections = self._add_additional_content(
                control, context.profile, context.merged_header, part_id_map, found_alters
            )

        self._add_yaml_header(context.merged_header)

        if context.required_sections:
            self._prompt_required_sections(context.required_sections, added_sections)

        self._md_file.write_out()
