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
import json
import logging
import pathlib
import traceback
from typing import Optional

from ruamel.yaml import YAML

from trestle.oscal.profile import Profile
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome
from trestle.transforms.implementations.osco import ProfileToOscoTransformer

logger = logging.getLogger(__name__)


class ProfileToOsco(TaskBase):
    """
    Task to convert Profile to OSC yaml.

    Attributes:
        name: Name of the task.
    """

    name = 'profile-to-osco'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task profile-to-osco.

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)

    def print_info(self) -> None:
        """Print the help string."""
        logger.info(f'Help information for {self.name} task.')
        logger.info('')
        logger.info(
            'Purpose: Transform Open Security Controls Assessment Language (OSCAL) Profile '
            + 'into Open Shift Compliance Operator (OSCO) .yaml file.'
        )
        logger.info('')
        logger.info('Configuration flags sit under [task.profile-to-osco]:')
        logger.info('  input-file = (required) path of the input file comprising OSCAL profile.')
        logger.info('  output-dir = (required) path of the output directory comprising synthesized .yaml file.')
        logger.info(
            '  output-name = (optional) name of created file in output directory, default is osco-profile.yaml.'
        )
        logger.info('  output-overwrite = (optional) true [default] or false; replace existing output when true.')
        logger.info(
            '  quiet = (optional) true or false [default]; display file creations and rules analysis when false.'
        )
        logger.info('')
        logger.info('Operation: The specified input profile is transformed into OSCO .yaml.')
        logger.info('')
        logger.info('Notes:')
        note11 = '[1] The input-file OSCAL profile should specify a metadata property with'
        note12 = 'name "osco_version" and value of the form "0.1.46".'
        note13 = 'The value corresponds with the OpenShift Compliance Operator (OSCO) version'
        note14 = 'and affects the format of the emitted yaml.'
        note15 = 'If not specified, the default is "0.1.46".'
        logger.info(f'{note11} {note12} {note13} {note14} {note15}')
        note21 = '[2] For OSCO version "0.1.39" and prior no "description" is emitted for "spec".'
        logger.info(f'{note21}')

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        return TaskOutcome('simulated-success')

    def execute(self) -> TaskOutcome:
        """Provide an actual outcome."""
        try:
            return self._execute()
        except Exception:
            logger.error(traceback.format_exc())
            return TaskOutcome('failure')

    def _execute(self) -> TaskOutcome:
        """Perform transformation."""
        # check config
        if not self._config:
            logger.error('config missing')
            return TaskOutcome('failure')
        # input-file
        input_file = self._config.get('input-file')
        if input_file is None:
            logger.error('config missing "input-file"')
            return TaskOutcome('failure')
        logger.info(f'input-file: {input_file}')
        input_path = pathlib.Path(input_file)
        # output-dir
        output_dir = self._config.get('output-dir')
        if output_dir is None:
            logger.error('config missing "output-dir"')
            return TaskOutcome('failure')
        output_path = pathlib.Path(output_dir)
        # insure output dir exists
        output_path.mkdir(exist_ok=True, parents=True)
        # output file path
        output_name = self._config.get('output-name', 'osco-profile.yaml')
        output_filepath = pathlib.Path(output_dir, output_name)
        logger.info(f'output-file: {output_filepath}')
        # overwrite
        overwrite = self._config.getboolean('output-overwrite', True)
        if not overwrite and pathlib.Path(output_filepath).exists():
            logger.error(f'output-file: {output_filepath} already exists')
            return TaskOutcome('failure')
        # read input
        profile = Profile.oscal_read(input_path)
        # transform
        transformer = ProfileToOscoTransformer()
        ydata = json.loads(transformer.transform(profile))
        # write output
        yaml = YAML(typ='safe')
        yaml.default_flow_style = False
        with open(output_filepath, 'w') as outfile:
            yaml.dump(ydata, outfile)
        # success
        return TaskOutcome('success')
