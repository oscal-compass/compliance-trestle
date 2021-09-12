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
from typing import Dict, List, Optional, Tuple, Union

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.core.generators as gens
import trestle.oscal.catalog as cat
import trestle.oscal.common as common
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core import const
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.profile_resolver import CatalogInterface, ProfileResolver
from trestle.utils.md_writer import MDWriter

logger = logging.getLogger(__name__)


class SSPGenerate(AuthorCommonCommand):
    """Generate SSP in markdown form from a Profile."""

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

        profile_path = trestle_root / f'profiles/{args.profile}/profile.json'

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
                    section_label = s[0].strip()
                    if section_label == 'statement':
                        logger.warning('Section label "statment" is not allowed.')
                        return 1
                    sections[s[0].strip()] = s[1].strip()
                else:
                    sections[section] = section

        logger.debug(f'ssp sections: {sections}')

        ssp_manager = SSPManager()

        return ssp_manager.generate_ssp(trestle_root, profile_path.resolve(), markdown_path, sections, yaml_header)


class SSPAssemble(AuthorCommonCommand):
    """Assemble markdown files of controls into an SSP json file."""

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

        ssp_manager = SSPManager()
        return ssp_manager.assemble_ssp(args.trestle_root, args.markdown, args.output)


class SSPManager():
    """Manage generation of SSP in markdown format from profile and assembly of edited markdown into json SSP."""

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
                        return ii, item_label, SSPManager._trim_prose_lines(prose_lines)
                    prose_lines.append(lines[ii].strip())
                    ii += 1
            elif lines[ii].startswith('# ') and lines[ii].strip().endswith(const.SSP_MD_IMPLEMENTATION_QUESTION):
                item_label = lines[ii].strip().split(' ')[1]
                ii += 1
                while ii < nlines:
                    if lines[ii].startswith(const.SSP_MD_HRULE_LINE):
                        return ii, item_label, SSPManager._trim_prose_lines(prose_lines)
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
            ii, part_label, prose_lines = SSPManager._get_label_prose(ii, lines)
            if ii < 0:
                break
            clean_label = SSPManager._strip_bad_chars(part_label)
            responses[clean_label] = prose_lines
        return responses

    def _get_implementations(self, control_file: pathlib.Path,
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
            trestle_root: The trestle root directory
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

        profile_resolver = ProfileResolver()
        resolved_catalog = profile_resolver.get_resolved_profile_catalog(trestle_root, profile_path)
        catalog_interface = CatalogInterface(resolved_catalog)

        # write out the controls
        for control in catalog_interface.get_all_controls(True):
            group_id, group_title, _ = catalog_interface.get_group_info(control.id)
            out_path = md_path / group_id
            self.write_control(out_path, control, group_title, yaml_header, sections)

        return 0

    def assemble_ssp(self, trestle_root: pathlib.Path, md_name: str, ssp_name: str) -> int:
        """
        Assemble the markdown directory into a json ssp model file.

        In normal operation the markdown would have been edited to provide implementation responses.
        These responses are captured as prose in the ssp json file.

        Args:
            trestle_root: The trestle root directory
            md_name: The name of the directory containing the markdown control files for the ssp
            ssp_name: The output name of the ssp json file to be created from the assembly

        Returns:
            0 on success, 1 otherwise

        """
        # find all groups in the markdown dir
        group_ids = []
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
                imp_reqs.extend(self._get_implementations(control_file, component))

        # create a control implementation to hold the implementation requirements
        control_imp: ossp.ControlImplementation = gens.generate_sample_model(ossp.ControlImplementation)
        control_imp.implemented_requirements = imp_reqs
        control_imp.description = const.SSP_SYSTEM_CONTROL_IMPLEMENTATION_TEXT

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
