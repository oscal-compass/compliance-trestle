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
from typing import Dict, List, Optional, Set, Union

import trestle.core.generators as gens
import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.markdown_validator import MarkdownValidator
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


class SSPGenerate(AuthorCommonCommand):
    """Generate SSP in markdown form from Catalog and Profile."""

    name = 'ssp-generate'

    def _init_arguments(self) -> None:
        file_help_str = 'Name of the profile model in the trestle workspace'
        self.add_argument('-p', '--profile', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated ssp markdown folder'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        verbose_help_str = 'Display verbose output'
        self.add_argument('-v', '--verbose', help=verbose_help_str, required=False, action='count', default=0)
        yaml_help_str = 'Path to the yaml header file'
        self.add_argument('-y', '--yaml-header', help=yaml_help_str, required=True, type=str)
        sections_help_str = 'Comma separated list of section:alias pairs for sections to output'
        self.add_argument('-s', '--sections', help=sections_help_str, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = fs.get_trestle_project_root(pathlib.Path.cwd())
        if not trestle_root:
            logger.warning(f'Current working directory {pathlib.Path.cwd()} is not with a trestle project.')
            return 1
        if not fs.allowed_task_name(args.output):
            logger.warning(f'{args.output} is not an allowed directory name')
            return 1

        profile: prof.Profile
        _, _, profile = load_distributed(pathlib.Path(f'profiles/{args.profile}/profile.json'))
        cat_href = profile.imports[0].href
        cat_name = fs.model_name_from_href_str(cat_href)

        _, _, catalog = load_distributed(pathlib.Path(f'catalogs/{cat_name}/catalog.json'))

        try:
            logging.debug(f'Loading yaml header file {args.yaml_header}')
            yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'), yaml.FullLoader)
        except yaml.YAMLError as e:
            logging.warning(f'YAML error loading yaml header for ssp generation: {e}')
            return 1
        markdown_path = trestle_root / args.output

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

        ssp_manager = SSPManager()

        return ssp_manager.generate_ssp(catalog, profile, markdown_path, sections, yaml_header)


class SSPAssemble(AuthorCommonCommand):
    """Assemble SSP in json format from a directory of markdown files."""

    name = 'ssp-assemble'

    def _init_arguments(self) -> None:
        file_help_str = 'Name of the input markdown file directory'
        self.add_argument('-m', '--markdown', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json SSP'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        verbose_help_str = 'Display verbose output'
        self.add_argument('-v', '--verbose', help=verbose_help_str, required=False, action='count', default=0)

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = fs.get_trestle_project_root(pathlib.Path.cwd())
        if not trestle_root:
            logger.warning(f'Current working directory {pathlib.Path.cwd()} is not with a trestle project.')
            return 1

        ssp_manager = SSPManager()
        return ssp_manager.assemble_ssp(args.markdown, args.output)


class SSPManager():
    """Manage generation of SSP in markdown format from profile+catalog, then assembly into json format SSP."""

    def __init__(self):
        """Initialize the class."""
        self._param_dict: Dict[str, str] = None
        self._md_file: MDWriter = None
        self._alters: List[prof.Alter] = None
        self._yaml_header: dict = None
        self._sections: Dict[str, str] = None

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

    def _get_part(self, control: cat.Control, part: cat.Part) -> List[Union[str, List[str]]]:
        items = []
        if part.prose is not None:
            fixed_prose = self._replace_params(part.prose, control, self._param_dict)
            label = self._get_label(part)
            pad = '' if label == '' else ' '
            items.append(f'{label}{pad}{fixed_prose}')
        if part.parts is not None:
            sub_list = []
            for prt in part.parts:
                sub_list.extend(self._get_part(control, prt))
            sub_list.append('')
            items.append(sub_list)
        return items

    def _add_parts(self, control: cat.Control) -> None:
        items = []
        for part in control.parts:
            if part.name == 'statement':
                items.append(self._get_part(control, part))
        # unwrap the list if it is many levels deep
        while not isinstance(items, str) and len(items) == 1:
            items = items[0]
        self._md_file.new_list(items)

    def _get_controls(self, control_handle: ControlHandle,
                      control_dict: Dict[str, ControlHandle]) -> Dict[str, ControlHandle]:
        control_dict[control_handle.control.id] = control_handle
        if control_handle.control.controls is not None:
            group_id = control_handle.group_id
            group_title = control_handle.group_title
            for sub_control in control_handle.control.controls:
                control_handle = ControlHandle(group_id, group_title, sub_control)
                control_dict = self._get_controls(control_handle, control_dict)
        return control_dict

    def _add_yaml_header(self) -> None:
        self._md_file.add_yaml_header(self._yaml_header)

    def _add_control_description(self, control_handle: ControlHandle) -> None:
        self._md_file.new_paragraph()
        title = f'{control_handle.control.id} - {control_handle.group_title} {control_handle.control.title}'
        self._md_file.new_header(level=1, title=title)
        self._md_file.new_header(level=2, title='Control Description')
        self._md_file.set_indent_level(-2)
        self._add_parts(control_handle.control)
        self._md_file.set_indent_level(0)

    def _get_control_section(self, control: cat.Control, section: str) -> Optional[str]:
        for alter in self._alters:
            if alter.control_id == control.id:
                if alter.adds is not None:
                    for add in alter.adds:
                        if add.parts is not None:
                            for part in add.parts:
                                if part.name == section:
                                    return part.prose
        return None

    def _add_control_section(self, control: cat.Control, section_tuple: str) -> None:
        prose = self._get_control_section(control, section_tuple[0])
        if prose is not None:
            self._md_file.new_paragraph()
            self._md_file.new_header(level=2, title=f'{control.id} Section {section_tuple[1]}')
            self._md_file.new_paragraph()
            self._md_file.new_line(prose)
            self._md_file.new_paragraph()

    def _add_response(self, control: cat.Control) -> None:
        self._md_file.new_paragraph()
        self._md_file.new_header(level=2, title=f'{control.id} What is the solution and how is it implemented?')

        for part in control.parts:
            if part.parts is not None:
                if part.name == 'statement':
                    for prt in part.parts:
                        self._md_file.new_paragraph()
                        self._md_file.new_hr()
                        self._md_file.new_header(level=3, title=f'Part {self._get_label(prt)}')
                        self._md_file.new_paragraph()
                        self._md_file.new_line('Add control implementation description here.')
                        self._md_file.new_paragraph()
        self._md_file.new_hr()
        self._md_file.new_paragraph()

    def _write_control(
        self,
        dest_path: pathlib.Path,
        control_handle: ControlHandle,
    ) -> None:
        control_file = dest_path / (control_handle.control.id + '.md')
        self._md_file = MDWriter(control_file)

        self._add_yaml_header()

        self._add_control_description(control_handle)

        self._add_response(control_handle.control)

        if self._sections is not None:
            for section_tuple in self._sections.items():
                self._add_control_section(control_handle.control, section_tuple)

        self._md_file.write_out()

    def generate_ssp(
        self,
        catalog: cat.Catalog,
        profile: prof.Profile,
        md_path: pathlib.Path,
        sections: Optional[Dict[str, str]],
        yaml_header: dict
    ) -> int:
        """
        Generate a partial ssp in markdown format from catalog, profile and yaml header.

        The catalog contains a list of controls and the profile selects a subset of them
        in groups.  The profile also specifies parameters for the controls.  The result
        is a directory of markdown files, one for each control in the profile.  Each control
        has the yaml header at the top.

        Args:
            catalog: An OSCAL catalog
            profile: An OSCAL profile
            md_path: The directory into which the markdown controls are written
            sections: A comma separated list of id:alias separated by colon to specify optional
                additional sections to be written out.  The id corresponds to the name found
                in the profile parts for the corresponding section, and the alias is the nicer
                version to be printed out in the section header of the markdown.
            yaml_header: The dictionary corresponding to the desired contents of the yaml header at the
                top of each markdown file.
        Returns:
            0 on success, 1 otherwise

        """
        logging.debug(
            f'Generate ssp in {md_path} from catalog {catalog.metadata.title}, profile {profile.metadata.title}'
        )
        # create the directory in which to write the control markdown files
        md_path.mkdir(exist_ok=True, parents=True)

        # build a convenience dictionary to access control handles by name
        control_dict: Dict[str, ControlHandle] = {}
        for group in catalog.groups:
            for control in group.controls:
                control_handle = ControlHandle(group.id, group.title, control)
                control_dict = self._get_controls(control_handle, control_dict)

        # get list of control_ids needed by profile
        control_ids: List[str] = []
        for _import in profile.imports:
            for include_control in _import.include_controls:
                control_ids.extend(include_control.with_ids)

        # get list of group id's and associated controls
        needed_group_ids: Set[str] = set()
        needed_controls: List[ControlHandle] = []
        for control_id in control_ids:
            control_handle = control_dict[control_id]
            needed_group_ids.add(control_handle.group_id)
            needed_controls.append(control_handle)

        # make the directories for each group
        for group_id in needed_group_ids:
            (md_path / group_id).mkdir(exist_ok=True)

        # assign values to class members for use when writing out the controls
        self._param_dict = profile.modify.set_parameters
        self._alters = profile.modify.alters
        self._yaml_header = yaml_header
        self._sections = sections

        # write out the controls
        for control_handle in needed_controls:
            out_path = md_path / control_handle.group_id
            self._write_control(out_path, control_handle)

        return 0

    def _get_implementations(self, control_file: pathlib.Path) -> List[ossp.ImplementedRequirement]:
        control_id = control_file.stem
        parse_tree = MarkdownValidator.load_markdown_parsetree(control_file)
        tree = parse_tree[0] if len(parse_tree) == 1 else parse_tree[1]
        imp_reqs: list[ossp.ImplementedRequirement] = []
        ii = 0
        while ii < len(tree):
            item = tree[ii]
            if item['type'] == 'thematic_break':
                section: str = tree[ii + 1]['children'][0]['text']
                if not section.startswith('Part '):
                    break
                text = tree[ii + 2]['children'][0]['text']
                by_comp: ossp.ByComponent = gens.generate_sample_model(ossp.ByComponent)
                by_comp.description = text
                statement: ossp.Statement = gens.generate_sample_model(ossp.Statement)
                part_label = section.split(' ')[1].replace('.', '')
                statement_label = f'{control_id}_smt.{part_label}'
                statement.by_components = {statement_label: by_comp}
                imp_req: ossp.ImplementedRequirement = gens.generate_sample_model(ossp.ImplementedRequirement)
                imp_req.control_id = control_id
                imp_req.statements = {statement_label: statement}
                imp_reqs.append(imp_req)
                ii += 2
            ii += 1
        return imp_reqs

    def assemble_ssp(self, md_name, ssp_name) -> int:
        """Assemble the markdown directory into an ssp."""
        # find all groups in the markdown dir
        group_ids = []
        trestle_root = fs.get_trestle_project_root(pathlib.Path.cwd())
        md_dir = trestle_root / md_name
        for gdir in md_dir.glob('*/'):
            group_ids.append(str(gdir.stem))
        imp_reqs: List[ossp.ImplementedRequirement] = []
        for group_id in group_ids:
            group_path = md_dir / group_id
            for control_file in group_path.glob('*.md'):
                imp_reqs.extend(self._get_implementations(control_file))
        control_imp: ossp.ControlImplementation = gens.generate_sample_model(ossp.ControlImplementation)
        control_imp.implemented_requirements = imp_reqs
        control_imp.description = 'This is the control implementation for the system.'
        ssp = gens.generate_sample_model(ossp.SystemSecurityPlan)
        ssp.control_implementation = control_imp
        import_profile: ossp.ImportProfile = gens.generate_sample_model(ossp.ImportProfile)
        import_profile.href = 'REPLACE_ME'
        ssp.import_profile = import_profile
        ssp_dir = trestle_root / ('system-security-plans/' + ssp_name)
        ssp_dir.mkdir(exist_ok=True, parents=True)
        ssp.oscal_write(ssp_dir / 'system-security-plan.json')
        return 0
