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

from pydantic import AnyUrl, EmailStr, Extra, Field, conint, constr

from trestle.core.base_model import OscalBaseModel


class AddrLine(OscalBaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$'
                     ) = Field(..., description='A single line of an address.', title='Address line')


class Address(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    type: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None, description='Indicates the type of address.', title='Address Type'
    )
    addr_lines: Optional[List[AddrLine]] = Field(None, alias='addr-lines')
    city: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        description='City, town or geographical region for the mailing address.',
        title='City',
    )
    state: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        description='State, province or analogous geographical region for mailing address',
        title='State',
    )
    postal_code: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='postal-code',
        description='Postal or ZIP code for mailing address',
        title='Postal Code',
    )
    country: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        description='The ISO 3166-1 alpha-2 country code for the mailing address.',
        title='Country Code',
    )


class WithinDateRange(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    start: datetime = Field(
        ...,
        description='The task must occur on or after the specified date.',
        title='Start Date Condition',
    )
    end: datetime = Field(
        ...,
        description='The task must occur on or before the specified date.',
        title='End Date Condition',
    )


class Version(OscalBaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description=
        'A string used to distinguish the current version of the document from other previous (and future) versions.',
        title='Document Version',
    )


class Value(OscalBaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$'
                     ) = Field(..., description='A parameter value or set of values.', title='Parameter Value')


class Unit(Enum):
    seconds = 'seconds'
    minutes = 'minutes'
    hours = 'hours'
    days = 'days'
    months = 'months'
    years = 'years'


class Type3(Enum):
    tool = 'tool'
    assessment_platform = 'assessment-platform'
    party = 'party'


class Type2(OscalBaseModel):
    __root__: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description=
        'Identifies the nature of the observation. More than one may be used to further qualify and enable filtering.',
        title='Observation Type',
    )


class Type1(Enum):
    statement_id = 'statement-id'
    objective_id = 'objective-id'


class Type(Enum):
    person = 'person'
    organization = 'organization'


class Transport(Enum):
    TCP = 'TCP'
    UDP = 'UDP'


class ThreatId(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    system: AnyUrl = Field(
        ...,
        description='Specifies the source of the threat information.',
        title='Threat Type Identification System',
    )
    href: Optional[str] = Field(
        None,
        description='An optional location for the threat data, from which this ID originates.',
        title='Threat Information Resource Reference',
    )
    id: str


class TelephoneNumber(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    type: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None, description='Indicates the type of phone number.', title='type flag'
    )
    number: str


class SystemId(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    identifier_type: Optional[AnyUrl] = Field(
        None,
        alias='identifier-type',
        description='Identifies the identification system from which the provided identifier was assigned.',
        title='Identification System Type',
    )
    id: str


class StatementId(OscalBaseModel):
    __root__: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description='Used to constrain the selection to only specificity identified statements.',
        title='Include Specific Statements',
    )


class Source(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    task_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        alias='task-uuid',
        description=
        'Uniquely identifies an assessment activity to be performed as part of the event. This UUID may be referenced elsewhere in an OSCAL document when referring to this information. A UUID should be consistently used for this schedule across revisions of the document.',
        title='Task Universally Unique Identifier',
    )


class SelectObjectiveById(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    objective_id: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        alias='objective-id',
        description='Points to an assessment objective.',
        title='Objective ID',
    )


class RoleId(OscalBaseModel):
    __root__: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description='A reference to the roles served by the user.',
        title='Role Identifier Reference',
    )


class RiskStatus(OscalBaseModel):
    __root__: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description='Describes the status of the associated risk.',
        title='Risk Status',
    )


class Remarks(OscalBaseModel):
    __root__: str = Field(
        ...,
        description='Additional commentary on the containing object.',
        title='Remarks',
    )


class RelatedRisk(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    risk_uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                      ) = Field(
                          ...,
                          alias='risk-uuid',
                          description='References an risk defined in the list of risks.',
                          title='Risk Universally Unique Identifier Reference',
                      )


class RelatedObservation1(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    observation_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        alias='observation-uuid',
        description='References an observation defined in the list of observations.',
        title='Observation Universally Unique Identifier Reference',
    )


