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
from typing import Dict, Iterator, List, Optional

from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.oscal.catalog import Catalog
from trestle.oscal.common import Property
from trestle.oscal.component import ComponentDefinition
from trestle.oscal.component import DefinedComponent
from trestle.oscal.mapping import MappingCollection
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome

logger = logging.getLogger(__name__)

timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc).isoformat()


class MCHelper:
    """OSCAL MC Helper."""

    def __init__(self, path: pathlib.Path) -> None:
        """Initialize."""
        self.path = path
        self.checks_map = {}
        self._read()
        self._enforce_limitation()
        self._create_checks_map()

    def _read(self) -> None:
        """Read."""
        self.mc = MappingCollection.oscal_read(self.path)
        self.mapping = self.mc.mappings[0]
        self.catalog_helper = CatalogHelper(pathlib.Path(self.mapping.source_resource.href))

    def _enforce_limitation(self):
        """Enforce limitation."""
        if len(self.mc.mappings) != 1:
            text = 'Expected exactly one mapping: {self.path}'
            raise RuntimeError(text)

    def _create_checks_map(self):
        """Create checks map."""
        for _map in self.mapping.maps:
            control = self._get_control(_map)
            checks = self._get_checks(_map)
            for check in checks:
                if check not in self.checks_map.keys():
                    self.checks_map[check] = []
                if control not in self.checks_map[check]:
                    self.checks_map[check].append(control)

    def _get_checks(self, _map: Dict) -> List[str]:
        """Get checks."""
        rval = []
        for prop in _map.props:
            if prop.name != 'target_rules_list':
                continue
            rval = prop.value.split(',')
            break
        return rval

    def _get_control(self, _map: Dict) -> str:
        """Get control."""
        rval = []
        for source in _map.sources:
            if source.type != 'control':
                continue
            rval = source.id_ref
            break
        return rval

    def get_source_href(self) -> str:
        """Get source href."""
        return self.mapping.source_resource.href

    def get_source_title(self) -> str:
        """Get source title."""
        return self.mc.metadata.title.replace('Mapping Collection for ', '')

    def get_control_ids_for_check_id(self, check_id: str) -> List[str]:
        """Get control ids for check id."""
        rval = []
        if check_id in self.checks_map.keys():
            rval = self.checks_map[check_id]
        return rval


class CDHelper:
    """OSCAL CD Helper."""

    def __init__(self, path: pathlib.Path) -> None:
        """Initialize."""
        self.path = path
        self.rule_sets = []
        self.prop_names = []
        self.rule_id_to_check_id_map = {}
        self.check_id_to_check_description = {}
        self._read()
        self._process()

    def _read(self) -> None:
        """Read."""
        self.cd = ComponentDefinition.oscal_read(self.path)

    def _process(self) -> None:
        """Process."""
        for component in self.component_generator():
            if component.type.lower() == 'validation':
                self._validation(component)
            else:
                self._non_validation(component)

    def _get_cd_ruleset_value(self, rule_set: str, name: str, props: List[Property]) -> str:
        """Get value of name in ruleset."""
        rval = ''
        for prop in props:
            if prop.remarks != rule_set:
                continue
            if prop.name != name:
                continue
            rval = prop.value
            break
        return rval

    def _add_rule(self, rule_id: str, check_id: str):
        """Add rule."""
        if rule_id not in self.rule_id_to_check_id_map:
            self.rule_id_to_check_id_map[rule_id] = []
        if check_id not in self.rule_id_to_check_id_map[rule_id]:
            self.rule_id_to_check_id_map[rule_id].append(check_id)

    def _validation(self, component: DefinedComponent) -> None:
        """Process validation."""
        rule_sets = []
        # find all rule sets
        for prop in component.props:
            if prop.remarks not in rule_sets:
                rule_sets.append(prop.remarks)
        # create maps
        for rule_set in rule_sets:
            rule_id = self._get_cd_ruleset_value(rule_set, 'Rule_Id', component.props)
            check_id = self._get_cd_ruleset_value(rule_set, 'Check_Id', component.props)
            check_description = self._get_cd_ruleset_value(rule_set, 'Check_Description', component.props)
            self._add_rule(rule_id, check_id)
            self.check_id_to_check_description[check_id] = check_description

    def _non_validation(self, component: DefinedComponent) -> None:
        """Process non-validation."""
        props = component.props
        for prop in props:
            if prop.remarks not in self.rule_sets:
                self.rule_sets.append(prop.remarks)
            if prop.name not in self.prop_names:
                self.prop_names.append(prop.name)

    def get_prop_names(self):
        """Get prop names."""
        return self.prop_names

    def get_check_ids_for_rule(self, rule_id: str) -> List[str]:
        """Get check ids for rule."""
        rval = []
        if rule_id in self.rule_id_to_check_id_map.keys():
            rval = self.rule_id_to_check_id_map[rule_id]
        return rval

    def component_generator(self) -> Iterator[Dict]:
        """Component generator."""
        for component in self.cd.components:
            yield component


