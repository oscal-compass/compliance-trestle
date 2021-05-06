# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Validate by confirming no duplicate items."""

import re

from trestle.core.base_model import OscalBaseModel
from trestle.core.const import NCNAME_REGEX
from trestle.core.validator import Validator
from trestle.core.validator_helper import find_values_by_name


class NcNameValidator(Validator):
    """Check that all item values conform to NCName regex."""

    def _model_is_valid_role_id(self, model: OscalBaseModel) -> bool:
        """Handle specific case for role_id."""
        role_ids_list = find_values_by_name(model, 'role_ids')
        p = re.compile(NCNAME_REGEX)
        for role_id_list in role_ids_list:
            for role_id in role_id_list:
                s = str(role_id.__root__)
                matched = p.match(s)
                if matched is None:
                    return False
        return True

    def model_is_valid(self, model: OscalBaseModel) -> bool:
        """Test if the model is valid."""
        return self._model_is_valid_role_id(model)
