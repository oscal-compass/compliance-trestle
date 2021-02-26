# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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
import logging
import json
import pathlib
from typing import Any, Dict, Optional

from trestle.core import const
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome
from trestle.utils import tanium

logger = logging.getLogger(__name__)


class TaniumToOscal(TaskBase):
    """
    Task to convert Tanium report to OSCAL json.

    Attributes:
        name: Name of the task.
    """

    name = 'tanium-to-oscal'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task tanium-to-oscal.

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)

    def print_info(self) -> None:
        """Print the help string."""
        logger.info(f'Help information for {self.name} task.')
        logger.info('')
        logger.info('Purpose: Transform Tanium files into Open Security Controls Assessment Language (OSCAL) partial results files.')
        logger.info('')
        logger.info('Configuration flags sit under [task.tanium-to-oscal]:')
        logger.info('  input-dir = (required) the path of the input directory comprising Tanium reports.')
        logger.info('  output-dir = (required) the path of the output directory comprising synthesized OSCAL .json files.')
        logger.info('  output-overwrite = (optional) true [default] or false; replace existing output when true.')
        logger.info('  quiet = (optional) true or false [default]; display file creations and rules analysis when false.')
        logger.info('  timestamp = (optional) timestamp for the Observations in ISO 8601 format, such as 2021-01-04T00:05:23+04:00 for example; if not specified then value for "Timestamp" key in the Tanium report is used if present, otherwise current time is used.')                                                       
        logger.info('')
        logger.info('Operation: A transformation is performed on one or more Tanium input files to produce corresponding output files in OSCAL partial results format. Input files are Tanium reports comprising individual lines consumable as json.')
        logger.info('')
        logger.info('All the Tanuim report files in the input-dir are processed, each producing a corresponding .json output-dir file.')
        logger.info('')
        logger.info('Expected Tanuim report keys are: { "IP Address", "Computer Name", "Comply", "Benchmark", "Benchmark Version", "ID", "Result", "Timestamp" }')
        
    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        return self._transform(True)
        
    def execute(self) -> TaskOutcome:
        """Provide an actual outcome."""
        return self._transform(False)

    def _transform(self, simulate: bool = False) -> TaskOutcome:
        mode = ''
        if simulate:
            mode = 'simulated-'
        if not self._config:
            logger.error(f'config missing')
            return TaskOutcome(mode + 'failure')
        # process config
        idir = self._config.get('input-dir')
        if idir is None:
            logger.error(f'config missing "input-dir"')
            return TaskOutcome(mode + 'failure')
        ipth = pathlib.Path(idir)
        odir = self._config.get('output-dir')
        if odir is None:
            logger.error(f'config missing "output-dir"')
            return TaskOutcome(mode + 'failure')
        opth = pathlib.Path(odir)
        overwrite = self._config.getboolean('output-overwrite', True)
        quiet = self._config.getboolean('quiet', False)
        # timestamp
        timestamp = self._config.get('timestamp')
        if timestamp is not None:
            try:
                tanium.Rule.set_default_datetime(timestamp)
            except Exception as e:
                logger.error(f'config invalid "timestamp"')
                return TaskOutcome(mode + 'failure')
        # insure output folder exists
        opth.mkdir(exist_ok=True, parents=True)
        # examine each file in the input folder
        for ifile in sorted(ipth.iterdir()):
            # assemble collection comprising output file name to unprocessed content
            collection = self._assemble(ifile)
            observations, analysis = tanium.get_observations(collection, 'json')
            oname = ifile.with_suffix('').name + '.oscal' + '.json'
            ofile = opth / pathlib.Path(oname)
            # only allow writing output file if either:
            # a) it does not already exist, or
            # b) output-overwrite flag is True
            if not overwrite:
                if ofile.exists():
                    logger.error(f'file exists: {ofile}')
                    return TaskOutcome(mode + 'failure')
            if not simulate:
                if not quiet:
                    logger.info(f'create: {ofile}')
                # write the OSCAL to the output file
                write_file = pathlib.Path(ofile).open('w', encoding=const.FILE_ENCODING)
                write_file.write(observations)
                # display analysis
                if not quiet:
                    logger.info(f'Rules Analysis:')
                    logger.info(f'rules [dispatched]: {analysis["dispatched_rules"]}')
                    logger.info(f'rules [unique]: {analysis["unique_rules"]}')
                    logger.info(f'results: {analysis["results"]}')
        return TaskOutcome(mode + 'success')

    def _assemble(self, ifile: pathlib.Path) -> Dict[str, Any]:
        """Formulate collection comprising output file name to unprocessed content."""
        collection = []
        #  handle Tanium individual files (just one pairing)
        with open(ifile) as fp:
            logger.debug(f'========== <{ifile.name}> ==========')
            lineno = 0
            line = fp.readline()
            while line:
                jdata = json.loads(line.strip())
                collection.append(jdata)
                logger.debug(f'{lineno} {jdata}')
                line = fp.readline()
                lineno += 1
            logger.debug(f'========== </{ifile.name}> ==========')
        return collection
    