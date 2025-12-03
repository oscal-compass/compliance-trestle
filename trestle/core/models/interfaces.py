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
"""Interfaces for use within other trestle functions defined as pydantic data models."""
from typing import Dict, Optional

from pydantic import Extra

import trestle.oscal.assessment_plan as o_ap
import trestle.oscal.assessment_results as o_ar
import trestle.oscal.catalog as o_catalog
import trestle.oscal.component as o_component
import trestle.oscal.poam as o_poam
import trestle.oscal.profile as o_profile
import trestle.oscal.ssp as o_ssp
from trestle.core.trestle_base_model import TrestleBaseModel


class OSCALAssembly(TrestleBaseModel):
    """Data model to represent an assembled set of OSCAL objects.

    Here the assembly represents the constraints as expected by the current OSCAL
    schema. At this point in time a 'flat' model has been chosen rather than an tree.
    """

    poam: Optional[o_poam.PlanOfActionAndMilestones] = None
    sar: Optional[o_ar.AssessmentResults] = None
    sap: Optional[o_ap.AssessmentPlan] = None
    ssp: Optional[o_ssp.SystemSecurityPlan] = None
    profiles: Optional[Dict[str, o_profile.Profile]] = None
    catalogs: Optional[Dict[str, o_catalog.Catalog]] = None
    components: Optional[Dict[str, o_component.ComponentDefinition]] = None

    class Config:
        """Pydantic config overrides."""

        allow_population_by_field_name = True
        # Enforce strict schema
        extra = Extra.forbid
        # Validate on assignment of variables to ensure no escapes
        validate_assignment = True
