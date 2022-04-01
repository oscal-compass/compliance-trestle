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
"""Handle direct i/o reading and writing controls as markdown."""
import copy
import logging
import pathlib
import re
import string
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import frontmatter

import trestle.oscal.catalog as cat
import trestle.oscal.ssp as ossp
from trestle.common import const
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_list, none_if_empty
from trestle.common.model_utils import ModelUtils
from trestle.common.str_utils import spaces_and_caps_to_snake
from trestle.core import generators as gens
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.markdown.markdown_processor import MarkdownNode
from trestle.core.markdown.md_writer import MDWriter
from trestle.oscal import common
from trestle.oscal import profile as prof

logger = logging.getLogger(__name__)


class ParameterRep(Enum):
    """Enum for ways to represent a parameter."""

    LEAVE_MOUSTACHE = 0
    VALUE_OR_STRING_NONE = 1
    LABEL_OR_CHOICES = 2
    VALUE_OR_LABEL_OR_CHOICES = 3
    VALUE_OR_EMPTY_STRING = 4


class ControlIOWriter():
    """Class to write controls as markdown."""

    def __init__(self):
        """Initialize the class."""
        self._md_file: Optional[MDWriter] = None

    @staticmethod
    def _wrap_label(label: str):
        l_side = '\['
        r_side = '\]'
        wrapped = '' if label == '' else f'{l_side}{label}{r_side}'
        return wrapped

    @staticmethod
    def get_prop(part_control: Union[common.Part, cat.Control], prop_name: str) -> str:
        """Get the property with that name."""
        for prop in as_list(part_control.props):
            if prop.name.strip().lower() == prop_name.strip().lower():
                return prop.value.strip()
        return ''

    @staticmethod
    def get_sort_id(control: cat.Control, allow_none=False) -> Optional[str]:
        """Get the sort-id for the control."""
        for prop in as_list(control.props):
            if prop.name == const.SORT_ID:
                return prop.value.strip()
        return None if allow_none else control.id

    @staticmethod
    def get_label(part_control: Union[common.Part, cat.Control]) -> str:
        """Get the label from the props of a part or control."""
        return ControlIOWriter.get_prop(part_control, 'label')

    def _get_part(self, part: common.Part, item_type: str, skip_id: Optional[str]) -> List[Union[str, List[str]]]:
        """
        Find parts with the specified item type, within the given part.

        For a part in a control find the parts in it that match the item_type
        Return list of string formatted labels and associated descriptive prose
        """
        items = []
        if part.name in ['statement', item_type]:
            # the options here are to force the label to be the part.id or the part.label
            # the label may be of the form (a) while the part.id is ac-1_smt.a.1.a
            # here we choose the latter and extract the final element
            label = ControlIOWriter.get_label(part)
            label = part.id.split('.')[-1] if not label else label
            wrapped_label = self._wrap_label(label)
            pad = '' if wrapped_label == '' or not part.prose else ' '
            prose = '' if part.prose is None else part.prose
            # top level prose has already been written out, if present
            # use presence of . in id to tell if this is top level prose
            if part.id != skip_id:
                items.append(f'{wrapped_label}{pad}{prose}')
            if part.parts:
                sub_list = []
                for prt in part.parts:
                    sub_list.extend(self._get_part(prt, item_type, skip_id))
                sub_list.append('')
                items.append(sub_list)
        return items

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
                    items.append(self._get_part(part, item_type, skip_id))
            # unwrap the list if it is many levels deep
            while not isinstance(items, str) and len(items) == 1:
                items = items[0]
            self._md_file.new_paragraph()
            self._md_file.new_list(items)

    def _add_yaml_header(self, yaml_header: Optional[Dict]) -> None:
        if yaml_header:
            self._md_file.add_yaml_header(yaml_header)

    @staticmethod
    def _gap_join(a_str: str, b_str: str) -> str:
        a_clean = a_str.strip()
        b_clean = b_str.strip()
        if not b_clean:
            return a_clean
        gap = '\n' if a_clean else ''
        return a_clean + gap + b_clean

    def _add_control_statement(
        self, control: cat.Control, group_title: str, sections_dict: Optional[Dict[str, str]] = None
    ) -> None:
        """Add the control statement and items to the md file."""
        self._md_file.new_paragraph()
        title = f'{control.id} - \[{group_title}\] {control.title}'
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
        label = self.get_label(control)
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

    @staticmethod
    def _get_control_section_part(part: common.Part, section_name: str) -> str:
        """Get the prose for a named section in the control."""
        prose = ''
        if part.name == section_name and part.prose is not None:
            prose = ControlIOWriter._gap_join(prose, part.prose)
        if part.parts:
            for sub_part in part.parts:
                prose = ControlIOWriter._gap_join(
                    prose, ControlIOWriter._get_control_section_part(sub_part, section_name)
                )
        return prose

    @staticmethod
    def _get_control_section_prose(control: cat.Control, section_name: str) -> str:
        prose = ''
        if control.parts:
            for part in control.parts:
                prose = ControlIOWriter._gap_join(prose, ControlIOWriter._get_control_section_part(part, section_name))
        return prose

    @staticmethod
    def _find_section_info(part: common.Part, skip_section_list: List[str]) -> Tuple[str, str, str]:
        """Find section not in list."""
        if part.prose and part.name not in skip_section_list:
            return part.id, part.name, part.title
        if part.parts:
            for sub_part in part.parts:
                id_, name, title = ControlIOWriter._find_section_info(sub_part, skip_section_list)
                if id_:
                    return id_, name, title
        return '', '', ''

    @staticmethod
    def _find_section(control: cat.Control, skip_section_list: List[str]) -> Tuple[str, str, str]:
        """Find next section not in list."""
        if control.parts:
            for part in control.parts:
                id_, name, title = ControlIOWriter._find_section_info(part, skip_section_list)
                if id_:
                    return id_, name, title
        return '', '', ''

    @staticmethod
    def _get_section(control: cat.Control, skip_section_list: List[str]) -> Tuple[str, str, str, str]:
        """Get sections that are not in the list."""
        id_, name, title = ControlIOWriter._find_section(control, skip_section_list)
        if id_:
            return id_, name, title, ControlIOWriter._get_control_section_prose(control, name)
        return '', '', '', ''

    def _add_sections(self, control: cat.Control, allowed_sections: Optional[List[str]]) -> None:
        """Add the extra control sections after the main ones."""
        skip_section_list = ['statement', 'item', 'objective']
        while True:
            _, name, title, prose = self._get_section(control, skip_section_list)
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

    def _insert_existing_text(self, part_label: str, existing_text: Dict[str, List[str]]) -> None:
        """Insert text captured in the previous markdown and reinsert to avoid overwrite."""
        if part_label in existing_text:
            self._md_file.new_paragraph()
            for line in existing_text[part_label]:
                self._md_file.new_line(line)

    def _add_implementation_response_prompts(
        self, control: cat.Control, comp_dict: Dict[str, Dict[str, List[str]]]
    ) -> None:
        """Add the response request text for all parts to the markdown along with the header."""
        self._md_file.new_hr()
        self._md_file.new_paragraph()
        self._md_file.new_header(level=2, title=f'{const.SSP_MD_IMPLEMENTATION_QUESTION}')

        # if the control has no parts written out then enter implementation in the top level entry
        # but if it does have parts written out, leave top level blank and provide details in the parts
        # Note that parts corresponding to sections don't get written out here so a check is needed
        # If we have responses per component then enter them in separate ### sections
        did_write_part = False
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
                            part_label = self.get_label(prt)
                            part_label = prt.id.split('.')[-1] if not part_label else part_label
                            self._md_file.new_header(level=2, title=f'Implementation {part_label}')
                            added_content = False
                            for comp_name, prose_dict in comp_dict.items():
                                if part_label in prose_dict:
                                    if comp_name != const.SSP_MAIN_COMP_NAME:
                                        self._md_file.new_header(level=3, title=comp_name)
                                    self._insert_existing_text(part_label, prose_dict)
                                    added_content = True
                            self._md_file.new_paragraph()
                            if not added_content:
                                self._md_file.new_line(f'{const.SSP_ADD_IMPLEMENTATION_FOR_ITEM_TEXT} {prt.id}')
                            did_write_part = True
        # if we loaded nothing for this control yet then it must need a fresh prompt for the control statement
        if not comp_dict and not did_write_part:
            self._md_file.new_line(f'{const.SSP_ADD_IMPLEMENTATION_FOR_CONTROL_TEXT} {control.id}')
        part_label = 'Statement'
        for comp_name, prose_dict in comp_dict.items():
            if part_label in prose_dict:
                if comp_name != const.SSP_MAIN_COMP_NAME:
                    self._md_file.new_header(level=3, title=comp_name)
                self._insert_existing_text(part_label, prose_dict)
        self._md_file.new_hr()

    @staticmethod
    def _get_adds(control_id: str, profile: prof.Profile) -> List[Tuple[str, str]]:
        adds = []
        if profile and profile.modify and profile.modify.alters:
            for alter in profile.modify.alters:
                if alter.control_id == control_id and alter.adds:
                    for add in alter.adds:
                        if add.parts:
                            for part in add.parts:
                                if part.prose:
                                    adds.append((part.name, part.prose))
        return adds

    def _add_additional_content(self, control: cat.Control, profile: prof.Profile) -> List[str]:
        adds = ControlIOWriter._get_adds(control.id, profile)
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

    @staticmethod
    def get_part_prose(control: cat.Control, part_name: str) -> str:
        """Get the prose for a named part."""
        prose = ''
        if control.parts:
            for part in control.parts:
                prose += ControlIOWriter._get_control_section_part(part, part_name)
        return prose.strip()

    @staticmethod
    def merge_dicts_deep(dest: Dict[Any, Any], src: Dict[Any, Any], overwrite_header_values: bool) -> None:
        """
        Merge dict src into dest.

        New items are always added from src to dest.
        Items present in both will be overriden dest if overwrite_header_values is True.
        """
        for key in src.keys():
            if key in dest:
                # if they are both dicts, recurse
                if isinstance(dest[key], dict) and isinstance(src[key], dict):
                    ControlIOWriter.merge_dicts_deep(dest[key], src[key], overwrite_header_values)
                # otherwise override dest if needed
                elif overwrite_header_values:
                    dest[key] = src[key]
            else:
                # if the item was not already in dest, add it from src
                dest[key] = src[key]

    def _prompt_required_sections(self, required_sections: List[str], added_sections: List[str]) -> None:
        """Add prompts for any required sections that haven't already been written out."""
        missing_sections = set(required_sections).difference(added_sections)
        for section in missing_sections:
            section_title = self._sections_dict.get(section, section)
            self._md_file.new_header(2, f'Control {section_title}')
            self._md_file.new_line(f'{const.PROFILE_ADD_REQUIRED_SECTION_FOR_CONTROL_TEXT}: {section_title}')

    @staticmethod
    def is_withdrawn(control: cat.Control) -> bool:
        """
        Determine if control is marked Withdrawn.

        Args:
            control: The control that may be marked withdrawn.

        Returns:
            True if marked withdrawn, false otherwise.

        This is determined by property with name 'status' with value 'Withdrawn'.
        """
        for prop in as_list(control.props):
            if prop.name and prop.value:
                if prop.name.lower().strip() == 'status' and prop.value.lower().strip() == 'withdrawn':
                    return True
        return False

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
        allowed_sections: Optional[List[str]]
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
        if ControlIOWriter.is_withdrawn(control):
            logger.debug(f'Not writing out control {control.id} since it is marked Withdrawn.')
            return
        control_file = dest_path / (control.id + '.md')
        # first read the existing markdown header and content if it exists
        existing_text, header = ControlIOReader.read_all_implementation_prose_and_header(control_file)
        self._md_file = MDWriter(control_file)
        self._sections_dict = sections_dict

        merged_header = copy.deepcopy(header)
        # if the control has an explicitly defined sort-id and there is none in the yaml_header, then insert it
        # in the yaml header and allow overwrite_header_values to control whether it overwrites an existing one
        # in the markdown header
        yaml_header = yaml_header if yaml_header else {}
        sort_id = ControlIOWriter.get_sort_id(control, True)
        if sort_id and const.SORT_ID not in yaml_header:
            yaml_header[const.SORT_ID] = sort_id
        ControlIOWriter.merge_dicts_deep(merged_header, yaml_header, overwrite_header_values)

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

        # only used for ssp-generate
        if prompt_responses:
            self._add_implementation_response_prompts(control, existing_text)

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
        label_column: bool = True
    ) -> str:
        """Write the control into markdown file with specified sections."""
        self._md_file = MDWriter(None)
        self._sections_dict = sections_dict

        for section in sections:
            if 'statement' == section:
                self._add_control_statement(control, group_title, sections_dict)

            elif 'objective' == section:
                self._add_control_objective(control, sections_dict)

            elif 'table_of_parameters' == section:
                self.get_params(control, label_column, self._md_file)

        self._add_sections(control, sections)

        return '\n'.join(self._md_file._lines)

    def get_control_statement(self, control: cat.Control) -> List[str]:
        """Get the control statement as formatted markdown from a control."""
        self._md_file = MDWriter(None)
        self._add_control_statement_ssp(control)
        return self._md_file.get_lines()

    def get_params(self, control: cat.Control, label_column=False, md_file=None) -> List[str]:
        """Get parameters of a control as a markdown table for ssp_io, with optional third label column."""
        reader = ControlIOReader()
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
                            ControlIOReader.param_to_str(param_dict[key], ParameterRep.VALUE_OR_EMPTY_STRING),
                            ControlIOReader.param_to_str(param_dict[key], ParameterRep.LABEL_OR_CHOICES, True),
                        ] for key in param_dict.keys()
                    ], ['Parameter ID', 'Values', 'Label or Choices']
                )
            else:
                self._md_file.new_table(
                    [
                        [key, ControlIOReader.param_to_str(param_dict[key], ParameterRep.VALUE_OR_LABEL_OR_CHOICES)]
                        for key in param_dict.keys()
                    ], ['Parameter ID', 'Values']
                )
            self._md_file.set_indent_level(-1)
            return self._md_file.get_lines()

        return []


