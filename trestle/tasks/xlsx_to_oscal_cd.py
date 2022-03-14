# -*- mode:python; coding:utf-8 -*-
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
"""OSCAL transformation tasks."""

import configparser
import datetime
import logging
import pathlib
import traceback
import uuid
from typing import Any, Dict, List, Optional

from trestle.oscal import OSCAL_VERSION
from trestle.oscal.catalog import Catalog
from trestle.oscal.common import Link
from trestle.oscal.common import Metadata
from trestle.oscal.common import Parameter
from trestle.oscal.common import ParameterGuideline
from trestle.oscal.common import ParameterValue
from trestle.oscal.common import Party
from trestle.oscal.common import Property
from trestle.oscal.common import Remarks
from trestle.oscal.common import ResponsibleParty
from trestle.oscal.common import ResponsibleRole
from trestle.oscal.common import Role
from trestle.oscal.component import ComponentDefinition
from trestle.oscal.component import ControlImplementation
from trestle.oscal.component import DefinedComponent
from trestle.oscal.component import ImplementedRequirement
from trestle.oscal.component import SetParameter
from trestle.oscal.component import Statement
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome
from trestle.tasks.xlsx_helper import XlsxHelper
from trestle.tasks.xlsx_helper import get_trestle_version

logger = logging.getLogger(__name__)


