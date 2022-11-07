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
"""Handle queries and utility operations on controls in memory."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

import trestle.oscal.catalog as cat
from trestle.common import const
from trestle.common.common_types import TypeWithParts, TypeWithProps
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_filtered_list, as_list, none_if_empty
from trestle.common.str_utils import string_from_root, strip_lower_equals
from trestle.oscal import common
from trestle.oscal import component as comp
from trestle.oscal import profile as prof

logger = logging.getLogger(__name__)


class ParameterRep(Enum):
    """Enum for ways to represent a parameter."""

    LEAVE_MOUSTACHE = 0
    VALUE_OR_STRING_NONE = 1
    LABEL_OR_CHOICES = 2
    VALUE_OR_LABEL_OR_CHOICES = 3
    VALUE_OR_EMPTY_STRING = 4
    ASSIGNMENT_FORM = 5


@dataclass
class ComponentImpInfo:
    """Class to capture component prose and status."""

    prose: str
    rules: List[str]
    status: common.ImplementationStatus = common.ImplementationStatus(state=const.STATUS_PLANNED)


# provide name for this type
CompDict = Dict[str, Dict[str, ComponentImpInfo]]


@dataclass
class PartInfo:
    """Class to capture control part info needed in markdown."""

    name: str
    prose: str
    smt_part: str = ''
    props: Optional[List[common.Property]] = None
    parts: Optional[List[PartInfo]] = None

    def to_dicts(self, part_id_map: Dict[str, str]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Convert the part info to a dict or list of props."""
        prop_list = []
        part = {}
        # if it has a part name then it is a part with prose
        if self.name:
            part['name'] = part_id_map.get(self.name, self.name)
            if self.prose:
                part['prose'] = self.prose
            if self.parts:
                all_subparts = []
                for subpart in self.parts:
                    subpart_dict, _ = subpart.to_dicts(part_id_map)
                    all_subparts.append(subpart_dict)
                part['parts'] = all_subparts

        # otherwise it is a list of props
        else:
            for prop in as_list(self.props):
                prop_d = {'name': prop.name, 'value': prop.value}
                if prop.ns:
                    prop_d['ns'] = str(prop.ns)
                if self.smt_part:
                    prop_d['smt-part'] = part_id_map.get(self.smt_part, self.smt_part)
                prop_list.append(prop_d)
        return part, prop_list


