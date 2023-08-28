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
"""Facilitate OSCAL-XCCDF transformation."""

import base64
import bz2
import json
import uuid
from typing import Any, Dict, Iterator, List, Optional, ValuesView
from xml.etree.ElementTree import Element  # noqa: S405 - used for typing only

from defusedxml import ElementTree

from ruamel.yaml import YAML

from trestle.oscal.assessment_results import AssessmentAssets
from trestle.oscal.assessment_results import ControlSelection
from trestle.oscal.assessment_results import LocalDefinitions1
from trestle.oscal.assessment_results import Observation
from trestle.oscal.assessment_results import Result
from trestle.oscal.assessment_results import ReviewedControls
from trestle.oscal.assessment_results import Status1
from trestle.oscal.assessment_results import SystemComponent
from trestle.oscal.common import AssessmentPlatform, ImplementedComponent, InventoryItem, Property, SubjectReference
from trestle.transforms.results import Results
from trestle.transforms.transformer_factory import ResultsTransformer
from trestle.transforms.transformer_helper import TransformerHelper


class XccdfResultToOscalARTransformer(ResultsTransformer):
    """Interface for Xccdf transformer."""

    def __init__(self) -> None:
        """Initialize."""
        self._modes = {}

    @property
    def analysis(self) -> List[str]:
        """Analysis."""
        return self._results_factory.analysis

    @property
    def checking(self):
        """Return checking."""
        return self._modes.get('checking', False)

    @property
    def tags(self):
        """Return tags."""
        return self._tags

    def set_tags(self, tags: Dict[str, str]) -> None:
        """Keep tags info (property name to property class)."""
        self._tags = tags

    def set_title(self, title: str) -> None:
        """Keep title info."""
        self._title = title

    def set_description(self, description: str) -> None:
        """Keep description info."""
        self._description = description

    def set_type(self, type_: str) -> None:
        """Keep type info."""
        self._type = type_

    def set_modes(self, modes: Dict[str, Any]) -> None:
        """Keep modes info."""
        if modes is not None:
            self._modes = modes

    def transform(self, blob: str) -> Results:
        """Transform the blob into a Results.

        The expected blob is a string that is one of:
            - data from OpenShift Compliance Operator (json, yaml, xml)
            - data from Auditree XCCDF fetcher/check (json)
        """
        self._results_factory = _OscalResultsFactory(
            self._title, self._description, self._type, self.get_timestamp(), self.checking, self.tags
        )
        results = self._ingest_xml(blob)
        if results is None:
            results = self._ingest_json(blob)
        if results is None:
            results = self._ingest_yaml(blob)
        return results

    def _ingest_xml(self, blob: str) -> Optional[Results]:
        """Ingest xml data."""
        # ?xml data
        if blob.startswith('<?xml'):
            resource = blob
            self._results_factory.ingest_xml(resource)
        else:
            return None
        results = Results()
        results.__root__.append(self._results_factory.result)
        return results

    def _ingest_configmaps(self, jdata: dict) -> None:
        """Ingest configmaps."""
        items = jdata['items']
        for item in items:
            if 'data' in item.keys():
                data = item['data']
                if 'results' in data:
                    resource = item
                    self._results_factory.ingest(resource)

    def _ingest_auditree(self, jdata: dict) -> None:
        """Ingest auditree."""
        for key in jdata.keys():
            for group in jdata[key]:
                for cluster in jdata[key][group]:
                    if 'resources' in cluster:
                        for resource in cluster['resources']:
                            self._results_factory.ingest(resource)

    def _ingest_json(self, blob: str) -> Optional[Results]:
        """Ingest json data."""
        try:
            # ? configmaps or auditree data
            jdata = json.loads(blob)
            # https://docs.openshift.com/container-platform/3.7/rest_api/api/v1.ConfigMap.html#Get-api-v1-namespaces-namespace-configmaps-name
            if 'kind' in jdata.keys() and jdata['kind'] == 'ConfigMapList' and 'items' in jdata.keys():
                self._ingest_configmaps(jdata)
            # https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/kubernetes/fetchers/fetch_cluster_resource.py
            else:
                self._ingest_auditree(jdata)
        except json.decoder.JSONDecodeError:
            return None
        results = Results()
        results.__root__.append(self._results_factory.result)
        return results

    def _ingest_yaml(self, blob: str) -> Results:
        """Ingest yaml data."""
        try:
            # ? yaml data
            yaml = YAML(typ='safe')
            resource = yaml.load(blob)
            self._results_factory.ingest(resource)
        except Exception as e:
            raise RuntimeError(e)
        results = Results()
        results.__root__.append(self._results_factory.result)
        return results


class XccdfTransformer(XccdfResultToOscalARTransformer):
    """Legacy class name."""


class RuleUse():
    """Represents one rule of XCCDF data."""

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

    @property
    def ns(self):
        """Derive namespace."""
        return f'https://ibm.github.io/compliance-trestle/schemas/oscal/ar/{self.scanner_name}'


