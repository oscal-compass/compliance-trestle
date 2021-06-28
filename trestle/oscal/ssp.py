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


class AdjustmentJustification(OscalBaseModel):
    __root__: str = Field(
        ...,
        description=
        'If the selected security level is different from the base security level, this contains the justification for the change.',
        title='Adjustment Justification',
    )


class State1(Enum):
    under_development = 'under-development'
    operational = 'operational'
    disposition = 'disposition'
    other = 'other'


class State(Enum):
    operational = 'operational'
    under_development = 'under-development'
    under_major_modification = 'under-major-modification'
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


class Selected(OscalBaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description='The selected (Confidentiality, Integrity, or Availability) security impact level.',
        title='Selected Level (Confidentiality, Integrity, or Availability)',
    )


class SecurityImpactLevel(OscalBaseModel):
    security_objective_confidentiality: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        alias='security-objective-confidentiality',
        description=
        'A target-level of confidentiality for the system, based on the sensitivity of information within the system.',
        title='Security Objective: Confidentiality',
    )
    security_objective_integrity: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        alias='security-objective-integrity',
        description=
        'A target-level of integrity for the system, based on the sensitivity of information within the system.',
        title='Security Objective: Integrity',
    )
    security_objective_availability: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        alias='security-objective-availability',
        description=
        'A target-level of availability for the system, based on the sensitivity of information within the system.',
        title='Security Objective: Availability',
    )