class ControlInterface:
    """Class to interact with controls in memory."""

    @staticmethod
    def _wrap_label(label: str):
        l_side = '\['
        r_side = '\]'
        wrapped = '' if label == '' else f'{l_side}{label}{r_side}'
        return wrapped

    @staticmethod
    def _gap_join(a_str: str, b_str: str) -> str:
        a_clean = a_str.strip()
        b_clean = b_str.strip()
        if not b_clean:
            return a_clean
        gap = '\n' if a_clean else ''
        return a_clean + gap + b_clean

    @staticmethod
    def _get_control_section_part(part: common.Part, section_name: str) -> str:
        """Get the prose for a named section in the control."""
        prose = ''
        if part.name == section_name and part.prose is not None:
            prose = ControlInterface._gap_join(prose, part.prose)
        if part.parts:
            for sub_part in part.parts:
                prose = ControlInterface._gap_join(
                    prose, ControlInterface._get_control_section_part(sub_part, section_name)
                )
        return prose

    @staticmethod
    def get_control_section_prose(control: cat.Control, section_name: str) -> str:
        """Get the prose for the control section."""
        prose = ''
        if control.parts:
            for part in control.parts:
                prose = ControlInterface._gap_join(
                    prose, ControlInterface._get_control_section_part(part, section_name)
                )
        return prose

    @staticmethod
    def _find_section_info(part: common.Part, skip_section_list: List[str]) -> Tuple[str, str, str]:
        """Find section not in list."""
        if part.prose and part.name not in skip_section_list:
            return part.id, part.name, part.title
        if part.parts:
            for sub_part in part.parts:
                id_, name, title = ControlInterface._find_section_info(sub_part, skip_section_list)
                if id_:
                    return id_, name, title
        return '', '', ''

    @staticmethod
    def _find_section(control: cat.Control, skip_section_list: List[str]) -> Tuple[str, str, str]:
        """Find next section not in list."""
        if control.parts:
            for part in control.parts:
                id_, name, title = ControlInterface._find_section_info(part, skip_section_list)
                if id_:
                    return id_, name, title
        return '', '', ''

    @staticmethod
    def strip_to_make_ncname(label: str) -> str:
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
    def get_prop(item: TypeWithProps, prop_name: str, default: Optional[str] = None) -> str:
        """Get the property with that name or return empty string."""
        for prop in as_list(item.props):
            if prop.name.strip().lower() == prop_name.strip().lower():
                return prop.value.strip()
        return default if default else ''

    @staticmethod
    def _delete_prop(part_control: TypeWithProps, prop_name: str) -> None:
        """Delete property with that name."""
        # assumes at most one instance
        names = [prop.name for prop in as_list(part_control.props)]
        if prop_name in names:
            index = names.index(prop_name)
            del part_control.props[index]
        part_control.props = none_if_empty(part_control.props)

    @staticmethod
    def _replace_prop(part_control: TypeWithProps, new_prop: common.Property) -> None:
        """Delete property with that name if present and insert new one."""
        # assumes at most one instance
        names = [prop.name for prop in as_list(part_control.props)]
        if new_prop.name in names:
            index = names.index(new_prop.name)
            del part_control.props[index]
        part_control.props = as_list(part_control.props)
        part_control.props.append(new_prop)

    @staticmethod
    def create_statement_id(control_id: str, lower: bool = False) -> str:
        """Create the control statement id from the control id."""
        id_ = f'{control_id}_smt'
        return id_.lower() if lower else id_

    @staticmethod
    def get_statement_id(control: cat.Control) -> str:
        """Find the statement id in the control."""
        for part in as_list(control.parts):
            if part.name == const.STATEMENT:
                return part.id
        return ControlInterface.create_statement_id(control.id)

    @staticmethod
    def get_sort_id(control: cat.Control, allow_none=False) -> Optional[str]:
        """Get the sort-id for the control."""
        for prop in as_list(control.props):
            if prop.name == const.SORT_ID:
                return prop.value.strip()
        return None if allow_none else control.id

    @staticmethod
    def get_label(item: TypeWithProps) -> str:
        """Get the label from the props of a part or control."""
        return ControlInterface.get_prop(item, 'label')

    @staticmethod
    def get_part_by_id(item: TypeWithParts, id_: str) -> Optional[common.Part]:
        """Find the part within this item's list of parts that matches id."""
        for part in as_list(item.parts):
            if part.id == id_:
                return part
            deep_part = ControlInterface.get_part_by_id(part, id_)
            if deep_part:
                return deep_part
        return None

    @staticmethod
    def get_part(part: common.Part, item_type: str, skip_id: Optional[str]) -> List[Union[str, List[str]]]:
        """
        Find parts with the specified item type, within the given part.

        For a part in a control find the parts in it that match the item_type
        Return list of string formatted labels and associated descriptive prose
        """
        items = []
        if part.name in [const.STATEMENT, item_type]:
            # the options here are to force the label to be the part.id or the part.label
            # the label may be of the form (a) while the part.id is ac-1_smt.a.1.a
            # here we choose the latter and extract the final element
            label = ControlInterface.get_label(part)
            label = part.id.split('.')[-1] if not label else label
            wrapped_label = ControlInterface._wrap_label(label)
            pad = '' if wrapped_label == '' or not part.prose else ' '
            prose = '' if part.prose is None else part.prose
            # top level prose has already been written out, if present
            # use presence of . in id to tell if this is top level prose
            if part.id != skip_id:
                items.append(f'{wrapped_label}{pad}{prose}')
            if part.parts:
                sub_list = []
                for prt in part.parts:
                    sub_list.extend(ControlInterface.get_part(prt, item_type, skip_id))
                sub_list.append('')
                items.append(sub_list)
        return items

    @staticmethod
    def _get_adds_for_control(profile: prof.Profile, control_id: str) -> List[prof.Add]:
        """Get the adds for a given control id from a profile."""
        adds: List[prof.Add] = []
        if profile.modify:
            for alter in as_list(profile.modify.alters):
                if alter.control_id == control_id:
                    adds.extend(as_list(alter.adds))
        return adds

    @staticmethod
    def get_all_add_info(control_id: str, profile: prof.Profile) -> List[PartInfo]:
        """Get the adds for a control from a profile by control id."""
        part_infos = []
        for add in ControlInterface._get_adds_for_control(profile, control_id):
            # add control level props with no name
            if add.props:
                smt_part = add.by_id if add.by_id else ''
                part_infos.append(PartInfo(name='', prose='', smt_part=smt_part, props=add.props))
            # add part level props with part name
            for part in as_list(add.parts):
                subpart_info = ControlInterface._get_part_and_subpart_info(part, add.by_id)
                part_infos.append(
                    PartInfo(
                        name=part.name, prose=part.prose, smt_part=add.by_id, props=part.props, parts=subpart_info
                    )
                )
        return part_infos

    @staticmethod
    def _get_part_and_subpart_info(part: common.Part, add_by_id: str) -> List[PartInfo]:
        """Get part and its subparts info needed for markdown purposes."""
        part_infos = []
        for subpart in as_list(part.parts):
            subpart_info = None
            if subpart.parts:
                # Recursively add subparts info
                subpart_info = ControlInterface._get_part_and_subpart_info(subpart, add_by_id)
            part_infos.append(
                PartInfo(
                    name=subpart.name, prose=subpart.prose, smt_part=add_by_id, props=subpart.props, parts=subpart_info
                )
            )

        return part_infos

    @staticmethod
    def get_section(control: cat.Control, skip_section_list: List[str]) -> Tuple[str, str, str, str]:
        """Get sections that are not in the list."""
        id_, name, title = ControlInterface._find_section(control, skip_section_list)
        if id_:
            return id_, name, title, ControlInterface.get_control_section_prose(control, name)
        return '', '', '', ''

    @staticmethod
    def get_part_prose(control: cat.Control, part_name: str) -> str:
        """Get the prose for a named part."""
        prose = ''
        for part in as_list(control.parts):
            prose += ControlInterface._get_control_section_part(part, part_name)
        return prose.strip()

    @staticmethod
    def setparam_to_param(param_id: str, set_param: prof.SetParameter) -> common.Parameter:
        """
        Convert setparameter to parameter.

        Args:
            param_id: the id of the parameter
            set_param: the set_parameter from a profile

        Returns:
            a Parameter with param_id and content from the SetParameter
        """
        return common.Parameter(
            id=param_id, values=set_param.values, select=set_param.select, label=set_param.label, props=set_param.props
        )

    @staticmethod
    def get_rules_dict_from_item(item: TypeWithProps) -> Dict[str, Dict[str, str]]:
        """Get all rules found in this items props."""
        # rules is dict containing rule_id and description
        rules = {}
        name = ''
        desc = ''
        id_ = ''
        for prop in as_list(item.props):
            if prop.name == const.RULE_ID:
                name = prop.value
                id_ = string_from_root(prop.remarks)
            elif prop.name == const.RULE_DESCRIPTION:
                desc = prop.value
            # grab each pair in case there are multiple pairs
            # then clear and look for new pair
            if name and desc:
                rules[id_] = {'name': name, 'description': desc}
                name = desc = id_ = ''
        return rules

    @staticmethod
    def get_rule_list_for_item(item: TypeWithProps) -> List[str]:
        """Get the list of rules applying to this item."""
        return [prop.value for prop in as_filtered_list(item.props, lambda p: p.name == const.RULE_ID)]

    @staticmethod
    def get_params_dict_from_item(item: TypeWithProps) -> Dict[str, Dict[str, str]]:
        """Get all params found in this item with rule_id as key."""
        # id, description, options - where options is a string containing comma-sep list of items
        # params is dict with rule_id as key and value contains: param_name, description and choices
        params: Dict[str, Dict[str, str]] = {}
        for prop in as_list(item.props):
            if prop.name == const.PARAMETER_ID:
                rule_id = string_from_root(prop.remarks)
                param_name = prop.value
                if rule_id in params:
                    raise TrestleError(f'Duplicate param {param_name} found for rule {rule_id}')
                # create new param for this rule
                params[rule_id] = {'name': param_name}
            elif prop.name == const.PARAMETER_DESCRIPTION:
                rule_id = string_from_root(prop.remarks)
                if rule_id in params:
                    params[rule_id]['description'] = prop.value
                else:
                    raise TrestleError(f'Param description for rule {rule_id} found with no param_id')
            elif prop.name == const.PARAMETER_VALUE_ALTERNATIVES:
                rule_id = string_from_root(prop.remarks)
                if rule_id in params:
                    params[rule_id]['options'] = prop.value
                else:
                    raise TrestleError(f'Param options for rule {rule_id} found with no param_id')
        new_params = {}
        for rule_id, param in params.items():
            if 'name' not in param:
                logger.warning(f'Parameter for rule_id {rule_id} has no matching name.  Ignoring the param.')
            else:
                param['description'] = param.get('description', '')
                param['options'] = param.get('options', '')
                new_params[rule_id] = param
        return new_params

    @staticmethod
    def get_param_vals_from_control_imp(control_imp: comp.ControlImplementation) -> Dict[str, str]:
        """Get param values from set_parameters in control implementation."""
        param_dict = {
            set_param.param_id: ControlInterface._setparam_values_as_str(set_param)
            for set_param in as_list(control_imp.set_parameters)
        }
        return {key: val for key, val in param_dict.items() if val}

    @staticmethod
    def merge_props(dest: Optional[List[common.Property]],
                    src: Optional[List[common.Property]]) -> List[common.Property]:
        """Merge a source list of properties into a destination list."""
        if not src:
            return dest
        new_props: List[common.Property] = []
        src_map = {prop.name: prop for prop in src}
        dest_map = {prop.name: prop for prop in dest}
        all_names = set(src_map.keys()).union(dest_map.keys())
        for name in sorted(all_names):
            if name in src_map and name not in dest_map:
                new_props.append(src_map[name])
            elif name in dest_map and name not in src_map:
                new_props.append(dest_map[name])
            else:
                new_prop = dest_map[name]
                src_prop = src_map[name]
                new_prop.class_ = src_prop.class_ if src_prop.class_ else new_prop.class_
                new_prop.ns = src_prop.ns if src_prop.ns else new_prop.ns
                new_prop.remarks = src_prop.remarks if src_prop.remarks else new_prop.remarks
                new_prop.uuid = src_prop.uuid if src_prop.uuid else new_prop.uuid
                new_prop.value = src_prop.value
                new_props.append(new_prop)
        return new_props

    @staticmethod
    def merge_part(dest: common.Part, src: common.Part) -> common.Part:
        """Merge a source part into the destination part."""
        dest.name = src.name if src.name else dest.name
        dest.ns = src.ns if src.ns else dest.ns
        dest.props = none_if_empty(ControlInterface.merge_props(dest.props, src.props))
        dest.prose = src.prose
        dest.title = src.title if src.title else dest.title
        ControlInterface.merge_parts(dest, src)
        return dest

    @staticmethod
    def merge_parts(dest: TypeWithParts, src: TypeWithParts) -> None:
        """Merge the parts from the source into the destination."""
        if not dest.parts:
            dest.parts = src.parts
        elif not src.parts:
            dest.parts = None
        else:
            new_parts: List[common.Part] = []
            dest_map = {part.id: part for part in dest.parts}
            for src_part in src.parts:
                dest_part = dest_map.get(src_part.id, None)
                if not dest_part:
                    new_parts.append(src_part)
                else:
                    new_part = ControlInterface.merge_part(dest_part, src_part)
                    if new_part:
                        new_parts.append(new_part)
            dest.parts = new_parts

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
                    ControlInterface.merge_dicts_deep(dest[key], src[key], overwrite_header_values)
                elif isinstance(dest[key], list) and isinstance(src[key], list):
                    for item in src[key]:
                        if item not in dest[key]:
                            dest[key].append(item)
                # otherwise override dest if needed
                elif overwrite_header_values:
                    dest[key] = src[key]
            else:
                # if the item was not already in dest, add it from src
                dest[key] = src[key]

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
        for _ in as_filtered_list(
                control.props,
                lambda p: strip_lower_equals(p.name, 'status') and strip_lower_equals(p.value, 'withdrawn')):
            return True
        return False

    @staticmethod
    def _setparam_values_as_str(set_param: comp.SetParameter) -> str:
        """Convert values to string."""
        out_str = ''
        for value in as_list(set_param.values):
            value_str = string_from_root(value)
            if value_str:
                if out_str:
                    out_str += ', '
                out_str += value_str
        return out_str

    @staticmethod
    def _param_values_as_str_list(param: common.Parameter) -> List[str]:
        """Convert param values to list of strings."""
        return [val.__root__ for val in as_list(param.values)]

    @staticmethod
    def _param_values_as_str(param: common.Parameter, brackets=False) -> Optional[str]:
        """Convert param values to string with optional brackets."""
        if not param.values:
            return None
        values_str = ', '.join(ControlInterface._param_values_as_str_list(param))
        return f'[{values_str}]' if brackets else values_str

    @staticmethod
    def _param_selection_as_str(param: common.Parameter, verbose=False, brackets=False) -> str:
        """Convert parameter selection to str."""
        if param.select and param.select.choice:
            how_many_str = ''
            if param.select.how_many:
                how_many_str = 'one' if param.select.how_many == common.HowMany.one else 'one or more'
            choices_str = '; '.join(as_list(param.select.choice))
            choices_str = f'[{choices_str}]' if brackets else choices_str
            choices_str = f'Selection ({how_many_str}): {choices_str}' if verbose else choices_str
            return choices_str
        return ''

    @staticmethod
    def _param_label_choices_as_str(param: common.Parameter, verbose=False, brackets=False) -> str:
        """Convert param label or choices to string, using choices if present."""
        choices = ControlInterface._param_selection_as_str(param, verbose, brackets)
        text = choices if choices else param.label
        text = text if text else param.id
        return text

    @staticmethod
    def _param_values_assignment_str(param: common.Parameter) -> str:
        """Convert param label or choices to string, using choices if present."""
        choices = ControlInterface._param_selection_as_str(param, True, False)
        if choices:
            text = f'[{choices}]'
        elif param.label:
            text = f'[Assignment: {param.label}]'
        else:
            text = param.id
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
            param: the parameter to convert
            param_rep: how to represent the parameter
            verbose: provide verbose text for selection choices
            brackets: add brackets around the lists of items
            params_format: a string containing a single dot that represents a form of highlighting around the param

        Returns:
            formatted string or None
        """
        param_str = None
        if param_rep == ParameterRep.VALUE_OR_STRING_NONE:
            param_str = ControlInterface._param_values_as_str(param)
            param_str = param_str if param_str else 'None'
        elif param_rep == ParameterRep.LABEL_OR_CHOICES:
            param_str = ControlInterface._param_label_choices_as_str(param, verbose, brackets)
        elif param_rep == ParameterRep.VALUE_OR_LABEL_OR_CHOICES:
            param_str = ControlInterface._param_values_as_str(param)
            if not param_str:
                param_str = ControlInterface._param_label_choices_as_str(param, verbose, brackets)
        elif param_rep == ParameterRep.VALUE_OR_EMPTY_STRING:
            param_str = ControlInterface._param_values_as_str(param, brackets)
            if not param_str:
                param_str = ''
        elif param_rep == ParameterRep.ASSIGNMENT_FORM:
            param_str = ControlInterface._param_values_assignment_str(param)
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
    def get_control_param_dict(
        control: cat.Control,
        values_only: bool,
    ) -> Dict[str, common.Parameter]:
        """
        Create mapping of param id's to params for params in the control.

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
    def _replace_ids_with_text(prose: str, param_rep: ParameterRep, param_dict: Dict[str, common.Parameter]) -> str:
        """Find all instances of param_ids in prose and replace each with corresponding parameter representation.

        Need to check all values in dict for a match
        Reject matches where the string has an adjacent alphanumeric char: param_1 and param_10 or aparam_1
        """
        for param in param_dict.values():
            if param.id not in prose:
                continue
            # create the replacement text for the param_id
            param_str = ControlInterface.param_to_str(param, param_rep)
            # non-capturing groups are odd in re.sub so capture all 3 groups and replace the middle one
            pattern = r'(^|[^a-zA-Z0-9_])' + param.id + r'($|[^a-zA-Z0-9_])'
            prose = re.sub(pattern, r'\1' + param_str + r'\2', prose)
        return prose

    @staticmethod
    def _replace_params(
        text: str,
        param_dict: Dict[str, common.Parameter],
        params_format: Optional[str] = None,
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES,
        show_value_warnings: bool = False
    ) -> str:
        """
        Replace params found in moustaches with values from the param_dict.

        A single line of prose may contain multiple moustaches.
        """
        # first check if there are any moustache patterns in the text
        if param_rep == ParameterRep.LEAVE_MOUSTACHE:
            return text
        orig_text = text
        staches: List[str] = re.findall(r'{{.*?}}', text)
        if not staches:
            return text
        # now have list of all staches including braces, e.g. ['{{foo}}', '{{bar}}']
        # clean the staches so they just have the param ids
        param_ids = []
        for stache in staches:
            # remove braces so these are just param_ids but may have extra chars
            stache_contents = stache[2:(-2)]
            param_id = stache_contents.replace('insert: param,', '').strip()
            param_ids.append(param_id)

        # now replace original stache text with param values
        for i, _ in enumerate(staches):
            # A moustache may refer to a param_id not listed in the control's params
            if param_ids[i] not in param_dict:
                if show_value_warnings:
                    logger.warning(f'Control prose references param {param_ids[i]} not set in the control: {staches}')
            elif param_dict[param_ids[i]] is not None:
                param = param_dict[param_ids[i]]
                param_str = ControlInterface.param_to_str(param, param_rep, False, False, params_format)
                text = text.replace(staches[i], param_str, 1).strip()
                if show_value_warnings and param_rep != ParameterRep.LABEL_OR_CHOICES and not param.values:
                    logger.warning(f'Parameter {param_id} has no values and was referenced by prose.')
            elif show_value_warnings:
                logger.warning(f'Control prose references param {param_ids[i]} with no specified value.')
        # there may be staches remaining that we can't replace if not in param_dict
        if text != orig_text:
            while True:
                new_text = ControlInterface._replace_params(
                    text, param_dict, params_format, param_rep, show_value_warnings
                )
                if new_text == text:
                    break
                text = new_text
        return text

    @staticmethod
    def _replace_part_prose(
        control: cat.Control,
        part: common.Part,
        param_dict: Dict[str, common.Parameter],
        params_format: Optional[str] = None,
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES,
        show_value_warnings: bool = False
    ) -> None:
        """Replace the part prose according to set_param."""
        if part.prose is not None:
            fixed_prose = ControlInterface._replace_params(
                part.prose, param_dict, params_format, param_rep, show_value_warnings
            )
            # change the prose in the control itself
            part.prose = fixed_prose
        for prt in as_list(part.parts):
            ControlInterface._replace_part_prose(
                control, prt, param_dict, params_format, param_rep, show_value_warnings
            )
        for sub_control in as_list(control.controls):
            for prt in as_list(sub_control.parts):
                ControlInterface._replace_part_prose(
                    sub_control, prt, param_dict, params_format, param_rep, show_value_warnings
                )

    @staticmethod
    def _replace_param_choices(
        param: common.Parameter,
        param_dict: Dict[str, common.Parameter],
        params_format: Optional[str],
        param_rep: ParameterRep,
        show_value_warnings: bool
    ) -> None:
        """Set values for all choices param that refer to params with values."""
        if param.select:
            new_choices: List[str] = []
            for choice in as_list(param.select.choice):
                new_choice = ControlInterface._replace_params(
                    choice, param_dict, params_format, param_rep, show_value_warnings
                )
                new_choices.append(new_choice)
            param.select.choice = new_choices

    @staticmethod
    def replace_control_prose(
        control: cat.Control,
        param_dict: Dict[str, common.Parameter],
        params_format: Optional[str] = None,
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES,
        show_value_warnings: bool = False
    ) -> None:
        """Replace the control prose according to set_param."""
        for param in as_list(control.params):
            ControlInterface._replace_param_choices(param, param_dict, params_format, param_rep, show_value_warnings)
        for part in as_list(control.parts):
            if part.prose is not None:
                fixed_prose = ControlInterface._replace_params(
                    part.prose, param_dict, params_format, param_rep, show_value_warnings
                )
                # change the prose in the control itself
                part.prose = fixed_prose
            for prt in as_list(part.parts):
                ControlInterface._replace_part_prose(
                    control, prt, param_dict, params_format, param_rep, show_value_warnings
                )

    @staticmethod
    def bad_header(header: str) -> bool:
        """Return true if header format is bad."""
        if not header or header[0] != '#':
            return True
        n = len(header)
        if n < 2:
            return True
        for ii in range(1, n):
            if header[ii] == ' ':
                return False
            if header[ii] != '#':
                return True
        return True

    @staticmethod
    def get_component_by_name(comp_def: comp.ComponentDefinition, comp_name: str) -> Optional[comp.DefinedComponent]:
        """Get the component with this name from the comp_def."""
        for sub_comp in as_list(comp_def.components):
            if sub_comp.title == comp_name:
                return sub_comp
        return None

    @staticmethod
    def get_control_imp_reqs(control_imp: Optional[comp.ControlImplementation],
                             control_id: str) -> List[comp.ImplementedRequirement]:
        """Get the imp_reqs for this control from the control implementation."""
        if control_imp is None:
            return []
        return as_filtered_list(control_imp.implemented_requirements, lambda imp_req: imp_req.control_id == control_id)

    @staticmethod
    def get_status_from_props(item: TypeWithProps) -> common.ImplementationStatus:
        """Get the status of an item from its props."""
        status = common.ImplementationStatus(state=const.STATUS_PLANNED)
        for prop in as_list(item.props):
            if prop.name == const.IMPLEMENTATION_STATUS:
                status = ControlInterface._prop_as_status(prop)
                break
        return status

    @staticmethod
    def _status_as_prop(status: common.ImplementationStatus) -> common.Property:
        """Convert status to property."""
        return common.Property(name=const.IMPLEMENTATION_STATUS, value=status.state, remarks=status.remarks)

    @staticmethod
    def _prop_as_status(prop: common.Property) -> common.ImplementationStatus:
        """Convert property to status."""
        return common.ImplementationStatus(state=prop.value, remarks=prop.remarks)

    @staticmethod
    def insert_status_in_props(item: TypeWithProps, status: common.ImplementationStatus) -> None:
        """Insert status content into props of the item."""
        prop = ControlInterface._status_as_prop(status)
        ControlInterface._replace_prop(item, prop)

    @staticmethod
    def _copy_status_in_props(dest: TypeWithProps, src: TypeWithProps) -> None:
        """Copy status in props from one object to another."""
        status = ControlInterface.get_status_from_props(src)
        ControlInterface.insert_status_in_props(dest, status)

    @staticmethod
    def insert_imp_req_into_component(
        component: comp.DefinedComponent, new_imp_req: comp.ImplementedRequirement
    ) -> None:
        """Insert imp req into component by matching control id to existing imp req."""
        for control_imp in as_list(component.control_implementations):
            for imp_req in as_list(control_imp.implemented_requirements):
                if imp_req.control_id == new_imp_req.control_id:
                    status = ControlInterface.get_status_from_props(new_imp_req)
                    ControlInterface.insert_status_in_props(imp_req, status)
                    imp_req.description = new_imp_req.description
                    statement_dict = {stat.statement_id: stat for stat in as_list(imp_req.statements)}
                    new_statements: List[comp.Statement] = []
                    for statement in as_list(new_imp_req.statements):
                        # get the original version of the statement if available, or use new one
                        stat = statement_dict.get(statement.statement_id, statement)
                        # update the description and status from markdown
                        stat.description = statement.description
                        ControlInterface._copy_status_in_props(stat, statement)
                        new_statements.append(stat)
                    imp_req.statements = none_if_empty(new_statements)
                    return
        # need to insert new imp_req into an available control_imp, so choose first one and make it if needed
        if not component.control_implementations:
            component.control_implementations = [
                comp.ControlImplementation(uuid=str(uuid4()), source=const.REPLACE_ME, description=const.REPLACE_ME)
            ]
        imp_reqs = as_list(component.control_implementations[0].implemented_requirements)
        imp_reqs.append(new_imp_req)
        component.control_implementations[0].implemented_requirements = imp_reqs
