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
"""OSCAL transformation tasks."""

import configparser
import datetime
import json
import logging
import pathlib
import traceback
import uuid
from typing import Dict, List, Optional, Tuple

import trestle
from trestle.core import const
from trestle.oscal import OSCAL_VERSION
from trestle.oscal.common import Metadata
from trestle.oscal.common import Party
from trestle.oscal.common import Property
from trestle.oscal.common import ResponsibleParty
from trestle.oscal.common import ResponsibleRole
from trestle.oscal.common import Role
from trestle.oscal.component import ComponentDefinition
from trestle.oscal.component import ControlImplementation
from trestle.oscal.component import DefinedComponent
from trestle.oscal.component import ImplementedRequirement
from trestle.oscal.component import SetParameter
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome

logger = logging.getLogger(__name__)


class CisToComponentDefinition(TaskBase):
    """
    Task to CIS to component definition from standard (e.g. CIS benchmark).

    Attributes:
        name: Name of the task.
    """

    name = 'cis-to-component-definition'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task cis-to-component-definition.

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)
        self._timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc
                                                                                    ).isoformat()

    def set_timestamp(self, timestamp: str) -> None:
        """Set the timestamp."""
        self._timestamp = timestamp

    def print_info(self) -> None:
        """Print the help string."""
        root_trestle = '/home/degenaro/git/shared-trestle-workspace.oscal-for-osco'
        logger.info(f'Help information for {self.name} task.')
        logger.info('')
        logger.info('Purpose: Create component definition from from standard (e.g. CIS benchmark).')
        logger.info('')
        logger.info('Configuration flags sit under [task.cis-to-component-definition]:')
        text1 = '  component-name         = '
        text2 = 'component name, e.g. OSCO.'
        logger.info(text1 + text2)
        text1 = '  org-name               = '
        text2 = 'organization name, e.g. International Business Machines.'
        logger.info(text1 + text2)
        text1 = '  org-remarks            = '
        text2 = 'organization remarks, e.g. IBM.'
        logger.info(text1 + text2)
        text1 = '  output-dir             = '
        text2 = 'location to write the generated component-definition.json file.'
        logger.info(text1 + text2)
        #
        text1 = '  profile-name           = '
        text2 = 'profile name, e.g. OCP4 CIS-benchmark v4.'
        logger.info(text1 + text2)
        text1 = '  profile-mnemonic       = '
        text2 = 'profile mnemonic, e.g. ocp4-cis-node.'
        logger.info(text1 + text2)
        text1 = '  profile-ns             = '
        text2 = 'profile ns, e.g. https://github.com/ComplianceAsCode/content/tree/master/ocp4.'
        logger.info(text1 + text2)
        text1 = '  profile-version        = '
        text2 = 'profile version, e.g. 1.1.'
        logger.info(text1 + text2)
        text1 = '  profile-check-version  = '
        text2 = 'profile check version, e.g. 0.1.58.'
        logger.info(text1 + text2)
        #
        text1 = '  profile-type           = '
        text2 = 'profile type, e.g. OCP4.'
        logger.info(text1 + text2)
        text1 = '  profile-list           = '
        text2 = 'profile list is blank separated list of "<suffix>" for config entries: '
        logger.info(text1 + text2)
        text1 = '                           profile-file.<suffix>, profile-title.<suffix>, profile-url.<suffix>'
        text2 = ', e.g. cis cis-node.'
        logger.info(text1 + text2)
        text1 = '  profile-file.<suffix>  = '
        text2 = 'path of the profile file to ingest'
        text3 = ', e.g. /home/degenaro/git/compliance-as-code.content/products/ocp4/profiles/cis-node.profile.'
        logger.info(text1 + text2 + text3)
        text1 = '  profile-title.<suffix> = '
        text2 = 'title of the profile'
        text3 = ', e.g. CIS Red Hat OpenShift Container Platform 4 Benchmark.'
        logger.info(text1 + text2 + text3)
        text1 = '  profile-url.<suffix>   = '
        text2 = 'URL of the profile'
        text3 = ', e.g. https://github.com/ComplianceAsCode/content/blob/master/products/ocp4/profiles/cis.profile.'
        logger.info(text1 + text2 + text3)
        text1 = '  rule-to-parameters-map = '
        text2 = 'map file for set-parameters, e.g. '
        text3 = root_trestle + '/component-definitions/osco/rule2var.json.'
        logger.info(text1 + text2 + text3)
        text1 = '  selected-rules         = '
        text2 = 'file with list of selected rules, e.g. '
        text3 = root_trestle + '/component-definitions/osco/selected_rules.json.'
        logger.info(text1 + text2 + text3)
        text1 = '  enabled-rules          = '
        text2 = 'file with list of enabled rules, e.g. '
        text3 = root_trestle + '/component-definitions/osco/enabled_rules.json.'
        logger.info(text1 + text2 + text3)
        #
        text = ''
        logger.info(text)
        text = 'Notes:'
        logger.info(text)
        text = '1. If a control has selected rules but no enabled rules, then all those selected are included.'
        logger.info(text)
        text = '2. If a control has selected and enabled rules, then only those enabled are included.'
        logger.info(text)
        text = '3. If a control has no selected rules, then none are included regardless of enabled.'
        logger.info(text)

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        return TaskOutcome('simulated-success')

    def execute(self) -> TaskOutcome:
        """Provide an actual outcome."""
        try:
            return self._execute()
        except Exception:
            logger.info(traceback.format_exc())
            return TaskOutcome('failure')

    def _execute(self) -> TaskOutcome:
        if not self._config:
            logger.error('config missing')
            return TaskOutcome('failure')
        try:
            component_name = self._config['component-name']
            org_name = self._config['org-name']
            org_remarks = self._config['org-remarks']
            profile_check_version = self._config['profile-check-version']
            profile_type = self._config['profile-type']
            profile_mnemonic = self._config['profile-mnemonic']
            profile_name = self._config['profile-name']
            profile_ns = self._config['profile-ns']
            profile_version = self._config['profile-version']
            profile_sets = {}
            profile_list = self._config['profile-list'].split()
            for profile in profile_list:
                profile_sets[profile] = {}
                profile_sets[profile]['profile-file'] = self._config[f'profile-file.{profile}']
                profile_sets[profile]['profile-url'] = self._config[f'profile-url.{profile}']
                profile_sets[profile]['profile-title'] = self._config[f'profile-title.{profile}']
                profile_sets[profile]['profile-ns'] = profile_ns
                profile_sets[profile]['component-name'] = component_name
            odir = self._config['output-dir']
        except KeyError as e:
            logger.info(f'key {e.args[0]} missing')
            return TaskOutcome('failure')
        # selected rules
        self._selected_rules = self._get_filter_rules('selected-rules', 'selected')
        # enabled rules
        self._enabled_rules = self._get_filter_rules('enabled-rules', 'enabled')
        # verbosity
        quiet = self._config.get('quiet', False)
        verbose = not quiet
        # output
        overwrite = self._config.getboolean('output-overwrite', True)
        opth = pathlib.Path(odir)
        # insure output dir exists
        opth.mkdir(exist_ok=True, parents=True)
        # calculate output file name & check writability
        oname = 'component-definition.json'
        ofile = opth / oname
        if not overwrite and pathlib.Path(ofile).exists():
            logger.error(f'output: {ofile} already exists')
            return TaskOutcome('failure')
        # fetch rule to parameters map
        self._rule_to_parm_map = self._get_parameters_map('rule-to-parameters-map')
        # roles, responsible_roles, parties, responsible parties
        party_uuid_01 = str(uuid.uuid4())
        party_uuid_02 = str(uuid.uuid4())
        party_uuid_03 = str(uuid.uuid4())
        roles = self._build_roles()
        responsible_roles = self._build_responsible_roles(party_uuid_01, party_uuid_02, party_uuid_03)
        parties = self._build_parties(org_name, org_remarks, party_uuid_01, party_uuid_02, party_uuid_03)
        responsible_parties = self._build_responsible_parties(party_uuid_01, party_uuid_02, party_uuid_03)
        # metadata
        metadata = Metadata(
            title=f'Component definition for {profile_type} profiles',
            last_modified=self._timestamp,
            oscal_version=OSCAL_VERSION,
            version=trestle.__version__,
            roles=roles,
            parties=parties,
            responsible_parties=responsible_parties
        )
        # defined component
        component_title = component_name
        component_description = component_name
        defined_component = DefinedComponent(
            uuid=str(uuid.uuid4()),
            description=component_description,
            title=component_title,
            type='Service',
        )
        # add control implementation per profile
        prop1 = Property(
            name='profile_name',
            value=profile_name,
            class_='scc_profile_name',
            ns=profile_ns,
        )
        prop2 = Property(
            name='profile_mnemonic',
            value=profile_mnemonic,
            class_='scc_profile_mnemonic',
            ns=profile_ns,
        )
        prop3 = Property(
            name='profile_version',
            value=profile_version,
            class_='scc_profile_version',
            ns=profile_ns,
        )
        prop4 = Property(
            name='profile_check_version',
            value=profile_check_version,
        )
        props = [prop1, prop2, prop3, prop4]
        for profile in profile_list:
            profile_set = profile_sets[profile]
            control_implementation = self._build_control_implementation(profile_set, responsible_roles, props)
            if control_implementation is not None:
                if defined_component.control_implementations is None:
                    defined_component.control_implementations = [control_implementation]
                else:
                    defined_component.control_implementations.append(control_implementation)
        # defined components
        defined_components = [defined_component]
        # component definition
        component_definition = ComponentDefinition(
            uuid=str(uuid.uuid4()),
            metadata=metadata,
            components=defined_components,
        )
        # write OSCAL ComponentDefinition to file
        if verbose:
            logger.info(f'output: {ofile}')
        component_definition.oscal_write(pathlib.Path(ofile))
        return TaskOutcome('success')

    def _get_set_parameter(self, rule: str) -> SetParameter:
        """Get set parameter."""
        set_parameter = None
        for key in self._rule_to_parm_map.keys():
            logger.debug(f'{key} {rule}')
            if key == rule:
                value = self._rule_to_parm_map[key]
                remarks = value['description']
                options = value['options']
                default_value = options['default']
                logger.debug(f'key: {key} options: {options}')
                set_parameter = SetParameter(
                    param_id=rule,
                    values=[f'{default_value}'],
                    remarks=remarks,
                )
        return set_parameter

    def _get_controls(self, rules: Dict[str, Tuple[str, str, str]]) -> Dict[str, List[str]]:
        """Get controls."""
        controls = {}
        for rule in rules.keys():
            control = rules[rule][1]
            if control not in controls.keys():
                controls[control] = [rule]
            else:
                controls[control] = controls[control] + [rule]
        # trim rules associated with control with respect to enabled rules
        for control in controls:
            controls[control] = self._get_trimmed_rules(control, controls[control])
            logger.debug(f'{control} {controls[control]}')
        return controls

    # determine if trim is needed for the control, and if so then
    # for the associated set of rules drop those that are not enabled
    def _get_trimmed_rules(self, control: str, rules_for_control: List[str]) -> List[str]:
        """Trim rules if any rule for control appears in enabled rules list."""
        retval = rules_for_control
        if self._is_trim_needed(rules_for_control):
            retval = []
            for rule in rules_for_control:
                if rule in self._enabled_rules:
                    retval = retval + [rule]
                    logger.debug(f'keep {control} {rule}')
                else:
                    logger.debug(f'drop {control} {rule}')
        return retval

    # if any rule in the set of rules for the control appears in the enabled list,
    # then trim is needed
    def _is_trim_needed(self, rules_for_control: List[str]) -> bool:
        """Check if trim is needed."""
        retval = False
        for rule in rules_for_control:
            if rule in self._enabled_rules:
                retval = True
                break
        return retval

    # fetch the set of rules that will be included/excluded from the CIS rules
    def _get_parameters_map(self, config_key: str) -> List[str]:
        """Get parameters map."""
        try:
            fp = pathlib.Path(self._config[config_key])
            f = fp.open('r', encoding=const.FILE_ENCODING)
            jdata = json.load(f)
            parameters_map = jdata
            f.close()
        except KeyError as e:
            logger.debug(f'key {e.args[0]} missing')
            parameters_map = {}
        except Exception:
            logger.error(f'unable to process {self._config[config_key]}')
            parameters_map = {}
        return parameters_map

    # fetch the set of rules that will be included/excluded from the CIS rules
    def _get_filter_rules(self, config_key: str, file_key: str) -> List[str]:
        """Get filter rules."""
        try:
            fp = pathlib.Path(self._config[config_key])
            f = fp.open('r', encoding=const.FILE_ENCODING)
            jdata = json.load(f)
            try:
                filter_rules = jdata[file_key]
            except Exception:
                filter_rules = jdata
            f.close()
        except KeyError as e:
            logger.debug(f'key {e.args[0]} missing')
            filter_rules = []
        except Exception:
            logger.error(f'unable to process {self._config[config_key]}')
            filter_rules = []
        return filter_rules

    # create map from file:
    # key is rule
    # value is tuple comprising [ category, control, description ]
    def _get_cis_rules(self, filename: str) -> Dict[str, Tuple[str, str, str]]:
        """Get CIS rules."""
        try:
            fp = pathlib.Path(filename)
            f = fp.open('r', encoding=const.FILE_ENCODING)
            content = f.readlines()
            rules = self._parse_cis_rules(content)
            f.close()
        except Exception:
            logger.error(f'unable to process {filename}')
            rules = {}
        return rules

    def _parse_cis_rules(self, content: List[str]) -> Dict[str, Tuple[str, str, str]]:
        """Parse CIS rules."""
        rules = {}
        lineno = 0
        for line in content:
            lineno += 1
            line = line.replace('\n', '')
            if line.startswith('  #### '):
                category = line.split('  #### ')[1]
                logger.debug(f'{lineno} category: {category}')
            elif line.startswith('  # '):
                text = line.split('  # ')[1].split(' ', 1)
                if '.' in text[0]:
                    control = text[0]
                    desc = text[1]
                    logger.debug(f'{lineno} control: {control} description: {desc}')
                else:
                    logger.debug(f'{lineno} skip: {line}')
            elif line.startswith('    - '):
                rule = line.split('    - ')[1]
                logger.debug(f'{lineno} rule: {rule}')
                if not self._is_selected(rule):
                    logger.debug(f'not selected rule: {rule}')
                elif rule in rules.keys():
                    logger.info(f'duplicate rule: {rule}')
                else:
                    rules[rule] = [category, control, desc]
            else:
                logger.debug(f'{lineno} skip: {line}')
        return rules

    # rule is selected if:
    # a) the selected rules file is not specified or is empty or
    # b) the rule appears in the list of selected rules from the file
    def _is_selected(self, rule: str) -> bool:
        """Check if rule is selected."""
        retval = True
        if len(self._selected_rules) > 0 and rule not in self._selected_rules:
            retval = False
        logger.debug(f'{retval} {rule}')
        return retval

    # rule is excluded if it does not appear in the list of trimmed rules
    # for the control
    def _is_excluded(self, rule: str, control: str, controls: Dict[str, List[str]]) -> bool:
        """Check if rule is excluded."""
        retval = False
        if rule not in controls[control]:
            logger.debug(f'exclude {rule} {control}')
            retval = True
        return retval

    def _build_roles(self) -> List[Role]:
        """Build roles."""
        value = [
            Role(id='prepared-by', title='Indicates the organization that created this content.'),
            Role(id='prepared-for', title='Indicates the organization for which this content was created..'),
            Role(
                id='content-approver',
                title='Indicates the organization responsible for all content represented in the "document".'
            ),
        ]
        return value

    def _build_control_implementation(
        self, profile_set: Dict[str, str], responsible_roles: List[ResponsibleRole], props: List[Property]
    ) -> ControlImplementation:
        """Build control implementation."""
        implemented_requirements = self._build_implemented_requirements(profile_set, responsible_roles)
        if len(implemented_requirements) == 0:
            control_implementation = None
        else:
            control_implementation = ControlImplementation(
                uuid=str(uuid.uuid4()),
                source=profile_set['profile-url'],
                description=f'{profile_set["component-name"]} implemented controls for {profile_set["profile-title"]}.',
                implemented_requirements=implemented_requirements,
                props=props,
            )
        return control_implementation

    def _build_implemented_requirements(self, profile_set: Dict[str, str],
                                        responsible_roles: List[ResponsibleRole]) -> List[ImplementedRequirement]:
        """Build implemented requirements."""
        implemented_requirements = []
        profile_file = profile_set['profile-file']
        rules = self._get_cis_rules(profile_file)
        controls = self._get_controls(rules)
        rule_prefix = 'xccdf_org.ssgproject.content_rule_'
        for rule in rules:
            if self._is_excluded(rule, rules[rule][1], controls):
                continue
            prop = Property(
                class_='scc_goal_name_id',
                ns=profile_set['profile-ns'],
                name='XCCDF_rule',
                value=f'{rule_prefix}{rule}',
                remarks=f'{rules[rule][2]}'
            )
            props = [prop]
            implemented_requirement = ImplementedRequirement(
                uuid=f'{str(uuid.uuid4())}',
                control_id=f'CIS-{rules[rule][1]}',
                description=f'{rules[rule][2]}',
                props=props,
                responsible_roles=responsible_roles,
            )
            set_parameter = self._get_set_parameter(rule)
            if set_parameter is not None:
                implemented_requirement.set_parameters = [set_parameter]
            implemented_requirements.append(implemented_requirement)
        return implemented_requirements

    def _build_responsible_roles(self, party_uuid_01: str, party_uuid_02: str,
                                 party_uuid_03: str) -> List[ResponsibleRole]:
        """Build responsible roles."""
        role_prepared_by = ResponsibleRole(role_id='prepared-by', party_uuids=[party_uuid_01])
        role_prepared_for = ResponsibleRole(role_id='prepared-for', party_uuids=[party_uuid_02, party_uuid_03])
        role_content_approver = ResponsibleRole(role_id='content-approver', party_uuids=[party_uuid_01])
        value = [
            role_prepared_by,
            role_prepared_for,
            role_content_approver,
        ]
        return value

    def _build_parties(
        self, org_name: str, org_remarks: str, party_uuid_01: str, party_uuid_02: str, party_uuid_03: str
    ) -> List[Party]:
        """Build parties."""
        value = [
            Party(uuid=party_uuid_01, type='organization', name=org_name, remarks=org_remarks),
            Party(
                uuid=party_uuid_02,
                type='organization',
                name='Customer',
                remarks='organization to be customized at account creation only for their Component Definition'
            ),
            Party(
                uuid=party_uuid_03,
                type='organization',
                name='ISV',
                remarks='organization to be customized at ISV subscription only for their Component Definition'
            ),
        ]
        return value

    def _build_responsible_parties(self, party_uuid_01: str, party_uuid_02: str,
                                   party_uuid_03: str) -> List[ResponsibleParty]:
        """Build responsible parties."""
        prepared_by = ResponsibleParty(role_id='prepared-by', party_uuids=[party_uuid_01])
        prepared_for = ResponsibleParty(role_id='prepared-for', party_uuids=[party_uuid_02, party_uuid_03])
        content_approver = ResponsibleParty(role_id='content-approver', party_uuids=[party_uuid_01])
        value = [
            prepared_by,
            prepared_for,
            content_approver,
        ]
        return value
