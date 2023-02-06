# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2023 IBM Corp. All rights reserved.
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
import csv
import datetime
import logging
import pathlib
import sys
import traceback
import uuid
from math import log10
from typing import Iterator, List, Optional

from trestle.common.list_utils import as_list
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
        self.eg_ns = 'https://ibm.github.io/compliance-trestle/schemas/oscal/cd'
        self.eg_ns_user = 'https://ibm.github.io/compliance-trestle/schemas/oscal/cd/user-defined'

    def print_info(self) -> None:
        """Print the help string."""
        name = self.name
        oscal_name = 'component_definition'
        #
        logger.info(f'Help information for {name} task.')
        logger.info('')
        logger.info(f'Purpose: From csv produce OSCAL {oscal_name} file.')
        logger.info('')
        logger.info('')
        logger.info(f'Configuration flags sit under [task.{name}]:')
        text1 = '  title                = '
        text2 = '(required) the component definition title.'
        logger.info(text1 + text2)
        text1 = '  version              = '
        text2 = '(required) the component definition version.'
        logger.info(text1 + text2)
        text1 = '  csv-file             = '
        text2 = '(required) the path of the csv file.'
        logger.info(text1 + text2)
        text1 = '  required columns:      '
        for text2 in CsvColumn.columns_required:
            logger.info(text1 + text2)
            text1 = '                         '
        text1 = '  optional columns:      '
        for text2 in CsvColumn.columns_optional:
            logger.info(text1 + text2)
            text1 = '                         '
        text1 = '  output-dir           = '
        text2 = '(required) the path of the output directory for synthesized OSCAL .json files.'
        logger.info(text1 + text2)
        text1 = '  component-definition = '
        text2 = '(optional) the path of the existing component-definition OSCAL .json file.'
        logger.info(text1 + text2)
        text1 = '  namespace            = '
        text2 = f'(optional) the namespace for properties, e.g. {self.eg_ns}'
        logger.info(text1 + text2)
        text1 = '  user-namespace       = '
        text2 = f'(optional) the user-namespace for properties, e.g. {self.eg_ns_user}'
        logger.info(text1 + text2)
        text1 = '  class.column-name    = '
        text2 = '(optional) the class to associate with the specified column name, e.g. class.Rule_Id = scc_class'
        logger.info(text1 + text2)
        text1 = '  output-overwrite     = '
        text2 = '(optional) true [default] or false; replace existing output when true.'
        logger.info(text1 + text2)

    def configure(self) -> bool:
        """Configure."""
        self._timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc
                                                                                    ).isoformat()
        # config verbosity
        self._quiet = self._config.get('quiet', False)
        self._verbose = not self._quiet
        # title
        self._title = self._config.get('title')
        if self._title is None:
            logger.warning('config missing "title"')
            return False
        # version
        self._version = self._config.get('version')
        if self._version is None:
            logger.warning('config missing "version"')
            return False
        # namespace
        self._ns = self._config.get('namespace')
        if self._ns is None:
            logger.warning('config missing "namespace"')
            return False
        # user-namespace
        self._user_ns = self._config.get('user-namespace')
        if self._user_ns is None:
            logger.warning('config missing "user-namespace"')
            return False
        # config csv
        self._csv_file = self._config.get('csv-file')
        if self._csv_file is None:
            logger.warning('config missing "csv-file"')
            return False
        self._csv_path = pathlib.Path(self._csv_file)
        if not self._csv_path.exists():
            logger.warning('"csv-file" not found')
            return False
        # announce csv
        if self._verbose:
            logger.info(f'input: {self._csv_file}')
        # config cd
        self._cd_path = None
        self._cd_file = self._config.get('component-definition')
        if self._cd_file is not None:
            self._cd_path = pathlib.Path(self._cd_file)
            if not self._cd_path.exists():
                logger.warning('"component-definition" not found')
                return False
        return True

    def get_class(self, name: str) -> str:
        """Get class value for specified name from config."""
        key = f'class.{name}'
        return self._config.get(key)

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
        if not self.configure():
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
        # fetch existing component-definition, if any
        self._cd_mgr = _CdMgr(self._cd_path, self._title, self._timestamp, self._version)
        # fetch csv
        self._csv_mgr = _CsvMgr(self._csv_path)
        # calculate deletion, addition & modification rule lists
        rules = self._calculate_rules()
        # calculate deletion, addition & modification set-parameter lists
        set_params = self._calculate_set_params(rules[2])
        # calculate deletion, addition & modification control mapping lists
        control_mappings = self._calculate_control_mappings(rules[2])
        # rule set manager
        self._rule_set_id_mgr = _RuleSetIdMgr(self._cd_mgr.get_max_rule_set_number(), len(rules[1]))
        # rule additions, deletions & modifications (by row)
        self.rules_del(rules[0])
        self.rules_add(rules[1])
        self.rules_mod(rules[2])
        # set-parameters additions, deletions & modifications (by row)
        self.set_params_del(set_params[0])
        self.set_params_add(set_params[1])
        self.set_params_mod(set_params[2])
        # control mappings additions, deletions & modifications (by row)
        self.control_mappings_del(control_mappings[0])
        self.control_mappings_add(control_mappings[1])
        # note: control mappings mod is currently not possible
        # note: add/del user columns not currently supported
        # prepare new/revised component definition
        component_definition = self._cd_mgr.get_component_definition()
        # write OSCAL ComponentDefinition to file
        if self._verbose:
            logger.info(f'output: {ofile}')
        component_definition.oscal_write(pathlib.Path(ofile))
        return TaskOutcome('success')

    def _calculate_rules(self) -> tuple:
        """Calculate rules add, delete, modify."""
        cd_rules = self._cd_mgr.get_rule_keys()
        csv_rules = self._csv_mgr.get_rule_keys()
        del_rules = []
        add_rules = []
        mod_rules = []
        for key in cd_rules:
            if key in csv_rules:
                continue
            else:
                del_rules.append(key)
                logger.debug(f'rules del: {key}')
        for key in csv_rules:
            if key in cd_rules:
                mod_rules.append(key)
                logger.debug(f'rules mod: {key}')
            else:
                add_rules.append(key)
                logger.debug(f'rules add: {key}')
        return (del_rules, add_rules, mod_rules)

    def _calculate_set_params(self, mod_rules: List) -> tuple:
        """Calculate set parameters add, delete, modify."""
        cd_set_params = self._cd_mgr.get_set_params_keys()
        csv_set_params = self._csv_mgr.get_set_params_keys()
        del_set_params = []
        add_set_params = []
        mod_set_params = []
        for key in cd_set_params:
            rule_key = (key[0], key[1], key[2])
            if rule_key not in mod_rules:
                continue
            if key in csv_set_params:
                continue
            else:
                del_set_params.append(key)
                logger.debug(f'params del: {key}')
        for key in csv_set_params:
            rule_key = (key[0], key[1], key[2])
            if rule_key not in mod_rules:
                continue
            if key in cd_set_params:
                mod_set_params.append(key)
                logger.debug(f'params mod: {key}')
            else:
                add_set_params.append(key)
                logger.debug(f'prams add: {key}')
        return (del_set_params, add_set_params, mod_set_params)

    def _calculate_control_mappings(self, mod_rules: List) -> tuple:
        """Calculate control mappings add, delete, modify."""
        cd_controls = self._cd_mgr.get_control_keys()
        csv_controls = self._csv_mgr.get_control_keys()
        del_control_mappings = []
        add_control_mappings = []
        mod_control_mappings = []
        for key in cd_controls:
            rule_key = (key[0], key[1], key[2])
            if rule_key not in mod_rules:
                continue
            if key in csv_controls:
                continue
            else:
                del_control_mappings.append(key)
                logger.debug(f'ctl-maps del: {key}')
        for key in csv_controls:
            rule_key = (key[0], key[1], key[2])
            if rule_key not in mod_rules:
                continue
            if key in cd_controls:
                mod_control_mappings.append(key)
                logger.debug(f'ctl-maps mod: {key}')
            else:
                add_control_mappings.append(key)
                logger.debug(f'ctl-maps add: {key}')
        return (del_control_mappings, add_control_mappings, mod_control_mappings)

    def rules_del(self, del_rules: List[str]) -> None:
        """Delete rules."""
        for tokens in del_rules:
            resource = tokens[0]
            component_type = tokens[1]
            rule_id = tokens[2]
            description = ''
            # component
            component = self._cd_mgr.get_component(resource, component_type, description)
            # props
            component.props = self._delete_rule_props(component, rule_id)

    def _delete_rule_props(self, component: DefinedComponent, rule_id: str) -> List[Property]:
        """Delete rule props."""
        props = []
        rule_set = _RuleSetHelper.get_rule_set(component.props, rule_id)
        for prop in component.props:
            if prop.remarks.__root__ != rule_set:
                props.append(prop)
            elif prop.name == 'Parameter_Id':
                self._delete_rule_set_parameter(component, prop.value)
            elif prop.name == 'Rule_Id':
                self._delete_rule_implemented_requirement(component, prop.value)
        return props

    def _control_implementation_generator(
        self, control_implementations: List[ControlImplementation]
    ) -> Iterator[ControlImplementation]:
        """Control implementation generator."""
        if control_implementations:
            for control_implementation in control_implementations:
                yield control_implementation

    def _set_parameter_generator(self, set_parameters: List[SetParameter]) -> Iterator[SetParameter]:
        """Set parameter generator."""
        if set_parameters:
            for set_parameter in set_parameters:
                yield set_parameter

    def _implemented_requirement_generator(
        self, implemented_requirements: List[ImplementedRequirement]
    ) -> Iterator[ImplementedRequirement]:
        """Implemented-requirement generator."""
        if implemented_requirements:
            for implemented_requirement in implemented_requirements:
                yield implemented_requirement

    def _delete_rule_set_parameter(self, component: DefinedComponent, parameter_id: str) -> None:
        """Delete rule set-parameter."""
        control_implementations = component.control_implementations
        for control_implementation in self._control_implementation_generator(control_implementations):
            if control_implementation.set_parameters:
                set_parameters = control_implementation.set_parameters
                control_implementation.set_parameters = []
                for set_parameter in set_parameters:
                    if set_parameter.param_id != parameter_id:
                        _OscalHelper.add_set_parameter(control_implementation.set_parameters, set_parameter)
                if not len(control_implementation.set_parameters):
                    control_implementation.set_parameters = None

    def _delete_rule_implemented_requirement(self, component: DefinedComponent, rule_id: str) -> None:
        """Delete rule implemented_requirement."""
        control_implementations = component.control_implementations
        component.control_implementations = []
        for control_implementation in self._control_implementation_generator(control_implementations):
            if control_implementation.implemented_requirements:
                implemented_requirements = control_implementation.implemented_requirements
                control_implementation.implemented_requirements = []
                for implemented_requirement in implemented_requirements:
                    self._delete_ir_props(implemented_requirement, rule_id)
                    self._delete_ir_statements(implemented_requirement, rule_id)
                    if len(as_list(implemented_requirement.props)) or len(as_list(implemented_requirement.statements)):
                        control_implementation.implemented_requirements.append(implemented_requirement)
            if len(as_list(control_implementation.implemented_requirements)):
                component.control_implementations.append(control_implementation)

    def _delete_ir_statements(self, implemented_requirement: ImplementedRequirement, rule_id: str) -> None:
        """Delete implemented-requirement statements."""
        if implemented_requirement.statements:
            statements = implemented_requirement.statements
            implemented_requirement.statements = []
            for statement in statements:
                statement.props = self._delete_props(statement.props, rule_id)
                if not len(statement.props):
                    statement.props = None
                if statement.props:
                    implemented_requirement.statements.append(statement)
            if not len(implemented_requirement.statements):
                implemented_requirement.statements = None

    def _delete_ir_props(self, implemented_requirement: ImplementedRequirement, rule_id: str) -> None:
        """Delete implemented-requirement props."""
        if implemented_requirement.props:
            implemented_requirement.props = self._delete_props(implemented_requirement.props, rule_id)
            if not len(implemented_requirement.props):
                implemented_requirement.props = None

    def _delete_props(self, props: List[Property], rule_id: str) -> List[property]:
        """Delete props."""
        rval = []
        if props:
            for prop in props:
                if prop.name == 'Rule_Id' and prop.value == rule_id:
                    continue
                rval.append(prop)
        return rval

    def rules_add(self, add_rules: List[str]) -> None:
        """Add rules."""
        for rule_key in add_rules:
            resource = self._csv_mgr.get_value(rule_key, 'Resource')
            component_type = self._csv_mgr.get_value(rule_key, 'Component_Type')
            description = ''
            # component
            component = self._cd_mgr.get_component(resource, component_type, description)
            # props
            component.props = as_list(component.props)
            component.props = component.props + self._create_rule_props(rule_key)
            # control implementation
            source = self._csv_mgr.get_value(rule_key, 'Profile_Reference_URL')
            description = self._csv_mgr.get_value(rule_key, 'Profile_Description')
            control_implementation = self._get_control_implementation(component, source, description)
            # set-parameter
            set_parameter = self._create_set_parameter(rule_key)
            if set_parameter:
                control_implementation.set_parameters = as_list(control_implementation.set_parameters)
                _OscalHelper.add_set_parameter(control_implementation.set_parameters, set_parameter)
            # control-mappings
            control_mappings = self._csv_mgr.get_value(rule_key, 'Control_Mappings').split()
            self._add_rule_prop(control_implementation, control_mappings, rule_key)

    def _add_rule_prop(
        self, control_implementation: ControlImplementation, control_mappings: List[str], rule_key: tuple
    ) -> None:
        """Add rule prop."""
        for control_mapping in control_mappings:
            control_id = derive_control_id(control_mapping)
            implemented_requirement = self._get_implemented_requirement(control_implementation, control_id)
            # create rule implementation (as property)
            name = 'Rule_Id'
            prop = Property(
                name=name,
                value=self._csv_mgr.get_value(rule_key, name),
                ns=self._ns,
                class_=self.get_class(name),
            )
            part_id = derive_part_id(control_mapping)
            if part_id is None:
                implemented_requirement.props = as_list(implemented_requirement.props)
                implemented_requirement.props.append(prop)
            else:
                statement = self._get_statement(implemented_requirement, part_id)
                statement.props.append(prop)

    def _create_rule_props(self, rule_key: tuple) -> List[Property]:
        """Create rule props."""
        rule_set = self._rule_set_id_mgr.get_next_rule_set_id()
        row_number = self._csv_mgr.get_row_number(rule_key)
        rule_set_mgr = _RuleSetMgr(row_number, rule_set)
        column_names = CsvColumn.get_filtered_required_column_names() + CsvColumn.get_filtered_optional_column_names()
        # req'd & optional props
        for column_name in column_names:
            column_value = self._csv_mgr.get_value(rule_key, column_name).strip()
            rule_set_mgr.add_prop(column_name, column_value, self._ns, self.get_class(column_name))
        # parameter columns
        column_names = CsvColumn.get_parameter_column_names()
        for column_name in column_names:
            column_value = self._csv_mgr.get_value(rule_key, column_name).strip()
            rule_set_mgr.add_prop(column_name, column_value, self._ns, self.get_class(column_name))
        # user props
        column_names = self._csv_mgr.get_user_column_names()
        for column_name in column_names:
            column_value = self._csv_mgr.get_value(rule_key, column_name)
            rule_set_mgr.add_prop(column_name, column_value, self._user_ns, self.get_class(column_name))
        rule_set_mgr.validate()
        return rule_set_mgr.get_props()

    def _get_control_implementation(
        self, component: DefinedComponent, source: str, description: str
    ) -> ControlImplementation:
        """Find or create control implementation."""
        component.control_implementations = as_list(component.control_implementations)
        for control_implementation in component.control_implementations:
            if control_implementation.source == source and control_implementation.description == description:
                return control_implementation
        control_implementation = ControlImplementation(
            uuid=str(uuid.uuid4()), source=source, description=description, implemented_requirements=[]
        )
        component.control_implementations.append(control_implementation)
        return control_implementation

    def _create_set_parameter(self, rule_key: tuple) -> SetParameter:
        """Create create set parameters."""
        set_parameter = None
        name = self._csv_mgr.get_value(rule_key, 'Parameter_Id')
        if name:
            value = self._csv_mgr.get_value(rule_key, 'Parameter_Default_Value')
            if value == '':
                row_number = self._csv_mgr.get_row_number(rule_key)
                column_name = 'Parameter_Default_Value'
                text = f'row "{row_number}" missing value for "{column_name}"'
                raise RuntimeError(text)
            values = value.split(',')
            set_parameter = SetParameter(
                param_id=name,
                values=values,
            )
        return set_parameter

    def _get_implemented_requirement(
        self, control_implementation: ControlImplementation, control_id: str
    ) -> ImplementedRequirement:
        """Find or create implemented requirement."""
        for implemented_requirement in control_implementation.implemented_requirements:
            if implemented_requirement.control_id == control_id:
                return implemented_requirement
        implemented_requirement = ImplementedRequirement(
            uuid=str(uuid.uuid4()),
            control_id=control_id,
            description='',
        )
        control_implementation.implemented_requirements.append(implemented_requirement)
        return implemented_requirement

    def _get_statement(self, implemented_requirement: ImplementedRequirement, part_id: str) -> Statement:
        """Find or create statement."""
        implemented_requirement.statements = as_list(implemented_requirement.statements)
        for statement in implemented_requirement.statements:
            if statement.statement_id == part_id:
                return statement
        statement = Statement(
            uuid=str(uuid.uuid4()),
            statement_id=part_id,
            description='',
            props=[],
        )
        implemented_requirement.statements.append(statement)
        return statement

    def rules_mod(self, mod_rules: List[str]) -> None:
        """Modify rules."""
        for rule_key in mod_rules:
            resource = self._csv_mgr.get_value(rule_key, 'Resource')
            component_type = self._csv_mgr.get_value(rule_key, 'Component_Type')
            description = ''
            # component
            component = self._cd_mgr.get_component(resource, component_type, description)
            # props
            component.props = self._modify_rule_props(component, rule_key)

    def _modify_rule_props(self, component: DefinedComponent, rule_key: tuple) -> List[Property]:
        """Modify rule props."""
        rule_id = self._csv_mgr.get_value(rule_key, 'Rule_Id')
        rule_set = _RuleSetHelper.get_rule_set(component.props, rule_id)
        column_names = CsvColumn.get_filtered_required_column_names() + CsvColumn.get_filtered_optional_column_names()
        # req'd & optional props
        ns = self._ns
        for column_name in column_names:
            column_value = self._csv_mgr.get_value(rule_key, column_name).strip()
            class_ = self.get_class(column_name)
            self._cd_mgr.update_rule_definition(component, rule_set, column_name, column_value, ns, class_)
        # parameter columns
        column_names = CsvColumn.get_parameter_column_names()
        for column_name in column_names:
            column_value = self._csv_mgr.get_value(rule_key, column_name).strip()
            class_ = self.get_class(column_name)
            self._cd_mgr.update_rule_definition(component, rule_set, column_name, column_value, ns, class_)
        # user props
        ns = self._user_ns
        column_names = self._csv_mgr.get_user_column_names()
        for column_name in column_names:
            column_value = self._csv_mgr.get_value(rule_key, column_name).strip()
            self._cd_mgr.update_rule_definition(component, rule_set, column_name, column_value, ns, class_)
        return component.props

    def set_params_del(self, del_set_params: List[str]) -> None:
        """Set parameters delete."""
        for tokens in del_set_params:
            resource = tokens[0]
            component_type = tokens[1]
            source = tokens[3]
            description = tokens[4]
            param_id = tokens[5]
            control_implementation = self._cd_mgr.find_control_implementation(
                resource, component_type, source, description
            )
            if control_implementation:
                set_parameters = control_implementation.set_parameters
                control_implementation.set_parameters = []
                for set_parameter in self._set_parameter_generator(set_parameters):
                    if set_parameter.param_id == param_id:
                        continue
                    _OscalHelper.add_set_parameter(control_implementation.set_parameters, set_parameter)
                if control_implementation.set_parameters == []:
                    control_implementation.set_parameters = None

    def set_params_add(self, add_set_params: List[str]) -> None:
        """Set parameters add."""
        for tokens in add_set_params:
            resource = tokens[0]
            component_type = tokens[1]
            rule_id = tokens[2]
            source = tokens[3]
            description = tokens[4]
            param_id = tokens[5]
            control_implementation = self._cd_mgr.find_control_implementation(
                resource, component_type, source, description
            )
            control_implementation.set_parameters = as_list(control_implementation.set_parameters)
            # add
            rule_key = _CsvMgr.get_rule_key(resource, component_type, rule_id)
            values = [self._csv_mgr.get_value(rule_key, 'Parameter_Default_Value')]
            set_parameter = SetParameter(
                param_id=param_id,
                values=values,
            )
            _OscalHelper.add_set_parameter(control_implementation.set_parameters, set_parameter)

    def set_params_mod(self, mod_set_params: List[str]) -> None:
        """Set parameters modify."""
        for tokens in mod_set_params:
            resource = tokens[0]
            component_type = tokens[1]
            rule_id = tokens[2]
            source = tokens[3]
            description = tokens[4]
            param_id = tokens[5]
            control_implementation = self._cd_mgr.find_control_implementation(
                resource, component_type, source, description
            )
            if control_implementation:
                set_parameters = control_implementation.set_parameters
                for set_parameter in self._set_parameter_generator(set_parameters):
                    if set_parameter.param_id != param_id:
                        continue
                    rule_key = _CsvMgr.get_rule_key(resource, component_type, rule_id)
                    values = [self._csv_mgr.get_value(rule_key, 'Parameter_Default_Value')]
                    replacement = SetParameter(
                        param_id=param_id,
                        values=values,
                    )
                    if set_parameter.values == replacement.values:
                        continue
                    logger.debug(f'params-mod: {rule_id} {param_id} {set_parameter.values} -> {replacement.values}')
                    set_parameter.values = replacement.values

    def _control_mappings_generator(self, control_mappings: List[str]) -> Iterator[List[str]]:
        """Control mappings generator."""
        for tokens in control_mappings:
            resource = tokens[0]
            component_type = tokens[1]
            source = tokens[3]
            description = tokens[4]
            control_implementation = self._cd_mgr.find_control_implementation(
                resource, component_type, source, description
            )
            if control_implementation:
                yield tokens

    def control_mappings_del(self, del_control_mappings: List[str]) -> None:
        """Control mappings delete."""
        for tokens in self._control_mappings_generator(del_control_mappings):
            resource = tokens[0]
            component_type = tokens[1]
            rule_id = tokens[2]
            source = tokens[3]
            description = tokens[4]
            smt_id = tokens[5]
            control_id = derive_control_id(smt_id)
            control_implementation = self._cd_mgr.find_control_implementation(
                resource, component_type, source, description
            )
            implemented_requirements = control_implementation.implemented_requirements
            control_implementation.implemented_requirements = []
            for implemented_requirement in self._implemented_requirement_generator(implemented_requirements):
                if implemented_requirement.control_id == control_id:
                    implemented_requirement.statements = _OscalHelper.remove_rule_statement(
                        implemented_requirement.statements, rule_id, smt_id
                    )
                    implemented_requirement.props = _OscalHelper.remove_rule(implemented_requirement.props, rule_id)
                    if len(as_list(implemented_requirement.props)) or len(as_list(implemented_requirement.statements)):
                        control_implementation.implemented_requirements.append(implemented_requirement)
                else:
                    control_implementation.implemented_requirements.append(implemented_requirement)

    def control_mappings_add(self, add_control_mappings: List[str]) -> None:
        """Control mappings add."""
        for tokens in self._control_mappings_generator(add_control_mappings):
            resource = tokens[0]
            component_type = tokens[1]
            rule_id = tokens[2]
            source = tokens[3]
            description = tokens[4]
            smt_id = tokens[5]
            control_id = derive_control_id(smt_id)
            control_implementation = self._cd_mgr.find_control_implementation(
                resource, component_type, source, description
            )
            implemented_requirement = self._get_implemented_requirement(control_implementation, control_id)
            # create rule implementation (as property)
            name = 'Rule_Id'
            prop = Property(
                name=name,
                value=rule_id,
                ns=self._ns,
                class_=self.get_class(name),
            )
            if smt_id == control_id:
                implemented_requirement.props = as_list(implemented_requirement.props)
                implemented_requirement.props.append(prop)
            else:
                statement = self._get_statement(implemented_requirement, smt_id)
                statement.props.append(prop)


