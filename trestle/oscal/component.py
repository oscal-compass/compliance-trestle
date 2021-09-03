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
import trestle.oscal.common as common


class Statement(OscalBaseModel):

    class Config:
        extra = Extra.forbid

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
    description: str = Field(
        ...,
        description='A summary of how the containing control statement is implemented by the component or capability.',
        title='Statement Implementation Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    remarks: Optional[common.Remarks] = None


class State(Enum):
    under_development = 'under-development'
    operational = 'operational'
    disposition = 'disposition'
    other = 'other'


class SetParameter(OscalBaseModel):

    class Config:
        extra = Extra.forbid

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


class IncorporatesComponent(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    component_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        alias='component-uuid',
        description='A reference to a component by its identifier',
        title='Component Reference',
    )
    description: str = Field(
        ...,
        description='A description of the component, including information about its function.',
        title='Component Description',
    )


class ImportComponentDefinition(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    href: str = Field(
        ...,
        description=
        'A link to a resource that defines a set of components and/or capabilities to import into this collection.',
        title='Hyperlink Reference',
    )


class ImplementedRequirement(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                 ) = Field(
                     ...,
                     description='A unique identifier for a specific control implementation.',
                     title='Control Implementation Identifier',
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
    description: str = Field(
        ...,
        description=
        'A description of how the specified control is implemented for the containing component or capability.',
        title='Control Implementation Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    set_parameters: Optional[List[SetParameter]] = Field(None, alias='set-parameters')
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    statements: Optional[List[Statement]] = Field(None)
    remarks: Optional[common.Remarks] = None


class ControlImplementation(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                 ) = Field(
                     ...,
                     description='A unique identifier for the set of implemented controls.',
                     title='Control Implementation Set Identifier',
                 )
    source: str = Field(
        ...,
        description=
        'A reference to an OSCAL catalog or profile providing the referenced control or subcontrol definition.',
        title='Source Resource Reference',
    )
    description: str = Field(
        ...,
        description=
        'A description of how the specified set of controls are implemented for the containing component or capability.',
        title='Control Implementation Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    set_parameters: Optional[List[SetParameter]] = Field(None, alias='set-parameters')
    implemented_requirements: List[ImplementedRequirement] = Field(..., alias='implemented-requirements')


class Capability(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
                 ) = Field(
                     ...,
                     description='A unique identifier for a capability.',
                     title='Capability Identifier',
                 )
    name: constr(regex=r'^\S(.*\S)?$') = Field(
        ...,
        description="The capability's human-readable name.",
        title='Capability Name',
    )
    description: str = Field(..., description='A summary of the capability.', title='Capability Description')
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    incorporates_components: Optional[List[IncorporatesComponent]] = Field(None, alias='incorporates-components')
    control_implementations: Optional[List[ControlImplementation]] = Field(None, alias='control-implementations')
    remarks: Optional[common.Remarks] = None


class Status(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    state: State = Field(..., description='The operational status.', title='State')
    remarks: Optional[common.Remarks] = None


class SystemComponent(OscalBaseModel):

    class Config:
        extra = Extra.forbid

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


class DefinedComponent(OscalBaseModel):

    class Config:
        extra = Extra.forbid

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
        description='A human readable name for the component.',
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
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    protocols: Optional[List[common.Protocol]] = Field(None)
    control_implementations: Optional[List[ControlImplementation]] = Field(None, alias='control-implementations')
    remarks: Optional[common.Remarks] = None


class ComponentDefinition(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier for this component definition instance. This UUID should be changed when this document is revised.',
        title='Component Definition Universally Unique Identifier',
    )
    metadata: common.Metadata
    import_component_definitions: Optional[List[ImportComponentDefinition]] = Field(
        None, alias='import-component-definitions'
    )
    components: Optional[List[DefinedComponent]] = Field(None)
    capabilities: Optional[List[Capability]] = Field(None)
    back_matter: Optional[common.BackMatter] = Field(None, alias='back-matter')


class Model(OscalBaseModel):
    component_definition: ComponentDefinition = Field(..., alias='component-definition')
