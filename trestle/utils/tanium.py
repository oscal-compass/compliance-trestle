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
import json
import logging
import uuid
from typing import Any, Dict, List, Tuple, Union

from trestle.oscal.assessment_results import Observation
from trestle.oscal.assessment_results import Property
from trestle.oscal.assessment_results import RelevantEvidence

logger = logging.getLogger(__name__)

t_analysis = Dict[str, Any]
t_oscal = Union[str, Dict[str, Any]]
t_tanium = Dict[str, Any]
t_resource = Dict[str, Any]


def get_observations(tanium: t_tanium, fmt: str = 'object') -> Tuple[t_oscal, t_analysis]:
    """Transform Tanium data to NIST OSCAL with statistics.

    Transforms the given Tanium data into OSCAL-like Assessment Results Observations.

    Args:
        tanuim: Tanium data to be transformed into observations.
        fmt: specify return value format, one of ['object', 'json']

    Returns:
        observations: comprises OSCAL-like Assessment Results observations.
        analysis: comprises statistics about the transformation.
    """
    observations = []
    rules = Rules(tanium)
    for rule in rules.list_all:
        observation = Observation(uuid=str(uuid.uuid4()), description=rule.id, methods=['TEST-AUTOMATED'])
        observation.title = rule.id
        description = rule.benchmark + ', version ' + rule.benchmark_version
        ns = None
        # intuit namespace
        if rule.id.startswith('xccdf'):
            ns = 'dns://xccdf'
        props = [
            Property(name='rule', value=rule.id, ns=ns, class_='id'),
            Property(name='result', value=rule.result, ns=ns, class_='result'),
            Property(name='time', value=rule.time, ns=ns, class_='timestamp'),
            Property(name='target', value=rule.computer, ns=ns, class_='computer-name'),
            Property(name='target', value=rule.ip, ns=ns, class_='computer-ip'),
        ]
        relevant_evidence = RelevantEvidence(description=description, props=props)
        observation.relevant_evidence = [relevant_evidence]
        observations.append(observation)
    if fmt == 'json':
        observations = _to_json(observations)
    return observations, rules.analysis


def _to_json(observations: List[Observation]) -> str:
    """Convert observation object list into json string."""
    observation_list = []
    for observation_model in observations:
        observation_json = json.loads(observation_model.json(exclude_none=True, by_alias=True, indent=2))
        observation_list.append(observation_json)
    observation_dict = json.dumps({'observations': observation_list}, indent=2)
    return observation_dict


class Rule():
    """Container for one rule + result with associated metadata."""

    default_timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc
                                                                                  ).isoformat()

    @staticmethod
    def set_default_timestamp(value: str) -> None:
        """Set the default timestamp value."""
        datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
        Rule.default_timestamp = value

    @staticmethod
    def get_default_timestamp() -> str:
        """Get the default timestamp value."""
        return Rule.default_timestamp

    def __init__(self, raw_resource: t_resource) -> None:
        """Initialize given specified args."""
        logger.debug(f'raw: {raw_resource}')
        keys = raw_resource.keys()
        for key in keys:
            if key.startswith('Comply'):
                key_comply = key
                break
        self.ip = raw_resource['IP Address']
        self.computer = raw_resource['Computer Name']
        self.count = raw_resource['Count']
        self.age = raw_resource['Age']
        self.benchmark = raw_resource[key_comply][0]['Benchmark']
        self.benchmark_version = raw_resource[key_comply][0]['Benchmark Version']
        self.profile = raw_resource[key_comply][0]['Profile']
        self.id = raw_resource[key_comply][0]['ID']
        self.result = raw_resource[key_comply][0]['Result']
        self.custom_id = raw_resource[key_comply][0]['Custom ID']
        self.version = raw_resource[key_comply][0]['Version']
        self.time = raw_resource[key_comply][0].get('Timestamp', Rule.default_timestamp)


class Rules():
    """Create and accumulate list of rule + result pairs with associated metadata."""

    def __init__(self, tanium: t_tanium) -> None:
        """Initialize given specified args."""
        # Perform rules extraction.
        self._rule_list = []
        self._unique_rules = []
        self._results = {}
        self._extract_rules(tanium)

    @property
    def list_all(self) -> List[Rule]:
        """Get the list of Rule instances."""
        return self._rule_list

    @property
    def analysis(self) -> t_analysis:
        """Get the analysis info."""
        return {
            'dispatched_rules': len(self._rule_list), 'unique_rules': len(self._unique_rules), 'results': self._results
        }

    def _extract_rules(self, tanium: t_tanium) -> None:
        """Extract the rules from the input data."""
        for raw_resource in tanium:
            resource = Rule(raw_resource)
            logger.debug(f'ip: {resource.ip}')
            logger.debug(f'computer: {resource.computer}')
            logger.debug(f'count: {resource.count}')
            logger.debug(f'age: {resource.age}')
            logger.debug(f'benchmark: {resource.benchmark}')
            logger.debug(f'profile: {resource.profile}')
            logger.debug(f'id: {resource.id}')
            logger.debug(f'result: {resource.result}')
            self._rule_list.append(resource)
            if resource.id not in self._unique_rules:
                self._unique_rules.append(resource.id)
            if resource.result not in self._results.keys():
                self._results[resource.result] = 0
            self._results[resource.result] += 1
        logger.debug(f'rules [dispatched]: {len(self._rule_list)}')
        logger.debug(f'rules [unique]: {len(self._unique_rules)}')
        logger.debug(f'results: {self._results}')
