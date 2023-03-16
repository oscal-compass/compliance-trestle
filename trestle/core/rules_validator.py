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
        for component in as_list(model.components):
            shared_params = {}
            # iterate by each control implementation within the component
            for control_imp in as_list(component.control_implementations):
                _, param_dict, _ = ControlInterface.get_rules_and_params_dict_from_item(control_imp)
                control_imp_rule_param_ids = [d['name'] for d in param_dict.values()]
                for set_param in as_list(control_imp.set_parameters):
                    # if not a rule parameter then ignore
                    if set_param.param_id not in (control_imp_rule_param_ids):
                        continue
                    opts_for_parameter = [p['options'] for p in param_dict.values() if p['name'] == set_param.param_id]
                    shared_params = {
                        set_param.param_id: [
                            {
                                'level': 'ci',
                                'control_id': '',
                                'values': set_param.values,
                                'options': opts_for_parameter
                            }
                        ]
                    }
                for imp_req in as_list(control_imp.implemented_requirements):
                    # gets a set of rules for each catalog
                    _, imp_param_dict, _ = ControlInterface.get_rules_and_params_dict_from_item(imp_req)
                    imp_req_rule_param_ids = [d['name'] for d in imp_param_dict.values()]
                    if not imp_req.set_parameters:
                        # filters param values for current control implementation
                        for shared_param_id in as_list(shared_params):
                            shared_param = [x for x in shared_params[shared_param_id] if x['level'] == 'ci'][0]
                            diff = self.val_diff_param_values(shared_params[shared_param_id], shared_param['values'])
                            if diff:
                                logger.error(
                                    f'Rule parameter value: {diff} provided for: {shared_param_id} in '
                                    f'control: {imp_req.control_id} in component: {component.title} is not consistent '
                                    'with other values provided across controls. Invalid model'
                                )
                                return False
                            shared_params[shared_param_id].append(
                                {
                                    'level': 'ip', 'control_id': imp_req.control_id, 'values': shared_param['values']
                                }
                            )
                        continue
                    for set_param in as_list(imp_req.set_parameters):
                        # if not a rule parameter then ignore
                        if set_param.param_id not in (control_imp_rule_param_ids + imp_req_rule_param_ids):
                            continue
                        # gets existing param if exists
                        existing_params = [x for x in shared_params[set_param.param_id] if x['level'] != 'ci']
                        if not existing_params:
                            # adds a non exisitng param across controls for revision
                            shared_params[set_param.param_id].append(
                                {
                                    'level': 'ip', 'control_id': imp_req.control_id, 'values': set_param.values
                                }
                            )
                            opts_for_param = [
                                p['options'] for p in shared_params[set_param.param_id] if p['level'] == 'ci'
                            ][0]
                            # validates if param value exist inside value alternatives for the param
                            for value in set_param.values:
                                if value not in opts_for_param[0]:
                                    logger.warning(
                                        f'Rule parameter value: {value} for parameter: {set_param.param_id} in '
                                        f'control {imp_req.control_id} for component: {component.title} '
                                        f'is not in the alternatives provided by default: {opts_for_param[0]} '
                                        'for the control implementation'
                                    )
                            continue
                        diff = self.val_diff_param_values(existing_params, set_param.values)
                        if diff:
                            logger.error(
                                f'Rule parameter value: {diff} provided for: {set_param.param_id} in '
                                f'control: {imp_req.control_id} in component: {component.title} is not consistent with '
                                'other values provided across controls. Invalid model'
                            )
                            return False
        return True
