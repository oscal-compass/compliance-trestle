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

from trestle.common.common_types import TopLevelOscalModel
from trestle.common.list_utils import as_list
from trestle.core.control_interface import ControlInterface
from trestle.core.validator import Validator
from trestle.oscal.component import ComponentDefinition
from trestle.oscal.ssp import SystemSecurityPlan

logger = logging.getLogger(__name__)

shared_params = {}


class RulesValidator(Validator):
    """Validator to confirm all rule parameter values are consistent."""

    @staticmethod
    def val_diff_param_values(existing_param: list, shared_param_values: list) -> list:
        """
        Test differences between rule param values.

        args:
            existing_param: Existing rule param values list.
            shared_param_values: Current rule param values list.

        returns:
            Difference between values if exist
        """
        for param_value in as_list(existing_param):
            # order params lists and gets differences
            param_value['values'].sort()
            shared_param_values.sort()
            param_vals_set = set(param_value['values'])
            difference = [x for x in shared_param_values if x not in param_vals_set]
            # if there´s a difference in params, log error
            return difference

    @staticmethod
    def return_dict_ids(item: list) -> list:
        """
        Retrieve dictionry of ids

        args:
            item: abstrac element where rule param ids are going to be retrieved

        returns:
            A list of rule parameter ids
        """
        _, param_dict, _ = ControlInterface.get_rules_and_params_dict_from_item(item)
        return [d['name'] for d in param_dict.values()]

    @staticmethod
    def add_shared_param(self, item: list, parent: list = None, bottom_level: bool = False) -> None:
        """
        Add a rule shared parameter to the rule shared parameters list

        args:
            existing_param: Existing rule param values list.
            shared_param_values: Current rule param values list.

        returns:
            Difference between values if exist
        """
        if parent:
            parent_ids = self.return_dict_ids(parent)
        param_ids = self.return_dict_ids(item)
        for set_param in as_list(item.set_parameters):
            if set_param.param_id not in (param_ids + parent_ids):
                continue
            # adds shared param
            if not bottom_level:
                shared_params[set_param.param_id].append({item.control_id: set_param.values})
            diff = self.val_diff_param_values(shared_params, set_param.values)
            if not diff:
                shared_params[set_param.param_id].append({item.control_id: set_param.values})
            logger.error(
                f'Rule parameter value: {diff} provided for: {set_param.param_id} in '
                f'control: {item.control_id} in component: {parent.title} is not consistent with '
                'other values provided across controls. Invalid model'
            )
            return False

    def model_is_valid(self, model: TopLevelOscalModel, quiet: bool) -> bool:
        """
        Test if the model is valid.

        args:
            model: A top level OSCAL model.
            quiet: Don't report msgs unless invalid.

        returns:
            True (valid) if the model's rule parameter values are the same accross controls.
        """
        # verify if model type is either an SSP of a Component Definition
        if not isinstance(model, (SystemSecurityPlan, ComponentDefinition)):
            return True
        # iterate by each component defined
        for component in as_list(model.system_implementation.components):
            # iterate by each control implementation within the component
            for control_imp in as_list(component.control_implementations):
                self.add_shared_param(control_imp)
                for imp_req in as_list(control_imp.implemented_requirements):
                    self.add_shared_param(imp_req, control_imp, True)
        return True
