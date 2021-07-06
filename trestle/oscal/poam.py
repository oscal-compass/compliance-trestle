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

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import AnyUrl, EmailStr, Field, conint, constr

from trestle.core.base_model import OscalBaseModel
import trestle.oscal.common as common


class State1(Enum):
    satisfied = 'satisfied'
    not_satisfied = 'not-satisfied'


class State(Enum):
    under_development = 'under-development'
    operational = 'operational'
    disposition = 'disposition'
    other = 'other'


class SetParameter(OscalBaseModel):
    param_id: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        alias='param-id',
        description=
        "A reference to a parameter within a control, who's catalog has been imported into the current implementation context.",
        title='Parameter ID',
    )
    values: List[common.Value] = Field(...)
    remarks: Optional[common.Remarks] = None


class SelectControlById(OscalBaseModel):
    control_id: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        alias='control-id',
        description='A reference to a control with a corresponding id value.',
        title='Control Identifier Reference',
    )
    statement_ids: Optional[List[common.StatementId]] = Field(None, alias='statement-ids')


class Origin1(OscalBaseModel):
    actors: List[common.OriginActor] = Field(...)
    related_tasks: Optional[List[common.RelatedTask]] = Field(None, alias='related-tasks')


class Origin(OscalBaseModel):
    actors: List[common.OriginActor] = Field(...)


class Method(OscalBaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description='Identifies how the observation was made.',
        title='Observation Method',
    )


class Entry(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'Uniquely identifies a risk log entry. This UUID may be referenced elsewhere in an OSCAL document when referring to this information. A UUID should be consistently used for this schedule across revisions of the document.',
        title='Risk Log Entry Universally Unique Identifier',
    )
    title: Optional[str] = Field(None, description='The title for this risk log entry.', title='Title')
    description: Optional[str] = Field(
        None,
        description='A human-readable description of what was done regarding the risk.',
        title='Risk Task Description',
    )
    start: datetime = Field(
        ...,
        description='Identifies the start date and time of the event.',
        title='Start',
    )
    end: Optional[datetime] = Field(
        None,
        description=
        'Identifies the end date and time of the event. If the event is a point in time, the start and end will be the same date and time.',
        title='End',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    logged_by: Optional[List[common.LoggedBy]] = Field(None, alias='logged-by')
    status_change: Optional[common.RiskStatus] = Field(None, alias='status-change')
    related_responses: Optional[List[common.RelatedResponse]] = Field(None, alias='related-responses')
    remarks: Optional[common.Remarks] = None


class ControlSelection(OscalBaseModel):
    description: Optional[str] = Field(
        None,
        description='A human-readable description of in-scope controls specified for assessment.',
        title='Assessed Controls Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    include_all: Optional[Dict[str, Any]] = Field(
        None,
        alias='include-all',
        description='A key word to indicate all.',
        title='All',
    )
    include_controls: Optional[List[SelectControlById]] = Field(None, alias='include-controls')
    exclude_controls: Optional[List[SelectControlById]] = Field(None, alias='exclude-controls')
    remarks: Optional[common.Remarks] = None


class Characterization(OscalBaseModel):
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    origin: Origin1
    facets: List[common.Facet] = Field(...)


class Status1(OscalBaseModel):
    state: State1 = Field(
        ...,
        description='An indication as to whether the objective is satisfied or not.',
        title='Objective Status State',
    )
    reason: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        description="The reason the objective was given it's status.",
        title='Objective Status Reason',
    )
    remarks: Optional[common.Remarks] = None


class FindingTarget(OscalBaseModel):
    type: common.Type1 = Field(
        ...,
        description='Identifies the type of the target.',
        title='Finding Target Type',
    )
    target_id: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        alias='target-id',
        description='Identifies the specific target qualified by the type.',
        title='Finding Target Identifier Reference',
    )
    title: Optional[str] = Field(
        None,
        description='The title for this objective status.',
        title='Objective Status Title',
    )
    description: Optional[str] = Field(
        None,
        description=
        "A human-readable description of the assessor's conclusions regarding the degree to which an objective is satisfied.",
        title='Objective Status Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    status: Status1 = Field(
        ...,
        description='A determination of if the objective is satisfied or not within a given system.',
        title='Objective Status',
    )
    implementation_status: Optional[common.ImplementationStatus] = Field(None, alias='implementation-status')
    remarks: Optional[common.Remarks] = None


