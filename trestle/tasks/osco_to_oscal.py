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
from typing import Optional

import yaml

from trestle.lib import osco
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome

logger = logging.getLogger(__name__)


class OscoToOscal(TaskBase):
    """
    Task to convert OSCO yaml to OSCAL json.

    Attributes:
        name: Name of the task.
    """

    name = 'osco-to-oscal'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task osco-to-oscal.

        Attributes:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)

    def print_info(self) -> None:
        """Print the help string."""
        logger.info(f'Help information for {self.name} task.')
        logger.info('Configuration flags sit under [task.osco-to-oscal].')
        logger.info('input-dir = the path of the input directory comprising .yaml files.')
        logger.info('output-dir = the path of the output directory comprising synthesized .oscal files.')
        logger.info('output-overwrite = true [default] or false; replace existing output when true.')
        logger.info('quiet = true or false [default]; display file creations and rules analysis when false.')

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        try:
            if self._config:
                idir = pathlib.Path(self._config.get('input-dir'))
                if idir is None:
                    logger.error(f'config missing "input-dir"')
                    return TaskOutcome('simulated-failure')
                odir = pathlib.Path(self._config.get('output-dir'))
                if odir is None:
                    logger.error(f'config missing "output-dir"')
                    return TaskOutcome('simulated-failure')
                overwrite = self._config.getboolean('output-overwrite', True)
                for ifile in sorted(pathlib.Path(idir).iterdir()):
                    parts = ifile.parts
                    ifn = parts[len(parts)-1]
                    if ifn.endswith('oscal-metadata.yaml'):
                        continue
                    if ifn.endswith('oscal-metadata.yml'):
                        continue
                    ofile = self._calculate_ofile(ifn, odir)
                    if not overwrite:
                        if ofile.exists():
                            logger.error(f'file exists: {ofile}')
                            return TaskOutcome('simulated-failure')
                    mfile = idir / 'oscal-metadata.yaml'
                    metadata = self._get_metadata(mfile)
                    logger.debug(f'create: {ofile}')
                    idata = self._read_content(ifile)
                    odata, analysis = osco.get_observations(idata, metadata)
                    self._write_content(ofile, odata, True)
                    logger.debug(f'Rules Analysis:')
                    logger.debug(f'config_maps: {analysis["config_maps"]}')
                    logger.debug(f'dispatched rules: {analysis["dispatched_rules"]}')
                    logger.debug(f'result types: {analysis["result_types"]}')
                return TaskOutcome('simulated-success')
            logger.error(f'config missing')
            return TaskOutcome('simulated-failure')
        except Exception:
            logger.error(traceback.format_exc())
            return TaskOutcome('simulated-failure')

    def execute(self) -> TaskOutcome:
        """Provide an actual outcome."""
        try:
            if self._config:
                idir = pathlib.Path(self._config.get('input-dir'))
                if idir is None:
                    logger.error(f'config missing "input-dir"')
                    return TaskOutcome('failure')
                odir = pathlib.Path(self._config.get('output-dir'))
                if odir is None:
                    logger.error(f'config missing "output-dir"')
                    return TaskOutcome('failure')
                overwrite = self._config.getboolean('output-overwrite', True)
                quiet = self._config.getboolean('quiet', False)
                odir.mkdir(exist_ok=True, parents=True)
                for ifile in sorted(pathlib.Path(idir).iterdir()):
                    parts = ifile.parts
                    ifn = parts[len(parts)-1]
                    if ifn.endswith('oscal-metadata.yaml'):
                        continue
                    if ifn.endswith('oscal-metadata.yml'):
                        continue
                    ofile = self._calculate_ofile(ifn, odir)
                    if not overwrite:
                        if ofile.exists():
                            logger.error(f'file exists: {ofile}')
                            return TaskOutcome('failure')
                    mfile = idir / 'oscal-metadata.yaml'
                    metadata = self._get_metadata(mfile)
                    if not quiet:
                        logger.info(f'create: {ofile}')
                    idata = self._read_content(ifile)
                    odata, analysis = osco.get_observations(idata, metadata)
                    self._write_content(ofile, odata)
                    if not quiet:
                        logger.info(f'Rules Analysis:')
                        logger.info(f'config_maps: {analysis["config_maps"]}')
                        logger.info(f'dispatched rules: {analysis["dispatched_rules"]}')
                        logger.info(f'result types: {analysis["result_types"]}')
                return TaskOutcome('success')
            logger.error(f'config missing')
            return TaskOutcome('failure')
        except Exception:
            logger.error(traceback.format_exc())
            return TaskOutcome('failure')
    
    def _read_content(self, ifile):
        with open(ifile, 'r+') as fp:
            data = fp.read()
            content = yaml.full_load(data)
        logger.debug('========== <content> ==========')
        logger.debug(content)
        logger.debug('========== </content> ==========')
        return content

    def _write_content(self, ofile, content, simulate=False):
        if simulate:
            return
        with open(ofile, 'w', encoding='utf-8') as fp:
            json.dump(content, fp, ensure_ascii=False, indent=2)
    
    def _calculate_ofile(self, ifn, odir):
        """Synthesize output file path+name."""
        ofn = ifn
        ofn = ofn.rsplit('.yaml')[0]
        ofn = ofn.rsplit('.yml')[0]
        ofn += '-oscal.json'
        ofile = pathlib.Path(odir, ofn)
        return ofile
    
    def _get_metadata(self, mfile):
        """Get metadata, if it exists."""
        metadata = {}
        try:
            with open(mfile, "r") as fp:
                metadata = yaml.full_load(fp)
        except:
            logger.debug(traceback.format_exc())
        return metadata
        