class _OscalHelper():
    """Oscal Helper."""

    @staticmethod
    def add_set_parameter(set_parameter_list: List[SetParameter], set_parameter: SetParameter) -> None:
        """Add set parameter."""
        set_parameter_list.append(set_parameter)

    @staticmethod
    def remove_rule_statement(statements: List[Statement], rule_id: str, smt_id: str) -> List[Statement]:
        """Remove rule from statements."""
        rval = statements
        if statements:
            rval = []
            for statement in statements:
                if statement.statement_id == smt_id:
                    statement.props = _OscalHelper.remove_rule(statement.props, rule_id)
                if statement.props is not None and len(statement.props):
                    rval.append(statement)
        return rval

    @staticmethod
    def remove_rule(props: List[Property], rule_id: str) -> List[Property]:
        """Remove rule from props."""
        rval = props
        if props:
            rval = []
            for prop in props:
                if prop.name != 'Rule_Id' or prop.value != rule_id:
                    rval.append(prop)
        return rval


class _RuleSetHelper():
    """RuleSet Helper."""

    @staticmethod
    def get_rule_set(props: List[Property], rule_id: str) -> str:
        """Get rule_set for given rule_id."""
        rule_set = None
        if props:
            for prop in props:
                if prop.name == 'Rule_Id' and prop.value == rule_id:
                    rule_set = prop.remarks.__root__
                    break
        return rule_set


