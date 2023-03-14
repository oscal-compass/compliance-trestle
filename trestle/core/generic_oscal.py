# Copyright (c) 2022 IBM Corp. All rights reserved.
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
"""Generic classes to support both SSP and DefinedComponents."""
from __future__ import annotations

import copy
import logging
from typing import List, Optional
from uuid import uuid4

from pydantic import Field, constr

import trestle.oscal.component as comp
import trestle.oscal.ssp as ossp
from trestle.common import const
from trestle.common.list_utils import as_list, none_if_empty
from trestle.core.control_interface import ControlInterface
from trestle.core.trestle_base_model import TrestleBaseModel
from trestle.oscal import common

logger = logging.getLogger(__name__)

IMPLEMENTED_REQUIREMENTS = 'implemented_requirements'


class GenericByComponent(TrestleBaseModel):
    """Generic ByComponent for SSP and DefinedComponent."""

    # only in SSP
    component_uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'  # noqa FS003
    ) = Field(
        ...,
        alias='component_uuid',
        description='A machine-oriented identifier reference to the component that is implemeting a given control.',
        title='Component Universally Unique Identifier Reference',
    )
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'  # noqa FS003
    ) = Field(
        ...,
        description=  # noqa E251
        'A machine-oriented, globally unique identifier with cross-instance scope that can be used to reference this by-component entry elsewhere in this or other OSCAL instances. The locally defined UUID of the by-component entry can be used to reference the data item locally or globally (e.g., in an imported OSCAL instance). This UUID should be assigned per-subject, which means it should be consistently used to identify the same subject across revisions of the document.',  # noqa E501
        title='By-Component Universally Unique Identifier',
    )
    description: str = Field(
        ...,
        description=  # noqa E251
        'An implementation statement that describes how a control or a control statement is implemented within the referenced system component.',  # noqa E501
        title='Control Implementation Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    set_parameters: Optional[List[GenericSetParameter]] = Field(None, alias='set-parameters')
    implementation_status: Optional[common.ImplementationStatus] = Field(None, alias='implementation-status')
    # removed export, inherited, satisfied
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    remarks: Optional[str] = None

    @staticmethod
    def generate() -> GenericByComponent:
        """Generate instance of generic ByComponent."""
        uuid = str(uuid4())
        return GenericByComponent(component_uuid=const.SAMPLE_UUID_STR, uuid=uuid, description='')

    def as_ssp(self) -> ossp.ByComponent:
        """Convert to ssp format."""
        set_params = []
        for set_param in as_list(self.set_parameters):
            new_set_param = ossp.SetParameter(
                param_id=set_param.param_id, values=set_param.values, remarks=set_param.remarks
            )
            set_params.append(new_set_param)
        set_params = none_if_empty(set_params)
        return ossp.ByComponent(
            component_uuid=self.component_uuid,
            uuid=self.uuid,
            description=self.description,
            props=self.props,
            links=self.links,
            set_parameters=set_params,
            implementation_status=self.implementation_status,
            responsible_roles=self.responsible_roles
        )


class GenericStatement(TrestleBaseModel):
    """Generic statement for SSP and DefinedComp."""

    statement_id: constr(
        regex=  # noqa E251
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'  # noqa FS003 E501
    ) = Field(
        ...,
        alias='statement_id',
        description='A human-oriented identifier reference to a control statement.',
        title='Control Statement Reference',
    )
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'  # noqa FS003 F722
    ) = Field(
        ...,
        description=  # noqa E251
        'A machine-oriented, globally unique identifier with cross-instance scope that can be used to reference this control statement elsewhere in this or other OSCAL instances. The UUID of the control statement in the source OSCAL instance is sufficient to reference the data item locally or globally (e.g., in an imported OSCAL instance).',  # noqa E501
        title='Control Statement Reference Universally Unique Identifier',
    )
    # this is not in ssp statement
    description: str = Field(
        ...,
        description='A summary of how the containing control statement is implemented by the component or capability.',
        title='Statement Implementation Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    remarks: Optional[str] = None
    # ssp has following
    by_components: Optional[List[GenericByComponent]] = Field(None, alias='by-components')

    def as_ssp(self) -> ossp.Statement:
        """Represent in ssp form."""
        class_dict = copy.deepcopy(self.__dict__)
        class_dict.pop('description', None)
        by_comps = []
        for by_comp in as_list(self.by_components):
            new_by_comp = by_comp.as_ssp()
            by_comps.append(new_by_comp)
        return ossp.Statement(
            statement_id=self.statement_id,
            uuid=self.uuid,
            props=self.props,
            links=self.links,
            responsible_roles=self.responsible_roles,
            by_components=by_comps,
            remarks=self.remarks
        )


class GenericComponent(TrestleBaseModel):
    """Generic component for SSP SystemComponent and DefinedComponent."""

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'  # noqa FS003 F722
    ) = Field(
        ...,
        description=  # noqa E251
        'A machine-oriented, globally unique identifier with cross-instance scope that can be used to reference this component elsewhere in this or other OSCAL instances. The locally defined UUID of the component can be used to reference the data item locally or globally (e.g., in an imported OSCAL instance). This UUID should be assigned per-subject, which means it should be consistently used to identify the same subject across revisions of the document.',  # noqa E501
        title='Component Identifier',
    )
    type: constr(regex=r'^\S(.*\S)?$') = Field(  # noqa A003 F722
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
    # ssp does not have a list of ci's but it does have one ci
    control_implementations: Optional[List[GenericControlImplementation]] = Field(None, alias='control-implementations')
    remarks: Optional[str] = None
    # ssp has
    status: common.ImplementationStatus

    def as_defined_component(self) -> comp.DefinedComponent:
        """Convert to DefinedComponent."""
        status = self.status
        class_dict = copy.deepcopy(self.__dict__)
        class_dict.pop('status', None)
        def_comp = comp.DefinedComponent(**class_dict)
        ControlInterface.insert_status_in_props(def_comp, status)
        return def_comp

    @classmethod
    def from_defined_component(cls, def_comp: comp.DefinedComponent) -> GenericComponent:
        """Convert defined component to generic."""
        status = ControlInterface.get_status_from_props(def_comp)
        class_dict = copy.deepcopy(def_comp.__dict__)
        if 'control_implementations' in class_dict:
            new_cis = []
            for ci in class_dict['control_implementations']:
                new_cis.append(GenericControlImplementation.from_component_ci(ci))
            class_dict['control-implementations'] = new_cis
            class_dict.pop('control_implementations', None)
        class_dict['status'] = status
        return cls(**class_dict)

    def as_system_component(self, status_override: str = '') -> ossp.SystemComponent:
        """Convert to SystemComponent."""
        class_dict = copy.deepcopy(self.__dict__)
        class_dict.pop('control_implementations', None)
        status_str = self.status.state if self.status else const.STATUS_OPERATIONAL
        status_str = status_override if status_override else status_str
        if status_str not in ['under-development', 'operational', 'disposition', 'other']:
            logger.warning(
                f'SystemComponent status {status_str} not recognized.  Setting to {const.STATUS_OPERATIONAL}'
            )
            status_str = const.STATUS_OPERATIONAL
        class_dict['status'] = ossp.Status(state=status_str, remarks=self.status.remarks)
        return ossp.SystemComponent(**class_dict)

    @staticmethod
    def generate() -> GenericComponent:
        """Generate instance of GenericComponent."""
        uuid = str(uuid4())
        status = common.ImplementationStatus(state=const.STATUS_OPERATIONAL)
        return GenericComponent(uuid=uuid, type=const.REPLACE_ME, title='', description='', status=status)


class GenericSetParameter(TrestleBaseModel):
    """Generic SetParameter for SSP and DefinedComponent."""

    param_id: constr(
        regex=  # noqa E251
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'  # noqa E501
    ) = Field(
        ...,
        alias='param-id',
        description=  # noqa E251
        "A human-oriented reference to a parameter within a control, who's catalog has been imported into the current implementation context.",  # noqa E501
        title='Parameter ID',
    )
    values: List[str] = Field(...)
    remarks: Optional[str] = None

    @staticmethod
    def from_defined_component(sp: comp.SetParameter):
        """Generate generic set parameter from comp_def version."""
        class_dict = {'param-id': sp.param_id, 'values': sp.values, 'remarks': sp.remarks}
        return GenericSetParameter(**class_dict)

    def to_ssp(self):
        """Convert to ssp format."""
        return (ossp.SetParameter(param_id=self.param_id, values=self.values, remarks=self.remarks))


class GenericImplementedRequirement(TrestleBaseModel):
    """Generic ImplementedRequirement for SSP and DefinedComponent."""

    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'  # noqa FS003 F722
    ) = Field(
        ...,
        description=  # noqa E251
        'A machine-oriented, globally unique identifier with cross-instance scope that can be used to reference a specific control implementation elsewhere in this or other OSCAL instances. The locally defined UUID of the control implementation can be used to reference the data item locally or globally (e.g., in an imported OSCAL instance).This UUID should be assigned per-subject, which means it should be consistently used to identify the same subject across revisions of the document.',  # noqa E501
        title='Control Implementation Identifier',
    )
    control_id: constr(
        regex=  # noqa E251
        r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'  # noqa E501
    ) = Field(
        ...,
        alias='control-id',
        description=  # noqa E251
        'A human-oriented identifier reference to a control with a corresponding id value. When referencing an externally defined control, the Control Identifier Reference must be used in the context of the external / imported OSCAL instance (e.g., uri-reference).',  # noqa E501
        title='Control Identifier Reference',
    )
    # only compdef has description
    description: str = Field(
        ...,
        description=  # noqa E251
        'A description of how the specified control is implemented for the containing component or capability.',  # noqa E501
        title='Control Implementation Description',
    )
    props: Optional[List[common.Property]] = Field(None)
    links: Optional[List[common.Link]] = Field(None)
    set_parameters: Optional[List[GenericSetParameter]] = Field(None, alias='set-parameters')
    responsible_roles: Optional[List[common.ResponsibleRole]] = Field(None, alias='responsible-roles')
    statements: Optional[List[GenericStatement]] = Field(None)
    remarks: Optional[str] = None
    # ssp has following
    by_components: Optional[List[GenericByComponent]] = Field(None, alias='by-components')

    @staticmethod
    def generate() -> GenericImplementedRequirement:
        """Generate instance of this class."""
        uuid = str(uuid4())
        class_dict = {'uuid': uuid, 'control-id': const.REPLACE_ME, 'description': ''}
        return GenericImplementedRequirement(**class_dict)

    @classmethod
    def from_comp_def(cls, imp_req: comp.ImplementedRequirement) -> GenericImplementedRequirement:
        """Convert component form of imp req to generic."""
        class_dict = copy.deepcopy(imp_req.__dict__)
        class_dict['control-id'] = class_dict.pop('control_id', None)
        return cls(**class_dict)

    def as_ssp(self) -> ossp.ImplementedRequirement:
        """Convert to ssp form."""
        class_dict = copy.deepcopy(self.__dict__)
        del class_dict['description']
        new_stat_list = []
        for statement in as_list(self.statements):
            new_stat_list.append(statement.as_ssp())
        if new_stat_list:
            class_dict['statements'] = new_stat_list
        return ossp.ImplementedRequirement(**class_dict)


