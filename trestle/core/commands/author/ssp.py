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
from typing import Dict, List, Optional

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.core.generators as gens
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core import const
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.profile_resolver import ProfileResolver

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
        self._alters: List[prof.Alter] = []
        self._sections: Dict[str, str] = {}

    def generate_ssp(
        self,
        trestle_root: pathlib.Path,
        profile_path: pathlib.Path,
        md_path: pathlib.Path,
        sections: Optional[Dict[str, str]],
        yaml_header: dict,
        all_details: bool = False
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
            all_details: Specify writing all control details or just partial.
        Returns:
            0 on success, 1 otherwise

        """
        logging.debug(f'Generate ssp in {md_path} from profile {profile_path}')

        profile_resolver = ProfileResolver()
        resolved_catalog = profile_resolver.get_resolved_profile_catalog(trestle_root, profile_path)
        catalog_interface = CatalogInterface(resolved_catalog)
        catalog_interface.write_catalog_as_markdown(md_path, yaml_header, sections, all_details)

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
        # generate the one dummy component that implementations will refer to in by_components
        component: ossp.SystemComponent = gens.generate_sample_model(ossp.SystemComponent)
        component.description = 'Dummy component created by trestle'

        # create system implementation to hold the dummy component
        system_imp: ossp.SystemImplementation = gens.generate_sample_model(ossp.SystemImplementation)
        system_imp.components = [component]

        md_path = trestle_root / md_name

        imp_reqs = CatalogInterface.read_catalog_imp_reqs(md_path, component)

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
