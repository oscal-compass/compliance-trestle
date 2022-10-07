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
from typing import List, Optional

from trestle.oscal import OSCAL_VERSION
from trestle.oscal.common import Metadata
from trestle.oscal.common import Property
from trestle.oscal.component import ComponentDefinition
from trestle.oscal.component import ControlImplementation
from trestle.oscal.component import DefinedComponent
from trestle.oscal.component import ImplementedRequirement
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome
from trestle.tasks.csv_helper import CsvHelper
from trestle.tasks.csv_helper import get_trestle_version

logger = logging.getLogger(__name__)


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

    def set_timestamp(self, timestamp: str) -> None:
        """Set the timestamp."""
        self._timestamp = timestamp

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
        # build components
        self._build_components()
        # create OSCAL ComponentDefinition
        metadata = Metadata(
            title='Component definition for ' + self._get_catalog_title() + ' profiles',
            last_modified=self._timestamp,
            oscal_version=OSCAL_VERSION,
            version=get_trestle_version(),
        )
        component_definition = ComponentDefinition(
            uuid=str(uuid.uuid4()),
            metadata=metadata,
            components=self._get_components(),
        )
        # write OSCAL ComponentDefinition to file
        if self._verbose:
            logger.info(f'output: {ofile}')
        component_definition.oscal_write(pathlib.Path(ofile))
        logger.info(f'{ofile}')
        # issues
        self._report_issues()
        return TaskOutcome('success')

    def _build_components(self) -> None:
        """Build components."""
        self._components = []
        defined_component = None
        control_implementations = {}
        implemented_requirements = {}
        # defined component
        for row in self.csv_helper.row_generator():
            type_ = self.csv_helper.get_value(row, 'Component_Type')
            title = self.csv_helper.get_value(row, 'Resource')
            description = self.csv_helper.get_value(row, 'Resource')
            defined_component = DefinedComponent(
                uuid=str(uuid.uuid4()),
                type=type_,
                title=title,
                description=description,
                control_implementations=[],
            )
            break
        self._components.append(defined_component)
        # control_implemenations
        for row in self.csv_helper.row_generator():
            control_id = self.csv_helper.get_value(row, 'Control_Mappings')
            source = self.csv_helper.get_value(row, 'Profile_Reference_URL')
            description = self.csv_helper.get_value(row, 'Profile_Description')
            if source not in control_implementations.keys():
                control_implementation = ControlImplementation(
                    uuid=str(uuid.uuid4()),
                    source=source,
                    description=description,
                    implemented_requirements=[],
                )
                control_implementations[source] = control_implementation
                defined_component.control_implementations.append(control_implementation)
        # implemented requirements
        for row in self.csv_helper.row_generator():
            control_id = self.csv_helper.get_value(row, 'Control_Mappings')
            source = self.csv_helper.get_value(row, 'Profile_Reference_URL')
            control_implementation = control_implementations[source]
            implemented_requirement = ImplementedRequirement(
                uuid=str(uuid.uuid4()),
                control_id=control_id,
                description=control_id,
                props=[],
            )
            implemented_requirements[control_id] = implemented_requirement
            control_implementation.implemented_requirements.append(implemented_requirement)
        # rules
        index = 0
        for index, row in enumerate(self.csv_helper.row_generator()):
            control_id = self.csv_helper.get_value(row, 'Control_Mappings')
            implemented_requirement = implemented_requirements[control_id]
            ns = self._ns
            remarks = f'rule_set_{str(index).zfill(3)}'
            # Rule_Id
            name = 'Rule_Id'
            value = self.csv_helper.get_value(row, name)
            prop = Property(
                name=name,
                value=value,
                ns=ns,
                remarks=remarks,
            )
            implemented_requirement.props.append(prop)
            # Rule_Description
            name = 'Rule_Description'
            value = self.csv_helper.get_value(row, name)
            prop = Property(
                name=name,
                value=value,
                ns=ns,
                remarks=remarks,
            )
            implemented_requirement.props.append(prop)

    def _get_catalog_title(self) -> str:
        """Get catalog title."""
        value = 'TBD'
        return value

    def _get_org_name(self) -> str:
        """Get org name."""
        value = 'TBD'
        return value

    def _get_org_remarks(self) -> str:
        """Get org remarks."""
        value = 'TBD'
        return value

    def _get_components(self) -> List[DefinedComponent]:
        """Get components."""
        value = self._components
        return value

    def _report_issues(self) -> None:
        """Report issues."""
        self.csv_helper.report_issues()