class _XccdfResult():
    """Represents one result of XCCDF data."""

    def __init__(self, xccdf_xml: str) -> None:
        """Initialize given specified args."""
        self.xccdf_xml = xccdf_xml

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
        if benchmark_href is not None and '-' in benchmark_href:
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
        results = self.xccdf_xml
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

    def rule_use_generator(self) -> Iterator[RuleUse]:
        """Generate RuleUses by way of parsing the embedded XML."""
        return self._parse_xml()


class _OscalResultsFactory():
    """Build XCCDF OSCAL entities."""

    default_timestamp = ResultsTransformer.get_timestamp()

    def __init__(
        self,
        title: str,
        description: str,
        type_: str,
        timestamp: str = default_timestamp,
        checking: bool = False,
        tags: Dict = None
    ) -> None:
        """Initialize."""
        self._title = title
        self._description = description
        self._type = type_
        self._timestamp = timestamp
        self._observation_list: List[Observation] = []
        self._assessment_asset_properties_list: List[Property] = []
        self._component_map: Dict[str, SystemComponent] = {}
        self._inventory_map: Dict[str, InventoryItem] = {}
        self._checking = checking
        self._tags = tags

    @property
    def components(self) -> List[SystemComponent]:
        """OSCAL components."""
        return list(self._component_map.values())

    @property
    def control_selections(self) -> List[ControlSelection]:
        """OSCAL control selections."""
        prop = []
        prop.append(ControlSelection())
        return prop

    @property
    def inventory(self) -> ValuesView[InventoryItem]:
        """OSCAL inventory."""
        return self._inventory_map.values()

    @property
    def local_definitions(self) -> LocalDefinitions1:
        """OSCAL local definitions."""
        prop = LocalDefinitions1()
        prop.components = self.components
        prop.assessment_assets = self.assessment_assets
        prop.inventory_items = list(self.inventory)
        return prop

    @property
    def assessment_assets(self) -> AssessmentAssets:
        """OSCAL assessment_assets."""
        _status = Status1(state='operational')
        component = SystemComponent(
            uuid=str(uuid.uuid4()),
            type=f'{self._type}',
            title=f'{self.scanner}',
            description=f'{self.scanner}',
            status=_status,
        )
        if self.assessment_asset_properties:
            component.props = []
            for prop in self.assessment_asset_properties:
                if prop.name == 'time':
                    continue
                component.props.append(prop)
        components = [component]
        assessment_platform = AssessmentPlatform(uuid=str(uuid.uuid4()))
        assessment_platforms = [assessment_platform]
        prop = AssessmentAssets(
            components=components,
            assessment_platforms=assessment_platforms,
        )
        return prop

    @property
    def scanner(self) -> str:
        prop = 'openScap'
        if self.assessment_asset_properties:
            for aa_prop in self.assessment_asset_properties:
                if aa_prop.name == 'scanner_name':
                    prop = aa_prop.value
                    break
        return prop

    @property
    def time(self) -> str:
        prop = self._timestamp
        if self.assessment_asset_properties:
            for aa_prop in self.assessment_asset_properties:
                if aa_prop.name == 'time':
                    prop = aa_prop.value
                    break
        return prop

    @property
    def observations(self) -> List[Observation]:
        """OSCAL observations."""
        return self._observation_list

    @property
    def assessment_asset_properties(self) -> List[Property]:
        """OSCAL assessment asset properties."""
        return self._assessment_asset_properties_list

    @property
    def reviewed_controls(self) -> ReviewedControls:
        """OSCAL reviewed controls."""
        prop = ReviewedControls(control_selections=self.control_selections)
        return prop

    @property
    def result(self) -> Result:
        """OSCAL result."""
        # perform result properties aggregation
        if self.observations:
            self._assessment_asset_properties_list = TransformerHelper().remove_common_observation_properties(
                self.observations
            )
        # produce result
        prop = Result(
            uuid=str(uuid.uuid4()),
            title=f'{self._title}',
            description=f'{self._description}',
            start=self.time,
            end=self.time,
            reviewed_controls=self.reviewed_controls,
        )
        if self.inventory:
            prop.local_definitions = self.local_definitions
        if self.observations:
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
        _type = 'Service'
        _title = f'{rule_use.target_type}'
        _desc = _title
        for component in self._component_map.values():
            if component.type == _type and component.title == _title and component.description == _desc:
                return
        component_ref = str(uuid.uuid4())
        status = Status1(state='operational')
        component = SystemComponent(uuid=component_ref, type=_type, title=_title, description=_desc, status=status)
        self._component_map[component_ref] = component

    def _get_component_ref(self, rule_use: RuleUse) -> str:
        """Get component reference for specified RuleUse."""
        uuid = None
        for component_ref, component in self._component_map.items():
            if component.title.endswith(rule_use.target_type):
                uuid = component_ref
        return uuid

    def _inventory_extract(self, rule_use: RuleUse) -> None:
        """Extract inventory from RuleUse."""
        if rule_use.inventory_key in self._inventory_map:
            return
        inventory = InventoryItem(uuid=str(uuid.uuid4()), description='inventory')
        inventory.props = self._get_inventory_properties(rule_use)
        inventory.implemented_components = [ImplementedComponent(component_uuid=self._get_component_ref(rule_use))]
        self._inventory_map[rule_use.inventory_key] = inventory

    def _get_inventory_properties(self, rule_use):
        """Get inventory properties."""
        props = []
        if rule_use.host_name is None:
            props.append(self._mk_prop('target', rule_use.target, rule_use.ns, self._tags.get('target')))
            props.append(self._mk_prop('target_type', rule_use.target_type, rule_use.ns, self._tags.get('')))
        else:
            props.append(self._mk_prop('target', rule_use.target, rule_use.ns, self._tags.get('')))
            props.append(self._mk_prop('target_type', rule_use.target_type, rule_use.ns, self._tags.get('')))
            props.append(self._mk_prop('host_name', rule_use.host_name, rule_use.ns, self._tags.get('host_name')))
        return props

    def _mk_prop(self, name: str, value: str, ns: str, class_: str) -> Property:
        """Make property."""
        if self._checking:
            if ns and class_:
                prop = Property(name=name, value=value, ns=ns, class_=class_)
            elif ns:
                prop = Property(name=name, value=value, ns=ns)
        else:
            if ns and class_:
                prop = Property.construct(name=name, value=value, ns=ns, class_=class_)
            elif ns:
                prop = Property.construct(name=name, value=value, ns=ns)
        return prop

    def _get_inventory_ref(self, rule_use: RuleUse) -> str:
        """Get inventory reference for specified RuleUse."""
        return self._inventory_map[rule_use.inventory_key].uuid

    def _observation_extract(self, rule_use: RuleUse) -> None:
        """Extract observation from RuleUse."""
        observation = Observation(
            uuid=str(uuid.uuid4()), description=rule_use.idref, methods=['TEST-AUTOMATED'], collected=self._timestamp
        )
        subject_reference = SubjectReference(subject_uuid=self._get_inventory_ref(rule_use), type='inventory-item')
        observation.subjects = [subject_reference]
        observation.props = self._get_observation_properties(rule_use)
        self._observation_list.append(observation)
        rule_use.observation = observation

    def _get_observation_properties(self, rule_use):
        """Get observation properties."""
        props = []
        props.append(self._mk_prop('scanner_name', rule_use.scanner_name, rule_use.ns, self._tags.get('')))
        props.append(self._mk_prop('scanner_version', rule_use.scanner_version, rule_use.ns, self._tags.get('')))
        props.append(self._mk_prop('idref', rule_use.idref, rule_use.ns, self._tags.get('idref')))
        props.append(self._mk_prop('version', rule_use.version, rule_use.ns, self._tags.get('version')))
        props.append(self._mk_prop('result', rule_use.result, rule_use.ns, self._tags.get('result')))
        props.append(self._mk_prop('time', rule_use.time, rule_use.ns, self._tags.get('time')))
        props.append(self._mk_prop('severity', rule_use.severity, rule_use.ns, self._tags.get('severity')))
        props.append(self._mk_prop('weight', rule_use.weight, rule_use.ns, self._tags.get('')))
        props.append(self._mk_prop('benchmark_id', rule_use.benchmark_id, rule_use.ns, self._tags.get('')))
        props.append(self._mk_prop('benchmark_href', rule_use.benchmark_href, rule_use.ns, self._tags.get('')))
        props.append(self._mk_prop('id', rule_use.id_, rule_use.ns, self._tags.get('id')))
        return props

    def _process(self, co_result: _XccdfResult) -> None:
        """Process ingested data."""
        rule_use_generator = co_result.rule_use_generator()
        for rule_use in rule_use_generator:
            self._component_extract(rule_use)
            self._inventory_extract(rule_use)
            self._observation_extract(rule_use)

    def ingest(self, xccdf_data: Dict[str, Any]) -> None:
        """Process XCCDF json."""
        if 'data' not in xccdf_data.keys():
            return
        if 'results' not in xccdf_data['data']:
            return
        results = xccdf_data['data']['results']
        self.ingest_xml(results)

    def ingest_xml(self, xccdf_xml: str) -> None:
        """Process XCCDF xml."""
        if not xccdf_xml.startswith('<?xml'):
            xccdf_xml = bz2.decompress(base64.b64decode(xccdf_xml))
        co_result = _XccdfResult(xccdf_xml)
        self._process(co_result)


def _remove_namespace(subject: str) -> str:
    """If a namespace is present in the subject string, remove it."""
    return subject.rsplit('}').pop()
