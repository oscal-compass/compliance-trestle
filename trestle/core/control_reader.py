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
"""Handle reading of writing controls from markdown."""
import logging
import pathlib
import re
import string
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import trestle.core.generic_oscal as generic
import trestle.oscal.catalog as cat
from trestle.common import const
from trestle.common.common_types import TypeWithProps
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_list, delete_list_from_list, merge_dicts, none_if_empty
from trestle.common.model_utils import ModelUtils
from trestle.common.str_utils import spaces_and_caps_to_snake
from trestle.core import generators as gens
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.core.control_interface import CompDict, ComponentImpInfo, ControlInterface
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.core.markdown.markdown_processor import MarkdownNode
from trestle.oscal import common
from trestle.oscal import component as comp
from trestle.oscal import profile as prof

logger = logging.getLogger(__name__)


class ControlReader():
    """Class to read controls from markdown."""

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
                indent = ControlReader._indent(line)
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

        return label_prefix + ControlReader._bump_label(label_suffix)

    @staticmethod
    def _read_parts(indent: int, ii: int, lines: List[str], parent_id: str,
                    parts: List[common.Part]) -> Tuple[int, List[common.Part]]:
        """If indentation level goes up or down, create new list or close current one."""
        while True:
            ii, new_indent, line = ControlReader._get_next_indent(ii, lines)
            if new_indent < 0:
                # we are done reading control statement
                return ii, parts
            if new_indent == indent:
                # create new item part and add to current list of parts
                id_text, prose = ControlReader._read_part_id_prose(line)
                # id_text is the part id and needs to be as a label property value
                # if none is there then create one from previous part, or use default
                if not id_text:
                    prev_label = ControlInterface.get_label(parts[-1]) if parts else ''
                    id_text = ControlReader._create_next_label(prev_label, indent)
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
                ii, new_parts = ControlReader._read_parts(new_indent, ii, lines, parts[-1].id, [])
                if new_parts:
                    parts[-1].parts = new_parts
            else:
                # return list of sub-parts
                return ii, parts

    @staticmethod
    def _read_control_statement(ii: int, lines: List[str], control_id: str) -> Tuple[int, common.Part]:
        """Search for the Control statement and read until next ## Control."""
        while 0 <= ii < len(lines) and not lines[ii].startswith(const.CONTROL_HEADER):
            ii += 1
        if ii >= len(lines):
            raise TrestleError(f'Control statement not found for control {control_id}')
        ii += 1

        ii, line = ControlReader._get_next_line(ii, lines)
        if ii < 0:
            # This means no statement and control withdrawn (this happens in NIST catalog)
            return ii, None
        if line and line[0] == ' ' and line.lstrip()[0] != '-':
            # prose that appears indented but has no - : treat it as the normal statement prose
            line = line.lstrip()
            indent = -1
            ii += 1
        else:
            ii, indent, line = ControlReader._get_next_indent(ii, lines)

        statement_id = ControlInterface.create_statement_id(control_id)
        statement_part = common.Part(name=const.STATEMENT, id=statement_id)
        # first line is either statement prose or start of statement parts
        if indent < 0:
            statement_part.prose = line
            ii += 1
        # we have absorbed possible statement prose.
        # now just read parts recursively
        # if there was no statement prose, this will re-read the line just read
        # as the start of the statement's parts
        ii, parts = ControlReader._read_parts(0, ii, lines, statement_part.id, [])
        statement_part.parts = none_if_empty(parts)
        return ii, statement_part

    @staticmethod
    def _read_control_objective(ii: int, lines: List[str], control_id: str) -> Tuple[int, Optional[common.Part]]:
        ii_orig = ii
        while 0 <= ii < len(lines) and not lines[ii].startswith(const.CONTROL_OBJECTIVE_HEADER):
            ii += 1

        if ii >= len(lines):
            return ii_orig, None
        ii += 1

        ii, line = ControlReader._get_next_line(ii, lines)
        if ii < 0:
            raise TrestleError(f'Unable to parse objective from control markdown {control_id}')
        if line and line[0] == ' ' and line.lstrip()[0] != '-':
            # prose that appears indented but has no - : treat it as the normal objective prose
            line = line.lstrip()
            indent = -1
            ii += 1
        else:
            ii, indent, line = ControlReader._get_next_indent(ii, lines)

        objective_part = common.Part(name='objective', id=f'{control_id}_obj')
        # first line is either objective prose or start of objective parts
        if indent < 0:
            objective_part.prose = line
            ii += 1
        # we have absorbed possible objective prose.
        # now just read parts recursively
        # if there was no objective prose, this will re-read the line just read
        # as the start of the objective's parts
        ii, parts = ControlReader._read_parts(0, ii, lines, objective_part.id, [])
        objective_part.parts = parts if parts else None
        return ii, objective_part

    @staticmethod
    def _read_sections(ii: int, lines: List[str], control_id: str,
                       control_parts: List[common.Part]) -> Tuple[int, Optional[List[common.Part]]]:
        """Read all sections following the section separated by ## Control."""
        new_parts = []
        prefix = const.CONTROL_HEADER + ' '
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
                    id_ = ControlInterface.strip_to_make_ncname(control_id + '_gdn')
                else:
                    id_ = ControlInterface.strip_to_make_ncname(control_id + '_' + label)
                label = ControlInterface.strip_to_make_ncname(label)
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
    def _comp_name_in_dict(comp_name: str, comp_dict: CompDict) -> str:
        """If the name is already in the dict in a similar form, stick to that form."""
        simple_name = ControlReader.simplify_name(comp_name)
        for name in comp_dict.keys():
            if simple_name == ControlReader.simplify_name(name):
                return name
        return comp_name

    @staticmethod
    def _add_node_to_dict(
        comp_name: str,
        label: str,
        comp_dict: CompDict,
        node: MarkdownNode,
        control_id: str,
        comp_list: List[str],
        context: ControlContext
    ) -> None:
        """Extract the label, prose, possible component name - along with implementation status."""
        component_mode = context.purpose == ContextPurpose.COMPONENT
        # for ssp, ### marks component name but for component it is ##
        # if it is a header, make sure it has correct format
        if node.key and node.key[0] == '#' and ControlInterface.bad_header(node.key):
            raise TrestleError(f'Improper header format for control {control_id}: {node.key}')
        if not component_mode:
            # look for component name heading if present
            prefix = '### '
            if node.key.startswith(prefix):
                if len(node.key.split()) <= 1:
                    raise TrestleError(
                        f'Header line in control {control_id} markdown starts with {prefix} but has no content.'
                    )
                comp_name = node.key.split(' ', 1)[1].strip()
                simp_comp_name = ControlReader.simplify_name(comp_name)
                if simp_comp_name == ControlReader.simplify_name(const.SSP_MAIN_COMP_NAME) and not component_mode:
                    raise TrestleError(
                        f'Response in control {control_id} has {const.SSP_MAIN_COMP_NAME} as a component heading.  '
                        'Instead, place all response prose for the default component at the top of the section, '
                        'with no ### component_name heading.  It will be entered as prose for the default system '
                        'component.'
                    )
                if simp_comp_name in comp_list:
                    raise TrestleError(
                        f'Control {control_id} has a section with two component headings for {comp_name}.  '
                        'Please combine the sections so there is only one heading for each component in a '
                        'statement.'
                    )
                comp_list.append(simp_comp_name)
                comp_name = ControlReader._comp_name_in_dict(comp_name, comp_dict)
            elif node.key.startswith('## What is the solution'):
                comp_name = const.SSP_MAIN_COMP_NAME
                simp_comp_name = ControlReader.simplify_name(comp_name)
                comp_list.append(simp_comp_name)
                comp_name = ControlReader._comp_name_in_dict(comp_name, comp_dict)

        # prose may be empty in md and we want to capture that so put it in the comp_dict
        prose = '\n'.join(ControlReader._clean_prose(node.content.text))
        # add the prose to the comp_dict, creating new entry as needed
        if comp_name in comp_dict:
            if label in comp_dict[comp_name]:
                comp_dict[comp_name][label].prose = prose
            else:
                # create new entry with prose
                comp_dict[comp_name][label] = ComponentImpInfo(prose=prose, rules=[])
        else:
            comp_dict[comp_name] = {label: ComponentImpInfo(prose=prose, rules=[])}

        # build list of subnodes that get handled specially so they aren't processed here
        subnode_kill: List[int] = []
        status_str = None
        remarks_str = None
        for ii, subnode in enumerate(node.subnodes):
            if subnode.key.find(const.IMPLEMENTATION_STATUS_REMARKS_HEADER) >= 0:
                remarks_str = subnode.key.split(maxsplit=4)[-1]
                subnode_kill.append(ii)
            elif subnode.key.find(const.IMPLEMENTATION_STATUS_HEADER) >= 0:
                status_str = subnode.key.split(maxsplit=3)[-1]
                subnode_kill.append(ii)
            # this effectively ignores the Rules: and regards them as read-only
            elif subnode.key.find('Rules:') >= 0:
                subnode_kill.append(ii)
        if status_str:
            new_status = common.ImplementationStatus(state=status_str, remarks=remarks_str)
            if comp_name not in comp_dict:
                comp_dict[comp_name] = {}
            if label not in comp_dict[comp_name]:
                comp_dict[comp_name][label] = ComponentImpInfo(prose='', rules=[])
            comp_dict[comp_name][label].status = new_status
        delete_list_from_list(node.subnodes, subnode_kill)
        for subnode in as_list(node.subnodes):
            ControlReader._add_node_to_dict(comp_name, label, comp_dict, subnode, control_id, comp_list, context)

    @staticmethod
    def _get_statement_label(control: Optional[cat.Control], statement_id: str) -> str:
        if control:
            for part in as_list(control.parts):
                if part.name == const.STATEMENT:
                    for sub_part in as_list(part.parts):
                        if sub_part.name == 'item' and sub_part.id == statement_id:
                            return ControlInterface.get_label(sub_part)
        return ''

    @staticmethod
    def _add_component_to_dict(
        control_imp: comp.ControlImplementation, comp_title: str, control: Optional[cat.Control], comp_dict: CompDict
    ) -> Tuple[Dict[str, Dict[str, str]], List[str]]:
        """Add imp_reqs for this control and this component to the component dictionary."""
        control_id = control.id if control else 'temp'
        params_dict = {}
        all_rules = set()
        sub_comp_dict = {}
        for imp_req in ControlInterface.get_control_imp_reqs(control_imp, control_id):
            # if description is same as control id regard it as not having prose
            # add top level control guidance with no statement id
            prose = ControlReader._handle_empty_prose(imp_req.description, control_id)
            params_dict.update(ControlInterface.get_params_dict_from_item(imp_req))
            rules_list = ControlInterface.get_rule_list_for_item(imp_req)
            all_rules.update(rules_list)
            status = ControlInterface.get_status_from_props(imp_req)
            sub_comp_dict[''] = ComponentImpInfo(prose=prose, status=status, rules=rules_list)
            for statement in as_list(imp_req.statements):
                rules_list = ControlInterface.get_rule_list_for_item(statement)
                all_rules.update(rules_list)
                status = ControlInterface.get_status_from_props(statement)
                label = ControlReader._get_statement_label(control, statement.statement_id)
                prose = ControlReader._handle_empty_prose(statement.description, statement.statement_id)
                sub_comp_dict[label] = ComponentImpInfo(prose=prose, status=status, rules=rules_list)
        if sub_comp_dict:
            comp_dict[comp_title] = sub_comp_dict
        return params_dict, sorted(all_rules)

    @staticmethod
    def _insert_header_content(
        imp_req: generic.GenericImplementedRequirement, header: Dict[str, Any], control_id: str
    ) -> None:
        """Insert yaml header content into the imp_req and its by_comps."""
        dict_ = header.get(const.TRESTLE_PROPS_TAG, {})
        # if an attribute is in the dict but it is None, need to make sure we get empty list anyway
        control_orig = as_list(dict_.get(const.CONTROL_ORIGINATION, []))
        imp_status = as_list(dict_.get(const.IMPLEMENTATION_STATUS, []))
        roles = as_list(dict_.get(const.RESPONSIBLE_ROLES, []))
        props = []
        responsible_roles = []
        for co in control_orig:
            if isinstance(co, str):
                props.append(common.Property(ns=const.NAMESPACE_NIST, name=const.CONTROL_ORIGINATION, value=co))
            elif isinstance(co, dict):
                if const.STATUS_INHERITED in co:
                    uuid = co[const.STATUS_INHERITED]
                    props.append(common.Property(name=const.LEV_AUTH_UUID, value=uuid))
                    props.append(
                        common.Property(
                            ns=const.NAMESPACE_NIST, name=const.CONTROL_ORIGINATION, value=const.STATUS_INHERITED
                        )
                    )
                else:
                    raise TrestleError(f'The yaml header for control {control_id} has unexpected content: {co}')
            else:
                raise TrestleError(f'The yaml header for control {control_id} has unexpected content: {co}')
        # FIXME this needs reworking
        for status in imp_status:
            if isinstance(status, str):
                props.append(
                    common.Property(ns=const.NAMESPACE_FEDRAMP, name=const.IMPLEMENTATION_STATUS, value=status)
                )
            elif isinstance(status, dict):
                if const.STATUS_PLANNED in status:
                    if const.STATUS_COMPLETION_DATE not in status:
                        raise TrestleError(
                            f'Planned status in the control {control_id} yaml header must '
                            f'specify completion date: {status}'
                        )
                    props.append(
                        common.Property(
                            ns=const.NAMESPACE_FEDRAMP, name=const.STATUS_PLANNED, value=status[const.STATUS_PLANNED]
                        )
                    )
                    datestr = status[const.STATUS_COMPLETION_DATE]
                    datestr = datestr.strftime('%Y-%m-%d') if isinstance(datestr, datetime) else str(datestr)
                    props.append(
                        common.Property(
                            ns=const.NAMESPACE_FEDRAMP, name=const.STATUS_PLANNED_COMPLETION_DATE, value=datestr
                        )
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
    def simplify_name(name: str) -> str:
        """Simplify the name to ignore variations in case, space, hyphen, underscore, slash."""
        return name.lower().replace(' ', '').replace('-', '').replace('_', '').replace('/', '')

    @staticmethod
    def _get_label_from_implementation_header(imp_header: str):
        # assumed to be of form: Implementation for part a.
        split_header = imp_header.split(' ', 4)
        if len(split_header) != 5:
            raise TrestleError(f'Implementation header cannot be parsed for statement part: {imp_header}')
        return split_header[4].strip()

    @staticmethod
    def read_all_implementation_prose_and_header(
        control: cat.Control, control_file: pathlib.Path, context: ControlContext
    ) -> Tuple[CompDict, Dict[str, List[str]]]:
        """
        Find all labels and associated implementation prose in the markdown for this control.

        Args:
            control_file: path to the control markdown file
            context: context of the control usage

        Returns:
            Dictionary by comp_name of Dictionaries of part labels and corresponding prose read from the markdown file.
            Also returns the yaml header as dict in second part of tuple.
            This does not generate components - it only tracks component names and associated responses.

        Notes:
            If a component is provided, any implementation prose for a control will be added.
            In addition, the implemented requirement will be queried for a
            property corresponding to implementation status and included if available.
        """
        # this level only adds for known component but add_node_to_dict can add for other components
        comp_name = context.comp_name if context.comp_name else const.SSP_MAIN_COMP_NAME
        control_id = control_file.stem

        comp_dict: CompDict = {}
        yaml_header = {}
        # use context.rules_dict and params_dict to map rules
        if context.purpose == ContextPurpose.COMPONENT:
            # find rule info needed by this control
            params_dict, rules_list = ControlReader._add_component_to_dict(
                context.control_implementation, context.comp_name, control, comp_dict
            )
            all_params = []
            if params_dict:
                if not set(params_dict.keys()).issuperset(rules_list):
                    raise TrestleError(f'Control {control_id} has a parameter assigned to a rule that is not defined.')
                if context.rules_dict:
                    all_params.extend(
                        [
                            {
                                context.rules_dict[id_]['name']: context.rules_params_dict[id_]
                                for id_ in context.rules_params_dict.keys()
                            }
                        ]
                    )
            if context.rules_dict:
                rule_ids = [id_ for id_ in context.rules_dict.keys() if context.rules_dict[id_]['name'] in rules_list]
                yaml_header[const.COMP_DEF_RULES_TAG] = [context.rules_dict[id_] for id_ in rule_ids]
                all_params.extend(
                    [context.rules_params_dict[id_] for id_ in rule_ids if id_ in context.rules_params_dict]
                )
            if all_params:
                yaml_header[const.RULES_PARAMS_TAG] = all_params
            if context.rules_param_vals:
                yaml_header[const.COMP_DEF_RULES_PARAM_VALS_TAG] = context.rules_param_vals

        if not control_file.exists():
            return comp_dict, yaml_header
        # if the file exists, load the contents and do not use prose from comp_dict
        try:
            md_api = MarkdownAPI()
            new_yaml_header, control_md = md_api.processor.process_markdown(control_file)
            yaml_header = new_yaml_header

            # first get the header strings, including statement labels, for statement imp reqs
            imp_string = '## Implementation '
            headers = control_md.get_all_headers_for_level(2)
            # get e.g. ## Implementation a.  ## Implementation b. etc
            imp_header_list = [header for header in headers if header.startswith(imp_string)]

            # now get the (one) header for the main solution
            main_headers = list(control_md.get_all_headers_for_key(const.SSP_MD_IMPLEMENTATION_QUESTION, False))
            # should be only one header, so warn if others found
            if main_headers:
                if len(main_headers) > 1:
                    logger.warning(
                        f'Control {control_id} has {len(main_headers)} main header responses.  Will use first one only.'
                    )
                main_header = main_headers[0]
                node = control_md.get_all_nodes_for_keys([main_header], False)[0]
                # this node is top level so it will have empty label
                # it may have subnodes of Rules, Implementation Status, Implementaton Remarks
                ControlReader._add_node_to_dict(comp_name, '', comp_dict, node, control_id, [], context)
            for imp_header in imp_header_list:
                label = ControlReader._get_label_from_implementation_header(imp_header)
                node = control_md.get_node_for_key(imp_header)
                ControlReader._add_node_to_dict(comp_name, label, comp_dict, node, control_id, [], context)

        except TrestleError as e:
            raise TrestleError(f'Error occurred reading {control_file}: {e}')
        return comp_dict, yaml_header

    @staticmethod
    def _handle_empty_prose(prose: str, id_: str) -> str:
        """Regard prompt text or id_ as no prose and return blank string."""
        if prose.startswith(const.SSP_ADD_IMPLEMENTATION_PREFIX) or prose == id_:
            return ''
        return prose

    @staticmethod
    def read_implemented_requirement(
        control_file: pathlib.Path, avail_comps: Dict[str, generic.GenericComponent], context: ControlContext
    ) -> Tuple[str, generic.GenericImplementedRequirement]:
        """
        Get the implementated requirement associated with given control and link to existing components or new ones.

        Args:
            control_file: path of the control markdown file
            avail_comps: dictionary of known components keyed by component name
            context: context of the control usage

        Returns:
            Tuple: The control sort-id and the one implemented requirement for this control.

        Notes:
            Each statement may have several responses, with each response in a by_component for a specific component.
            statement_map keeps track of statements that may have several by_component responses.
        """
        control_id = control_file.stem
        comp_dict, header = ControlReader.read_all_implementation_prose_and_header(None, control_file, context)

        statement_map: Dict[str, generic.GenericStatement] = {}
        # create a new implemented requirement linked to the control id to hold the statements
        imp_req: generic.GenericImplementedRequirement = generic.GenericImplementedRequirement.generate()
        imp_req.control_id = control_id

        raw_comp_dict = {ControlReader.simplify_name(key): value for key, value in comp_dict.items()}
        raw_avail_comps = {ControlReader.simplify_name(key): value for key, value in avail_comps.items()}

        # the comp_dict captures all component names referenced by the control
        # need to create new components if not already in dict by looping over comps referenced by this control
        for comp_name in comp_dict.keys():
            component: Optional[generic.GenericComponent] = None
            raw_comp_name = ControlReader.simplify_name(comp_name)
            if raw_comp_name == ControlReader.simplify_name(const.SSP_MD_IMPLEMENTATION_QUESTION):
                comp_info: ComponentImpInfo = list(raw_comp_dict[raw_comp_name].items())[0][1]
                imp_req.description = ControlReader._handle_empty_prose(comp_info.prose, control_id)
                if comp_info.status:
                    ControlInterface.insert_status_in_props(imp_req, comp_info.status)
                continue
            if raw_comp_name in raw_avail_comps:
                component = raw_avail_comps[raw_comp_name]
            else:
                # here is where we create a new component on the fly as needed
                component = generic.GenericComponent.generate()
                component.title = comp_name
                avail_comps[comp_name] = component
                raw_avail_comps[raw_comp_name] = component
            # now create statements to hold the by-components and assign the statement id
            for label, comp_info in raw_comp_dict[raw_comp_name].items():
                # if there is a statement label create by_comp - otherwise assign status and prose to imp_req
                # create a new by-component to add to this statement
                if context.purpose == ContextPurpose.COMPONENT and not label:
                    imp_req.description = ControlReader._handle_empty_prose(comp_info.prose, control_id)
                    ControlInterface.insert_status_in_props(imp_req, comp_info.status)
                    continue
                by_comp: generic.GenericByComponent = generic.GenericByComponent.generate()
                # link it to the component uuid
                by_comp.component_uuid = component.uuid
                by_comp.implementation_status = comp_info.status
                # add the response prose to the description
                by_comp.description = ControlReader._handle_empty_prose(comp_info.prose, control_id)
                statement_id = ControlInterface.create_statement_id(control_id)
                # control level response has '' as label
                if label in ['', const.STATEMENT]:
                    statement_part_id = statement_id
                else:
                    clean_label = label.strip('.')
                    statement_part_id = ControlInterface.strip_to_make_ncname(f'{statement_id}.{clean_label}')
                if statement_part_id in statement_map:
                    statement = statement_map[statement_part_id]
                else:
                    statement: generic.GenericStatement = generic.GenericStatement.generate()
                    statement.statement_id = statement_part_id
                    statement.by_components = []
                    statement_map[statement_part_id] = statement
                statement.by_components.append(by_comp)

        imp_req.statements = list(statement_map.values())
        ControlReader._insert_header_content(imp_req, header, control_id)
        sort_id = header.get(const.SORT_ID, control_id)
        return sort_id, imp_req

    @staticmethod
    def _add_control_part(
        control_id: str,
        subnode: MarkdownNode,
        required_sections_list: List[str],
        sections_dict: Dict[str, str],
        snake_dict: Dict[str, str],
        control_parts: List[common.Part],
        found_sections: List[str],
        write_mode: bool
    ) -> bool:
        match = re.match(const.CONTROL_REGEX, subnode.key)
        if match:
            part_name_raw = match.groups(0)[0]
            prose = ControlReader._clean_prose(subnode.content.text)
            prose = '\n'.join(prose)
            # prose may be empty but make part anyway if it was in markdown
            # it also may contain sub-parts
            part_name_snake = spaces_and_caps_to_snake(part_name_raw)
            part_name = snake_dict.get(part_name_snake, part_name_snake)
            # if section is required and it hasn't been edited with prose raise error
            if not write_mode and part_name in required_sections_list and prose.startswith(
                    const.PROFILE_ADD_REQUIRED_SECTION_FOR_CONTROL_TEXT):
                missing_section = sections_dict.get(part_name, part_name)
                raise TrestleError(f'Control {control_id} is missing prose for required section {missing_section}')
            id_ = f'{control_id}_{part_name}'
            # use sections dict to find correct title otherwise leave it None
            part_title = sections_dict.get(part_name, None)
            part = common.Part(id=id_, name=part_name, prose=prose, title=part_title)
            part.parts = ControlReader._add_sub_parts(part.id, subnode)
            control_parts.append(part)
            found_sections.append(part_name)
            return True
        return False

    @staticmethod
    def _add_sub_parts(part_id: str,
                       node: MarkdownNode,
                       fixed_part_name: Optional[str] = None) -> Optional[List[common.Part]]:
        if not node.subnodes:
            return None
        parts = []
        for subnode in node.subnodes:
            # the count of hashes should be correct based on parsing already down by the markdown parser
            match = re.match(const.AFTER_HASHES_REGEX, subnode.key)
            if not match:
                raise TrestleError(f'Unexpected editable header {subnode.key} found in part {part_id}')
            part_name = match.groups(0)[0]
            part_name_snake = spaces_and_caps_to_snake(part_name)
            id_ = part_id + '.' + part_name_snake
            prose_lines = ControlReader._clean_prose(subnode.content.text)
            prose = '\n'.join(prose_lines)
            final_part_name = fixed_part_name if fixed_part_name else part_name_snake
            part = common.Part(id=id_, name=final_part_name, prose=prose)
            part.parts = ControlReader._add_sub_parts(part.id, subnode, fixed_part_name)
            parts.append(part)
        return parts

    @staticmethod
    def _add_sub_part(
        control_id: str,
        subnode: MarkdownNode,
        label_map: Dict[str, str],
        by_id_parts: Dict[str, List[common.Part]],
        sections_dict: Dict[str, str]
    ) -> None:
        """Add subnode contents to the list of by_id statement parts for the top level of the control."""
        match = re.match(const.PART_REGEX, subnode.key)
        if not match:
            raise TrestleError(f'Unexpected editable header {subnode.key} found in control {control_id}')
        by_part_label = match.groups(0)[0]
        control_label_map = label_map.get(control_id, None)
        if control_label_map is None:
            raise TrestleError(f'No label map found for control {control_id}')
        by_part_id = control_label_map.get(by_part_label, None)
        if by_part_id is None:
            raise TrestleError(f'No part id found for label {by_part_label} in control {control_id}')
        inv_map = {v: k for k, v in sections_dict.items()} if sections_dict else {}
        for node2 in as_list(subnode.subnodes):
            hash_pattern = '### '
            if node2.key.startswith(hash_pattern):
                part_name = spaces_and_caps_to_snake(node2.key.replace(hash_pattern, '', 1).strip())
                part_name = inv_map.get(part_name, part_name)
                prose = ControlReader._clean_prose(node2.content.text)
                prose = '\n'.join(prose)
                id_ = f'{by_part_id}.{part_name}'
                part = common.Part(id=id_, name=part_name, prose=prose)
                part.parts = ControlReader._add_sub_parts(part.id, node2)
            else:
                raise TrestleError(f'Unexpected header {node2.key} found in control {control_id}')
            if by_part_id not in by_id_parts:
                by_id_parts[by_part_id] = []
            by_id_parts[by_part_id].append(part)

    @staticmethod
    def _get_props_list(control_id: str, label_map: Dict[str, str],
                        yaml_header: Dict[str, Any]) -> Tuple[List[common.Property], Dict[str, List[common.Property]]]:
        """Get the list of props in the yaml header of this control as separate lists with and without by_id."""
        prop_list = yaml_header.get(const.TRESTLE_ADD_PROPS_TAG, [])
        props = []
        props_by_id = {}
        for prop_d in prop_list:
            by_id = prop_d.get('smt-part', None)
            if by_id and control_id in label_map:
                by_id = label_map[control_id].get(by_id, by_id)
            prop = common.Property(name=prop_d['name'], value=prop_d['value'], ns=prop_d.get('ns', None))
            if by_id:
                if by_id not in props_by_id:
                    props_by_id[by_id] = []
                props_by_id[by_id].append(prop)
            else:
                props.append(prop)
        return props, props_by_id

    @staticmethod
    def read_editable_content(
        control_path: pathlib.Path,
        required_sections_list: List[str],
        label_map: Dict[str, Dict[str, str]],
        sections_dict: Dict[str, str],
        write_mode: bool
    ) -> Tuple[str, List[prof.Alter], Dict[str, Any]]:
        """Get parts for the markdown control corresponding to Editable Content - along with the set-parameter dict."""
        control_id = control_path.stem
        new_alters: List[prof.Alter] = []
        snake_dict: Dict[str, str] = {}

        md_api = MarkdownAPI()
        yaml_header, control_tree = md_api.processor.process_markdown(control_path)
        # extract the sort_id if present in header
        sort_id = yaml_header.get(const.SORT_ID, control_id)
        # merge the incoming sections_dict with the one in the header, with priority to incoming
        header_sections_dict: Dict[str, str] = yaml_header.get(const.SECTIONS_TAG, {})
        merged_sections_dict = merge_dicts(header_sections_dict, sections_dict)
        # query header for mapping of short to long section names
        # create reverse lookup of long snake name to short name needed for part
        for key, value in merged_sections_dict.items():
            snake_dict[spaces_and_caps_to_snake(value)] = key
        found_sections: List[str] = []

        editable_node = None
        for header in list(control_tree.get_all_headers_for_level(1)):
            if header.startswith('# Editable'):
                editable_node = control_tree.get_node_for_key(header)
                break
        if not editable_node:
            return sort_id, [], {}

        control_parts = []
        by_id_parts = {}
        for subnode in editable_node.subnodes:
            # check if it is a part added directly to the list of parts for the control
            if not ControlReader._add_control_part(control_id,
                                                   subnode,
                                                   required_sections_list,
                                                   merged_sections_dict,
                                                   snake_dict,
                                                   control_parts,
                                                   found_sections,
                                                   write_mode):
                # otherwise add it to the list of new parts to be added to the sub-parts of a part based on by-id
                ControlReader._add_sub_part(control_id, subnode, label_map, by_id_parts, merged_sections_dict)

        missing_sections = set(required_sections_list) - set(found_sections)
        if missing_sections:
            raise TrestleError(f'Control {control_id} is missing required sections {missing_sections}')
        param_dict: Dict[str, Any] = {}
        # get set_params from the header and add to parm_dict
        header_params = yaml_header.get(const.SET_PARAMS_TAG, {})
        if header_params:
            param_dict.update(header_params)

        props, props_by_id = ControlReader._get_props_list(control_id, label_map, yaml_header)

        # When adding props without by_id it can either be starting or ending and we default to ending
        # This is the default behavior as described for implicit binding in
        # https://pages.nist.gov/OSCAL/concepts/processing/profile-resolution/
        # When adding props to a part using by_id, it is the same situation because it cannot be before or after since
        # props are not in the same list as parts

        adds: List[prof.Add] = []

        # add the parts and props at control level
        if control_parts or props:
            adds.append(prof.Add(parts=none_if_empty(control_parts), props=none_if_empty(props), position='ending'))

        # add the parts and props at the part level, by-id
        by_ids = set(by_id_parts.keys()).union(props_by_id.keys())
        for by_id in sorted(by_ids):
            parts = by_id_parts.get(by_id, None)
            props = props_by_id.get(by_id, None)
            adds.append(prof.Add(parts=parts, props=props, position='ending', by_id=by_id))

        new_alters = []
        if adds:
            new_alters = [prof.Alter(control_id=control_id, adds=adds)]
        return sort_id, new_alters, param_dict

    @staticmethod
    def _update_display_prop_namespace(item: TypeWithProps):
        """Set namespace for special property display_name."""
        for prop in as_list(item.props):
            if prop.name == const.DISPLAY_NAME:
                prop.ns = const.TRESTLE_GENERIC_NS

    @staticmethod
    def read_control(control_path: pathlib.Path, set_parameters_flag: bool) -> Tuple[cat.Control, str]:
        """Read the control and group title from the markdown file."""
        control = gens.generate_sample_model(cat.Control)
        md_api = MarkdownAPI()
        yaml_header, control_tree = md_api.processor.process_markdown(control_path)
        control_titles = list(control_tree.get_all_headers_for_level(1))
        if len(control_titles) == 0:
            raise TrestleError(f'Control markdown: {control_path} contains no control title.')

        control.id, group_title, control.title = ControlReader._parse_control_title_line(control_titles[0])

        control_headers = list(control_tree.get_all_headers_for_level(2))
        if len(control_headers) == 0:
            raise TrestleError(f'Control markdown: {control_path} contains no control statements.')

        control_statement = control_tree.get_node_for_key(control_headers[0])
        rc, statement_part = ControlReader._read_control_statement(
            0, control_statement.content.raw_text.split('\n'), control.id
        )
        if rc < 0:
            return control, group_title
        control.parts = [statement_part] if statement_part else None
        control_objective = control_tree.get_node_for_key(const.CONTROL_OBJECTIVE_HEADER)
        if control_objective is not None:
            _, objective_part = ControlReader._read_control_objective(
                0, control_objective.content.raw_text.split('\n'), control.id
            )
            if objective_part:
                if control.parts:
                    control.parts.append(objective_part)
                else:
                    control.parts = [objective_part]
        for header_key in control_tree.get_all_headers_for_key(const.CONTROL_HEADER, False):
            if header_key not in {control_headers[0], const.CONTROL_OBJECTIVE_HEADER, control_titles[0]}:
                section_node = control_tree.get_node_for_key(header_key)
                _, control.parts = ControlReader._read_sections(
                    0, section_node.content.raw_text.split('\n'), control.id, control.parts
                )
        if set_parameters_flag:
            params: Dict[str, str] = yaml_header.get(const.SET_PARAMS_TAG, [])
            if params:
                control.params = []
                for id_, param_dict in params.items():
                    param_dict['id'] = id_
                    param = ModelUtils.dict_to_parameter(param_dict)
                    # if display_name is in list of properties, set its namespace
                    ControlReader._update_display_prop_namespace(param)
                    control.params.append(param)
        if const.SORT_ID in yaml_header:
            control.props = control.props if control.props else []
            control.props.append(common.Property(name=const.SORT_ID, value=yaml_header[const.SORT_ID]))
        return control, group_title
