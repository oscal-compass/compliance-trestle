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
import uuid
from typing import Any, Dict, List, Union, ValuesView

from trestle.oscal.assessment_results import ControlSelection
from trestle.oscal.assessment_results import Finding
from trestle.oscal.assessment_results import FindingTarget
from trestle.oscal.assessment_results import ImplementedComponent
from trestle.oscal.assessment_results import InventoryItem
from trestle.oscal.assessment_results import LocalDefinitions1
from trestle.oscal.assessment_results import Observation
from trestle.oscal.assessment_results import Property
from trestle.oscal.assessment_results import RelatedObservation
from trestle.oscal.assessment_results import Result
from trestle.oscal.assessment_results import ReviewedControls
from trestle.oscal.assessment_results import Status
from trestle.oscal.assessment_results import Status1
from trestle.oscal.assessment_results import SubjectReference
from trestle.oscal.assessment_results import SystemComponent
from trestle.oscal.assessment_results import Type1

logger = logging.getLogger(__name__)

t_analysis = Dict[str, Any]
t_component = SystemComponent
t_component_ref = str
t_computer_name = str
t_control = str
t_control_selection = ControlSelection
t_finding = Finding
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
t_findings_map = Dict[t_control, Any]
t_results_map = Dict[str, Any]


class RuleUse():
    """Represents one row of Tanium data."""

    def __init__(self, tanium_row: t_tanium_row, default_timestamp: t_timestamp) -> None:
        """Initialize given specified args."""
        logger.debug(f'tanium-row: {tanium_row}')
        keys = tanium_row.keys()
        for key in keys:
            if key.startswith('Comply'):
                key_comply = key
                break
        self.ip_address = tanium_row['IP Address']
        self.computer_name = tanium_row['Computer Name']
        self.count = tanium_row['Count']
        self.age = tanium_row['Age']
        self.benchmark = tanium_row[key_comply][0]['Benchmark']
        self.benchmark_version = tanium_row[key_comply][0]['Benchmark Version']
        self.profile = tanium_row[key_comply][0]['Profile']
        self.id = tanium_row[key_comply][0]['ID']
        self.result = tanium_row[key_comply][0]['Result']
        self.custom_id = tanium_row[key_comply][0]['Custom ID']
        self.version = tanium_row[key_comply][0]['Version']
        self.timestamp = tanium_row[key_comply][0].get('Timestamp', default_timestamp)
        self.collected = tanium_row[key_comply][0].get('Collected', default_timestamp)
        # if no control, then control is rule
        if len(self.custom_id) == 0:
            self.custom_id = self.id


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
        self.findings_map: t_findings_map = {}
        self.inventory_map: t_inventory_map = {}
        self.results_map: t_results_map = {}
        self.ns = 'http://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium'
        # pocket used to set aside "dirty" entries (missing computer-name) for later patching-up
        self.pocket = []
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
        return self.component_map

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

    def _normalize(self, value: str) -> str:
        """Normalize result value."""
        result = None
        if value is not None:
            result = value.upper()
            if result not in ['PASS', 'FAIL']:
                result = 'ERROR'
        return result

    def _aggregator(self, control, prev: str, curr: str) -> str:
        """Aggregate an overall result.

        If any FAIL then FAIL
        else if any ERROR then ERROR
        else any not PASS then ERROR
        else PASS
        """
        result = 'ERROR'
        nprev = self._normalize(prev)
        ncurr = self._normalize(curr)
        if nprev is None:
            result = ncurr
        elif 'FAIL' in [nprev, ncurr]:
            result = 'FAIL'
        elif 'ERROR' in [nprev, ncurr]:
            result = 'ERROR'
        elif nprev == 'PASS' and ncurr == 'PASS':
            result = 'PASS'
        logger.debug(f'{control} {result} {prev} {curr}')
        return result

    @property
    def findings(self) -> List[t_finding]:
        """OSCAL findings."""
        prop = []
        for control in self.findings_map.keys():
            related_observations = []
            finding = Finding(uuid=str(uuid.uuid4()), title=control, description=control)
            prop.append(finding)
            aggregate = None
            version = None
            for rule in self.findings_map[control].keys():
                for rule_use in self.findings_map[control][rule]:
                    version = rule_use.version
                    if rule_use.result not in self.results_map.keys():
                        self.results_map[rule_use.result] = 0
                    self.results_map[rule_use.result] += 1
                    profile = rule_use.profile
                    related_observations.append(RelatedObservation(observation_uuid=rule_use.observation.uuid))
                    aggregate = self._aggregator(control, aggregate, rule_use.result)
                    logger.debug(f'{control} {rule} {rule_use.result} {aggregate}')
            if aggregate == 'PASS':
                status = Status1.satisfied
            else:
                status = Status1.not_satisfied
            logger.debug(f'{control} {status} {aggregate}')

            finding_type = Type1('statement-id')
            finding_target = FindingTarget(type=finding_type, id_ref=control, status=status)
            props = [
                Property(name='Profile', value=profile, ns=self.ns, class_='scc_predefined_profile'),
                Property(name='Custom ID', value=control, ns=self.ns),
                Property(name='Version', value=version, ns=self.ns, class_='scc_mapping_version'),
            ]
            finding_target.props = props
            finding.target = finding_target
            finding.related_observations = related_observations
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
            findings=self.findings,
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
        analysis.append(f'findings: {len(self.findings_map)}')
        analysis.append(f'results: {self.results_map}')
        return analysis

    def _get_inventory_ref(self, computer_name: t_computer_name) -> t_inventory_ref:
        """Get inventory reference for specified computer name."""
        return self.inventory_map[computer_name].uuid

    def _component_extract(self, rule_use: RuleUse) -> None:
        """Extract component from Tanium row."""
        component_type = rule_use.profile.split('-')[0].strip()
        component_title = component_type
        component_description = component_type
        if len(component_type) == 0:
            logger.debug(f'component extract: skip profile: {rule_use.profile}')
            return
        for component_ref in self.component_map.keys():
            component = self.component_map[component_ref]
            if component.type == component_type:
                if component.title == component_title:
                    if component.description == component_description:
                        return
        component_ref = str(uuid.uuid4())
        status = Status(state='operational')
        component = SystemComponent(
            type=component_type, title=component_title, description=component_description, status=status
        )
        self.component_map[component_ref] = component

    def _get_component_ref(self, rule_use: RuleUse) -> t_component_ref:
        uuid = None
        component_type = rule_use.profile.split('-')[0].strip()
        component_title = component_type
        component_description = component_type
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
        if rule_use.computer_name in self.inventory_map.keys():
            inventory = self.inventory_map[rule_use.computer_name]
            for prop in inventory.props:
                if prop.name == 'IP Address':
                    if rule_use.ip_address not in prop.value:
                        prop.value += ', ' + rule_use.ip_address
                    break
        else:
            inventory = InventoryItem(uuid=str(uuid.uuid4()), description='inventory')
            props = []
            props.append(
                Property(
                    name='Computer Name', value=rule_use.computer_name, ns=self.ns, class_='scc_inventory_item_id'
                )
            )
            props.append(Property(name='IP Address', value=rule_use.ip_address, ns=self.ns))
            props.append(Property(name='Count', value=rule_use.count, ns=self.ns))
            props.append(Property(name='Age', value=rule_use.age, ns=self.ns))
            inventory.props = props
            inventory.implemented_components = [ImplementedComponent(component_uuid=self._get_component_ref(rule_use))]
            self.inventory_map[rule_use.computer_name] = inventory

    def _observation_extract(self, rule_use: RuleUse) -> None:
        """Extract observation from Tanium row."""
        observation = Observation(
            uuid=str(uuid.uuid4()), description=rule_use.id, methods=['TEST-AUTOMATED'], collected=rule_use.collected
        )
        subject_reference = SubjectReference(
            uuid_ref=self._get_inventory_ref(rule_use.computer_name), type='inventory-item'
        )
        observation.subjects = [subject_reference]
        props = [
            Property(name='Benchmark', value=rule_use.benchmark, ns=self.ns, class_='scc_predefined_profile'),
            Property(name='Benchmark Version', value=rule_use.benchmark_version, ns=self.ns, class_='scc_goal_version'),
            Property(name='ID', value=rule_use.id, ns=self.ns, class_='scc_goal_name_id'),
            Property(name='Result', value=rule_use.result, ns=self.ns, class_='scc_result'),
            Property(name='Timestamp', value=rule_use.timestamp, ns=self.ns, class_='scc_timestamp'),
        ]
        observation.props = props
        self.observation_list.append(observation)
        rule_use.observation = observation

    def _finding_extract(self, rule_use: RuleUse) -> None:
        """Extract finding from Tanium row."""
        control = rule_use.custom_id
        if control not in self.findings_map.keys():
            self.findings_map[control] = {}
        rule = rule_use.id
        if rule not in self.findings_map[control].keys():
            self.findings_map[control][rule] = []
        self.findings_map[control][rule].append(rule_use)

    def _process(self, rule_use: RuleUse) -> None:
        self._component_extract(rule_use)
        self._inventory_extract(rule_use)
        self._observation_extract(rule_use)
        self._finding_extract(rule_use)

    def ingest(self, tanium_row: t_tanium_row) -> None:
        """Process one row of Tanium."""
        rule_use = RuleUse(tanium_row, ResultsMgr.timestamp)
        if ' ' in rule_use.custom_id:
            control = rule_use.custom_id.split(' ')[1]
        else:
            control = rule_use.custom_id
        if control not in self.control_list:
            self.control_list.append(control)
        if len(rule_use.computer_name.strip()) == 0:
            # set aside rule_use with missing computer-name
            self.pocket.append(rule_use)
        else:
            # process current rule_use
            self._process(rule_use)
            self.map_ip_address_to_computer_name[rule_use.ip_address] = rule_use.computer_name
            # fix up the set aside rule_uses by adding computer-name, then process
            removals = []
            for pocket_rule_use in self.pocket:
                if pocket_rule_use.ip_address in self.map_ip_address_to_computer_name:
                    # ip-address now has computer-name, so process
                    pocket_rule_use.computer_name = self.map_ip_address_to_computer_name[pocket_rule_use.ip_address]
                    logger.debug(f'fix: {rule_use.ip_address} -> {rule_use.computer_name}')
                    self._process(pocket_rule_use)
                    removals.append(pocket_rule_use)
            for pocket_rule_use in removals:
                self.pocket.remove(pocket_rule_use)
