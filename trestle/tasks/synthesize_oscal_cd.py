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
import csv
import datetime
import logging
import pathlib
import traceback
import uuid
from typing import Dict, Iterator, List, Optional

from trestle.oscal.component import ComponentDefinition
from trestle.oscal.component import ControlImplementation
from trestle.oscal.component import DefinedComponent
from trestle.oscal.component import ImplementedRequirement
from trestle.oscal.mapping import MappingCollection
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome

logger = logging.getLogger(__name__)

timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc).isoformat()


class CsvHelper:
    """Component Definition Csv Helper."""

    head0 = [
        '$$Component_Title',
        '$$Component_Description',
        '$$Component_Type',
        '$$Rule_Id',
        '$$Rule_Description',
        '$Parameter_Id',
        '$Parameter_Description',
        '$Parameter_Value_Alternatives',
        '$Parameter_Value_Default',
        '$$Profile_Source',
        '$$Profile_Description',
        '$$Control_Id_List',
        '$Check_Id',
        '$Check_Description',
        '$$Namespace',
    ]
    head1 = [
        'A human readable name for the component.',  # noqa
        'A description of the component including information about its function.'  # noqa
        'A category describing the purpose of the component. ALLOWED VALUES interconnection:software:hardware:service:physical:process-procedure:plan:guidance:standard:validation:',  # noqa
        'A textual label that uniquely identifies a policy (desired state) that can be used to reference it elsewhere in this or other documents.',  # noqa
        'A description of the policy (desired state) including information about its purpose and scope.',  # noqa
        'A textual label that uniquely identifies the parameter associated with that policy (desired state) or controls implemented by the policy (desired state).',  # noqa
        'A description of the parameter including the purpose and use of the parameter.',  # noqa
        'ONLY for the policy (desired state) parameters: A value or set of values the parameter can take. The catalog parameters values are defined in the catalog. ',  # noqa
        'A value recommended by Compliance Team in this profile for the parameter of the control or policy (desired state). If a CIS-benchmark exists, the default default could be the CIS-benchmark recommended value.',  # noqa
        'A URL reference to the source catalog or profile for which this component is implementing controls for. A profile designates a selection and configuration of controls from one or more catalogs',  # noqa
        'A description of the profile.',  # noqa
        'A list of textual labels that uniquely identify the controls or statements that the component implements.',  # noqa
        'A textual label that uniquely identifies a check of the policy (desired state) that can be used to reference it elsewhere in this or other documents.',  # noqa
        'A description of the check of the policy (desired state) including the method (interview or examine or test) and procedure details.',  # noqa
        'A namespace qualifying the property\'s name. This allows different organizations to associate distinct semantics with the same name. Used in conjunction with "class" as the ontology concept.',  # noqa
    ]
    rows = []
    rows.append(head0)
    rows.append(head1)

    def __init__(self, path: pathlib.Path) -> None:
        """Initialize."""
        self.path = path

    def _get_rule_sets(self, defined_component: DefinedComponent) -> Dict:
        """Get rule sets."""
        rval = {}
        props = defined_component.props
        for prop in props:
            key = prop.remarks
            if key not in rval:
                rval[key] = {}
            rval[key][prop.name] = prop.value
            if prop.name == 'Rule_Id':
                rval[key]['Namespace'] = prop.ns
        return rval

    def _get_profile_source(self, defined_component: DefinedComponent) -> str:
        """Get profile source."""
        rval = ''
        if defined_component.control_implementations:
            for control_implementation in defined_component.control_implementations:
                rval = control_implementation.source
                break
        return rval

    def _get_profile_description(self, defined_component: DefinedComponent) -> str:
        """Get profile description."""
        rval = ''
        if defined_component.control_implementations:
            for control_implementation in defined_component.control_implementations:
                rval = control_implementation.description
                break
        return rval

    def _get_control_id_list(self, defined_component: DefinedComponent) -> str:
        """Get control id  list."""
        rval = ''
        if defined_component.control_implementations:
            for control_implementation in defined_component.control_implementations:
                if control_implementation.implemented_requirements:
                    for implemented_requirement in control_implementation.implemented_requirements:
                        rval = f'{rval} {implemented_requirement.control_id}'
        return rval.strip()

    def add_column(self, row: List, ruleset: Dict, name: str):
        """Add column."""
        if name in ruleset.keys():
            row.append(ruleset[name])
        else:
            row.append('')

    def component_add(self, defined_component: DefinedComponent) -> None:
        """Component add."""
        rule_sets = self._get_rule_sets(defined_component)
        profile_source = self._get_profile_source(defined_component)
        profile_description = self._get_profile_description(defined_component)
        control_id_list = self._get_control_id_list(defined_component)
        for rule_set in rule_sets.values():
            row = []
            row.append(defined_component.title)
            row.append(defined_component.description)
            row.append(defined_component.type)
            self.add_column(row, rule_set, 'Rule_Id')
            self.add_column(row, rule_set, 'Rule_Description')
            self.add_column(row, rule_set, 'Parameter_Id')
            self.add_column(row, rule_set, 'Parameter_Description')
            self.add_column(row, rule_set, 'Parameter_Value_Alternatives')
            self.add_column(row, rule_set, 'Parameter_Value_Default')
            row.append(profile_source)
            row.append(profile_description)
            row.append(control_id_list)
            self.add_column(row, rule_set, 'Check_Id')
            self.add_column(row, rule_set, 'Check_Description')
            self.add_column(row, rule_set, 'Namespace')
            self.rows.append(row)

    def write(self) -> None:
        """Write."""
        with open(self.path, 'w', newline='', encoding='utf-8') as output:
            csv_writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in self.rows:
                csv_writer.writerow(row)


