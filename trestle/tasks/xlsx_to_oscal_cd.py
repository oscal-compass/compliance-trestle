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
from typing import Dict, List, Optional

from trestle.oscal import OSCAL_VERSION
from trestle.oscal.common import Metadata
from trestle.oscal.common import Party
from trestle.oscal.common import Property
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

key_sep = sep = '|'


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
            logger.warning(f'output: {ofile} already exists')
            return TaskOutcome('failure')
        # initialize
        self.defined_components = {}
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
            components=list(self.defined_components.values()),
        )
        # write OSCAL ComponentDefinition to file
        if self._verbose:
            logger.info(f'output: {ofile}')
        component_definition.oscal_write(pathlib.Path(ofile))
        # issues
        self._report_issues()
        return TaskOutcome('success')

    def _process_rows(self, responsible_roles: List[ResponsibleRole]) -> None:
        """Process spread sheet rows."""
        ci_map = {}
        for row in self.xlsx_helper.row_generator():
            # quit when first row with no goal_id encountered
            goal_name_id = self.xlsx_helper.get_goal_name_id(row)
            controls = self.xlsx_helper.get_controls(row)
            if len(controls.keys()) == 0:
                continue
            # component
            component_name = self.xlsx_helper.get_component_name(row)
            component_type = 'Service'
            defined_component = self._get_defined_component(component_name, component_type)
            # parameter
            parameter_name, parameter_description = self.xlsx_helper.get_parameter_name_and_description(row)
            # control implementations
            source = self._get_catalog_url()
            description = component_name + ' implemented controls for ' + self._get_catalog_title(
            ) + '. It includes assessment asset configuration for CICD.'
            key = source + key_sep + description
            control_implementation = ci_map.get(key)
            if not control_implementation:
                ci_map[key] = ControlImplementation(
                    uuid=str(uuid.uuid4()),
                    source=source,
                    description=description,
                    implemented_requirements=[],
                )
                control_implementation = ci_map[key]
                if defined_component.control_implementations is None:
                    defined_component.control_implementations = []
                defined_component.control_implementations.append(control_implementation)
            # implemented requirements
            self._add_implemented_requirements(
                row, control_implementation, controls, component_name, parameter_name, responsible_roles, goal_name_id
            )
            # keep alternative parameter values at control implementation level
            parameter_values = self.xlsx_helper.get_parameter_values(row)
            self._add_set_parameter_values(parameter_name, parameter_values, control_implementation)

    def _add_implemented_requirements(
        self,
        row: int,
        control_implementation: ControlImplementation,
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
                remarks=str(goal_remarks)
            )
            prop2 = Property(
                name='goal_version',
                class_=self._get_class_for_property_name('goal_version'),
                value=self._get_goal_version(),
                ns=self._get_namespace(),
                remarks=str(goal_name_id)
            )
            props = [prop1, prop2]
            control_id, _ = self.catalog_interface.get_control_id_and_status(control)
            if not control_id:
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
            self._add_set_parameter_default(parameter_name, parameter_value_default, implemented_requirement)
            # implemented_requirements
            control_implementation.implemented_requirements.append(implemented_requirement)

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

    def _add_set_parameter_values(
        self, parameter_name: str, parameter_values: str, control_implementation: ControlImplementation
    ) -> None:
        """Add set parameter values (the set of choices)."""
        if parameter_name is not None:
            parameter_name = parameter_name.replace(' ', '_')
            if parameter_values is not None:
                set_parameters = [SetParameter(param_id=parameter_name, values=parameter_values)]
                if control_implementation.set_parameters is None:
                    control_implementation.set_parameters = []
                # set_parameters is a list
                control_implementation.set_parameters.extend(set_parameters)

    def _add_set_parameter_default(
        self, parameter_name: str, parameter_value_default: str, implemented_requirement: ImplementedRequirement
    ) -> None:
        """Add set parameter default (the "recommended" value)."""
        if parameter_name is not None:
            parameter_name = parameter_name.replace(' ', '_')
            if parameter_value_default is not None:
                if implemented_requirement.set_parameters is None:
                    implemented_requirement.set_parameters = []
                values = [parameter_value_default]
                set_parameter = SetParameter(param_id=parameter_name, values=values)
                set_parameters = [set_parameter]
                # set_parameters is a list
                implemented_requirement.set_parameters.extend(set_parameters)

    def _get_defined_component(self, component_name: str, component_type: str) -> DefinedComponent:
        """Get defined component."""
        key = component_name + key_sep + component_type
        defined_component = self.defined_components.get(key)
        if not defined_component:
            # create new component
            component_title = component_name
            component_description = component_name
            defined_component = DefinedComponent(
                uuid=str(uuid.uuid4()),
                description=component_description,
                title=component_title,
                type=component_type,
            )
            self.defined_components[key] = defined_component
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
