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

    header_tokens = ['Control', 'class', 'Param', 'Prop', 'link', 'Part', 'Controls']
    label_tokens = [
        'id',
        'ns',
        'class',
        'remarks',
        'depends_on',
        'label',
        'usage',
        'constraints',
        'guidelines',
        'values',
        'select',
        'choice',
        'remarks',
        'prose',
        'link'
    ]

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
        return list of string formatted labels and associated descriptive prose
        """
        items = []
        # parts that are sections are output separately
        if part.name not in self._sections:
            if part.prose is not None:
                label = self._get_label(part)
                wrapped_label = self._wrap_label(label)
                pad = '' if wrapped_label == '' else ' '
                items.append(f'{wrapped_label}{pad}{part.prose}')
            if part.parts is not None:
                sub_list = []
                for prt in part.parts:
                    sub_list.extend(self._get_part(control, prt))
                sub_list.append('')
                items.append(sub_list)
        return items

    def _add_parts(self, control: cat.Control) -> None:
        """For a given control add its parts to the md file after replacing params."""
        items = []
        if control.parts is not None:
            for part in control.parts:
                if part.name == 'statement':
                    items.append(self._get_part(control, part))
            # unwrap the list if it is many levels deep
            while not isinstance(items, str) and len(items) == 1:
                items = items[0]
            self._md_file.new_paragraph()
            self._md_file.new_list(items)

    def _add_yaml_header(self, yaml_header: Optional[dict]) -> None:
        if yaml_header:
            self._md_file.add_yaml_header(yaml_header)

    def _add_control_description(self, control: cat.Control, group_title: str) -> None:
        """Add the control description and parts to the md file."""
        self._md_file.new_paragraph()
        title = f'{control.id} - {group_title} {control.title}'
        self._md_file.new_header(level=1, title=title)
        self._md_file.new_header(level=2, title='Control Description')
        self._md_file.set_indent_level(-1)
        self._add_parts(control)
        self._md_file.set_indent_level(-1)

    def _get_control_section_part(self, part: common.Part, section: str) -> str:
        """Get the prose for a section in the control."""
        prose = ''
        if part.name == section and part.prose is not None:
            prose += part.prose
        if part.parts is not None and part.parts:
            for sub_part in part.parts:
                prose += self._get_control_section_part(sub_part, section)
        return prose

    def _get_control_section(self, control: cat.Control, section: str) -> str:
        """
        Find section text first in the control and then in the profile.

        If found in both they are appended
        """
        prose = ''
        for part in control.parts:
            prose += self._get_control_section_part(part, section)
        return prose

    def _add_control_section(self, control: cat.Control, section_tuple: str) -> None:
        """Add the control section to the md file."""
        prose = self._get_control_section(control, section_tuple[0])
        if prose:
            self._md_file.new_header(level=1, title=f'{control.id} section: {section_tuple[1]}')
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
        self._md_file.new_header(level=2, title=f'{control.id} {const.SSP_MD_IMPLEMENTATION_QUESTION}')

        # if the control has no parts written out then enter implementation in the top level entry
        # but if it does have parts written out, leave top level blank and provide details in the parts
        # Note that parts corresponding to sections don't get written out here so a check is needed
        did_write_part = False
        if control.parts:
            for part in control.parts:
                if part.parts:
                    if part.name == 'statement':
                        for prt in part.parts:
                            # parts that are sections are output separately
                            if prt.name in self._sections:
                                continue
                            if not did_write_part:
                                self._md_file.new_line(const.SSP_MD_LEAVE_BLANK_TEXT)
                                did_write_part = True
                            self._md_file.new_hr()
                            part_label = self._get_label(prt)
                            self._md_file.new_header(level=2, title=f'Part {part_label}')
                            self._md_file.new_line(f'{const.SSP_ADD_IMPLEMENTATION_FOR_STATEMENT_TEXT} {prt.id}')
                            self._insert_existing_text(part_label, existing_text)
                            self._md_file.new_paragraph()
        if not did_write_part:
            self._md_file.new_line(f'{const.SSP_ADD_IMPLEMENTATION_FOR_CONTROL_TEXT} {control.id}')
        self._md_file.new_hr()

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
    def _get_label_prose(ii: int, lines: List[str]) -> Tuple[int, str, List[str]]:
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
            if lines[ii].startswith('## Part'):
                item_label = lines[ii].strip().split(' ')[-1]
                ii += 1
                # collect until next hrule
                while ii < nlines:
                    if lines[ii].startswith(const.SSP_MD_HRULE_LINE):
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
    def get_all_implementation_prose(control_file: pathlib.Path) -> Dict[str, List[str]]:
        """
        Find all labels and associated prose in this control.

        Args:
            control_file: path to the control markdown file

        Returns:
            Dictionary of part labels and corresponding prose read from the markdown file.
        """
        if not control_file.exists():
            return {}
        ii = 0
        lines: List[str] = []
        with control_file.open('r') as f:
            raw_lines = f.readlines()
        lines = [line.strip('\r\n') for line in raw_lines]

        # keep moving down through the file picking up labels and prose
        responses: Dict[str, List[str]] = {}
        while True:
            ii, part_label, prose_lines = ControlIo._get_label_prose(ii, lines)
            if ii < 0:
                break
            clean_label = ControlIo._strip_bad_chars(part_label)
            responses[clean_label] = prose_lines
        return responses

    def get_implementations(self, control_file: pathlib.Path,
                            component: ossp.SystemComponent) -> List[ossp.ImplementedRequirement]:
        """Get implementation requirements associated with given control and link to the one component we created."""
        control_id = control_file.stem
        imp_reqs: list[ossp.ImplementedRequirement] = []
        responses = self.get_all_implementation_prose(control_file)

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

    def write_control(
        self,
        dest_path: pathlib.Path,
        control: cat.Control,
        group_title: str,
        yaml_header: Optional[dict],
        sections: Optional[Dict[str, str]]
    ) -> None:
        """Write out the control in markdown format."""
        control_file = dest_path / (control.id + '.md')
        existing_text = self.get_all_implementation_prose(control_file)
        self._md_file = MDWriter(control_file)
        self._sections = sections

        self._add_yaml_header(yaml_header)

        self._add_control_description(control, group_title)

        if self._sections is not None:
            for section_tuple in self._sections.items():
                self._add_control_section(control, section_tuple)

        self._add_response(control, existing_text)

        self._md_file.write_out()

    # Below deals with writing out full control details

    def _write_part_full(self, part: common.Part, level: int) -> None:
        title = f'Part: {part.name}'
        self._md_file.new_header(level=level, title=title)
        self._md_file.new_paragraph()
        if part.id:
            self._md_file.new_paraline(f'id: {part.id}')
        if part.ns:
            self._md_file.new_paraline(f'ns: {part.ns}')
        if part.class_:
            self._md_file.new_paraline(f'class: {part.class_}')
        if part.title:
            self._md_file.new_paraline(f'title: {part.title}')
        if part.prose:
            self._md_file.new_paraline('prose:')
            self._md_file.new_line(part.prose)
        if part.props:
            for prop in part.props:
                self._write_prop(prop, level + 1)
        if part.parts:
            for sub_part in part.parts:
                self._write_part_full(sub_part, level + 1)
        if part.links:
            for link in part.links:
                self._write_link(link)

    def _write_part_prose(self, part: common.Part, level: int) -> None:
        if part.prose:
            heading = '#' * level
            self._md_file.new_paraline(f'{heading} Prose:')
            self._md_file.new_paraline(part.prose)
        if part.parts:
            for sub_part in part.parts:
                self._write_part_prose(sub_part, level + 1)

    def _write_parts_prose(self, control: cat.Control) -> None:
        if control.parts:
            for part in control.parts:
                self._write_part_prose(part, 2)

    def _write_parts_full(self, control: cat.Control) -> None:
        if control.parts:
            for part in control.parts:
                self._write_part_full(part, 2)

    def _write_link(self, link: common.Link) -> None:
        self._md_file.new_line(f'link: {link.href}')
        if link.rel:
            self._md_file.new_paraline(f'rel: {link.rel}')
        if link.media_type:
            self._md_file.new_paraline(f'media_type: {link.media_type}')
        if link.text:
            self._md_file.new_paraline(f'text: {link.text}')

    def _write_constraint(self, constraint: common.ParameterConstraint) -> None:
        self._md_file.new_paraline('constraint:')
        if constraint.description:
            self._md_file.new_paraline(f'description: {constraint.description}')
        if constraint.tests:
            for test in constraint.tests:
                self._md_file.new_paraline(f'test: {test.expression}')
                if test.remarks:
                    self._md_file.new_paraline(f'remarks: {test.remarks.__root__}')

    def _write_guideline(self, guideline: common.ParameterGuideline) -> None:
        self._md_file.new_paraline(f'guideline: {guideline.prose}')

    def _write_param(self, param: common.Parameter, level: int) -> None:
        self._md_file.new_paragraph()
        title = f'Param: {param.id}'
        self._md_file.new_header(level, title)
        if param.class_:
            self._md_file.new_paraline(f'class: {param.class_}')
        if param.depends_on:
            self._md_file.new_paraline(f'depends_on: {param.depends_on}')
        if param.props:
            for prop in param.props:
                self._write_prop(prop, level + 1)
        if param.links:
            for link in param.links:
                self._write_link(link, level + 1)
        if param.label:
            self._md_file.new_line(f'label: {param.label}')
        if param.usage:
            self._md_file.new_paraline(f'usage: {param.usage}')
        if param.constraints:
            self._md_file.new_paraline('constraints:')
            for constraint in param.constraints:
                self._write_constraint(constraint)
        if param.guidelines:
            self._md_file.new_line('guidelines:')
            for guideline in param.guidelines:
                self._write_guideline(guideline)
        if param.values:
            self._md_file.new_paraline('values:')
            for value in param.values:
                self._md_file.new_paraline(value.__root__)
        if param.select:
            if param.select.how_many:
                how_many_text = param.select.how_many.name
                self._md_file.new_paraline(f'select: {how_many_text}')
            if param.select.choice:
                self._md_file.new_paraline('choice:')
                for choice in param.select.choice:
                    self._md_file.new_paraline(choice)
        if param.remarks:
            self._md_file.new_paraline(f'remarks: {param.remarks.__root__}')

    def _write_params_full(self, control: cat.Control) -> None:
        if control.params:
            for param in control.params:
                self._write_param(param, 2)

    def _write_prop(self, prop: common.Property, level: int) -> None:
        self._md_file.new_paragraph()
        title = f'Prop: {prop.name} - {prop.value}'
        self._md_file.new_header(level, title)
        if prop.uuid:
            self._md_file.new_header(level + 1, f'uuid: {prop.uuid}')
        if prop.ns:
            self._md_file.new_header(level + 1, f'ns: {prop.ns}')
        if prop.class_:
            self._md_file.new_header(level + 1, f'class: {prop.class_}')
        if prop.remarks:
            self._md_file.new_header(level + 1, f'remarks: {prop.remarks.__root__}')

    def _write_props_full(self, control: cat.Control) -> None:
        if control.props:
            for prop in control.props:
                self._write_prop(prop, 2)

    def _write_links_full(self, control: cat.Control) -> None:
        if control.links:
            for link in control.links:
                self._md_file.new_paragraph()
                title = f'link: {link.href} {link.rel}'
                self._md_file.new_header(2, title)

    def _get_control_list(self, control: cat.Control) -> List[str]:
        control_list: List[str] = [control.id]
        if control.controls:
            for sub_control in control.controls:
                control_list.extend(self._get_control_list(sub_control))
        return control_list

    def _write_controls_full(self, control: cat.Control) -> None:
        control_list: List[str] = []
        if control.controls:
            for sub_control in control.controls:
                control_list.extend(self._get_control_list(sub_control))
            self._md_file.new_header(level=2, title='Controls:')
            for id_ in control_list:
                self._md_file.new_line(id_)

    def write_control_full(
        self, dest_path: pathlib.Path, control: cat.Control, group_title: str, all_details: bool
    ) -> None:
        """Write out the full control in markdown format."""
        self._md_file = MDWriter(dest_path)
        self._md_file.new_paragraph()
        title = f'Control: {control.id} - {group_title} {control.title}'
        self._md_file.new_header(level=1, title=title)
        self._md_file.set_indent_level(-1)
        if all_details:
            if control.class_:
                self._md_file.new_header(level=2, title=f'class: {control.class_}')

            self._write_params_full(control)
            self._write_props_full(control)
            self._write_links_full(control)
        self._write_parts_prose(control)
        self._write_controls_full(control)

        self._md_file.write_out()

    def _get_id_title(self, ii: int, lines: List[str]) -> Tuple[int, str, str]:
        while ii < len(lines):
            line = lines[ii]
            ii += 1
            if line.startswith('# Control: '):
                id_ = line.split()[2]
                # FIXME this should be regex since - may be in title
                title = line.split('-')[-1]
                return (ii, id_, title)
        raise TrestleError('Unable to find #Control: heading in control markdown file.')

    def _get_header_level(self, line: str) -> int:
        return -1

    def _read_param(self, ii: int, lines: List[str], name: str, params: List[common.Parameter], level: int) -> int:
        # if level appears at same depth leave
        # if one line label thing read it
        # if multiline read until...
        return -1

    def _read_prop(
        self, ii: int, lines: List[str], name: str, value: str, props: List[common.Property], level: int
    ) -> int:
        return -1

    def _read_link(self, ii: int, lines: List[str], href: str, links: List[common.Link], level: int) -> int:
        return -1

    def _read_part(self, ii: int, lines: List[str], name: str, parts: List[common.Part], level: int) -> int:
        return -1

    def _read_controls(self, ii: int, lines: List[str], control_id_list: List[str]) -> int:
        """Read list of included control ids at end of file - not actual full control details."""
        while ii < len(lines):
            line = lines[ii]
            if line:
                control_id_list.append(line)
            ii += 1
        return -1

    def _get_attribute(self, ii: int, lines: List[str], control: cat.Control, control_id_list: List[str]) -> int:
        """Look for a high level entry heading for a control attribute."""
        while ii < len(lines):
            line = lines[ii]
            ii += 1
            if line:
                if line.startswith('## class: '):
                    control.class_ = line.split()[-1]
                elif line.startswith('## Param: '):
                    ii = self._read_param(ii, lines, line.split()[-1], control.params, 2)
                elif line.startswith('## Prop: '):
                    tokens = line.split()
                    ii = self._read_prop(ii, lines, tokens[-3], tokens[-1], control.props, 2)
                elif line.startswith('## link:'):
                    ii = self._read_link(ii, lines, line.split()[-1], control.links, 2)
                elif line.startswith('## Part: '):
                    ii = self._read_part(ii, lines, line.split()[-1], control.parts, 2)
                elif line.startswith('## Controls: '):
                    ii = self._read_controls(ii, lines, control_id_list)
                else:
                    raise TrestleError(f'Error parsing md for control {control.id} line {line}.')
                return ii
        return -1

    def read_control_full(self, control_path: pathlib.Path) -> cat.Control:
        """Read the control at the given path."""
        control = gens.generate_sample_model(cat.Control)
        control.params = []
        control.props = []
        control.links = []
        control.parts = []
        control_id_list = []
        with open(control_path, 'r', encoding=const.FILE_ENCODING) as md_file:
            lines = [line.strip() for line in md_file.readlines()]
        ii, control.id, control.title = self._get_id_title(0, lines)
        self._get_header_level('## test')
        self._read_param(0, lines, 'test', [], 0)
        self._read_prop(0, lines, 'test', 'value', [], 0)
        self._read_link(0, lines, control, [], 0)
        self._read_part(0, lines, 'test', [], 0)
        while ii > 0:
            ii = self._get_attribute(ii, lines, control, control_id_list)
        return control
