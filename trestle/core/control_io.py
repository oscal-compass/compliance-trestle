# Copyright (c) 2021 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Handle direct i/o reading and writing controls as markdown."""

import logging
import pathlib
import string
from typing import Dict, List, Optional, Tuple, Union

import trestle.oscal.catalog as cat
import trestle.oscal.ssp as ossp
from trestle.core import const
from trestle.core import generators as gens
from trestle.core.err import TrestleError
from trestle.oscal import common
from trestle.utils.md_writer import MDWriter

logger = logging.getLogger(__name__)


class ControlIo():
    """Class to read and write controls as markdown."""

    def __init__(self):
        """Initialize the class."""
        self._md_file: Optional[MDWriter] = None

    def _wrap_label(self, label: str):
        l_side = '\['
        r_side = '\]'
        wrapped = '' if label == '' else f'{l_side}{label}{r_side}'
        return wrapped

    def _get_label(self, part: common.Part) -> str:
        # get the label from the props of a part
        if part.props is not None:
            for prop in part.props:
                if prop.name == 'label':
                    return prop.value.strip()
        return ''

    def _get_part(self, control: cat.Control, part: common.Part) -> List[Union[str, List[str]]]:
        """
        Find parts in control that require implementations.

        For a part in a control find the parts in it that require implementations
        Return list of string formatted labels and associated descriptive prose
        """
        items = []
        if part.name in ['item', 'statement']:
            # the options here are to force the label to be the part.id or the part.label
            # the label may be of the form (a) while the part.id is ac-1_smt.a.1.a
            # here we choose the latter and extract the final element
            label = part.id.split('.')[-1]
            wrapped_label = self._wrap_label(label)
            pad = '' if wrapped_label == '' or part.prose is None else ' '
            prose = '' if part.prose is None else part.prose
            # statement prose has already been written out, if present
            if part.name != 'statement':
                items.append(f'{wrapped_label}{pad}{prose}')
            if part.parts:
                sub_list = []
                for prt in part.parts:
                    sub_list.extend(self._get_part(control, prt))
                sub_list.append('')
                items.append(sub_list)
        return items

    def _add_parts(self, control: cat.Control) -> None:
        """For a given control add its parts to the md file after replacing params."""
        items = []
        if control.parts:
            for part in control.parts:
                if part.name == 'statement':
                    # If the statement has prose write it as a raw line and not list element
                    if part.prose:
                        self._md_file.new_line(part.prose)
                    items.append(self._get_part(control, part))
            # unwrap the list if it is many levels deep
            while not isinstance(items, str) and len(items) == 1:
                items = items[0]
            self._md_file.new_paragraph()
            self._md_file.new_list(items)

    def _add_yaml_header(self, yaml_header: Optional[dict]) -> None:
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
        title = f'{control.id} - [{group_title}] {control.title}'
        self._md_file.new_header(level=1, title=title)
        self._md_file.new_header(level=2, title='Control Statement')
        self._md_file.set_indent_level(-1)
        self._add_parts(control)
        self._md_file.set_indent_level(-1)

    def _get_control_section_part(self, part: common.Part, section: str) -> str:
        """Get the prose for a named section in the control."""
        prose = ''
        if part.name == section and part.prose is not None:
            prose = self._gap_join(prose, part.prose)
        if part.parts:
            for sub_part in part.parts:
                prose = self._gap_join(prose, self._get_control_section_part(sub_part, section))
        return prose

    def _get_control_section(self, control: cat.Control, section: str) -> str:
        prose = ''
        if control.parts:
            for part in control.parts:
                prose = self._gap_join(prose, self._get_control_section_part(part, section))
        return prose

    def _find_section_info(self, part: common.Part, section_list: List[str]):
        """Find section not in list."""
        if part.prose and part.name not in section_list:
            return part.id, part.name
        if part.parts:
            for part in part.parts:
                id_, name = self._find_section_info(part, section_list)
                if id_:
                    return id_, name
        return '', ''

    def _find_section(self, control: cat.Control, section_list: List[str]) -> Tuple[str, str]:
        """Find next section not in list."""
        if control.parts:
            for part in control.parts:
                id_, name = self._find_section_info(part, section_list)
                if id_:
                    return id_, name
        return '', ''

    def _get_section(self, control: cat.Control, section_list: List[str]) -> Tuple[str, str, str]:
        """Get sections that are not in the list."""
        id_, name = self._find_section(control, section_list)
        if id_:
            return id_, name, self._get_control_section(control, name)
        return '', '', ''

    def _add_sections(self, control: cat.Control) -> None:
        """Add the control sections, e.g. guidance."""
        section_list = ['statement', 'item']
        while True:
            name, id_, prose = self._get_section(control, section_list)
            if not name:
                return
            if prose:
                section_list.append(id_)
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
                                did_write_part = True
                            self._md_file.new_hr()
                            part_label = self._get_label(prt)
                            self._md_file.new_header(level=2, title=f'Implementation {part_label}')
                            self._md_file.new_line(f'{const.SSP_ADD_IMPLEMENTATION_FOR_ITEM_TEXT} {prt.id}')
                            self._insert_existing_text(part_label, existing_text)
                            self._md_file.new_paragraph()
        if not did_write_part:
            self._md_file.new_line(f'{const.SSP_ADD_IMPLEMENTATION_FOR_CONTROL_TEXT} {control.id}')
        self._md_file.new_hr()

    def _add_additional_content(self) -> None:
        self._md_file.new_header(level=1, title='Additional Content')
        self._md_file.new_line('<!-- Provide additional content here -->')
        self._md_file.new_line(
            "<!-- Add content here. Each heading of '##' is intepreted as a part of the control. -->"
        )
        self._md_file.new_line(
            '<!-- For the title to be valid it MUST follow the structure of ## Control [part type] -->'
        )
        self._md_file.new_line('<!-- See https://ibm.github.io/compliance-trestle/page.html for suggested types. -->')

    @staticmethod
    def _strip_bad_chars(label: str) -> str:
        """
        Remove chars that would cause statement_id regex to fail.

        Actual value can't start with digit, ., or -
        """
        allowed_chars = string.ascii_letters + string.digits + '-._'
        new_label = ''
        for c in label:
            if c in allowed_chars:
                new_label += c
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
        _______\n## Part label
        _______\n# label
        If a section is meant to be left blank it goes ahead and reads the comment text
        """
        nlines = len(lines)
        prose_lines: List[str] = []
        item_label = ''
        while ii < nlines:
            # start of new part
            if lines[ii].startswith('## Implementation'):
                item_label = lines[ii].strip().split(' ')[-1]
                ii += 1
                # collect until next hrule
                while ii < nlines:
                    if lines[ii].startswith(const.SSP_MD_HRULE_LINE) or lines[ii].startswith('## Implementation'):
                        return ii, item_label, ControlIo._trim_prose_lines(prose_lines)
                    prose_lines.append(lines[ii].strip())
                    ii += 1
            elif lines[ii].startswith('# ') and lines[ii].strip().endswith(const.SSP_MD_IMPLEMENTATION_QUESTION):
                item_label = lines[ii].strip().split(' ')[1]
                ii += 1
                while ii < nlines:
                    if lines[ii].startswith(const.SSP_MD_HRULE_LINE):
                        return ii, item_label, ControlIo._trim_prose_lines(prose_lines)
                    prose_lines.append(lines[ii].strip())
                    ii += 1
            ii += 1
        return -1, item_label, prose_lines

    @staticmethod
    def _load_control_lines(control_file: pathlib.Path) -> List[str]:
        lines: List[str] = []
        with control_file.open('r', encoding=const.FILE_ENCODING) as f:
            raw_lines = f.readlines()
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
    def read_all_implementation_prose(control_file: pathlib.Path) -> Dict[str, List[str]]:
        """
        Find all labels and associated prose in this control.

        Args:
            control_file: path to the control markdown file

        Returns:
            Dictionary of part labels and corresponding prose read from the markdown file.
        """
        if not control_file.exists():
            return {}
        lines = ControlIo._load_control_lines(control_file)
        ii = 0
        # keep moving down through the file picking up labels and prose
        responses: Dict[str, List[str]] = {}
        while True:
            ii, part_label, prose_lines = ControlIo._read_label_prose(ii, lines)
            if ii < 0:
                break
            clean_label = ControlIo._strip_bad_chars(part_label)
            responses[clean_label] = prose_lines
        return responses

    def read_implementations(self, control_file: pathlib.Path,
                             component: ossp.SystemComponent) -> List[ossp.ImplementedRequirement]:
        """Get implementation requirements associated with given control and link to the one component we created."""
        control_id = control_file.stem
        imp_reqs: list[ossp.ImplementedRequirement] = []
        responses = self.read_all_implementation_prose(control_file)

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
            statement.statement_id = f'{control_id}_smt.{label}'
            statement.by_components = [by_comp]
            # create a new implemented requirement linked to the control id to hold the statement
            imp_req: ossp.ImplementedRequirement = gens.generate_sample_model(ossp.ImplementedRequirement)
            imp_req.control_id = control_id
            imp_req.statements = [statement]
            imp_reqs.append(imp_req)
        return imp_reqs

    @staticmethod
    def _read_id_title(ii: int, lines: List[str], control: cat.Control) -> Tuple[int, str]:
        while ii < len(lines):
            line = lines[ii]
            ii += 1
            if line.startswith('# '):
                if line.count('-') < 2:
                    raise TrestleError(f'Markdown control title format error: {line}')
                control.id = line.split()[1]
                first_dash = line.find('-')
                title_line = line[first_dash + 1:]
                group_start = title_line.find('[')
                group_end = title_line.find(']')
                if group_start < 0 or group_end < 0 or group_start > group_end:
                    raise TrestleError(f'unable to read group and title for control {control.id}')
                group_id = title_line[group_start + 1:group_end].strip()
                control.title = title_line[group_end + 1:].strip()
                return ii, group_id
        raise TrestleError('Unable to find #Control: heading in control markdown file.')

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
                indent = ControlIo._indent(line)
                if indent >= 0:
                    # extract text after -
                    start = indent + 1
                    while start < len(line) and line[start] != ' ':
                        start += 1
                    if start >= len(line):
                        raise TrestleError(f'Invalid line {line}')
                    return ii, indent, line[start:]
                else:
                    return ii, indent, line
            else:
                ii += 1
        return ii, -1, ''

    @staticmethod
    def _read_part_id_prose(line: str) -> Tuple[str, str]:
        """Extract the part id letter or number and prose from line."""
        start = line.find('\\[')
        end = line.find('\\]')
        if start < 0 or end < 0:
            raise TrestleError(f'Control items must have label surrounded by \\[ \\]: {line}')
        prose = line[end + 2:].strip()
        id_ = ControlIo._strip_bad_chars(line[start + 2:end])
        id_ = id_.replace('.', '')
        return id_, prose

    @staticmethod
    def _read_parts(indent: int, ii: int, lines: List[str], parent_id: str,
                    parts: List[common.Part]) -> Tuple[int, List[common.Part]]:
        """If indentation level goes up or down, create new list or close current one."""
        while True:
            ii, new_indent, line = ControlIo._get_next_indent(ii, lines)
            if new_indent < 0:
                # we are done reading control statement
                return ii, parts
            if new_indent == indent:
                # create new item part and add to current list of parts
                id_text, prose = ControlIo._read_part_id_prose(line)
                id_ = parent_id + '.' + id_text
                part = common.Part(name='item', id=id_, prose=prose)
                parts.append(part)
                ii += 1
            elif new_indent > indent:
                # add new list of parts to last part and continue
                if len(parts) == 0:
                    raise TrestleError(f'Improper indentation structure: {line}')
                ii, new_parts = ControlIo._read_parts(new_indent, ii, lines, parts[-1].id, [])
                if new_parts:
                    parts[-1].parts = new_parts
            else:
                # return list of sub-parts
                return ii, parts

    @staticmethod
    def _read_control_statement(ii: int, lines: List[str], control: cat.Control) -> int:
        """Search for the Control statement and read until next ## Control."""
        while 0 <= ii < len(lines) and not lines[ii].startswith('## Control '):
            ii += 1
        if not lines[ii].startswith('## Control'):
            raise TrestleError(f'Control statement not found for {control.id}')
        ii += 1

        ii, line = ControlIo._get_next_line(ii, lines)
        if ii < 0:
            # This means no statement and control withdrawn (this happens in NIST catalog)
            return ii
        if line and line[0] == ' ' and line.lstrip()[0] != '-':
            # prose that appears indented but has no - : treat it as the normal statement prose
            line = line.lstrip()
            indent = -1
            ii += 1
        else:
            ii, indent, line = ControlIo._get_next_indent(ii, lines)

        statement_part = common.Part(name='statement', id=f'{control.id}_smt')
        # first line is either statement prose or start of statement parts
        if indent < 0:
            statement_part.prose = line
            ii += 1
        # we have absorbed possible statement prose.
        # now just read parts recursively
        # if there was no statement prose, this will re-read the line just read
        # as the start of the statement's parts
        ii, parts = ControlIo._read_parts(0, ii, lines, statement_part.id, [])
        statement_part.parts = parts if parts else None
        control.parts = [statement_part]
        return ii

    @staticmethod
    def _read_sections(ii: int, lines: List[str], control: cat.Control) -> None:
        """Read all sections following the section separated by ## Control."""
        new_parts = []
        prefix = '## Control '
        while 0 <= ii < len(lines):
            line = lines[ii]
            if line.startswith('## What is the solution') or line.startswith('# Additional Content'):
                ii += 1
                continue
            if line and not line.startswith(prefix):
                raise TrestleError(f'Error parsing section for control {control.id}: {line}')
            label = line[len(prefix):].lstrip()
            prose = ''
            ii += 1
            while 0 <= ii < len(lines) and not lines[ii].startswith(prefix) and not lines[ii].startswith(
                    '# Additional Content'):
                prose = '\n'.join([prose, lines[ii]])
                ii += 1
            if prose:
                id_ = control.id + '_smt.' + label
                new_parts.append(common.Part(id=id_, name=label, prose=prose.strip('\n')))
        if new_parts:
            if control.parts:
                control.parts.extend(new_parts)
            else:
                control.parts = new_parts
        if not control.parts:
            control.parts = None
        return ii, lines, control

    def read_control(self, control_path: pathlib.Path) -> Tuple[cat.Control]:
        """Read the control markdown file."""
        control = gens.generate_sample_model(cat.Control)
        lines = ControlIo._load_control_lines(control_path)
        ii, _ = ControlIo._read_id_title(0, lines, control)
        ii = ControlIo._read_control_statement(ii, lines, control)
        ii = ControlIo._read_sections(ii, lines, control)
        return control

    def write_control(
        self,
        dest_path: pathlib.Path,
        control: cat.Control,
        group_title: str,
        yaml_header: Optional[dict],
        sections: Optional[Dict[str, str]],
        additional_content: bool,
        prompt_responses: bool
    ) -> None:
        """Write out the control in markdown format."""
        control_file = dest_path / (control.id + '.md')
        existing_text = self.read_all_implementation_prose(control_file)
        self._md_file = MDWriter(control_file)
        self._sections = sections

        self._add_yaml_header(yaml_header)

        self._add_control_statement(control, group_title)

        self._add_sections(control)

        if prompt_responses:
            self._add_response(control, existing_text)

        if additional_content:
            self._add_additional_content()

        self._md_file.write_out()
