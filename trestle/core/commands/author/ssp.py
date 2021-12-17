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
import logging
import pathlib
import traceback
from typing import Dict, List, Set

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.core.generators as gens
import trestle.oscal.common as com
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
from trestle.core import const, err
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.profile_resolver import ProfileResolver
from trestle.core.utils import as_list, none_if_empty
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
            '-phv',
            '--preserve-header-values',
            help=const.HELP_PRESERVE_HEADER_VALUES,
            required=False,
            action='store_true',
            default=False
        )
        sections_help_str = (
            'Comma separated list of section:alias pairs for sections to output.' + ' Otherwises defaults to all.'
        )
        self.add_argument('-s', '--sections', help=sections_help_str, required=False, type=str)

    @staticmethod
    def _sections_from_args(args: argparse.Namespace) -> Dict[str, str]:
        sections = {}
        if args.sections is not None:
            section_tuples = args.sections.strip("'").split(',')
            for section in section_tuples:
                if ':' in section:
                    s = section.split(':')
                    sections[s[0].strip()] = s[1].strip()
                else:

                    sections[section] = section
            if 'statement' in sections.keys():
                raise err.TrestleError('"statement" sections are not allowed ')
        return sections

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = args.trestle_root
        if not fs.allowed_task_name(args.output):
            logger.warning(f'{args.output} is not an allowed directory name')
            return CmdReturnCodes.COMMAND_ERROR.value

        profile_path = trestle_root / f'profiles/{args.profile}/profile.json'

        yaml_header: dict = {}
        if 'yaml_header' in args and args.yaml_header is not None:
            try:
                logging.debug(f'Loading yaml header file {args.yaml_header}')
                yaml = YAML()
                yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'))
            except YAMLError as e:
                logging.warning(f'YAML error loading yaml header for ssp generation: {e}')
                return CmdReturnCodes.COMMAND_ERROR.value

        markdown_path = trestle_root / args.output

        profile_resolver = ProfileResolver()
        try:
            resolved_catalog = profile_resolver.get_resolved_profile_catalog(trestle_root, profile_path)
            catalog_interface = CatalogInterface(resolved_catalog)
        except Exception as e:
            logger.error(f'Error creating the resolved profile catalog: {e}')
            logger.debug(traceback.format_exc())
            return CmdReturnCodes.COMMAND_ERROR.value

        try:
            sections = SSPGenerate._sections_from_args(args)
            if sections == {}:
                s_list = catalog_interface.get_sections()
                for item in s_list:
                    sections[item] = item
            logger.debug(f'ssp sections: {sections}')
        except err.TrestleError:
            logger.warning('"statement" section is not allowed.')
            return CmdReturnCodes.COMMAND_ERROR.value

        try:
            catalog_interface.write_catalog_as_markdown(
                markdown_path,
                yaml_header,
                sections,
                True,
                False,
                None,
                preserve_header_values=args.preserve_header_values
            )
        except Exception as e:
            logger.error(f'Error writing the catalog as markdown: {e}')
            logger.debug(traceback.format_exc())
            return CmdReturnCodes.COMMAND_ERROR.value

        return CmdReturnCodes.SUCCESS.value


