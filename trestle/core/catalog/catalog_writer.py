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
"""Provide interface to write OSCAL catalog to markdown."""

import copy
import logging
from typing import Any, Dict, List

import trestle.common.const as const
import trestle.oscal.catalog as cat
from trestle.common.list_utils import as_list, deep_get, none_if_empty
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.catalog.catalog_merger import CatalogMerger
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.core.control_interface import ComponentImpInfo, ControlInterface
from trestle.core.control_writer import ControlWriter
from trestle.oscal import common
from trestle.oscal import component as comp
from trestle.oscal import profile as prof

logger = logging.getLogger(__name__)


class CatalogWriter():
    """
    Catalog writer.

    Catalog writer handles all operation related to writing
    catalog to markdown.
    """

    def __init__(self, catalog_interface: CatalogInterface):
        """Initialize catalog writer."""
        self._catalog_interface = catalog_interface

    def write_catalog_as_profile_markdown(
        self, context: ControlContext, part_id_map: Dict[str, Dict[str, str]], md_alters: List[prof.Alter]
    ) -> None:
        """Write out the catalog as profile markdown."""
        # Get the list of params for this profile from its set_params
        # this is just from the set_params
        profile_set_param_dict = CatalogInterface._get_full_profile_param_dict(context.profile)

        # write out the controls
        for control in self._catalog_interface.get_all_controls_from_catalog(True):
            # here we do special handling of how set-parameters merge with the yaml header
            new_context = ControlContext.clone(context)
            new_context.merged_header = {}

            new_context = self._add_inherited_props_to_header(new_context, control.id)

            # get all params and vals for this control from the resolved profile catalog with block adds in effect
            control_param_dict = ControlInterface.get_control_param_dict(control, False)
            set_param_dict = self._construct_set_parameters_dict(profile_set_param_dict, control_param_dict, context)

            if set_param_dict:
                self._add_set_params_from_cli_yaml_header_to_header(new_context, set_param_dict, control_param_dict)

            elif const.SET_PARAMS_TAG in new_context.merged_header:
                # need to cull any params that are not in control
                pop_list: List[str] = []
                for key in new_context.merged_header[const.SET_PARAMS_TAG].keys():
                    if key not in control_param_dict:
                        pop_list.append(key)
                for pop in pop_list:
                    new_context.merged_header[const.SET_PARAMS_TAG].pop(pop)

            found_control_alters = [alter for alter in md_alters if alter.control_id == control.id]

            self._write_control_into_dir(new_context, control, part_id_map, found_control_alters)

    def _add_inherited_props_to_header(self, context: ControlContext, control_id: str) -> ControlContext:
        """Add inherited props to the merged header under inherited tag."""
        if context.inherited_props:
            inherited_props = context.inherited_props.get(control_id, None)
            if inherited_props:
                # build set in order of list so that duplicates will have final value stick, then convert to list
                unique_props = list({prop['name']: prop for prop in inherited_props}.values())
                context.merged_header[const.TRESTLE_INHERITED_PROPS_TAG] = unique_props

        return context

    def _add_set_params_from_cli_yaml_header_to_header(
        self, context: ControlContext, set_param_dict: Dict[str, str], control_param_dict: Dict[str, common.Parameter]
    ):
        """
        Add set parameters from the provided cli yaml header to the merged header.

        If overwrite-header-value flag is given
            - Set-parameters in set_param_dict will be overwritten with those in cli yaml header
            - No new params from the cli yaml header will be added <- TODO: Is this correct?
        If ohv flag is NOT given :
            - Set-parameters from the cli yaml header will be added
            - Will not overwrite params that are already in set_param_dict
        """
        if const.SET_PARAMS_TAG not in context.cli_yaml_header:
            context.cli_yaml_header[const.SET_PARAMS_TAG] = {}

        if context.cli_yaml_header:
            if context.overwrite_header_values:
                # update the control params with new values
                for key, value in context.cli_yaml_header[const.SET_PARAMS_TAG].items():
                    if key in control_param_dict:
                        set_param_dict[key] = value
            else:
                # update the control params with any values in yaml header not set in control
                # need to maintain order in the set_param_dict
                for key, value in context.cli_yaml_header[const.SET_PARAMS_TAG].items():
                    if key in control_param_dict and key not in set_param_dict:
                        set_param_dict[key] = value
        context.merged_header[const.SET_PARAMS_TAG] = set_param_dict

    def _construct_set_parameters_dict(
        self,
        profile_set_param_dict: Dict[str, common.Parameter],
        control_param_dict: Dict[str, Dict[str, Any]],
        context: ControlContext
    ) -> Dict[str, Dict[str, Any]]:
        """
        Build set-parameters dictionary from the given profile.modify.set-parameters and control.params.

        Resulting dictionary will have:
        - All parameters from the control where:
            - If control_param in profile.modify.set_params:
                - Display name (if exists) - from profile
                - Profile-values - from profile
                - Values - from control
            - If control_param is not in profile.modify.set_params:
                - Values - from control
        """
        set_param_dict: Dict[str, Dict[str, Any]] = {}
        for param_id, param_dict in control_param_dict.items():
            # if the param is in the full_param_dict, load its contents first and mark as profile-values
            display_name = ''
            if param_id in profile_set_param_dict:
                # get the param from the profile set_param
                param = profile_set_param_dict[param_id]
                display_name, _ = CatalogInterface._get_display_name_and_ns(param)
                # assign its contents to the dict
                new_dict = ModelUtils.parameter_to_dict(param, True)
                if const.VALUES in new_dict:
                    if context.purpose == ContextPurpose.PROFILE:
                        new_dict[const.PROFILE_VALUES] = new_dict[const.VALUES]
                        new_dict.pop(const.VALUES)
                # then insert the original, incoming values as values
                if param_id in control_param_dict:
                    orig_param = control_param_dict[param_id]
                    orig_dict = ModelUtils.parameter_to_dict(orig_param, True)
                    # pull only the values from the actual control dict
                    # all the other elements are from the profile set_param
                    new_dict[const.VALUES] = orig_dict.get(const.VALUES, None)
                    new_dict[const.GUIDELINES] = orig_dict.get(const.GUIDELINES, None)
                    if new_dict[const.VALUES] is None:
                        new_dict.pop(const.VALUES)
                    if new_dict[const.GUIDELINES] is None:
                        new_dict.pop(const.GUIDELINES)
            else:
                # if the profile doesnt change this param at all, show it in the header with values
                tmp_dict = ModelUtils.parameter_to_dict(param_dict, True)
                values = tmp_dict.get('values', None)
                # if values are None then don´t display them in the markdown
                if values is not None:
                    new_dict = {'id': param_id, 'values': values, const.PROFILE_VALUES: ['<REPLACE_ME>']}
                else:
                    new_dict = {'id': param_id, const.PROFILE_VALUES: ['<REPLACE_ME>']}
            new_dict.pop('id', None)
            # validates if there are aggregated parameter values to the current parameter
            aggregated_props = [prop for prop in as_list(param_dict.props) if prop.name == const.AGGREGATES]
            if aggregated_props != []:
                props_to_add = []
                for prop in aggregated_props:
                    props_to_add.append(prop.value)
                new_dict[const.AGGREGATES] = props_to_add
                new_dict.pop(const.PROFILE_VALUES, None)
            alt_identifier = [prop for prop in as_list(param_dict.props) if prop.name == const.ALT_IDENTIFIER]
            if alt_identifier != []:
                new_dict[const.ALT_IDENTIFIER] = alt_identifier[0].value
            # adds display name, if no display name then do not add to dict
            if display_name != '' and display_name is not None:
                new_dict[const.DISPLAY_NAME] = display_name
            key_order = (
                const.LABEL,
                const.GUIDELINES,
                const.VALUES,
                const.AGGREGATES,
                const.ALT_IDENTIFIER,
                const.DISPLAY_NAME,
                const.PROFILE_VALUES
            )
            ordered_dict = {k: new_dict[k] for k in key_order if k in new_dict.keys()}
            set_param_dict[param_id] = ordered_dict

        return set_param_dict

    @staticmethod
    def _fixup_param_dicts(context: ControlContext) -> None:
        """Merge info in the rules params dict and the rules param vals dict."""
        for comp_name, comp_dict in context.rules_params_dict.items():
            rules_dict = context.rules_dict.get(comp_name, {})
            for rule_id, param_dict in comp_dict.items():
                rule_name = deep_get(rules_dict, [rule_id, 'name'], 'unknown_rule_name')
                param_dict[const.HEADER_RULE_ID] = rule_name

    def write_catalog_as_ssp_markdown(self, context: ControlContext, part_id_map: Dict[str, Dict[str, str]]) -> None:
        """
        Write out the catalog as component markdown.

        Already have resolved profile catalog, but with no setparams from compdefs
        Load all control level rules and param values based on compdefs and profile values

        In memory:
        for each compdef:
            for each comp:
                load top level rules
                for each control_imp:
                    load set-params
                    for each imp_req (bound to 1 control):
                        load set-params
                        load control level rules and status
                        load part level rules and status
                        add as compinfo to control comp_dict

        """
        # generate rule and param info from the components
        self._catalog_interface.generate_control_rule_info(part_id_map, context)

        # now have all rules in context.rules_dict and all rules_params in context.rules_params_dict
        # all set-params per component for each control are in the cat interface
        # all comp-infos by control and part are in the cat interface
        #
        # can now write out catalog and pull from the markdown:
        # header for param values to set during assem
        # prose and status for This System
        # status for all parts that still have rules

        CatalogWriter._fixup_param_dicts(context)

        # remove items left after above loop
        context.component = None
        context.comp_name = None

        # get param_dict of set_params in profile
        profile_set_param_dict = CatalogInterface._get_full_profile_param_dict(context.profile)
        catalog_merger = CatalogMerger(self._catalog_interface)
        for control in self._catalog_interface.get_all_controls_from_dict():
            control_id = control.id
            context.comp_dict = self._catalog_interface._control_comp_dicts.get(control_id, {})
            control_file_path = self._catalog_interface.get_control_file_path(context.md_root, control_id)
            control_file_path.parent.mkdir(exist_ok=True, parents=True)
            # the catalog interface is from the resolved profile catalog
            control = self._catalog_interface.get_control(control_id)
            _, group_title, _ = self._catalog_interface.get_group_info_by_control(control_id)
            control_param_dict = ControlInterface.get_control_param_dict(control, False)
            set_param_dict = self._construct_set_parameters_dict(profile_set_param_dict, control_param_dict, context)
            new_context = ControlContext.clone(context)

            if set_param_dict:
                self._add_set_params_from_cli_yaml_header_to_header(new_context, set_param_dict, control_param_dict)

            elif const.SET_PARAMS_TAG in new_context.merged_header:
                # need to cull any params that are not in control
                pop_list: List[str] = []
                for key in new_context.merged_header[const.SET_PARAMS_TAG].keys():
                    if key not in control_param_dict:
                        pop_list.append(key)
                for pop in pop_list:
                    new_context.merged_header[const.SET_PARAMS_TAG].pop(pop)

            # merge the md_header and md_comp_dict with info in cat_interface for this control in new_context
            catalog_merger._merge_header_and_comp_dict(control, control_file_path, new_context)

            if const.COMP_DEF_RULES_PARAM_VALS_TAG in new_context.merged_header:
                for _, param_list in new_context.merged_header[const.COMP_DEF_RULES_PARAM_VALS_TAG].items():
                    for param_dict in param_list:
                        param_dict.pop(const.HEADER_RULE_ID, None)

            control_writer = ControlWriter()
            control_writer.write_control_for_editing(
                new_context, control, control_file_path.parent, group_title, part_id_map, []
            )

    def write_catalog_as_component_markdown(
        self, context: ControlContext, part_id_map: Dict[str, Dict[str, str]]
    ) -> None:
        """Write out the catalog as component markdown."""
        context.rules_dict = {}
        context.rules_params_dict = {}

        def _update_values(set_param: comp.SetParameter, control_param_dict) -> None:
            # set the param values based on the control_param_dict if available
            if set_param.param_id in control_param_dict:
                control_param_dict[set_param.param_id] = set_param

        control_ids_in_comp_imp = [
            imp_req.control_id for imp_req in as_list(context.control_implementation.implemented_requirements)
        ]

        missing_controls = set(control_ids_in_comp_imp).difference(self._catalog_interface.get_control_ids())
        if missing_controls:
            logger.warning(f'Component {context.comp_name} references controls {missing_controls} not in profile.')

        # get top level rule info applying to all controls
        comp_rules_dict, comp_rules_params_dict, _ = ControlInterface.get_rules_and_params_dict_from_item(context.component)  # noqa E501
        context.rules_dict[context.comp_name] = comp_rules_dict
        context.rules_params_dict.update(comp_rules_params_dict)
        for control_imp in as_list(context.component.control_implementations):
            control_imp_rules_dict, control_imp_rules_params_dict, _ = ControlInterface.get_rules_and_params_dict_from_item(control_imp)  # noqa E501
            context.rules_dict[context.comp_name].update(control_imp_rules_dict)
            comp_rules_params_dict = context.rules_params_dict.get(context.comp_name, {})
            comp_rules_params_dict.update(control_imp_rules_params_dict)
            context.rules_params_dict[context.comp_name] = comp_rules_params_dict
            ci_set_params = ControlInterface.get_set_params_from_item(control_imp)
            for imp_req in as_list(control_imp.implemented_requirements):
                control_part_id_map = part_id_map.get(imp_req.control_id, {})
                control_rules, statement_rules, _ = ControlInterface.get_rule_list_for_imp_req(imp_req)
                if control_rules or statement_rules:
                    if control_rules:
                        status = ControlInterface.get_status_from_props(imp_req)
                        comp_info = ComponentImpInfo(imp_req.description, control_rules, [], status)
                        self._catalog_interface.add_comp_info(imp_req.control_id, context.comp_name, '', comp_info)
                    set_params = copy.deepcopy(ci_set_params)
                    set_params.update(ControlInterface.get_set_params_from_item(imp_req))
                    for set_param in set_params.values():
                        self._catalog_interface.add_comp_set_param(imp_req.control_id, context.comp_name, set_param)
                    for statement in as_list(imp_req.statements):
                        rule_list, _ = ControlInterface.get_rule_list_for_item(statement)
                        if rule_list:
                            status = ControlInterface.get_status_from_props(statement)
                            if statement.statement_id not in control_part_id_map:
                                label = statement.statement_id
                                logger.warning(
                                    f'No statement label found for statement id {label}.  Defaulting to {label}.'
                                )
                            else:
                                label = control_part_id_map[statement.statement_id]
                            comp_info = ComponentImpInfo(statement.description, rule_list, [], status)
                            self._catalog_interface.add_comp_info(
                                imp_req.control_id, context.comp_name, label, comp_info
                            )

        catalog_merger = CatalogMerger(self._catalog_interface)

        for control in self._catalog_interface.get_all_controls_from_catalog(True):
            if control.id in control_ids_in_comp_imp:
                context.comp_dict = self._catalog_interface.get_comp_info(control.id)
                new_context = ControlContext.clone(context)
                # get the resolved catalog values for the control params
                control_param_dict = ControlInterface.get_control_param_dict(control, False)
                # update them with values in the ci
                for set_param in as_list(new_context.control_implementation.set_parameters):
                    _update_values(set_param, control_param_dict)
                # update them with values in the imp_req
                for imp_req in as_list(new_context.control_implementation.implemented_requirements):
                    if imp_req.control_id == control.id:
                        for set_param in as_list(imp_req.set_parameters):
                            _update_values(set_param, control_param_dict)

                # insert the param values into the header
                if control_param_dict:
                    new_context.merged_header[const.PARAM_VALUES_TAG] = {}
                    for key, param in control_param_dict.items():
                        new_context.merged_header[const.PARAM_VALUES_TAG][key] = none_if_empty(
                            ControlInterface._param_values_as_str_list(param)
                        )
                # merge the md_header and md_comp_dict with info in cat_interface for this control
                control_file_path = self._catalog_interface.get_control_file_path(context.md_root, control.id)
                catalog_merger._merge_header_and_comp_dict(control, control_file_path, new_context)

                self._write_control_into_dir(new_context, control, part_id_map, [])

    def write_catalog_as_catalog(self, context: ControlContext, part_id_map: Dict[str, Dict[str, str]]) -> None:
        """Write the catalog as a simple catalog."""
        # write out the controls
        for control in self._catalog_interface.get_all_controls_from_catalog(True):
            # here we do special handling of how set-parameters merge with the yaml header
            new_context = ControlContext.clone(context)

            control_param_dict = ControlInterface.get_control_param_dict(control, False)
            set_param_dict: Dict[str, str] = {}
            for param_id, param_dict in control_param_dict.items():
                tmp_dict = ModelUtils.parameter_to_dict(param_dict, True)
                values = tmp_dict.get('values', None)
                new_dict = {'values': values}
                set_param_dict[param_id] = new_dict
            if set_param_dict:
                if const.SET_PARAMS_TAG not in new_context.cli_yaml_header:
                    new_context.cli_yaml_header[const.SET_PARAMS_TAG] = {}
                if new_context.overwrite_header_values:
                    # update the control params with new values
                    for key, value in new_context.cli_yaml_header[const.SET_PARAMS_TAG].items():
                        if key in control_param_dict:
                            set_param_dict[key] = value
                else:
                    # update the control params with any values in yaml header not set in control
                    # need to maintain order in the set_param_dict
                    for key, value in new_context.cli_yaml_header[const.SET_PARAMS_TAG].items():
                        if key in control_param_dict and key not in set_param_dict:
                            set_param_dict[key] = value
                new_context.cli_yaml_header[const.SET_PARAMS_TAG] = set_param_dict
            elif const.SET_PARAMS_TAG in new_context.cli_yaml_header:
                # need to cull any params that are not in control
                pop_list: List[str] = []
                for key in new_context.cli_yaml_header[const.SET_PARAMS_TAG].keys():
                    if key not in control_param_dict:
                        pop_list.append(key)
                for pop in pop_list:
                    new_context.cli_yaml_header[const.SET_PARAMS_TAG].pop(pop)

            self._write_control_into_dir(new_context, control, part_id_map, [])

    def _write_control_into_dir(
        self,
        context: ControlContext,
        control: cat.Control,
        part_id_map: Dict[str, Dict[str, str]],
        found_control_alters: List[prof.Alter]
    ):
        # we need to create the dir structure on demand because we don't know a priori what groups are included
        _, group_title, _ = self._catalog_interface.get_group_info_by_control(control.id)
        group_dir = context.md_root
        control_path = self._catalog_interface.get_control_path(control.id)
        for sub_dir in control_path:
            group_dir = group_dir / sub_dir
            if not group_dir.exists():
                group_dir.mkdir(parents=True, exist_ok=True)

        writer = ControlWriter()
        writer.write_control_for_editing(context, control, group_dir, group_title, part_id_map, found_control_alters)
