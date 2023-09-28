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
import os
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
from trestle.common.list_utils import as_list, comma_sep_to_list, delete_list_from_list, none_if_empty
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
from trestle.core.control_interface import ControlInterface, ParameterRep
from trestle.core.control_reader import ControlReader
from trestle.core.crm.ssp_inheritance_api import SSPInheritanceAPI
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver
from trestle.core.remote.cache import FetcherFactory
from trestle.core.validator import Validator
from trestle.core.validator_factory import validator_factory

logger = logging.getLogger(__name__)


class SSPGenerate(AuthorCommonCommand):
    """Generate SSP in markdown form from a Profile."""

    name = 'ssp-generate'

    def _init_arguments(self) -> None:
        file_help_str = 'Main profile href, or name of the profile model in the trestle workspace'
        self.add_argument('-p', '--profile', help=file_help_str, required=True, type=str)
        self.add_argument(
            '-o', '--output', help='Name of the output generated ssp markdown folder', required=True, type=str
        )  # noqa E501
        self.add_argument('-cd', '--compdefs', help=const.HELP_COMPDEFS, required=False, type=str)

        ls_help_str = 'Leveraged ssp with inheritable controls href or name in the trestle_workspace'
        self.add_argument('-ls', '--leveraged-ssp', help=ls_help_str, required=False, type=str)

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

            yaml_header: Dict[str, Any] = {}
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
                args.leveraged_ssp,
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
        leveraged_ssp_name_or_href: str,
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
                logger.info(f'Overwriting the content in {md_path}.')
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
            context.profile = fetcher.get_oscal()
            profile_path = profile_href

        profile_resolver = ProfileResolver()
        # in ssp context we want to see missing value warnings
        resolved_catalog = profile_resolver.get_resolved_profile_catalog(
            trestle_root,
            profile_path,
            block_params=False,
            params_format='[.]',
            param_rep=ParameterRep.ASSIGNMENT_FORM,
            show_value_warnings=True
        )

        catalog_api = CatalogAPI(catalog=resolved_catalog, context=context)

        context.cli_yaml_header[const.TRESTLE_GLOBAL_TAG] = {}
        profile_header = {'title': context.profile.metadata.title, 'href': profile_href}

        context.cli_yaml_header[const.TRESTLE_GLOBAL_TAG][const.PROFILE] = profile_header

        catalog_api.write_catalog_as_markdown()

        # Generate inheritance view after controls view completes
        if leveraged_ssp_name_or_href:
            self._generate_inheritance_markdown(trestle_root, leveraged_ssp_name_or_href, resolved_catalog, md_path)

        return CmdReturnCodes.SUCCESS.value

    def _generate_inheritance_markdown(
        self,
        trestle_root: pathlib.Path,
        leveraged_ssp_name_or_href: str,
        resolved_catalog: CatalogInterface,
        md_path: str
    ) -> None:
        """
        Generate markdown for inheritance view.

        Notes:
            This will create the inheritance view markdown files in the same directory as the ssp markdown files.
            The information will be from the leveraged ssp, but filtered by the chose profile to ensure only relevant
            control are present for mapping.
        """
        # if file not recognized as URI form, assume it represents name of file in trestle directory
        ssp_in_trestle_dir = '://' not in leveraged_ssp_name_or_href
        ssp_href = leveraged_ssp_name_or_href
        if ssp_in_trestle_dir:
            local_path = f'{const.MODEL_DIR_SSP}/{leveraged_ssp_name_or_href}/system-security-plan.json'
            ssp_href = const.TRESTLE_HREF_HEADING + local_path

        inheritance_view_path: pathlib.Path = md_path.joinpath(const.INHERITANCE_VIEW_DIR)
        inheritance_view_path.mkdir(exist_ok=True)
        logger.debug(f'Creating content for inheritance view in {inheritance_view_path}')

        ssp_inheritance_api = SSPInheritanceAPI(inheritance_view_path, trestle_root)

        # Filter the ssp implemented requirements by the catalog specified
        catalog_api: CatalogAPI = CatalogAPI(catalog=resolved_catalog)
        ssp_inheritance_api.write_inheritance_as_markdown(ssp_href, catalog_api)


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

    @staticmethod
    def _get_ssp_component(ssp: ossp.SystemSecurityPlan, gen_comp: generic.GenericComponent) -> ossp.SystemComponent:
        for component in as_list(ssp.system_implementation.components):
            if component.title == gen_comp.title:
                return component
        # if this is a new system component assign its status as operational by default
        # the status of the system components are not stored in the markdown
        gen_comp.status.state = const.STATUS_OPERATIONAL
        new_component = gen_comp.as_system_component()
        return new_component

    @staticmethod
    def _merge_by_comps(stat: ossp.Statement, statement: ossp.Statement, set_params: List[ossp.SetParameter]) -> None:
        for by_comp in as_list(statement.by_components):
            found = False
            for dest_by_comp in as_list(stat.by_components):
                if dest_by_comp.component_uuid == by_comp.component_uuid:
                    dest_by_comp.description = by_comp.description
                    dest_by_comp.props = as_list(dest_by_comp.props)
                    dest_by_comp.props.extend(as_list(statement.props))
                    dest_by_comp.props = none_if_empty(ControlInterface.clean_props(by_comp.props))
                    dest_by_comp.implementation_status = by_comp.implementation_status
                    dest_by_comp.set_parameters = none_if_empty(set_params)
                    found = True
                    break
            if not found:
                stat.by_components = as_list(stat.by_components)
                by_comp.set_parameters = none_if_empty(set_params)
                stat.by_components.append(by_comp)

    @staticmethod
    def _merge_statement(
        imp_req: ossp.ImplementedRequirement,
        statement: generic.GenericStatement,
        set_params: List[ossp.SetParameter],
    ) -> None:
        """Merge the generic statement into the statements of the imp_req."""
        # if the statement id is already in the imp_req, merge its by_comps into the existing statement
        for stat in as_list(imp_req.statements):
            if stat.statement_id == statement.statement_id:
                SSPAssemble._merge_by_comps(stat, statement, set_params)
                return
        # otherwise just ad the statement - but only if it has by_comps
        if statement.by_components:
            imp_req.statements = as_list(imp_req.statements)
            imp_req.statements.append(statement)

    @staticmethod
    def _merge_imp_req_into_imp_req(
        imp_req: ossp.ImplementedRequirement,
        gen_imp_req: generic.GenericImplementedRequirement,
        set_params: List[ossp.SetParameter]
    ) -> None:
        """Merge comp def imp req into existing imp req."""
        # convert generic imp req from comp defs into ssp form
        src_imp_req = gen_imp_req.as_ssp()
        imp_req.props = none_if_empty(
            ControlInterface.clean_props(gen_imp_req.props, remove_imp_status=True, remove_all_rule_info=True)
        )
        for statement in as_list(src_imp_req.statements):
            SSPAssemble._merge_statement(imp_req, statement, set_params)

    @staticmethod
    def _get_params_for_rules(context: ControlContext, rules_list: List[str],
                              set_params: List[ossp.SetParameter]) -> List[ossp.SetParameter]:
        """Get all set_params needed by the rules along with non-rule set_params."""
        needed_param_ids: Set[str] = set()
        rule_dict = context.rules_params_dict.get(context.comp_name, {})
        # find param_ids needed by rules
        for rule_id in rules_list:
            # get list of param_ids associated with this rule_id
            param_ids = [param['name'] for param in rule_dict.values() if param['rule-id'] == rule_id]
            needed_param_ids.update(param_ids)
        all_rule_param_ids = [param['name'] for param in rule_dict.values()]
        # any set_param that isn't associated with a rule should be included as a normal control set param with no rule
        for set_param in set_params:
            if set_param.param_id not in all_rule_param_ids:
                needed_param_ids.add(set_param.param_id)
        param_ids_list = sorted(needed_param_ids)
        needed_set_params: List[ossp.SetParameter] = []
        for param_id in param_ids_list:
            set_param = None
            for sp in set_params:
                if sp.param_id == param_id:
                    set_param = sp
                    break
            if set_param:
                needed_set_params.append(set_param)
            else:
                logger.warning(f'No set param found for param {param_id}')
        return needed_set_params

    @staticmethod
    def _add_imp_req_to_ssp(
        ssp: ossp.SystemSecurityPlan,
        gen_comp: generic.GenericComponent,
        gen_imp_req: generic.GenericImplementedRequirement,
        set_params: List[ossp.SetParameter],
        context: ControlContext
    ) -> None:
        """Add imp req from control implementation into new ssp being assembled."""
        # the incoming gen_imp_req comes directly from the comp def
        # but the imp_req here is pulled from the ssp and created if not already there
        imp_req = CatalogReader._get_imp_req_for_control(ssp, gen_imp_req.control_id)
        local_set_params = as_list(set_params)[:]
        local_set_params.extend(as_list(imp_req.set_parameters))
        local_set_params = ControlInterface.uniquify_set_params(local_set_params)
        # get any rules set at control level, if present
        rules_list, _ = ControlInterface.get_rule_list_for_item(gen_imp_req)  # type: ignore
        # There should be no rule content at top level of imp_req in ssp so strip them out
        imp_req.props = none_if_empty(
            ControlInterface.clean_props(gen_imp_req.props, remove_imp_status=True, remove_all_rule_info=True)
        )
        # if we have rules applying or need to make set_params, we need to make a by_comp
        control_set_params = SSPAssemble._get_params_for_rules(context, rules_list, local_set_params)
        if rules_list or control_set_params:
            by_comp = gens.generate_sample_model(ossp.ByComponent)
            by_comp.component_uuid = gen_comp.uuid
            by_comp.description = gen_imp_req.description
            by_comp.set_parameters = none_if_empty(control_set_params)
            by_comp.implementation_status = ControlInterface.get_status_from_props(gen_imp_req)  # type: ignore
            by_comp.props = none_if_empty(ControlInterface.clean_props(gen_imp_req.props))
            imp_req.by_components = as_list(imp_req.by_components)
            imp_req.by_components.append(by_comp)
        # each statement in ci corresponds to by_comp in an ssp imp req
        # so insert the new by_comp directly into the ssp, generating parts as needed
        imp_req.statements = as_list(imp_req.statements)
        for statement in as_list(gen_imp_req.statements):
            if ControlInterface.item_has_rules(statement):  # type: ignore
                imp_req = CatalogReader._get_imp_req_for_statement(ssp, gen_imp_req.control_id, statement.statement_id)
                by_comp = CatalogReader._get_by_comp_from_imp_req(imp_req, statement.statement_id, gen_comp.uuid)
                by_comp.description = statement.description
                by_comp.props = none_if_empty(ControlInterface.clean_props(statement.props))
                rules_list, _ = ControlInterface.get_rule_list_for_item(statement)  # type: ignore
                by_comp.set_parameters = none_if_empty(
                    SSPAssemble._get_params_for_rules(context, rules_list, local_set_params)
                )
        imp_req.statements = none_if_empty(imp_req.statements)
        ssp.control_implementation.implemented_requirements = as_list(
            ssp.control_implementation.implemented_requirements
        )

    @staticmethod
    def _merge_imp_req_into_ssp(
        ssp: ossp.SystemSecurityPlan,
        gen_imp_req: generic.GenericImplementedRequirement,
        set_params: List[ossp.SetParameter],
    ) -> None:
        """Merge the new imp_reqs into the ssp."""
        for imp_req in as_list(ssp.control_implementation.implemented_requirements):
            if imp_req.control_id == gen_imp_req.control_id:
                SSPAssemble._merge_imp_req_into_imp_req(imp_req, gen_imp_req, set_params)
                return
        new_imp_req = gen_imp_req.as_ssp()
        imp_req.props = none_if_empty(
            ControlInterface.clean_props(gen_imp_req.props, remove_imp_status=True, remove_all_rule_info=True)
        )
        ssp.control_implementation.implemented_requirements.append(new_imp_req)

    def _merge_comp_defs(
        self,
        ssp: ossp.SystemSecurityPlan,
        comp_dict: Dict[str, generic.GenericComponent],
        context: ControlContext,
        catalog_interface: CatalogInterface
    ) -> None:
        """Merge the original generic comp defs into the ssp."""
        all_comps: List[ossp.SystemComponent] = []
        # determine if this is a new and empty ssp
        new_ssp = not ssp.control_implementation.implemented_requirements
        for _, gen_comp in comp_dict.items():
            context.comp_name = gen_comp.title
            all_ci_props: List[com.Property] = []
            ssp_comp = SSPAssemble._get_ssp_component(ssp, gen_comp)
            set_params: List[ossp.SetParameter] = []
            for ci in as_list(gen_comp.control_implementations):
                all_ci_props.extend(as_list(ci.props))
                # get the list of set_params in the control implementation - for this component
                for sp in as_list(ci.set_parameters):
                    set_params.append(sp.to_ssp())
                for imp_req in as_list(ci.implemented_requirements):
                    # ignore any controls not in the ssp profile (resolved catalog)
                    if not catalog_interface.get_control(imp_req.control_id):
                        logger.debug(f'Ignoring imp_req for control {imp_req.control_id} not in ssp profile')
                        continue
                    if new_ssp:
                        SSPAssemble._add_imp_req_to_ssp(ssp, gen_comp, imp_req, set_params, context)
                    else:
                        # compile all new uuids for new component definitions
                        comp_uuids = [x.uuid for x in comp_dict.values()]
                        for imp_requirement in as_list(ssp.control_implementation.implemented_requirements):
                            to_delete = []
                            for i, by_comp in enumerate(imp_requirement.by_components):
                                if by_comp.component_uuid not in comp_uuids:
                                    logger.warning(
                                        f'By_component {by_comp.component_uuid} removed from implemented requirement '
                                        f'{imp_requirement.control_id} because the corresponding component is not in '
                                        'the specified compdefs '
                                    )
                                    to_delete.append(i)
                            if to_delete:
                                delete_list_from_list(imp_requirement.by_components, to_delete)
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
            comp_def, _ = ModelUtils.load_model_for_class(trestle_root, comp_name, comp.ComponentDefinition)
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
            res_cat = ProfileResolver.get_resolved_profile_catalog(
                trestle_root, profile_href, param_rep=ParameterRep.LEAVE_MOUSTACHE
            )
            catalog_interface = CatalogInterface(res_cat)

            new_file_content_type = FileContentType.JSON

            # if output ssp already exists, load it to see if new one is different
            existing_ssp: Optional[ossp.SystemSecurityPlan] = None
            new_ssp_path = ModelUtils.get_model_path_for_name_and_class(
                trestle_root, new_ssp_name, ossp.SystemSecurityPlan
            )
            if new_ssp_path:
                _, _, existing_ssp = ModelUtils.load_distributed(new_ssp_path, trestle_root)
                new_file_content_type = FileContentType.path_to_content_type(new_ssp_path)

            ssp: ossp.SystemSecurityPlan

            # if orig ssp exists - need to load it rather than instantiate new one
            orig_ssp_path = ModelUtils.get_model_path_for_name_and_class(
                trestle_root, orig_ssp_name, ossp.SystemSecurityPlan
            )

            context = ControlContext.generate(ContextPurpose.SSP, True, trestle_root, md_path)
            context.comp_def_name_list = comma_sep_to_list(args.compdefs)
            part_id_map_by_id = catalog_interface.get_statement_part_id_map(False)
            catalog_interface.generate_control_rule_info(part_id_map_by_id, context)

            # load all original comp defs
            # only additions from markdown will be imp_req prose and status
            # and param vals
            # if this is a new ssp then create system component in the comp_dict
            comp_dict = SSPAssemble._build_comp_dict_from_comp_defs(
                trestle_root, context.comp_def_name_list, not orig_ssp_path
            )

            part_id_map_by_label = catalog_interface.get_statement_part_id_map(True)

            # if ssp already exists use it as container for new content
            if orig_ssp_path:
                # load the existing json ssp
                _, _, ssp = ModelUtils.load_distributed(orig_ssp_path, trestle_root)
                # add the This System comp to the comp dict so its uuid is known
                sys_comp = SSPAssemble._get_this_system_as_gen_comp(ssp)
                if not sys_comp:
                    raise TrestleError('Original ssp has no system component.')
                comp_dict[const.SSP_MAIN_COMP_NAME] = sys_comp

                # Verifies older compdefs in an ssp no longer exist in newly provided ones
                comp_titles = [x.title for x in comp_dict.values()]
                ssp_sys_imp_comps = ssp.system_implementation.components
                diffs = [x for x in ssp_sys_imp_comps if x.title not in comp_titles]
                if diffs:
                    for diff in diffs:
                        logger.warning(
                            f'Component named: {diff.title} was removed from system components from ssp '
                            'because the corresponding component is not in '
                            'the specified compdefs '
                        )
                    index_list = [ssp_sys_imp_comps.index(value) for value in diffs if value in ssp_sys_imp_comps]
                    delete_list_from_list(ssp.system_implementation.components, index_list)

                self._merge_comp_defs(ssp, comp_dict, context, catalog_interface)
                CatalogReader.read_ssp_md_content(md_path, ssp, comp_dict, part_id_map_by_label, context)

                new_file_content_type = FileContentType.path_to_content_type(orig_ssp_path)
            else:
                # create a sample ssp to hold all the parts
                ssp = gens.generate_sample_model(ossp.SystemSecurityPlan)
                ssp.control_implementation.implemented_requirements = []
                ssp.control_implementation.description = const.SSP_SYSTEM_CONTROL_IMPLEMENTATION_TEXT
                ssp.system_implementation.components = []
                self._merge_comp_defs(ssp, comp_dict, context, catalog_interface)
                CatalogReader.read_ssp_md_content(md_path, ssp, comp_dict, part_id_map_by_label, context)

                import_profile: ossp.ImportProfile = gens.generate_sample_model(ossp.ImportProfile)
                import_profile.href = const.REPLACE_ME
                ssp.import_profile = import_profile

            # now that we know the complete list of needed components, add them to the sys_imp
            # TODO if the ssp already existed then components may need to be removed if not ref'd by imp_reqs
            self._generate_roles_in_metadata(ssp)

            # If this is a leveraging SSP, update it with the retrieved the exports from the leveraged SSP
            inheritance_markdown_path = md_path.joinpath(const.INHERITANCE_VIEW_DIR)
            if os.path.exists(inheritance_markdown_path):
                SSPInheritanceAPI(inheritance_markdown_path, trestle_root).update_ssp_inheritance(ssp)

            ssp.import_profile.href = profile_href

            if args.version:
                ssp.metadata.version = args.version

            if ModelUtils.models_are_equivalent(existing_ssp, ssp):
                logger.info('No changes to assembled ssp so ssp not written out.')
                return CmdReturnCodes.SUCCESS.value

            if args.regenerate:
                ssp, _, _ = ModelUtils.regenerate_uuids(ssp)
            ModelUtils.update_last_modified(ssp)
            # validate model rules before saving
            args_validate = argparse.Namespace(mode=const.VAL_MODE_RULES)
            validator: Validator = validator_factory.get(args_validate)
            if not validator.model_is_valid(ssp, True, trestle_root):
                logger.error(
                    'Validation of file to be imported did not pass. Rule parameter values validation failed, '
                    'please check values are correct for shared parameters in current model'
                )
                return CmdReturnCodes.COMMAND_ERROR.value
            # write out the ssp as json
            ModelUtils.save_top_level_model(ssp, trestle_root, new_ssp_name, new_file_content_type)

            return CmdReturnCodes.SUCCESS.value

        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while assembling SSP')


