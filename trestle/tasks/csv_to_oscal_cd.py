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
from math import log10
from typing import List, Optional

from trestle.oscal import OSCAL_VERSION
from trestle.oscal.common import Metadata
from trestle.oscal.common import Property
from trestle.oscal.component import ComponentDefinition
from trestle.oscal.component import ControlImplementation
from trestle.oscal.component import DefinedComponent
from trestle.oscal.component import ImplementedRequirement
from trestle.oscal.component import SetParameter
from trestle.oscal.component import Statement
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome
from trestle.tasks.csv_helper import CsvHelper

logger = logging.getLogger(__name__)


def derive_control_id(control_mapping: str) -> str:
    """Derive control id."""
    rval = control_mapping.split('_smt')[0]
    return rval


def derive_part_id(control_mapping: str) -> str:
    """Derive part id."""
    if '_smt.' in control_mapping:
        rval = control_mapping
    else:
        rval = None
    return rval


class CsvToOscalComponentDefinition(TaskBase):
    """
    Task to create OSCAL ComponentDefinition json.

    Attributes:
        name: Name of the task.
    """

    name = 'csv-to-oscal-cd'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task csv-to-oscal-cd.

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)
        self.csv_helper = CsvHelper()
        self._timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc
                                                                                    ).isoformat()
        self._verbose = False

    def print_info(self) -> None:
        """Print the help string."""
        self.csv_helper.print_info(self.name, 'component_definition')

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        return TaskOutcome('simulated-success')

    def execute(self) -> TaskOutcome:
        """Provide an executed outcome."""
        try:
            return self._execute()
        except Exception:
            logger.error(traceback.format_exc())
            return TaskOutcome('failure')

    def _execute(self) -> TaskOutcome:
        """Execute path core."""
        if not self.csv_helper.configure(self):
            return TaskOutcome('failure')
        # verbosity
        quiet = self._config.get('quiet', False)
        verbose = not quiet
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
        # namespace
        self._ns = self._config.get('namespace')
        # user-namespace
        self._ns_user = self._config.get('user-namespace')
        # process rows
        self._process_rows()
        # create OSCAL ComponentDefinition
        metadata = Metadata(
            title=self.csv_helper.get_title(),
            last_modified=self._timestamp,
            oscal_version=OSCAL_VERSION,
            version=self.csv_helper.get_version(),
        )
        component_definition = ComponentDefinition(
            uuid=str(uuid.uuid4()),
            metadata=metadata,
            components=self._get_components(),
        )
        # write OSCAL ComponentDefinition to file
        if verbose:
            logger.info(f'output: {ofile}')
        component_definition.oscal_write(pathlib.Path(ofile))
        # issues
        self._report_issues()
        return TaskOutcome('success')

    def _get_component_key(self, row: List[str]) -> str:
        """Get component key."""
        resource = self.csv_helper.get_value(row, 'Resource')
        component_type = self.csv_helper.get_value(row, 'Component_Type')
        return f'{resource}:{component_type}'

    def _get_component(self, row: List[str]) -> None:
        """Get component."""
        key = self._get_component_key(row)
        rval = self._components.get(key)
        if rval is None:
            resource = self.csv_helper.get_value(row, 'Resource')
            type_ = self.csv_helper.get_value(row, 'Component_Type')
            description = ''
            rval = DefinedComponent(
                uuid=str(uuid.uuid4()),
                type=type_,
                title=resource,
                description=description,
                control_implementations=[],
            )
            self._components[key] = rval
            logger.debug(f'created component: {key}')
        return rval

    def _get_control_implementation_key(self, row: List[str]) -> str:
        """Get control implementation key."""
        resource = self.csv_helper.get_value(row, 'Resource')
        component_type = self.csv_helper.get_value(row, 'Component_Type')
        profile_description = self.csv_helper.get_value(row, 'Profile_Description')
        return f'{resource}:{component_type}:{profile_description}'

    def _get_control_implementation(self, row: List[str]) -> None:
        """Get control implementation."""
        key = self._get_control_implementation_key(row)
        rval = self._control_implementations.get(key)
        if rval is None:
            source = self.csv_helper.get_value(row, 'Profile_Reference_URL')
            description = self.csv_helper.get_value(row, 'Profile_Description')
            rval = ControlImplementation(
                uuid=str(uuid.uuid4()),
                source=source,
                description=description,
                implemented_requirements=[],
            )
            self._control_implementations[key] = rval
            component = self._get_component(row)
            component.control_implementations.append(rval)
            logger.debug(f'created control implementation: {key}')
        return rval

    def _create_rule_prop(
        self,
        row_num: int,
        control_implementation: ControlImplementation,
        row: List[str],
        col: str,
        ns: str,
        remarks: str
    ) -> None:
        """Create rule property."""
        value = self.csv_helper.get_value(row, col)
        logger.debug(f'row_num: {row_num} col: {col} value: {value}')
        if value is None or value == '':
            return
        else:
            class_ = self.csv_helper.get_class(col)
            prop = Property(
                name=col,
                value=value,
                ns=ns,
                class_=class_,
                remarks=remarks,
            )
            control_implementation.props.append(prop)

    def _get_rule_definition_key(self, row: List[str]) -> str:
        """Get rule definition key."""
        resource = self.csv_helper.get_value(row, 'Resource')
        component_type = self.csv_helper.get_value(row, 'Component_Type')
        rule_id = self.csv_helper.get_value(row, 'Rule_Id')
        return f'{resource}:{component_type}:{rule_id}'

    def _register_rule_set(self, row_num: int, key: str, props: List[Property]):
        """Register rule set."""
        self._rule_definitions[key] = props
        logger.debug(f'{row_num} {key} {props}')

    def _add_parameter(self, row_num: int, row: List[str], control_implementation, ns, remarks) -> None:
        # Parameter, if any
        value = self.csv_helper.get_value(row, 'Parameter_Id')
        if value:
            self._create_rule_prop(row_num, control_implementation, row, 'Parameter_Id', ns, remarks)
            self._create_rule_prop(row_num, control_implementation, row, 'Parameter_Description', ns, remarks)
            self._create_rule_prop(row_num, control_implementation, row, 'Parameter_Value_Alternatives', ns, remarks)
            name = self.csv_helper.get_value(row, 'Parameter_Id')
            value = self.csv_helper.get_value(row, 'Parameter_Default_Value')
            if value == '':
                col = 'Parameter_Default_Value'
                text = f'row: {row} missing expected value for col: {col}'
                raise RuntimeError(text)
            values = value.split(',')
            set_parameter = SetParameter(
                param_id=name,
                values=values,
            )
            if control_implementation.set_parameters is None:
                control_implementation.set_parameters = []
            control_implementation.set_parameters.append(set_parameter)

    def _add_rule_definition(self, row_num: int, row: List[str]) -> None:
        """Add rule definition."""
        # Create rule definition (as properties)
        key = self._get_rule_definition_key(row)
        rule_definition = self._rule_definitions.get(key)
        if rule_definition is None:
            control_implementation = self._get_control_implementation(row)
            ns = self._ns
            ns_user = self._ns_user
            fill_sz = int(log10(self.csv_helper.row_count())) + 1
            remarks = f'rule_set_{str(row_num).zfill(fill_sz)}'
            if control_implementation.props is None:
                control_implementation.props = []
            for column_name in self.csv_helper.get_filtered_required_column_names():
                self._create_rule_prop(row_num, control_implementation, row, column_name, ns, remarks)
            for column_name in self.csv_helper.get_filtered_optional_column_names():
                self._create_rule_prop(row_num, control_implementation, row, column_name, ns, remarks)
            # Parameter, if any
            self._add_parameter(row_num, row, control_implementation, ns, remarks)
            # user props
            for col_name in self.csv_helper.get_user_column_names():
                value = self.csv_helper.get_value(row, col_name)
                if not value:
                    continue
                self._create_rule_prop(row_num, control_implementation, row, col_name, ns_user, remarks)
            # Rule set created
            self._register_rule_set(row_num, key, control_implementation.props)
        else:
            text = f'row: {row_num} rule definition: "{key}" already exists?'
            raise RuntimeError(text)

    def _get_implemented_requirement_key(self, control_id: str, row: List[str]) -> str:
        """Get implemented requirement key."""
        resource = self.csv_helper.get_value(row, 'Resource')
        component_type = self.csv_helper.get_value(row, 'Component_Type')
        return f'{resource}:{component_type}:{control_id}'

    def _get_implemented_requirement(self, control_id: str, row: List[str]) -> None:
        """Get implemented requirement."""
        key = self._get_implemented_requirement_key(control_id, row)
        rval = self._implemented_requirements.get(key)
        if rval is None:
            rval = ImplementedRequirement(
                uuid=str(uuid.uuid4()),
                control_id=control_id,
                description='',
            )
            self._implemented_requirements[key] = rval
            control_implementation = self._get_control_implementation(row)
            control_implementation.implemented_requirements.append(rval)
            logger.debug(f'created implemented requirement: {key}')
        return rval

    def _get_statement(self, implemented_requirement: ImplementedRequirement, part_id: str) -> Statement:
        """Get statement."""
        rval = None
        if implemented_requirement.statements is None:
            implemented_requirement.statements = []
        for statement in implemented_requirement.statements:
            if statement.statement_id == part_id:
                rval = statement
                break
        if rval is None:
            statement = Statement(statement_id=part_id, uuid=str(uuid.uuid4()), description='', props=[])
            implemented_requirement.statements.append(statement)
        return statement

    def _add_rule_implementation(self, control_mapping: str, row: List[str]) -> None:
        """Add rule implementation."""
        # Create rule implementation (as property)
        name = 'Rule_Id'
        prop = Property(
            name=name,
            value=self.csv_helper.get_value(row, name),
            ns=self._ns,
            class_=self.csv_helper.get_class(name),
        )
        # Find or create implementation requirement
        control_id = derive_control_id(control_mapping)
        implemented_requirement = self._get_implemented_requirement(control_id, row)
        part_id = derive_part_id(control_mapping)
        # Add rule to implementation requirement as property or statement
        if part_id is None:
            if implemented_requirement.props is None:
                implemented_requirement.props = []
            implemented_requirement.props.append(prop)
        else:
            statement = self._get_statement(implemented_requirement, part_id)
            statement.props.append(prop)

    def _validate_columns(self, row) -> None:
        """Validate columns."""
        for col in self.csv_helper.get_required_column_names():
            value = self.csv_helper.get_value(row, col)
            if value is None or value == '':
                text = f'row: {row} missing expected value for col: {col}'
                raise RuntimeError(text)

    def _process_rows(self) -> None:
        """Process rows."""
        self._rule_definitions = {}
        self._implemented_requirements = {}
        self._control_implementations = {}
        self._components = {}
        for row_num, row in enumerate(self.csv_helper.row_generator()):
            control_mappings = self.csv_helper.get_value(row, 'Control_Mappings').split()
            if len(control_mappings):
                self._validate_columns(row)
                for control_mapping in control_mappings:
                    self._add_rule_implementation(control_mapping, row)
                self._add_rule_definition(row_num, row)

    def _get_components(self) -> List[DefinedComponent]:
        """Get components."""
        rval = []
        for key in self._components.keys():
            rval.append(self._components[key])
        return rval

    def _report_issues(self) -> None:
        """Report issues."""
        self.csv_helper.report_issues()