class ControlsHelper:
    """Controls Helper."""

    def __init__(self, mc_helper: MCHelper, cd_helper: CDHelper) -> None:
        """Initialize."""
        self.mc_helper = mc_helper
        self.cd_helper = cd_helper

    def get_source_href(self):
        """Get source href."""
        return self.mc_helper.get_source_href()

    def get_source_title(self):
        """Get source title."""
        return self.mc_helper.get_source_title()

    def get_mappped_controls_for_rule_id(self, rule_id: str) -> List[str]:
        """Get mapped controls for rule."""
        rval = []
        # get all checks for rule
        check_ids = self.cd_helper.get_check_ids_for_rule(rule_id)
        # for each check, get all controls
        for check_id in check_ids:
            control_ids = self.mc_helper.get_control_ids_for_check_id(check_id)
            # add each control to list, if not already present
            for control_id in control_ids:
                if control_id not in rval:
                    rval.append(control_id)
        return rval


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
        'A description of the component including information about its function.',  # noqa
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
    head_extra = []
    rows = []

    def __init__(self, path: pathlib.Path, controls_helper: ControlsHelper) -> None:
        """Initialize."""
        self.path = path
        self.controls_helper = controls_helper

    def _init_headings(self):
        """Initialize headings."""
        if not len(self.rows):
            for name in self.head_extra:
                self.head0.append(name)
                self.head1.append(name)
            self.rows.append(self.head0)
            self.rows.append(self.head1)

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
        if not rval:
            rval = self._get_profile_source(defined_component)
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

    def add_head_extra(self, headings: List[str]):
        """Add extra headings."""
        normalized_headings = []
        for h in self.head0:
            normalized_headings.append(h.replace('$', ''))
        for heading in headings:
            if heading not in normalized_headings:
                if heading not in self.head_extra:
                    self.head_extra.append(heading)

    def _get_csv_ruleset_value(self, ruleset: Dict, name: str) -> str:
        """Get ruleset  value."""
        rval = ''
        if name in ruleset.keys():
            rval = ruleset[name]
        return rval

    def _get_parameter_value_default(self, defined_component: DefinedComponent, parameter_id: str) -> str:
        """Get parameter value default."""
        rval = ''
        if defined_component.control_implementations:
            for control_implementation in defined_component.control_implementations:
                if control_implementation.set_parameters:
                    for set_parameter in control_implementation.set_parameters:
                        if set_parameter.param_id == parameter_id:
                            rval = ','.join(set_parameter.values)
                            break
                    if rval:
                        break
        return rval

    def component_add(self, defined_component: DefinedComponent) -> None:
        """Component add."""
        self._init_headings()
        rule_sets = self._get_rule_sets(defined_component)
        profile_source = self.controls_helper.get_source_href()
        profile_description = self.controls_helper.get_source_title()
        for rule_set in rule_sets.values():
            # get column values
            rule_id = self._get_csv_ruleset_value(rule_set, 'Rule_Id')
            control_id_list = self.controls_helper.get_mappped_controls_for_rule_id(rule_id)
            if not control_id_list:
                continue
            control_ids = ' '.join(control_id_list)
            rule_description = self._get_csv_ruleset_value(rule_set, 'Rule_Description')
            if defined_component.type.lower() == 'validation':
                parameter_id = ''
                parameter_description = ''
                parameter_value_alternatives = ''
                parameter_value_default = ''
            else:
                parameter_id = self._get_csv_ruleset_value(rule_set, 'Parameter_Id')
                parameter_description = self._get_csv_ruleset_value(rule_set, 'Parameter_Description')
                parameter_value_alternatives = self._get_csv_ruleset_value(rule_set, 'Parameter_Value_Alternatives')
                parameter_value_default = self._get_parameter_value_default(defined_component, parameter_id)
            check_id = self._get_csv_ruleset_value(rule_set, 'Check_Id')
            check_description = self._get_csv_ruleset_value(rule_set, 'Check_Description')
            namespace = self._get_csv_ruleset_value(rule_set, 'Namespace')
            # add column values to row
            row = []
            row.append(defined_component.title)
            row.append(defined_component.description)
            row.append(defined_component.type)
            row.append(rule_id)
            row.append(rule_description)
            row.append(parameter_id)
            row.append(parameter_description)
            row.append(parameter_value_alternatives)
            row.append(parameter_value_default)
            row.append(profile_source)
            row.append(profile_description)
            row.append(control_ids)
            row.append(check_id)
            row.append(check_description)
            row.append(namespace)
            for name in self.head_extra:
                if defined_component.type.lower() == 'validation':
                    value = ''
                else:
                    value = self._get_csv_ruleset_value(rule_set, name)
                row.append(value)
            # add row to rows
            self.rows.append(row)

    def write(self) -> None:
        """Write."""
        with open(self.path, 'w', newline='', encoding='utf-8') as output:
            csv_writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in self.rows:
                csv_writer.writerow(row)


class CatalogHelper:
    """OSCAL Catalog Helper."""

    def __init__(self, path: pathlib.Path) -> None:
        """Initialize."""
        self.path = path
        self._read()

    def _read(self) -> None:
        """Read."""
        self.catalog = Catalog.oscal_read(self.path)
        self.catalog_interface = CatalogInterface(self.catalog)
        self._create_map_control_id_to_title()

    def _create_map_control_id_to_title(self) -> None:
        """Create map."""
        self.map_control_id_to_title = {}
        for control_id in self.get_control_ids():
            control = self.catalog_interface.get_control(control_id)
            self.map_control_id_to_title[control.id] = control.title

    def get_title(self, control_id: str) -> str:
        """Get title."""
        return self.map_control_id_to_title[control_id]

    def get_control_ids(self) -> List[str]:
        """Get control ids."""
        return self.catalog_interface.get_control_ids()


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
        mc_helper = MCHelper(self._mc_path)
        controls_helper = ControlsHelper(mc_helper, cd_helper)
        csv_helper = CsvHelper(self._ofile, controls_helper)
        # process components
        csv_helper.add_head_extra(cd_helper.get_prop_names())
        for component in cd_helper.component_generator():
            csv_helper.component_add(component)
        csv_helper.write()
        return TaskOutcome('success')
