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
"""Facilitate OSCAL-OSCO transformation."""

import base64
import bz2
import json
import logging
import uuid
from typing import Any, Dict, Iterator, List, ValuesView
from xml.etree.ElementTree import Element  # noqa: S405 - used for typing only

from defusedxml import ElementTree

from ruamel.yaml import YAML

from trestle.core.utils import as_list
from trestle.oscal.assessment_results import ControlSelection
from trestle.oscal.assessment_results import LocalDefinitions1
from trestle.oscal.assessment_results import Observation
from trestle.oscal.assessment_results import Result
from trestle.oscal.assessment_results import ReviewedControls
from trestle.oscal.assessment_results import Status1
from trestle.oscal.assessment_results import SystemComponent
from trestle.oscal.common import ImplementedComponent, InventoryItem, Property, SubjectReference
from trestle.oscal.profile import Profile
from trestle.transforms.results import Results
from trestle.transforms.transformer_factory import FromOscalTransformer
from trestle.transforms.transformer_factory import ResultsTransformer

logger = logging.getLogger(__name__)


class OscoTransformer(ResultsTransformer):
    """Interface for Osco transformer."""

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

    def set_modes(self, modes: Dict[str, Any]) -> None:
        """Keep modes info."""
        if modes is not None:
            self._modes = modes

    def transform(self, blob: str) -> Results:
        """Transform the blob into a Results.

        The expected blob is a string that is one of:
            - data from OpenShift Compliance Operator (json, yaml, xml)
            - data from Auditree OSCO fetcher/check (json)
        """
        results = None
        self._results_factory = OscalResultsFactory(self.get_timestamp(), self.checking)
        if results is None:
            results = self._ingest_xml(blob)
        if results is None:
            results = self._ingest_json(blob)
        if results is None:
            results = self._ingest_yaml(blob)
        return results

    def _ingest_xml(self, blob: str) -> Results:
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

    def _ingest_json(self, blob: str) -> Results:
        """Ingest json data."""
        try:
            # ? configmaps or auditree data
            jdata = json.loads(blob)
            # https://docs.openshift.com/container-platform/3.7/rest_api/api/v1.ConfigMap.html#Get-api-v1-namespaces-namespace-configmaps-name
            if 'kind' in jdata.keys() and jdata['kind'] == 'ConfigMapList' and 'items' in jdata.keys():
                items = jdata['items']
                for item in items:
                    if 'data' in item.keys():
                        data = item['data']
                        if 'results' in data:
                            resource = item
                            self._results_factory.ingest(resource)
            # https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/kubernetes/fetchers/fetch_cluster_resource.py
            else:
                for key in jdata.keys():
                    for group in jdata[key]:
                        for cluster in jdata[key][group]:
                            if 'resources' in cluster:
                                for resource in cluster['resources']:
                                    self._results_factory.ingest(resource)
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
            raise e
        results = Results()
        results.__root__.append(self._results_factory.result)
        return results


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

    def rule_use_generator(self) -> Iterator[RuleUse]:
        """Generate RuleUses by way of parsing the embedded XML."""
        return self._parse_xml()


