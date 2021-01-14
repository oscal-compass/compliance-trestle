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
"""Facilitate OpenShift Compliance Operator yaml to OSCAL json transformation."""

import base64
import bz2
import logging
import uuid
from typing import Any, Dict, List, Union
from xml.etree import ElementTree

from trestle.oscal.assessment_results import Observation
from trestle.oscal.assessment_results import Property
from trestle.oscal.assessment_results import RelevantEvidence
from trestle.oscal.assessment_results import Subject
from trestle.oscal.assessment_results_partial import AssessmentResultsPartial

logger = logging.getLogger(__name__)


def get_observations(idata: Dict, oscal_metadata: Dict) -> (AssessmentResultsPartial, Dict):
    """
    Transform OSCO yaml to NIST OSCAL json with statistics.

    Required ```idata``` is dict representation of OSCO yaml.
    Optional ```oscal_metadata``` helps more completely formulate each observation.

    Returned ```odata``` comprises list of OSCAL-like Assessment Results observations.
    Returned ```analysis``` comprises dict of statistics.
    """
    rules = Rules(idata)
    return _get_observations(rules, oscal_metadata)


def _get_observations(rules: Dict, oscal_metadata: Dict) -> (AssessmentResultsPartial, Dict):
    """Produce an OSCAL-like partial results object comprising a collection of Observations."""
    observation_list = []
    for rule in rules.instances:
        observation = _get_observation(rule, oscal_metadata)
        observation_list.append(observation)
    external_data = {
        'observations': observation_list,
    }
    value = AssessmentResultsPartial(**external_data)
    logger.debug(f'_get_observations: {value}')
    return value, rules.analysis


def _get_observation(rule: Dict, oscal_metadata: Dict) -> Observation:
    """Produce one Observation."""
    external_data = {}
    external_data['uuid'] = str(uuid.uuid4())
    external_data['description'] = rule['idref']
    external_data['title'] = rule['idref']
    external_data['relevant-evidence'] = _get_relevant_evidence(rule, oscal_metadata)
    external_data['subjects'] = _get_subjects(rule, oscal_metadata)
    external_data['methods'] = ['TEST-AUTOMATED']
    if len(external_data['subjects']) == 0:
        del external_data['subjects']
    value = Observation(**external_data)
    logger.debug(f'_get_observation: {value}')
    return value


def _get_relevant_evidence(rule: Dict, oscal_metadata: Dict) -> List[RelevantEvidence]:
    """Produce one RelecentEvidence for the specified rule."""
    external_data = {}
    external_data['description'] = 'Evidence location.'
    name = rule['name']
    entry = _get_entry(oscal_metadata, name)
    ns = None
    if entry is not None:
        if 'locker' in entry:
            external_data['href'] = entry['locker']
        if 'namespace' in entry:
            ns = entry['namespace']
    p1 = _get_property(ns, 'id', 'rule', rule['idref'])
    p2 = _get_property(ns, 'timestamp', 'time', rule['time'])
    p3 = _get_property(ns, 'result', 'result', rule['result_type'])
    p4 = _get_property(ns, 'target', 'target', rule['target'])
    external_data['props'] = [p1, p2, p3, p4]
    value = [RelevantEvidence(**external_data)]
    logger.debug(f'_get_relevant_evidence: {value}')
    return value


def _get_subjects(rule: Dict, oscal_metadata: Dict) -> List[Subject]:
    """Produce one list of Subjects for the specified rule."""
    value = []
    name = rule['name']
    entry = _get_entry(oscal_metadata, name)
    if entry is not None:
        if 'subject-references' in entry:
            subject_references = entry['subject-references']
            if 'component' in subject_references:
                subject = subject_references['component']
                _add_subject(value, subject)
            if 'inventory-item' in subject_references:
                subject = subject_references['inventory-item']
                _add_subject(value, subject)
    logger.debug(f'_get_subjects: {value}')
    return value


def _add_subject(subject_list: List, subject: Dict) -> None:
    """Add one Subject to the list."""
    external_data = {}
    external_data['uuid-ref'] = subject['uuid-ref']
    external_data['type'] = subject['type']
    if 'title' in subject:
        external_data['title'] = subject['title']
    if 'properties' in subject:
        external_data['props'] = []
        properties = subject['properties']
        for name in properties:
            value = properties[name]
            prop = {}
            prop['name'] = name
            prop['value'] = value
            external_data['props'].append(prop)
    value = Subject(**external_data)
    subject_list.append(value)


def _get_property(ns: str, classification: str, name: str, value: str) -> Property:
    """Produce one property."""
    external_data = {}
    if ns is not None:
        external_data['ns'] = 'dns://' + ns
    if classification is not None:
        external_data['class'] = classification
    external_data['name'] = name
    external_data['value'] = value
    value = Property(**external_data)
    logger.debug(f'_get_property: {value}')
    return value


