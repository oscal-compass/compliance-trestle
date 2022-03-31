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
from typing import Dict, List, Optional, Set

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.core.generators as gens
import trestle.oscal.common as com
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
from trestle.common import const, file_utils, log
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.common.list_utils import as_list, none_if_empty
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.author.profile import sections_to_dict
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver

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
            '-ohv',
            '--overwrite-header-values',
            help=const.HELP_OVERWRITE_HEADER_VALUES,
            required=False,
            action='store_true',
            default=False
        )
        sections_help_str = (
            'Comma separated list of section:alias pairs.  Provides mapping of short names to long for markdown.'
        )
        self.add_argument('-s', '--sections', help=sections_help_str, required=False, type=str)
        allowed_sections_help_str = (
            'Comma separated list of section short names to include in the markdown.  Others will not appear.'
        )
        self.add_argument('-as', '--allowed-sections', help=allowed_sections_help_str, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = args.trestle_root
            if not file_utils.is_directory_name_allowed(args.output):
                raise TrestleError(f'{args.output} is not an allowed directory name')

            profile_path = trestle_root / f'profiles/{args.profile}/profile.json'

            yaml_header: dict = {}
            if args.yaml_header:
                try:
                    logging.debug(f'Loading yaml header file {args.yaml_header}')
                    yaml = YAML()
                    yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'))
                except YAMLError as e:
                    raise TrestleError(f'YAML error loading yaml header for ssp generation: {e}')

            markdown_path = trestle_root / args.output

            profile_resolver = ProfileResolver()

            resolved_catalog = profile_resolver.get_resolved_profile_catalog(trestle_root, profile_path)
            catalog_interface = CatalogInterface(resolved_catalog)

            sections_dict: Dict[str, str] = {}
            if args.sections:
                sections_dict = sections_to_dict(args.sections)
                if 'statement' in sections_dict:
                    raise TrestleError('Statement is not allowed as a section name.')
                # add any existing sections from the controls but only have short names
                control_section_short_names = catalog_interface.get_sections()
                for short_name in control_section_short_names:
                    if short_name not in sections_dict:
                        sections_dict[short_name] = short_name
                logger.debug(f'ssp sections dict: {sections_dict}')

            catalog_interface.write_catalog_as_markdown(
                md_path=markdown_path,
                yaml_header=yaml_header,
                sections_dict=sections_dict,
                prompt_responses=True,
                additional_content=False,
                profile=None,
                overwrite_header_values=args.overwrite_header_values,
                set_parameters=False,
                required_sections=None,
                allowed_sections=args.allowed_sections
            )

            return CmdReturnCodes.SUCCESS.value

        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while writing markdown from catalog')


class SSPAssemble(AuthorCommonCommand):
    """Assemble markdown files of controls into an SSP json file."""

    name = 'ssp-assemble'

    def _init_arguments(self) -> None:
        name_help_str = (
            'Optional name of the ssp model in the trestle workspace that is being modified.  '
            'If not provided the output name is used.'
        )
        self.add_argument('-n', '--name', help=name_help_str, required=False, type=str)
        file_help_str = 'Name of the input markdown file directory'
        self.add_argument('-m', '--markdown', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json SSP'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)
        self.add_argument('-vn', '--version', help=const.HELP_VERSION, required=False, type=str)

    def _merge_imp_reqs(self, ssp: ossp.SystemSecurityPlan, imp_reqs: List[ossp.ImplementedRequirement]) -> None:
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

        changed = ssp.control_implementation.implemented_requirements != imp_reqs
        ssp.control_implementation.implemented_requirements = imp_reqs
        return changed

    def _generate_roles_in_metadata(self, ssp: ossp.SystemSecurityPlan) -> bool:
        """Find all roles referenced by imp reqs and create role in metadata as needed."""
        metadata = ssp.metadata
        metadata.roles = as_list(metadata.roles)
        known_role_ids = [role.id for role in metadata.roles]
        changed = False
        for imp_req in ssp.control_implementation.implemented_requirements:
            role_ids = [resp_role.role_id for resp_role in as_list(imp_req.responsible_roles)]
            for role_id in role_ids:
                if role_id not in known_role_ids:
                    role = com.Role(id=role_id, title=role_id)
                    metadata.roles.append(role)
                    known_role_ids.append(role_id)
                    changed = True
        metadata.roles = none_if_empty(metadata.roles)
        return changed

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = pathlib.Path(args.trestle_root)

            md_path = trestle_root / args.markdown

            # the original, reference ssp name defaults to same as output if name not specified
            # thus in cyclic editing you are reading and writing same json ssp
            orig_ssp_name = args.output
            if args.name:
                orig_ssp_name = args.name
            new_ssp_name = args.output

            new_file_content_type = FileContentType.JSON

            # if output ssp already exists, load it to see if new one is different
            existing_ssp: Optional[ossp.SystemSecurityPlan] = None
            new_ssp_path = ModelUtils.full_path_for_top_level_model(trestle_root, new_ssp_name, ossp.SystemSecurityPlan)
            if new_ssp_path:
                _, _, existing_ssp = ModelUtils.load_distributed(new_ssp_path, trestle_root)
                new_file_content_type = FileContentType.path_to_content_type(new_ssp_path)

            ssp: ossp.SystemSecurityPlan
            comp_dict: Dict[str, ossp.SystemComponent] = {}

            # if orig ssp exists - need to load it rather than instantiate new one
            orig_ssp_path = ModelUtils.full_path_for_top_level_model(
                trestle_root, orig_ssp_name, ossp.SystemSecurityPlan
            )

            # need to load imp_reqs from markdown but need component first
            if orig_ssp_path:
                # load the existing json ssp
                _, _, ssp = ModelUtils.load_distributed(orig_ssp_path, trestle_root)
                for component in ssp.system_implementation.components:
                    comp_dict[component.title] = component
                # read the new imp reqs from markdown and have them reference existing components
                imp_reqs = CatalogInterface.read_catalog_imp_reqs(md_path, comp_dict)
                self._merge_imp_reqs(ssp, imp_reqs)
                new_file_content_type = FileContentType.path_to_content_type(orig_ssp_path)
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
            component_list: List[ossp.SystemComponent] = []
            for comp in comp_dict.values():
                component_list.append(comp)
            if ssp.system_implementation.components:
                # reconstruct list with same order as existing, but add/remove components as needed
                new_list: List[ossp.SystemComponent] = []
                for comp in ssp.system_implementation.components:
                    if comp in component_list:
                        new_list.append(comp)
                for comp in component_list:
                    if comp not in new_list:
                        new_list.append(comp)
                ssp.system_implementation.components = new_list
            elif component_list:
                ssp.system_implementation.components = component_list
            self._generate_roles_in_metadata(ssp)

            if args.version:
                ssp.metadata.version = com.Version(__root__=args.version)

            if ModelUtils.models_are_equivalent(existing_ssp, ssp):
                logger.info('No changes to assembled ssp so ssp not written out.')
                return CmdReturnCodes.SUCCESS.value

            if args.regenerate:
                ssp, _, _ = ModelUtils.regenerate_uuids(ssp)
            ModelUtils.update_last_modified(ssp)

            # write out the ssp as json
            ModelUtils.save_top_level_model(ssp, trestle_root, new_ssp_name, new_file_content_type)

            return CmdReturnCodes.SUCCESS.value

        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while assembling SSP')


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
        self.add_argument('-vn', '--version', help=const.HELP_VERSION, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = pathlib.Path(args.trestle_root)

            return self.filter_ssp(trestle_root, args.name, args.profile, args.output, args.regenerate, args.version)
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error generating the filtered ssp')

    def filter_ssp(
        self,
        trestle_root: pathlib.Path,
        ssp_name: str,
        profile_name: str,
        out_name: str,
        regenerate: bool,
        version: Optional[str]
    ) -> int:
        """
        Filter the ssp based on controls included by the profile and output new ssp.

        Args:
            trestle_root: root directory of the trestle project
            ssp_name: name of the ssp model
            profile_name: name of the profile model used for filtering
            out_name: name of the output ssp model with filtered controls
            regenerate: whether to regenerate the uuid's in the ssp
            version: new version for the model

        Returns:
            0 on success, 1 otherwise
        """
        ssp: ossp.SystemSecurityPlan

        ssp, _ = ModelUtils.load_top_level_model(trestle_root, ssp_name, ossp.SystemSecurityPlan, FileContentType.JSON)
        profile_path = ModelUtils.path_for_top_level_model(
            trestle_root, profile_name, prof.Profile, FileContentType.JSON
        )

        prof_resolver = ProfileResolver()
        catalog = prof_resolver.get_resolved_profile_catalog(trestle_root, profile_path)
        catalog_interface = CatalogInterface(catalog)

        # The input ssp should reference a superset of the controls referenced by the profile
        # Need to cull references in the ssp to controls not in the profile
        # Also make sure the output ssp contains imp reqs for all controls in the profile
        control_imp = ssp.control_implementation
        ssp_control_ids: Set[str] = set()

        new_set_params: List[ossp.SetParameter] = []
        for set_param in as_list(control_imp.set_parameters):
            control = catalog_interface.get_control_by_param_id(set_param.param_id)
            if control is not None:
                new_set_params.append(set_param)
                ssp_control_ids.add(control.id)
        control_imp.set_parameters = new_set_params if new_set_params else None

        new_imp_requirements: List[ossp.ImplementedRequirement] = []
        for imp_requirement in as_list(control_imp.implemented_requirements):
            control = catalog_interface.get_control(imp_requirement.control_id)
            if control is not None:
                new_imp_requirements.append(imp_requirement)
                ssp_control_ids.add(control.id)
        control_imp.implemented_requirements = new_imp_requirements

        # make sure all controls in the profile have implemented reqs in the final ssp
        if not ssp_control_ids.issuperset(catalog_interface.get_control_ids()):
            raise TrestleError('Unable to filter the ssp because the profile references controls not in it.')

        ssp.control_implementation = control_imp
        if regenerate:
            ssp, _, _ = ModelUtils.regenerate_uuids(ssp)
        if version:
            ssp.metadata.version = com.Version(__root__=version)
        ModelUtils.update_last_modified(ssp)

        ModelUtils.save_top_level_model(ssp, trestle_root, out_name, FileContentType.JSON)

        return CmdReturnCodes.SUCCESS.value
