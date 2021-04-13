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
import traceback
from typing import Any, Dict, List, Optional

from trestle.core import const
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome
from trestle.transforms.implementations.tanium import TaniumTransformer
from trestle.transforms.results import Results

logger = logging.getLogger(__name__)

t_filename = str
t_results = Results
t_tanium_transformer = TaniumTransformer

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
        logger.info('Operation: A transformation is performed on one or more Tanium input files to produce output in OSCAL partial results format. Input files are Tanium reports comprising individual lines consumable as json.')
        logger.info('')
        logger.info('All the Tanium report files in the input-dir are processed. Each input file produces a corresponding .json output-dir file.')
        logger.info('')
        logger.info('Expected Tanium report keys are: { "IP Address", "Computer Name", "Comply", "Benchmark", "Benchmark Version", "ID", "Result", "Timestamp" }')
        
    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        self._simulate = True
        return self._transform()
        
    def execute(self) -> TaskOutcome:
        """Provide an actual outcome."""
        self._simulate = False
        return self._transform()
    
    def _transform(self) -> TaskOutcome:
        try:
            return self._transform_work()
        except Exception:
            logger.info(traceback.format_exc())
            mode = ''
            if self._simulate:
                mode = 'simulated-'
            return TaskOutcome(mode + 'failure')
            
    def _transform_work(self) -> TaskOutcome:
        mode = ''
        if self._simulate:
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
        opth = pathlib.Path(odir)
        self._overwrite = self._config.getboolean('output-overwrite', True)
        quiet = self._config.get('quiet', False)
        self._verbose = not self._simulate and not quiet
        # timestamp
        timestamp = self._config.get('timestamp')
        if timestamp is not None:
            try:
                TaniumTransformer.set_timestamp(timestamp)
            except Exception as e:
                logger.error(f'config invalid "timestamp"')
                return TaskOutcome(mode + 'failure')
        # insure output dir exists
        opth.mkdir(exist_ok=True, parents=True)
        # process
        for ifile in sorted(ipth.iterdir()):    
            blob = self._read_file(ifile)
            tanium_transformer = TaniumTransformer()
            results = tanium_transformer.transform(blob)
            oname = ifile.stem + '.oscal' + '.json'
            ofile = opth / oname
            if not self._overwrite and pathlib.Path(ofile).exists():
                logger.error(f'output: {ofile} already exists')
                return TaskOutcome(mode + 'failure')
            self._write_file(results, ofile)
            self._show_analysis(tanium_transformer)
        return TaskOutcome(mode + 'success')

    def _read_file(self, ifile: t_filename):
        if not self._simulate:
            if self._verbose:
                logger.info(f'input: {ifile}') 
        with open(ifile) as fp:
            blob = fp.read()
        return blob
        
    def _write_file(self, result: str, ofile: t_filename) -> None:
        """Write oscal results file."""
        if not self._simulate:
            if self._verbose:
                logger.info(f'output: {ofile}')
            result.oscal_write(pathlib.Path(ofile))
    
    def _show_analysis(self, tanium_transformer: t_tanium_transformer) -> None:
        """Show analysis."""
        if not self._simulate:
            if self._verbose:
                analysis = tanium_transformer.analysis
                for line in analysis:
                    logger.info(line)
    