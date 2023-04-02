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

from trestle.common.common_types import TopLevelOscalModel
from trestle.common.common_types import TypeWithSetParams
from trestle.common.list_utils import as_list, deep_set, get_item_from_list
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.profile_resolver import ProfileResolver
from trestle.core.validator import Validator
from trestle.oscal.ssp import SystemSecurityPlan

logger = logging.getLogger(__name__)


class RulesValidator(Validator):
    """Validator to confirm all rule parameter values are consistent."""

    rule_param_values_dict = {}

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
        profile_resolver = ProfileResolver()
        catalog = profile_resolver.get_resolved_profile_catalog(trestle_root, model.import_profile.href)
        catalog_interface = CatalogInterface(catalog)
        # iterate by each implemented requirement defined
        for imp_req in as_list(model.control_implementation.implemented_requirements):
            # iterate by each by_component in each implemented requirement
            for by_component in as_list(imp_req.by_components):
                component = get_item_from_list(components, by_component.component_uuid, lambda x: x.uuid)
                self.add_shared_param(imp_req, imp_req.control_id, catalog_interface, component.title)
                self.add_shared_param(by_component, imp_req.control_id, catalog_interface, component.title)
            # includes rule param values in each by_component present in statements
            for statement in as_list(imp_req.statements):
                for by_comp in as_list(statement.by_components):
                    component = get_item_from_list(components, by_component.component_uuid, lambda x: x.uuid)
                    self.add_shared_param(by_comp, imp_req.control_id, catalog_interface, component.title)
        if not self.rule_param_values_dict:
            return True
        # compare all values in shared paramerets by component basis
        for shared_param, values_dict in as_list(self.rule_param_values_dict.items()):
            for comp_name, value_dict in values_dict.items():
                expected_value = next(iter(value_dict.values()))
                all_equal = all(value == expected_value for value in value_dict.values())
                if not all_equal:
                    logger.error(
                        f'Rule parameter values for param: {shared_param} in '
                        f' {comp_name} is not consistent with '
                        'other values provided across controls. Invalid model'
                    )
                    return False
        return True