class Satisfied(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier that can be used to reference this satisfied entry elsewhere in an OSCAL document. A UUID should be consistently used for a given resource across revisions of the document.',
        title='Satisfied Universally Unique Identifier',
    )
    responsibility_uuid: Optional[constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    )] = Field(
        None,
        alias='responsibility-uuid',
        description="Identifies a 'provided' assembly associated with this assembly.",
        title='Provided UUID',
    )
    description: str = Field(
        ...,
        description=
        'An implementation statement that describes the aspects of a control or control statement implementation that a leveraging system is implementing based on a requirement from a leveraged system.',
        title='Satisfied Control Implementation Responsibility Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    remarks: Optional[common.Remarks] = None


class Responsibility(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier that can be used to reference this responsibility entry elsewhere in an OSCAL document. A UUID should be consistently used for a given resource across revisions of the document.',
        title='Responsibility Universally Unique Identifier',
    )
    provided_uuid: Optional[constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    )] = Field(
        None,
        alias='provided-uuid',
        description="Identifies a 'provided' assembly associated with this assembly.",
        title='Provided UUID',
    )
    description: str = Field(
        ...,
        description=
        'An implementation statement that describes the aspects of the control or control statement implementation that a leveraging system must implement to satisfy the control provided by a leveraged system.',
        title='Control Implementation Responsibility Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    remarks: Optional[common.Remarks] = None


class Provided(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier that can be used to reference this provided entry elsewhere in an OSCAL document. A UUID should be consistently used for a given resource across revisions of the document.',
        title='Provided Universally Unique Identifier',
    )
    description: str = Field(
        ...,
        description=
        'An implementation statement that describes the aspects of the control or control statement implementation that can be provided to another system leveraging this system.',
        title='Provided Control Implementation Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    remarks: Optional[common.Remarks] = None


class Inherited(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier that can be used to reference this inherited entry elsewhere in an OSCAL document. A UUID should be consistently used for a given resource across revisions of the document.',
        title='Inherited Universally Unique Identifier',
    )
    provided_uuid: Optional[constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    )] = Field(
        None,
        alias='provided-uuid',
        description="Identifies a 'provided' assembly associated with this assembly.",
        title='Provided UUID',
    )
    description: str = Field(
        ...,
        description=
        'An implementation statement that describes the aspects of a control or control statement implementation that a leveraging system is inheriting from a leveraged system.',
        title='Inherited Control Implementation Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')


class InformationTypeId(OscalBaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description='An identifier qualified by the given identification system used, such as NIST SP 800-60.',
        title='Information Type Systematized Identifier',
    )


class ImportProfile(OscalBaseModel):
    href: str = Field(
        ...,
        description="A resolvable URL reference to the profile to use as the system's control baseline.",
        title='Profile Reference',
    )
    remarks: Optional[common.Remarks] = None


class Export(OscalBaseModel):
    description: Optional[str] = Field(
        None,
        description=
        'An implementation statement that describes the aspects of the control or control statement implementation that can be available to another system leveraging this system.',
        title='Control Implementation Export Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    provided: Optional[List[Provided]] = Field(None)
    responsibilities: Optional[List[Responsibility]] = Field(None)
    remarks: Optional[common.Remarks] = None


class Diagram(OscalBaseModel):
    uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                 ) = Field(..., description='The identifier for this diagram.', title='Diagram ID')
    description: Optional[str] = Field(None, description='A summary of the diagram.', title='Diagram Description')
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    caption: Optional[str] = Field(None, description='A brief caption to annotate the diagram.', title='Caption')
    remarks: Optional[str] = Field(
        None,
        description='Commentary about the diagram that enhances it.',
        title='remarks field',
    )


class DateAuthorized(OscalBaseModel):
    __root__: constr(
        regex=
        r'^((2000|2400|2800|(19|2[0-9](0[48]|[2468][048]|[13579][26])))-02-29)|(((19|2[0-9])[0-9]{2})-02-(0[1-9]|1[0-9]|2[0-8]))|(((19|2[0-9])[0-9]{2})-(0[13578]|10|12)-(0[1-9]|[12][0-9]|3[01]))|(((19|2[0-9])[0-9]{2})-(0[469]|11)-(0[1-9]|[12][0-9]|30))(Z|[+-][0-9]{2}:[0-9]{2})?$'
    ) = Field(
        ...,
        description='The date the system received its authorization.',
        title='System Authorization Date',
    )


class DataFlow(OscalBaseModel):
    description: str = Field(
        ...,
        description="A summary of the system's data flow.",
        title='Data Flow Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    diagrams: Optional[List[Diagram]] = Field(None)
    remarks: Optional[common.Remarks] = None


class Categorization(OscalBaseModel):
    system: AnyUrl = Field(
        ...,
        description='Specifies the information type identification system used.',
        title='Information Type Identification System',
    )
    information_type_ids: Optional[List[InformationTypeId]] = Field(None, alias='information-type-ids')


class ByComponent(OscalBaseModel):
    component_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        alias='component-uuid',
        description='A reference to the component that is implementing a given control or control statement.',
        title='Component Universally Unique Identifier Reference',
    )
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier that can be used to reference this by-component entry elsewhere in an OSCAL document. A UUID should be consistently used for a given resource across revisions of the document.',
        title='By-Component Universally Unique Identifier',
    )
    description: str = Field(
        ...,
        description=
        'An implementation statement that describes how a control or a control statement is implemented within the referenced system component.',
        title='Control Implementation Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    set_parameters: Optional[List[SetParameter]] = Field(None, alias='set-parameters')
    implementation_status: Optional[common.ImplementationStatus] = Field(None, alias='implementation-status')
    export: Optional[Export] = Field(
        None,
        description='Identifies content intended for external consumption, such as with leveraged organizations.',
        title='Export',
    )
    inherited: Optional[List[Inherited]] = Field(None)
    satisfied: Optional[List[Satisfied]] = Field(None)
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    remarks: Optional[common.Remarks] = None


class Base(OscalBaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description='The prescribed base (Confidentiality, Integrity, or Availability) security impact level.',
        title='Base Level (Confidentiality, Integrity, or Availability)',
    )


class AvailabilityImpact(OscalBaseModel):
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    base: Base
    selected: Optional[Selected] = None
    adjustment_justification: Optional[AdjustmentJustification] = Field(None, alias='adjustment-justification')


class AuthorizationBoundary(OscalBaseModel):
    description: str = Field(
        ...,
        description="A summary of the system's authorization boundary.",
        title='Authorization Boundary Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    diagrams: Optional[List[Diagram]] = Field(None)
    remarks: Optional[str] = Field(
        None,
        description="Commentary about the system's authorization boundary that enhances the diagram.",
        title='remarks field',
    )


class Status1(OscalBaseModel):
    state: State = Field(..., description='The current operating status.', title='State')
    remarks: Optional[common.Remarks] = None


class Status(OscalBaseModel):
    state: State1 = Field(..., description='The operational status.', title='State')
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


class Statement(OscalBaseModel):
    statement_id: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        alias='statement-id',
        description='A reference to a control statement by its identifier',
        title='Control Statement Reference',
    )
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier that can be used to reference this control statement entry elsewhere in an OSCAL document. A UUID should be consistently used for a given resource across revisions of the document.',
        title='Control Statement Reference Universally Unique Identifier',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    by_components: Optional[List[ByComponent]] = Field(None, alias='by-components')
    remarks: Optional[common.Remarks] = None


class ImplementedRequirement(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier that can be used to reference this control requirement entry elsewhere in an OSCAL document. A UUID should be consistently used for a given resource across revisions of the document.',
        title='Control Requirement Universally Unique Identifier',
    )
    control_id: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        alias='control-id',
        description='A reference to a control with a corresponding id value.',
        title='Control Identifier Reference',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    set_parameters: Optional[List[SetParameter]] = Field(None, alias='set-parameters')
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    statements: Optional[List[Statement]] = Field(None)
    by_components: Optional[List[ByComponent]] = Field(None, alias='by-components')
    remarks: Optional[common.Remarks] = None


class ControlImplementation(OscalBaseModel):
    description: str = Field(
        ...,
        description=
        'A statement describing important things to know about how this set of control satisfaction documentation is approached.',
        title='Control Implementation Description',
    )
    set_parameters: Optional[List[SetParameter]] = Field(None, alias='set-parameters')
    implemented_requirements: List[ImplementedRequirement] = Field(..., alias='implemented-requirements')


class NetworkArchitecture(OscalBaseModel):
    description: str = Field(
        ...,
        description="A summary of the system's network architecture.",
        title='Network Architecture Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    diagrams: Optional[List[Diagram]] = Field(None)
    remarks: Optional[common.Remarks] = None


class LeveragedAuthorization(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier that can be used to reference this leveraged authorization entry elsewhere in an OSCAL document. A UUID should be consistently used for a given resource across revisions of the document.',
        title='Leveraged Authorization Universally Unique Identifier',
    )
    title: str = Field(
        ...,
        description='A human readable name for the leveraged authorization in the context of the system.',
        title='title field',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    party_uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                       ) = Field(
                           ...,
                           alias='party-uuid',
                           description='A reference to the party that manages the leveraged system.',
                           title='party-uuid field',
                       )
    date_authorized: DateAuthorized = Field(..., alias='date-authorized')
    remarks: Optional[common.Remarks] = None


class SystemImplementation(OscalBaseModel):
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    leveraged_authorizations: Optional[List[LeveragedAuthorization]] = Field(None, alias='leveraged-authorizations')
    users: List[common.SystemUser] = Field(...)
    components: List[SystemComponent] = Field(...)
    inventory_items: Optional[List[common.InventoryItem]] = Field(None, alias='inventory-items')
    remarks: Optional[common.Remarks] = None


class IntegrityImpact(OscalBaseModel):
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    base: Base
    selected: Optional[Selected] = None
    adjustment_justification: Optional[AdjustmentJustification] = Field(None, alias='adjustment-justification')


class ConfidentialityImpact(OscalBaseModel):
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    base: Base
    selected: Optional[Selected] = None
    adjustment_justification: Optional[AdjustmentJustification] = Field(None, alias='adjustment-justification')


class InformationType(OscalBaseModel):
    uuid: Optional[constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    )] = Field(
        None,
        description=
        'A globally unique identifier that can be used to reference this information type entry elsewhere in an OSCAL document. A UUID should be consistently used for a given resource across revisions of the document.',
        title='Information Type Universally Unique Identifier',
    )
    title: str = Field(
        ...,
        description=
        'A human readable name for the information type. This title should be meaningful within the context of the system.',
        title='title field',
    )
    description: str = Field(
        ...,
        description='A summary of how this information type is used within the system.',
        title='Information Type Description',
    )
    categorizations: Optional[List[Categorization]] = Field(None)
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    confidentiality_impact: ConfidentialityImpact = Field(
        ...,
        alias='confidentiality-impact',
        description=
        'The expected level of impact resulting from the unauthorized disclosure of the described information.',
        title='Confidentiality Impact Level',
    )
    integrity_impact: IntegrityImpact = Field(
        ...,
        alias='integrity-impact',
        description=
        'The expected level of impact resulting from the unauthorized modification of the described information.',
        title='Integrity Impact Level',
    )
    availability_impact: AvailabilityImpact = Field(
        ...,
        alias='availability-impact',
        description=
        'The expected level of impact resulting from the disruption of access to or use of the described information or the information system.',
        title='Availability Impact Level',
    )


class SystemInformation(OscalBaseModel):
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    information_types: List[InformationType] = Field(..., alias='information-types')


class SystemCharacteristics(OscalBaseModel):
    system_ids: List[common.SystemId] = Field(..., alias='system-ids')
    system_name: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        alias='system-name',
        description='The full name of the system.',
        title='System Name - Full',
    )
    system_name_short: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='system-name-short',
        description=
        'A short name for the system, such as an acronym, that is suitable for display in a data table or summary list.',
        title='System Name - Short',
    )
    description: str = Field(..., description='A summary of the system.', title='System Description')
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    date_authorized: Optional[DateAuthorized] = Field(None, alias='date-authorized')
    security_sensitivity_level: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        alias='security-sensitivity-level',
        description='The overall information system sensitivity categorization, such as defined by FIPS-199.',
        title='Security Sensitivity Level',
    )
    system_information: SystemInformation = Field(..., alias='system-information')
    security_impact_level: SecurityImpactLevel = Field(..., alias='security-impact-level')
    status: Status1
    authorization_boundary: AuthorizationBoundary = Field(..., alias='authorization-boundary')
    network_architecture: Optional[NetworkArchitecture] = Field(None, alias='network-architecture')
    data_flow: Optional[DataFlow] = Field(None, alias='data-flow')
    responsible_parties: Optional[List[common.ResponsibleParty]] = Field(None, alias='responsible-parties')
    remarks: Optional[common.Remarks] = None


class SystemSecurityPlan(OscalBaseModel):
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier for this catalog instance. This UUID should be changed when this document is revised.',
        title='System Security Plan Universally Unique Identifier',
    )
    metadata: common.Metadata
    import_profile: ImportProfile = Field(..., alias='import-profile')
    system_characteristics: SystemCharacteristics = Field(..., alias='system-characteristics')
    system_implementation: SystemImplementation = Field(..., alias='system-implementation')
    control_implementation: ControlImplementation = Field(..., alias='control-implementation')
    back_matter: Optional[common.BackMatter] = Field(None, alias='back-matter')


class Model(OscalBaseModel):
    system_security_plan: SystemSecurityPlan = Field(..., alias='system-security-plan')