class _RuleSetIdMgr():
    """RuleSetId Manager."""

    def __init__(self, max_rule_set_number: int, add_rules_count: int) -> None:
        """Initialize."""
        self._prev_rule_set_number = max_rule_set_number
        self._rule_set_number_digits = max_rule_set_number + add_rules_count + 1
        self._fill_sz = int(log10(self._rule_set_number_digits)) + 1

    def get_next_rule_set_id(self) -> str:
        self._prev_rule_set_number += 1
        rval = f'rule_set_{str(self._prev_rule_set_number).zfill(self._fill_sz)}'
        return rval


class _RuleSetMgr():
    """RuleSet manager."""

    def __init__(self, row_number: int, rule_set: str) -> None:
        """Initialize."""
        self._row_number = row_number
        self._rule_set = rule_set
        self._props = {}

    def add_prop(self, name: str, value: str, ns: str, class_: str) -> None:
        """Add prop."""
        if value is not None and len(value):
            prop = Property(
                name=name,
                value=value,
                ns=ns,
                class_=class_,
                remarks=self._rule_set,
            )
            self._props[name] = prop

    def validate(self) -> None:
        """Validate."""
        if 'Parameter_Id' not in self._props.keys():
            forbidden = CsvColumn.get_parameter_dependent_column_names()
            for name in self._props.keys():
                if name in forbidden:
                    text = f'row "{self._row_number}" invalid "{name}"'
                    raise RuntimeError(text)

    def get_props(self) -> List[Property]:
        """Get props."""
        rval = []
        c1 = CsvColumn.get_required_column_names()
        for key in c1:
            if key in self._props.keys():
                rval.append(self._props[key])
        c2 = CsvColumn.get_optional_column_names()
        for key in c2:
            if key in self._props.keys():
                rval.append(self._props[key])
        for key in self._props.keys():
            if key in c1 or key in c2:
                continue
            rval.append(self._props[key])
        return rval


