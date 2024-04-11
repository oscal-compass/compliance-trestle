# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2023 IBM Corp. All rights reserved.
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
"""OSCAL transformation tasks."""

# mypy: ignore-errors  # noqa E800
import configparser
import datetime
import logging
import pathlib
import traceback
import uuid
from typing import Dict, Iterator, List, Optional

from trestle.oscal import OSCAL_VERSION
from trestle.oscal.common import Metadata, Property
from trestle.oscal.component import ComponentDefinition
from trestle.oscal.component import ControlImplementation
from trestle.oscal.component import DefinedComponent
from trestle.oscal.component import ImplementedRequirement
from trestle.oscal.mapping import MappingCollection
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome

logger = logging.getLogger(__name__)

timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc).isoformat()


class CDHelper:
    """OSCAL CD Helper."""

    def __init__(self, path: pathlib.Path, title: str, version: str) -> None:
        """Initialize."""
        self.path = path
        if title:
            metadata = Metadata(
                title=title,
                last_modified=timestamp,
                oscal_version=OSCAL_VERSION,
                version=version,
            )
            self.cd = ComponentDefinition(
                uuid=str(uuid.uuid4()),
                metadata=metadata,
                components=[],
            )

    def read(self) -> None:
        """Read."""
        self.cd = ComponentDefinition.oscal_read(self.path)

    def write(self) -> None:
        """Write."""
        self.cd.oscal_write(pathlib.Path(self.path))

    def component_generator(self) -> Iterator[Dict]:
        """Component generator."""
        for component in self.cd.components:
            yield component

    def component_add(self, component: Dict) -> None:
        """Component add."""
        self.cd.components.append(component)

    def component_get_rules(self, component: Dict) -> List[str]:
        """Get component rules."""
        rval = []
        if component.props:
            for prop in component.props:
                if prop.name == 'Rule_Id':
                    rval.append(prop.value)
        return rval

    def get_rule_sets(self):
        """Get rulesets."""
        rval = []
        for component in self.component_generator():
            if component.props:
                for prop in component.props:
                    if prop.name == 'Rule_Id':
                        if prop.remarks in rval:
                            continue
                        rval.append(prop.remarks)
        return rval

    def get_ruleset_rule(self, ruleset: str):
        """Get ruleset rule."""
        rval = None
        for component in self.component_generator():
            if component.props:
                for prop in component.props:
                    if prop.remarks != ruleset:
                        continue
                    if prop.name != 'Rule_Id':
                        continue
                    rval = prop.value
                    break
        return rval

    def get_ruleset_check(self, ruleset: str):
        """Get ruleset check."""
        rval = None
        for component in self.component_generator():
            if component.props:
                for prop in component.props:
                    if prop.remarks != ruleset:
                        continue
                    if prop.name != 'Check_Id':
                        continue
                    rval = prop.value
                    break
        return rval

    def get_check_to_rule_map(self):
        """Get check to rule map."""
        rval = {}
        rulesets = self.get_rule_sets()
        for ruleset in rulesets:
            rule = self.get_ruleset_rule(ruleset)
            check = self.get_ruleset_check(ruleset)
            if rule and check:
                rval[check] = rule
                logger.debug(f'{ruleset}: {check} -> {rule}')
        return rval


class MCHelper:
    """OSCAL MC Helper."""

    def __init__(self, path: pathlib.Path) -> None:
        """Initialize."""
        self.path = path

    def read(self) -> None:
        """Read."""
        self.mc = MappingCollection.oscal_read(self.path)
    
    def prop_generator(self) -> Iterator[Property]:
        """Prop generator."""
        for mapping in self.mc.mappings:
            for map in mapping.maps:
                for prop in map.props:
                    yield prop
                    
    def get_checks(self) -> List[str]:
        """Get checks."""
        rval = []
        for prop in self.prop_generator():
            if prop.name != 'target_rules_list':
                continue
            rules = prop.value.strip().split(',')
            for rule in rules:
                if rule not in rval:
                    rval.append(rule)
        return rval
    
    def get_rules(self, props: List[Dict]) -> List[str]:
        """Get rules."""
        rval = []
        for prop in props:
            if prop.name == 'target_rules_list':
                rval = prop.value.split()
                break
        return rval

    def get_controls(self, sources: List[Dict]) -> List[str]:
        """Get controls."""
        rval = []
        for source in sources:
            rval.append(source.id_ref)
        return rval

    def get_tuples(self) -> List:
        """Get tuples."""
        rval = []
        for mapping in self.mc.mappings:
            source_resource = mapping.source_resource.href
            for map_ in mapping.maps:
                rules = self.get_rules(map_.props)
                controls = self.get_controls(map_.sources)
                for rule in rules:
                    for control in controls:
                        item = [rule, source_resource, control]
                        rval.append(item)
        return rval


