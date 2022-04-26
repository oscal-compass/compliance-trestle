# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2022 IBM Corp. All rights reserved.
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
import logging
import pathlib
import traceback
import uuid
from typing import List, Optional

from trestle.oscal import OSCAL_VERSION
from trestle.oscal.common import Metadata
from trestle.oscal.profile import Import
from trestle.oscal.profile import Modify
from trestle.oscal.profile import Profile
from trestle.oscal.profile import SelectControlById
from trestle.oscal.profile import SetParameter
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome
from trestle.tasks.xlsx_helper import XlsxHelper
from trestle.tasks.xlsx_helper import get_trestle_version

logger = logging.getLogger(__name__)


class XlsxToOscalProfile(TaskBase):
    """
    Task to create OSCAL Profile json.

    Attributes:
        name: Name of the task.
    """

    name = 'xlsx-to-oscal-profile'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task xlsx-to-oscal-profile.

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)
        self.xlsx_helper = XlsxHelper()
        self._timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc
                                                                                    ).isoformat()

    def set_timestamp(self, timestamp: str) -> None:
        """Set the timestamp."""
        self._timestamp = timestamp

    def print_info(self) -> None:
        """Print the help string."""
        self.xlsx_helper.print_info(self.name, 'profile')

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        return TaskOutcome('simulated-success')

    def execute(self) -> TaskOutcome:
        """Provide an executed outcome."""
        try:
            return self._execute()
        except Exception:
            logger.info(traceback.format_exc())
            return TaskOutcome('failure')

    def _execute(self) -> TaskOutcome:
        """Execute path core."""
        if not self.xlsx_helper.configure(self):
            return TaskOutcome('failure')
        # config output
        odir = self._config.get('output-dir')
        opth = pathlib.Path(odir)
        self._overwrite = self._config.getboolean('output-overwrite', True)
        # insure output dir exists
        opth.mkdir(exist_ok=True, parents=True)
        # calculate output file name & check writability
        oname = 'profile.json'
        ofile = opth / oname
        if not self._overwrite and pathlib.Path(ofile).exists():
            logger.error(f'output: {ofile} already exists')
            return TaskOutcome('failure')
        # create OSCAL Profile
        metadata = Metadata(
            title='Profile for ' + self._get_profile_title(),
            last_modified=self._timestamp,
            oscal_version=OSCAL_VERSION,
            version=get_trestle_version(),
        )
        if self.xlsx_helper.profile_type == self.xlsx_helper.by_control:
            imports = self._get_imports_by_control()
            profile = Profile(
                uuid=str(uuid.uuid4()),
                metadata=metadata,
                imports=imports,
            )
        else:
            if self.xlsx_helper.profile_type == self.xlsx_helper.by_rule:
                imports = self._get_imports_by_rule()
            elif self.xlsx_helper.profile_type == self.xlsx_helper.by_check:
                imports = self._get_imports_by_check()
            else:
                imports = self._get_imports_by_goal()
            set_parameters = self._get_set_parameters()
            modify = Modify(set_parameters=set_parameters)
            profile = Profile(
                uuid=str(uuid.uuid4()),
                metadata=metadata,
                imports=imports,
                modify=modify,
            )
        # write OSCAL Profile to file
        if self._verbose:
            logger.info(f'output: {ofile}')
        profile.oscal_write(pathlib.Path(ofile))
        # issues
        self._report_issues()
        return TaskOutcome('success')

    def _get_imports_by_goal(self) -> List[Import]:
        """Get imports by goal."""
        return self._get_imports_by_check()

    def _get_imports_by_control(self) -> List[Import]:
        """Get imports by control."""
        import_ = Import(
            href=self._get_spread_sheet_url(),
            include_controls=[SelectControlById(with_ids=self._get_with_ids_by_control())],
        )
        imports = [import_]
        return imports

    def _get_imports_by_rule(self) -> List[Import]:
        """Get imports by rule."""
        import_ = Import(
            href=self._get_spread_sheet_url(),
            include_controls=[SelectControlById(with_ids=self._get_with_ids_by_rule())],
        )
        imports = [import_]
        return imports

    def _get_imports_by_check(self) -> List[Import]:
        """Get imports by check."""
        import_ = Import(
            href=self._get_spread_sheet_url(),
            include_controls=[SelectControlById(with_ids=self._get_with_ids_by_check())],
        )
        imports = [import_]
        return imports

    def _get_with_ids_by_control(self) -> List[str]:
        """Get controls from spread sheet."""
        control_list = []
        for row in self.xlsx_helper.row_generator():
            # quit when first row with no goal_id encountered
            controls = self.xlsx_helper.get_controls(row)
            if controls is not None:
                for control in controls:
                    control = self._oscal_namify(control)
                    if control in control_list:
                        continue
                    control_list.append(control)
        return sorted(control_list, key=self._control_sort_key)

    def _get_with_ids_by_rule(self) -> List[str]:
        """Get rules from spread sheet."""
        rule_name_id_list = []
        for row in self.xlsx_helper.row_generator():
            # quit when first row with no goal_id encountered
            rule_name_id = self.xlsx_helper.get_rule_name_id(row, strict=True)
            if rule_name_id is not None:
                if rule_name_id in rule_name_id_list:
                    continue
                rule_name_id_list.append(rule_name_id)
        return sorted(rule_name_id_list)

    def _get_with_ids_by_check(self) -> List[str]:
        """Get check from spread sheet."""
        check_name_id_list = []
        for row in self.xlsx_helper.row_generator():
            # quit when first row with no goal_id encountered
            check_name_id = self.xlsx_helper.get_check_name_id(row, strict=True)
            if check_name_id is not None:
                if check_name_id in check_name_id_list:
                    continue
                check_name_id_list.append(check_name_id)
        return sorted(check_name_id_list)

    def _control_sort_key(self, control: str) -> (str, int, int):
        """Fabricate sort key."""
        k1 = control.split('-')[0]
        k2 = int(control.split('-')[1].split('.')[0])
        if '.' in control:
            k3 = int(control.split('-')[1].split('.')[1])
        else:
            k3 = 0
        return (k1, k2, k3)

    def _oscal_namify(self, control: str) -> str:
        """Rectify parenthesized numbers in controls."""
        control = control.replace('(', '.')
        control = control.replace(')', '')
        return control

    def _get_set_parameters(self) -> List[SetParameter]:
        """Get set parameters from spread sheet."""
        set_parameters = []
        for row in self.xlsx_helper.row_generator():
            # quit when first row with no goal_id encountered
            param_id, label = self.xlsx_helper.get_parameter_name_and_description(row)
            usage = self.xlsx_helper.get_parameter_usage(row)
            values = self.xlsx_helper.get_parameter_values(row)
            if param_id is None:
                continue
            set_parameter = SetParameter(
                param_id=param_id,
                label=label,
                usage=usage,
            )
            if values is not None:
                set_parameter.values = values
            set_parameters.append(set_parameter)
        return set_parameters

    def _get_profile_title(self) -> str:
        """Get profile title from config."""
        value = self._config.get('profile-title')
        logger.debug(f'profile-title: {value}')
        return value

    def _get_spread_sheet_url(self) -> str:
        """Get spread sheet url from config."""
        value = self._config.get('spread-sheet-url')
        logger.debug(f'spread-sheet-url: {value}')
        return value

    def _report_issues(self) -> None:
        """Report issues."""
        self.xlsx_helper.report_issues()
