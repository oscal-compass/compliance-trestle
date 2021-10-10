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
"""Validate by confirming no duplicate items."""

import logging
import re

from trestle.core.base_model import OscalBaseModel
from trestle.core.validator import Validator
from trestle.oscal.__init__ import OSCAL_VERSION_REGEX

logger = logging.getLogger(__name__)


class OSCALVersionValidator(Validator):
    """Validator to confirm the OSCAL version is the one supported."""

    def model_is_valid(self, model: OscalBaseModel) -> bool:
        """
        Test if the model is valid based on OSCAL version.

        args:
            model: An Oscal model that can be passed to the validator.

        returns:
            True (valid) if the OSCAL version in the model is supported.
        """
        oscal_version = model.metadata.oscal_version.__root__
        p = re.compile(OSCAL_VERSION_REGEX)
        matched = p.match(oscal_version)
        return matched is not None
