# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Create ssp from catalog and profile."""

import argparse
import copy
import logging
import pathlib
import traceback
from typing import List, Set

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.core.generators as gens
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
from trestle.core import const
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.profile_resolver import ProfileResolver
from trestle.core.validator_helper import regenerate_uuids
from trestle.utils import fs, log

logger = logging.getLogger(__name__)


class SSPGenerate(AuthorCommonCommand):
    """Generate SSP in markdown form from a Profile."""

    name = 'ssp-generate'

    def _init_arguments(self) -> None:
        file_help_str = 'Name of the profile model in the trestle workspace'
        self.add_argument('-p', '--profile', help=file_help_str, required=True, type=str)
        self.add_argument('-o', '--output', help=const.HELP_MARKDOWN_NAME, required=True, type=str)
        self.add_argument('-y', '--yaml-header', help=const.HELP_YAML_PATH, required=False, type=str)
        self.add_argument(
            '-hdm',
            '--header-dont-merge',
            help=const.HELP_HEADER_MERGE,
            required=False,
            action='store_true',
            default=False
        )
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
                yaml = YAML()
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
                    sections[s[0].strip()] = s[1].strip()
                else:

                    sections[section] = section
            if 'statement' in sections.keys():
                logger.warning('Section label "statement" is not allowed.')
                return 1

        logger.debug(f'ssp sections: {sections}')

        profile_resolver = ProfileResolver()
        try:
            resolved_catalog = profile_resolver.get_resolved_profile_catalog(trestle_root, profile_path)
            catalog_interface = CatalogInterface(resolved_catalog)
        except Exception as e:
            logger.error(f'Error creating the resolved profile catalog: {e}')
            logger.debug(traceback.format_exc())
            return 1
        try:
            catalog_interface.write_catalog_as_markdown(
                markdown_path, yaml_header, sections, True, False, None, header_dont_merge=args.header_dont_merge
            )
        except Exception as e:
            logger.error(f'Error writing the catalog as markdown: {e}')
            logger.debug(traceback.format_exc())
            return 1

        return 0