class OscalResultsFactory():
    """Build OSCO OSCAL entities."""

    default_timestamp = ResultsTransformer.get_timestamp()

    def __init__(self, timestamp: str = default_timestamp, checking: bool = False) -> None:
        """Initialize."""
        self._timestamp = timestamp
        self._observation_list: List[Observation] = []
        self._component_map: Dict[str, SystemComponent] = {}
        self._inventory_map: Dict[str, InventoryItem] = {}
        self._ns = 'https://ibm.github.io/compliance-trestle/schemas/oscal/ar/osco'
        self._checking = checking

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
        prop.inventory_items = list(self.inventory)
        return prop

    @property
    def observations(self) -> List[Observation]:
        """OSCAL observations."""
        return self._observation_list

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
            start=self._timestamp,
            end=self._timestamp,
            reviewed_controls=self.reviewed_controls,
        )
        if len(self.inventory) > 0:
            prop.local_definitions = self.local_definitions
        if len(self._observation_list) > 0:
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
        _title = f'Red Hat OpenShift Kubernetes Service Compliance Operator for {rule_use.target_type}'
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
        if self._checking:
            return self._get_inventory_properties_checked(rule_use)
        else:
            return self._get_inventory_properties_unchecked(rule_use)

    def _get_inventory_properties_checked(self, rule_use):
        """Get inventory properties, with checking."""
        props = []
        if rule_use.host_name is None:
            props.append(Property(name='target', value=rule_use.target, ns=self._ns, class_='scc_inventory_item_id'))
            props.append(Property(name='target_type', value=rule_use.target_type, ns=self._ns))
        else:
            props.append(Property(name='target', value=rule_use.target, ns=self._ns))
            props.append(Property(name='target_type', value=rule_use.target_type, ns=self._ns))
            props.append(
                Property(name='host_name', value=rule_use.host_name, ns=self._ns, class_='scc_inventory_item_id')
            )
        return props

    def _get_inventory_properties_unchecked(self, rule_use):
        """Get observation properties, without checking."""
        props = []
        if rule_use.host_name is None:
            props.append(
                Property.construct(name='target', value=rule_use.target, ns=self._ns, class_='scc_inventory_item_id')
            )
            props.append(Property.construct(name='target_type', value=rule_use.target_type, ns=self._ns))
        else:
            props.append(Property.construct(name='target', value=rule_use.target, ns=self._ns))
            props.append(Property.construct(name='target_type', value=rule_use.target_type, ns=self._ns))
            props.append(
                Property.construct(
                    name='host_name', value=rule_use.host_name, ns=self._ns, class_='scc_inventory_item_id'
                )
            )
        return props

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
        if self._checking:
            return self._get_observation_properties_checked(rule_use)
        else:
            return self._get_observation_properties_unchecked(rule_use)

    def _get_observation_properties_checked(self, rule_use):
        """Get observation properties, with checking."""
        props = []
        props.append(Property(name='scanner_name', value=rule_use.scanner_name, ns=self._ns))
        props.append(Property(name='scanner_version', value=rule_use.scanner_version, ns=self._ns))
        props.append(Property(name='idref', value=rule_use.idref, ns=self._ns, class_='scc_check_name_id'))
        props.append(Property(name='version', value=rule_use.version, ns=self._ns, class_='scc_check_version'))
        props.append(Property(name='result', value=rule_use.result, ns=self._ns, class_='scc_result'))
        props.append(Property(name='time', value=rule_use.time, ns=self._ns, class_='scc_timestamp'))
        props.append(Property(name='severity', value=rule_use.severity, ns=self._ns, class_='scc_check_severity'))
        props.append(Property(name='weight', value=rule_use.weight, ns=self._ns))
        props.append(Property(name='benchmark_id', value=rule_use.benchmark_id, ns=self._ns))
        props.append(Property(name='benchmark_href', value=rule_use.benchmark_href, ns=self._ns))
        props.append(Property(name='id', value=rule_use.id_, ns=self._ns, class_='scc_predefined_profile'))
        return props

    def _get_observation_properties_unchecked(self, rule_use):
        """Get observation properties, without checking."""
        props = []
        props.append(Property.construct(name='scanner_name', value=rule_use.scanner_name, ns=self._ns))
        props.append(Property.construct(name='scanner_version', value=rule_use.scanner_version, ns=self._ns))
        props.append(Property.construct(name='idref', value=rule_use.idref, ns=self._ns, class_='scc_check_name_id'))
        props.append(
            Property.construct(name='version', value=rule_use.version, ns=self._ns, class_='scc_check_version')
        )
        props.append(Property.construct(name='result', value=rule_use.result, ns=self._ns, class_='scc_result'))
        props.append(Property.construct(name='time', value=rule_use.time, ns=self._ns, class_='scc_timestamp'))
        props.append(
            Property.construct(name='severity', value=rule_use.severity, ns=self._ns, class_='scc_check_severity')
        )
        props.append(Property.construct(name='weight', value=rule_use.weight, ns=self._ns))
        props.append(Property.construct(name='benchmark_id', value=rule_use.benchmark_id, ns=self._ns))
        props.append(Property.construct(name='benchmark_href', value=rule_use.benchmark_href, ns=self._ns))
        props.append(Property.construct(name='id', value=rule_use.id_, ns=self._ns, class_='scc_predefined_profile'))
        return props

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
        if not osco_xml.startswith('<?xml'):
            osco_xml = bz2.decompress(base64.b64decode(osco_xml))
        co_report = ComplianceOperatorReport(osco_xml)
        self._process(co_report)


def _remove_namespace(subject: str) -> str:
    """If a namespace is present in the subject string, remove it."""
    return subject.rsplit('}').pop()