class _CdMgr():
    """CD Manager."""

    def __init__(self, cd_path: pathlib.Path, title: str, timestamp: str, version: str) -> None:
        """Initialize."""
        if cd_path:
            self._component_definition = ComponentDefinition.oscal_read(cd_path)
            metadata = self._component_definition.metadata
            metadata.title = title
            metadata.last_modified = timestamp
            metadata.oscal_version = OSCAL_VERSION
            metadata.version = version
        else:
            metadata = Metadata(
                title=title,
                last_modified=timestamp,
                oscal_version=OSCAL_VERSION,
                version=version,
            )
            self._component_definition = ComponentDefinition(
                uuid=str(uuid.uuid4()),
                metadata=metadata,
                components=[],
            )
        #
        self._max_rule_set_number = -1
        self._cd_rules_map = {}
        self._cd_set_params_map = {}
        self._cd_controls_map = {}
        #
        for component in self._component_definition.components:
            self.accounting(component)
        logger.debug(f'cd rules: {len(self._cd_rules_map)}')
        logger.debug(f'cd params: {len(self._cd_rules_map)}')
        logger.debug(f'cd controls: {len(self._cd_controls_map)}')

    def get_component(self, resource: str, component_type: str, description: str) -> DefinedComponent:
        """Get component."""
        for component in self._component_definition.components:
            if component.title == resource and component.type == component_type:
                logger.debug(f'located component: title={component.title} type={component.type}')
                return component
        component = DefinedComponent(
            uuid=str(uuid.uuid4()),
            type=component_type,
            title=resource,
            description=description,
            control_implementations=[],
        )
        self._component_definition.components.append(component)
        logger.debug(f'created component: title={component.title} type={component.type}')
        return component

    def find_component(self, resource: str, component_type: str) -> DefinedComponent:
        """Find component."""
        rval = None
        for component in self._component_definition.components:
            if component.title == resource and component.type == component_type:
                logger.debug(f'located component: title={component.title} type={component.type}')
                rval = component
                break
        return rval

    def find_control_implementation(
        self, resource: str, component_type: str, source: str, description: str
    ) -> ControlImplementation:
        """Find control-implementation."""
        rval = None
        component = self.find_component(resource, component_type)
        for control_implementation in component.control_implementations:
            if control_implementation.source == source and control_implementation.description == description:
                rval = control_implementation
                break
        return rval

    def get_component_definition(self) -> ComponentDefinition:
        """Get component definition."""
        # remove empty components
        self._remove_empty_components()
        return self._component_definition

    def _remove_empty_components(self) -> None:
        """Remove empty components."""
        component_definition = self._component_definition
        components = component_definition.components
        component_definition.components = []
        for component in components:
            if component.props is None or len(component.props) == 0:
                if component.control_implementations is None or len(component.control_implementations) == 0:
                    continue
            component_definition.components.append(component)

    def get_max_rule_set_number(self) -> int:
        """Get max rule set number."""
        return self._max_rule_set_number

    def get_rule_keys(self) -> List[str]:
        """Get rule keys."""
        return self._cd_rules_map.keys()

    def get_set_params_keys(self) -> List[str]:
        """Get set-parameter keys."""
        return self._cd_set_params_map.keys()

    def get_control_keys(self) -> List[str]:
        """Get control keys."""
        return self._cd_controls_map.keys()

    def accounting(self, component: DefinedComponent) -> None:
        """Accounting."""
        # rule definitions
        self.accounting_rule_definitions(component)
        # set-parameters & control mappings
        if component.control_implementations:
            for control_implementation in component.control_implementations:
                # set-parameters
                self.accounting_set_parameters(component, control_implementation)
                # control mappings
                self.accounting_control_mappings(component, control_implementation)

    def accounting_rule_definitions(self, component: DefinedComponent) -> None:
        """Accounting, rule definitions."""
        if component.props:
            for prop in component.props:
                if prop.name == 'Rule_Id':
                    key = (component.title, component.type, prop.value)
                    value = prop.remarks.__root__
                    self._cd_rules_map[key] = value
                    logger.debug(f'cd: {key} {self._cd_rules_map[key]}')
                    rule_set_number = int(value.replace('rule_set_', ''))
                    if rule_set_number > self._max_rule_set_number:
                        self._max_rule_set_number = rule_set_number

    def accounting_set_parameters(
        self, component: DefinedComponent, control_implementation: ControlImplementation
    ) -> None:
        """Accounting, set-parameters."""
        if control_implementation.set_parameters:
            for set_parameter in control_implementation.set_parameters:
                rule_id = self._get_rule_id(component, set_parameter.param_id)
                key = (
                    component.title,
                    component.type,
                    rule_id,
                    control_implementation.source,
                    control_implementation.description,
                    set_parameter.param_id
                )
                value = set_parameter.values
                self._cd_set_params_map[key] = value

    def accounting_control_mappings(
        self, component: DefinedComponent, control_implementation: ControlImplementation
    ) -> None:
        """Accounting, control mappings."""
        if control_implementation.implemented_requirements:
            for implemented_requirement in control_implementation.implemented_requirements:
                self.accounting_control_mappings_props(component, control_implementation, implemented_requirement)
                self.accounting_control_mappings_statements(component, control_implementation, implemented_requirement)

    def accounting_control_mappings_props(
        self,
        component: DefinedComponent,
        control_implementation: ControlImplementation,
        implemented_requirement: ImplementedRequirement
    ) -> None:
        """Accounting, control mappings props."""
        if implemented_requirement.props:
            for prop in implemented_requirement.props:
                if prop.name == 'Rule_Id':
                    rule_id = prop.value
                    key = (
                        component.title,
                        component.type,
                        rule_id,
                        control_implementation.source,
                        control_implementation.description,
                        implemented_requirement.control_id,
                    )
                    self._cd_controls_map[key] = prop

    def accounting_control_mappings_statements(
        self,
        component: DefinedComponent,
        control_implementation: ControlImplementation,
        implemented_requirement: ImplementedRequirement
    ) -> None:
        """Accounting, control mappings statements."""
        if implemented_requirement.statements:
            for statement in implemented_requirement.statements:
                if statement.props:
                    for prop in statement.props:
                        if prop.name == 'Rule_Id':
                            rule_id = prop.value
                            key = (
                                component.title,
                                component.type,
                                rule_id,
                                control_implementation.source,
                                control_implementation.description,
                                statement.statement_id,
                            )
                            self._cd_controls_map[key] = prop

    def _get_rule_id(self, component: DefinedComponent, param_id: str) -> str:
        """Get rule_id for given param_id."""
        rule_id = None
        if component.props:
            map_ = {}
            rule_set = None
            for prop in component.props:
                if prop.name == 'Rule_Id':
                    map_[prop.remarks.__root__] = prop.value
                elif prop.name == 'Parameter_Id' and prop.value == param_id:
                    rule_set = prop.remarks.__root__
            if rule_set:
                rule_id = map_[rule_set]
        return rule_id

    def update_rule_definition(
        self, component: DefinedComponent, rule_set: str, name: str, value: str, ns: str, class_: str
    ) -> None:
        """Update rule definition."""
        if value is not None and len(value):
            prop = self.find_property(component, rule_set, name)
            if prop:
                # no change
                if prop.value == value:
                    return
                # replace value
                logger.debug(f'update-rule: {rule_set} {name} {prop.value} -> {value}')
                prop.value = value
            else:
                self.add_property(component, rule_set, name, value, ns, class_)
        else:
            self.delete_property(component, rule_set, name)

    def find_property(self, component: DefinedComponent, rule_set: str, name: str) -> Property:
        """Find property."""
        rval = None
        for prop in component.props:
            if prop.remarks.__root__ == rule_set and prop.name == name:
                rval = prop
                break
        return rval

    def add_property(
        self, component: DefinedComponent, rule_set: str, name: str, value: str, ns: str, class_: str
    ) -> None:
        """Add property."""
        prop_add = Property(
            name=name,
            value=value,
            ns=ns,
            class_=class_,
            remarks=rule_set,
        )
        last = 0
        for index, prop in enumerate(component.props):
            if prop.remarks.__root__ == rule_set:
                last = index
        props = []
        for index, prop in enumerate(component.props):
            if prop_add:
                if index > last:
                    props.append(prop_add)
                    prop_add = None
                    logger.debug(f'add-prop (last): {rule_set} {name} {prop.value} ->> {value}')
                elif prop_add.remarks.__root__ == prop.remarks.__root__:
                    if CsvColumn.get_order(prop.name) > CsvColumn.get_order(prop_add.name):
                        props.append(prop_add)
                        prop_add = None
                        logger.debug(f'add-prop (order): {rule_set} {name} {prop.value} ->> {value}')
            props.append(prop)
        component.props = props

    def delete_property(self, component: DefinedComponent, rule_set: str, name: str) -> None:
        """Delete property."""
        props = []
        for prop in component.props:
            if prop.remarks.__root__ == rule_set and prop.name == name:
                logger.debug(f'delete-prop: {rule_set} {name} {prop.value}')
            else:
                props.append(prop)
        component.props = props