class RelatedObservation(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    observation_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        alias='observation-uuid',
        description='References an observation defined in the list of observations.',
        title='Observation Universally Unique Identifier Reference',
    )


class Published(OscalBaseModel):
    __root__: datetime = Field(
        ...,
        description=
        'The date and time the document was published. The date-time value must be formatted according to RFC 3339 with full time and time zone included.',
        title='Publication Timestamp',
    )


class Property(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    name: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description=
        "A textual label that uniquely identifies a specific attribute, characteristic, or quality of the property's containing object.",
        title='Property Name',
    )
    uuid: Optional[constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    )] = Field(
        None,
        description=
        'A unique identifier that can be used to reference this property elsewhere in an OSCAL document. A UUID should be consistently used for a given location across revisions of the document.',
        title='Property Universally Unique Identifier',
    )
    ns: Optional[AnyUrl] = Field(
        None,
        description=
        "A namespace qualifying the property's name. This allows different organizations to associate distinct semantics with the same name.",
        title='Property Namespace',
    )
    value: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description='Indicates the value of the attribute, characteristic, or quality.',
        title='Property Value',
    )
    class_: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='class',
        description=
        "A textual label that provides a sub-type or characterization of the property's name. This can be used to further distinguish or discriminate between the semantics of multiple properties of the same object with the same name and ns.",
        title='Property Class',
    )
    remarks: Optional[Remarks] = None


class PortRange(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    start: Optional[conint(ge=0, multiple_of=1)] = Field(
        None,
        description='Indicates the starting port number in a port range',
        title='Start',
    )
    end: Optional[conint(ge=0, multiple_of=1)] = Field(
        None,
        description='Indicates the ending port number in a port range',
        title='End',
    )
    transport: Optional[Transport] = Field(None, description='Indicates the transport type.', title='Transport')


class Protocol(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: Optional[constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    )] = Field(
        None,
        description=
        'A globally unique identifier that can be used to reference this service protocol entry elsewhere in an OSCAL document. A UUID should be consistently used for a given resource across revisions of the document.',
        title='Service Protocol Information Universally Unique Identifier',
    )
    name: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description=
        'The common name of the protocol, which should be the appropriate "service name" from the IANA Service Name and Transport Protocol Port Number Registry.',
        title='Protocol Name',
    )
    title: Optional[str] = Field(
        None,
        description='A human readable name for the protocol (e.g., Transport Layer Security).',
        title='Protocol Title',
    )
    port_ranges: Optional[List[PortRange]] = Field(None, alias='port-ranges')


class PartyUuid(OscalBaseModel):
    __root__: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                     ) = Field(
                         ...,
                         description='References a party defined in metadata.',
                         title='Party Reference',
                     )


class ParameterValue(OscalBaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$'
                     ) = Field(..., description='A parameter value or set of values.', title='Parameter Value')


class ParameterGuideline(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    prose: str = Field(
        ...,
        description='Prose permits multiple paragraphs, lists, tables etc.',
        title='Guideline Text',
    )


class OscalVersion(OscalBaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description='The OSCAL model version the document was authored against.',
        title='OSCAL version',
    )


class OnDate(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    date: datetime = Field(
        ...,
        description='The task must occur on the specified date.',
        title='On Date Condition',
    )


class MemberOfOrganization(OscalBaseModel):
    __root__: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'Identifies that the party object is a member of the organization associated with the provided UUID.',
        title='Organizational Affiliation',
    )


class LoggedBy(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    party_uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                       ) = Field(
                           ...,
                           alias='party-uuid',
                           description='A pointer to the party who is making the log entry.',
                           title='Party UUID Reference',
                       )
    role_id: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='role-id',
        description='A point to the role-id of the role in which the party is making the log entry.',
        title='Actor Role',
    )


class LocationUuid(OscalBaseModel):
    __root__: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                     ) = Field(
                         ...,
                         description='References a location defined in metadata.',
                         title='Location Reference',
                     )