class GenericControlImplementation(TrestleBaseModel):
    """Generic control implementation for SSP and CompDef."""

    # not in ssp
    uuid: constr(
        regex=r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$'  # noqa FS003 F722
    ) = Field(
        ...,
        description=  # noqa E251
        'A machine-oriented, globally unique identifier with cross-instance scope that can be used to reference a set of implemented controls elsewhere in this or other OSCAL instances. The locally defined UUID of the control implementation set can be used to reference the data item locally or globally (e.g., in an imported OSCAL instance). This UUID should be assigned per-subject, which means it should be consistently used to identify the same subject across revisions of the document.',  # noqa E501
        title='Control Implementation Set Identifier',
    )
    # not in ssp
    source: str = Field(
        ...,
        description=  # noqa E251
        'A reference to an OSCAL catalog or profile providing the referenced control or subcontrol definition.',  # noqa E501
        title='Source Resource Reference',
    )
    description: str = Field(
        ...,
        description=  # noqa E251
        'A description of how the specified set of controls are implemented for the containing component or capability.',  # noqa E501
        title='Control Implementation Description',
    )
    # not in ssp
    props: Optional[List[common.Property]] = Field(None)
    # not in ssp
    links: Optional[List[common.Link]] = Field(None)
    set_parameters: Optional[List[GenericSetParameter]] = Field(None, alias='set-parameters')
    implemented_requirements: List[GenericImplementedRequirement] = Field(..., alias='implemented-requirements')

    @staticmethod
    def generate() -> GenericControlImplementation:
        """Generate instance of this class."""
        uuid = str(uuid4())
        imp_reqs = [GenericImplementedRequirement.generate()]
        class_dict = {
            'uuid': uuid,
            'control-id': const.REPLACE_ME,
            'source': const.REPLACE_ME,
            'description': '',
            'implemented-requirements': imp_reqs
        }
        return GenericControlImplementation(**class_dict)

    @classmethod
    def from_component_ci(cls, control_imp: comp.ControlImplementation) -> GenericControlImplementation:
        """Convert component control imp to generic."""
        class_dict = copy.deepcopy(control_imp.__dict__)
        if IMPLEMENTED_REQUIREMENTS in class_dict:
            new_irs = []
            ir_list = class_dict.get(IMPLEMENTED_REQUIREMENTS, None)
            for ir in as_list(ir_list):
                new_ir = GenericImplementedRequirement.from_comp_def(ir)
                new_irs.append(new_ir)
            class_dict['implemented-requirements'] = none_if_empty(new_irs)
            class_dict.pop(IMPLEMENTED_REQUIREMENTS, None)
            new_sps = []
            sp_list = class_dict.get('set_parameters', None)
            for sp in as_list(sp_list):
                new_sps.append(GenericSetParameter.from_defined_component(sp))
            class_dict['set-parameters'] = none_if_empty(new_sps)
            class_dict.pop('set_parameters', None)

        return cls(**class_dict)

    def as_ssp(self) -> ossp.ControlImplementation:
        """Represent in ssp form."""
        imp_reqs = []
        for imp_req in self.implemented_requirements:
            imp_reqs.append(imp_req.as_ssp())
        class_dict = self.__dict__
        for prop in ['uuid', 'source', 'props', 'links', IMPLEMENTED_REQUIREMENTS]:
            class_dict.pop(prop, None)
        if imp_reqs:
            class_dict['implemented-requirements'] = imp_reqs
            class_dict.pop(IMPLEMENTED_REQUIREMENTS, None)
        return ossp.ControlImplementation(**class_dict)


GenericComponent.update_forward_refs()
