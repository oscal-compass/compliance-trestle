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
"""Validate based on all registered validators."""

import trestle.core.validator_factory as vfact
from trestle.core.base_model import OscalBaseModel
from trestle.core.validator import Validator


class AllValidator(Validator):
    """Validator to confirm the model passes all registered validation tests."""

    last_failure_msg: str

    def error_msg(self) -> str:
        """Return information on which validation failed."""
        return self.last_failure_msg

    def model_is_valid(self, model: OscalBaseModel) -> bool:
        """
        Validate an oscal model against all available validators in the trestle library.

        args:
            model: An Oscal model that can be passed to the validator.

        returns:
            True (valid) if the model passed all registered validators.
        """
        self.last_failure_msg = self.__doc__
        for val in vfact.validator_factory.get_all():
            if val != self:
                if not val.model_is_valid(model):
                    self.last_failure_msg = val.error_msg()
                    return False
        return True