class Link(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    href: str = Field(
        ...,
        description='A resolvable URL reference to a resource.',
        title='Hypertext Reference',
    )
    rel: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        description=
        "Describes the type of relationship provided by the link. This can be an indicator of the link's purpose.",
        title='Relation',
    )
    media_type: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='media-type',
        description=
        'Specifies a media type as defined by the Internet Assigned Numbers Authority (IANA) Media Types Registry.',
        title='Media Type',
    )
    text: Optional[str] = Field(
        None,
        description='A textual label to associate with the link, which may be used for presentation in a tool.',
        title='Link Text',
    )


class LastModified(OscalBaseModel):
    __root__: datetime = Field(
        ...,
        description=
        'The date and time the document was last modified. The date-time value must be formatted according to RFC 3339 with full time and time zone included.',
        title='Last Modified Timestamp',
    )


class ImportSsp(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    href: str = Field(
        ...,
        description='>A resolvable URL reference to the system security plan for the system being assessed.',
        title='System Security Plan Reference',
    )
    remarks: Optional[Remarks] = None


class ImplementationStatus(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    state: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description='Identifies the implementation status of the control or control objective.',
        title='Implementation State',
    )
    remarks: Optional[Remarks] = None


class HowMany(Enum):
    one = 'one'
    one_or_more = 'one-or-more'


class Hash(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    algorithm: constr(regex=r'^\S(.*\S)?$'
                      ) = Field(..., description='Method by which a hash is derived', title='Hash algorithm')
    value: str


class FunctionPerformed(OscalBaseModel):
    __root__: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description='Describes a function performed for a given authorized privilege by this user class.',
        title='Functions Performed',
    )


class Facet(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    name: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description='The name of the risk metric within the specified system.',
        title='Facet Name',
    )
    system: AnyUrl = Field(
        ...,
        description=
        'Specifies the naming system under which this risk metric is organized, which allows for the same names to be used in different systems controlled by different parties. This avoids the potential of a name clash.',
        title='Naming System',
    )
    value: constr(regex=r'^\S(.*\S)?$'
                  ) = Field(..., description='Indicates the value of the facet.', title='Facet Value')
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    remarks: Optional[Remarks] = None


class ExternalId(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    scheme: AnyUrl = Field(
        ...,
        description='Indicates the type of external identifier.',
        title='External Identifier Schema',
    )
    id: str


class EmailAddress(OscalBaseModel):
    __root__: EmailStr = Field(
        ...,
        description='An email address as defined by RFC 5322 Section 3.4.1.',
        title='Email Address',
    )


class DocumentId(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    scheme: Optional[AnyUrl] = Field(
        None,
        description=
        'Qualifies the kind of document identifier using a URI. If the scheme is not provided the value of the element will be interpreted as a string of characters.',
        title='Document Identification Scheme',
    )
    identifier: str


class Dependency(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    task_uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                      ) = Field(
                          ...,
                          alias='task-uuid',
                          description='References a unique task by UUID.',
                          title='Task Universally Unique Identifier Reference',
                      )
    remarks: Optional[Remarks] = None


class ControlObjectiveSelection(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    description: Optional[str] = Field(
        None,
        description='A human-readable description of this collection of control objectives.',
        title='Control Objectives Description',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    include_all: Optional[Dict[str, Any]] = Field(
        None,
        alias='include-all',
        description='A key word to indicate all.',
        title='All',
    )
    include_objectives: Optional[List[SelectObjectiveById]] = Field(None, alias='include-objectives')
    exclude_objectives: Optional[List[SelectObjectiveById]] = Field(None, alias='exclude-objectives')
    remarks: Optional[Remarks] = None


class Citation(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    text: str = Field(..., description='A line of citation text.', title='Citation Text')
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)


class Base64(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    filename: Optional[str] = Field(
        None,
        description=
        'Name of the file before it was encoded as Base64 to be embedded in a resource. This is the name that will be assigned to the file when the file is decoded.',
        title='File Name',
    )
    media_type: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='media-type',
        description=
        'Specifies a media type as defined by the Internet Assigned Numbers Authority (IANA) Media Types Registry.',
        title='Media Type',
    )
    value: str


class AuthorizedPrivilege(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    title: str = Field(
        ...,
        description='A human readable name for the privilege.',
        title='Privilege Title',
    )
    description: Optional[str] = Field(
        None,
        description="A summary of the privilege's purpose within the system.",
        title='Privilege Description',
    )
    functions_performed: List[FunctionPerformed] = Field(..., alias='functions-performed')


class AtFrequency(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    period: conint(
        ge=1, multiple_of=1
    ) = Field(
        ...,
        description='The task must occur after the specified period has elapsed.',
        title='Period',
    )
    unit: Unit = Field(..., description='The unit of time for the period.', title='Time Unit')


class AssessmentSubjectPlaceholder(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'Uniquely identifies a set of assessment subjects that will be identified by a task or an activity that is part of a task.',
        title='Assessment Subject Placeholder Universally Unique Identifier',
    )
    description: Optional[str] = Field(
        None,
        description='A human-readable description of intent of this assessment subject placeholder.',
        title='Assessment Subject Placeholder Description',
    )
    sources: List[Source] = Field(...)
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    remarks: Optional[Remarks] = None


class AssessmentPart(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: Optional[constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    )] = Field(
        None,
        description=
        "A unique identifier for a specific part instance. This identifier's uniqueness is document scoped and is intended to be consistent for the same part across minor revisions of the document.",
        title='Part Identifier',
    )
    name: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description="A textual label that uniquely identifies the part's semantic type.",
        title='Part Name',
    )
    ns: Optional[AnyUrl] = Field(
        None,
        description=
        "A namespace qualifying the part's name. This allows different organizations to associate distinct semantics with the same name.",
        title='Part Namespace',
    )
    class_: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='class',
        description=
        "A textual label that provides a sub-type or characterization of the part's name. This can be used to further distinguish or discriminate between the semantics of multiple parts of the same control with the same name and ns.",
        title='Part Class',
    )
    title: Optional[str] = Field(
        None,
        description='A name given to the part, which may be used by a tool for display and navigation.',
        title='Part Title',
    )
    props: Optional[List[Property]] = Field(None)
    prose: Optional[str] = Field(
        None,
        description='Permits multiple paragraphs, lists, tables etc.',
        title='Part Text',
    )
    parts: Optional[List[AssessmentPart]] = None
    links: Optional[List[Link]] = Field(None)


class AssessmentMethod(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'Uniquely identifies this defined assessment method. This UUID may be referenced elsewhere in an OSCAL document when referring to this information. A UUID should be consistently used for a given assessment method across revisions of the document.',
        title='Assessment Method Universally Unique Identifier',
    )
    description: Optional[str] = Field(
        None,
        description='A human-readable description of this assessment method.',
        title='Assessment Method Description',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    part: AssessmentPart
    remarks: Optional[Remarks] = None


class Timing(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    on_date: Optional[OnDate] = Field(
        None,
        alias='on-date',
        description='The task is intended to occur on the specified date.',
        title='On Date Condition',
    )
    within_date_range: Optional[WithinDateRange] = Field(
        None,
        alias='within-date-range',
        description='The task is intended to occur within the specified date range.',
        title='On Date Range Condition',
    )
    at_frequency: Optional[AtFrequency] = Field(
        None,
        alias='at-frequency',
        description='The task is intended to occur at the specified frequency.',
        title='Frequency Condition',
    )


class Test(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    expression: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description='A formal (executable) expression of a constraint',
        title='Constraint test',
    )
    remarks: Optional[Remarks] = None


class ParameterConstraint(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    description: Optional[str] = Field(
        None,
        description='A textual summary of the constraint to be applied.',
        title='Constraint Description',
    )
    tests: Optional[List[Test]] = Field(None)


class SystemUser(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                 ) = Field(
                     ...,
                     description='The unique identifier for the user class.',
                     title='User Universally Unique Identifier',
                 )
    title: Optional[str] = Field(
        None,
        description='A name given to the user, which may be used by a tool for display and navigation.',
        title='User Title',
    )
    short_name: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='short-name',
        description='A short common name, abbreviation, or acronym for the user.',
        title='User Short Name',
    )
    description: Optional[str] = Field(
        None,
        description="A summary of the user's purpose within the system.",
        title='User Description',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    role_ids: Optional[List[RoleId]] = Field(None, alias='role-ids')
    authorized_privileges: Optional[List[AuthorizedPrivilege]] = Field(None, alias='authorized-privileges')
    remarks: Optional[Remarks] = None


class SubjectReference(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    subject_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        alias='subject-uuid',
        description="A pointer to a component, inventory-item, location, party, user, or resource using it's UUID.",
        title='Subject Universally Unique Identifier Reference',
    )
    type: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description='Used to indicate the type of object pointed to by the uuid-ref within a subject.',
        title='Subject Universally Unique Identifier Reference Type',
    )
    title: Optional[str] = Field(
        None,
        description='The title or name for the referenced subject.',
        title='Subject Reference Title',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    remarks: Optional[Remarks] = None


class MitigatingFactor(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'Uniquely identifies this mitigating factor. This UUID may be referenced elsewhere in an OSCAL document when referring to this information. Once assigned, a UUID should be consistently used for a given mitigating factor across revisions.',
        title='Mitigating Factor Universally Unique Identifier',
    )
    implementation_uuid: Optional[constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    )] = Field(
        None,
        alias='implementation-uuid',
        description='Points to an implementation statement in the SSP.',
        title='Implementation UUID',
    )
    description: str = Field(
        ...,
        description='A human-readable description of this mitigating factor.',
        title='Mitigating Factor Description',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    subjects: Optional[List[SubjectReference]] = Field(None)


class SelectSubjectById(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    subject_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        alias='subject-uuid',
        description="A pointer to a component, inventory-item, location, party, user, or resource using it's UUID.",
        title='Subject Universally Unique Identifier Reference',
    )
    type: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description='Used to indicate the type of object pointed to by the uuid-ref within a subject.',
        title='Subject Universally Unique Identifier Reference Type',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    remarks: Optional[Remarks] = None


class AssessmentSubject(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    type: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description=
        'Indicates the type of assessment subject, such as a component, inventory, item, location, or party represented by this selection statement.',
        title='Subject Type',
    )
    description: Optional[str] = Field(
        None,
        description='A human-readable description of the collection of subjects being included in this assessment.',
        title='Include Subjects Description',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    include_all: Optional[Dict[str, Any]] = Field(
        None,
        alias='include-all',
        description='A key word to indicate all.',
        title='All',
    )
    include_subjects: Optional[List[SelectSubjectById]] = Field(None, alias='include-subjects')
    exclude_subjects: Optional[List[SelectSubjectById]] = Field(None, alias='exclude-subjects')
    remarks: Optional[Remarks] = None


class Role(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    id: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description=
        "A unique identifier for a specific role instance. This identifier's uniqueness is document scoped and is intended to be consistent for the same role across minor revisions of the document.",
        title='Role Identifier',
    )
    title: str = Field(
        ...,
        description='A name given to the role, which may be used by a tool for display and navigation.',
        title='Role Title',
    )
    short_name: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='short-name',
        description='A short common name, abbreviation, or acronym for the role.',
        title='Role Short Name',
    )
    description: Optional[str] = Field(
        None,
        description="A summary of the role's purpose and associated responsibilities.",
        title='Role Description',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    remarks: Optional[Remarks] = None


class Rlink(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    href: str = Field(
        ...,
        description='A resolvable URI reference to a resource.',
        title='Hypertext Reference',
    )
    media_type: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='media-type',
        description=
        'Specifies a media type as defined by the Internet Assigned Numbers Authority (IANA) Media Types Registry.',
        title='Media Type',
    )
    hashes: Optional[List[Hash]] = Field(None)


class Resource(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier that can be used to reference this defined resource elsewhere in an OSCAL document. A UUID should be consistently used for a given resource across revisions of the document.',
        title='Resource Universally Unique Identifier',
    )
    title: Optional[str] = Field(
        None,
        description='A name given to the resource, which may be used by a tool for display and navigation.',
        title='Resource Title',
    )
    description: Optional[str] = Field(
        None,
        description='A short summary of the resource used to indicate the purpose of the resource.',
        title='Resource Description',
    )
    props: Optional[List[Property]] = Field(None)
    document_ids: Optional[List[DocumentId]] = Field(None, alias='document-ids')
    citation: Optional[Citation] = Field(
        None,
        description='A citation consisting of end note text and optional structured bibliographic data.',
        title='Citation',
    )
    rlinks: Optional[List[Rlink]] = Field(None)
    base64: Optional[Base64] = Field(
        None,
        description='The Base64 alphabet in RFC 2045 - aligned with XSD.',
        title='Base64',
    )
    remarks: Optional[Remarks] = None


class BackMatter(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    resources: Optional[List[Resource]] = Field(None)


class Revision(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    title: Optional[str] = Field(
        None,
        description='A name given to the document revision, which may be used by a tool for display and navigation.',
        title='Document Title',
    )
    published: Optional[Published] = None
    last_modified: Optional[LastModified] = Field(None, alias='last-modified')
    version: Optional[Version] = None
    oscal_version: Optional[OscalVersion] = Field(None, alias='oscal-version')
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    remarks: Optional[Remarks] = None


class ResponsibleRole(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    role_id: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        alias='role-id',
        description='The role that is responsible for the business function.',
        title='Responsible Role ID',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    party_uuids: Optional[List[PartyUuid]] = Field(None, alias='party-uuids')
    remarks: Optional[Remarks] = None


class ResponsibleParty(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    role_id: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        alias='role-id',
        description='The role that the party is responsible for.',
        title='Responsible Role',
    )
    party_uuids: List[PartyUuid] = Field(..., alias='party-uuids')
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    remarks: Optional[Remarks] = None


class RequiredAsset(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'Uniquely identifies this required asset. This UUID may be referenced elsewhere in an OSCAL document when referring to this information. Once assigned, a UUID should be consistently used for a given required asset across revisions.',
        title='Required Universally Unique Identifier',
    )
    subjects: Optional[List[SubjectReference]] = Field(None)
    title: Optional[str] = Field(
        None,
        description='The title for this required asset.',
        title='Title for Required Asset',
    )
    description: str = Field(
        ...,
        description='A human-readable description of this required asset.',
        title='Description of Required Asset',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    remarks: Optional[Remarks] = None


class RelevantEvidence(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    href: Optional[str] = Field(
        None,
        description='>A resolvable URL reference to relevant evidence.',
        title='Relevant Evidence Reference',
    )
    description: str = Field(
        ...,
        description='A human-readable description of this evidence.',
        title='Relevant Evidence Description',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    remarks: Optional[Remarks] = None


class Party(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A unique identifier that can be used to reference this defined location elsewhere in an OSCAL document. A UUID should be consistently used for a given party across revisions of the document.',
        title='Party Universally Unique Identifier',
    )
    type: Type = Field(
        ...,
        description='A category describing the kind of party the object describes.',
        title='Party Type',
    )
    name: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        description='The full name of the party. This is typically the legal name associated with the party.',
        title='Party Name',
    )
    short_name: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        alias='short-name',
        description='A short common name, abbreviation, or acronym for the party.',
        title='Party Short Name',
    )
    external_ids: Optional[List[ExternalId]] = Field(None, alias='external-ids')
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    email_addresses: Optional[List[EmailAddress]] = Field(None, alias='email-addresses')
    telephone_numbers: Optional[List[TelephoneNumber]] = Field(None, alias='telephone-numbers')
    addresses: Optional[List[Address]] = Field(None)
    location_uuids: Optional[List[LocationUuid]] = Field(None, alias='location-uuids')
    member_of_organizations: Optional[List[MemberOfOrganization]] = Field(None, alias='member-of-organizations')
    remarks: Optional[Remarks] = None


class Part(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    id: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        description=
        "A unique identifier for a specific part instance. This identifier's uniqueness is document scoped and is intended to be consistent for the same part across minor revisions of the document.",
        title='Part Identifier',
    )
    name: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description="A textual label that uniquely identifies the part's semantic type.",
        title='Part Name',
    )
    ns: Optional[AnyUrl] = Field(
        None,
        description=
        "A namespace qualifying the part's name. This allows different organizations to associate distinct semantics with the same name.",
        title='Part Namespace',
    )
    class_: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='class',
        description=
        "A textual label that provides a sub-type or characterization of the part's name. This can be used to further distinguish or discriminate between the semantics of multiple parts of the same control with the same name and ns.",
        title='Part Class',
    )
    title: Optional[str] = Field(
        None,
        description='A name given to the part, which may be used by a tool for display and navigation.',
        title='Part Title',
    )
    props: Optional[List[Property]] = Field(None)
    prose: Optional[str] = Field(
        None,
        description='Permits multiple paragraphs, lists, tables etc.',
        title='Part Text',
    )
    parts: Optional[List[Part]] = None
    links: Optional[List[Link]] = Field(None)


class LocalObjective(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    control_id: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        alias='control-id',
        description='A reference to a control with a corresponding id value.',
        title='Control Identifier Reference',
    )
    description: Optional[str] = Field(
        None,
        description='A human-readable description of this control objective.',
        title='Objective Description',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    parts: List[Part] = Field(...)
    remarks: Optional[Remarks] = None


class ParameterSelection(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    how_many: Optional[HowMany] = Field(
        None,
        alias='how-many',
        description=
        'Describes the number of selections that must occur. Without this setting, only one value should be assumed to be permitted.',
        title='Parameter Cardinality',
    )
    choice: Optional[List[str]] = Field(None)


class Parameter(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    id: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        description=
        "A unique identifier for a specific parameter instance. This identifier's uniqueness is document scoped and is intended to be consistent for the same parameter across minor revisions of the document.",
        title='Parameter Identifier',
    )
    class_: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='class',
        description='A textual label that provides a characterization of the parameter.',
        title='Parameter Class',
    )
    depends_on: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='depends-on',
        description='Another parameter invoking this one',
        title='Depends on',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    label: Optional[str] = Field(
        None,
        description=
        'A short, placeholder name for the parameter, which can be used as a substitute for a value if no value is assigned.',
        title='Parameter Label',
    )
    usage: Optional[str] = Field(
        None,
        description='Describes the purpose and use of a parameter',
        title='Parameter Usage Description',
    )
    constraints: Optional[List[ParameterConstraint]] = Field(None)
    guidelines: Optional[List[ParameterGuideline]] = Field(None)
    values: Optional[List[ParameterValue]] = Field(None)
    select: Optional[ParameterSelection] = None
    remarks: Optional[Remarks] = None


class OriginActor(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    type: Type3 = Field(..., description='The kind of actor.', title='Actor Type')
    actor_uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                       ) = Field(
                           ...,
                           alias='actor-uuid',
                           description='A pointer to the tool or person based on the associated type.',
                           title='Actor Universally Unique Identifier Reference',
                       )
    role_id: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='role-id',
        description='For a party, this can optionally be used to specify the role the actor was performing.',
        title='Actor Role',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)


class Location(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A unique identifier that can be used to reference this defined location elsewhere in an OSCAL document. A UUID should be consistently used for a given location across revisions of the document.',
        title='Location Universally Unique Identifier',
    )
    title: Optional[str] = Field(
        None,
        description='A name given to the location, which may be used by a tool for display and navigation.',
        title='Location Title',
    )
    address: Address
    email_addresses: Optional[List[EmailAddress]] = Field(None, alias='email-addresses')
    telephone_numbers: Optional[List[TelephoneNumber]] = Field(None, alias='telephone-numbers')
    urls: Optional[List[AnyUrl]] = Field(None)
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    remarks: Optional[Remarks] = None


class Metadata(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    title: str = Field(
        ...,
        description='A name given to the document, which may be used by a tool for display and navigation.',
        title='Document Title',
    )
    published: Optional[Published] = None
    last_modified: LastModified = Field(..., alias='last-modified')
    version: Version
    oscal_version: OscalVersion = Field(..., alias='oscal-version')
    revisions: Optional[List[Revision]] = Field(None)
    document_ids: Optional[List[DocumentId]] = Field(None, alias='document-ids')
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    roles: Optional[List[Role]] = Field(None)
    locations: Optional[List[Location]] = Field(None)
    parties: Optional[List[Party]] = Field(None)
    responsible_parties: Optional[List[ResponsibleParty]] = Field(None, alias='responsible-parties')
    remarks: Optional[Remarks] = None


class ImplementedComponent(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    component_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        alias='component-uuid',
        description='A reference to a component that is implemented as part of an inventory item.',
        title='Component Universally Unique Identifier Reference',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    responsible_parties: Optional[List[ResponsibleParty]] = Field(None, alias='responsible-parties')
    remarks: Optional[Remarks] = None


class InventoryItem(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier that can be used to reference this inventory item entry elsewhere in an OSCAL document. A UUID should be consistently used for a given resource across revisions of the document.',
        title='Inventory Item Universally Unique Identifier',
    )
    description: str = Field(
        ...,
        description='A summary of the inventory item stating its purpose within the system.',
        title='Inventory Item Description',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    responsible_parties: Optional[List[ResponsibleParty]] = Field(None, alias='responsible-parties')
    implemented_components: Optional[List[ImplementedComponent]] = Field(None, alias='implemented-components')
    remarks: Optional[Remarks] = None


class IdentifiedSubject(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    subject_placeholder_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        alias='subject-placeholder-uuid',
        description='References a unique assessment subject placeholder defined by this task.',
        title='Assessment Subject Placeholder Universally Unique Identifier Reference',
    )
    subjects: List[AssessmentSubject] = Field(...)


class RelatedTask(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    task_uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                      ) = Field(
                          ...,
                          alias='task-uuid',
                          description='References a unique task by UUID.',
                          title='Task Universally Unique Identifier Reference',
                      )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    responsible_parties: Optional[List[ResponsibleParty]] = Field(None, alias='responsible-parties')
    subjects: Optional[List[AssessmentSubject]] = Field(None)
    identified_subject: Optional[IdentifiedSubject] = Field(
        None,
        alias='identified-subject',
        description='Used to detail assessment subjects that were identfied by this task.',
        title='Identified Subject',
    )
    remarks: Optional[Remarks] = None


class RelatedResponse(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    response_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        alias='response-uuid',
        description='References a unique risk response by UUID.',
        title='Response Universally Unique Identifier Reference',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    related_tasks: Optional[List[RelatedTask]] = Field(None, alias='related-tasks')
    remarks: Optional[Remarks] = None


class AssociatedActivity(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    activity_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        alias='activity-uuid',
        description='References an activity defined in the list of activities.',
        title='Activity Universally Unique Identifier Reference',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    responsible_roles: Optional[List[ResponsibleRole]] = Field(None, alias='responsible-roles')
    subjects: List[AssessmentSubject] = Field(...)
    remarks: Optional[Remarks] = None


class Task(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                 ) = Field(
                     ...,
                     description='Uniquely identifies this assessment task.',
                     title='Task Universally Unique Identifier',
                 )
    type: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(..., description='The type of task.', title='Task Type')
    title: str = Field(..., description='The title for this task.', title='Task Title')
    description: Optional[str] = Field(
        None,
        description='A human-readable description of this task.',
        title='Task Description',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    timing: Optional[Timing] = Field(
        None,
        description='The timing under which the task is intended to occur.',
        title='Event Timing',
    )
    dependencies: Optional[List[Dependency]] = Field(None)
    tasks: Optional[List[Task]] = None
    associated_activities: Optional[List[AssociatedActivity]] = Field(None, alias='associated-activities')
    subjects: Optional[List[AssessmentSubject]] = Field(None)
    responsible_roles: Optional[List[ResponsibleRole]] = Field(None, alias='responsible-roles')
    remarks: Optional[Remarks] = None


class UsesComponent(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    component_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        alias='component-uuid',
        description='A reference to a component that is implemented as part of an inventory item.',
        title='Component Universally Unique Identifier Reference',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    responsible_parties: Optional[List[ResponsibleParty]] = Field(None, alias='responsible-parties')
    remarks: Optional[Remarks] = None


class AssessmentPlatform(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                 ) = Field(
                     ...,
                     description='Uniquely identifies this assessment Platform.',
                     title='Assessment Platform Universally Unique Identifier',
                 )
    title: Optional[str] = Field(
        None,
        description='The title or name for the assessment platform.',
        title='Assessment Platform Title',
    )
    props: Optional[List[Property]] = Field(None)
    links: Optional[List[Link]] = Field(None)
    uses_components: Optional[List[UsesComponent]] = Field(None, alias='uses-components')
    remarks: Optional[Remarks] = None


AssessmentPart.update_forward_refs()
Part.update_forward_refs()
Task.update_forward_refs()