class ControlIOReader():
    """Class to read controls from markdown."""

    @staticmethod
    def _strip_to_make_ncname(label: str) -> str:
        """Strip chars to conform with NCNAME regex."""
        orig_label = label
        # make sure first char is allowed
        while label and label[0] not in const.NCNAME_UTF8_FIRST_CHAR_OPTIONS:
            label = label[1:]
        new_label = label[:1]
        # now check remaining chars
        if len(label) > 1:
            for ii in range(1, len(label)):
                if label[ii] in const.NCNAME_UTF8_OTHER_CHAR_OPTIONS:
                    new_label += label[ii]
        # do final check to confirm it is NCNAME
        match = re.search(const.NCNAME_REGEX, new_label)
        if not match:
            raise TrestleError(f'Unable to convert label {orig_label} to NCNAME format.')
        return new_label

    @staticmethod
    def _load_control_lines_and_header(control_file: pathlib.Path) -> Tuple[List[str], Dict[str, Any]]:
        lines: List[str] = []
        try:
            content = control_file.open('r', encoding=const.FILE_ENCODING).read()
        except UnicodeDecodeError as e:
            logger.debug(f'See: {const.WEBSITE_ROOT}/errors/#utf-8-encoding-only')
            raise TrestleError(f'Unable to load file due to utf-8 encoding issues: {e}')
        try:
            fm = frontmatter.loads(content)
        except Exception as e:
            logger.error(
                f'Error parsing yaml header from file {control_file}. '
                f'This is most likely due to an incorrect yaml structure.'
            )
            raise TrestleError(f'Failure parsing yaml header on file {control_file}: {e}')
        raw_lines = fm.content.split('\n')
        header = fm.metadata
        # Any fully blank lines will be retained but as empty strings
        lines = [line.strip('\r\n').rstrip() for line in raw_lines]
        clean_lines = []
        # need to keep indentation and empty lines
        for line in lines:
            if line.startswith('<!--') or line.startswith('__________________'):
                continue
            clean_lines.append(line)
        return clean_lines, header

    @staticmethod
    def _parse_control_title_line(line: str) -> Tuple[int, str, str]:
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
    def _get_next_line(ii: int, lines: List[str]) -> Tuple[int, str]:
        while ii < len(lines):
            line = lines[ii]
            if line:
                return ii, line
            ii += 1
        return -1, ''

    @staticmethod
    def _get_next_indent(ii: int, lines: List[str]) -> Tuple[int, int, str]:
        """Seek to next content line.  ii remains at line read."""
        while 0 <= ii < len(lines):
            line = lines[ii]
            if line:
                if line[0] == '#':
                    return ii, -1, line
                indent = ControlIOReader._indent(line)
                if indent >= 0:
                    # extract text after -
                    start = indent + 1
                    while start < len(line) and line[start] == ' ':
                        start += 1
                    if start >= len(line):
                        raise TrestleError(f'Invalid line {line}')
                    return ii, indent, line[start:]
                return ii, indent, line
            ii += 1
        return ii, -1, ''

    @staticmethod
    def _read_part_id_prose(line: str) -> Tuple[str, str]:
        """Extract the part id letter or number and prose from line."""
        start = line.find('\\[')
        end = line.find('\\]')
        prose = line.strip() if start < 0 else line[end + 2:].strip()
        id_ = '' if start < 0 or end < 0 else line[start + 2:end]
        return id_, prose

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

        return label_prefix + ControlIOReader._bump_label(label_suffix)

    @staticmethod
    def _read_parts(indent: int, ii: int, lines: List[str], parent_id: str,
                    parts: List[common.Part]) -> Tuple[int, List[common.Part]]:
        """If indentation level goes up or down, create new list or close current one."""
        while True:
            ii, new_indent, line = ControlIOReader._get_next_indent(ii, lines)
            if new_indent < 0:
                # we are done reading control statement
                return ii, parts
            if new_indent == indent:
                # create new item part and add to current list of parts
                id_text, prose = ControlIOReader._read_part_id_prose(line)
                # id_text is the part id and needs to be as a label property value
                # if none is there then create one from previous part, or use default
                if not id_text:
                    prev_label = ControlIOWriter.get_label(parts[-1]) if parts else ''
                    id_text = ControlIOReader._create_next_label(prev_label, indent)
                id_ = ControlIOReader._strip_to_make_ncname(parent_id.rstrip('.') + '.' + id_text.strip('.'))
                name = 'objective' if id_.find('_obj') > 0 else 'item'
                prop = common.Property(name='label', value=id_text)
                part = common.Part(name=name, id=id_, prose=prose, props=[prop])
                parts.append(part)
                ii += 1
            elif new_indent > indent:
                # add new list of parts to last part and continue
                if len(parts) == 0:
                    raise TrestleError(f'Improper indentation structure: {line}')
                ii, new_parts = ControlIOReader._read_parts(new_indent, ii, lines, parts[-1].id, [])
                if new_parts:
                    parts[-1].parts = new_parts
            else:
                # return list of sub-parts
                return ii, parts

    @staticmethod
    def _read_control_statement(ii: int, lines: List[str], control_id: str) -> Tuple[int, common.Part]:
        """Search for the Control statement and read until next ## Control."""
        while 0 <= ii < len(lines) and not lines[ii].startswith('## Control '):
            ii += 1
        if ii >= len(lines):
            raise TrestleError(f'Control statement not found for control {control_id}')
        ii += 1

        ii, line = ControlIOReader._get_next_line(ii, lines)
        if ii < 0:
            # This means no statement and control withdrawn (this happens in NIST catalog)
            return ii, None
        if line and line[0] == ' ' and line.lstrip()[0] != '-':
            # prose that appears indented but has no - : treat it as the normal statement prose
            line = line.lstrip()
            indent = -1
            ii += 1
        else:
            ii, indent, line = ControlIOReader._get_next_indent(ii, lines)

        statement_part = common.Part(name='statement', id=f'{control_id}_smt')
        # first line is either statement prose or start of statement parts
        if indent < 0:
            statement_part.prose = line
            ii += 1
        # we have absorbed possible statement prose.
        # now just read parts recursively
        # if there was no statement prose, this will re-read the line just read
        # as the start of the statement's parts
        ii, parts = ControlIOReader._read_parts(0, ii, lines, statement_part.id, [])
        statement_part.parts = parts if parts else None
        return ii, statement_part

    @staticmethod
    def _read_control_objective(ii: int, lines: List[str], control_id: str) -> Tuple[int, Optional[common.Part]]:
        ii_orig = ii
        while 0 <= ii < len(lines) and not lines[ii].startswith('## Control Objective'):
            ii += 1

        if ii >= len(lines):
            return ii_orig, None
        ii += 1

        ii, line = ControlIOReader._get_next_line(ii, lines)
        if ii < 0:
            raise TrestleError(f'Unable to parse objective from control markdown {control_id}')
        if line and line[0] == ' ' and line.lstrip()[0] != '-':
            # prose that appears indented but has no - : treat it as the normal objective prose
            line = line.lstrip()
            indent = -1
            ii += 1
        else:
            ii, indent, line = ControlIOReader._get_next_indent(ii, lines)

        objective_part = common.Part(name='objective', id=f'{control_id}_obj')
        # first line is either objective prose or start of objective parts
        if indent < 0:
            objective_part.prose = line
            ii += 1
        # we have absorbed possible objective prose.
        # now just read parts recursively
        # if there was no objective prose, this will re-read the line just read
        # as the start of the objective's parts
        ii, parts = ControlIOReader._read_parts(0, ii, lines, objective_part.id, [])
        objective_part.parts = parts if parts else None
        return ii, objective_part

    @staticmethod
    def _read_sections(ii: int, lines: List[str], control_id: str,
                       control_parts: List[common.Part]) -> Tuple[int, Optional[List[common.Part]]]:
        """Read all sections following the section separated by ## Control."""
        new_parts = []
        prefix = '## Control '
        while 0 <= ii < len(lines):
            line = lines[ii]
            if line.startswith('## What is the solution') or line.startswith(f'# {const.EDITABLE_CONTENT}'):
                ii += 1
                continue
            if not line:
                ii += 1
                continue
            if line and not line.startswith(prefix):
                # the control has no sections to read, so exit the loop
                break
            label = line[len(prefix):].strip()
            prose = ''
            ii += 1
            while 0 <= ii < len(lines) and not lines[ii].startswith(prefix) and not lines[ii].startswith(
                    f'# {const.EDITABLE_CONTENT}'):
                prose = '\n'.join([prose, lines[ii]])
                ii += 1
            if prose:
                if label.lower() == 'guidance':
                    id_ = ControlIOReader._strip_to_make_ncname(control_id + '_gdn')
                else:
                    id_ = ControlIOReader._strip_to_make_ncname(control_id + '_' + label)
                label = ControlIOReader._strip_to_make_ncname(label)
                new_parts.append(common.Part(id=id_, name=label, prose=prose.strip('\n')))
        if new_parts:
            control_parts = [] if not control_parts else control_parts
            control_parts.extend(new_parts)
        control_parts = none_if_empty(control_parts)
        return ii, control_parts

    @staticmethod
    def _clean_prose(prose: List[str]) -> List[str]:
        # remove empty and horizontal rule lines at start and end of list of prose lines
        forward_index = 0
        for line in prose:
            if line.strip() and not line.startswith('____'):
                break
            forward_index += 1
        new_prose = prose[forward_index:]
        reverse_index = 0
        for line in reversed(new_prose):
            if line.strip() and not line.startswith('____'):
                break
            reverse_index += 1
        clean_prose = new_prose[:len(new_prose) - reverse_index]
        clean_prose = clean_prose if clean_prose else ['']
        # if there is no useful prose this will return [''] and allow generation of a statement with empty prose
        return clean_prose

    @staticmethod
    def _simplify_name(name: str) -> str:
        name = name.lower().strip()
        return re.sub(' +', ' ', name)

    @staticmethod
    def _comp_name_in_dict(comp_name: str, comp_dict: Dict[str, List[Dict[str, str]]]) -> str:
        """If the name is already in the dict in a similar form, stick to that form."""
        simple_name = ControlIOReader._simplify_name(comp_name)
        for name in comp_dict.keys():
            if simple_name == ControlIOReader._simplify_name(name):
                return name
        return comp_name

    @staticmethod
    def _add_node_to_dict(
        comp_name: str,
        label: str,
        comp_dict: Dict[str, Dict[str, List[str]]],
        node: MarkdownNode,
        control_id: str,
        comp_list: List[str]
    ) -> None:
        prose = ControlIOReader._clean_prose(node.content.text)
        if node.key.startswith('### '):
            if len(node.key.split()) <= 1:
                raise TrestleError(f'Line in control {control_id} markdown starts with ### but has no component name.')
            comp_name = node.key.split(' ', 1)[1].strip()
            simp_comp_name = ControlIOReader._simplify_name(comp_name)
            if simp_comp_name == ControlIOReader._simplify_name(const.SSP_MAIN_COMP_NAME):
                raise TrestleError(
                    f'Response in control {control_id} has {const.SSP_MAIN_COMP_NAME} as a component heading.  '
                    'Instead, place all response prose for the default component at the top of th section, '
                    'with no ### component specified.  It will be entered as prose for the default system component.'
                )
            if simp_comp_name in comp_list:
                raise TrestleError(
                    f'Control {control_id} has a section with two ### component headings for {comp_name}.  '
                    'Please combine the sections so there is only one heading for each component in a statement.'
                )
            comp_list.append(simp_comp_name)
            comp_name = ControlIOReader._comp_name_in_dict(comp_name, comp_dict)
        if comp_name in comp_dict:
            if label in comp_dict[comp_name]:
                comp_dict[comp_name][label].extend(prose)
            else:
                comp_dict[comp_name][label] = prose
        else:
            comp_dict[comp_name] = {label: prose}
        for subnode in node.subnodes:
            ControlIOReader._add_node_to_dict(comp_name, label, comp_dict, subnode, control_id, comp_list)

    @staticmethod
    def read_all_implementation_prose_and_header(
        control_file: pathlib.Path
    ) -> Tuple[Dict[str, Dict[str, List[str]]], Dict[str, List[str]]]:
        """
        Find all labels and associated prose in this control.

        Args:
            control_file: path to the control markdown file

        Returns:
            Dictionary by comp_name of Dictionaries of part labels and corresponding prose read from the markdown file.
            Also returns the yaml header as dict in second part of tuple.
            This does not generate components - it only tracks component names and associated responses.
        """
        comp_dict = {}
        yaml_header = {}
        # this level only adds for top level component but add_node_to_dict can add for other components
        comp_name = const.SSP_MAIN_COMP_NAME
        control_id = control_file.stem
        try:
            if not control_file.exists():
                return comp_dict, yaml_header
            md_api = MarkdownAPI()
            yaml_header, control = md_api.processor.process_markdown(control_file)

            imp_string = 'Implementation'
            headers = control.get_all_headers_for_key(imp_string, False)
            header_list = list(headers)
            if not header_list:
                # if statement has no parts there is only one response for entire control
                headers = control.get_all_headers_for_key(const.SSP_MD_IMPLEMENTATION_QUESTION, False)
                # should be only one header, so warn if others found
                n_headers = 0
                for header in headers:
                    node = control.get_node_for_key(header)
                    ControlIOReader._add_node_to_dict(comp_name, 'Statement', comp_dict, node, control_id, [])
                    n_headers += 1
                    if n_headers > 1:
                        logger.warning(
                            f'Control {control_id} has single statement with extra response #{n_headers}'
                            ' when it should only have one.'
                        )
            else:
                for header in header_list:
                    tokens = header.split(' ', 2)
                    if tokens[0] == '##' and tokens[1] == imp_string:
                        label = tokens[2].strip()
                        node = control.get_node_for_key(header)
                        ControlIOReader._add_node_to_dict(comp_name, label, comp_dict, node, control_id, [])

        except TrestleError as e:
            raise TrestleError(f'Error occurred reading {control_file}: {e}')
        return comp_dict, yaml_header

    @staticmethod
    def _insert_header_content(imp_req: ossp.ImplementedRequirement, header: Dict[str, Any], control_id: str) -> None:
        """Insert yaml header content into the imp_req and its by_comps."""
        dict_ = header.get(const.SSP_FEDRAMP_TAG, {})
        # if an attribute is in the dict but it is None, need to make sure we get empty list anyway
        control_orig = as_list(dict_.get(const.CONTROL_ORIGINATION, []))
        imp_status = as_list(dict_.get(const.IMPLEMENTATION_STATUS, []))
        roles = as_list(dict_.get(const.RESPONSIBLE_ROLES, []))
        props = []
        responsible_roles = []
        for co in control_orig:
            if isinstance(co, str):
                props.append(common.Property(ns=const.NAMESPACE_FEDRAMP, name=const.CONTROL_ORIGINATION, value=co))
            elif isinstance(co, dict):
                if const.INHERITED in co:
                    uuid = co[const.INHERITED]
                    props.append(common.Property(name=const.LEV_AUTH_UUID, value=uuid))
                    props.append(
                        common.Property(
                            ns=const.NAMESPACE_FEDRAMP, name=const.CONTROL_ORIGINATION, value=const.INHERITED
                        )
                    )
                else:
                    raise TrestleError(f'The yaml header for control {control_id} has unexpected content: {co}')
            else:
                raise TrestleError(f'The yaml header for control {control_id} has unexpected content: {co}')
        for status in imp_status:
            if isinstance(status, str):
                props.append(
                    common.Property(ns=const.NAMESPACE_FEDRAMP, name=const.IMPLEMENTATION_STATUS, value=status)
                )
            elif isinstance(status, dict):
                if const.PLANNED in status:
                    if const.COMPLETION_DATE not in status:
                        raise TrestleError(
                            f'Planned status in the control {control_id} yaml header must '
                            f'specify completion date: {status}'
                        )
                    props.append(
                        common.Property(ns=const.NAMESPACE_FEDRAMP, name=const.PLANNED, value=status[const.PLANNED])
                    )
                    datestr = status[const.COMPLETION_DATE]
                    if isinstance(datestr, datetime):
                        datestr = datestr.strftime('%Y-%m-%d')
                    else:
                        datestr = str(datestr)
                    props.append(
                        common.Property(ns=const.NAMESPACE_FEDRAMP, name=const.PLANNED_COMPLETION_DATE, value=datestr)
                    )
                else:
                    if len(status) != 1:
                        raise TrestleError(f'Unexpected content in control {control_id} yaml header: {status}')
                    value = list(status.keys())[0]
                    remark = list(status.values())[0]
                    props.append(
                        common.Property(
                            ns=const.NAMESPACE_FEDRAMP,
                            name=const.IMPLEMENTATION_STATUS,
                            value=value,
                            remarks=common.Remarks(__root__=remark)
                        )
                    )
            else:
                raise TrestleError(f'Unexpected content in control {control_id} yaml header: {status}')
        for role in roles:
            if isinstance(role, str):
                # role_id must conform to NCNAME regex
                role = role.strip().replace(' ', '_')
                if role:
                    responsible_roles.append(common.ResponsibleRole(role_id=role))
            else:
                logger.warning(f'Role in header for control {control_id} not recognized: {role}')
        if props:
            imp_req.props = as_list(imp_req.props)
            imp_req.props.extend(props)
        if responsible_roles:
            imp_req.responsible_roles = as_list(imp_req.responsible_roles)
            imp_req.responsible_roles.extend(responsible_roles)
            imp_req.responsible_roles = none_if_empty(imp_req.responsible_roles)
            # enforce single list of resp. roles for control and each by_comp
            for by_comp in as_list(imp_req.by_components):
                by_comp.responsible_roles = imp_req.responsible_roles

    @staticmethod
    def read_implemented_requirement(
        control_file: pathlib.Path, avail_comps: Dict[str, ossp.SystemComponent]
    ) -> Tuple[str, ossp.ImplementedRequirement]:
        """
        Get the implementated requirement associated with given control and link to existing components or new ones.

        Args:
            control_file: path of the control markdown file
            avail_comps: dictionary of known components keyed by component name

        Returns:
            Tuple: The control sort-id and the one implemented requirement for this control.

        Notes:
            Each statement may have several responses, with each response in a by_component for a specific component.
            statement_map keeps track of statements that may have several by_component responses.
        """
        control_id = control_file.stem
        comp_dict, header = ControlIOReader.read_all_implementation_prose_and_header(control_file)

        statement_map: Dict[str, ossp.Statement] = {}
        # create a new implemented requirement linked to the control id to hold the statements
        imp_req: ossp.ImplementedRequirement = gens.generate_sample_model(ossp.ImplementedRequirement)
        imp_req.control_id = control_id

        # the comp_dict captures all component names referenced by the control
        for comp_name in comp_dict.keys():
            if comp_name in avail_comps:
                component = avail_comps[comp_name]
            else:
                # here is where we create a new component on the fly as needed
                component = gens.generate_sample_model(ossp.SystemComponent)
                component.title = comp_name
                avail_comps[comp_name] = component
            for label, prose_lines in comp_dict[comp_name].items():
                # create a statement to hold the by-components and assign the statement id
                if label == 'Statement':
                    statement_id = f'{control_id}_smt'
                else:
                    clean_label = label.strip('.')
                    statement_id = ControlIOReader._strip_to_make_ncname(f'{control_id}_smt.{clean_label}')
                if statement_id in statement_map:
                    statement = statement_map[statement_id]
                else:
                    statement: ossp.Statement = gens.generate_sample_model(ossp.Statement)
                    statement.statement_id = statement_id
                    statement.by_components = []
                    statement_map[statement_id] = statement
                # create a new by-component to add to this statement
                by_comp: ossp.ByComponent = gens.generate_sample_model(ossp.ByComponent)
                # link it to the component uuid
                by_comp.component_uuid = component.uuid
                # add the response prose to the description
                by_comp.description = '\n'.join(prose_lines)
                statement.by_components.append(by_comp)

        imp_req.statements = list(statement_map.values())
        ControlIOReader._insert_header_content(imp_req, header, control_id)
        sort_id = header.get(const.SORT_ID, control_id)
        return sort_id, imp_req

    @staticmethod
    def _read_added_part(ii: int, lines: List[str], control_id: str,
                         sections_dict: Dict[str, str]) -> Tuple[int, Optional[common.Part]]:
        """Read a single part indicated by ## Control foo."""
        snake_dict: Dict[str, str] = {}
        # create reverse lookup of long snake name to short name needed for part
        for key, value in sections_dict.items():
            snake_dict[spaces_and_caps_to_snake(value)] = key
        while 0 <= ii < len(lines):
            # look for ## Control foo - then read prose
            line = lines[ii]
            prefix = '## Control '
            if line:
                if not line.startswith(prefix):
                    raise TrestleError(f'Unexpected line in {const.EDITABLE_CONTENT} for control {control_id}: {line}')
                part_name_long_raw = line[len(prefix):].strip()
                part_name_snake = spaces_and_caps_to_snake(part_name_long_raw)
                # if the long name isn't there use the snake version for the part
                # otherwise the part will have the desired short name for the corresponding section
                part_name = snake_dict.get(part_name_snake, part_name_snake)
                # use sections dict to find correct title otherwise use the title from the markdown
                part_title = sections_dict.get(part_name, part_name_long_raw)
                prose_lines = []
                ii += 1
                have_content = False
                while 0 <= ii < len(lines):
                    line = lines[ii]
                    if not line.startswith(prefix):
                        if line:
                            have_content = True
                        prose_lines.append(line)
                        ii += 1
                        continue
                    break
                if have_content:
                    prose = '\n'.join(prose_lines)
                    # strip leading / trailing new lines.
                    prose = prose.strip('\n')
                    id_ = f'{control_id}_{part_name}'
                    part = common.Part(id=id_, name=part_name, prose=prose, title=part_title)
                    return ii, part
            ii += 1
        return -1, None

    @staticmethod
    def read_new_alters_and_params(control_path: pathlib.Path,
                                   required_sections_list: List[str]) -> Tuple[str, List[prof.Alter], Dict[str, Any]]:
        """Get parts for the markdown control corresponding to Editable Content - along with the set-parameter dict."""
        control_id = control_path.stem
        new_alters: List[prof.Alter] = []
        lines, header = ControlIOReader._load_control_lines_and_header(control_path)
        # extract the sort_id if present in header
        sort_id = header.get(const.SORT_ID, control_id)
        # query header for mapping of short to long section names
        sections_dict: Dict[str, str] = header.get(const.SECTIONS_TAG, {})
        found_sections: List[str] = []
        ii = 0
        while 0 <= ii < len(lines):
            line = lines[ii]
            if line.startswith(f'# {const.EDITABLE_CONTENT}'):
                ii += 1
                while 0 <= ii < len(lines):
                    ii, part = ControlIOReader._read_added_part(ii, lines, control_id, sections_dict)
                    if ii < 0:
                        break
                    # if section is required and it hasn't been edited with prose raise error
                    if part.name in required_sections_list and part.prose.startswith(
                            const.PROFILE_ADD_REQUIRED_SECTION_FOR_CONTROL_TEXT):
                        missing_section = sections_dict.get(part.name, part.name)
                        raise TrestleError(
                            f'Control {control_id} is missing prose for required section {missing_section}'
                        )
                    alter = prof.Alter(
                        control_id=control_id,
                        adds=[prof.Add(parts=[part], position='after', by_id=f'{control_id}_smt')]
                    )
                    new_alters.append(alter)
                    found_sections.append(part.name)
            else:
                ii += 1
        missing_sections = set(required_sections_list) - set(found_sections)
        if missing_sections:
            raise TrestleError(f'Control {control_id} is missing required sections {missing_sections}')
        param_dict: Dict[str, Any] = {}
        header_params = header.get(const.SET_PARAMS_TAG, {})
        if header_params:
            param_dict.update(header_params)
        return sort_id, new_alters, param_dict

    @staticmethod
    def param_values_as_str_list(param: common.Parameter) -> List[str]:
        """Convert param values to list of strings."""
        return [val.__root__ for val in as_list(param.values)]

    @staticmethod
    def param_values_as_str(param: common.Parameter, brackets=False) -> Optional[str]:
        """Convert param values to string with optional brackets."""
        if not param.values:
            return None
        values_str = ', '.join(ControlIOReader.param_values_as_str_list(param))
        return f'[{values_str}]' if brackets else values_str

    @staticmethod
    def param_selection_as_str(param: common.Parameter, verbose=False, brackets=False) -> str:
        """Convert parameter selection to str."""
        if param.select and param.select.choice:
            how_many_str = ''
            if param.select.how_many:
                how_many_str = 'one' if param.select.how_many == common.HowMany.one else 'one or more'
            choices_str = '; '.join(as_list(param.select.choice))
            choices_str = f'[{choices_str}]' if brackets else choices_str
            choices_str = f'Choose {how_many_str}: {choices_str}' if verbose else choices_str
            return choices_str
        return ''

    @staticmethod
    def param_label_choices_as_str(param: common.Parameter, verbose=False, brackets=False) -> str:
        """Convert param label or choices to string, using choices if present."""
        choices = ControlIOReader.param_selection_as_str(param, verbose, brackets)
        text = choices if choices else param.label
        text = text if text else param.id
        return text

    @staticmethod
    def param_to_str(
        param: common.Parameter,
        param_rep: ParameterRep,
        verbose=False,
        brackets=False,
        params_format: Optional[str] = None,
    ) -> Optional[str]:
        """
        Convert parameter to string based on best available representation.

        Args:
            param_rep: how to represent the parameter
            verbose: provide verbose text for selection choices
            brackets: add brackets around the lists of items
            params_format: a string containing a single dot that represents a form of highlighting around the param

        Returns:
            formatted string or None
        """
        param_str = None
        if param_rep == ParameterRep.VALUE_OR_STRING_NONE:
            param_str = ControlIOReader.param_values_as_str(param)
            param_str = param_str if param_str else 'None'
        elif param_rep == ParameterRep.LABEL_OR_CHOICES:
            param_str = ControlIOReader.param_label_choices_as_str(param, verbose, brackets)
        elif param_rep == ParameterRep.VALUE_OR_LABEL_OR_CHOICES:
            param_str = ControlIOReader.param_values_as_str(param)
            if not param_str:
                param_str = ControlIOReader.param_label_choices_as_str(param, verbose, brackets)
        elif param_rep == ParameterRep.VALUE_OR_EMPTY_STRING:
            param_str = ControlIOReader.param_values_as_str(param, brackets)
            if not param_str:
                param_str = ''
        if param_str is not None and params_format:
            if params_format.count('.') > 1:
                raise TrestleError(
                    f'Additional text {params_format} '
                    f'for the parameters cannot contain multiple dots (.)'
                )
            param_str = params_format.replace('.', param_str)
        return param_str

    @staticmethod
    def str_to_param(param: common.Parameter, param_str: str) -> None:
        """Replace parameter contents with contents in string."""
        # this is a simple version that replaces the values but it can be more elaborate
        param.values = [common.ParameterValue(__root__=param_str)]

    @staticmethod
    def get_control_param_dict(
        control: cat.Control,
        values_only: bool,
    ) -> Dict[str, common.Parameter]:
        """
        Create mapping of param id's to params.

        Args:
            control: the control containing params of interest
            values_only: only add params to the dict that have actual values

        Returns:
            Dictionary of param_id mapped to param

        Notes:
            Warning is given if there is a parameter with no ID
        """
        param_dict: Dict[str, common.Parameter] = {}
        for param in as_list(control.params):
            if not param.id:
                logger.warning(f'Control {control.id} has parameter with no id.  Ignoring.')
            if param.values or not values_only:
                param_dict[param.id] = param
        return param_dict

    @staticmethod
    def read_control(control_path: pathlib.Path, set_parameters: bool) -> Tuple[cat.Control, str]:
        """Read the control and group title from the markdown file."""
        control = gens.generate_sample_model(cat.Control)
        md_api = MarkdownAPI()
        yaml_header, control_tree = md_api.processor.process_markdown(control_path)
        control_titles = list(control_tree.get_all_headers_for_level(1))
        if len(control_titles) == 0:
            raise TrestleError(f'Control markdown: {control_path} contains no control title.')

        control.id, group_title, control.title = ControlIOReader._parse_control_title_line(control_titles[0])

        control_headers = list(control_tree.get_all_headers_for_level(2))
        if len(control_headers) == 0:
            raise TrestleError(f'Control markdown: {control_path} contains no control statements.')

        control_statement = control_tree.get_node_for_key(control_headers[0])
        rc, statement_part = ControlIOReader._read_control_statement(
            0, control_statement.content.raw_text.split('\n'), control.id
        )
        if rc < 0:
            return control, group_title
        control.parts = [statement_part] if statement_part else None
        control_objective = control_tree.get_node_for_key('## Control Objective')
        if control_objective is not None:
            _, objective_part = ControlIOReader._read_control_objective(
                0, control_objective.content.raw_text.split('\n'), control.id
            )
            if objective_part:
                if control.parts:
                    control.parts.append(objective_part)
                else:
                    control.parts = [objective_part]
        for header_key in control_tree.get_all_headers_for_key('## Control', False):
            if header_key not in {control_headers[0], '## Control Objective', control_titles[0]}:
                section_node = control_tree.get_node_for_key(header_key)
                _, control.parts = ControlIOReader._read_sections(
                    0, section_node.content.raw_text.split('\n'), control.id, control.parts
                )
        if set_parameters:
            params: Dict[str, str] = yaml_header.get(const.SET_PARAMS_TAG, [])
            if params:
                control.params = []
                for id_, param_dict in params.items():
                    param_dict['id'] = id_
                    param = ModelUtils.dict_to_parameter(param_dict)
                    control.params.append(param)
        if const.SORT_ID in yaml_header:
            control.props = control.props if control.props else []
            control.props.append(common.Property(name=const.SORT_ID, value=yaml_header[const.SORT_ID]))
        return control, group_title
