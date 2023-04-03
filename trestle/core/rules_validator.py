# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2023 IBM Corp. All rights reserved.
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
"""Validate by confirming rule parameter values are consistent."""
import logging
import pathlib
from typing import List

from trestle.common.common_types import TopLevelOscalModel
from trestle.common.common_types import TypeWithSetParams
from trestle.common.list_utils import as_list, deep_set, get_item_from_list
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.profile_resolver import ProfileResolver
from trestle.core.validator import Validator
from trestle.oscal.ssp import ByComponent, ImplementedRequirement, Statement, SystemComponent, SystemSecurityPlan

logger = logging.getLogger(__name__)


class RulesValidator(Validator):
    """Validator to confirm all rule parameter values are consistent."""

    rule_param_values_dict = {}

    def iter_and_add(
        self,
        by_components: List[ByComponent],
        components: List[SystemComponent],
        cat_int: CatalogInterface,
        imp_requirement: ImplementedRequirement,
        statement: Statement = None
    ) -> None:
        """
        Iterate all by components in an object and add the rule shared parameter values to list.

        args:
            by_components: A list of by components.
            components: Components defined at System implementation level.
            cat_int: Instance of catalog interface with controls catalog loaded.
            imp_requirement: Current implemented requirement.
            statement: Statement if iterating by statements.
        """
        for by_component in as_list(by_components):
            component = get_item_from_list(components, by_component.component_uuid, lambda x: x.uuid)
            # first adds implmented requirement set params
            if not statement:
                self.add_shared_param(imp_requirement, imp_requirement.control_id, cat_int, component.title)
            # then  adds by components set params per requirement
            self.add_shared_param(by_component, imp_requirement.control_id, cat_int, component.title)

    def add_shared_param(
        self, item: TypeWithSetParams, control_id: str, cat_int: CatalogInterface, comp_name: str = ''
    ) -> None:
        """
        Add a rule shared parameter to the rule shared parameters list.

        args:
            item: Generic item to iterate over parameters.
            control_id: Current control id.
            cat_int: Instance of catalog interface with controls catalog loaded.
            comp_name: Component name to save.
        """
        for set_param in as_list(item.set_parameters):
            control = cat_int.get_control_by_param_id(set_param.param_id)
            if not control:
                deep_set(self.rule_param_values_dict, [set_param.param_id, comp_name, control_id], set_param.values)

    def model_is_valid(self, model: TopLevelOscalModel, quiet: bool, trestle_root: pathlib.Path = '') -> bool:
        """
        Test if the model is valid.

        args:
            model: A top level OSCAL model.
            quiet: Don't report msgs unless invalid.
            trestle_root: Trestle root path.

        returns:
            True (valid) if the model's rule parameter values are the same accross controls.
        """
        # verify if model type is either an SSP of a Component Definition
        if not isinstance(model, (SystemSecurityPlan)):
            return True

        components = as_list(model.system_implementation.components)
        profile_catalog = ProfileResolver().get_resolved_profile_catalog(trestle_root, model.import_profile.href)
        catalog_interface = CatalogInterface(profile_catalog)
        # iterate by each implemented requirement defined
        for imp_req in as_list(model.control_implementation.implemented_requirements):
            # iterate by each by_component in each implemented requirement
            self.iter_and_add(imp_req.by_components, components, catalog_interface, imp_req)
            # includes rule param values in each by_component present in statements
            for statement in as_list(imp_req.statements):
                self.iter_and_add(statement.by_components, components, catalog_interface, imp_req, statement)
        if not self.rule_param_values_dict:
            return True
        # compare all values in shared paramerets by component basis
        for shared_param, values_dict in as_list(self.rule_param_values_dict.items()):
            for comp_name, value_dict in values_dict.items():
                expected_value = next(iter(value_dict.values()))
                if not all(value == expected_value for value in value_dict.values()):
                    logger.error(
                        f'Rule parameter values for param: {shared_param} in '
                        f' {comp_name} is not consistent with '
                        'other values provided across controls. Invalid model'
                    )
                    return False
        return True
