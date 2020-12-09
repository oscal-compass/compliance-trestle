# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
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
import json
import logging
from uuid import uuid4
from xml.etree import ElementTree

import yaml

logger = logging.getLogger(__name__)


def transform(ifile, ofile, overwrite, metadata):
    """
    Transform ```ifile``` from OSCO yaml to NIST OSCAL json and save as ```ofile```.

    An existing .oscal file is replaced unless the specified value for the
    ```overwrite``` parameter is ```False```.

    Provide optional ```metadata``` to more completely formulate the observations.

    -----
    Sample metadata entry:
    -----
    ssg-ocp4-ds-cis-10.221.139.104-pod:
       subject-references:
          component:
             uuid-ref: 56666738-0f9a-4e38-9aac-c0fad00a5821
             type: component
             title: Red Hat OpenShift Kubernetes
          inventory-item:
             uuid-ref: 46aADFAC-A1fd-4Cf0-a6aA-d1AfAb3e0d3e
             type: inventory-item
             title: Pod
             properties:
                target: kube-br7qsa3d0vceu2so1a90-roksopensca-default-0000026b.iks.ibm
                cluster-name: ROKS-OpenSCAP-1
                cluster-type: openshift
                cluster-region: us-south
    -----
    """
    content = _read_content(ifile)
    rules = Rules(content)
    observations = Observations(rules, metadata)
    output = {'observations': observations.instances}
    _write_content(ofile, output)
    return rules.analysis


def _read_content(ifile):
    with open(ifile, 'r+') as fp:
        data = fp.read()
        content = yaml.full_load(data)
    logger.debug('========== <content> ==========')
    logger.debug(content)
    logger.debug('========== </content> ==========')
    return content


def _write_content(ofile, content):
    with open(ofile, 'w', encoding='utf-8') as fp:
        json.dump(content, fp, ensure_ascii=False, indent=2)


class Observations():
    """Create and accumulate list of OSCAL-like Observations."""

    def __init__(self, rules, metadata):
        """Initialize given specified args."""
        # List of observations.
        self._instances = []
        # Transform each rule+result into an observation.
        for rule in rules.instances:
            observation = self._create_observation(rule, metadata)
            self._instances.append(observation)

    @property
    def instances(self):
        """Get the list of observations."""
        return self._instances

    def _create_observation(self, rule, metadata):
        observation = {}
        observation['uuid'] = str(uuid4())
        observation['description'] = rule['idref']
        observation['title'] = rule['idref']
        observation['evidence-group'] = self._create_evidence_group(rule, metadata)
        subject_references = self._create_subject_references(rule, metadata)
        if subject_references is not None:
            observation['subject-references'] = subject_references
        observation['observation-methods'] = self._create_observation_methods(rule, metadata)
        return observation

    def _create_evidence_group(self, rule, metadata):
        evidence = self._create_evidence(rule, metadata)
        evidence_group = [evidence]
        return evidence_group

    def _create_evidence(self, rule, metadata):
        evidence = {}
        if 'repo-url' in metadata:
            evidence['description'] = 'Evidence location.'
            evidence['href'] = metadata['repo-url']
        if 'ns' in metadata:
            ns = metadata['ns']
        else:
            ns = None
        p1 = self._create_property(ns, 'id', 'rule', rule['idref'])
        p2 = self._create_property(ns, 'timestamp', 'time', rule['time'])
        p3 = self._create_property(ns, 'result', 'result', rule['result_type'])
        p4 = self._create_property(ns, 'target', 'target', rule['target'])
        properties = [p1, p2, p3, p4]
        evidence['properties'] = properties
        return evidence

    def _create_property(self, ns, classification, name, value):
        prop = {}
        if ns is not None:
            prop['ns'] = ns
        prop['class'] = classification
        prop['name'] = name
        prop['value'] = value
        return prop

    def _create_subject_references(self, rule, metadata):
        subject_references = None
        try:
            name = rule['name']
            entry = metadata[name]
            if entry is not None:
                component = entry['subject-references']['component']
                inventory_item = entry['subject-references']['inventory-item']
                subject_references = [component, inventory_item]
        except Exception:
            logger.debug('missing or invalid subject references')
        return subject_references

    def _create_observation_methods(self, rule, metadata):
        observation_methods = ['TEST-AUTOMATED']
        return observation_methods


class Rules():
    """Create and accumulate list of rule + result pairs with associated metadata."""

    def __init__(self, content):
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
    def instances(self):
        """Get the list of rules."""
        return self._instances

    @property
    def benchmark(self):
        """Get the benchmark info."""
        return self._benchmark

    @property
    def metadata(self):
        """Get the metadata info."""
        return self._metadata

    @property
    def analysis(self):
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

    def _extract_rules(self):
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

    def _parse_xml(self, results, name):
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

    def _get_target(self, root):
        """Extract 'target' info from the stringified XML."""
        target = None
        for lev1 in root:
            tag = _remove_namespace(lev1.tag)
            if tag == 'target':
                target = root.find(lev1.tag).text
                break
        return target

    def _get_config_map(self, root):
        """Extract 'config_map' info from the stringified XML."""
        retval = ''
        for lev1 in root:
            tag = _remove_namespace(lev1.tag)
            if tag == 'benchmark':
                href = lev1.get('href')
                retval = href.split('.')[0].rsplit('/', 1)[1]
                break
        return retval

    def _get_result(self, lev1):
        """Extract 'result' info from the stringified XML."""
        result = None
        for lev2 in lev1:
            tag = _remove_namespace(lev2.tag)
            if tag == 'result':
                result = lev1.find(lev2.tag).text
                break
        return result

    def _post(self, config_map, idref, time, result_type, target, name):
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


def _remove_namespace(subject):
    """If a namespace is present in the subject string, remove it."""
    return subject.rsplit('}').pop()