class ProfileToOscoTransformer(FromOscalTransformer):
    """Interface for Profile to Osco transformer."""

    def __init__(
        self,
        extends='ocp4-cis-node',
        api_version='compliance.openshift.io/v1alpha1',
        kind='TailoredProfile',
        name='customized-tailored-profile',
        namespace='openshift-compliance',
    ) -> None:
        """Initialize."""
        self._extends = extends
        self._api_version = api_version
        self._kind = kind
        self._name = name
        self._namespace = namespace

    def transform(self, profile: Profile) -> str:
        """Transform the Profile into a OSCO yaml."""
        self._profile = profile
        self._osco_version = self._get_normalized_version('osco_version', '0.1.46')
        # set values
        set_values = self._get_set_values()
        # spec
        if self._osco_version < (0, 1, 40):
            # for versions prior to 0.1.40, exclude 'description'
            spec = {
                'extends': self._get_metadata_prop_value('base_profile_mnemonic', self._extends),
                'title': self._profile.metadata.title,
                'setValues': set_values,
            }
        else:
            # for versions 0.1.40 and beyond, include 'description'
            spec = {
                'description': self._get_metadata_prop_value('profile_mnemonic', self._name),
                'extends': self._get_metadata_prop_value('base_profile_mnemonic', self._extends),
                'title': self._profile.metadata.title,
                'setValues': set_values,
            }
        disable_rules = self._get_disable_rules()
        if len(disable_rules) > 0:
            spec['disableRules'] = disable_rules
        # yaml data
        ydata = {
            'apiVersion': self._api_version,
            'kind': self._kind,
            'metadata': {
                'name': self._get_metadata_prop_value('profile_mnemonic', self._name),
                'namespace': self._namespace,
            },
            'spec': spec,
        }
        return json.dumps(ydata)

    def _get_normalized_version(self, prop_name, prop_default) -> (int, int, int):
        """Get normalized version.

        Normalize the "x.y.z" string value to an integer: 1,000,000*x + 1,000*y + z.
        """
        try:
            vparts = self._get_metadata_prop_value(prop_name, prop_default).split('.')
            normalized_version = (int(vparts[0]), int(vparts[1]), int(vparts[2]))
        except Exception:
            logger.warning(f'metadata prop name={prop_name} value error')
            vparts = prop_default.split('.')
            normalized_version = (int(vparts[0]), int(vparts[1]), int(vparts[2]))
        return normalized_version

    def _get_set_values(self) -> List[Dict]:
        """Extract set_paramater name/value pairs from profile."""
        set_values = []
        # for check versions prior to 0.1.59 include parameters
        # for later versions parameters should not be specified, caveat emptor
        if self._profile.modify is not None:
            for set_parameter in as_list(self._profile.modify.set_parameters):
                name = self._format_osco_rule_name(set_parameter.param_id)
                parameter_value = set_parameter.values[0]
                value = parameter_value.__root__
                rationale = self._get_rationale_for_set_value()
                set_value = {'name': name, 'value': value, 'rationale': rationale}
                set_values.append(set_value)
        return set_values

    def _format_osco_rule_name(self, name: str) -> str:
        """Format for OSCO.

        1. remove prefix xccdf_org.ssgproject.content_rule_
        2. change underscores to dashes
        3. add prefix ocp4-
        """
        normalized_name = name.replace('xccdf_org.ssgproject.content_rule_', '').replace('_', '-')
        if not normalized_name.startswith('ocp4-'):
            normalized_name = f'ocp4-{normalized_name}'
        return normalized_name

    def _get_metadata_prop_value(self, name: str, default_: str) -> str:
        """Extract metadata prop or else default if not present."""
        for prop in as_list(self._profile.metadata.props):
            if prop.name == name:
                return prop.value
        logger.info(f'using default: {name} = {default_}')
        return default_

    def _get_disable_rules(self) -> List[str]:
        """Extract disabled rules."""
        value = []
        for item in as_list(self._profile.imports):
            for control in as_list(item.exclude_controls):
                self._add_disable_rules_for_control(value, control)
        return value

    def _add_disable_rules_for_control(self, value, control):
        """Extract disabled rules for control."""
        for with_id in as_list(control.with_ids):
            name = self._format_osco_rule_name(with_id.__root__)
            rationale = self._get_rationale_for_disable_rule()
            entry = {'name': name, 'rationale': rationale}
            value.append(entry)

    def _get_rationale_for_set_value(self) -> str:
        """Rationale for set value."""
        return 'not determinable from specification'

    def _get_rationale_for_disable_rule(self) -> str:
        """Rationale for disable rule."""
        return 'not determinable from specification'
