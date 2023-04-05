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
from typing import Optional

from trestle.common.common_types import TopLevelOscalModel
from trestle.common.common_types import TypeWithSetParams
from trestle.common.list_utils import as_list, deep_set
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.profile_resolver import ProfileResolver
from trestle.core.validator import Validator
from trestle.oscal.ssp import ImplementedRequirement, SystemSecurityPlan

logger = logging.getLogger(__name__)


class RuleParametersValidator(Validator):
    """Validator to confirm all rule parameter values are consistent."""

    def __init__(self):
        """Initialize rule param values dictionary."""
        self._rule_param_values_dict = {}

    def _add_imp_req_rule_params_to_dict(
        self,
        imp_requirement: ImplementedRequirement,
        cat_int: CatalogInterface,
    ) -> None:
        """
        Iterate all by components in an object and add the rule shared parameter values to list.

        args:
            imp_requirement: Current implemented requirement.
            cat_int: Instance of catalog interface with controls catalog loaded.
        """
        for by_component in as_list(imp_requirement.by_components):
            # adds rule param values present in set parameters for current imp req
            self._add_rule_params(imp_requirement, imp_requirement.control_id, cat_int, by_component.component_uuid)
            # adds rule param values present in set parameters for current by_component in by_components list
            # in the current implemented requirement
            self._add_rule_params(by_component, imp_requirement.control_id, cat_int, by_component.component_uuid)
            for statement in as_list(imp_requirement.statements):
                # iterates by each by component inclded at each statemtent set for current imp req
                for by_comp in as_list(statement.by_components):
                    # adds rule param values present in set parameters for current by_component in by_components list
                    # of current statement in current implemented requirement
                    self._add_rule_params(by_comp, imp_requirement.control_id, cat_int, by_comp.component_uuid)

    def _add_rule_params(
        self, item: TypeWithSetParams, control_id: str, cat_int: CatalogInterface, comp_uuid: str = ''
    ) -> None:
        """
        Add a rule shared parameter to the rule shared parameters list.

        args:
            item: Generic item to iterate over parameters.
            control_id: Current control id.
            cat_int: Instance of catalog interface with controls catalog loaded.
            comp_uuid: Component uuid to save.
        """
        for set_param in as_list(item.set_parameters):
            # validates if current param_id is or not associated with a control so we can assume it´s a rule param
            control = cat_int.get_control_by_param_id(set_param.param_id)
            if not control:
                deep_set(self._rule_param_values_dict, [set_param.param_id, comp_uuid, control_id], set_param.values)

    def model_is_valid(
        self, model: TopLevelOscalModel, quiet: bool, trestle_root: Optional[pathlib.Path] = None
    ) -> bool:
        """
        Test if the model is valid.

        args:
            model: A top level OSCAL model.
            quiet: Don't report msgs unless invalid.
            trestle_root: Trestle root path.

        returns:
            True (valid) if the model's rule parameter values are the same across controls.
        """
        # verify if model type is either an SSP of a Component Definition
        if not isinstance(model, SystemSecurityPlan):
            return True

        if not model.import_profile.href:
            logger.info(f'INVALID: Model {model.metadata.title} has no referenced profile')
            return False
        profile_catalog = ProfileResolver().get_resolved_profile_catalog(trestle_root, model.import_profile.href)
        catalog_interface = CatalogInterface(profile_catalog)
        # iterate by each implemented requirement defined
        for imp_req in model.control_implementation.implemented_requirements:
            # adds rule param values to dict by implemented requirement basis
            self._add_imp_req_rule_params_to_dict(imp_req, catalog_interface)
        if self._rule_param_values_dict:
            # compare all values in shared paramerets by component basis
            for shared_param, values_dict in self._rule_param_values_dict.items():
                for comp_name, value_dict in values_dict.items():
                    expected_value = next(iter(value_dict.values()))
                    if not all(value == expected_value for value in value_dict.values()):
                        logger.error(
                            f'Rule parameter values for param: {shared_param} in '
                            f' {comp_name} are not consistent with '
                            'other values provided across controls. Invalid model'
                        )
                        return False
        return True
