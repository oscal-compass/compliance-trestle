# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Facilitate OpenShift Compliance Operator report to NIST OSCAL json transformation."""

import base64
import bz2
import logging
import uuid
from typing import Any, Dict, Iterator, List, ValuesView
from xml.etree.ElementTree import Element  # noqa: S405 - used for typing only

from defusedxml import ElementTree

from trestle.oscal.assessment_results import ControlSelection
from trestle.oscal.assessment_results import LocalDefinitions1
from trestle.oscal.assessment_results import Observation
from trestle.oscal.assessment_results import Result
from trestle.oscal.assessment_results import ReviewedControls
from trestle.oscal.assessment_results import Status1
from trestle.oscal.assessment_results import SystemComponent
from trestle.oscal.common import ImplementedComponent, InventoryItem, Property, SubjectReference
from trestle.transforms.transformer_factory import ResultsTransformer

logger = logging.getLogger(__name__)


class RuleUse():
    """Represents one rule of OSCO data."""

    def __init__(self, args: Dict[str, str]) -> None:
        """Initialize given specified args."""
        self.id_ = args['id_']
        self.target = args['target']
        self.target_type = args['target_type']
        self.host_name = args['host_name']
        self.benchmark_href = args['benchmark_href']
        self.benchmark_id = args['benchmark_id']
        self.scanner_name = args['scanner_name']
        self.scanner_version = args['scanner_version']
        self.idref = args['idref']
        self.version = args['version']
        self.time = args['time']
        self.result = args['result']
        self.severity = args['severity']
        self.weight = args['weight']

    @property
    def inventory_key(self):
        """Derive inventory key."""
        if self.host_name is None:
            # OpenScap 1.3.3
            rval = self.target + ':' + self.target_type
        else:
            # OpenScap 1.3.5
            rval = self.host_name + ':' + self.target_type
        return rval


class ComplianceOperatorReport():
    """Represents one report of OSCO data."""

    def __init__(self, osco_xml: str) -> None:
        """Initialize given specified args."""
        self.osco_xml = osco_xml

    def _get_version(self, root: Element) -> str:
        """Extract version from the XML."""
        value = None
        for key, val in root.attrib.items():
            if key == 'version':
                value = val
                break
        return value

    def _get_id(self, root: Element) -> str:
        """Extract id from the XML."""
        value = None
        for key, val in root.attrib.items():
            if key == 'id':
                value = val
                break
        return value

    def _get_target(self, root: Element) -> str:
        """Extract target from the XML."""
        value = None
        for lev1 in root:
            tag = _remove_namespace(lev1.tag)
            if tag == 'target':
                value = root.find(lev1.tag).text
                break
        return value

    def _get_target_type(self, root: Element) -> str:
        """Extract target_type from the XML."""
        value = None
        benchmark_href = self._get_benchmark_href(root)
        if benchmark_href is not None:
            value = benchmark_href.split('-')[1]
        return value

    def _get_benchmark(self, root: Element, kw) -> str:
        """Extract benchmark from the XML."""
        value = None
        for lev1 in root:
            tag = _remove_namespace(lev1.tag)
            if tag == 'benchmark':
                value = lev1.get(kw)
                break
        return value

    def _get_benchmark_href(self, root: Element) -> str:
        """Extract benchmark.href from the XML."""
        return self._get_benchmark(root, 'href')

    def _get_benchmark_id(self, root: Element) -> str:
        """Extract benchmark.id from the XML."""
        return self._get_benchmark(root, 'id')

    def _get_fact(self, lev1: Element, kw: str) -> str:
        """Extract fact from the XML."""
        value = None
        for lev2 in lev1:
            tag = _remove_namespace(lev2.tag)
            if tag == 'fact':
                name = lev2.get('name')
                if name == kw:
                    value = lev2.text
                    break
        return value

    def _get_scanner_name(self, root: Element) -> str:
        """Extract scanner:name from the XML."""
        value = None
        for lev1 in root:
            tag = _remove_namespace(lev1.tag)
            if tag == 'target-facts':
                value = self._get_fact(lev1, 'urn:xccdf:fact:scanner:name')
                break
        return value

    def _get_scanner_version(self, root: Element) -> str:
        """Extract scanner:version from the XML."""
        value = None
        for lev1 in root:
            tag = _remove_namespace(lev1.tag)
            if tag == 'target-facts':
                value = self._get_fact(lev1, 'urn:xccdf:fact:scanner:version')
                break
        return value

    def _get_host_name(self, root: Element) -> str:
        """Extract asset:identifier:host_name from the XML."""
        value = None
        for lev1 in root:
            tag = _remove_namespace(lev1.tag)
            if tag == 'target-facts':
                value = self._get_fact(lev1, 'urn:xccdf:fact:asset:identifier:host_name')
                break
        return value

    def _get_result(self, lev1: Element) -> str:
        """Extract result from the XML."""
        value = None
        for lev2 in lev1:
            tag = _remove_namespace(lev2.tag)
            if tag == 'result':
                value = lev1.find(lev2.tag).text
                break
        return value

    def _parse_xml(self) -> Iterator[RuleUse]:
        """Parse the stringified XML."""
        results = self.osco_xml
        root = ElementTree.fromstring(results, forbid_dtd=True)
        version = self._get_version(root)
        id_ = self._get_id(root)
        target = self._get_target(root)
        target_type = self._get_target_type(root)
        host_name = self._get_host_name(root)
        benchmark_href = self._get_benchmark_href(root)
        benchmark_id = self._get_benchmark_id(root)
        scanner_name = self._get_scanner_name(root)
        scanner_version = self._get_scanner_version(root)
        for lev1 in root:
            tag = _remove_namespace(lev1.tag)
            if tag == 'rule-result':
                idref = lev1.get('idref')
                time = lev1.get('time')
                severity = lev1.get('severity')
                weight = lev1.get('weight')
                result = self._get_result(lev1)
                args = {
                    'id_': id_,
                    'target': target,
                    'target_type': target_type,
                    'host_name': host_name,
                    'benchmark_href': benchmark_href,
                    'benchmark_id': benchmark_id,
                    'scanner_name': scanner_name,
                    'scanner_version': scanner_version,
                    'idref': idref,
                    'version': version,
                    'time': time,
                    'result': result,
                    'severity': severity,
                    'weight': weight
                }
                rule_use = RuleUse(args)
                yield rule_use

    def rule_use_generator(self) -> RuleUse:
        """Generate RuleUses by way of parsing the embedded XML."""
        return self._parse_xml()


