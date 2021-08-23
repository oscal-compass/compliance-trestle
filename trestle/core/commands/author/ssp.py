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
import string
from typing import Any, Dict, List, Optional, Tuple, Union

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.core.generators as gens
import trestle.oscal.catalog as cat
import trestle.oscal.common as common
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core.catalog_resolver import CatalogInterface, CatalogResolver
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.markdown_validator import MarkdownValidator
from trestle.utils.md_writer import MDWriter

logger = logging.getLogger(__name__)


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
        yaml_help_str = 'Path to the optional yaml header file'
        self.add_argument('-y', '--yaml-header', help=yaml_help_str, required=False, type=str)
        sections_help_str = 'Comma separated list of section:alias pairs for sections to output'
        self.add_argument('-s', '--sections', help=sections_help_str, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = args.trestle_root
        if not fs.allowed_task_name(args.output):
            logger.warning(f'{args.output} is not an allowed directory name')
            return 1

        profile_path = pathlib.Path(f'profiles/{args.profile}/profile.json')

        yaml_header: dict = {}
        if 'yaml_header' in args and args.yaml_header is not None:
            try:
                logging.debug(f'Loading yaml header file {args.yaml_header}')
                yaml = YAML(typ='safe')
                yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'))
            except YAMLError as e:
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

        return ssp_manager.generate_ssp(trestle_root, profile_path.resolve(), markdown_path, sections, yaml_header)


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
        return ssp_manager.assemble_ssp(args.markdown, args.output, False)


class SSPManager():
    """Manage generation of SSP in markdown format from profile+catalog, then assembly into json format SSP."""

    def __init__(self):
        """Initialize the class."""
        self._param_dict: Dict[str, str] = {}
        self._md_file: Optional[MDWriter] = None
        self._alters: List[prof.Alter] = []
        self._sections: Dict[str, str] = {}

    def _wrap_label(self, label: str):
        l_side = '\['
        r_side = '\]'
        wrapped = '' if label == '' else f'{l_side}{label}{r_side}'
        return wrapped

    def _get_label(self, part: common.Part) -> str:
        if part.props is not None:
            for prop in part.props:
                if prop.name == 'label':
                    return prop.value.strip()
        return ''

    def _get_part(self, control: cat.Control, part: common.Part) -> List[Union[str, List[str]]]:
        # for a part in a control replace the params using the _param_dict
        items = []
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
        # for a given control add its parts to the md file after replacing params
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
        if yaml_header is not None:
            self._md_file.add_yaml_header(yaml_header)

    def _add_control_description(self, control: cat.Control, group_title: str) -> None:
        self._md_file.new_paragraph()
        title = f'{control.id} - {group_title} {control.title}'
        self._md_file.new_header(level=1, title=title)
        self._md_file.new_header(level=2, title='Control Description')
        self._md_file.set_indent_level(-1)
        self._add_parts(control)
        self._md_file.set_indent_level(-1)

    def _get_control_section(self, control: cat.Control, section: str) -> str:
        # look for the section text first in the control and then in the profile
        # if found in both they are appended
        prose = ''
        for part in control.parts:
            if part.name == section and part.prose is not None:
                prose += part.prose
        for alter in self._alters:
            if alter.control_id == control.id:
                for adds in alter.adds:
                    if adds.parts is not None:
                        for part in adds.parts:
                            if part.name == section and part.prose is not None:
                                prose += part.prose
        return prose

    def _add_control_section(self, control: cat.Control, section_tuple: str) -> None:
        prose = self._get_control_section(control, section_tuple[0])
        if prose:
            self._md_file.new_header(level=2, title=f'{control.id} Section {section_tuple[1]}')
            self._md_file.new_line(prose)
            self._md_file.new_paragraph()

    def _add_response(self, control: cat.Control) -> None:
        self._md_file.new_hr()
        self._md_file.new_paragraph()
        self._md_file.new_header(level=2, title=f'{control.id} What is the solution and how is it implemented?')

        for part in control.parts:
            if part.parts is not None:
                if part.name == 'statement':
                    for prt in part.parts:
                        self._md_file.new_hr()
                        self._md_file.new_header(level=3, title=f'Part {self._get_label(prt)}')
                        self._md_file.new_line(f'Add control implementation description here for statement {prt.id}')
                        self._md_file.new_paragraph()
        self._md_file.new_hr()

    def _write_control(
        self, dest_path: pathlib.Path, control: cat.Control, group_title: str, yaml_header: Optional[dict]
    ) -> None:
        control_file = dest_path / (control.id + '.md')
        self._md_file = MDWriter(control_file)

        self._add_yaml_header(yaml_header)

        self._add_control_description(control, group_title)

        self._add_response(control)

        if self._sections is not None:
            for section_tuple in self._sections.items():
                self._add_control_section(control, section_tuple)

        self._md_file.write_out()

    def generate_ssp(
        self,
        trestle_root: pathlib.Path,
        profile_path: pathlib.Path,
        md_path: pathlib.Path,
        sections: Optional[Dict[str, str]],
        yaml_header: dict
    ) -> int:
        """
        Generate a partial ssp in markdown format from a profile and yaml header.

        The catalog contains a list of controls and the profile selects a subset of them
        in groups.  The profile also specifies parameters for the controls.  The result
        is a directory of markdown files, one for each control in the profile.  Each control
        has the yaml header at the top.

        Args:
            profile_path: File path for OSCAL profile
            md_path: The directory into which the markdown controls are written
            sections: A comma separated list of id:alias separated by colon to specify optional
                additional sections to be written out.  The id corresponds to the name found
                in the profile parts for the corresponding section, and the alias is the nicer
                version to be printed out in the section header of the markdown.
            yaml_header: The dictionary corresponding to the desired contents of the yaml header at the
                top of each markdown file.  If the dict is empty no yaml header is included.
        Returns:
            0 on success, 1 otherwise

        """
        logging.debug(f'Generate ssp in {md_path} from profile {profile_path}')
        # create the directory in which to write the control markdown files
        md_path.mkdir(exist_ok=True, parents=True)

        catalog_resolver = CatalogResolver()
        resolved_catalog = catalog_resolver.get_resolved_profile_catalog(trestle_root, profile_path)
        catalog_interface = CatalogInterface(resolved_catalog)

        # write out the controls
        for control in catalog_interface.get_all_controls():
            group_id, group_title, _ = catalog_interface.get_group_info(control.id)
            out_path = md_path / group_id
            self._write_control(out_path, control, group_title, yaml_header)

        return 0

    def _get_label_prose(self, ii: int, tree: List[Dict[str, Any]]) -> Tuple[int, str, str]:
        """Find the statement label and prose in each section of the control markdown parse tree."""
        # call this repeatedly and get label prose for each part sequentially
        # this doesn't handle emphasis (e.g. bold) properly.  the direct methods below are preferred
        ntree = len(tree)
        label = ''
        prose_lines = []

        while ii < ntree:
            # look for thematic break followed by heading (Part...) and paragraph (Response statement)
            if tree[ii]['type'] == 'thematic_break':
                while ii < ntree and tree[ii]['type'] != 'heading':
                    ii += 1
                if ii >= ntree:
                    break
                # we are now on a heading line
                if 'children' in tree[ii] and 'text' in tree[ii]['children'][0]:
                    section: str = tree[ii]['children'][0]['text']
                    # find start of Part and grab label
                    if section.startswith('Part '):
                        label = section.split(' ')[-1]
                        ii += 1
                        while ii < ntree and tree[ii]['type'] != 'thematic_break':
                            if 'children' in tree[ii]:
                                children = tree[ii]['children']
                                for child in children:
                                    if 'text' in child:
                                        prose_lines.append(child['text'])
                            ii += 1
                        break
            else:
                ii += 1

        prose = '\n'.join(prose_lines)
        if not prose_lines or label == '':
            ii = -1
        return ii, label, prose

    def _strip_bad_chars(self, label: str) -> str:
        # remove chars that would cause statement regex to fail.  Just letters and digits
        allowed_chars = string.ascii_letters + string.digits
        new_label = ''
        for c in label:
            if c in allowed_chars:
                new_label += c
        return new_label

    def _get_implementations_via_tree(self, control_file: pathlib.Path,
                                      component: ossp.SystemComponent) -> List[ossp.ImplementedRequirement]:
        # get implementation requirements associated with a given control and link them to the one component we created
        control_id = control_file.stem
        parse_tree = MarkdownValidator.load_markdown_parsetree(control_file)
        tree = parse_tree[1]
        imp_reqs: list[ossp.ImplementedRequirement] = []
        ii = 0

        # keep moving down through the tree picking up labels and prose for the imp requirements
        while True:
            ii, part_label, prose = self._get_label_prose(ii, tree)
            # break at end of file
            if ii < 0:
                break
            # create a new by-component to hold this statement
            by_comp: ossp.ByComponent = gens.generate_sample_model(ossp.ByComponent)
            # link it to the one dummy component uuid
            by_comp.component_uuid = component.uuid
            # add the response prose to the description
            by_comp.description = prose
            # create a statement to hold the by-component and assign the statement id
            statement: ossp.Statement = gens.generate_sample_model(ossp.Statement)
            # strip badchars from label
            clean_label = self._strip_bad_chars(part_label)
            statement.statement_id = f'{control_id}_smt.{clean_label}'
            statement.by_components = [by_comp]
            # create a new implemented requirement linked to the control id to hold the statement
            imp_req: ossp.ImplementedRequirement = gens.generate_sample_model(ossp.ImplementedRequirement)
            imp_req.control_id = control_id
            imp_req.statements = [statement]
            imp_reqs.append(imp_req)

        return imp_reqs

    def _trim_prose_lines(self, lines: List[str]) -> str:
        # trim dead space at start and end
        ii = 0
        while lines[ii].strip(' \r\n') == '':
            ii += 1
        jj = len(lines) - 1
        while jj >= 0 and lines[jj].strip(' \r\n') == '':
            jj -= 1
        if jj < ii:
            return ''
        return '\n'.join(lines[ii:(jj + 1)])

    def _get_label_prose_direct(self, ii: int, lines: List[str]) -> str:
        # ii should point to start of file or directly at a new Part
        nlines = len(lines)
        prose_lines: List[str] = []
        part_label = ''
        while ii < nlines:
            if lines[ii].startswith('### Part'):
                part_label = lines[ii].strip().split(' ')[-1]
                ii += 1
                while ii < nlines:
                    if lines[ii].startswith('### Part') or lines[ii].startswith('---'):
                        return ii, part_label, self._trim_prose_lines(prose_lines)
                    prose_lines.append(lines[ii])
                    ii += 1
            ii += 1
        return -1, part_label, '\n'.join(prose_lines)

    def _get_implementations_direct(self, control_file: pathlib.Path,
                                    component: ossp.SystemComponent) -> List[ossp.ImplementedRequirement]:
        # get implementation requirements associated with a given control and link them to the one component we created
        control_id = control_file.stem
        imp_reqs: list[ossp.ImplementedRequirement] = []
        ii = 0
        lines: List[str] = []
        with open(control_file, 'r') as f:
            raw_lines = f.readlines()
        lines = [line.strip('\r\n') for line in raw_lines]

        # keep moving down through the tree picking up labels and prose for the imp requirements
        while True:
            ii, part_label, prose = self._get_label_prose_direct(ii, lines)
            if ii < 0:
                break
            # create a new by-component to hold this statement
            by_comp: ossp.ByComponent = gens.generate_sample_model(ossp.ByComponent)
            # link it to the one dummy component uuid
            by_comp.component_uuid = component.uuid
            # add the response prose to the description
            by_comp.description = prose
            # create a statement to hold the by-component and assign the statement id
            statement: ossp.Statement = gens.generate_sample_model(ossp.Statement)
            # strip badchars from label
            clean_label = self._strip_bad_chars(part_label)
            statement.statement_id = f'{control_id}_smt.{clean_label}'
            statement.by_components = [by_comp]
            # create a new implemented requirement linked to the control id to hold the statement
            imp_req: ossp.ImplementedRequirement = gens.generate_sample_model(ossp.ImplementedRequirement)
            imp_req.control_id = control_id
            imp_req.statements = [statement]
            imp_reqs.append(imp_req)

        return imp_reqs

    def assemble_ssp(self, md_name: str, ssp_name: str, use_tree: bool) -> int:
        """Assemble the markdown directory into an ssp."""
        # use_tree dictates which code to use to extract prose from the .md files
        # default is not to use tree and parse directly
        # find all groups in the markdown dir
        group_ids = []
        trestle_root = fs.get_trestle_project_root(pathlib.Path.cwd())
        md_dir = trestle_root / md_name

        for gdir in md_dir.glob('*/'):
            group_ids.append(str(gdir.stem))

        # generate the one dummy component that implementations will refer to in by_components
        component: ossp.SystemComponent = gens.generate_sample_model(ossp.SystemComponent)
        component.description = 'Dummy component created by trestle'

        # create system implementation to hold the dummy component
        system_imp: ossp.SystemImplementation = gens.generate_sample_model(ossp.SystemImplementation)
        system_imp.components = [component]

        # create implementation requirements for each control, linked to the dummy component uuid
        imp_reqs: List[ossp.ImplementedRequirement] = []
        for group_id in group_ids:
            group_path = md_dir / group_id
            for control_file in group_path.glob('*.md'):
                if not use_tree:
                    imp_reqs.extend(self._get_implementations_direct(control_file, component))
                else:
                    imp_reqs.extend(self._get_implementations_via_tree(control_file, component))

        # create a control implementation to hold the implementation requirements
        control_imp: ossp.ControlImplementation = gens.generate_sample_model(ossp.ControlImplementation)
        control_imp.implemented_requirements = imp_reqs
        control_imp.description = 'This is the control implementation for the system.'

        # create a sample ssp to hold all the parts
        ssp = gens.generate_sample_model(ossp.SystemSecurityPlan)

        # insert the parts into the ssp
        ssp.control_implementation = control_imp
        ssp.system_implementation = system_imp
        import_profile: ossp.ImportProfile = gens.generate_sample_model(ossp.ImportProfile)
        import_profile.href = 'REPLACE_ME'
        ssp.import_profile = import_profile

        # write out the ssp as json
        ssp_dir = trestle_root / ('system-security-plans/' + ssp_name)
        ssp_dir.mkdir(exist_ok=True, parents=True)
        ssp.oscal_write(ssp_dir / 'system-security-plan.json')

        return 0
