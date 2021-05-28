# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Create ssp from catalog and profile."""

import pathlib
from typing import Dict, List, Set

from mdutils.mdutils import MdUtils

import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof


class ControlHandle():
    """Convenience class for handling controls as member of a group."""

    def __init__(self, group_id: str, group_title: str, control: cat.Control):
        """Initialize the control handle."""
        self.group_id = group_id
        self.group_title = group_title
        self.control = control


class SSPGenerator():
    """Create SSP from Catalog and Profile."""

    def __init__(self) -> None:
        """Initialize the class."""
        pass

    def _replace_params(self, text: str, control: cat.Control) -> str:
        # replace params with assignments
        if control.params is not None:
            for param in control.params:
                if param.select is not None:
                    if param.select.how_many is not None:
                        selection = f'*[Selection ({param.select.how_many}): '
                    else:
                        selection = '*[Selection: '
                    text = text.replace(param.id, selection + ', '.join(param.select.choice) + ']*')
                else:
                    text = text.replace(param.id, '*[Assignment: ' + param.label + ']*')

        # strip {{ }}
        text = text.replace(' {{', '').replace(' }}', '').replace('insert: param, ', '')

        return text

    def _get_part(self, md_file: MdUtils, control: cat.Control, part: cat.Part):
        items = []
        if part.prose is not None:
            fixed_prose = self._replace_params(part.prose, control)
            prefix = ''
            if part.props is not None:
                for prop in part.props:
                    if prop.name == 'label':
                        prefix = (prop.value + ' ')
            items.append(f'{prefix}{fixed_prose}')
        if part.parts is not None:
            sub_list = []
            for prt in part.parts:
                sub_list.append(self._get_part(md_file, control, prt))
            items.append(sub_list)
        return items

    def _dump_parts(self, md_file: MdUtils, control: cat.Control):
        items = []
        for part in control.parts:
            if part.name != 'guidance':
                items.append(self._get_part(md_file, control, part))
        md_file.new_list(items, marked_with='')

    def _get_guidance(self, control: cat.Control):
        for part in control.parts:
            if part.name == 'guidance':
                return part.prose

    def _add_controls(self, control_handle: ControlHandle,
                      control_dict: Dict[str, ControlHandle]) -> Dict[str, ControlHandle]:
        control_dict[control_handle.control.id] = control_handle
        if control_handle.control.controls is not None:
            group_id = control_handle.group_id
            group_title = control_handle.group_title
            for sub_control in control_handle.control.controls:
                control_handle = ControlHandle(group_id, group_title, sub_control)
                control_dict = self._add_controls(control_handle, control_dict)
        return control_dict

    def _dump_control(self, dest_path: pathlib.Path, control: cat.Control, group_title: str) -> None:
        control_file = (dest_path / control.id).with_suffix('.md')
        md_file = MdUtils(file_name=str(control_file))

        md_file.write('<!-- yaml \n' + 'REPLACE_ME' + '\nyaml -->\n')
        md_file.new_header(level=1, title=f'{control.id} - {group_title} {control.title}')
        md_file.new_header(level=2, title='Control Description')

        self._dump_parts(md_file, control)
        guidance = self._get_guidance(control)
        if guidance is not None:
            md_file.new_header(level=3, title='Prime Guidance')
            md_file.new_paragraph(guidance)

        md_file.create_md_file()

    def generate_ssp(self, catalog: cat.Catalog, profile: prof.Profile, md_path: pathlib.Path) -> int:
        """Generate ssp from catalog and profile."""
        control_dict: Dict[str, ControlHandle] = {}
        for group in catalog.groups:
            for control in group.controls:
                control_handle = ControlHandle(group.id, group.title, control)
                control_dict = self._add_controls(control_handle, control_dict)

        control_ids: List[str] = []
        for _import in profile.imports:
            for include_control in _import.include_controls:
                control_ids.extend(include_control.with_ids)

        needed_group_ids: Set[str] = set()
        needed_controls: List[ControlHandle] = []

        for control_id in control_ids:
            control_handle = control_dict[control_id]
            needed_group_ids.add(control_handle.group_id)
            needed_controls.append(control_handle)

        for group_id in needed_group_ids:
            (md_path / group_id).mkdir(exist_ok=True)

        for control_handle in needed_controls:
            out_path = md_path / control_handle.group_id
            self._dump_control(out_path, control_handle.control, control_handle.group_title)

        return 0
