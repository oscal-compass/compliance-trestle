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
"""Special types are defined here."""
from typing import TypeVar

import trestle.sdk.oscal.component as comp
import trestle.sdk.oscal.profile as prof
import trestle.sdk.oscal.ssp as ossp
from trestle.sdk.models.base_model import OscalBaseModel
from trestle.sdk.oscal.assessment_plan import AssessmentPlan
from trestle.sdk.oscal.assessment_results import AssessmentResults
from trestle.sdk.oscal.catalog import Catalog, Control, Group
from trestle.sdk.oscal.common import AssessmentPart, Part, Resource
from trestle.sdk.oscal.poam import PlanOfActionAndMilestones

# model types containing uuids that should not regenerate
FixedUuidModel = Resource

TopLevelOscalModel = TypeVar(
    'TopLevelOscalModel',
    AssessmentPlan,
    AssessmentResults,
    Catalog,
    comp.ComponentDefinition,
    PlanOfActionAndMilestones,
    prof.Profile,
    ossp.SystemSecurityPlan
)

OBT = TypeVar('OBT', bound=OscalBaseModel)
TG = TypeVar('TG')
TG2 = TypeVar('TG2')

TypeWithProps = TypeVar(
    'TypeWithProps',
    Control,
    Part,
    AssessmentPart,
    comp.Statement,
    ossp.Statement,
    comp.ImplementedRequirement,
    ossp.ImplementedRequirement
)

TypeWithParts = TypeVar('TypeWithParts', Control, Part, Group, prof.Add, prof.Group)

TypeWithByComps = TypeVar(
    'TypeWithByComps', ossp.ImplementedRequirement, ossp.Statement, comp.ImplementedRequirement, comp.Statement
)

TypeWithSetParams = TypeVar(
    'TypeWithSetParams',
    ossp.ImplementedRequirement,
    ossp.ByComponent,
    ossp.ControlImplementation,
    comp.ImplementedRequirement,
    comp.ControlImplementation,
    prof.Modify
)

TypeWithParamId = TypeVar('TypeWithParamId', ossp.SetParameter, prof.SetParameter, comp.SetParameter)