class CsvColumn():
    """CsvColumn."""

    columns_required = [
        'Rule_Id',
        'Rule_Description',
        'Profile_Reference_URL',
        'Profile_Description',
        'Component_Type',
        'Control_Mappings',
        'Resource',
    ]

    # columns required which do not become properties
    columns_required_filtered = [
        'Profile_Reference_URL',
        'Profile_Description',
        'Component_Type',
        'Control_Mappings',
        'Resource',
    ]

    columns_optional = [
        'Parameter_Id',
        'Parameter_Description',
        'Parameter_Default_Value',
        'Parameter_Value_Alternatives',
        'Check_Id',
        'Check_Description',
        'Fetcher',
        'Fetcher_Description',
        'Resource_Instance_Type',
    ]

    # optional columns which do not become properties, initially
    columns_optional_filtered = [
        'Parameter_Id',
        'Parameter_Description',
        'Parameter_Default_Value',
        'Parameter_Value_Alternatives',
    ]

    # optional columns which do become properties, afterwards
    columns_parameters = [
        'Parameter_Id',
        'Parameter_Description',
        'Parameter_Value_Alternatives',
    ]

    # optional columns which require Parameter_Id be present in the row
    columns_parameters_dependent = [
        'Parameter_Description',
        'Parameter_Default_Value',
        'Parameter_Value_Alternatives',
    ]

    columns_filtered = columns_required_filtered + columns_optional_filtered

    @staticmethod
    def get_order(column_name: str) -> int:
        """Get order for column_name."""
        rval = sys.maxsize
        columns_ordered = CsvColumn.columns_required + CsvColumn.columns_optional
        if column_name in columns_ordered:
            rval = columns_ordered.index(column_name)
        return rval

    @staticmethod
    def get_required_column_names() -> List[str]:
        """Get required column names."""
        rval = []
        rval += CsvColumn.columns_required
        return rval

    @staticmethod
    def get_filtered_required_column_names() -> List[str]:
        """Get filtered required column names."""
        rval = []
        for column_name in CsvColumn.get_required_column_names():
            if column_name not in CsvColumn.columns_filtered:
                rval.append(column_name)
        return rval

    @staticmethod
    def get_optional_column_names() -> List[str]:
        """Get optional column names."""
        rval = []
        rval += CsvColumn.columns_optional
        return rval

    @staticmethod
    def get_filtered_optional_column_names() -> List[str]:
        """Get filtered optional column names."""
        rval = []
        for column_name in CsvColumn.get_optional_column_names():
            if column_name not in CsvColumn.columns_filtered:
                rval.append(column_name)
        return rval

    @staticmethod
    def get_reserved_column_names() -> List[str]:
        """Get reserved column names."""
        rval = []
        rval += CsvColumn.columns_required
        rval += CsvColumn.columns_optional
        return rval

    @staticmethod
    def get_parameter_column_names() -> List[str]:
        """Get parameter column names."""
        rval = []
        rval += CsvColumn.columns_parameters
        return rval

    @staticmethod
    def get_parameter_dependent_column_names() -> List[str]:
        """Get parameter dependent column names."""
        rval = []
        rval += CsvColumn.columns_parameters_dependent
        return rval


