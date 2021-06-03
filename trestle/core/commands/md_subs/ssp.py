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

import argparse
import logging
import pathlib
from typing import Dict, List, Set, Union

import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.utils.load_distributed import load_distributed
from trestle.utils.md_writer import MDWriter

import yaml

logger = logging.getLogger(__name__)


class ControlHandle():
    """Convenience class for handling controls as member of a group."""

    def __init__(self, group_id: str, group_title: str, control: cat.Control):
        """Initialize the control handle."""
        self.group_id = group_id
        self.group_title = group_title
        self.control = control


class SSP(CommandPlusDocs):
    """Create SSP in markdown form from Catalog and Profile."""

    name = 'ssp'

    def _init_arguments(self) -> None:
        cat_help_str = 'Name of the catalog file'
        self.add_argument('-f', '--file', help=cat_help_str, required=True, type=str)
        prof_help_str = 'Name of the profile file'
        self.add_argument('-p', '--profile', help=prof_help_str, required=True, type=str)
        yaml_help_str = 'Path to the yaml header file'
        self.add_argument('-yh', '--yaml-header', help=yaml_help_str, required=True, type=str)
        sections_help_str = 'Comma separated list of section:alias pairs for sections to output'
        self.add_argument('-s', '--sections', help=sections_help_str, required=False, type=str)
        task_help_str = 'Name of the generated ssp markdown folder'
        self.add_argument('-o', '--output', help=task_help_str, required=True, type=str)
        verbose_help_str = 'Display verbose output'
        self.add_argument('-v', '--verbose', help=verbose_help_str, required=False, action='count', default=0)

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = fs.get_trestle_project_root(pathlib.Path.cwd())
        if not trestle_root:
            logger.warning(f'Current working directory {pathlib.Path.cwd()} is not with a trestle project.')
            return 1
        if not fs.allowed_task_name(args.output):
            logger.warning(
                f'Task name {args.output} is invalid as it interferes with OSCAL and trestle reserved names.'
            )
            return 1
        _, _, catalog = load_distributed(pathlib.Path(f'catalogs/{args.file}/catalog.json'))
        _, _, profile = load_distributed(pathlib.Path(f'profiles/{args.profile}/profile.json'))

        try:
            logging.debug(f'Loading yaml header file {args.yaml_header}')
            yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'), yaml.FullLoader)
        except yaml.YAMLError as e:
            logging.warning(f'YAML error loading yaml header for ssp generation: {e}')
            return 1
        markdown_path = trestle_root / ('md/' + args.output)

        sections = None
        if args.sections is not None:
            section_tuples = args.sections.strip("'").split(',')
            sections = {}
            for section in section_tuples:
                if ':' in section:
                    s = section.split(':')
                    sections[s[0]] = s[1]
                else:
                    sections[section] = section

        return self.generate_ssp(catalog, profile, markdown_path, sections, yaml_header)

    def _replace_params(self, text: str, control: cat.Control, param_dict: Dict[str, prof.SetParameter]) -> str:
        # replace params with assignments from the profile
        if control.params is not None:
            for param in control.params:
                set_param = param_dict.get(param.id, None)
                if set_param is not None:
                    text = text.replace(param.id, str(set_param.values[0].__root__))

        # strip {{ }}
        text = text.replace(' {{', '').replace(' }}', '').replace('insert: param, ', '').strip()

        return text

    def _get_label(self, part: cat.Part) -> str:
        if part.props is not None:
            for prop in part.props:
                if prop.name == 'label':
                    return prop.value.strip()
        return ''

    def _get_part(
        self, md_file: MDWriter, control: cat.Control, part: cat.Part, param_dict: Dict[str, prof.SetParameter]
    ):
        items = []
        if part.prose is not None:
            fixed_prose = self._replace_params(part.prose, control, param_dict)
            label = self._get_label(part)
            pad = '' if label == '' else ' '
            items.append(f'{label}{pad}{fixed_prose}')
        if part.parts is not None:
            sub_list = []
            for prt in part.parts:
                sub_list.extend(self._get_part(md_file, control, prt, param_dict))
            sub_list.append('')
            items.append(sub_list)
        return items

    def _add_parts(self, md_file: MDWriter, control: cat.Control, param_dict: Dict[str, prof.SetParameter]):
        items = []
        for part in control.parts:
            if part.name == 'statement':
                items.append(self._get_part(md_file, control, part, param_dict))
        # unwrap the list if it is many levels deep
        while not isinstance(items, str) and len(items) == 1:
            items = items[0]
        md_file.new_list(items)

    def _get_named_prose_from_part(self, part: cat.Part, name: str) -> str:
        if part.name == name:
            return part.prose
        if part.parts is not None:
            for prt in part.parts:
                prose = self._get_named_prose_from_part(prt, name)
                if prose is not None:
                    return prose.strip()
        return None

    def _get_named_prose(self, parts: List[cat.Part], name: str) -> str:
        for part in parts:
            prose = self._get_named_prose_from_part(part, name)
            if prose is not None:
                return prose.strip()

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

    def _add_yaml_header(self, md_file: MDWriter, yaml_header: dict) -> None:
        md_file.add_yaml_header(yaml_header)

    def _add_control_description(
        self, md_file: MDWriter, control: cat.Control, group_title: str, param_dict: Dict[str, prof.SetParameter]
    ) -> None:
        md_file.new_paragraph()
        md_file.new_header(level=1, title=f'{control.id} - {group_title} {control.title}')
        md_file.new_header(level=2, title='Control Description')
        md_file.set_indent_level(-1)
        self._add_parts(md_file, control, param_dict)
        md_file.set_indent_level(0)

    def _get_control_section(self, control: cat.Control, section: str, alters: List[prof.Alter]) -> None:
        for alter in alters:
            if alter.control_id == control.id:
                if alter.adds is not None:
                    for add in alter.adds:
                        if add.parts is not None:
                            for part in add.parts:
                                if part.name == section:
                                    return part.prose
        return None

    def _add_control_section(
        self, md_file: MDWriter, control: cat.Control, section_tuple: str, alters: List[prof.Alter]
    ) -> None:
        prose = self._get_control_section(control, section_tuple[0], alters)
        if prose is not None:
            md_file.new_paragraph()
            md_file.new_header(level=2, title=f'{control.id} Section {section_tuple[1]}')
            md_file.new_paragraph()
            md_file.new_line(prose)
            md_file.new_paragraph()

    def _add_response(self, md_file: MDWriter, control: cat.Control) -> None:
        md_file.new_paragraph()
        md_file.new_header(level=2, title=f'{control.id} What is the solution and how is it implemented?')

        for part in control.parts:
            if part.parts is not None:
                if part.name == 'statement':
                    for prt in part.parts:
                        md_file.new_paragraph()
                        md_file.new_hr()
                        md_file.new_header(level=3, title=f'Part {self._get_label(prt)}')
                        md_file.new_paragraph()
                        md_file.new_line('Add control implementation description here.')
                        md_file.new_paragraph()
        md_file.new_hr()
        md_file.new_paragraph()

    def _add_control(
        self,
        dest_path: pathlib.Path,
        control: cat.Control,
        group_title: str,
        param_dict: Dict[str, prof.SetParameter],
        sections: Union[List[str], None],
        alters: List[prof.Alter],
        yaml_header: dict
    ) -> None:
        control_file = dest_path / (control.id + '.md')
        md_file = MDWriter(control_file)

        self._add_yaml_header(md_file, yaml_header)

        self._add_control_description(md_file, control, group_title, param_dict)

        self._add_response(md_file, control)

        if sections is not None:
            for section_tuple in sections.items():
                self._add_control_section(md_file, control, section_tuple, alters)

        md_file.write_out()

    def generate_ssp(
        self,
        catalog: cat.Catalog,
        profile: prof.Profile,
        md_path: pathlib.Path,
        sections: Union[Dict[str, str], None],
        yaml_header: dict
    ) -> int:
        """Generate ssp from catalog and profile."""
        logging.debug(
            f'Generate ssp in {md_path} from catalog {catalog.metadata.title}, profile {profile.metadata.title}'
        )
        md_path.mkdir(exist_ok=True, parents=True)
        control_dict: Dict[str, ControlHandle] = {}
        for group in catalog.groups:
            for control in group.controls:
                control_handle = ControlHandle(group.id, group.title, control)
                control_dict = self._add_controls(control_handle, control_dict)

        # get list of control_ids needed by profile
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

        # now get list of param substitution values
        param_dict = profile.modify.set_parameters

        for control_handle in needed_controls:
            out_path = md_path / control_handle.group_id
            alters = profile.modify.alters
            self._add_control(
                out_path, control_handle.control, control_handle.group_title, param_dict, sections, alters, yaml_header
            )

        return 0
