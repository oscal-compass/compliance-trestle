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


class WithId(OscalBaseModel):
    __root__: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(..., description='', title='Match Controls by Identifier')


class WithChildControls(Enum):
    yes = 'yes'
    no = 'no'


class SetParameter(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    param_id: constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    ) = Field(
        ...,
        alias='param-id',
        description="Indicates the value of the 'id' flag on a target parameter; i.e. which parameter to set",
        title='Parameter ID',
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
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
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
    constraints: Optional[List[common.ParameterConstraint]] = Field(None)
    guidelines: Optional[List[common.ParameterGuideline]] = Field(None)
    values: Optional[List[common.ParameterValue]] = Field(None)
    select: Optional[common.ParameterSelection] = None


class Remove(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    by_name: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='by-name',
        description='Identify items to remove by matching their assigned name',
        title='Reference by (assigned) name',
    )
    by_class: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='by-class',
        description='Identify items to remove by matching their class.',
        title='Reference by class',
    )
    by_id: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='by-id',
        description='Identify items to remove indicated by their id.',
        title='Reference by ID',
    )
    by_item_name: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='by-item-name',
        description="Identify items to remove by the name of the item's information element name, e.g. title or prop",
        title='Item Name Reference',
    )
    by_ns: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='by-ns',
        description="Identify items to remove by the item's ns, which is the namespace associated with a part, or prop.",
        title='Item Namespace Reference',
    )


class Position(Enum):
    before = 'before'
    after = 'after'
    starting = 'starting'
    ending = 'ending'


class Order(Enum):
    keep = 'keep'
    ascending = 'ascending'
    descending = 'descending'


class Method(Enum):
    use_first = 'use-first'
    merge = 'merge'
    keep = 'keep'


class Matching(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    pattern: Optional[constr(regex=r'^\S(.*\S)?$')] = Field(
        None,
        description='A glob expression matching the IDs of one or more controls to be selected.',
        title='Pattern',
    )


class IncludeAll(OscalBaseModel):
    pass

    class Config:
        extra = Extra.forbid


class Combine(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    method: Optional[Method] = Field(
        None,
        description='How clashing controls should be handled',
        title='Combination method',
    )


class AsIs(OscalBaseModel):
    __root__: bool = Field(
        ...,
        description=
        'An As-is element indicates that the controls should be structured in resolution as they are structured in their source catalogs. It does not contain any elements or attributes.',
        title='As is',
    )


class Add(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    position: Optional[Position] = Field(
        None,
        description='Where to add the new content with respect to the targeted element (beside it or inside it)',
        title='Position',
    )
    by_id: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='by-id',
        description='Target location of the addition.',
        title='Reference by ID',
    )
    title: Optional[str] = Field(
        None,
        description='A name given to the control, which may be used by a tool for display and navigation.',
        title='Title Change',
    )
    params: Optional[List[common.Parameter]] = Field(None)
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    parts: Optional[List[common.Part]] = Field(None)


class Alter(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    control_id: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='control-id',
        description='A reference to a control with a corresponding id value.',
        title='Control Identifier Reference',
    )
    removes: Optional[List[Remove]] = Field(None)
    adds: Optional[List[Add]] = Field(None)


class Modify(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    set_parameters: Optional[List[SetParameter]] = Field(None, alias='set-parameters')
    alters: Optional[List[Alter]] = Field(None)


class SelectControlById(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    with_child_controls: Optional[WithChildControls] = Field(
        None,
        alias='with-child-controls',
        description='When a control is included, whether its child (dependent) controls are also included.',
        title='Include contained controls with control',
    )
    with_ids: Optional[List[WithId]] = Field(None, alias='with-ids')
    matching: Optional[List[Matching]] = Field(None)


class Import(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    href: str = Field(
        ...,
        description='A resolvable URL reference to the base catalog or profile that this profile is tailoring.',
        title='Catalog or Profile Reference',
    )
    include_all: Optional[IncludeAll] = Field(None, alias='include-all')
    include_controls: Optional[List[SelectControlById]] = Field(None, alias='include-controls')
    exclude_controls: Optional[List[SelectControlById]] = Field(None, alias='exclude-controls')


class InsertControls(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    order: Optional[Order] = Field(
        None,
        description='A designation of how a selection of controls in a profile is to be ordered.',
        title='Order',
    )
    include_all: Optional[IncludeAll] = Field(None, alias='include-all')
    include_controls: Optional[List[SelectControlById]] = Field(None, alias='include-controls')
    exclude_controls: Optional[List[SelectControlById]] = Field(None, alias='exclude-controls')


class Group(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    id: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        description=
        "A unique identifier for a specific group instance that can be used to reference the group within this and in other OSCAL documents. This identifier's uniqueness is document scoped and is intended to be consistent for the same group across minor revisions of the document.",
        title='Group Identifier',
    )
    class_: Optional[constr(
        regex=
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'
    )] = Field(
        None,
        alias='class',
        description='A textual label that provides a sub-type or characterization of the group.',
        title='Group Class',
    )
    title: str = Field(
        ...,
        description='A name given to the group, which may be used by a tool for display and navigation.',
        title='Group Title',
    )
    params: Optional[List[common.Parameter]] = Field(None)
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    parts: Optional[List[common.Part]] = Field(None)
    groups: Optional[List[Group]] = None
    insert_controls: Optional[List[InsertControls]] = Field(None, alias='insert-controls')


class Custom(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    groups: Optional[List[Group]] = Field(None)
    insert_controls: Optional[List[InsertControls]] = Field(None, alias='insert-controls')


class Merge(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    combine: Optional[Combine] = None
    as_is: Optional[AsIs] = Field(None, alias='as-is')
    custom: Optional[Custom] = None


class Profile(OscalBaseModel):

    class Config:
        extra = Extra.forbid

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'
    ) = Field(
        ...,
        description=
        'A globally unique identifier for this profile instance. This UUID should be changed when this document is revised.',
        title='Catalog Universally Unique Identifier',
    )
    metadata: common.Metadata
    imports: List[Import] = Field(...)
    merge: Optional[Merge] = None
    modify: Optional[Modify] = None
    back_matter: Optional[common.BackMatter] = Field(None, alias='back-matter')


class Model(OscalBaseModel):
    profile: Profile


Group.update_forward_refs()
