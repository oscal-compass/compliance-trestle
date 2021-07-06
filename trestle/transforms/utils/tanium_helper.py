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
"""Facilitate Tanium report to NIST OSCAL json transformation."""

import datetime
import logging
import traceback
import uuid
from typing import Any, Dict, List, Union, ValuesView

from trestle.oscal.assessment_results import ControlSelection
from trestle.oscal.assessment_results import LocalDefinitions1
from trestle.oscal.assessment_results import Observation
from trestle.oscal.assessment_results import Result
from trestle.oscal.assessment_results import ReviewedControls
from trestle.oscal.assessment_results import Status1
from trestle.oscal.assessment_results import SystemComponent
from trestle.oscal.common import ImplementedComponent, InventoryItem, Property, SubjectReference

logger = logging.getLogger(__name__)

t_analysis = Dict[str, Any]
t_component = SystemComponent
t_component_ref = str
t_computer_name = str
t_control = str
t_control_selection = ControlSelection
t_inventory = InventoryItem
t_inventory_ref = str
t_local_definitions = LocalDefinitions1
t_observation = Observation
t_oscal = Union[str, Dict[str, Any]]
t_tanium_collection = Any
t_tanium_row = Dict[str, Any]
t_timestamp = str
t_resource = Dict[str, Any]
t_result = Result
t_reviewed_controls = ReviewedControls

t_component_map = Dict[t_component_ref, t_component]
t_inventory_map = Dict[t_computer_name, t_inventory]
t_observation_list = List[Observation]


class RuleUse():
    """Represents one row of Tanium data."""

    def __init__(self, tanium_row: t_tanium_row, comply, default_timestamp: t_timestamp) -> None:
        """Initialize given specified args."""
        logger.debug(f'tanium-row: {tanium_row}')
        try:
            # level 1 keys
            self.computer_name = tanium_row['Computer Name']
            self.tanium_client_ip_address = tanium_row['Tanium Client IP Address']
            self.ip_address = str(tanium_row['IP Address'])
            self.count = str(tanium_row['Count'])
            # comply keys
            self.check_id = comply['Check ID']
            self.rule_id = comply['Rule ID']
            self.state = comply['State']
            #
            self.check_id_level = '[no results]'
            self.check_id_version = '[no results]'
            self.check_id_benchmark = '[no results]'
            self.component = '[no results]'
            self.component_type = '[no results]'
            #
            if ';' in self.check_id:
                items = self.check_id.split(';')
                if len(items) > 2:
                    self.check_id_level = items[2]
                if len(items) > 1:
                    self.check_id_version = items[1]
                if len(items) > 0:
                    self.check_id_benchmark = items[0]
                    self.component = items[0]
                    if self.component.startswith('CIS '):
                        self.component = self.component[len('CIS '):]
                    if self.component.endswith(' Benchmark'):
                        self.component = self.component[:-len(' Benchmark')]
                    self.component_type = 'Operating System'
            #
            self.timestamp = comply.get('Timestamp', default_timestamp)
            #
            self.collected = default_timestamp
        except Exception as e:
            logger.debug(f'tanium-row: {tanium_row}')
            logger.debug(e)
            logger.debug(traceback.format_exc())
            raise e
        return