class _CsvMgr():
    """Csv Manager."""

    def __init__(self, csv_path: pathlib.Path) -> None:
        """Initialize."""
        self._csv = []
        with open(csv_path, 'r', newline='') as f:
            csv_reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for row in csv_reader:
                self._csv.append(row)
        self._verify()
        self._csv_rules_map = {}
        self._csv_set_params_map = {}
        self._csv_controls_map = {}
        for row_num, row in self.row_generator():
            self._check_row_minimum_requirements(row_num, row)
            resource = self.get_row_value(row, 'Resource')
            component_type = self.get_row_value(row, 'Component_Type')
            rule_id = self.get_row_value(row, 'Rule_Id')
            # rule sets
            key = _CsvMgr.get_rule_key(resource, component_type, rule_id)
            if key in self._csv_rules_map:
                text = f'row "{row_num}" contains duplicate Rule_Id "{rule_id}"'
                raise RuntimeError(text)
            self._csv_rules_map[key] = [row_num, row]
            logger.debug(f'csv-rules: {key} {self._csv_rules_map[key][0]}')
            # set parameters, by component
            source = self.get_row_value(row, 'Profile_Reference_URL')
            description = self.get_row_value(row, 'Profile_Description')
            param_id = self.get_row_value(row, 'Parameter_Id')
            if param_id:
                key = (resource, component_type, rule_id, source, description, param_id)
                self._csv_set_params_map[key] = [row_num, row]
                logger.debug(f'csv-set-parameters: {key} {self._csv_set_params_map[key][0]}')
            # control mappings
            control_mappings = self.get_row_value(row, 'Control_Mappings')
            if control_mappings:
                controls = control_mappings.split()
                for control in controls:
                    key = (resource, component_type, rule_id, source, description, control)
                    self._csv_controls_map[key] = [row_num, row]
        logger.debug(f'csv rules: {len(self._csv_rules_map)}')
        logger.debug(f'csv params: {len(self._csv_set_params_map)}')
        logger.debug(f'csv controls: {len(self._csv_controls_map)}')

    @staticmethod
    def get_rule_key(resource: str, component_type: str, rule_id: str) -> tuple:
        """Get rule_key."""
        return (resource, component_type, rule_id)

    def row_generator(self) -> [int, Iterator[List[str]]]:
        """Generate rows."""
        index = 0
        for row in self._csv:
            index += 1
            if index == 1:
                continue
            control_mappings = self.get_row_value(row, 'Control_Mappings')
            if not len(control_mappings):
                continue
            logger.debug(f'row_gen: {index} {row}')
            yield index, row

    def _check_row_minimum_requirements(self, row_num: int, row: List) -> None:
        """Check row minimum requirements."""
        for column_name in CsvColumn.get_required_column_names():
            value = self.get_row_value(row, column_name)
            if value is None or value == '':
                text = f'row "{row_num}" missing value for "{column_name}"'
                raise RuntimeError(text)

    def _verify(self) -> None:
        """Verify."""
        required_columns = CsvColumn.get_required_column_names()
        if len(self._csv):
            head_row = self._csv[0]
            for heading in head_row:
                if heading in required_columns:
                    required_columns.remove(heading)
        if len(required_columns):
            text = f'Missing columns: {required_columns}'
            raise RuntimeError(text)

    def get_rule_keys(self) -> List[tuple]:
        """Get rule keys."""
        return self._csv_rules_map.keys()

    def get_set_params_keys(self) -> List[tuple]:
        """Get set-parameter keys."""
        return self._csv_set_params_map.keys()

    def get_control_keys(self) -> List[tuple]:
        """Get control keys."""
        return self._csv_controls_map.keys()

    def get_col_index(self, column_name: str) -> int:
        """Get index for column name."""
        rval = -1
        index = 0
        head_row = self._csv[0]
        for heading in head_row:
            if heading == column_name:
                rval = index
                break
            index += 1
        return rval

    def get_row(self, rule_key: tuple) -> List:
        """Get row for rule."""
        return self._csv_rules_map[rule_key][1]

    def get_row_number(self, rule_key: tuple) -> List:
        """Get row number for rule."""
        return self._csv_rules_map[rule_key][0]

    def get_row_value(self, row: List[str], name: str) -> str:
        """Get value for specified name."""
        rval = ''
        index = self.get_col_index(name)
        if index >= 0:
            rval = row[index]
        return rval

    def get_value(self, rule_key: tuple, name: str) -> str:
        """Get value for specified name."""
        row = self.get_row(rule_key)
        return self.get_row_value(row, name)

    def get_user_column_names(self) -> List[str]:
        """Get user column names."""
        user_column_names = []
        reserved_column_names = CsvColumn.get_reserved_column_names()
        for column_name in self._csv[0]:
            if column_name not in reserved_column_names:
                user_column_names.append(column_name)
        return user_column_names
