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
"""Validate by confirming no duplicate uuids."""
import pathlib
from typing import Optional

from trestle.common.model_utils import ModelUtils
from trestle.core.base_model import OscalBaseModel
from trestle.core.validator import Validator
from trestle.oscal.profile import Profile


class DuplicatesValidator(Validator):
    """Validator to check for duplicate uuids and param_ids in the model."""

    def model_is_valid(self, model: OscalBaseModel, quiet: bool, trestle_root: Optional[pathlib.Path] = None) -> bool:
        """
        Test if the model is valid and contains no duplicate uuids or param_ids.

        args:
            model: An Oscal model that can be passed to the validator.
            quiet: Don't report msgs unless invalid.

        returns:
            True (valid) if the model does not contain duplicate uuid's.
        """
        if not ModelUtils.has_no_duplicate_values_by_name(model, 'uuid'):
            return False
        # only profile, comp-def and ssp have set-params and only set-params have param_id
        # param_id is required to be unique in profiles but not in other models
        if isinstance(model, Profile):
            return ModelUtils.has_no_duplicate_values_by_name(model, 'param_id')
        return True
