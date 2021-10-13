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
"""OSCAL transformation tasks."""

import configparser
import datetime
import logging
import pathlib
import traceback
import uuid
from typing import Optional

from trestle import __version__
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
from trestle.oscal.profile import Profile
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome
from trestle.utils.oscal_helper import ProfileHelper

logger = logging.getLogger(__name__)


class BuildComponentDefinition(TaskBase):
    """
    Task to build component definition from standard (e.g. CIS benchmark).

    Attributes:
        name: Name of the task.
    """

    name = 'build-component-definition'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task build-component-definition.

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)
        self._timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc
                                                                                    ).isoformat()

    def print_info(self) -> None:
        """Print the help string."""
        logger.info(f'Help information for {self.name} task.')
        logger.info('')
        logger.info('Purpose: Build component definition from from standard (e.g. CIS benchmark).')
        logger.info('')
        logger.info('Configuration flags sit under [task.build-component-definition]:')
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
        text1 = '  profile-type           = '
        text2 = 'profile type, e.g. OCP4.'
        logger.info(text1 + text2)
        text1 = '  profile-ns             = '
        text2 = 'profile ns, e.g. https://github.com/ComplianceAsCode/content/tree/master/ocp4.'
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
        text3 = '/home/degenaro/git/shared-trestle-workspace.oscal-for-osco/component-definitions/osco/rule2var.json.'
        logger.info(text1 + text2 + text3)
        text1 = '  tailored-profile-file  = '
        text2 = 'profile containing include/exclude statements, e.g. '
        text3 = '/home/degenaro/git/shared-trestle-workspace.master/profiles/roks-ocp4-tailored-profile/profile.json.'
        logger.info(text1 + text2 + text3)
        
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
        # process config
        profile_list = self._config.get('profile-list')
        if profile_list is None:
            logger.error('config missing "profile-list" list')
            return TaskOutcome('failure')
        profile_list = profile_list.split()
        # component name
        component_name = self._config.get('component-name')
        if component_name is None:
            logger.error('config missing "component_name" ')
            return TaskOutcome('failure')
        # profiles
        profile_type = self._config.get('profile-type')
        if profile_type is None:
            logger.error('config missing "profile-type" ')
            return TaskOutcome('failure')
        profile_ns = self._config.get('profile-ns')
        if profile_ns is None:
            logger.error('config missing "profile-ns" ')
            return TaskOutcome('failure')
        for profile in profile_list:
            key = f'profile-file.{profile}'
            profile_file = self._config.get(key)
            if profile_file is None:
                logger.error(f'config missing "{key}"')
                return TaskOutcome('failure')
            key = f'profile-url.{profile}'
            profile_url = self._config.get(key)
            if profile_url is None:
                logger.error(f'config missing "{key}"')
                return TaskOutcome('failure')
            key = f'profile-title.{profile}'
            profile_title = self._config.get(key)
            if profile_title is None:
                logger.error(f'config missing "{key}"')
                return TaskOutcome('failure')
        # tailored-profile
        tailored_profile = self._config.get('tailored-profile-file')
        if tailored_profile is None:
            logger.debug('config missing "tailored-profile-file"')
            self.tailored_profile_helper = None
        else:
            self.tailored_profile_helper = ProfileHelper(tailored_profile)
            if not self.tailored_profile_helper.exists():
                logger.error('"tailored-profile-file" not found')
                return TaskOutcome('failure')
        # verbosity
        quiet = self._config.get('quiet', False)
        verbose = not quiet
        # output
        overwrite = self._config.getboolean('output-overwrite', True)
        odir = self._config.get('output-dir')
        if odir is None:
            logger.error('config missing "output-dir"')
            return TaskOutcome('failure')
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
        self._rule_to_parm_map = {}
        filepath = self._config.get('rule-to-parameters-map')
        if filepath is not None:
            import json
            with open(filepath) as f:
                self._rule_to_parm_map = json.load(f)

        # roles, responsible_roles, parties, responsible parties
        party_uuid_01 = str(uuid.uuid4())
        party_uuid_02 = str(uuid.uuid4())
        party_uuid_03 = str(uuid.uuid4())
        roles = self._build_roles()
        responsible_roles = self._build_responsible_roles(party_uuid_01, party_uuid_02, party_uuid_03)
        parties = self._build_parties(party_uuid_01, party_uuid_02, party_uuid_03)
        responsible_parties = self._build_responsible_parties(party_uuid_01, party_uuid_02, party_uuid_03)
        # metadata
        metadata = Metadata(
            title=f'Component definition for {self._get_profile_type} profiles',
            last_modified=self._get_timestamp,
            oscal_version=self._get_oscal_version,
            version=self._get_trestle_version,
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
            value=self._get_profile_name,
            class_='scc_profile_name',
            ns=self._get_profile_ns,
        )
        prop2 = Property(
            name='profile_version',
            value=self._get_profile_version,
            class_='scc_profile_version',
            ns=self._get_profile_ns,
        )
        props = [prop1, prop2] + self.tailored_profile_helper.get_metadata_properties()
        for profile in profile_list:
            control_implementation = self._build_control_implementation(profile, profile_ns, responsible_roles, props)
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

    @property
    def _get_timestamp(self):
        return self._timestamp

    @property
    def _get_trestle_version(self):
        return __version__

    @property
    def _get_oscal_version(self):
        return OSCAL_VERSION

    @property
    def _get_org_name(self) -> str:
        """Get org-name from config."""
        value = self._config.get('org-name')
        logger.debug(f'org-name: {value}')
        return value

    @property
    def _get_org_remarks(self) -> str:
        """Get org-remarks from config."""
        value = self._config.get('org-remarks')
        logger.debug(f'org-remarks: {value}')
        return value

    @property
    def _get_component_name(self) -> str:
        """Get component-name from config."""
        value = self._config.get('component-name')
        logger.debug(f'component-name: {value}')
        return value

    @property
    def _get_profile_name(self):
        """Get profile name from config."""
        value = self._config.get('profile-name')
        logger.debug(f'profile-name: {value}')
        return value
    
    @property
    def _get_profile_version(self):
        """Get profile version from config."""
        value = self._config.get('profile-version')
        logger.debug(f'profile-version: {value}')
        return value
        
    @property
    def _get_profile_ns(self):
        """Get profile ns from config."""
        value = self._config.get('profile-ns')
        logger.debug(f'profile-ns: {value}')
        return value
    
    @property
    def _get_profile_type(self):
        """Get profile type from config."""
        value = self._config.get('profile-type')
        logger.debug(f'profile-type: {value}')
        return value

    def _get_profile_url(self, profile) -> str:
        """Get profile url from config."""
        value = self._config.get(f'profile-url.{profile}')
        logger.debug(f'profile-url: {value}')
        return value

    def _get_profile_title(self, profile) -> str:
        """Get profile title from config."""
        value = self._config.get(f'profile-title.{profile}')
        logger.debug(f'profile-title: {value}')
        return value

    def _get_profile_file(self, profile) -> str:
        """Get profile file from config."""
        value = self._config.get(f'profile-file.{profile}')
        logger.debug(f'profile-file: {value}')
        return value

    def _get_set_parameter(self, rule):
        set_parameter = None
        for key in self._rule_to_parm_map.keys():
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

    def _get_rules(self, filename):
        rules = {}
        with open(filename) as f:
            content = f.readlines()
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
                if rule in rules.keys():
                    logger.info(f'duplicate rule: {rule}')
                else:
                    rules[rule] = [category, control, desc]
            else:
                logger.debug(f'{lineno} skip: {line}')
        return rules

    def _build_roles(self):
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

    def _build_control_implementation(self, profile, profile_ns, responsible_roles, props):
        implemented_requirements = self._build_implemented_requirements(profile, profile_ns, responsible_roles)
        control_implementation = ControlImplementation(
            uuid=str(uuid.uuid4()),
            source=self._get_profile_url(profile),
            description=f'{self._get_component_name} implemented controls for {self._get_profile_title(profile)}.',
            implemented_requirements=implemented_requirements,
            props=props,
        )
        return control_implementation

    def _build_implemented_requirements(self, profile, profile_ns, responsible_roles):
        implemented_requirements = []
        logger.info(f'{profile}')
        profile_file = self._get_profile_file(profile)
        rules = self._get_rules(profile_file)
        rule_prefix = 'xccdf_org.ssgproject.content_rule_'
        for rule in rules:
            logger.debug(f'{rule}: {rules[rule]}')
            rule_id = 'CIS-'+rules[rule][1]
            if self.tailored_profile_helper.is_filtered(rule_id):
                logger.debug(f'{rule_id} exclude')
                continue
            logger.debug(f'{rule_id} include')
            prop = Property(
                class_='scc_goal_name_id',
                ns=profile_ns,
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
                if implemented_requirement.set_parameters is None:
                    implemented_requirement.set_parameters = [set_parameter]
                else:
                    implemented_requirement.set_parameters.append(set_parameter)
            implemented_requirements.append(implemented_requirement)
        return implemented_requirements

    def _build_responsible_roles(self, party_uuid_01, party_uuid_02, party_uuid_03):
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

    def _build_parties(self, party_uuid_01, party_uuid_02, party_uuid_03):
        """Build parties."""
        value = [
            Party(uuid=party_uuid_01, type='organization', name=self._get_org_name, remarks=self._get_org_remarks),
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

    def _build_responsible_parties(self, party_uuid_01, party_uuid_02, party_uuid_03):
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
