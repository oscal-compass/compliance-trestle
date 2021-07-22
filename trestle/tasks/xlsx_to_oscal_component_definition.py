# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2021 IBM Corp. All rights reserved.
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
from mypyc.primitives import str_ops
"""OSCAL transformation tasks."""

import configparser
import datetime
import logging
import json
import pathlib
import string
import traceback
import uuid
from typing import Any, Dict, List, Optional

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from trestle import __version__
from trestle.core import const
from trestle.oscal import OSCAL_VERSION
from trestle.oscal.catalog import Catalog
from trestle.oscal.common import Metadata
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
from trestle.utils.oscal_helper import CatalogHelper
from trestle.utils.parameter_helper import ParameterHelper

logger = logging.getLogger(__name__)

t_component_name = str
t_control = str
t_description = str
t_goal_id = int
t_goal_name_id = str
t_goal_remarks = str
t_goal_text = str
t_goal_version = str
t_guidelines = str
t_name = str
t_parameter_usage = str
t_parameter_value = str
t_parameter_values = str
t_row = int
t_statements = List[str]
t_tokens = List[str]
t_type = str
t_uuid_str = str
t_values = str
t_work_sheet = Worksheet

t_controls = Dict[t_control, t_statements]


class XlsxToOscalComponentDefinition(TaskBase):
    """
    Task to create OSCAL ComponentDefinition json.

    Attributes:
        name: Name of the task.
    """

    name = 'xlsx-to-oscal-component-definition'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task xlsx-to-oscal-component-definition.

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)
        self._timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc
                                                                                    ).isoformat()

    def set_timestamp(self, timestamp) -> None:
        """Set the timestamp."""
        self._timestamp = timestamp

    def print_info(self) -> None:
        """Print the help string."""
        logger.info(f'Help information for {self.name} task.')
        logger.info('')
        logger.info(
            'Purpose: From spread sheet and catalog produce Open Security Controls Assessment Language (OSCAL) component definition file.'
        )
        logger.info('')
        logger.info('Configuration flags sit under [task.xlsx-to-oscal-component-definition]:')
        logger.info(
            '  catalog-file      = (required) the path of the OSCAL catalog file, for example NIST Special Publication 800-53 Revision 4.'
        )
        logger.info(
            '  spread-sheet-file = (required) the path of the spread sheet file, containing data for production of component definition.'
        )
        logger.info('  work-sheet-name   = (required) the name of the work sheet in the spread sheet file.')
        logger.info('                      column "a" contains goal ID.')
        logger.info('                      column "b" contains goal text.')
        logger.info('                      column "ac-ai" contains controls.')
        logger.info('                      column "am" contains component name.')
        logger.info('                      column "an" contains goal name.')
        logger.info('                      column "ar" contains parameter name and description, separated by newline.')
        logger.info('                      column "as" contains parameter values.')
        logger.info(
            '  output-dir        = (required) the path of the output directory comprising synthesized OSCAL .json files.'
        )
        logger.info('  output-overwrite  = (optional) true [default] or false; replace existing output when true.')

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
        if not self._config:
            logger.error(f'config missing')
            return TaskOutcome('failure')
        # process config
        catalog_file = self._config.get('catalog-file')
        if catalog_file is None:
            logger.error(f'config missing "catalog-file"')
            return TaskOutcome('failure')
        catalog_helper = CatalogHelper(catalog_file)
        if not catalog_helper.exists():
            logger.error(f'"catalog-file" not found')
            return TaskOutcome('failure')
        spread_sheet = self._config.get('spread-sheet-file')
        if spread_sheet is None:
            logger.error(f'config missing "spread-sheet"')
            return TaskOutcome('failure')
        if not pathlib.Path(spread_sheet).exists():
            logger.error(f'"spread-sheet" not found')
            return TaskOutcome('failure')
        odir = self._config.get('output-dir')
        opth = pathlib.Path(odir)
        self._overwrite = self._config.getboolean('output-overwrite', True)
        quiet = self._config.get('quiet', False)
        self._verbose = not quiet
        # insure output dir exists
        opth.mkdir(exist_ok=True, parents=True)
        # announce spreadsheet
        if self._verbose:
            logger.info(f'input: {spread_sheet}')
        # calculate output file name & check writability
        oname = 'component-definition.json'
        ofile = opth / oname
        if not self._overwrite and pathlib.Path(ofile).exists():
            logger.error(f'output: {ofile} already exists')
            return TaskOutcome(mode + 'failure')
        # initialize
        defined_components = []
        # load the .xlsx contents
        wb = load_workbook(spread_sheet)
        sheet_name = self._config.get('work-sheet-name')
        if sheet_name is None:
            logger.error(f'config missing "work-sheet-name"')
            return TaskOutcome('failure')
        work_sheet = wb[sheet_name]
        component_names = []
        parameters = {}
        parameter_helper = None
        # accumulators
        self.rows_missing_goal_name_id = []
        self.rows_missing_controls = []
        self.rows_missing_parameters = []
        self.rows_missing_parameters_values = []
        # roles
        roles = [
            Role(id='prepared-by', title='Indicates the organization that created this content.'),
            Role(id='prepared-for', title='Indicates the organization for which this content was created..'),
            Role(
                id='content-approver',
                title='Indicates the organization responsible for all content represented in the "document".'
            ),
        ]
        # parties
        party_uuid_01 = str(uuid.uuid4())
        party_uuid_02 = str(uuid.uuid4())
        party_uuid_03 = str(uuid.uuid4())
        parties = [
            Party(uuid=party_uuid_01, type='organization', name='International Business Machines', remarks='IBM'),
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
        # responsible parties
        prepared_by = ResponsibleParty(role_id='prepared-by', party_uuids=[party_uuid_01])
        prepared_for = ResponsibleParty(role_id='prepared-for', party_uuids=[party_uuid_02, party_uuid_03])
        content_approver = ResponsibleParty(role_id='content-approver', party_uuids=[party_uuid_01])
        responsible_parties = [
            prepared_by,
            prepared_for,
            content_approver,
        ]
        # responsible-roles
        role_prepared_by = ResponsibleRole(role_id='prepared-by', party_uuids=[party_uuid_01])
        role_prepared_for = ResponsibleRole(role_id='prepared-for', party_uuids=[party_uuid_02, party_uuid_03])
        role_content_approver = ResponsibleRole(role_id='content-approver', party_uuids=[party_uuid_01])
        responsible_roles = [
            role_prepared_by,
            role_prepared_for,
            role_content_approver,
        ]
        # process each row of spread sheet
        for row in self._row_generator(work_sheet):
            # quit when first row with no goal_id encountered
            goal_id = self._get_goal_id(work_sheet, row)
            goal_name_id = self._get_goal_name_id(work_sheet, row)
            controls = self._get_controls(work_sheet, row)
            if len(controls.keys()) == 0:
                continue
            scc_check_name_id = str(goal_name_id) + '_check'
            # component
            component_name = self._get_component_name(work_sheet, row)
            if component_name not in component_names:
                component_names.append(component_name)
                component_title = component_name
                component_description = component_name
                defined_component = DefinedComponent(
                    uuid=str(uuid.uuid4()),
                    description=component_description,
                    title=component_title,
                    type='Service',
                )
                defined_components.append(defined_component)
            else:
                for defined_component in defined_components:
                    if component_name == defined_component.title:
                        break
            # parameter
            parameter_name, parameter_description = self._get_parameter_name_and_description(work_sheet, row)
            usage = self._get_parameter_usage(work_sheet, row)
            if parameter_name is not None:
                parameter_name = parameter_name.strip()
                if ' ' in parameter_name:
                    parameter_name = parameter_name.replace(' ', '_')
                    logger.info(f'row={row} edited {parameter_name} to remove whitespace')
                values = self._get_parameter_values(work_sheet, row)
                guidelines = self._get_guidelines(values)
                href = 'http://ibm.github.io/compliance-trestle/schemas/oscal/cd/' + component_name.replace(' ', '%20')
                parameter_helper = ParameterHelper(
                    values=values,
                    id_=parameter_name,
                    label=parameter_description,
                    href=href,
                    usage=usage,
                    guidelines=guidelines,
                )
                parameters[str(uuid.uuid4())] = parameter_helper.get_parameter()
            # implemented requirements
            implemented_requirements = []
            goal_remarks = self._get_goal_remarks(work_sheet, row)
            parameter_value_default = self._get_parameter_value_default(work_sheet, row)
            for control in controls.keys():
                control_uuid = self._get_control_uuid(control)
                prop1 = Property(
                    name='goal_name_id',
                    class_='scc_goal_name_id',
                    value=goal_name_id,
                    ns='http://ibm.github.io/compliance-trestle/schemas/oscal/cd/ibm-cloud',
                    remarks=Remarks(__root__=str(goal_remarks))
                )
                prop2 = Property(
                    name='goal_version',
                    class_='scc_goal_version',
                    value=self._get_goal_version(),
                    ns='http://ibm.github.io/compliance-trestle/schemas/oscal/cd/ibm-cloud',
                    remarks=Remarks(__root__=str(goal_name_id))
                )
                props = [prop1, prop2]
                control_id, status = catalog_helper.find_control_id(control)
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
                # statements
                control_statements = controls[control]
                if len(control_statements) > 0:
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
                # set_parameters
                if parameter_name is None:
                    if row not in self.rows_missing_parameters:
                        self.rows_missing_parameters.append(row)
                else:
                    parameter_name = parameter_name.replace(' ', '_')
                    if parameter_value_default is None:
                        if row not in self.rows_missing_parameters_values:
                            self.rows_missing_parameters_values.append(row)
                    else:
                        values = [parameter_value_default]
                        set_parameter = SetParameter(param_id=parameter_name, values=values)
                        set_parameters = [set_parameter]
                        implemented_requirement.set_parameters = set_parameters
                # implemented_requirements
                implemented_requirements.append(implemented_requirement)
            # control implementations
            control_implementation = ControlImplementation(
                uuid=str(uuid.uuid4()),
                source=
                'https://github.com/usnistgov/oscal-content/blob/master/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json',
                description=component_name +
                ' implemented controls for NIST 800-53. It includes assessment asset configuration for CICD (and tbd runtime SCC)."',
                implemented_requirements=implemented_requirements,
            )
            if defined_component.control_implementations is None:
                defined_component.control_implementations = [control_implementation]
            else:
                defined_component.control_implementations.append(control_implementation)
        # create OSCAL ComponentDefinition
        metadata = Metadata(
            title='Component definition for NIST profiles',
            last_modified=self._timestamp,
            oscal_version=OSCAL_VERSION,
            version=__version__,
            roles=roles,
            parties=parties,
            responsible_parties=responsible_parties
        )
        component_definition = ComponentDefinition(
            uuid=str(uuid.uuid4()),
            metadata=metadata,
            components=defined_components,  #params=parameters,
        )
        # write OSCAL ComponentDefinition to file
        if self._verbose:
            logger.info(f'output: {ofile}')
        component_definition.oscal_write(pathlib.Path(ofile))
        # issues
        if len(self.rows_missing_goal_name_id) > 0:
            logger.info(f'rows missing goal_name_id: {self.rows_missing_goal_name_id}')
        if len(self.rows_missing_controls) > 0:
            logger.info(f'rows missing controls: {self.rows_missing_controls}')
        if len(self.rows_missing_parameters) > 0:
            logger.info(f'rows missing parameters: {self.rows_missing_parameters}')
        if len(self.rows_missing_parameters_values) > 0:
            logger.info(f'rows missing parameters values: {self.rows_missing_parameters_values}')
        # <hack>
        # create a catalog containing the parameters,
        # since parameters are not supported in OSCAL 1.0.0 component definition
        if parameter_helper is not None:
            tdir = self._config.get('output-dir')
            tdir = tdir.replace('component-definitions', 'catalogs')
            tpth = pathlib.Path(tdir)
            tname = 'catalog.json'
            tfile = tpth / tname
            parameter_helper.write_parameters_catalog(
                parameters=parameters,
                timestamp=self._timestamp,
                oscal_version=OSCAL_VERSION,
                version=__version__,
                ofile=tfile,
                verbose=self._verbose,
            )
        #</hack>
        return TaskOutcome('success')

    def _row_generator(self, work_sheet: t_work_sheet) -> t_row:
        """Generate rows until goal_id is None."""
        row = 1
        while True:
            row = row + 1
            goal_id = self._get_goal_id(work_sheet, row)
            if goal_id is None:
                break
            yield row

    def _get_goal_version(self) -> t_goal_version:
        """Fix goal_version at 1.0."""
        return '1.0'

    def _get_control_uuid(self, control) -> t_uuid_str:
        value = str(uuid.uuid4())
        return value

    def _get_goal_id(self, work_sheet: t_work_sheet, row: t_row) -> t_goal_id:
        """Get goal_id from work_sheet."""
        col = 'a'
        value = work_sheet[col + str(row)].value
        return value

    def _get_goal_text(self, work_sheet: t_work_sheet, row: t_row) -> t_goal_text:
        """Get goal_text from work_sheet."""
        col = 'b'
        goal_text = work_sheet[col + str(row)].value
        # normalize & tokenize
        value = goal_text.replace('\t', ' ')
        return value

    def _get_controls(self, work_sheet: t_work_sheet, row: t_row) -> t_controls:
        """Produce dict of controls mapped to statements
        Example: {'au-2': ['(a)', '(d)'], 'au-12': [], 'si-4': ['(a)', '(b)', '(c)']}
        """
        value = {}
        for col in ['ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai']:
            control = work_sheet[col + str(row)].value
            if control is not None:
                # remove blanks
                control = ''.join(control.split())
                if len(control) > 0:
                    if control.lower() == 'none':
                        continue
                    # remove rhs of : inclusive
                    if ':' in control:
                        control = control.split(':')[0]
                    # remove alphabet parts of control & accumulate in statements
                    statements = []
                    for i in ['a',
                              'b',
                              'c',
                              'd',
                              'e',
                              'f',
                              'g',
                              'h',
                              'i',
                              'j',
                              'k',
                              'l',
                              'm',
                              'n',
                              'o'
                              'p',
                              'q',
                              'r',
                              's',
                              't',
                              'u',
                              'v',
                              'w',
                              'x',
                              'y',
                              'z']:
                        needle = '(' + i + ')'
                        if needle in control:
                            statements.append(needle)
                            control = control.replace(needle, '')
                    control = control.lower()
                    # skip bogus control made up if dashes only
                    if len(control.replace('-', '')) == 0:

                        logger.info(f'{row}!!!!!!!!!!!!')

                        continue
                    if control not in value.keys():
                        value[control] = statements
        if len(value.keys()) == 0:
            self.rows_missing_controls.append(row)
        logger.debug(f'row: {row} controls {value}')
        return value

    def _get_goal_name_id(self, work_sheet: t_work_sheet, row: t_row) -> t_goal_name_id:
        """Get goal_name_id from work_sheet."""
        col = 'an'
        value = work_sheet[col + str(row)].value
        if value is None:
            self.rows_missing_goal_name_id.append(row)
            value = self._get_goal_id(work_sheet, row)
        value = str(value).strip()
        return value

    def _get_parameter_name_and_description(self, work_sheet: t_work_sheet, row: t_row) -> (t_name, t_description):
        """Get parameter_name and description from work_sheet."""
        name = None
        description = None
        col = 'ar'
        combined_values = work_sheet[col + str(row)].value
        if combined_values is not None:
            if '\n' in combined_values:
                parameter_parts = combined_values.split('\n')
            elif ' ' in combined_values:
                parameter_parts = combined_values.split(' ', 1)
            else:
                parameter_parts = combined_values
            if len(parameter_parts) != 2:
                raise RuntimeError(f'row {row} col {col} unable to parse')
            name = parameter_parts[1]
            description = parameter_parts[0]
        value = name, description
        return value

    def _get_parameter_value_default(self, work_sheet: t_work_sheet, row: t_row) -> t_parameter_value:
        """Get parameter_value_default from work_sheet."""
        name = None
        description = None
        col = 'as'
        value = work_sheet[col + str(row)].value
        if value is not None:
            value = str(value).split(',')[0].strip()
        return value

    def _get_parameter_values(self, work_sheet: t_work_sheet, row: t_row) -> t_parameter_values:
        """Get parameter_values from work_sheet."""
        name = None
        description = None
        col = 'as'
        value = work_sheet[col + str(row)].value
        if value is None:
            logger.info(f'row {row} col {col} missing value')
        # massage into comma separated list of values
        value = str(value).strip().replace(' ', '')
        value = value.replace(',[]', '')
        value = value.replace('[', '')
        value = value.replace(']', '')
        return value

    def _get_guidelines(self, values: t_values) -> t_guidelines:
        """Get guidelines based on values."""
        type = self._get_type(values)
        value = f'The first listed value option is set by default in the system unless set-parameter is used to satisfy a control requirements. Type {type}.'
        return value

    def _get_type(self, values: t_values) -> t_type:
        """Get type based on values."""
        if self._is_int(values):
            value = 'Integer'
        elif self._is_float(values):
            value = 'Float'
        else:
            value = 'String'
        return value

    def _is_int(self, values: t_values) -> bool:
        """Determine if string represents list of int."""
        try:
            for value in values.split(','):
                int(value)
            retval = True
        except:
            retval = False
        return retval

    def _is_float(self, values: t_values) -> bool:
        """Determine if string represents list of float."""
        try:
            for value in values.split(','):
                float(value)
            retval = True
        except:
            retval = False
        return retval

    def _get_parameter_usage(self, work_sheet: t_work_sheet, row: t_row) -> t_parameter_usage:
        """Get parameter_usage from work_sheet."""
        return self._get_goal_remarks(work_sheet, row)

    def _get_goal_text_tokens(self, work_sheet: t_work_sheet, row: t_row) -> t_tokens:
        """Get goal_text tokens from work_sheet."""
        goal_text = self._get_goal_text(work_sheet, row)
        tokens = goal_text.split()
        return tokens

    def _get_goal_remarks(self, work_sheet: t_work_sheet, row: t_row) -> t_goal_remarks:
        """Get goal_remarks from work_sheet."""
        tokens = self._get_goal_text_tokens(work_sheet, row)
        # replace "Check whether" with "Ensure", if present
        if len(tokens) > 0:
            if tokens[0] == 'Check':
                if len(tokens) > 1:
                    if tokens[1] == 'whether':
                        tokens.pop(0)
                tokens[0] = 'Ensure'
        value = ' '.join(tokens)
        return value

    def _get_component_name(self, work_sheet: t_work_sheet, row: t_row) -> t_component_name:
        """Get component_name from work_sheet."""
        col = 'am'
        value = work_sheet[col + str(row)].value
        if value is None:
            raise RuntimeError(f'row {row} col {col} missing component name')
        return value