class SSPAssemble(AuthorCommonCommand):
    """Assemble markdown files of controls into an SSP json file."""

    name = 'ssp-assemble'

    def _init_arguments(self) -> None:
        file_help_str = 'Name of the input markdown file directory'
        self.add_argument('-m', '--markdown', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json SSP'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)

    def _merge_imp_reqs(
        self, ssp: ossp.SystemSecurityPlan, imp_reqs: List[ossp.ImplementedRequirement], regenerate: bool
    ) -> None:
        """
        Merge the new imp_reqs into the ssp and optionally regenerate uuids.

        If a statement has same id and same by_comp uuid as ssp, use the ssp version with new description.
        Otherwise just insert the statement.
        When the statement was loaded it had access to the current components so the uuids should match.
        """
        id_map: Dict[str, Dict[str, ossp.Statement]] = {}
        control_map: Dict[str, ossp.ImplementedRequirement] = {}
        for imp_req in ssp.control_implementation.implemented_requirements:
            control_map[imp_req.control_id] = imp_req
            for statement in imp_req.statements:
                for by_comp in statement.by_components:
                    id_ = statement.statement_id
                    if id_ not in id_map:
                        id_map[id_] = {}
                    id_map[id_][by_comp.component_uuid] = statement

        for imp_req in imp_reqs:
            if imp_req.control_id in control_map:
                imp_req.uuid = control_map[imp_req.control_id].uuid
            for statement in as_list(imp_req.statements):
                id_ = statement.statement_id
                # for each statement id match the statement per component to the original
                if id_ in id_map:
                    comp_dict = id_map[id_]
                    for by_comp in as_list(statement.by_components):
                        if by_comp.component_uuid in comp_dict:
                            statement.uuid = comp_dict[by_comp.component_uuid].uuid
                            for orig_by_comp in as_list(comp_dict[by_comp.component_uuid].by_components):
                                if orig_by_comp.component_uuid == by_comp.component_uuid:
                                    by_comp.uuid = orig_by_comp.uuid
                                    break

        ssp.control_implementation.implemented_requirements = imp_reqs
        if regenerate:
            regenerate_uuids(ssp)

    def _generate_roles_in_metadata(self, ssp: ossp.SystemSecurityPlan) -> None:
        """Find all roles referenced by imp reqs and create role in metadata as needed."""
        metadata = ssp.metadata
        metadata.roles = as_list(metadata.roles)
        known_role_ids = [role.id for role in metadata.roles]
        for imp_req in ssp.control_implementation.implemented_requirements:
            role_ids = [resp_role.role_id for resp_role in as_list(imp_req.responsible_roles)]
            for role_id in role_ids:
                if role_id not in known_role_ids:
                    role = com.Role(id=role_id, title=role_id)
                    metadata.roles.append(role)
                    known_role_ids.append(role_id)
        metadata.roles = none_if_empty(metadata.roles)

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = pathlib.Path(args.trestle_root)

        md_path = trestle_root / args.markdown

        # if ssp already exists - should load it rather than make new one
        ssp_path = fs.path_for_top_level_model(
            trestle_root, args.output, ossp.SystemSecurityPlan, fs.FileContentType.JSON
        )
        ssp: ossp.SystemSecurityPlan
        comp_dict: Dict[str, ossp.SystemComponent] = {}

        try:
            # need to load imp_reqs from markdown but need component first
            if ssp_path.exists():
                # load the existing json ssp
                _, _, ssp = fs.load_distributed(ssp_path, trestle_root)
                for component in ssp.system_implementation.components:
                    comp_dict[component.title] = component
                # read the new imp reqs from markdown and have them reference existing components
                imp_reqs = CatalogInterface.read_catalog_imp_reqs(md_path, comp_dict)
                self._merge_imp_reqs(ssp, imp_reqs, args.regenerate)
            else:
                # create a sample ssp to hold all the parts
                ssp = gens.generate_sample_model(ossp.SystemSecurityPlan)
                # load the imp_reqs from markdown and create components as needed, referenced by ### headers
                imp_reqs = CatalogInterface.read_catalog_imp_reqs(md_path, comp_dict)

                # create system implementation
                system_imp: ossp.SystemImplementation = gens.generate_sample_model(ossp.SystemImplementation)
                ssp.system_implementation = system_imp

                # create a control implementation to hold the implementated requirements
                control_imp: ossp.ControlImplementation = gens.generate_sample_model(ossp.ControlImplementation)
                control_imp.implemented_requirements = imp_reqs
                control_imp.description = const.SSP_SYSTEM_CONTROL_IMPLEMENTATION_TEXT

                # insert the parts into the ssp
                ssp.control_implementation = control_imp
                ssp.system_implementation = system_imp

                # we don't have access to the original profile so we don't know the href
                import_profile: ossp.ImportProfile = gens.generate_sample_model(ossp.ImportProfile)
                import_profile.href = 'REPLACE_ME'
                ssp.import_profile = import_profile

            # now that we know the complete list of needed components, add them to the sys_imp
            # TODO if the ssp already existed then components may need to be removed if not ref'd by imp_reqs
            ssp.system_implementation.components = []
            for comp in comp_dict.values():
                ssp.system_implementation.components.append(comp)
            self._generate_roles_in_metadata(ssp)

        except Exception as e:
            logger.warning(f'Error assembling the ssp from markdown: {e}')
            logger.debug(traceback.format_exc())
            return CmdReturnCodes.COMMAND_ERROR.value

        # write out the ssp as json
        try:
            fs.save_top_level_model(ssp, trestle_root, args.output, fs.FileContentType.JSON)
        except Exception as e:
            logger.warning(f'Error saving the generated ssp: {e}')
            logger.debug(traceback.format_exc())
            return CmdReturnCodes.COMMAND_ERROR.value

        return CmdReturnCodes.SUCCESS.value


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
                return CmdReturnCodes.COMMAND_ERROR.value

            ssp.control_implementation = control_imp
            if regenerate:
                regenerate_uuids(ssp)
            fs.save_top_level_model(ssp, trestle_root, out_name, fs.FileContentType.JSON)
        except Exception as e:
            logger.warning(f'Error generating the filtered ssp: {e}')
            logger.debug(traceback.format_exc())
            return CmdReturnCodes.COMMAND_ERROR.value

        return CmdReturnCodes.SUCCESS.value
