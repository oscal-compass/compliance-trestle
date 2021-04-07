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
"""Facilitate OpenShift Compliance Operator (OSCO) yaml to NIST OSCAL json transformation."""

import base64
import bz2
import json
import logging
import uuid
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

from pydantic import Field

from trestle.core.base_model import OscalBaseModel
from trestle.oscal.assessment_results import Observation
from trestle.oscal.assessment_results import Property
from trestle.oscal.assessment_results import RelevantEvidence
from trestle.oscal.assessment_results import SubjectReference as Subject

logger = logging.getLogger(__name__)

t_analysis = Dict[str, Any]
t_benchmark = Dict[str, str]
t_json = Dict[str, List[Any]]
t_metadata_entry = Dict[Any, Any]
t_metadata = Dict[Any, t_metadata_entry]
t_osco = Dict[str, Any]
t_rule = Dict[str, str]
t_rule_metadata = Dict[str, str]
t_subject = Dict[Any, Any]


class AssessmentResultsPartial(OscalBaseModel):
    """Partial OSCAL Assessments Results comprising Observations only."""

    observations: Optional[List[Observation]] = Field(None, min_items=1)


def get_observations(osco: t_osco,
                     oscal_metadata: Optional[t_metadata] = None) -> (AssessmentResultsPartial, t_analysis):
    """Transform OSCO data to NIST OSCAL with statistics.

    Transforms the given OpenShift Compliance Operator data into OSCAL-like
    Assessment Results Observations. Optional metadata is employed to produce
    enhanced Observations.

    Args:
        osco: OSCO data to be transformed into observations.
        oscal_metadata: helps more completely formulate each observation, if present.

    Returns:
        assessment_results_partial: comprises OSCAL-like Assessment Results observations.
        analysis: comprises statistics about the transformation.
    """
    rules = Rules(osco)
    observation_list = []
    for rule in rules.instances:
        observation = _get_observation(rule, oscal_metadata)
        observation_list.append(observation)
    assessment_results_partial = AssessmentResultsPartial(observations=observation_list)
    logger.debug(f'get_observations: {assessment_results_partial}')
    return assessment_results_partial, rules.analysis


def get_observations_json(osco: t_osco, oscal_metadata: Optional[t_metadata] = None) -> (t_json, t_analysis):
    """Transform OSCO data to NIST OSCAL json with statistics.

    Transforms the given OpenShift Compliance Operator data into OSCAL-like
    Assessment Results observations json. Optional metadata is employed to produce
    enhanced Observations json.

    Args:
        osco: OSCO data to be transformed into observations.
        oscal_metadata: helps more completely formulate each observation, if present.

    Returns:
        assessment_results_partial: comprises OSCAL-like Assessment Results observations json.
        analysis: comprises statistics about the transformation.
    """
    observation_list = []
    arp, analysis = get_observations(osco, oscal_metadata)
    for observation_model in arp.observations:
        observation_json = json.loads(observation_model.json(exclude_none=True, by_alias=True, indent=2))
        observation_list.append(observation_json)
    return {'observations': observation_list}, analysis


def _get_observation(rule: t_rule, oscal_metadata: Optional[t_metadata] = None) -> Observation:
    """Produce one Observation."""
    value = Observation(
        uuid=str(uuid.uuid4()), description=rule['idref'], methods=['TEST-AUTOMATED'], collected=rule['time']
    )
    value.title = rule['idref']
    value.relevant_evidence = _get_relevant_evidence(rule, oscal_metadata)
    subjects = _get_subjects(rule, oscal_metadata)
    if len(subjects) > 0:
        value.subjects = subjects
    props = _get_props(rule, oscal_metadata)
    if len(props) > 0:
        value.props = props
    logger.debug(f'_get_observation: {value}')
    return value


def _get_relevant_evidence(rule: t_rule, oscal_metadata: Optional[t_metadata] = None) -> List[RelevantEvidence]:
    """Produce one RelevantEvidence for the specified rule."""
    description = 'Evidence location.'
    href = None
    name = rule['name']
    entry = _get_entry(name, oscal_metadata)
    ns = None
    if entry is not None:
        if 'locker' in entry:
            href = entry['locker']
        if 'namespace' in entry:
            ns = entry['namespace']
    p1 = _get_property(ns, 'id', 'rule', rule['idref'])
    p2 = _get_property(ns, 'result', 'result', rule['result_type'])
    props = [p1, p2]
    relevant_evidence = RelevantEvidence(description=description, props=props)
    if href is not None:
        relevant_evidence.href = href
    value = [relevant_evidence]
    logger.debug(f'_get_relevant_evidence: {value}')
    return value