class XlsxToOscalComponentDefinition(TaskBase):
    """
    Task to create OSCAL ComponentDefinition json.

    Attributes:
        name: Name of the task.
    """

    name = 'xlsx-to-oscal-cd'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task xlsx-to-oscal-cd.

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)
        self.xlsx_helper = XlsxHelper()
        self._timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc
                                                                                    ).isoformat()

    def set_timestamp(self, timestamp: str) -> None:
        """Set the timestamp."""
        self._timestamp = timestamp

    def print_info(self) -> None:
        """Print the help string."""
        self.xlsx_helper.print_info(self.name, 'component_definition')

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        return TaskOutcome('simulated-success')

    def execute(self) -> TaskOutcome:
        """Provide an executed outcome."""
        try:
            return self._execute()
        except Exception:
            logger.info(traceback.format_exc())
            return TaskOutcome('failure')

    def _execute(self) -> TaskOutcome:
        """Execute path core."""
        if not self.xlsx_helper.configure(self):
            return TaskOutcome('failure')
        # config output
        odir = self._config.get('output-dir')
        opth = pathlib.Path(odir)
        self._overwrite = self._config.getboolean('output-overwrite', True)
        # insure output dir exists
        opth.mkdir(exist_ok=True, parents=True)
        # calculate output file name & check writability
        oname = 'component-definition.json'
        ofile = opth / oname
        if not self._overwrite and pathlib.Path(ofile).exists():
            logger.error(f'output: {ofile} already exists')
            return TaskOutcome('failure')
        # initialize
        self.component_names = []
        self.defined_components = []
        self.parameters = {}
        self.parameter_helper = None
        # roles, responsible_roles, parties, responsible parties
        party_uuid_01 = str(uuid.uuid4())
        party_uuid_02 = str(uuid.uuid4())
        party_uuid_03 = str(uuid.uuid4())
        roles = self._build_roles()
        responsible_roles = self._build_responsible_roles(party_uuid_01, party_uuid_02, party_uuid_03)
        parties = self._build_parties(party_uuid_01, party_uuid_02, party_uuid_03)
        responsible_parties = self._build_responsible_parties(party_uuid_01, party_uuid_02, party_uuid_03)
        # process each row of spread sheet
        self._process_rows(responsible_roles)
        # create OSCAL ComponentDefinition
        metadata = Metadata(
            title='Component definition for ' + self._get_catalog_title() + ' profiles',
            last_modified=self._timestamp,
            oscal_version=OSCAL_VERSION,
            version=get_trestle_version(),
            roles=roles,
            parties=parties,
            responsible_parties=responsible_parties
        )
        component_definition = ComponentDefinition(
            uuid=str(uuid.uuid4()),
            metadata=metadata,
            components=self.defined_components,
        )
        # write OSCAL ComponentDefinition to file
        if self._verbose:
            logger.info(f'output: {ofile}')
        component_definition.oscal_write(pathlib.Path(ofile))
        # issues
        self._report_issues()
        # <hack>
        # create a catalog containing the parameters,
        # since parameters are not supported in OSCAL 1.0.0 component definition
        self._write_catalog()
        # </hack>
        return TaskOutcome('success')

    def _process_rows(self, responsible_roles: List[ResponsibleRole]) -> None:
        """Process spread sheet rows."""
        for row in self.xlsx_helper.row_generator():
            # quit when first row with no goal_id encountered
            goal_name_id = self.xlsx_helper.get_goal_name_id(row)
            controls = self.xlsx_helper.get_controls(row)
            if len(controls.keys()) == 0:
                continue
            # component
            component_name = self.xlsx_helper.get_component_name(row)
            defined_component = self._get_defined_component(component_name)
            # parameter
            parameter_name, parameter_description = self.xlsx_helper.get_parameter_name_and_description(row)
            self._add_parameter(row, component_name, parameter_name, parameter_description)
            # implemented requirements
            self.implemented_requirements = []
            self._add_implemented_requirements(
                row, controls, component_name, parameter_name, responsible_roles, goal_name_id
            )
            # control implementations
            control_implementation = ControlImplementation(
                uuid=str(uuid.uuid4()),
                source=self._get_catalog_url(),
                description=component_name + ' implemented controls for ' + self._get_catalog_title()
                + '. It includes assessment asset configuration for CICD."',
                implemented_requirements=self.implemented_requirements,
            )
            if defined_component.control_implementations is None:
                defined_component.control_implementations = [control_implementation]
            else:
                defined_component.control_implementations.append(control_implementation)

    def _add_implemented_requirements(
        self,
        row: int,
        controls: Dict[str, List[str]],
        component_name: str,
        parameter_name: str,
        responsible_roles: List[ResponsibleRole],
        goal_name_id: str
    ) -> None:
        """Add implemented requirements."""
        goal_remarks = self.xlsx_helper.get_goal_remarks(row)
        parameter_value_default = self.xlsx_helper.get_parameter_value_default(row)
        for control in controls.keys():
            control_uuid = str(uuid.uuid4())
            prop1 = Property(
                name='goal_name_id',
                class_=self._get_class_for_property_name('goal_name_id'),
                value=goal_name_id,
                ns=self._get_namespace(),
                remarks=Remarks(__root__=str(goal_remarks))
            )
            prop2 = Property(
                name='goal_version',
                class_=self._get_class_for_property_name('goal_version'),
                value=self._get_goal_version(),
                ns=self._get_namespace(),
                remarks=Remarks(__root__=str(goal_name_id))
            )
            props = [prop1, prop2]
            control_id, status = self.catalog_helper.find_control_id(control)
            if control_id is None:
                logger.info(f'row {row} control {control} not found in catalog')
                control_id = control
            # implemented_requirement
            implemented_requirement = ImplementedRequirement(
                uuid=control_uuid,
                description=control,
                props=props,
                control_id=control_id,
                responsible_roles=responsible_roles,
            )
            # add statements
            self._add_statements(row, control, controls, component_name, implemented_requirement)
            # add set_parameter
            self._add_set_parameter(row, parameter_name, parameter_value_default, implemented_requirement)
            # implemented_requirements
            self.implemented_requirements.append(implemented_requirement)

    def _add_parameter(self, row: int, component_name: str, parameter_name: str, parameter_description: str) -> None:
        """Add_parameter."""
        usage = self.xlsx_helper.get_parameter_usage(row)
        if parameter_name is not None:
            parameter_name = parameter_name.strip()
            values = self.xlsx_helper.get_parameter_values(row)
            guidelines = self._get_guidelines(values)
            href = self._get_namespace() + '/' + component_name.replace(' ', '%20')
            self.parameter_helper = ParameterHelper(
                values=values,
                id_=parameter_name,
                label=parameter_description,
                href=href,
                usage=usage,
                guidelines=guidelines,
            )
            self.parameters[str(uuid.uuid4())] = self.parameter_helper.get_parameter()

    def _add_statements(
        self,
        row: int,
        control: str,
        controls: Dict[str, List[str]],
        component_name: str,
        implemented_requirement: ImplementedRequirement
    ) -> None:
        """Add statements."""
        control_statements = controls[control]
        if control_statements:
            statements = []
            for control_statement in control_statements:
                statement_id = control + control_statement
                if any(i in control for i in '()'):
                    control = control.replace('(', '_')
                    control = control.replace(')', '')
                    logger.info(f'row {row} control {control} edited to remove parentheses')
                statement = Statement(
                    statement_id=control,
                    uuid=str(uuid.uuid4()),
                    description=f'{component_name} implements {statement_id}'
                )
                statements.append(statement)
            implemented_requirement.statements = statements

    def _add_set_parameter(
        self,
        row: int,
        parameter_name: str,
        parameter_value_default: str,
        implemented_requirement: ImplementedRequirement
    ) -> None:
        """Add set parameter."""
        if parameter_name is not None:
            parameter_name = parameter_name.replace(' ', '_')
            if parameter_value_default is not None:
                values = [parameter_value_default]
                set_parameter = SetParameter(param_id=parameter_name, values=values)
                set_parameters = [set_parameter]
                implemented_requirement.set_parameters = set_parameters

    def _get_defined_component(self, component_name: str) -> DefinedComponent:
        """Get defined component."""
        if component_name not in self.component_names:
            # create new component
            self.component_names.append(component_name)
            component_title = component_name
            component_description = component_name
            defined_component = DefinedComponent(
                uuid=str(uuid.uuid4()),
                description=component_description,
                title=component_title,
                type='Service',
            )
            self.defined_components.append(defined_component)
        else:
            # find existing component
            for defined_component in self.defined_components:
                if component_name == defined_component.title:
                    break
        return defined_component

    def _build_roles(self) -> List[Role]:
        """Build roles."""
        value = [
            Role(id='prepared-by', title='Indicates the organization that created this content.'),
            Role(id='prepared-for', title='Indicates the organization for which this content was created..'),
            Role(
                id='content-approver',
                title='Indicates the organization responsible for all content represented in the "document".'
            ),
        ]
        return value

    def _build_responsible_roles(self, party_uuid_01: str, party_uuid_02: str,
                                 party_uuid_03: str) -> List[ResponsibleRole]:
        """Build responsible roles."""
        role_prepared_by = ResponsibleRole(role_id='prepared-by', party_uuids=[party_uuid_01])
        role_prepared_for = ResponsibleRole(role_id='prepared-for', party_uuids=[party_uuid_02, party_uuid_03])
        role_content_approver = ResponsibleRole(role_id='content-approver', party_uuids=[party_uuid_01])
        value = [
            role_prepared_by,
            role_prepared_for,
            role_content_approver,
        ]
        return value

    def _build_parties(self, party_uuid_01: str, party_uuid_02: str, party_uuid_03: str) -> List[Party]:
        """Build parties."""
        value = [
            Party(uuid=party_uuid_01, type='organization', name=self._get_org_name(), remarks=self._get_org_remarks()),
            Party(
                uuid=party_uuid_02,
                type='organization',
                name='Customer',
                remarks='organization to be customized at account creation only for their Component Definition'
            ),
            Party(
                uuid=party_uuid_03,
                type='organization',
                name='ISV',
                remarks='organization to be customized at ISV subscription only for their Component Definition'
            ),
        ]
        return value

    def _build_responsible_parties(self, party_uuid_01: str, party_uuid_02: str,
                                   party_uuid_03: str) -> List[ResponsibleParty]:
        """Build responsible parties."""
        prepared_by = ResponsibleParty(role_id='prepared-by', party_uuids=[party_uuid_01])
        prepared_for = ResponsibleParty(role_id='prepared-for', party_uuids=[party_uuid_02, party_uuid_03])
        content_approver = ResponsibleParty(role_id='content-approver', party_uuids=[party_uuid_01])
        value = [
            prepared_by,
            prepared_for,
            content_approver,
        ]
        return value

    def _report_issues(self) -> None:
        """Report issues."""
        self.xlsx_helper.report_issues()

    def _write_catalog(self) -> None:
        """Create a catalog containing the parameters."""
        if self.parameter_helper is not None:
            tdir = self._config.get('output-dir')
            tdir = tdir.replace('component-definitions', 'catalogs')
            tpth = pathlib.Path(tdir)
            # insure output dir exists
            tpth.mkdir(exist_ok=True, parents=True)
            tname = 'catalog.json'
            tfile = tpth / tname
            self.parameter_helper.write_parameters_catalog(
                parameters=self.parameters,
                timestamp=self._timestamp,
                oscal_version=OSCAL_VERSION,
                version=get_trestle_version(),
                ofile=tfile,
                verbose=self._verbose,
            )

    def _get_org_name(self) -> str:
        """Get org-name from config."""
        value = self._config.get('org-name')
        logger.debug(f'org-name: {value}')
        return value

    def _get_org_remarks(self) -> str:
        """Get org-remarks from config."""
        value = self._config.get('org-remarks')
        logger.debug(f'org-remarks: {value}')
        return value

    def _get_class_for_property_name(self, property_name: str) -> str:
        """Get class for property-name from config."""
        value = None
        data = self._config.get('property-name-to-class')
        if data is not None:
            for item in data.split(','):
                item = item.strip()
                parts = item.split(':')
                if len(parts) != 2 or parts[0] != property_name:
                    continue
                value = parts[1]
                break
        logger.debug(f'property-name-to-class: {property_name} -> {value}')
        return value

    def _get_namespace(self) -> str:
        """Get namespace from config."""
        value = self._config.get('namespace')
        logger.debug(f'namespace: {value}')
        return value

    def _get_catalog_url(self) -> str:
        """Get catalog url from config."""
        value = self._config.get('catalog-url')
        logger.debug(f'catalog-url: {value}')
        return value

    def _get_catalog_title(self) -> str:
        """Get catalog title from config."""
        value = self._config.get('catalog-title')
        logger.debug(f'catalog-title: {value}')
        return value

    def _get_goal_version(self) -> str:
        """Fix goal_version at 1.0."""
        return '1.0'

    def _get_guidelines(self, values: str) -> str:
        """Get guidelines based on values."""
        type_ = self._get_type(values)
        value = 'The first listed value option is set by default in the system '
        value += 'unless set-parameter is used to satisfy a control requirements. '
        value += f'Type {type_}.'
        return value

    def _get_type(self, values: str) -> str:
        """Get type based on values."""
        if self._is_int(values):
            value = 'Integer'
        elif self._is_float(values):
            value = 'Float'
        else:
            value = 'String'
        return value

    def _is_int(self, values: str) -> bool:
        """Determine if string represents list of int."""
        try:
            for value in values.split(','):
                int(value)
            retval = True
        except Exception:
            retval = False
        return retval

    def _is_float(self, values: str) -> bool:
        """Determine if string represents list of float."""
        try:
            for value in values.split(','):
                float(value)
            retval = True
        except Exception:
            retval = False
        return retval


