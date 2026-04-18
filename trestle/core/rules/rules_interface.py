# Copyright (c) 2026 The OSCAL Compass Authors. All rights reserved.
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
"""Rules support helpers."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Set, Tuple

from trestle.common import const
from trestle.common.common_types import TypeWithProps
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_list
from trestle.oscal import common
from trestle.oscal import ssp as ossp

logger = logging.getLogger(__name__)


class RulesInterface:
    """Rule utilities for parsing and filtering rule properties."""

    @staticmethod
    def get_rules_dict_from_item(item: TypeWithProps) -> Tuple[Dict[str, Dict[str, str]], List[common.Property]]:
        """Get all rules found in this items props."""
        # rules is dict containing rule_id and description
        rules_dict = {}
        name = ''
        desc = ''
        id_ = ''
        rules_props = []
        for prop in as_list(item.props):
            if prop.name == const.RULE_ID:
                name = prop.value
                id_ = prop.remarks
                rules_props.append(prop)
            elif prop.name == const.RULE_DESCRIPTION:
                desc = prop.value
                rules_props.append(prop)
            # grab each pair in case there are multiple pairs
            # then clear and look for new pair
            if name and desc:
                rules_dict[id_] = {'name': name, 'description': desc}
                name = desc = id_ = ''
        return rules_dict, rules_props

    @staticmethod
    def item_has_rules(item: TypeWithProps) -> bool:
        """Determine if the item has rules in its props."""
        _, rules_props = RulesInterface.get_rules_dict_from_item(item)
        return bool(rules_props)

    @staticmethod
    def get_rule_list_for_item(item: TypeWithProps) -> Tuple[List[str], List[common.Property]]:
        """Get the list of rules applying to this item from its top level props."""
        props = []
        rule_list = []
        for prop in as_list(item.props):
            if prop.name == const.RULE_ID:
                rule_list.append(prop.value)
                props.append(prop)
        return rule_list, props

    @staticmethod
    def get_rule_list_for_imp_req(
        imp_req: ossp.ImplementedRequirement,
    ) -> Tuple[List[str], List[str], List[common.Property]]:
        """Get the list of rules applying to an imp_req as two lists."""
        comp_rules, rule_props = RulesInterface.get_rule_list_for_item(imp_req)
        statement_rules = set()
        for statement in as_list(imp_req.statements):
            stat_rules, statement_props = RulesInterface.get_rule_list_for_item(statement)
            statement_rules.update(stat_rules)
            rule_props.extend(statement_props)
        return comp_rules, sorted(statement_rules), rule_props

    @staticmethod
    def get_params_dict_from_item(item: TypeWithProps) -> Tuple[Dict[str, List[Dict[str, str]]], List[common.Property]]:
        """Get all params found in this item with rule_id as key."""
        # id, description, options - where options is a string containing comma-sep list of items
        # params is dict with rule_id as key and value contains: param_name, description and choices
        params: Dict[str, List[Dict[str, str]]] = {}
        props = []
        for prop in as_list(item.props):
            if const.PARAMETER_ID in prop.name:
                rule_id = prop.remarks
                param_name = prop.value
                # rule already exists in parameters dict
                if rule_id is not None:
                    if rule_id in params.keys():
                        existing_param = next((prm for prm in params[rule_id] if prm['name'] == param_name), None)
                        if existing_param is not None:
                            raise TrestleError(f'Param id for rule {rule_id} already exists')
                        else:
                            # append a new parameter for the current rule
                            params[rule_id].append({'name': param_name})
                    else:
                        # create new param for this rule for the first parameter
                        params[rule_id] = [{'name': param_name}]
                        props.append(prop)
            elif const.PARAMETER_DESCRIPTION in prop.name:
                rule_id = prop.remarks
                if rule_id in params:
                    param = next((prm for prm in params[rule_id] if prm['name'] == param_name), None)
                    if param is not None:
                        param['description'] = prop.value
                        props.append(prop)
                    else:
                        raise TrestleError(f'Param description for rule {rule_id} found with no param_id')
            elif const.PARAMETER_VALUE_ALTERNATIVES in prop.name:
                rule_id = prop.remarks
                if rule_id in params:
                    param = next((prm for prm in params[rule_id] if prm['name'] == param_name), None)
                    if param is not None:
                        param['options'] = prop.value
                        props.append(prop)
                    else:
                        raise TrestleError(f'Param options for rule {rule_id} found with no param_id')
        new_params: dict[str, list[dict[str, str]]] = {}
        for rule_id, rule_params in params.items():
            new_params[rule_id] = []
            for param in rule_params:
                if 'name' not in param:
                    logger.warning(f'Parameter for rule_id {rule_id} has no matching name.  Ignoring the param.')
                else:
                    param['description'] = param.get('description', '')
                    param['options'] = param.get('options', '')
                    new_params[rule_id].append(param)
        return new_params, props

    @staticmethod
    def get_rules_and_params_dict_from_item(
        item: TypeWithProps,
    ) -> Tuple[Dict[str, Dict[str, str]], Dict[str, List[Dict[str, str]]], List[common.Property]]:
        """Get the rule dict and params dict from item with props."""
        rules_dict, rules_props = RulesInterface.get_rules_dict_from_item(item)
        params_dict, params_props = RulesInterface.get_params_dict_from_item(item)
        rules_props.extend(params_props)
        return rules_dict, params_dict, rules_props

    @staticmethod
    def cull_props_by_rules(props: Optional[List[common.Property]], rules: List[str]) -> List[common.Property]:
        """Cull properties to the ones needed by rules."""
        needed_rule_ids: Set[str] = set()
        culled_props: List[common.Property] = []
        for prop in as_list(props):
            if prop.value in rules and prop.remarks:
                needed_rule_ids.add(prop.remarks)
        for prop in as_list(props):
            if prop.value in rules or prop.remarks in needed_rule_ids:
                culled_props.append(prop)
        return culled_props
