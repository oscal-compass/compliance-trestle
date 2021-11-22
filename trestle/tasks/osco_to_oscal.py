# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
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
import logging
import pathlib
import traceback
from typing import Optional

from trestle.core import const
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome
from trestle.transforms.implementations.osco import OscoTransformer

logger = logging.getLogger(__name__)


class OscoToOscal(TaskBase):
    """
    Task to convert Osco report to OSCAL json.

    Attributes:
        name: Name of the task.
    """

    name = 'osco-to-oscal'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task osco-to-oscal.

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)

    def print_info(self) -> None:
        """Print the help string."""
        logger.info(f'Help information for {self.name} task.')
        logger.info('')
        logger.info(
            'Purpose: Transform Osco files into Open Security Controls Assessment Language (OSCAL) '
            + 'partial results files.'
        )
        logger.info('')
        logger.info('Configuration flags sit under [task.osco-to-oscal]:')
        logger.info(
            '  checking  = (optional) True indicates perform strict checking of OSCAL properties, default is False.'
        )
        logger.info('  input-dir = (required) the path of the input directory comprising Osco reports.')
        logger.info(
            '  output-dir = (required) the path of the output directory comprising synthesized OSCAL .json files.'
        )
        logger.info('  output-overwrite = (optional) true [default] or false; replace existing output when true.')
        logger.info(
            '  quiet = (optional) true or false [default]; display file creations and rules analysis when false.'
        )
        logger.info(
            '  timestamp = (optional) timestamp for the Observations in ISO 8601 format, such as '
            + ' 2021-01-04T00:05:23+04:00 for example; if not specified then value for "Timestamp" key in the Osco '
            + ' report is used if present, otherwise current time is used.'
        )
        logger.info('')
        logger.info(
            'Operation: A transformation is performed on one or more Osco input files to produce output in OSCAL '
            + 'partial results format.'
        )

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        self._simulate = True
        return self._transform()

    def execute(self) -> TaskOutcome:
        """Provide an actual outcome."""
        self._simulate = False
        return self._transform()

    def _transform(self) -> TaskOutcome:
        """Perform transformation."""
        try:
            return self._transform_work()
        except Exception:
            logger.error(traceback.format_exc())
            mode = ''
            if self._simulate:
                mode = 'simulated-'
            return TaskOutcome(mode + 'failure')

    def _transform_work(self) -> TaskOutcome:
        """
        Perform transformation work steps.

        Work steps: read input, process, write output, display analysis
        """
        mode = ''
        if self._simulate:
            mode = 'simulated-'
        if not self._config:
            logger.error('config missing')
            return TaskOutcome(mode + 'failure')
        # config required input & output dirs
        try:
            idir = self._config['input-dir']
            ipth = pathlib.Path(idir)
            odir = self._config['output-dir']
            opth = pathlib.Path(odir)
        except KeyError as e:
            logger.debug(f'key {e.args[0]} missing')
            return TaskOutcome(mode + 'failure')
        # config optional overwrite & quiet
        self._overwrite = self._config.getboolean('output-overwrite', True)
        quiet = self._config.get('quiet', False)
        self._verbose = not self._simulate and not quiet
        # config optional timestamp
        timestamp = self._config.get('timestamp')
        if timestamp is not None:
            try:
                OscoTransformer.set_timestamp(timestamp)
            except Exception:
                logger.error('config invalid "timestamp"')
                return TaskOutcome(mode + 'failure')
        # config optional performance
        modes = {
            'checking': self._config.getboolean('checking', False),
        }
        # insure output dir exists
        opth.mkdir(exist_ok=True, parents=True)
        # process
        for ifile in sorted(ipth.iterdir()):
            if ifile.suffix not in ['.json', '.jsn', '.yaml', '.yml', '.xml']:
                continue
            blob = self._read_file(ifile)
            osco_transformer = OscoTransformer()
            osco_transformer.set_modes(modes)
            results = osco_transformer.transform(blob)
            oname = ifile.stem + '.oscal' + '.json'
            ofile = opth / oname
            if not self._overwrite and pathlib.Path(ofile).exists():
                logger.error(f'output: {ofile} already exists')
                return TaskOutcome(mode + 'failure')
            self._write_file(results, ofile)
            self._show_analysis(osco_transformer)
        return TaskOutcome(mode + 'success')

    def _read_file(self, ifile: str):
        """Read raw input file."""
        if not self._simulate:
            if self._verbose:
                logger.info(f'input: {ifile}')
        with open(ifile, encoding=const.FILE_ENCODING) as fp:
            blob = fp.read()
        return blob

    def _write_file(self, result: str, ofile: str) -> None:
        """Write oscal results file."""
        if not self._simulate:
            if self._verbose:
                logger.info(f'output: {ofile}')
            result.oscal_write(pathlib.Path(ofile))

    def _show_analysis(self, osco_transformer: OscoTransformer) -> None:
        """Show analysis."""
        if not self._simulate:
            if self._verbose:
                analysis = osco_transformer.analysis
                for line in analysis:
                    logger.info(line)
