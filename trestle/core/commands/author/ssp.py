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
from typing import Any, Dict, List, Optional, Set

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.core.generators as gens
import trestle.core.generic_oscal as generic
import trestle.oscal.common as com
import trestle.oscal.component as comp
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
from trestle.common import const, file_utils, log
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.common.list_utils import as_list, comma_sep_to_list, deep_set, none_if_empty
from trestle.common.load_validate import load_validate_model_name
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog.catalog_api import CatalogAPI
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.catalog.catalog_reader import CatalogReader
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.author.component import ComponentAssemble
from trestle.core.commands.common.cmd_utils import clear_folder
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.core.control_interface import ControlInterface
from trestle.core.control_reader import ControlReader
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver
from trestle.core.remote.cache import FetcherFactory

logger = logging.getLogger(__name__)


class SSPGenerate(AuthorCommonCommand):
    """Generate SSP in markdown form from a Profile."""

    name = 'ssp-generate'

    def _init_arguments(self) -> None:
        file_help_str = 'Main profile href, or name of the profile model in the trestle workspace'
        self.add_argument('-p', '--profile', help=file_help_str, required=True, type=str)
        self.add_argument('-o', '--output', help=const.HELP_MARKDOWN_NAME, required=True, type=str)
        self.add_argument('-cd', '--compdefs', help=const.HELP_COMPDEFS, required=False, type=str)
        self.add_argument('-y', '--yaml-header', help=const.HELP_YAML_PATH, required=False, type=str)
        self.add_argument(
            '-fo', '--force-overwrite', help=const.HELP_FO_OUTPUT, required=False, action='store_true', default=False
        )
        self.add_argument(
            '-ohv',
            '--overwrite-header-values',
            help=const.HELP_OVERWRITE_HEADER_VALUES,
            required=False,
            action='store_true',
            default=False
        )

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = args.trestle_root
            if not file_utils.is_directory_name_allowed(args.output):
                raise TrestleError(f'{args.output} is not an allowed directory name')

            yaml_header: dict = {}
            if args.yaml_header:
                try:
                    logging.debug(f'Loading yaml header file {args.yaml_header}')
                    yaml = YAML()
                    yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'))
                except YAMLError as e:
                    raise TrestleError(f'YAML error loading yaml header {args.yaml_header} for ssp generation: {e}')

            compdef_name_list = comma_sep_to_list(args.compdefs)

            md_path = trestle_root / args.output

            return self._generate_ssp_markdown(
                trestle_root,
                args.profile,
                compdef_name_list,
                md_path,
                yaml_header,
                args.overwrite_header_values,
                args.force_overwrite
            )

        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while writing markdown from catalog')

    def _generate_ssp_markdown(
        self,
        trestle_root: pathlib.Path,
        profile_name_or_href: str,
        compdef_name_list: List[str],
        md_path: pathlib.Path,
        yaml_header: Dict[str, Any],
        overwrite_header_values: bool,
        force_overwrite: bool
    ) -> int:
        """
        Generate the ssp markdown from the profile and compdefs.

        Notes:
        Get RPC from profile.
        For each compdef:
            For each comp:
                Load top level rules
                for each control_imp:
                    Load rules params values
                    For each imp_req (bound to 1 control):
                        Load control level rules and status
                        Load part level rules
                        If rules apply then write out control and add to list written out
                        If control exists, read it and insert content
        """
        if force_overwrite:
            try:
                logger.debug(f'Overwriting the content of {md_path}.')
                clear_folder(pathlib.Path(md_path))
            except TrestleError as e:  # pragma: no cover
                raise TrestleError(f'Unable to overwrite contents of {md_path}: {e}')

        context = ControlContext.generate(ContextPurpose.SSP, True, trestle_root, md_path)
        context.cli_yaml_header = yaml_header
        context.sections_dict = None
        context.prompt_responses = True
        context.overwrite_header_values = overwrite_header_values
        context.allowed_sections = None
        context.comp_def_name_list = compdef_name_list

        # if file not recognized as URI form, assume it represents name of file in trestle directory
        profile_in_trestle_dir = '://' not in profile_name_or_href
        profile_href = profile_name_or_href
        if profile_in_trestle_dir:
            local_path = f'profiles/{profile_name_or_href}/profile.json'
            profile_href = const.TRESTLE_HREF_HEADING + local_path
            profile_path = trestle_root / local_path
            _, _, context.profile = ModelUtils.load_distributed(profile_path, trestle_root)
        else:
            fetcher = FetcherFactory.get_fetcher(trestle_root, profile_href)
            context.profile: prof.Profile = fetcher.get_oscal(profile_path)
            profile_path = profile_href

        profile_resolver = ProfileResolver()
        # in ssp context we want to see missing value warnings
        resolved_catalog = profile_resolver.get_resolved_profile_catalog(
            trestle_root, profile_path, block_params=False, params_format='[.]', show_value_warnings=True
        )

        catalog_api = CatalogAPI(catalog=resolved_catalog, context=context)

        context.cli_yaml_header[const.TRESTLE_GLOBAL_TAG] = {}
        profile_header = {'title': context.profile.metadata.title, 'href': profile_href}

        context.cli_yaml_header[const.TRESTLE_GLOBAL_TAG][const.PROFILE] = profile_header

        catalog_api.write_catalog_as_markdown()

        return CmdReturnCodes.SUCCESS.value


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
        self.add_argument('-cd', '--compdefs', help=const.HELP_COMPDEFS, required=False, type=str)
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)
        self.add_argument('-vn', '--version', help=const.HELP_VERSION, required=False, type=str)

    def _merge_imp_reqs(self, ssp: ossp.SystemSecurityPlan, imp_reqs: List[ossp.ImplementedRequirement]) -> bool:
        """
        Merge the new imp_reqs into the ssp.

        If a statement has same id and same by_comp uuid as ssp, use the ssp version with new description.
        Otherwise just insert the statement.
        When the statement was loaded it had access to the current components so the uuids should match.
        """
        id_map: Dict[str, Dict[str, ossp.Statement]] = {}
        by_comp_map: Dict[str, Dict[str, ossp.ByComponent]] = {}
        control_map: Dict[str, ossp.ImplementedRequirement] = {}
        component_uuid_map: Dict[str, str] = {}
        # go through existing ssp and create map of existing statements by statement id and component uuid
        for component in as_list(ssp.system_implementation.components):
            component_uuid_map[component.title] = component.uuid
        for imp_req in as_list(ssp.control_implementation.implemented_requirements):
            control_map[imp_req.control_id] = imp_req
            for statement in as_list(imp_req.statements):
                for by_comp in as_list(statement.by_components):
                    id_ = statement.statement_id
                    deep_set(id_map, [id_, by_comp.component_uuid], statement)
            for by_comp in as_list(imp_req.by_components):
                deep_set(by_comp_map, [imp_req.control_id, by_comp.component_uuid], by_comp)

        # now go through provided imp_reqs and update the uuid refs
        for imp_req in imp_reqs:
            control_by_comp_map = by_comp_map.get(imp_req.control_id, {})
            if imp_req.control_id in control_map:
                imp_req.uuid = control_map[imp_req.control_id].uuid
            for by_comp in as_list(imp_req.by_components):
                if by_comp.component_uuid in control_by_comp_map:
                    by_comp.uuid = control_by_comp_map[by_comp.component_uuid].uuid
                else:
                    pass
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

        # now that uuids have been fixed up - set the ssp imp_reqs equal to what was loaded from markdown
        changed = ssp.control_implementation.implemented_requirements != imp_reqs
        ssp.control_implementation.implemented_requirements = imp_reqs
        return changed

    @staticmethod
    def _get_ssp_component(ssp: ossp.SystemSecurityPlan, gen_comp: generic.GenericComponent) -> ossp.SystemComponent:
        for component in as_list(ssp.system_implementation.components):
            if component.title == gen_comp.title:
                return component
        new_component = gen_comp.as_system_component()
        return new_component

    @staticmethod
    def _merge_imp_req_into_imp_req(
        imp_req: ossp.ImplementedRequirement,
        gen_imp_req: generic.GenericImplementedRequirement,
        set_params: List[ossp.SetParameter]
    ) -> None:
        """Merge comp def imp req into existing imp req."""
        # convert generic imp req from comp defs into ssp form
        src_imp_req = gen_imp_req.as_ssp()
        imp_req.props = none_if_empty(ControlInterface.clean_props(gen_imp_req.props))
        imp_req.statements = src_imp_req.statements
        for statement in as_list(imp_req.statements):
            statement.props = none_if_empty(ControlInterface.clean_props(statement.props))
        imp_req.by_components = src_imp_req.by_components

    @staticmethod
    def _get_imp_req_for_statement(
        ssp: ossp.SystemSecurityPlan, control_id: str, statement_id: str
    ) -> ossp.ImplementedRequirement:
        control_imp_req: Optional[ossp.ImplementedRequirement] = None
        for imp_req in as_list(ssp.control_implementation.implemented_requirements):
            if imp_req.control_id == control_id:
                control_imp_req = imp_req
                if statement_id in [stat.statement_id for stat in as_list(imp_req.statements)]:
                    return imp_req
        # we didn't find imp_req with statement so need to make statement and/or imp_req
        if not control_imp_req:
            control_imp_req = gens.generate_sample_model(ossp.ImplementedRequirement)
            control_imp_req.control_id = control_id
            control_imp_req.statements = []
            ssp.control_implementation.implemented_requirements = as_list(
                ssp.control_implementation.implemented_requirements
            )
            ssp.control_implementation.implemented_requirements.append(control_imp_req)
        statement = gens.generate_sample_model(ossp.Statement)
        statement.statement_id = statement_id
        statement.by_components = []
        control_imp_req.statements.append(statement)
        return control_imp_req

    @staticmethod
    def _get_by_comp_from_imp_req(
        imp_req: ossp.ImplementedRequirement, statement_id: str, comp_uuid: str
    ) -> ossp.ByComponent:
        # this assumes the statement with id has been generated as needed
        for statement in as_list(imp_req.statements):
            if statement.statement_id == statement_id:
                for by_comp in as_list(statement.by_components):
                    if by_comp.component_uuid == comp_uuid:
                        return by_comp
                # didnt find bycomp so need to make one
                by_comp = gens.generate_sample_model(ossp.ByComponent)
                by_comp.component_uuid = comp_uuid
                statement.by_components = as_list(statement.by_components)
                statement.by_components.append(by_comp)
                return by_comp
        raise TrestleError(f'Internal error seeking by_comp for component {comp_uuid} and statement {statement_id}')

    @staticmethod
    def _add_imp_req_to_ssp(
        ssp: ossp.SystemSecurityPlan,
        gen_comp: generic.GenericComponent,
        gen_imp_req: generic.GenericImplementedRequirement,
        set_params: List[ossp.SetParameter]
    ) -> None:
        src_imp_req = gen_imp_req.as_ssp()
        src_imp_req.props = none_if_empty(ControlInterface.clean_props(gen_imp_req.props))
        src_imp_req.by_components = []
        # each statement in ci corresponds to by_comp in an ssp imp req
        # so insert the new by_comp directly into the ssp, generating parts as needed
        for statement in as_list(gen_imp_req.statements):
            imp_req = SSPAssemble._get_imp_req_for_statement(ssp, gen_imp_req.control_id, statement.statement_id)
            by_comp = SSPAssemble._get_by_comp_from_imp_req(imp_req, statement.statement_id, gen_comp.uuid)
            by_comp.description = statement.description
            by_comp.props = none_if_empty(ControlInterface.clean_props(statement.props))
            by_comp.set_parameters = none_if_empty(set_params)
        ssp.control_implementation.implemented_requirements = as_list(
            ssp.control_implementation.implemented_requirements
        )

    @staticmethod
    def _merge_imp_req_into_ssp(
        ssp: ossp.SystemSecurityPlan,
        gen_imp_req: generic.GenericImplementedRequirement,
        set_params: List[ossp.SetParameter]
    ) -> None:
        """Merge the new imp_reqs into the ssp."""
        for imp_req in as_list(ssp.control_implementation.implemented_requirements):
            if imp_req.uuid == gen_imp_req.uuid:
                SSPAssemble._merge_imp_req_into_imp_req(imp_req, gen_imp_req, set_params)
                return
        new_imp_req = gen_imp_req.as_ssp()
        imp_req.props = none_if_empty(ControlInterface.clean_props(gen_imp_req.props))
        imp_req.statements = gen_imp_req.statements
        for statement in as_list(imp_req.statements):
            statement.props = none_if_empty(ControlInterface.clean_props(statement.props))
        ssp.control_implementation.implemented_requirements = as_list(
            ssp.control_implementation.implemented_requirements
        )
        ssp.control_implementation.implemented_requirements.append(new_imp_req)

    def _merge_comp_defs(self, ssp: ossp.SystemSecurityPlan, comp_dict: Dict[str, generic.GenericComponent]) -> None:
        """Merge the original generic comp defs into the ssp."""
        all_comps: List[ossp.SystemComponent] = []
        # determine if this is a new and empty ssp
        new_ssp = not ssp.control_implementation.implemented_requirements
        for _, gen_comp in comp_dict.items():
            all_ci_props: List[com.Property] = []
            ssp_comp = SSPAssemble._get_ssp_component(ssp, gen_comp)
            set_params: List[ossp.SetParameter] = []
            for ci in as_list(gen_comp.control_implementations):
                all_ci_props.extend(as_list(ci.props))
                for sp in as_list(ci.set_parameters):
                    set_params.append(ossp.SetParameter(sp.param_id, sp.values, sp.remarks))
                for imp_req in as_list(ci.implemented_requirements):
                    if new_ssp:
                        SSPAssemble._add_imp_req_to_ssp(ssp, gen_comp, imp_req, set_params)
                    else:
                        SSPAssemble._merge_imp_req_into_ssp(ssp, imp_req, set_params)
            ssp_comp.props = as_list(gen_comp.props)
            ssp_comp.props.extend(all_ci_props)
            ssp_comp.props = none_if_empty(ControlInterface.clean_props(ssp_comp.props))
            all_comps.append(ssp_comp)

        ssp.system_implementation.components = none_if_empty(all_comps)

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

    @staticmethod
    def _build_comp_dict_from_comp_defs(
        trestle_root: pathlib.Path, comp_def_name_list: List[str], create_sys_comp: bool
    ) -> Dict[str, generic.GenericComponent]:
        comp_dict: Dict[str, generic.GenericComponent] = {}
        for comp_name in comp_def_name_list:
            comp_def, _ = ModelUtils.load_top_level_model(trestle_root, comp_name, comp.ComponentDefinition)
            for def_comp in as_list(comp_def.components):
                gen_def_comp = generic.GenericComponent.from_defined_component(def_comp)
                comp_dict[def_comp.title] = gen_def_comp
        if create_sys_comp:
            sys_comp = generic.GenericComponent.generate()
            sys_comp.type = const.THIS_SYSTEM_AS_KEY
            sys_comp.title = const.SSP_MAIN_COMP_NAME
            comp_dict[sys_comp.title] = sys_comp
        return comp_dict

    @staticmethod
    def _get_this_system_as_gen_comp(ssp: ossp.SystemSecurityPlan) -> Optional[generic.GenericComponent]:
        for component in as_list(ssp.system_implementation.components):
            if component.title == const.SSP_MAIN_COMP_NAME:
                return generic.GenericComponent.from_defined_component(component)
        return None

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

            _, profile_href = ComponentAssemble._get_profile_title_and_href_from_dir(md_path)
            res_cat = ProfileResolver.get_resolved_profile_catalog(trestle_root, profile_href)
            catalog_interface = CatalogInterface(res_cat)

            new_file_content_type = FileContentType.JSON

            # if output ssp already exists, load it to see if new one is different
            existing_ssp: Optional[ossp.SystemSecurityPlan] = None
            new_ssp_path = ModelUtils.full_path_for_top_level_model(trestle_root, new_ssp_name, ossp.SystemSecurityPlan)
            if new_ssp_path:
                _, _, existing_ssp = ModelUtils.load_distributed(new_ssp_path, trestle_root)
                new_file_content_type = FileContentType.path_to_content_type(new_ssp_path)

            ssp: ossp.SystemSecurityPlan

            # if orig ssp exists - need to load it rather than instantiate new one
            orig_ssp_path = ModelUtils.full_path_for_top_level_model(
                trestle_root, orig_ssp_name, ossp.SystemSecurityPlan
            )

            context = ControlContext.generate(ContextPurpose.SSP, True, trestle_root, md_path)
            context.comp_def_name_list = comma_sep_to_list(args.compdefs)
            part_id_map = catalog_interface.get_statement_part_id_map(False)
            catalog_interface.generate_control_rule_info(part_id_map, context)

            # load all original comp defs
            # only additions from markdown will be imp_req prose and status
            # and param vals
            # if this is a new ssp then create system component in the comp_dict
            comp_dict = SSPAssemble._build_comp_dict_from_comp_defs(
                trestle_root, context.comp_def_name_list, not orig_ssp_path
            )

            # if ssp already exists use it as container for new content
            if orig_ssp_path:
                # load the existing json ssp
                _, _, ssp = ModelUtils.load_distributed(orig_ssp_path, trestle_root)
                # add the This System comp to the comp dict so its uuid is known
                sys_comp = SSPAssemble._get_this_system_as_gen_comp(ssp)
                if not sys_comp:
                    raise TrestleError('Original ssp has no system component.')
                comp_dict[const.SSP_MAIN_COMP_NAME] = sys_comp

                self._merge_comp_defs(ssp, comp_dict)
                CatalogReader.read_ssp_md_content(md_path, ssp, catalog_interface, context)

                new_file_content_type = FileContentType.path_to_content_type(orig_ssp_path)
            else:
                # create a sample ssp to hold all the parts
                ssp = gens.generate_sample_model(ossp.SystemSecurityPlan)
                ssp.control_implementation.implemented_requirements = []
                ssp.control_implementation.description = const.SSP_SYSTEM_CONTROL_IMPLEMENTATION_TEXT
                ssp.system_implementation.components = []
                self._merge_comp_defs(ssp, comp_dict)
                CatalogReader.read_ssp_md_content(md_path, ssp, catalog_interface, context)

                # FIXME use set params dict
                # FIXME self._merge_comp_defs(ssp, comp_dict)
                # FIXME self._merge_imp_reqs(ssp, new_imp_reqs)
                import_profile: ossp.ImportProfile = gens.generate_sample_model(ossp.ImportProfile)
                import_profile.href = 'REPLACE_ME'
                ssp.import_profile = import_profile

            # now that we know the complete list of needed components, add them to the sys_imp
            # TODO if the ssp already existed then components may need to be removed if not ref'd by imp_reqs
            self._generate_roles_in_metadata(ssp)

            ssp.import_profile.href = profile_href

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
    """Filter the controls in an ssp based on files included by profile and/or list of component names."""

    name = 'ssp-filter'

    def _init_arguments(self) -> None:
        file_help_str = 'Name of the input ssp'
        self.add_argument('-n', '--name', help=file_help_str, required=True, type=str)
        file_help_str = 'Name of the optional input profile that defines set of controls in filtered ssp'
        self.add_argument('-p', '--profile', help=file_help_str, required=False, type=str)
        output_help_str = 'Name of the output generated SSP'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)
        self.add_argument('-vn', '--version', help=const.HELP_VERSION, required=False, type=str)
        comp_help_str = 'Colon-delimited list of component names to include in filtered ssp.'
        self.add_argument('-c', '--components', help=comp_help_str, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = pathlib.Path(args.trestle_root)
            comp_names: Optional[List[str]] = None
            if args.components:
                comp_names = args.components.split(':')
            elif not args.profile:
                logger.warning('You must specify either a profile or list of component names for ssp-filter.')
                return 1

            return self.filter_ssp(
                trestle_root, args.name, args.profile, args.output, args.regenerate, args.version, comp_names
            )
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error generating the filtered ssp')

    def filter_ssp(
        self,
        trestle_root: pathlib.Path,
        ssp_name: str,
        profile_name: str,
        out_name: str,
        regenerate: bool,
        version: Optional[str],
        components: Optional[List[str]] = None
    ) -> int:
        """
        Filter the ssp based on controls included by the profile and/or components and output new ssp.

        Args:
            trestle_root: root directory of the trestle project
            ssp_name: name of the ssp model
            profile_name: name of the optional profile model used for filtering
            out_name: name of the output ssp model with filtered controls
            regenerate: whether to regenerate the uuid's in the ssp
            version: new version for the model
            components: optional list of component names used for filtering

        Returns:
            0 on success, 1 otherwise
        """
        # load the ssp
        ssp: ossp.SystemSecurityPlan
        ssp, _ = load_validate_model_name(trestle_root, ssp_name, ossp.SystemSecurityPlan, FileContentType.JSON)
        profile_path = ModelUtils.path_for_top_level_model(
            trestle_root, profile_name, prof.Profile, FileContentType.JSON
        )

        if components:
            raw_comp_names = [ControlReader.simplify_name(name) for name in components]
            comp_uuids: List[str] = []
            for component in ssp.system_implementation.components:
                if ControlReader.simplify_name(component.title) in raw_comp_names:
                    comp_uuids.append(component.uuid)
            # imp_reqs can be by comp
            # and imp_reqs can have statements that are by comp
            if comp_uuids:
                new_imp_reqs: List[ossp.ImplementedRequirement] = []
                # these are all required to be present
                for imp_req in ssp.control_implementation.implemented_requirements:
                    new_by_comps: List[ossp.ByComponent] = []
                    # by_comps is optional
                    for by_comp in as_list(imp_req.by_components):
                        if by_comp.component_uuid in comp_uuids:
                            new_by_comps.append(by_comp)
                    imp_req.by_components = none_if_empty(new_by_comps)
                    new_imp_reqs.append(imp_req)
                    new_statements: List[ossp.Statement] = []
                    for statement in as_list(imp_req.statements):
                        new_by_comps: List[ossp.ByComponent] = []
                        for by_comp in as_list(statement.by_components):
                            if by_comp.component_uuid in comp_uuids:
                                new_by_comps.append(by_comp)
                        statement.by_components = none_if_empty(new_by_comps)
                        new_statements.append(statement)
                    imp_req.statements = none_if_empty(new_statements)
                ssp.control_implementation.implemented_requirements = new_imp_reqs
                # now remove any unused components from the ssp
                new_comp_list: List[ossp.SystemComponent] = []
                for comp_ in ssp.system_implementation.components:
                    if comp_.uuid in comp_uuids:
                        new_comp_list.append(comp_)
                ssp.system_implementation.components = new_comp_list

        # filter by controls in profile
        if profile_name:
            prof_resolver = ProfileResolver()
            catalog = prof_resolver.get_resolved_profile_catalog(trestle_root, profile_path, show_value_warnings=True)
            catalog_api = CatalogAPI(catalog=catalog)

            # The input ssp should reference a superset of the controls referenced by the profile
            # Need to cull references in the ssp to controls not in the profile
            # Also make sure the output ssp contains imp reqs for all controls in the profile
            control_imp = ssp.control_implementation
            ssp_control_ids: Set[str] = set()

            new_set_params: List[ossp.SetParameter] = []
            for set_param in as_list(control_imp.set_parameters):
                control = catalog_api._catalog_interface.get_control_by_param_id(set_param.param_id)
                if control is not None:
                    new_set_params.append(set_param)
                    ssp_control_ids.add(control.id)
            control_imp.set_parameters = none_if_empty(new_set_params)

            new_imp_requirements: List[ossp.ImplementedRequirement] = []
            for imp_requirement in as_list(control_imp.implemented_requirements):
                control = catalog_api._catalog_interface.get_control(imp_requirement.control_id)
                if control is not None:
                    new_imp_requirements.append(imp_requirement)
                    ssp_control_ids.add(control.id)
            control_imp.implemented_requirements = new_imp_requirements

            # make sure all controls in the profile have implemented reqs in the final ssp
            if not ssp_control_ids.issuperset(catalog_api._catalog_interface.get_control_ids()):
                raise TrestleError('Unable to filter the ssp because the profile references controls not in it.')

            ssp.control_implementation = control_imp

        if version:
            ssp.metadata.version = com.Version(__root__=version)

        existing_ssp_path = ModelUtils.full_path_for_top_level_model(trestle_root, out_name, ossp.SystemSecurityPlan)
        if existing_ssp_path is not None:
            existing_ssp, _ = load_validate_model_name(trestle_root, out_name, ossp.SystemSecurityPlan)
            if ModelUtils.models_are_equivalent(existing_ssp, ssp):
                logger.info('No changes to filtered ssp so ssp not written out.')
                return CmdReturnCodes.SUCCESS.value

        if regenerate:
            ssp, _, _ = ModelUtils.regenerate_uuids(ssp)

        ModelUtils.update_last_modified(ssp)

        ModelUtils.save_top_level_model(ssp, trestle_root, out_name, FileContentType.JSON)

        return CmdReturnCodes.SUCCESS.value
