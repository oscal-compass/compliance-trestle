# -*- mode:python; coding:utf-8 -*-

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
"""Validate by confirming all refs have corresponding id."""
from trestle.core.base_model import OscalBaseModel
from trestle.core.validator import Validator
from trestle.core.validator_helper import find_values_by_name


class RefsValidator(Validator):
    """Validator to confirm all references in responsible parties are found in roles."""

    def model_is_valid(self, model: OscalBaseModel) -> bool:
        """
        Test if the model is valid.

        args:
            model: An Oscal model that can be passed to the validator.
        returns:
            True (valid) if the model's responsible parties match those found in roles.
        """
        # FIXME oscal 1.0.0
        metadata = model.metadata
        roles_list_of_lists = find_values_by_name(metadata, 'roles')
        roles_list = [item.id for sublist in roles_list_of_lists for item in sublist]
        roles_set = set(roles_list)
        responsible_parties_list = find_values_by_name(metadata, 'responsible_parties')
        if not responsible_parties_list:
            return True
        responsible_parties = [item for sublist in responsible_parties_list for item in sublist]
        party_roles = []
        for r in responsible_parties:
            party_roles.append(r.role_id)
        for party in party_roles:
            if party not in roles_set:
                return False
        return True