class SSPFilter(AuthorCommonCommand):
    """
    Filter the controls in an ssp.

    The filtered ssp is based on controls included by the following:
    profile, components, implementation status, and/or control origination.
    """

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
        is_help_str = 'Comma-delimited list of control implementation statuses to include in filtered ssp.'
        self.add_argument('-is', '--implementation-status', help=is_help_str, required=False, type=str)
        co_help_str = 'Comma-delimited list of control origination values to include in filtered ssp.'
        self.add_argument('-co', '--control-origination', help=co_help_str, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = pathlib.Path(args.trestle_root)
            comp_names: Optional[List[str]] = None
            impl_status_values: Optional[List[str]] = None
            co_values: Optional[List[str]] = None

            if not (args.components or args.implementation_status or args.profile or args.control_origination):
                logger.warning(
                    'You must specify at least one, or a combination of: profile, list of component names'
                    ', list of implementation statuses, or list of control origination values for ssp-filter.'
                )
                return CmdReturnCodes.COMMAND_ERROR.value

            if args.components:
                comp_names = args.components.split(':')

            if args.implementation_status:
                impl_status_values = args.implementation_status.split(',')
                allowed_is_values = {
                    const.STATUS_PLANNED,
                    const.STATUS_PARTIAL,
                    const.STATUS_IMPLEMENTED,
                    const.STATUS_ALTERNATIVE,
                    const.STATUS_NOT_APPLICABLE
                }
                allowed_is_string = ', '.join(str(item) for item in allowed_is_values)
                for impl_status in impl_status_values:
                    if impl_status not in allowed_is_values:
                        logger.warning(
                            f'Provided implementation status "{impl_status}" is invalid.\n'
                            f'Please use the following for ssp-filter: {allowed_is_string}'
                        )
                        return CmdReturnCodes.COMMAND_ERROR.value

            if args.control_origination:
                co_values = args.control_origination.split(',')
                allowed_co_values = {
                    const.ORIGINATION_ORGANIZATION,
                    const.ORIGINATION_SYSTEM_SPECIFIC,
                    const.ORIGINATION_INHERITED,
                    const.ORIGINATION_CUSTOMER_CONFIGURED,
                    const.ORIGINATION_CUSTOMER_PROVIDED
                }
                allowed_co_string = ', '.join(str(item) for item in allowed_co_values)
                for co in co_values:
                    if co not in allowed_co_values:
                        logger.warning(
                            f'Provided control origination "{co}" is invalid.\n'
                            f'Please use the following for ssp-filter: {allowed_co_string}'
                        )
                        return CmdReturnCodes.COMMAND_ERROR.value

            return self.filter_ssp(
                trestle_root,
                args.name,
                args.profile,
                args.output,
                args.regenerate,
                args.version,
                comp_names,
                impl_status_values,
                co_values
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
        components: Optional[List[str]] = None,
        implementation_status: Optional[List[str]] = None,
        control_origination: Optional[List[str]] = None
    ) -> int:
        """
        Filter the ssp and output new ssp.

        The filtered ssp is based on controls included by the following:
        profile, components, implementation status, and/or control origination.

        Args:
            trestle_root: root directory of the trestle workspace
            ssp_name: name of the ssp model
            profile_name: name of the optional profile model used for filtering
            out_name: name of the output ssp model with filtered controls
            regenerate: whether to regenerate the uuid's in the ssp
            version: new version for the model
            components: optional list of component names used for filtering
            implementation_status: optional list of implementation statuses for filtering
            control_origination: optional list of control origination values for filtering

        Returns:
            0 on success, 1 otherwise
        """
        # load the ssp
        ssp: ossp.SystemSecurityPlan
        ssp, _ = load_validate_model_name(trestle_root, ssp_name, ossp.SystemSecurityPlan, FileContentType.JSON)
        profile_path = ModelUtils.get_model_path_for_name_and_class(
            trestle_root, profile_name, prof.Profile, FileContentType.JSON
        )

        if components:
            raw_comp_names = [ControlReader.simplify_name(name) for name in components]
            comp_uuids: List[str] = []
            for component in ssp.system_implementation.components:
                if ControlReader.simplify_name(component.title) in raw_comp_names:
                    comp_uuids.append(component.uuid)

            if len(comp_uuids) != len(components):
                raise TrestleError(
                    f'Unable to filter the ssp because one of the components {components} is not in the ssp.'
                )

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

        # filter implemented requirements and statements by component implementation status
        # this will remove any implemented requirements without statements or by_component fields set
        if implementation_status:
            new_imp_reqs: List[ossp.ImplementedRequirement] = []
            # these are all required to be present
            for imp_req in ssp.control_implementation.implemented_requirements:
                new_by_comps: List[ossp.ByComponent] = []
                # by_comps is optional
                for by_comp in as_list(imp_req.by_components):
                    if by_comp.implementation_status.state in implementation_status:
                        new_by_comps.append(by_comp)
                imp_req.by_components = none_if_empty(new_by_comps)

                new_statements: List[ossp.Statement] = []
                for statement in as_list(imp_req.statements):
                    new_by_comps: List[ossp.ByComponent] = []
                    for by_comp in as_list(statement.by_components):
                        if by_comp.implementation_status.state in implementation_status:
                            new_by_comps.append(by_comp)
                    statement.by_components = none_if_empty(new_by_comps)
                    if statement.by_components is not None:
                        new_statements.append(statement)
                imp_req.statements = none_if_empty(new_statements)

                if imp_req.by_components is not None or imp_req.statements is not None:
                    new_imp_reqs.append(imp_req)

            ssp.control_implementation.implemented_requirements = new_imp_reqs

        # filter implemented requirements by control origination property.
        # this will remove any implemented requirements without the control origination
        # property set
        if control_origination:
            new_imp_reqs: List[ossp.ImplementedRequirement] = []

            for imp_requirement in ssp.control_implementation.implemented_requirements:
                if imp_requirement.props:
                    for prop in imp_requirement.props:
                        if prop.name == const.CONTROL_ORIGINATION and prop.value in control_origination:
                            new_imp_reqs.append(imp_requirement)
                            # only add the imp requirement one time
                            break

            ssp.control_implementation.implemented_requirements = new_imp_reqs

        if version:
            ssp.metadata.version = version

        existing_ssp_path = ModelUtils.get_model_path_for_name_and_class(
            trestle_root, out_name, ossp.SystemSecurityPlan
        )
        if existing_ssp_path is not None:
            existing_ssp, _ = load_validate_model_name(trestle_root, out_name, ossp.SystemSecurityPlan)
            if ModelUtils.models_are_equivalent(existing_ssp, ssp):  # type: ignore
                logger.info('No changes to filtered ssp so ssp not written out.')
                return CmdReturnCodes.SUCCESS.value

        if regenerate:
            ssp, _, _ = ModelUtils.regenerate_uuids(ssp)

        ModelUtils.update_last_modified(ssp)

        ModelUtils.save_top_level_model(ssp, trestle_root, out_name, FileContentType.JSON)

        return CmdReturnCodes.SUCCESS.value
