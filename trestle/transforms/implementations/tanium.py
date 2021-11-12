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
"""Facilitate Tanium report to NIST OSCAL transformation."""

import datetime
import json
import logging
import multiprocessing
import os
import traceback
import uuid
from typing import Any, Dict, List, Optional, ValuesView

from trestle.oscal.assessment_results import ControlSelection
from trestle.oscal.assessment_results import LocalDefinitions1
from trestle.oscal.assessment_results import Observation
from trestle.oscal.assessment_results import Result
from trestle.oscal.assessment_results import ReviewedControls
from trestle.oscal.assessment_results import Status1
from trestle.oscal.assessment_results import SystemComponent
from trestle.oscal.common import ImplementedComponent, InventoryItem, Property, SubjectReference
from trestle.transforms.results import Results
from trestle.transforms.transformer_factory import ResultsTransformer

logger = logging.getLogger(__name__)


class TaniumTransformer(ResultsTransformer):
    """Interface for Tanium transformer."""

    def __init__(self) -> None:
        """Initialize."""
        self._modes = {}

    @property
    def analysis(self) -> List[str]:
        """Return analysis info."""
        return self._analysis

    @property
    def blocksize(self):
        """Return blocksize."""
        return self._modes.get('blocksize', 10000)

    @property
    def cpus_max(self):
        """Return cpus_max."""
        return self._modes.get('cpus_max', 1)

    @property
    def cpus_min(self):
        """Return cpus_min."""
        return self._modes.get('cpus_min', 1)

    @property
    def checking(self):
        """Return checking."""
        return self._modes.get('checking', False)

    def set_modes(self, modes: Dict[str, Any]) -> None:
        """Keep modes info."""
        if modes is not None:
            self._modes = modes

    def transform(self, blob: str) -> Results:
        """Transform the blob into a Results."""
        ts0 = datetime.datetime.now()
        results = Results()
        ru_factory = RuleUseFactory(self.get_timestamp())
        ru_list = ru_factory.make_list(blob)
        tanium_oscal_factory = TaniumOscalFactory(
            self.get_timestamp(), ru_list, self.blocksize, self.cpus_max, self.cpus_min, self.checking
        )
        results.__root__.append(tanium_oscal_factory.result)
        ts1 = datetime.datetime.now()
        self._analysis = tanium_oscal_factory.analysis
        self._analysis.append(f'transform time: {ts1-ts0}')
        return results


class RuleUse():
    """Represents one row of Tanium data."""

    def __init__(self, tanium_row: Dict[str, Any], comply: Dict[str, str], default_timestamp: str) -> None:
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
            # defaults
            no_results = '[no results]'
            self.check_id_level = no_results
            self.check_id_version = no_results
            self.check_id_benchmark = no_results
            self.component = no_results
            self.component_type = no_results
            # parse
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
            # timestamp
            self.timestamp = comply.get('Timestamp', default_timestamp)
            # collected
            self.collected = default_timestamp
        except Exception as e:
            logger.debug(f'tanium-row: {tanium_row}')
            logger.debug(e)
            logger.debug(traceback.format_exc())
            raise e


class RuleUseFactory():
    """Build RuleUse list."""

    def __init__(self, timestamp: str) -> None:
        """Initialize given specified args."""
        self._timestamp = timestamp

    def _make_sublist(self, tanium_row: Dict[str, Any]) -> List[RuleUse]:
        """Build RuleUse sublist from input data item."""
        retval = []
        keys = tanium_row.keys()
        for key in keys:
            if key.startswith('Comply'):
                break
        comply_list = tanium_row[key]
        for comply in comply_list:
            rule_use = RuleUse(tanium_row, comply, self._timestamp)
            retval.append(rule_use)
        return retval

    def make_list(self, blob: str) -> List[RuleUse]:
        """Build RuleUse list from input data."""
        retval = []
        lines = blob.splitlines()
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                jdata = json.loads(line)
                if type(jdata) is list:
                    for item in jdata:
                        logger.debug(f'item: {item}')
                        retval += self._make_sublist(item)
                else:
                    logger.debug(f'jdata: {jdata}')
                    retval += self._make_sublist(jdata)
        logger.debug(f'ru_list: {len(retval)}')
        return retval