class ResultsMgr():
    """Represents collection of data to transformed into an AssessmentResult.results."""

    # the current time for consistent timestamping
    timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc).isoformat()

    @staticmethod
    def set_timestamp(value: str) -> None:
        """Set the default timestamp value."""
        datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        ResultsMgr.timestamp = value

    @staticmethod
    def get_timestamp() -> str:
        """Get the default timestamp value."""
        return ResultsMgr.timestamp

    def __init__(self) -> None:
        """Initialize."""
        self.observation_list: t_observation_list = []
        self.component_map: t_component_map = {}
        self.inventory_map: t_inventory_map = {}
        self.ns = 'http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium'
        # track ip-address to computer-name
        self.map_ip_address_to_computer_name = {}
        # list of controls
        self.control_list = []

    @property
    def controls(self) -> t_component_map:
        """OSCAL controls."""
        return sorted(self.control_list)

    @property
    def components(self) -> t_component_map:
        """OSCAL components."""
        return list(self.component_map.values())

    @property
    def inventory(self) -> ValuesView[InventoryItem]:
        """OSCAL inventory."""
        return self.inventory_map.values()

    @property
    def observations(self) -> List[t_observation]:
        """OSCAL observations."""
        return self.observation_list

    @property
    def control_selections(self) -> List[t_control_selection]:
        """OSCAL control selections."""
        prop = []
        prop.append(ControlSelection())
        return prop

    @property
    def local_definitions(self) -> t_local_definitions:
        """OSCAL local definitions."""
        prop = LocalDefinitions1()
        prop.components = self.components
        prop.inventory_items = list(self.inventory)
        return prop

    @property
    def reviewed_controls(self) -> t_reviewed_controls:
        """OSCAL reviewed controls."""
        prop = ReviewedControls(control_selections=self.control_selections)
        return prop

    @property
    def result(self) -> t_result:
        """OSCAL result."""
        prop = Result(
            uuid=str(uuid.uuid4()),
            title='Tanium',
            description='Tanium',
            start=ResultsMgr.timestamp,
            end=ResultsMgr.timestamp,
            reviewed_controls=self.reviewed_controls,
            local_definitions=self.local_definitions,
            observations=self.observations
        )
        return prop

    @property
    def analysis(self) -> List[str]:
        """OSCAL statistics."""
        logger.debug(f'controls: {self.controls}')
        analysis = []
        analysis.append(f'inventory: {len(self.inventory)}')
        analysis.append(f'observations: {len(self.observations)}')
        return analysis

    def _get_inventory_ref(self, rule_use: RuleUse) -> t_inventory_ref:
        """Get inventory reference for specified rule use."""
        return self.inventory_map[rule_use.tanium_client_ip_address].uuid

    def _component_extract(self, rule_use: RuleUse) -> None:
        """Extract component from Tanium row."""
        component_type = rule_use.component_type
        component_title = rule_use.component
        component_description = rule_use.component
        for component_ref in self.component_map.keys():
            component = self.component_map[component_ref]
            if component.type == component_type:
                if component.title == component_title:
                    if component.description == component_description:
                        return
        component_ref = str(uuid.uuid4())
        status = Status1(state='operational')
        component = SystemComponent(
            uuid=component_ref,
            type=component_type,
            title=component_title,
            description=component_description,
            status=status
        )
        self.component_map[component_ref] = component

    def _get_component_ref(self, rule_use: RuleUse) -> t_component_ref:
        """Get component reference for specified rule use."""
        uuid = None
        component_type = rule_use.component_type
        component_title = rule_use.component
        component_description = rule_use.component
        for component_ref in self.component_map.keys():
            component = self.component_map[component_ref]
            if component.type == component_type:
                if component.title == component_title:
                    if component.description == component_description:
                        uuid = component_ref
                        break
        return uuid

    def _inventory_extract(self, rule_use: RuleUse) -> None:
        """Extract inventory from Tanium row."""
        if rule_use.tanium_client_ip_address in self.inventory_map.keys():
            pass
        else:
            inventory = InventoryItem(uuid=str(uuid.uuid4()), description='inventory')
            props = []
            props.append(Property(name='Computer_Name', value=rule_use.computer_name, ns=self.ns))
            props.append(
                Property(
                    name='Tanium_Client_IP_Address',
                    value=rule_use.tanium_client_ip_address,
                    ns=self.ns,
                    class_='scc_inventory_item_id'
                )
            )
            props.append(Property(name='IP_Address', value=rule_use.ip_address, ns=self.ns))
            props.append(Property(name='Count', value=rule_use.count, ns=self.ns))
            inventory.props = props
            inventory.implemented_components = [ImplementedComponent(component_uuid=self._get_component_ref(rule_use))]
            self.inventory_map[rule_use.tanium_client_ip_address] = inventory

    def _observation_extract(self, rule_use: RuleUse) -> None:
        """Extract observation from Tanium row."""
        observation = Observation(
            uuid=str(uuid.uuid4()),
            description=rule_use.rule_id,
            methods=['TEST-AUTOMATED'],
            collected=rule_use.collected
        )
        subject_reference = SubjectReference(subject_uuid=self._get_inventory_ref(rule_use), type='inventory-item')
        observation.subjects = [subject_reference]
        props = [
            Property(name='Check_ID', value=rule_use.check_id, ns=self.ns),
            Property(
                name='Check_ID_Benchmark',
                value=rule_use.check_id_benchmark,
                ns=self.ns,
                class_='scc_predefined_profile'
            ),
            Property(
                name='Check_ID_Version',
                value=rule_use.check_id_version,
                ns=self.ns,
                class_='scc_predefined_profile_version'
            ),
            Property(name='Check_ID_Level', value=rule_use.check_id_level, ns=self.ns),
            Property(name='Rule_ID', value=rule_use.rule_id, ns=self.ns, class_='scc_goal_description'),
            Property(name='Rule_ID', value=rule_use.rule_id, ns=self.ns, class_='scc_check_name_id'),
            Property(name='State', value=rule_use.state, ns=self.ns, class_='scc_result'),
            Property(name='Timestamp', value=rule_use.timestamp, ns=self.ns, class_='scc_timestamp'),
        ]
        observation.props = props
        self.observation_list.append(observation)
        rule_use.observation = observation

    def _process(self, rule_use: RuleUse) -> None:
        self._component_extract(rule_use)
        self._inventory_extract(rule_use)
        self._observation_extract(rule_use)

    def ingest(self, tanium_row: t_tanium_row) -> None:
        """Process one row of Tanium."""
        keys = tanium_row.keys()
        for key in keys:
            if key.startswith('Comply'):
                break
        comply_list = tanium_row[key]
        for comply in comply_list:
            rule_use = RuleUse(tanium_row, comply, ResultsMgr.timestamp)
            self._process(rule_use)