class ParameterHelper():
    """Parameter Helper class is a temporary hack because Component Definition does not support Parameters."""

    def __init__(self, values: Any, id_: str, label: str, href: str, usage: str, guidelines: str) -> None:
        """Initialize."""
        self._parameter_values = ParameterValue(__root__=str(values))
        self._id = id_
        self._label = label
        self._links = [Link(href=href)]
        self._usage = usage
        self._guidelines = ParameterGuideline(prose=guidelines)

    def get_parameter(self) -> Parameter:
        """Get parameter."""
        parameter = Parameter(
            id=self._id,
            label=self._label,
            links=self._links,
            usage=self._usage,
            guidelines=[self._guidelines],
            values=[self._parameter_values]
        )
        return parameter

    def write_parameters_catalog(
        self,
        parameters: Dict[str, Parameter],
        timestamp: str,
        oscal_version: str,
        version: str,
        ofile: str,
        verbose: bool,
    ) -> None:
        """Write parameters catalog."""
        parameter_metadata = Metadata(
            title='Component Parameters',
            last_modified=timestamp,
            oscal_version=oscal_version,
            version=version,
        )
        parameter_catalog = Catalog(
            uuid=str(uuid.uuid4()),
            metadata=parameter_metadata,
            params=list(parameters.values()),
        )
        if verbose:
            logger.info(f'output: {ofile}')
        parameter_catalog.oscal_write(pathlib.Path(ofile))