def _uuid() -> str:
    """Create uuid."""
    return str(uuid.uuid4())


def _uuid_component() -> str:
    """Create uuid for component."""
    return _uuid()


def _uuid_inventory() -> str:
    """Create uuid for inventory."""
    return _uuid()


def _uuid_observation() -> str:
    """Create uuid for observation."""
    return _uuid()


def _uuid_result() -> str:
    """Create uuid for result."""
    return _uuid()


class TaniumOscalFactory():
    """Build Tanium OSCAL entities."""

    def __init__(
        self,
        timestamp: str,
        rule_use_list: List[RuleUse],
        blocksize: int = 11000,
        cpus_max: int = 1,
        cpus_min: int = 1,
        checking: bool = False
    ) -> None:
        """Initialize given specified args."""
        self._rule_use_list = rule_use_list
        self._timestamp = timestamp
        self._component_map = {}
        self._inventory_map = {}
        self._observation_list = []
        self._ns = 'https://ibm.github.io/compliance-trestle/schemas/oscal/ar/tanium'
        self._cpus = None
        self._checking = checking
        self._result = None
        # blocksize: default, min
        self._blocksize = blocksize
        if self._blocksize < 1:
            self._blocksize = 1
        # cpus max: default, max, min
        self._cpus_max = cpus_max
        if self._cpus_max > os.cpu_count():
            self._cpus_max = os.cpu_count()
        self._cpus_min = cpus_min
        if self._cpus_min > self._cpus_max:
            self._cpus_min = self._cpus_max
        if self._cpus_min < 1:
            self._cpus_min = 1

    def _is_duplicate_component(self, rule_use: RuleUse) -> bool:
        """Check for duplicate component."""
        retval = False
        component_type = rule_use.component_type
        component_title = rule_use.component
        for component in self._component_map.values():
            if component.type != component_type:
                continue
            if component.title != component_title:
                continue
            retval = True
            break
        return retval

    def _derive_components(self) -> Dict[str, ValuesView[InventoryItem]]:
        """Derive components from RuleUse list."""
        self._component_map = {}
        for rule_use in self._rule_use_list:
            if self._is_duplicate_component(rule_use):
                continue
            component_type = rule_use.component_type
            component_title = rule_use.component
            # See Note in _get_component_ref.
            component_description = rule_use.component
            component_ref = _uuid_component()
            status = Status1(state='operational')
            component = SystemComponent(
                uuid=component_ref,
                type=component_type,
                title=component_title,
                description=component_description,
                status=status
            )
            self._component_map[component_ref] = component

    def _get_component_ref(self, rule_use: RuleUse) -> Optional[str]:
        """Get component reference for specified rule use."""
        uuid = None
        for component_ref, component in self._component_map.items():
            if component.type != rule_use.component_type:
                continue
            if component.title != rule_use.component:
                continue
            # Note: currently title and description are the same,
            # therefore checking description is not necessary.
            uuid = component_ref
            break
        return uuid

    def _derive_inventory(self) -> Dict[str, InventoryItem]:
        """Derive inventory from RuleUse list."""
        self._inventory_map = {}
        if self._checking:
            self._derive_inventory_checked()
        else:
            self._derive_inventory_unchecked()

    def _derive_inventory_checked(self) -> Dict[str, InventoryItem]:
        """Derive inventory from RuleUse list, properties checked."""
        self._inventory_map = {}
        for rule_use in self._rule_use_list:
            if rule_use.tanium_client_ip_address in self._inventory_map:
                continue
            inventory = InventoryItem(uuid=_uuid_inventory(), description='inventory')
            inventory.props = [
                Property.construct(name='Computer_Name', value=rule_use.computer_name, ns=self._ns),
                Property.construct(
                    name='Tanium_Client_IP_Address',
                    value=rule_use.tanium_client_ip_address,
                    ns=self._ns,
                    class_='scc_inventory_item_id'
                ),
                Property.construct(name='IP_Address', value=rule_use.ip_address, ns=self._ns),
                Property.construct(name='Count', value=rule_use.count, ns=self._ns)
            ]
            component_uuid = self._get_component_ref(rule_use)
            if component_uuid is not None:
                inventory.implemented_components = [ImplementedComponent(component_uuid=component_uuid)]
            self._inventory_map[rule_use.tanium_client_ip_address] = inventory

    def _derive_inventory_unchecked(self) -> Dict[str, InventoryItem]:
        """Derive inventory from RuleUse list, properties unchecked."""
        self._inventory_map = {}
        for rule_use in self._rule_use_list:
            if rule_use.tanium_client_ip_address in self._inventory_map:
                continue
            inventory = InventoryItem(uuid=_uuid_inventory(), description='inventory')
            inventory.props = [
                Property.construct(name='Computer_Name', value=rule_use.computer_name, ns=self._ns),
                Property.construct(
                    name='Tanium_Client_IP_Address',
                    value=rule_use.tanium_client_ip_address,
                    ns=self._ns,
                    class_='scc_inventory_item_id'
                ),
                Property.construct(name='IP_Address', value=rule_use.ip_address, ns=self._ns),
                Property.construct(name='Count', value=rule_use.count, ns=self._ns)
            ]
            component_uuid = self._get_component_ref(rule_use)
            if component_uuid is not None:
                inventory.implemented_components = [ImplementedComponent(component_uuid=component_uuid)]
            self._inventory_map[rule_use.tanium_client_ip_address] = inventory

    def _get_inventory_ref(self, rule_use: RuleUse) -> str:
        """Get inventory reference for specified rule use."""
        return self._inventory_map[rule_use.tanium_client_ip_address].uuid

    def _get_observtion_properties(self, rule_use):
        """Get observation properties."""
        if self._checking:
            return self._get_observtion_properties_checked(rule_use)
        else:
            return self._get_observtion_properties_unchecked(rule_use)

    def _get_observtion_properties_checked(self, rule_use):
        """Get observation properties, with checking."""
        props = [
            Property(name='Check_ID', value=rule_use.check_id, ns=self._ns),
            Property(
                name='Check_ID_Benchmark',
                value=rule_use.check_id_benchmark,
                ns=self._ns,
                class_='scc_predefined_profile'
            ),
            Property(
                name='Check_ID_Version',
                value=rule_use.check_id_version,
                ns=self._ns,
                class_='scc_predefined_profile_version'
            ),
            Property(name='Check_ID_Level', value=rule_use.check_id_level, ns=self._ns),
            Property(name='Rule_ID', value=rule_use.rule_id, ns=self._ns, class_='scc_goal_description'),
            Property(name='Rule_ID', value=rule_use.rule_id, ns=self._ns, class_='scc_check_name_id'),
            Property(name='State', value=rule_use.state, ns=self._ns, class_='scc_result'),
            Property(name='Timestamp', value=rule_use.timestamp, ns=self._ns, class_='scc_timestamp'),
        ]
        return props

    def _get_observtion_properties_unchecked(self, rule_use):
        """Get observation properties, without checking."""
        props = [
            Property.construct(name='Check_ID', value=rule_use.check_id, ns=self._ns),
            Property.construct(
                name='Check_ID_Benchmark',
                value=rule_use.check_id_benchmark,
                ns=self._ns,
                class_='scc_predefined_profile'
            ),
            Property.construct(
                name='Check_ID_Version',
                value=rule_use.check_id_version,
                ns=self._ns,
                class_='scc_predefined_profile_version'
            ),
            Property.construct(name='Check_ID_Level', value=rule_use.check_id_level, ns=self._ns),
            Property.construct(name='Rule_ID', value=rule_use.rule_id, ns=self._ns, class_='scc_goal_description'),
            Property.construct(name='Rule_ID', value=rule_use.rule_id, ns=self._ns, class_='scc_check_name_id'),
            Property.construct(name='State', value=rule_use.state, ns=self._ns, class_='scc_result'),
            Property.construct(name='Timestamp', value=rule_use.timestamp, ns=self._ns, class_='scc_timestamp'),
        ]
        return props

    # parallel process to process one chuck of entire data set
    def _batch_observations(self, index: int):
        """Derive batch of observations from RuleUse list."""
        observation_partial_list = []
        # determine which chunk to process
        batch_size = (len(self._rule_use_list) // self._batch_workers) + 1
        start = index * batch_size
        end = (index + 1) * batch_size
        end = min(end, len(self._rule_use_list))
        logger.debug(f'start: {start} end: {end-1}')
        # process just the one chunk
        for i in range(start, end):
            rule_use = self._rule_use_list[i]
            observation = Observation(
                uuid=_uuid_observation(),
                description=rule_use.rule_id,
                methods=['TEST-AUTOMATED'],
                collected=rule_use.collected
            )
            subject_reference = SubjectReference(subject_uuid=self._get_inventory_ref(rule_use), type='inventory-item')
            observation.subjects = [subject_reference]
            observation.props = self._get_observtion_properties(rule_use)
            observation_partial_list.append(observation)
        return observation_partial_list

    @property
    def _batch_workers(self) -> int:
        """Calculate number of parallel processes to employ."""
        if self._cpus is None:
            cpus_estimate = len(self._rule_use_list) // self._blocksize
            self._cpus = max(min(cpus_estimate, self._cpus_max), self._cpus_min)
            logger.debug(f'CPUs estimate: {cpus_estimate} available: {os.cpu_count()} selection: {self._cpus}')
        return self._cpus

    def _derive_observations(self) -> List[Observation]:
        """Derive observations from RuleUse list."""
        self._observation_list = []
        if self._batch_workers == 1:
            # no need for multiprocessing
            self._observation_list = self._batch_observations(0)
        else:
            # use multiprocessing to perform observations creation in parallel
            pool = multiprocessing.Pool(processes=self._batch_workers)
            rval_list = pool.map(self._batch_observations, range(self._batch_workers))
            # gather observations from the sundry batch workers
            for observations_partial_list in rval_list:
                self._observation_list += observations_partial_list

    @property
    def components(self) -> List[SystemComponent]:
        """OSCAL components."""
        return list(self._component_map.values())

    @property
    def inventory(self) -> ValuesView[InventoryItem]:
        """OSCAL inventory."""
        return self._inventory_map.values()

    @property
    def observations(self) -> List[Observation]:
        """OSCAL observations."""
        return self._observation_list

    @property
    def local_definitions(self) -> LocalDefinitions1:
        """OSCAL local definitions."""
        rval = LocalDefinitions1()
        rval.components = self.components
        rval.inventory_items = list(self.inventory)
        return rval

    @property
    def control_selections(self) -> List[ControlSelection]:
        """OSCAL control selections."""
        rval = []
        rval.append(ControlSelection())
        return rval

    @property
    def reviewed_controls(self) -> ReviewedControls:
        """OSCAL reviewed controls."""
        rval = ReviewedControls(control_selections=self.control_selections)
        return rval

    @property
    def analysis(self) -> List[str]:
        """OSCAL statistics."""
        analysis = []
        analysis.append(f'components: {len(self.components)}')
        analysis.append(f'inventory: {len(self.inventory)}')
        analysis.append(f'observations: {len(self.observations)}')
        return analysis

    @property
    def result(self) -> Result:
        """OSCAL result."""
        if self._result is None:
            self._derive_components()
            self._derive_inventory()
            self._derive_observations()
            self._result = Result(
                uuid=_uuid_result(),
                title='Tanium',
                description='Tanium',
                start=self._timestamp,
                end=self._timestamp,
                reviewed_controls=self.reviewed_controls,
                local_definitions=self.local_definitions,
                observations=self.observations
            )
        return self._result
