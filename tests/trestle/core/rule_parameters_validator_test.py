# Copyright (c) 2026 The OSCAL Compass Authors. All rights reserved.
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
"""Tests for backward-compatible RuleParametersValidator import path."""

from trestle.core.rule_parameters_validator import RuleParametersValidator as CompatRuleParametersValidator
from trestle.core.rules.rule_parameters_validator import RuleParametersValidator as NewRuleParametersValidator


def test_rule_parameters_validator_backward_compatibility() -> None:
    """Confirm old and new import paths resolve to the same validator class."""
    assert CompatRuleParametersValidator is NewRuleParametersValidator


def test_rule_parameters_validator_non_ssp_model_is_valid() -> None:
    """Non-SSP models should always be treated as valid."""
    validator = NewRuleParametersValidator()
    assert validator.model_is_valid(object(), quiet=True, trestle_root=None) is True