class CDHelper:
    """OSCAL CD Helper."""

    def __init__(self, path: pathlib.Path) -> None:
        """Initialize."""
        self.path = path

    def read(self) -> None:
        """Read."""
        self.cd = ComponentDefinition.oscal_read(self.path)

    def component_generator(self) -> Iterator[Dict]:
        """Component generator."""
        for component in self.cd.components:
            yield component


class MCHelper:
    """OSCAL MC Helper."""

    def __init__(self, path: pathlib.Path) -> None:
        """Initialize."""
        self.path = path

    def read(self) -> None:
        """Read."""
        self.mc = MappingCollection.oscal_read(self.path)

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
    Task to create OSCAL ComponentDefinition csv.

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
        text1 = '  cd                   = '
        text2 = '(required) the path of the component-definition .json file.'
        logger.info(text1 + text2)
        text1 = '  mc                   = '
        text2 = '(required) the path of the mapping-collection .json file.'
        logger.info(text1 + text2)
        text1 = '  output-dir           = '
        text2 = '(required) the path of the output directory for synthesized OSCAL .csv file.'
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
        self._odir = self._config.get('output-dir')
        self._opth = pathlib.Path(self._odir)
        # announce output
        self._ofile = self._opth / 'component-definition.csv'
        if self._verbose:
            logger.info(f'output (cd): {self._ofile}')
        self._overwrite = self._config.getboolean('output-overwrite', True)
        # insure output dir exists
        self._opth.mkdir(exist_ok=True, parents=True)
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
        # helpers
        cd_helper = CDHelper(self._cd_path)
        cd_helper.read()
        mc_helper = MCHelper(self._mc_path)
        mc_helper.read()
        mc_tuples = mc_helper.get_tuples()
        csv_helper = CsvHelper(self._ofile)
        # synthesize cd
        for component in cd_helper.component_generator():
            component.control_implementations = ControlImplementationHelper.get_control_implementations(
                component, mc_tuples
            )
            csv_helper.component_add(component)
        csv_helper.write()
        return TaskOutcome('success')
