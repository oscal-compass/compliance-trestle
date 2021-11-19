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
from typing import Any, Dict, List, Optional, Tuple, Union

import frontmatter

import trestle.oscal.catalog as cat
import trestle.oscal.ssp as ossp
from trestle.core import const
from trestle.core import generators as gens
from trestle.core.err import TrestleError
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.markdown.md_writer import MDWriter
from trestle.core.utils import spaces_and_caps_to_snake
from trestle.oscal import common
from trestle.oscal import profile as prof

logger = logging.getLogger(__name__)


class ControlIOWriter():
    """Class write controls as markdown."""

    def __init__(self):
        """Initialize the class."""
        self._md_file: Optional[MDWriter] = None

    # Start of section to write controls to markdown

    @staticmethod
    def _wrap_label(label: str):
        l_side = '\['
        r_side = '\]'
        wrapped = '' if label == '' else f'{l_side}{label}{r_side}'
        return wrapped

    @staticmethod
    def _get_label(part: common.Part) -> str:
        """Get the label from the props of a part."""
        if part.props is not None:
            for prop in part.props:
                if prop.name == 'label':
                    return prop.value.strip()
        return ''

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
            label = part.id.split('.')[-1]
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

    def _add_control_statement(self, control: cat.Control, group_title: str) -> None:
        """Add the control statement and items to the md file."""
        self._md_file.new_paragraph()
        title = f'{control.id} - \[{group_title}\] {control.title}'
        self._md_file.new_header(level=1, title=title)
        self._md_file.new_header(level=2, title='Control Statement')
        self._md_file.set_indent_level(-1)
        self._add_part_and_its_items(control, 'statement', 'item')
        self._md_file.set_indent_level(-1)

    def _add_control_objective(self, control: cat.Control) -> None:
        if control.parts:
            for part in control.parts:
                if part.name == 'objective':
                    self._md_file.new_paragraph()
                    self._md_file.new_header(level=2, title='Control Objective')
                    self._md_file.set_indent_level(-1)
                    self._add_part_and_its_items(control, 'objective', 'objective')
                    self._md_file.set_indent_level(-1)
                    return

    @staticmethod
    def _get_control_section_part(part: common.Part, section: str) -> str:
        """Get the prose for a named section in the control."""
        prose = ''
        if part.name == section and part.prose is not None:
            prose = ControlIOWriter._gap_join(prose, part.prose)
        if part.parts:
            for sub_part in part.parts:
                prose = ControlIOWriter._gap_join(prose, ControlIOWriter._get_control_section_part(sub_part, section))
        return prose

    @staticmethod
    def _get_control_section(control: cat.Control, section: str) -> str:
        prose = ''
        if control.parts:
            for part in control.parts:
                prose = ControlIOWriter._gap_join(prose, ControlIOWriter._get_control_section_part(part, section))
        return prose

    @staticmethod
    def _find_section_info(part: common.Part, section_list: List[str]):
        """Find section not in list."""
        if part.prose and part.name not in section_list:
            return part.id, part.name
        if part.parts:
            for part in part.parts:
                id_, name = ControlIOWriter._find_section_info(part, section_list)
                if id_:
                    return id_, name
        return '', ''

    @staticmethod
    def _find_section(control: cat.Control, section_list: List[str]) -> Tuple[str, str]:
        """Find next section not in list."""
        if control.parts:
            for part in control.parts:
                id_, name = ControlIOWriter._find_section_info(part, section_list)
                if id_:
                    return id_, name
        return '', ''

    @staticmethod
    def _get_section(control: cat.Control, section_list: List[str]) -> Tuple[str, str, str]:
        """Get sections that are not in the list."""
        id_, name = ControlIOWriter._find_section(control, section_list)
        if id_:
            return id_, name, ControlIOWriter._get_control_section(control, name)
        return '', '', ''

    def _add_sections(self, control: cat.Control) -> None:
        """Add the extra control sections after the main ones."""
        skip_section_list = ['statement', 'item', 'objective']
        while True:
            name, id_, prose = self._get_section(control, skip_section_list)
            if not name:
                return
            if prose:
                skip_section_list.append(id_)
                if self._sections and id_ in self._sections:
                    id_ = self._sections[id_]
                self._md_file.new_header(level=2, title=f'Control {id_}')
                self._md_file.new_line(prose)
                self._md_file.new_paragraph()

    def _insert_existing_text(self, part_label: str, existing_text: Dict[str, List[str]]) -> None:
        """Insert text captured in the previous markdown and reinsert to avoid overwrite."""
        if part_label in existing_text:
            self._md_file.new_paragraph()
            for line in existing_text[part_label]:
                self._md_file.new_line(line)

    def _add_response(self, control: cat.Control, existing_text: Dict[str, List[str]]) -> None:
        """Add the response request text for all parts to the markdown along with the header."""
        self._md_file.new_hr()
        self._md_file.new_paragraph()
        self._md_file.new_header(level=2, title=f'{const.SSP_MD_IMPLEMENTATION_QUESTION}')

        # if the control has no parts written out then enter implementation in the top level entry
        # but if it does have parts written out, leave top level blank and provide details in the parts
        # Note that parts corresponding to sections don't get written out here so a check is needed
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
                                did_write_part = True
                            self._md_file.new_hr()
                            part_label = self._get_label(prt)
                            # if no label guess the label from the sub-part id
                            if not part_label:
                                part_label = prt.id.split('.')[-1]
                            self._md_file.new_header(level=2, title=f'Implementation {part_label}')
                            # don't write out the prompt for text if there is some already there
                            if part_label not in existing_text:
                                self._md_file.new_line(f'{const.SSP_ADD_IMPLEMENTATION_FOR_ITEM_TEXT} {prt.id}')
                            self._insert_existing_text(part_label, existing_text)
                            self._md_file.new_paragraph()
        if not did_write_part:
            self._md_file.new_line(f'{const.SSP_ADD_IMPLEMENTATION_FOR_CONTROL_TEXT} {control.id}')
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

    def _add_additional_content(self, control: cat.Control, profile: prof.Profile) -> None:
        adds = ControlIOWriter._get_adds(control.id, profile)
        has_content = len(adds) > 0

        self._md_file.new_header(level=1, title='Editable Content')
        self._md_file.new_line('<!-- Make additions and edits below -->')
        self._md_file.new_line(
            '<!-- The above represents the contents of the control as received by the profile, prior to additions. -->'  # noqa E501
        )
        self._md_file.new_line(
            '<!-- If the profile makes additions to the control, they will appear below. -->'  # noqa E501
        )
        self._md_file.new_line(
            '<!-- The above may not be edited but you may edit the content below, and/or introduce new additions to be made by the profile. -->'  # noqa E501
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

        for add in adds:
            name, prose = add
            self._md_file.new_header(level=2, title=f'Control {name}')
            self._md_file.new_paraline(prose)

    @staticmethod
    def get_part_prose(control: cat.Control, part_name: str) -> str:
        """Get the prose for a named part."""
        prose = ''
        if control.parts:
            for part in control.parts:
                prose += ControlIOWriter._get_control_section_part(part, part_name)
        return prose.strip()

    @staticmethod
    def merge_dicts_deep(dest: Dict[Any, Any], src: Dict[Any, Any]) -> None:
        """
        Merge dict src into dest in a deep manner and handle lists.

        All contents of dest are retained and new values from src do not change dest.
        But any new items in src are added to dest.
        This changes dest in place.
        """
        for key in src.keys():
            if key in dest:
                if isinstance(dest[key], dict) and isinstance(src[key], dict):
                    ControlIOWriter.merge_dicts_deep(dest[key], src[key])
                elif isinstance(dest[key], list):
                    # grow dest list for the key by adding new items from src
                    if isinstance(src[key], list):
                        try:
                            # Simple types (e.g. lists of strings) will get merged neatly
                            missing = set(src[key]) - set(dest[key])
                            dest[key].extend(missing)
                        except TypeError:
                            # This is a complex type - use simplistic safe behaviour
                            logger.debug('Ignoring complex types within lists when merging dictionaries.')
                    else:
                        if src[key] not in dest[key]:
                            dest[key].append(src[key])
                elif isinstance(src[key], list):
                    dest[key] = [dest[key]]
                    dest[key].extend(src[key])
                # if the item is in both, leave dest as-is and ignore the src value
            else:
                # if the item was not already in dest, add it from src
                dest[key] = src[key]

    def write_control(
        self,
        dest_path: pathlib.Path,
        control: cat.Control,
        group_title: str,
        yaml_header: Optional[Dict],
        sections: Optional[Dict[str, str]],
        additional_content: bool,
        prompt_responses: bool,
        profile: Optional[prof.Profile],
        header_dont_merge: bool
    ) -> None:
        """
        Write out the control in markdown format into the specified directory.

        Args:
            dest_path: Path to the directory where the control will be written
            control: The control to write as markdown
            group_title: Title of the group containing the control
            yaml_header: Optional dict to be written as markdown yaml header
            sections: Optional string lookup dict mapping section abbrev. to pretty version for display
            additional_content: Should the additional content be printed corresponding to profile adds
            prompt_responses: Should the markdown include prompts for implementation detail responses
            profile: Profile containing the adds making up additional content

        Returns:
            None

        Notes:
            The filename is constructed from the control's id, so only the markdown directory is required.
            If a yaml header is present in the file it is merged with the optional provided header.
            The header in the file takes precedence over the provided one.
        """
        control_file = dest_path / (control.id + '.md')
        existing_text, header = ControlIOReader.read_all_implementation_prose_and_header(control_file)
        self._md_file = MDWriter(control_file)
        self._sections = sections

        # Need to merge any existing header info with the new one.  Either could be empty.
        if header_dont_merge and not header == {}:
            merged_header = {}
        else:
            merged_header = copy.deepcopy(yaml_header) if yaml_header else {}
        if header:
            ControlIOWriter.merge_dicts_deep(merged_header, header)
        self._add_yaml_header(merged_header)

        self._add_control_statement(control, group_title)

        self._add_control_objective(control)

        self._add_sections(control)

        if prompt_responses:
            self._add_response(control, existing_text)

        if additional_content:
            self._add_additional_content(control, profile)

        self._md_file.write_out()


# Start of section to read controls from markdown


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
    def _trim_prose_lines(lines: List[str]) -> List[str]:
        """
        Trim empty lines at start and end of list of lines in prose.

        Also need to exclude the line requesting implementation prose
        """
        ii = 0
        n_lines = len(lines)
        while ii < n_lines and (lines[ii].strip(' \r\n') == ''
                                or lines[ii].find(const.SSP_ADD_IMPLEMENTATION_PREFIX) >= 0):
            ii += 1
        jj = n_lines - 1
        while jj >= 0 and lines[jj].strip(' \r\n') == '':
            jj -= 1
        if jj < ii:
            return ''
        return lines[ii:(jj + 1)]

    @staticmethod
    def _read_label_prose(ii: int, lines: List[str]) -> Tuple[int, str, List[str]]:
        r"""
        Return the found label and its corresponding list of prose lines.

        ii should point to start of file or directly at a new Part or control
        This looks for two types of reference lines:
        _______\n## Control label
        _______\n# label
        If a section is meant to be left blank it goes ahead and reads the comment text
        """
        nlines = len(lines)
        prose_lines: List[str] = []
        item_label = ''
        tld_prose_lines = []
        if ii == 0:
            # read the entire control to validate contents
            ii, _ = ControlIOReader._read_control_statement(0, lines, 'dummy_id')
            ii, _ = ControlIOReader._read_sections(ii, lines, 'xx', [])
            # go back to beginning and seek the implementation question
            ii = 0
            while ii < nlines and not lines[ii].strip().endswith(const.SSP_MD_IMPLEMENTATION_QUESTION):
                ii += 1
            # skip over the question
            ii += 1
        while -1 < ii < nlines:
            # start of new part
            if lines[ii].startswith('## Implementation'):
                split = lines[ii].strip().split()
                if len(split) < 3:
                    raise TrestleError('Implementation line must include label')
                item_label = split[-1]
                ii += 1
                if ii < nlines and lines[ii] and ControlIOReader._indent(lines[ii]) <= 0:
                    msg = f'Implementation line for control appears broken by newline: {lines[ii]}'
                    raise TrestleError(msg)
                # collect until next hrule
                while ii < nlines:
                    if lines[ii].startswith(const.SSP_MD_HRULE_LINE) or lines[ii].startswith('## Implementation'):
                        return ii, item_label, ControlIOReader._trim_prose_lines(prose_lines)
                    prose_lines.append(lines[ii].strip())
                    ii += 1
            elif lines[ii].startswith('# ') or lines[ii].startswith('## '):
                raise TrestleError(f'Improper heading level in control statement: {lines[ii]}')
            else:
                tld_prose = lines[ii].strip()
                if tld_prose and not tld_prose.startswith(const.SSP_ADD_IMPLEMENTATION_PREFIX):
                    tld_prose_lines.append(tld_prose)
            ii += 1
        # if we did not find normal labelled prose regard any found prose as top_level_description
        if not item_label and tld_prose_lines:
            return nlines, 'top_level_description', tld_prose_lines
        return -1, item_label, prose_lines

    @staticmethod
    def _load_control_lines(control_file: pathlib.Path) -> List[str]:
        lines: List[str] = []
        try:
            content = control_file.open('r', encoding=const.FILE_ENCODING).read()
        except UnicodeDecodeError as e:
            logger.error('utf-8 decoding failed.')
            logger.error(f'See: {const.WEBSITE_ROOT}/errors/#utf-8-encoding-only')
            logger.debug(f'Underlying exception {e}')
            raise TrestleError('Unable to load file due to utf-8 encoding issues.')
        try:
            fm = frontmatter.loads(content)
        except Exception as e:
            logger.error(f'Error parsing yaml header from file {control_file}')
            logger.error('This is most likely due to an incorrect yaml structure.')
            logger.debug(f'Underlying error: {str(e)}')
            raise TrestleError(f'Failure parsing yaml header on file {control_file}')
        raw_lines = fm.content.split('\n')
        # Any fully blank lines will be retained but as empty strings
        lines = [line.strip('\r\n').rstrip() for line in raw_lines]
        clean_lines = []
        # need to keep indentation and empty lines
        for line in lines:
            if line.startswith('<!--') or line.startswith('__________________'):
                continue
            clean_lines.append(line)
        return clean_lines

    @staticmethod
    def _read_id_group_id_title(line: str) -> Tuple[int, str, str]:
        """Process the line and find the control id, group id and control title."""
        if line.count('-') < 2:
            raise TrestleError(f'Markdown control title format error: {line}')
        control_id = line.split()[1]
        first_dash = line.find('-')
        title_line = line[first_dash + 1:]
        group_start = title_line.find('\[')
        group_end = title_line.find('\]')
        if group_start < 0 or group_end < 0 or group_start > group_end:
            raise TrestleError(f'unable to read group and title for control {control_id}')
        group_id = title_line[group_start + 2:group_end].strip()
        control_title = title_line[group_end + 2:].strip()
        return control_id, group_id, control_title

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
                    while start < len(line) and line[start] != ' ':
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
                    prev_label = ControlIOWriter._get_label(parts[-1]) if parts else ''
                    id_text = ControlIOReader._create_next_label(prev_label, indent)
                id_ = ControlIOReader._strip_to_make_ncname(parent_id + '.' + id_text)
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
                       control_parts: List[common.Part]) -> Tuple[int, List[common.Part]]:
        """Read all sections following the section separated by ## Control."""
        new_parts = []
        prefix = '## Control '
        while 0 <= ii < len(lines):
            line = lines[ii]
            if line.startswith('## What is the solution') or line.startswith('# Editable Content'):
                ii += 1
                continue
            if not line:
                ii += 1
                continue
            if line and not line.startswith(prefix):
                # the control has no sections to read, so exit the loop
                break
            label = line[len(prefix):].lstrip()
            prose = ''
            ii += 1
            while 0 <= ii < len(lines) and not lines[ii].startswith(prefix) and not lines[ii].startswith(
                    '# Editable Content'):
                prose = '\n'.join([prose, lines[ii]])
                ii += 1
            if prose:
                id_ = ControlIOReader._strip_to_make_ncname(control_id + '_smt.' + label)
                label = ControlIOReader._strip_to_make_ncname(label)
                new_parts.append(common.Part(id=id_, name=label, prose=prose.strip('\n')))
        if new_parts:
            if control_parts:
                control_parts.extend(new_parts)
            else:
                control_parts = new_parts
        if not control_parts:
            control_parts = None
        return ii, control_parts

    @staticmethod
    def read_all_implementation_prose_and_header(
        control_file: pathlib.Path
    ) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
        """
        Find all labels and associated prose in this control.

        Args:
            control_file: path to the control markdown file

        Returns:
            Dictionary of part labels and corresponding prose read from the markdown file.
        """
        try:
            if not control_file.exists():
                return {}, {}
            md_api = MarkdownAPI()
            header, _ = md_api.processor.process_markdown(control_file)

            lines = ControlIOReader._load_control_lines(control_file)
            ii = 0
            # keep moving down through the file picking up labels and prose
            responses: Dict[str, List[str]] = {}
            while True:
                ii, part_label, prose_lines = ControlIOReader._read_label_prose(ii, lines)
                while prose_lines and not prose_lines[0].strip(' \r\n'):
                    del prose_lines[0]
                while prose_lines and not prose_lines[-1].strip(' \r\n'):
                    del prose_lines[-1]
                if part_label and prose_lines:
                    responses[part_label] = prose_lines
                if ii < 0:
                    break
        except TrestleError as e:
            logger.error(f'Error occurred reading {control_file}')
            raise e
        return responses, header

    @staticmethod
    def read_implementations(control_file: pathlib.Path,
                             component: ossp.SystemComponent) -> List[ossp.ImplementedRequirement]:
        """Get implementation requirements associated with given control and link to the one component we created."""
        control_id = control_file.stem
        imp_reqs: List[ossp.ImplementedRequirement] = []
        responses, _ = ControlIOReader.read_all_implementation_prose_and_header(control_file)

        for response in responses.items():
            label = response[0]
            prose_lines = response[1]
            # create a new by-component to hold this statement
            by_comp: ossp.ByComponent = gens.generate_sample_model(ossp.ByComponent)
            # link it to the one dummy component uuid
            by_comp.component_uuid = component.uuid
            # add the response prose to the description
            by_comp.description = '\n'.join(prose_lines)
            # create a statement to hold the by-component and assign the statement id
            statement: ossp.Statement = gens.generate_sample_model(ossp.Statement)
            statement.statement_id = ControlIOReader._strip_to_make_ncname(f'{control_id}_smt.{label}')
            statement.by_components = [by_comp]
            # create a new implemented requirement linked to the control id to hold the statement
            imp_req: ossp.ImplementedRequirement = gens.generate_sample_model(ossp.ImplementedRequirement)
            imp_req.control_id = control_id
            imp_req.statements = [statement]
            imp_reqs.append(imp_req)
        return imp_reqs

    @staticmethod
    def _read_added_part(ii: int, lines: List[str], control_id: str) -> Tuple[int, Optional[common.Part]]:
        """Read a single part indicated by ## Control foo."""
        while 0 <= ii < len(lines):
            # look for ## Control foo - then read prose
            line = lines[ii]
            prefix = '## Control '
            if line:
                if not line.startswith(prefix):
                    raise TrestleError(f'Unexpected line in Editable Content for control {control_id}: {line}')
                part_name_raw = line[len(prefix):]
                part_name = spaces_and_caps_to_snake(part_name_raw)
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
                    id_ = f'{control_id}_{part_name}'
                    part = common.Part(id=id_, name=part_name, prose=prose)
                    return ii, part
            ii += 1
        return -1, None

    @staticmethod
    def read_new_alters(control_path: pathlib.Path) -> List[prof.Alter]:
        """Get parts for the markdown control corresponding to Editable Content - if any."""
        control_id = control_path.stem
        new_alters: List[prof.Alter] = []
        lines = ControlIOReader._load_control_lines(control_path)
        ii = 0
        while 0 <= ii < len(lines):
            line = lines[ii]
            if line.startswith('# Editable Content'):
                ii += 1
                while 0 <= ii < len(lines):
                    ii, part = ControlIOReader._read_added_part(ii, lines, control_id)
                    if ii < 0:
                        break
                    alter = prof.Alter(
                        control_id=control_id,
                        adds=[prof.Add(parts=[part], position='after', by_id=f'{control_id}_smt')]
                    )
                    new_alters.append(alter)
            else:
                ii += 1
        return new_alters

    @staticmethod
    def read_control(control_path: pathlib.Path) -> cat.Control:
        """Read the control markdown file."""
        control = gens.generate_sample_model(cat.Control)
        md_api = MarkdownAPI()
        _, control_tree = md_api.processor.process_markdown(control_path)
        control_titles = list(control_tree.get_all_headers_for_level(1))
        if len(control_titles) == 0:
            raise TrestleError(f'Control markdown: {control_path} contains no control title.')

        control.id, _, control.title = ControlIOReader._read_id_group_id_title(control_titles[0])

        control_headers = list(control_tree.get_all_headers_for_level(2))
        if len(control_headers) == 0:
            raise TrestleError(f'Control markdown: {control_path} contains no control statements.')

        control_statement = control_tree.get_node_for_key(control_headers[0])
        rc, statement_part = ControlIOReader._read_control_statement(
            0, control_statement.content.raw_text.split('\n'), control.id
        )
        if rc < 0:
            return control
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
        return control