class ResultsMgr():
    """Represents collection of data to transformed into an AssessmentResult.results."""

    default_timestamp = ResultsTransformer.get_timestamp()

    def __init__(self, timestamp: str = default_timestamp) -> None:
        """Initialize."""
        self.timestamp = timestamp
        self.observation_list: List[Observation] = []
        self.component_map: Dict[str, SystemComponent] = {}
        self.inventory_map: Dict[str, InventoryItem] = {}
        self.results_map: Dict[str, Any] = {}
        self.ns = 'https://ibm.github.io/compliance-trestle/schemas/oscal/ar/osco'

    @property
    def components(self) -> Dict[str, SystemComponent]:
        """OSCAL components."""
        return list(self.component_map.values())

    @property
    def control_selections(self) -> List[ControlSelection]:
        """OSCAL control selections."""
        prop = []
        prop.append(ControlSelection())
        return prop

    @property
    def inventory(self) -> ValuesView[InventoryItem]:
        """OSCAL inventory."""
        return self.inventory_map.values()

    @property
    def local_definitions(self) -> LocalDefinitions1:
        """OSCAL local definitions."""
        prop = LocalDefinitions1()
        prop.components = self.components
        prop.inventory_items = list(self.inventory)
        return prop

    @property
    def observations(self) -> List[Observation]:
        """OSCAL observations."""
        return self.observation_list

    @property
    def reviewed_controls(self) -> ReviewedControls:
        """OSCAL reviewed controls."""
        prop = ReviewedControls(control_selections=self.control_selections)
        return prop

    @property
    def result(self) -> Result:
        """OSCAL result."""
        prop = Result(
            uuid=str(uuid.uuid4()),
            title='OpenShift Compliance Operator',
            description='OpenShift Compliance Operator Scan Results',
            start=self.timestamp,
            end=self.timestamp,
            reviewed_controls=self.reviewed_controls,
        )
        if len(self.inventory) > 0:
            prop.local_definitions = self.local_definitions
        if len(self.observation_list) > 0:
            prop.observations = self.observations
        return prop

    @property
    def analysis(self) -> List[str]:
        """OSCAL statistics."""
        analysis = []
        analysis.append(f'inventory: {len(self.inventory)}')
        analysis.append(f'observations: {len(self.observations)}')
        return analysis

    def _component_extract(self, rule_use: RuleUse) -> None:
        """Extract component from RuleUse."""
        component_type = 'Service'
        component_title = f'Red Hat OpenShift Kubernetes Service Compliance Operator for {rule_use.target_type}'
        component_description = component_title
        for component in self.component_map.values():
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

    def _get_component_ref(self, rule_use: RuleUse) -> str:
        """Get component reference for specified RuleUse."""
        uuid = None
        for component_ref, component in self.component_map.items():
            if component.title.endswith(rule_use.target_type):
                uuid = component_ref
        return uuid

    def _inventory_extract(self, rule_use: RuleUse) -> None:
        """Extract inventory from RuleUse."""
        if rule_use.inventory_key in self.inventory_map:
            return
        inventory = InventoryItem(uuid=str(uuid.uuid4()), description='inventory')
        props = []
        if rule_use.host_name is None:
            props.append(Property(name='target', value=rule_use.target, ns=self.ns, class_='scc_inventory_item_id'))
            props.append(Property(name='target_type', value=rule_use.target_type, ns=self.ns))
        else:
            props.append(Property(name='target', value=rule_use.target, ns=self.ns))
            props.append(Property(name='target_type', value=rule_use.target_type, ns=self.ns))
            props.append(
                Property(name='host_name', value=rule_use.host_name, ns=self.ns, class_='scc_inventory_item_id')
            )
        inventory.props = props
        inventory.implemented_components = [ImplementedComponent(component_uuid=self._get_component_ref(rule_use))]
        self.inventory_map[rule_use.inventory_key] = inventory

    def _get_inventory_ref(self, rule_use: RuleUse) -> str:
        """Get inventory reference for specified RuleUse."""
        return self.inventory_map[rule_use.inventory_key].uuid

    def _observation_extract(self, rule_use: RuleUse) -> None:
        """Extract observation from RuleUse."""
        observation = Observation(
            uuid=str(uuid.uuid4()), description=rule_use.idref, methods=['TEST-AUTOMATED'], collected=self.timestamp
        )
        subject_reference = SubjectReference(subject_uuid=self._get_inventory_ref(rule_use), type='inventory-item')
        observation.subjects = [subject_reference]
        props = []
        props.append(Property(name='scanner_name', value=rule_use.scanner_name, ns=self.ns))
        props.append(Property(name='scanner_version', value=rule_use.scanner_version, ns=self.ns))
        props.append(Property(name='idref', value=rule_use.idref, ns=self.ns, class_='scc_check_name_id'))
        props.append(Property(name='version', value=rule_use.version, ns=self.ns, class_='scc_check_version'))
        props.append(Property(name='result', value=rule_use.result, ns=self.ns, class_='scc_result'))
        props.append(Property(name='time', value=rule_use.time, ns=self.ns, class_='scc_timestamp'))
        props.append(Property(name='severity', value=rule_use.severity, ns=self.ns, class_='scc_check_severity'))
        props.append(Property(name='weight', value=rule_use.weight, ns=self.ns))
        props.append(Property(name='benchmark_id', value=rule_use.benchmark_id, ns=self.ns))
        props.append(Property(name='benchmark_href', value=rule_use.benchmark_href, ns=self.ns))
        props.append(Property(name='id', value=rule_use.id_, ns=self.ns, class_='scc_predefined_profile'))
        observation.props = props
        self.observation_list.append(observation)
        rule_use.observation = observation

    def _process(self, co_report: ComplianceOperatorReport) -> None:
        """Process ingested data."""
        rule_use_generator = co_report.rule_use_generator()
        for rule_use in rule_use_generator:
            self._component_extract(rule_use)
            self._inventory_extract(rule_use)
            self._observation_extract(rule_use)

    def ingest(self, osco_data: Dict[str, Any]) -> None:
        """Process OSCO json."""
        if 'data' not in osco_data.keys():
            return
        if 'results' not in osco_data['data']:
            return
        results = osco_data['data']['results']
        self.ingest_xml(results)

    def ingest_xml(self, osco_xml: str) -> None:
        """Process OSCO xml."""
        if osco_xml.startswith('<?xml'):
            pass
        else:
            osco_xml = bz2.decompress(base64.b64decode(osco_xml))
        co_report = ComplianceOperatorReport(osco_xml)
        self._process(co_report)


def _remove_namespace(subject: str) -> str:
    """If a namespace is present in the subject string, remove it."""
    return subject.rsplit('}').pop()