class Status(OscalBaseModel):
    state: State = Field(..., description='The operational status.', title='State')
    remarks: Optional[common.Remarks] = None


class SystemComponent(OscalBaseModel):
    uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                 ) = Field(
                     ...,
                     description='The unique identifier for the component.',
                     title='Component Identifier',
                 )
    type: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description='A category describing the purpose of the component.',
        title='Component Type',
    )
    title: str = Field(
        ...,
        description='A human readable name for the system component.',
        title='Component Title',
    )
    description: str = Field(
        ...,
        description='A description of the component, including information about its function.',
        title='Component Description',
    )
    purpose: Optional[str] = Field(
        None,
        description='A summary of the technological or business purpose of the component.',
        title='Purpose',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    status: Status = Field(
        ...,
        description='Describes the operational status of the system component.',
        title='Status',
    )
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    protocols: Optional[List[common.Protocol]] = Field(None)
    remarks: Optional[common.Remarks] = None


class AssessmentAssets(OscalBaseModel):
    components: Optional[List[SystemComponent]] = Field(None)
    assessment_platforms: List[common.AssessmentPlatform] = Field(..., alias='assessment-platforms')


class RiskLog(OscalBaseModel):
    entries: List[Entry] = Field(...)


class ReviewedControls(OscalBaseModel):
    description: Optional[str] = Field(
        None,
        description='A human-readable description of control objectives.',
        title='Control Objective Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    control_selections: List[ControlSelection] = Field(..., alias='control-selections')
    control_objective_selections: Optional[List[common.ControlObjectiveSelection]] = Field(
        None, alias='control-objective-selections'
    )
    remarks: Optional[common.Remarks] = None


class Response(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'Uniquely identifies this remediation. This UUID may be referenced elsewhere in an OSCAL document when referring to this information. Once assigned, a UUID should be consistently used for a given remediation across revisions.',
        title='Remediation Universally Unique Identifier',
    )
    lifecycle: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description=
        'Identifies whether this is a recommendation, such as from an assessor or tool, or an actual plan accepted by the system owner.',
        title='Remediation Intent',
    )
    title: str = Field(..., description='The title for this response activity.', title='Response Title')
    description: str = Field(
        ...,
        description='A human-readable description of this response plan.',
        title='Response Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    origins: Optional[List[Origin1]] = Field(None)
    required_assets: Optional[List[common.RequiredAsset]] = Field(None, alias='required-assets')
    tasks: Optional[List[common.Task]] = Field(None)
    remarks: Optional[common.Remarks] = None


class Risk(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'Uniquely identifies this risk. This UUID may be referenced elsewhere in an OSCAL document when referring to this information. Once assigned, a UUID should be consistently used for a given risk across revisions.',
        title='Risk Universally Unique Identifier',
    )
    title: str = Field(..., description='The title for this risk.', title='Risk Title')
    description: str = Field(
        ...,
        description=
        'A human-readable summary of the identified risk, to include a statement of how the risk impacts the system.',
        title='Risk Description',
    )
    statement: str = Field(
        ...,
        description='An summary of impact for how the risk affects the system.',
        title='Risk Statement',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    status: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(..., description='Describes the status of the associated risk.', title='Status')
    origins: Optional[List[Origin1]] = Field(None)
    threat_ids: Optional[List[common.ThreatId]] = Field(None, alias='threat-ids')
    characterizations: Optional[List[Characterization]] = Field(None)
    mitigating_factors: Optional[List[common.MitigatingFactor]] = Field(None, alias='mitigating-factors')
    deadline: Optional[datetime] = Field(
        None,
        description='The date/time by which the risk must be resolved.',
        title='Risk Resolution Deadline',
    )
    remediations: Optional[List[Response]] = Field(None)
    risk_log: Optional[RiskLog] = Field(
        None,
        alias='risk-log',
        description='A log of all risk-related tasks taken.',
        title='Risk Log',
    )
    related_observations: Optional[List[common.RelatedObservation1]] = Field(None, alias='related-observations')


class PoamItem(OscalBaseModel):
    uuid: Optional[constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    )] = Field(
        None,
        description=
        'Uniquely identifies the POA&M entry. This UUID may be referenced elsewhere in an OSCAL document when referring to this information. A UUID should be consistently used for a given POA&M item across revisions of the document.',
        title='POA&M Item Universally Unique Identifier',
    )
    title: str = Field(
        ...,
        description='The title or name for this POA&M item .',
        title='POA&M Item Title',
    )
    description: str = Field(
        ...,
        description='A human-readable description of POA&M item.',
        title='POA&M Item Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    origins: Optional[List[Origin]] = Field(None)
    related_observations: Optional[List[common.RelatedObservation]] = Field(None, alias='related-observations')
    related_risks: Optional[List[common.RelatedRisk]] = Field(None, alias='related-risks')
    remarks: Optional[common.Remarks] = None


class Observation(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'Uniquely identifies this observation. This UUID may be referenced elsewhere in an OSCAL document when referring to this information. Once assigned, a UUID should be consistently used for a given observation across revisions.',
        title='Observation Universally Unique Identifier',
    )
    title: Optional[str] = Field(None, description='The title for this observation.', title='Observation Title')
    description: str = Field(
        ...,
        description='A human-readable description of this assessment observation.',
        title='Observation Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    methods: List[Method] = Field(...)
    types: Optional[List[common.Type2]] = Field(None)
    origins: Optional[List[Origin1]] = Field(None)
    subjects: Optional[List[common.SubjectReference]] = Field(None)
    relevant_evidence: Optional[List[common.RelevantEvidence]] = Field(None, alias='relevant-evidence')
    collected: datetime = Field(
        ...,
        description='Date/time stamp identifying when the finding information was collected.',
        title='collected field',
    )
    expires: Optional[datetime] = Field(
        None,
        description=
        'Date/time identifying when the finding information is out-of-date and no longer valid. Typically used with continuous assessment scenarios.',
        title='expires field',
    )
    remarks: Optional[common.Remarks] = None


class LocalDefinitions(OscalBaseModel):
    components: Optional[List[SystemComponent]] = Field(None)
    inventory_items: Optional[List[common.InventoryItem]] = Field(None, alias='inventory-items')
    remarks: Optional[common.Remarks] = None


class PlanOfActionAndMilestones(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'Uniquely identifies this POA&M. This UUID must be changed each time the content of the POA&M changes.',
        title='POA&M Universally Unique Identifier',
    )
    metadata: common.Metadata
    import_ssp: Optional[common.ImportSsp] = Field(None, alias='import-ssp')
    system_id: Optional[common.SystemId] = Field(None, alias='system-id')
    local_definitions: Optional[LocalDefinitions] = Field(None, alias='local-definitions')
    observations: Optional[List[Observation]] = Field(None)
    risks: Optional[List[Risk]] = Field(None)
    poam_items: List[PoamItem] = Field(..., alias='poam-items')
    back_matter: Optional[common.BackMatter] = Field(None, alias='back-matter')


class Step(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'Uniquely identifies a step. This UUID may be referenced elsewhere in an OSCAL document when referring to this step. A UUID should be consistently used for a given test step across revisions of the document.',
        title='Step Universally Unique Identifier',
    )
    title: Optional[str] = Field(None, description='The title for this step.', title='Step Title')
    description: str = Field(
        ...,
        description='A human-readable description of this step.',
        title='Step Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    reviewed_controls: Optional[ReviewedControls] = Field(None, alias='reviewed-controls')
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    remarks: Optional[common.Remarks] = None


class Activity(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'Uniquely identifies this assessment activity. This UUID may be referenced elsewhere in an OSCAL document when referring to this information. A UUID should be consistently used for a given included activity across revisions of the document.',
        title='Assessment Activity Universally Unique Identifier',
    )
    title: Optional[str] = Field(
        None,
        description='The title for this included activity.',
        title='Included Activity Title',
    )
    description: str = Field(
        ...,
        description='A human-readable description of this included activity.',
        title='Included Activity Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    steps: Optional[List[Step]] = Field(None)
    related_controls: Optional[ReviewedControls] = Field(None, alias='related-controls')
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    remarks: Optional[common.Remarks] = None


class Model(OscalBaseModel):
    plan_of_action_and_milestones: PlanOfActionAndMilestones = Field(..., alias='plan-of-action-and-milestones')