class ControlImplementationHelper:
    """ControlImplementation Helper."""

    @classmethod
    def get_rules(cls, component: DefinedComponent) -> List:
        """Get rules."""
        rval = []
        if component.props:
            for prop in component.props:
                if prop.name == 'Rule_Id':
                    rval.append(prop.value)
        return rval
    
    @classmethod
    def drop_rule(cls, component: DefinedComponent, rule: str) -> None:
        """Drop rule."""
        ruleset = None
        if component.props:
            for prop in component.props:
                if prop.name == 'Rule_Id':
                    ruleset = prop.remarks
        props = component.props
        component.props = []
        for prop in props:
            if prop.remarks != ruleset:
                component.props.append(prop)
            else:
                print(f'drop: {component.title} {rule} {ruleset}')
    
    @classmethod
    def get_control_implementations(cls, component: DefinedComponent, mc_tuples: List) -> List[ControlImplementation]:
        """Get control implementations."""
        rval = None
        rules = ControlImplementationHelper.get_rules(component)
        implemented_requirements = []
        source = ''
        for rule in rules:
            for mc_tuple in mc_tuples:
                if mc_tuple[0] != rule:
                    continue
                implemented_requirement = ImplementedRequirement(
                    uuid=str(uuid.uuid4()), control_id=mc_tuple[2], description=''
                )
                implemented_requirements.append(implemented_requirement)
                source = mc_tuple[1]
        if implemented_requirements:
            control_implementation = ControlImplementation(
                uuid=str(uuid.uuid4()),
                source=source,
                description='',
                implemented_requirements=implemented_requirements
            )
            rval = [control_implementation]
        return rval


class SynthesizeOscalComponentDefinition(TaskBase):
    """
    Task to create OSCAL ComponentDefinition json.

    Attributes:
        name: Name of the task.
    """

    name = 'synthesize-oscal-cd'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task synthesize-oscal-cd.

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)

    def print_info(self) -> None:
        """Print the help string."""
        name = self.name
        oscal_name = 'component_definition'
        #
        logger.info(f'Help information for {name} task.')
        logger.info('')
        logger.info(f'Purpose: From csv produce OSCAL {oscal_name} file.')
        logger.info('')
        logger.info('')
        logger.info(f'Configuration flags sit under [task.{name}]:')
        text1 = '  title                = '
        text2 = '(required) the component definition title.'
        logger.info(text1 + text2)
        text1 = '  version              = '
        text2 = '(required) the component definition version.'
        logger.info(text1 + text2)
        text1 = '  cd                   = '
        text2 = '(required) the path of the component-definition .json file.'
        logger.info(text1 + text2)
        text1 = '  mc                   = '
        text2 = '(required) the path of the mapping-collection .json file.'
        logger.info(text1 + text2)
        text1 = '  output-dir           = '
        text2 = '(required) the path of the output directory for synthesized OSCAL .json files.'
        logger.info(text1 + text2)
        text1 = '  output-overwrite     = '
        text2 = '(optional) true [default] or false; replace existing output when true.'
        logger.info(text1 + text2)

    def configure(self) -> bool:
        """Configure."""
        self._timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc
                                                                                    ).isoformat()
        # config verbosity
        self._quiet = self._config.get('quiet', False)
        self._verbose = not self._quiet
        # title
        self._title = self._config.get('title')
        if self._title is None:
            logger.warning('config missing "title"')
            return False
        # version
        self._version = self._config.get('version')
        if self._version is None:
            logger.warning('config missing "version"')
            return False
        # config cd
        self._cd = self._config.get('cd')
        if self._cd is None:
            logger.warning('config missing "cd"')
            return False
        self._cd_path = pathlib.Path(self._cd)
        if not self._cd_path.exists():
            logger.warning('"cd" not found')
            return False
        # announce cd
        if self._verbose:
            logger.info(f'input (cd): {self._cd}')
        # config mc
        self._mc = self._config.get('mc')
        if self._mc is None:
            logger.warning('config missing "mc"')
            return False
        self._mc_path = pathlib.Path(self._mc)
        if not self._mc_path.exists():
            logger.warning('"mc" not found')
            return False
        # announce mc
        if self._verbose:
            logger.info(f'input (mc): {self._mc}')
        # config output
        odir = self._config.get('output-dir')
        opth = pathlib.Path(odir)
        # announce output
        self._ofile = opth / 'component-definition.json'
        if self._verbose:
            logger.info(f'output (cd): {self._ofile}')
        self._overwrite = self._config.getboolean('output-overwrite', True)
        # insure output dir exists
        opth.mkdir(exist_ok=True, parents=True)
        return True

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        return TaskOutcome('simulated-success')

    def execute(self) -> TaskOutcome:
        """Provide an executed outcome."""
        try:
            return self._execute()
        except Exception:
            logger.error(traceback.format_exc())
            return TaskOutcome('failure')
        
    def _execute(self) -> TaskOutcome:
        """Execute path core."""
        self.configure()
        cd_helper = CDHelper(self._cd_path, None, None)
        cd_helper.read()
        mc_helper = MCHelper(self._mc_path)
        mc_helper.read()
        mc_tuples = mc_helper.get_tuples()
        # calculate rules to include
        check_to_rule_map = {}
        cd_check_to_rule_map = cd_helper.get_check_to_rule_map()
        mc_checks = mc_helper.get_checks()
        for check in mc_checks:
            if check in cd_check_to_rule_map.keys():
                check_to_rule_map[check] = cd_check_to_rule_map[check]
        logger.debug(f'original: {len(cd_check_to_rule_map)}')
        logger.debug(f'redacted: {len(check_to_rule_map)}')
        # 
        cd_synth_helper = CDHelper(self._ofile, self._title, self._version)
        for component in cd_helper.component_generator():
            
            rules = ControlImplementationHelper.get_rules(component)
            for rule in rules:
                if rule in check_to_rule_map.values():
                    continue
                ControlImplementationHelper.drop_rule(component, rule)
            
            component.control_implementations = ControlImplementationHelper.get_control_implementations(
                component, mc_tuples
            )
            cd_synth_helper.component_add(component)
        cd_synth_helper.write()
        return TaskOutcome('success')
