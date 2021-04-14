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
from trestle.oscal.assessment_results import InventoryItem
from trestle.oscal.assessment_results import LocalDefinitions1
from trestle.oscal.assessment_results import Observation
from trestle.oscal.assessment_results import Property
from trestle.oscal.assessment_results import RelatedObservation
from trestle.oscal.assessment_results import Result
from trestle.oscal.assessment_results import ReviewedControls
from trestle.oscal.assessment_results import Status1
from trestle.oscal.assessment_results import SubjectReference as Subject
from trestle.oscal.assessment_results import Type1

logger = logging.getLogger(__name__)

t_analysis = Dict[str, Any]
t_control = str
t_control_selection = ControlSelection
t_finding = Finding
t_inventory = InventoryItem
t_inventory_ref = str
t_ip = str
t_json = str
t_local_definitions = LocalDefinitions1
t_observation = Observation
t_oscal = Union[str, Dict[str, Any]]
t_tanium_row = Dict[str, Any]
t_timestamp = str
t_resource = Dict[str, Any]
t_result = Result
t_reviewed_controls = ReviewedControls

t_inventory_map = Dict[t_ip, t_inventory]
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
        self.ip = tanium_row['IP Address']
        self.computer = tanium_row['Computer Name']
        self.count = tanium_row['Count']
        self.age = tanium_row['Age']
        self.benchmark = tanium_row[key_comply][0]['Benchmark']
        self.benchmark_version = tanium_row[key_comply][0]['Benchmark Version']
        self.profile = tanium_row[key_comply][0]['Profile']
        self.id = tanium_row[key_comply][0]['ID']
        self.result = tanium_row[key_comply][0]['Result']
        self.custom_id = tanium_row[key_comply][0]['Custom ID']
        self.version = tanium_row[key_comply][0]['Version']
        self.time = tanium_row[key_comply][0].get('Timestamp', default_timestamp)
        # if no control, then control is rule
        if len(self.custom_id) == 0:
            self.custom_id = self.id
        if '-' in self.profile:
            self.profile_catalog = self.profile.split('-', 1)[1].strip()
            self.profile_segment = self.profile.split('-', 1)[0].strip()
        else:
            self.profile_catalog = 'N/A'
            self.profile_segment = 'N/A'
        if ' ' in self.custom_id:
            self.id_ref = self.custom_id.split()[1].strip()
        else:
            self.id_ref = self.custom_id


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
        self.inventory_map: t_inventory_map = {}
        self.observation_list: t_observation_list = []
        self.findings_map: t_findings_map = {}
        self.results_map: t_findings_map = {}

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
            for rule in self.findings_map[control].keys():
                for rule_use in self.findings_map[control][rule]:
                    if rule_use.result not in self.results_map.keys():
                        self.results_map[rule_use.result] = 0
                    self.results_map[rule_use.result] += 1
                    profile_catalog = rule_use.profile_catalog
                    id_ref = rule_use.id_ref
                    related_observations.append(RelatedObservation(observation_uuid=rule_use.observation.uuid))
                    aggregate = self._aggregator(control, aggregate, rule_use.result)
                    logger.debug(f'{control} {rule} {rule_use.result} {aggregate}')
            if aggregate == 'PASS':
                status = Status1.satisfied
            else:
                status = Status1.not_satisfied
            logger.debug(f'{control} {status} {aggregate}')

            finding_type = Type1('objective-id')
            id_ref = control
            finding_target = FindingTarget(type=finding_type, id_ref=id_ref, status=status)
            props = [
                Property(name='profile', value=profile_catalog, ns='dns://tanium', class_='source'),
                Property(name='id-ref', value=id_ref, ns='dns://tanium', class_='source'),
                Property(name='result', value=aggregate, ns='dns://xccdf', class_='STRVALUE')
            ]
            finding_target.props = props
            finding.target = finding_target
            finding.related_observations = related_observations
        return prop

    @property
    def local_definitions(self) -> t_local_definitions:
        """OSCAL local definitions."""
        prop = LocalDefinitions1()
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
            reviewed_controls=self.reviewed_controls,
            findings=self.findings,
            local_definitions=self.local_definitions,
            observations=self.observations
        )
        return prop

    @property
    def analysis(self) -> List[str]:
        """OSCAL statistics."""
        analysis = []
        analysis.append(f'inventory: {len(self.inventory)}')
        analysis.append(f'observations: {len(self.observations)}')
        analysis.append(f'findings: {len(self.findings_map)}')
        analysis.append(f'results: {self.results_map}')
        return analysis

    def _get_inventroy_ref(self, ip: t_ip) -> t_inventory_ref:
        """Get inventory reference for specified IP."""
        return self.inventory_map[ip].uuid

    def _inventory_extract(self, rule_use: RuleUse) -> None:
        """Extract inventory from Tanium row."""
        if rule_use.ip not in self.inventory_map.keys():
            inventory = InventoryItem(uuid=str(uuid.uuid4()), description='inventory')
            inventory.props = [
                Property(name='computer-name', value=rule_use.computer, ns='dns://tanium', class_=' inventory-item'),
                Property(name='computer-ip', value=rule_use.ip, ns='dns://tanium', class_=' inventory-item'),
                Property(name='profile', value=rule_use.profile_segment, ns='dns://tanium', class_=' inventory-item'),
            ]
            self.inventory_map[rule_use.ip] = inventory
        rule_use.inventory = self.inventory_map[rule_use.ip]

    def _observation_extract(self, rule_use: RuleUse) -> None:
        """Extract observation from Tanium row."""
        observation = Observation(
            uuid=str(uuid.uuid4()), description=rule_use.id, methods=['TEST-AUTOMATED'], collected=rule_use.time
        )
        subject = Subject(uuid_ref=self._get_inventroy_ref(rule_use.ip), type='inventory-item')
        observation.subjects = [subject]
        if rule_use.id.startswith('xccdf'):
            ns = 'dns://xccdf'
        else:
            ns = 'dns://tanium'
        props = [
            Property(name='benchmark', value=rule_use.benchmark, ns='dns://tanium', class_='source'),
            Property(name='rule', value=rule_use.id, ns=ns, class_='id'),
            Property(name='result', value=rule_use.result, ns=ns, class_='result'),
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

    def ingest(self, tanium: t_tanium_row) -> None:
        """Process one row of Tanium."""
        rule_use = RuleUse(tanium, ResultsMgr.timestamp)
        self._inventory_extract(rule_use)
        self._observation_extract(rule_use)
        self._finding_extract(rule_use)
