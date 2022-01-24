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
from trestle.common.common_types import TopLevelOscalModel
from trestle.common.list_utils import as_list
from trestle.core.validator import Validator


class RefsValidator(Validator):
    """Validator to confirm all references in responsible parties are found in roles."""

    def model_is_valid(self, model: TopLevelOscalModel) -> bool:
        """
        Test if the model is valid.

        args:
            model: A top level OSCAL model.
        returns:
            True (valid) if the model's responsible parties match those found in roles.
        """
        roles = as_list(model.metadata.roles)
        role_ids = [role.id for role in roles]
        responsible_parties = as_list(model.metadata.responsible_parties)
        if not responsible_parties:
            return True
        party_roles = [party.role_id for party in responsible_parties]
        # return true if all party roles are in the roles list
        return all(item in role_ids for item in party_roles)