def _get_entry(oscal_metadata: Dict, name: str) -> Union[Dict, None]:
    """Find and return the entry in the metadata for the specified name, if any."""
    value = None
    if oscal_metadata is not None:
        if name in oscal_metadata:
            value = oscal_metadata[name]
    logger.debug(f'_get_entry: {value}')
    return value


class Rules():
    """Create and accumulate list of rule + result pairs with associated metadata."""

    def __init__(self, content: Dict) -> Any:
        """Initialize given specified args."""
        # List of extracted rules.
        self._instances = []
        # List of unique config_maps.
        self._config_maps = []
        # Dict of unique result types.
        self._result_types = {}
        # Dict of benchmark for this set of rules.
        self._benchmark = {}
        # Dict of metadata for this set of rules.
        self._metadata = {}
        # Dict of raw data to be processed.
        self._content = content
        # Perform rules extraction.
        self._extract_rules()

    @property
    def instances(self) -> List:
        """Get the list of rules."""
        return self._instances

    @property
    def benchmark(self) -> Dict:
        """Get the benchmark info."""
        return self._benchmark

    @property
    def metadata(self) -> Dict:
        """Get the metadata info."""
        return self._metadata

    @property
    def analysis(self) -> Dict:
        """Get the analysis info."""
        logger.debug('Rules Analysis:')
        logger.debug(f'config_maps: {self._config_maps}')
        logger.debug(f'dispatched rules: {len(self._instances)}')
        logger.debug(f'result types: {self._result_types}')
        return {
            'config_maps': self._config_maps,
            'dispatched_rules': len(self._instances),
            'result_types': self._result_types
        }

    def _extract_rules(self) -> None:
        """Extract the rules from the input data."""
        while True:
            resource = self._content
            if resource is None:
                logger.debug(f'resource: {resource}')
                break
            if 'kind' not in resource.keys():
                logger.debug('kind: not found')
                break
            if resource['kind'] != 'ConfigMap':
                logger.debug(f'kind: {resource["kind"]}')
                break
            if 'results' not in resource['data']:
                logger.debug('results: not found')
                break
            if 'metadata' not in resource.keys():
                logger.debug('metadata: not found')
                self._metadata['name'] = None
                self._metadata['namespace'] = None
            else:
                self._metadata['name'] = resource['metadata']['name']
                self._metadata['namespace'] = resource['metadata']['namespace']
            results = resource['data']['results']
            if results.startswith('<?xml'):
                pass
            else:
                results = bz2.decompress(base64.b64decode(results))
            logger.debug('========== <results> ==========')
            logger.debug(results)
            logger.debug('========== </results> ==========')
            self._parse_xml(results, self._metadata['name'])
            break

    def _parse_xml(self, results: str, name: str) -> None:
        """Parse the stringified XML."""
        root = ElementTree.fromstring(results)
        target = self._get_target(root)
        config_map = self._get_config_map(root)
        stats = {}
        for lev1 in root:
            tag = _remove_namespace(lev1.tag)
            if tag == 'rule-result':
                idref = lev1.get('idref')
                time = lev1.get('time')
                result = self._get_result(lev1)
                self._post(config_map, idref, time, result, target, name)
                if result not in stats.keys():
                    stats[result] = 0
                stats[result] += 1
            elif tag == 'benchmark':
                self._benchmark['href'] = lev1.get('href')
                self._benchmark['id'] = lev1.get('id')

    def _get_target(self, root: ElementTree.Element) -> str:
        """Extract 'target' info from the XML."""
        target = None
        for lev1 in root:
            tag = _remove_namespace(lev1.tag)
            if tag == 'target':
                target = root.find(lev1.tag).text
                break
        return target

    def _get_config_map(self, root: ElementTree.Element) -> str:
        """Extract 'config_map' info from the XML."""
        retval = ''
        for lev1 in root:
            tag = _remove_namespace(lev1.tag)
            if tag == 'benchmark':
                href = lev1.get('href')
                retval = href.split('.')[0].rsplit('/', 1)[1]
                break
        return retval

    def _get_result(self, lev1: ElementTree.Element) -> str:
        """Extract 'result' info from the XML."""
        result = None
        for lev2 in lev1:
            tag = _remove_namespace(lev2.tag)
            if tag == 'result':
                result = lev1.find(lev2.tag).text
                break
        return result

    def _post(self, config_map: str, idref: str, time: str, result_type: str, target: str, name: str) -> None:
        """Append a rule entry."""
        instance = {}
        instance['config_map'] = config_map
        instance['idref'] = idref
        instance['time'] = time
        instance['result_type'] = result_type
        instance['target'] = target
        instance['name'] = name
        self._instances.append(instance)
        if config_map not in self._config_maps:
            self._config_maps.append(config_map)
        if (result_type not in self._result_types):
            self._result_types[result_type] = 0
        self._result_types[result_type] += 1
        logger.debug(instance)


def _remove_namespace(subject: str) -> str:
    """If a namespace is present in the subject string, remove it."""
    return subject.rsplit('}').pop()
