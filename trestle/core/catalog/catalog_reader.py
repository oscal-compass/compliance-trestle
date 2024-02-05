# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Provide interface to read catalog from markdown back to OSCAL."""

import logging
import pathlib
from typing import Any, Dict, List, Optional, Tuple, Union

import trestle.common.const as const
import trestle.core.generators as gens
import trestle.core.generic_oscal as generic
import trestle.oscal.catalog as cat
import trestle.oscal.common as com
import trestle.oscal.component as comp
from trestle.common.common_types import TypeWithSetParams
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_list, none_if_empty
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.control_context import ControlContext
from trestle.core.control_interface import CompDict, ComponentImpInfo, ControlInterface
from trestle.core.control_reader import ControlReader
from trestle.oscal import profile as prof
from trestle.oscal import ssp as ossp

logger = logging.getLogger(__name__)


class CatalogReader():
    """
    Catalog reader.

    Catalog reader handles all operations related to
    reading catalog from markdown.
    """

    def __init__(self, catalog_interface: CatalogInterface):
        """Initialize catalog reader."""
        self._catalog_interface = catalog_interface

    def read_additional_content(
        self,
        md_path: pathlib.Path,
        required_sections_list: List[str],
        label_map: Dict[str, Dict[str, str]],
        sections_dict: Dict[str, str],
        write_mode: bool
    ) -> Tuple[List[prof.Alter], Dict[str, Any], Dict[str, str]]:
        """Read all markdown controls and return list of alters plus control param dict and param sort map."""
        alters_map: Dict[str, prof.Alter] = {}
        final_param_dict: Dict[str, Any] = {}
        param_sort_map: Dict[str, str] = {}
        for group_path in CatalogInterface._get_group_ids_and_dirs(md_path).values():
            for control_file in group_path.glob('*.md'):
                sort_id, control_alters, control_param_dict = ControlReader.read_editable_content(
                    control_file,
                    required_sections_list,
                    label_map,
                    sections_dict,
                    write_mode
                )
                alters_map[sort_id] = control_alters
                for param_id, param_dict in control_param_dict.items():
                    # if profile_values are present, overwrite values with them
                    if const.PROFILE_VALUES in param_dict:
                        if param_dict[const.PROFILE_VALUES] != [] and param_dict[const.PROFILE_VALUES] is not None:
                            if not write_mode and const.REPLACE_ME_PLACEHOLDER in param_dict[const.PROFILE_VALUES]:
                                param_dict[const.PROFILE_VALUES].remove(const.REPLACE_ME_PLACEHOLDER)
                            if param_dict[const.PROFILE_VALUES] != [] and param_dict[const.PROFILE_VALUES] is not None:
                                param_dict[const.VALUES] = param_dict[const.PROFILE_VALUES]
                        if not write_mode:
                            param_dict.pop(const.PROFILE_VALUES)
                    # verifies if at control profile edition the param value origin was modified
                    # through the profile-param-value-origin tag
                    if const.PROFILE_PARAM_VALUE_ORIGIN in param_dict:
                        if param_dict[const.PROFILE_PARAM_VALUE_ORIGIN] != const.REPLACE_ME_PLACEHOLDER:
                            param_dict[const.PARAM_VALUE_ORIGIN] = param_dict[const.PROFILE_PARAM_VALUE_ORIGIN]
                            param_dict.pop(const.PROFILE_PARAM_VALUE_ORIGIN)
                        else:
                            # removes replace me placeholder and profile-param-value-origin as it was not modified
                            param_dict.pop(const.PROFILE_PARAM_VALUE_ORIGIN)
                            # validates param-value-origin is in dict to remove it
                            # because a value wasn´t provided and it shouldn´t be inheriting value from parent
                            if const.PARAM_VALUE_ORIGIN in param_dict:
                                param_dict.pop(const.PARAM_VALUE_ORIGIN)
                    final_param_dict[param_id] = param_dict
                    param_sort_map[param_id] = sort_id
        new_alters: List[prof.Alter] = []
        # fill the alters according to the control sorting order
        for key in sorted(alters_map.keys()):
            new_alters.extend(alters_map[key])
        return new_alters, final_param_dict, param_sort_map

    def read_catalog_from_markdown(self, md_path: pathlib.Path, set_parameters_flag: bool) -> cat.Catalog:
        """
        Read the groups and catalog controls from the given directory.

        This will overwrite the existing groups and controls in the catalog.
        """
        id_map = CatalogInterface._get_group_ids_and_dirs(md_path)
        groups: List[cat.Group] = []
        # read each group dir
        for group_id, group_dir in id_map.items():
            control_list_raw = []
            group_title = ''
            # Need to get group title from at least one control in this directory
            # All controls in dir should have same group title
            # Set group title to the first one found and warn if different non-empty title appears
            # Controls with empty group titles are tolerated but at least one title must be present or warning given
            # The special group with no name that has the catalog as parent is just a list and has no title
            for control_path in group_dir.glob('*.md'):
                control, control_group_title = ControlReader.read_control(control_path, set_parameters_flag)
                if control_group_title:
                    if group_title:
                        if control_group_title != group_title:
                            logger.warning(
                                f'Control {control.id} group title {control_group_title} differs from {group_title}'
                            )
                    else:
                        group_title = control_group_title
                control_list_raw.append(control)
            control_list = sorted(control_list_raw, key=lambda control: ControlInterface.get_sort_id(control))
            if group_id:
                if not group_title:
                    logger.warning(
                        f'No group title found in controls for group {group_id}.  The title will be recovered if assembling into an existing catalog with the group title defined.'  # noqa E501
                    )
                new_group = cat.Group(id=group_id, title=group_title)
                new_group.controls = none_if_empty(control_list)
                groups.append(new_group)
            else:
                # if the list of controls has no group id it also has no title and is just the controls of the catalog
                self._catalog_interface._catalog.controls = none_if_empty(control_list)
        self._catalog_interface._catalog.groups = none_if_empty(groups)
        self._catalog_interface._create_control_dict()
        self._catalog_interface._catalog.params = none_if_empty(self._catalog_interface._catalog.params)
        return self._catalog_interface._catalog

    @staticmethod
    def read_catalog_imp_reqs(md_path: pathlib.Path, context: ControlContext) -> List[comp.ImplementedRequirement]:
        """Read the full set of control implemented requirements from markdown.

        Args:
            md_path: Path to the markdown control files, with directories for each group
            context: Context for the operation

        Returns:
            List of implemented requirements gathered from each control

        Notes:
            As the controls are read into the catalog the needed components are added if not already available.
            avail_comps provides the mapping of component name to the actual component.
            This is only used during component assemble and only for updating one component
        """
        imp_req_map: Dict[str, comp.ImplementedRequirement] = {}
        for group_path in CatalogInterface._get_group_ids_and_dirs(md_path).values():
            for control_file in group_path.glob('*.md'):
                sort_id, imp_req = ControlReader.read_implemented_requirement(control_file, context)
                imp_req_map[sort_id] = imp_req
        return [imp_req_map[key] for key in sorted(imp_req_map.keys())]

    @staticmethod
    def _get_imp_req_for_control(ssp: ossp.SystemSecurityPlan, control_id: str) -> ossp.ImplementedRequirement:
        for imp_req in as_list(ssp.control_implementation.implemented_requirements):
            if imp_req.control_id == control_id:
                return imp_req
        imp_req = gens.generate_sample_model(ossp.ImplementedRequirement)
        imp_req.control_id = control_id
        ssp.control_implementation.implemented_requirements = as_list(
            ssp.control_implementation.implemented_requirements
        )
        ssp.control_implementation.implemented_requirements.append(imp_req)
        return imp_req

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
            control_imp_req.statements = None
            ssp.control_implementation.implemented_requirements = as_list(
                ssp.control_implementation.implemented_requirements
            )
            ssp.control_implementation.implemented_requirements.append(control_imp_req)
        statement = gens.generate_sample_model(ossp.Statement)
        statement.statement_id = statement_id
        statement.by_components = None
        control_imp_req.statements = as_list(control_imp_req.statements)
        control_imp_req.statements.append(statement)
        return control_imp_req

    @staticmethod
    def _get_by_comp_from_imp_req(
        imp_req: ossp.ImplementedRequirement, statement_id: str, comp_uuid: str
    ) -> ossp.ByComponent:
        if statement_id:
            for statement in as_list(imp_req.statements):
                if statement.statement_id == statement_id:
                    for by_comp in as_list(statement.by_components):
                        if by_comp.component_uuid == comp_uuid:
                            return by_comp
                    # didnt find bycomp so need to make one
                    by_comp = gens.generate_sample_model(ossp.ByComponent)
                    by_comp.component_uuid = comp_uuid
                    by_comp.implementation_status = com.ImplementationStatus(state=const.STATUS_PLANNED)
                    statement.by_components = as_list(statement.by_components)
                    statement.by_components.append(by_comp)
                    return by_comp
        else:
            for by_comp in as_list(imp_req.by_components):
                if by_comp.component_uuid == comp_uuid:
                    return by_comp
            by_comp = gens.generate_sample_model(ossp.ByComponent)
            by_comp.component_uuid = comp_uuid
            by_comp.implementation_status = com.ImplementationStatus(state=const.STATUS_PLANNED)
            imp_req.by_components = as_list(imp_req.by_components)
            imp_req.by_components.append(by_comp)
            return by_comp
        raise TrestleError(f'Internal error seeking by_comp for component {comp_uuid} and statement {statement_id}')

    @staticmethod
    def _read_comp_info_from_md(control_file_path: pathlib.Path,
                                context: ControlContext) -> Tuple[Dict[str, Any], CompDict]:
        md_header = {}
        comp_dict = {}
        if control_file_path.exists():
            md_header, comp_dict = ControlReader.read_control_info_from_md(control_file_path, context)
        return md_header, comp_dict

    @staticmethod
    def _update_ssp_with_comp_info(
        ssp: ossp.SystemSecurityPlan,
        control_id: str,
        gen_comp: generic.GenericComponent,
        comp_info_dict: Dict[str, ComponentImpInfo],
        part_id_map_by_label: Dict[str, Dict[str, str]]
    ) -> None:
        # get imp req for control and find one with by_comp, creating if needed
        imp_req = CatalogReader._get_imp_req_for_control(ssp, control_id)
        # if control has no parts it will not have part id map and bycomps will go at control level
        control_part_id_map = part_id_map_by_label.get(control_id, {})
        for label, comp_info in comp_info_dict.items():
            if label:
                part_id = control_part_id_map.get(label, '')
            else:
                part_id = ''
            by_comp = CatalogReader._get_by_comp_from_imp_req(imp_req, part_id, gen_comp.uuid)
            by_comp.description = comp_info.prose
            by_comp.implementation_status = comp_info.status

    @staticmethod
    def _insert_set_param_into_by_comps(
        item: Union[ossp.ImplementedRequirement, ossp.ByComponent],
        rule_id: str,
        param_name: str,
        param_values: List[str],
        comp_uuid: str
    ) -> None:
        for by_comp in as_list(item.by_components):
            if by_comp.component_uuid == comp_uuid:
                for prop in as_list(by_comp.props):
                    if prop.name == const.RULE_ID and prop.value == rule_id:
                        found = False
                        for sp in as_list(by_comp.set_parameters):
                            if sp.param_id == param_name:
                                sp.values = param_values
                                found = True
                                break
                        if not found:
                            sp = ossp.SetParameter(param_id=param_name, values=param_values)
                            by_comp.set_parameters = as_list(by_comp.set_parameters)
                            by_comp.set_parameters.append(sp)

    @staticmethod
    def _insert_param_dict_in_imp_req(
        imp_req: ossp.ImplementedRequirement,
        param_dict: Dict[str, str],
        comp_name: str,
        md_header: Dict[str, Dict[str, str]],
        comp_uuid: str
    ):
        """Insert the param in the by_comps that are supported by the rule."""
        # given param name find rule_id in comp name header entry
        # then find all statements with by_comp that have that rule id in props
        rules_dict = md_header.get(const.RULES_PARAMS_TAG, {})
        comp_rules_params = rules_dict.get(comp_name, [])
        param_name = param_dict['name']
        param_values = param_dict['values']
        for comp_rule_param in comp_rules_params:
            if comp_rule_param['name'] == param_name:
                rule_id = comp_rule_param[const.HEADER_RULE_ID]
                CatalogReader._insert_set_param_into_by_comps(imp_req, rule_id, param_name, param_values, comp_uuid)
                for statement in as_list(imp_req.statements):
                    CatalogReader._insert_set_param_into_by_comps(
                        statement, rule_id, param_name, param_values, comp_uuid
                    )

    @staticmethod
    def _add_set_params_to_item(param_dict: Dict[str, str], item: TypeWithSetParams, param_id: str) -> None:
        value_list = param_dict[const.SSP_VALUES]
        param_values = value_list
        new_sp_list = []
        for sp in as_list(item.set_parameters):
            if sp.param_id != param_id:
                new_sp_list.append(sp)
        item.set_parameters = new_sp_list
        item.set_parameters.append(ossp.SetParameter(param_id=param_id, values=param_values))

    @staticmethod
    def _update_ssp_with_md_header(
        ssp: ossp.SystemSecurityPlan,
        control_id: str,
        comp_dict: Dict[str, generic.GenericComponent],
        md_header: Dict[str, Dict[str, str]]
    ) -> None:
        """Update the ssp with info from the header of an ssp control markdown file."""
        # rules param vals go in bycomps of imp_req
        # param vals go directly in imp_req
        rules_param_vals_dict = md_header.get(const.COMP_DEF_RULES_PARAM_VALS_TAG, {})
        imp_req = CatalogReader._get_imp_req_for_control(ssp, control_id)
        for comp_name, param_dict_list in rules_param_vals_dict.items():
            for param_dict in as_list(param_dict_list):
                if const.SSP_VALUES in param_dict:
                    param_dict['values'] = param_dict['ssp-values']
                CatalogReader._insert_param_dict_in_imp_req(
                    imp_req, param_dict, comp_name, md_header, comp_dict[comp_name].uuid
                )
        param_vals_dict = md_header.get(const.SET_PARAMS_TAG, {})
        for param_id, param_dict in param_vals_dict.items():
            if const.SSP_VALUES in param_dict:
                CatalogReader._add_set_params_to_item(param_dict, imp_req, param_id)

    @staticmethod
    def read_ssp_md_content(
        md_path: pathlib.Path,
        ssp: ossp.SystemSecurityPlan,
        comp_dict: Dict[str, generic.GenericComponent],
        part_id_map_by_label: Dict[str, Dict[str, str]],
        context: ControlContext
    ) -> None:
        """
        Read md content into the ssp.

        Args:
            md_path: path to the catalog markdown
            ssp: ssp in which to insert the md content
            comp_dict: map of component name to component
            part_id_map_by_label: map label to part_id of control
            context: control context for the procedure

        Notes:
            The ssp should already contain info from the comp defs and this fills in selected content from md.
            The only content read from md is:
                ssp values in the comp def rules param vals of the header
                ssp values in the set-params of the header
                all prose for implementaton responses
                all status values
            ssp has components but may not have all needed imp reqs and bycomps
            know controlid and comp name in comp_dict
        """
        for group_path in CatalogInterface._get_group_ids_and_dirs(md_path).values():
            for control_file in group_path.glob('*.md'):
                skip = False
                for file in control_file.parents:
                    if file.name == const.INHERITANCE_VIEW_DIR:
                        skip = True
                        break
                if skip:
                    continue

                control_id = control_file.stem

                md_header, control_comp_dict = CatalogReader._read_comp_info_from_md(control_file, context)

                for comp_name, comp_info_dict in control_comp_dict.items():
                    if comp_name not in comp_dict:
                        err_msg = f'Control {control_id} references component {comp_name} not defined in a component-definition.'  # noqa E501
                        # give added guidance if no comp defs were specified at command line
                        if not context.comp_def_name_list:
                            err_msg += '  Please specify the names of any component-definitions needed for assembly.'
                        raise TrestleError(err_msg)
                    CatalogReader._update_ssp_with_comp_info(
                        ssp, control_id, comp_dict[comp_name], comp_info_dict, part_id_map_by_label
                    )
                CatalogReader._update_ssp_with_md_header(ssp, control_id, comp_dict, md_header)