def _get_subjects(rule: t_rule, oscal_metadata: Optional[t_metadata] = None) -> List[Subject]:
    """Produce one list of Subjects for the specified rule."""
    value = []
    name = rule['name']
    entry = _get_entry(name, oscal_metadata)
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


def _add_subject(subject_list: List[t_subject], subject: t_subject) -> None:
    """Add one Subject to the list."""
    value = Subject(uuid_ref=subject['uuid-ref'], type=subject['type'])
    if 'title' in subject:
        value.title = subject['title']
    if 'properties' in subject:
        props = []
        properties = subject['properties']
        for name in properties:
            prop = _get_property('osco', 'inventory-item', name, properties[name])
            props.append(prop)
        value.props = props
    subject_list.append(value)


def _get_props(rule: t_rule, oscal_metadata: Optional[t_metadata] = None) -> List[Subject]:
    """Produce one list of Properties for the specified rule."""
    value = []
    name = rule['name']
    entry = _get_entry(name, oscal_metadata)
    if entry is not None:
        if 'benchmark' in entry:
            prop = _get_property('osco', 'source', 'benchmark', entry['benchmark'])
            value.append(prop)
    return value


def _get_property(ns: str, classification: str, name: str, value: str) -> Property:
    """Produce one property."""
    value = Property(name=name, value=value)
    if ns is not None:
        value.ns = 'dns://' + ns
    if classification is not None:
        value.class_ = classification
    logger.debug(f'_get_property: {value}')
    return value


def _get_entry(name: str, oscal_metadata: Optional[t_metadata] = None) -> Optional[t_metadata_entry]:
    """Find and return the entry in the metadata for the specified name, if any."""
    value = None
    if oscal_metadata is not None:
        if name in oscal_metadata:
            value = oscal_metadata[name]
    logger.debug(f'_get_entry: {value}')
    return value


class Rules():
    """Create and accumulate list of rule + result pairs with associated metadata."""

    def __init__(self, content: t_osco) -> None:
        """Initialize given specified args."""
        # List of extracted rules.
        self._instances = []
        # List of unique config_maps.
        self._config_maps = []
        # Dict of unique result types.
        self._result_types = {}
        # Dict of benchmark for this set of rules.
        self._benchmark = {}
        # Dict of ruledata for this set of rules.
        self._rule_metadata = {}
        # Dict of raw data to be processed.
        self._content = content
        # Perform rules extraction.
        self._extract_rules()

    @property
    def instances(self) -> List[t_rule]:
        """Get the list of rules."""
        return self._instances

    @property
    def benchmark(self) -> t_benchmark:
        """Get the benchmark info."""
        return self._benchmark

    @property
    def rule_metadata(self) -> t_rule_metadata:
        """Get the rule metadata info."""
        return self._rule_metadata

    @property
    def analysis(self) -> t_analysis:
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
        resource = self._content
        if resource is None:
            logger.debug(f'resource: {resource}')
            return
        if 'kind' not in resource.keys():
            logger.debug('kind: not found')
            return
        if resource['kind'] != 'ConfigMap':
            logger.debug(f'kind: {resource["kind"]}')
            return
        if 'results' not in resource['data']:
            logger.debug('results: not found')
            return
        if 'metadata' not in resource.keys():
            logger.debug('metadata: not found')
            self._rule_metadata['name'] = None
            self._rule_metadata['namespace'] = None
        else:
            self._rule_metadata['name'] = resource['metadata']['name']
            self._rule_metadata['namespace'] = resource['metadata']['namespace']
        results = resource['data']['results']
        if results.startswith('<?xml'):
            pass
        else:
            results = bz2.decompress(base64.b64decode(results))
        logger.debug('========== <results> ==========')
        logger.debug(results)
        logger.debug('========== </results> ==========')
        self._parse_xml(results, self._rule_metadata['name'])

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
