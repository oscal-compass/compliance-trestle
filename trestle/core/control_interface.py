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
import pathlib
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import trestle.oscal.catalog as cat
from trestle.common import const
from trestle.common.common_types import TypeWithProps
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_list
from trestle.core.trestle_base_model import TrestleBaseModel
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


class ComponentImpInfo(TrestleBaseModel):
    """Class to capture component prose and status."""

    prose: str
    implementation_status = const.STATUS_TRESTLE_UNKNOWN
    remarks: Optional[str]


# define the type
CompDict = Dict[str, Dict[str, ComponentImpInfo]]


class ContextPurpose(Enum):
    """Specify the modality of the control markdown."""

    CATALOG = 0
    COMPONENT = 1
    PROFILE = 2
    SSP = 3


class ControlContext(TrestleBaseModel):
    """Class encapsulating control markdown usage."""

    purpose: ContextPurpose
    to_markdown: bool
    trestle_root: pathlib.Path
    md_root: pathlib.Path
    yaml_header: Optional[Dict[Any, Any]] = None
    sections_dict: Optional[Dict[str, str]] = None
    prompt_responses = False
    additional_content = False
    profile: Optional[prof.Profile] = None
    overwrite_header_values = False
    set_parameters = False
    required_sections: Optional[List[str]] = None
    allowed_sections: Optional[List[str]] = None
    comp_def: Optional[comp.ComponentDefinition] = None
    comp_name: Optional[str] = None

    @classmethod
    def generate(
        cls,
        purpose: ContextPurpose,
        to_markdown: bool,
        trestle_root: pathlib.Path,
        md_root: pathlib.Path,
        yaml_header: Optional[Dict[Any, Any]] = None,
        sections_dict: Optional[Dict[str, str]] = None,
        prompt_responses=False,
        additional_content=False,
        profile: Optional[prof.Profile] = None,
        overwrite_header_values=False,
        set_parameters=False,
        required_sections: Optional[List[str]] = None,
        allowed_sections: Optional[List[str]] = None,
        comp_def: Optional[comp.ComponentDefinition] = None,
        comp_name: Optional[str] = None
    ) -> ControlContext:
        """Generate control context of the needed type."""
        context = cls(
            purpose=purpose,
            to_markdown=to_markdown,
            trestle_root=trestle_root,
            md_root=md_root,
            yaml_header=yaml_header,
            sections_dict=sections_dict,
            prompt_responses=prompt_responses,
            additional_content=additional_content,
            profile=profile,
            overwrite_header_values=overwrite_header_values,
            set_parameters=set_parameters,
            required_sections=required_sections,
            allowed_sections=allowed_sections,
            comp_def=comp_def,
            comp_name=comp_name
        )
        if purpose == ContextPurpose.CATALOG:
            context.comp_name = 'foo'
        elif purpose == ContextPurpose.PROFILE:
            context.comp_name = 'bar'
        return context


class ControlInterface():
    """Class to interact with controls in memory."""

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
    def get_prop(part_control: TypeWithProps, prop_name: str, default: Optional[str] = None) -> str:
        """Get the property with that name or return empty string."""
        for prop in as_list(part_control.props):
            if prop.name.strip().lower() == prop_name.strip().lower():
                return prop.value.strip()
        return default if default else ''

    @staticmethod
    def get_sort_id(control: cat.Control, allow_none=False) -> Optional[str]:
        """Get the sort-id for the control."""
        for prop in as_list(control.props):
            if prop.name == const.SORT_ID:
                return prop.value.strip()
        return None if allow_none else control.id

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
    def get_label(part_control: TypeWithProps) -> str:
        """Get the label from the props of a part or control."""
        return ControlInterface.get_prop(part_control, 'label')

    @staticmethod
    def get_part(part: common.Part, item_type: str, skip_id: Optional[str]) -> List[Union[str, List[str]]]:
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
    def get_adds(control_id: str, profile: prof.Profile) -> List[Tuple[str, str]]:
        """Get the adds for a control from a profile by control id."""
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
    def _get_control_section_prose(control: cat.Control, section_name: str) -> str:
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
    def get_section(control: cat.Control, skip_section_list: List[str]) -> Tuple[str, str, str, str]:
        """Get sections that are not in the list."""
        id_, name, title = ControlInterface._find_section(control, skip_section_list)
        if id_:
            return id_, name, title, ControlInterface._get_control_section_prose(control, name)
        return '', '', '', ''

    @staticmethod
    def get_part_prose(control: cat.Control, part_name: str) -> str:
        """Get the prose for a named part."""
        prose = ''
        if control.parts:
            for part in control.parts:
                prose += ControlInterface._get_control_section_part(part, part_name)
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
                    ControlInterface.merge_dicts_deep(dest[key], src[key], overwrite_header_values)
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
        for prop in as_list(control.props):
            if prop.name and prop.value:
                if prop.name.lower().strip() == 'status' and prop.value.lower().strip() == 'withdrawn':
                    return True
        return False
