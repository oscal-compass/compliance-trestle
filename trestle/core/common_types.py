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
"""Special types are defined here."""

from typing import TypeVar

from trestle.oscal import common
from trestle.oscal.assessment_plan import AssessmentPlan
from trestle.oscal.assessment_results import AssessmentResults
from trestle.oscal.catalog import Catalog
from trestle.oscal.component import ComponentDefinition
from trestle.oscal.poam import PlanOfActionAndMilestones
from trestle.oscal.profile import Profile
from trestle.oscal.ssp import SystemSecurityPlan

TopLevelOscalModel = TypeVar(
    'TopLevelOscalModel',
    AssessmentPlan,
    AssessmentResults,
    Catalog,
    ComponentDefinition,
    PlanOfActionAndMilestones,
    Profile,
    SystemSecurityPlan
)

# model types containing uuids that should not regenerate
FixedUuidModel = common.Resource