class SSPAssemble(AuthorCommonCommand):
    """Assemble markdown files of controls into an SSP json file."""

    name = 'ssp-assemble'

    def _init_arguments(self) -> None:
        file_help_str = 'Name of the input markdown file directory'
        self.add_argument('-m', '--markdown', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json SSP'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)

    def _imp_reqs_equivalent(
        self, imp_reqs: List[ossp.ImplementedRequirement], orig_imp_reqs: List[ossp.ImplementedRequirement]
    ) -> bool:
        """
        Check if imp_reqs are the same except for internal uuids.

        Create copy of each imp_req and set the uuids within it to match the original - then check equality.
        TODO: trigger new uuid only if new imp_reqs are added
        """
        if len(imp_reqs) == len(orig_imp_reqs):
            for reqs in zip(imp_reqs, orig_imp_reqs):
                # make a copy of the new imp req
                tmp_req = copy.deepcopy(reqs[0])
                if tmp_req.statements is not None and reqs[1].statements is not None:
                    if len(tmp_req.statements) != len(reqs[1].statements):
                        return False
                    tmp_req.uuid = reqs[1].uuid
                    for stats in zip(tmp_req.statements, reqs[1].statements):
                        if stats[0].by_components is not None and stats[1].by_components is not None:
                            if len(stats[0].by_components) != len(stats[1].by_components):
                                return False
                            stats[0].uuid = stats[1].uuid
                            for by_comps in zip(stats[0].by_components, stats[1].by_components):
                                by_comps[0].uuid = by_comps[1].uuid
                if tmp_req != reqs[1]:
                    return False
        return True

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = pathlib.Path(args.trestle_root)

        md_path = trestle_root / args.markdown

        # if ssp already exists - should load it rather than make new one
        ssp_path = fs.path_for_top_level_model(
            trestle_root, args.output, ossp.SystemSecurityPlan, fs.FileContentType.JSON
        )
        ssp: ossp.SystemSecurityPlan

        try:
            # need to load imp_reqs from markdown but need component first
            if ssp_path.exists():
                _, _, ssp = fs.load_distributed(ssp_path, trestle_root)
                # use first component
                component = ssp.system_implementation.components[0]
                imp_reqs = CatalogInterface.read_catalog_imp_reqs(md_path, component)
                orig_imp_reqs = ssp.control_implementation.implemented_requirements
                if not args.regenerate and not self._imp_reqs_equivalent(imp_reqs, orig_imp_reqs):
                    ssp.control_implementation.implemented_requirements = imp_reqs
                if args.regenerate:
                    regenerate_uuids(ssp)
            else:
                # create a sample ssp to hold all the parts
                ssp = gens.generate_sample_model(ossp.SystemSecurityPlan)
                # generate the one dummy component that implementations will refer to in by_components
                component: ossp.SystemComponent = gens.generate_sample_model(ossp.SystemComponent)
                component.description = 'The System'
                imp_reqs = CatalogInterface.read_catalog_imp_reqs(md_path, component)

                # create system implementation to hold the dummy component
                system_imp: ossp.SystemImplementation = gens.generate_sample_model(ossp.SystemImplementation)
                system_imp.components = [component]

                # create a control implementation to hold the implementation requirements
                control_imp: ossp.ControlImplementation = gens.generate_sample_model(ossp.ControlImplementation)
                control_imp.implemented_requirements = imp_reqs
                control_imp.description = const.SSP_SYSTEM_CONTROL_IMPLEMENTATION_TEXT

                # insert the parts into the ssp
                ssp.control_implementation = control_imp
                ssp.system_implementation = system_imp

                import_profile: ossp.ImportProfile = gens.generate_sample_model(ossp.ImportProfile)
                import_profile.href = 'REPLACE_ME'
                ssp.import_profile = import_profile

        except Exception as e:
            logger.warning(f'Error assembling the ssp from markdown: {e}')
            logger.debug(traceback.format_exc())
            return 1

        # write out the ssp as json
        try:
            fs.save_top_level_model(ssp, trestle_root, args.output, fs.FileContentType.JSON)
        except Exception as e:
            logger.warning(f'Error saving the generated ssp: {e}')
            logger.debug(traceback.format_exc())
            return 1

        return 0


class SSPFilter(AuthorCommonCommand):
    """Filter the controls in an ssp based on files included by profile."""

    name = 'ssp-filter'

    def _init_arguments(self) -> None:
        file_help_str = 'Name of the input ssp'
        self.add_argument('-n', '--name', help=file_help_str, required=True, type=str)
        file_help_str = 'Name of the input profile that defines set of controls in output ssp'
        self.add_argument('-p', '--profile', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated SSP'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = pathlib.Path(args.trestle_root)

        return self.filter_ssp(trestle_root, args.name, args.profile, args.output, args.regenerate)

    def filter_ssp(self, trestle_root: pathlib.Path, ssp_name: str, profile_name: str, out_name: str, regenerate: bool):
        """Filter the ssp based on the profile and output new ssp."""
        ssp: ossp.SystemSecurityPlan

        try:
            ssp, _ = fs.load_top_level_model(trestle_root, ssp_name, ossp.SystemSecurityPlan, fs.FileContentType.JSON)
            profile_path = fs.path_for_top_level_model(
                trestle_root, profile_name, prof.Profile, fs.FileContentType.JSON
            )

            prof_resolver = ProfileResolver()
            catalog = prof_resolver.get_resolved_profile_catalog(trestle_root, profile_path)
            catalog_interface = CatalogInterface(catalog)

            # The input ssp should reference a superset of the controls referenced by the profile
            # Need to cull references in the ssp to controls not in the profile
            # Also make sure the output ssp contains imp reqs for all controls in the profile
            control_imp = ssp.control_implementation
            ssp_control_ids: Set[str] = set()

            set_params = control_imp.set_parameters
            new_set_params: List[ossp.SetParameter] = []
            if set_params is not None:
                for set_param in set_params:
                    control = catalog_interface.get_control_by_param_id(set_param.param_id)
                    if control is not None:
                        new_set_params.append(set_param)
                        ssp_control_ids.add(control.id)
            control_imp.set_parameters = new_set_params if new_set_params else None

            imp_requirements = control_imp.implemented_requirements
            new_imp_requirements: List[ossp.ImplementedRequirement] = []
            if imp_requirements is not None:
                for imp_requirement in imp_requirements:
                    control = catalog_interface.get_control(imp_requirement.control_id)
                    if control is not None:
                        new_imp_requirements.append(imp_requirement)
                        ssp_control_ids.add(control.id)
            control_imp.implemented_requirements = new_imp_requirements

            # make sure all controls in the profile have implemented reqs in the final ssp
            if not ssp_control_ids.issuperset(catalog_interface.get_control_ids()):
                logger.warning('Unable to filter the ssp because the profile references controls not in it.')
                logger.debug(traceback.format_exc())
                return 1

            ssp.control_implementation = control_imp
            if regenerate:
                regenerate_uuids(ssp)
            fs.save_top_level_model(ssp, trestle_root, out_name, fs.FileContentType.JSON)
        except Exception as e:
            logger.warning(f'Error generating the filtered ssp: {e}')
            logger.debug(traceback.format_exc())
            return 1

        return 0
