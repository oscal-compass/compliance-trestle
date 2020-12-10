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
import os
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
        Initialize trestle task pass-fail.

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

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        try:
            if self._config:
                idir = self._config.get('input-dir')
                if idir is None:
                    logger.error(f'config missing "input-dir"')
                    return TaskOutcome('simulated-failure')
                odir = self._config.get('output-dir')
                if odir is None:
                    logger.error(f'config missing "output-dir"')
                    return TaskOutcome('simulated-failure')
                overwrite = self._config.getboolean('output-overwrite', True)
                for pfile in sorted(pathlib.Path(idir).iterdir()):
                    ifile = str(pfile)
                    if ifile.endswith('oscal-metadata.yaml'):
                        continue
                    if ifile.endswith('oscal-metadata.yml'):
                        continue
                    ofile = self._calculate_ofile(ifile, odir)
                    if not overwrite:
                        if os.path.exists(ofile):
                            logger.error(f'file exists: {ofile}')
                            return TaskOutcome('simulated-failure')
                    mfile = self._calculate_mfile(idir)
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
            traceback.print_exc()
            return TaskOutcome('simulated-exception')

    def execute(self) -> TaskOutcome:
        """Provide an actual outcome."""
        try:
            if self._config:
                idir = self._config.get('input-dir')
                if idir is None:
                    logger.error(f'config missing "input-dir"')
                    return TaskOutcome('failure')
                odir = self._config.get('output-dir')
                if odir is None:
                    logger.error(f'config missing "output-dir"')
                    return TaskOutcome('failure')
                overwrite = self._config.getboolean('output-overwrite', True)
                os.makedirs(odir, exist_ok = True) 
                for pfile in sorted(pathlib.Path(idir).iterdir()):
                    ifile = str(pfile)
                    if ifile.endswith('oscal-metadata.yaml'):
                        continue
                    if ifile.endswith('oscal-metadata.yml'):
                        continue
                    ofile = self._calculate_ofile(ifile, odir)
                    if not overwrite:
                        if os.path.exists(ofile):
                            logger.error(f'file exists: {ofile}')
                            return TaskOutcome('simulated-failure')
                    mfile = self._calculate_mfile(idir)
                    metadata = self._get_metadata(mfile)
                    logger.info(f'create: {ofile}')
                    idata = self._read_content(ifile)
                    odata, analysis = osco.get_observations(idata, metadata)
                    self._write_content(ofile, odata)
                    logger.info(f'Rules Analysis:')
                    logger.info(f'config_maps: {analysis["config_maps"]}')
                    logger.info(f'dispatched rules: {analysis["dispatched_rules"]}')
                    logger.info(f'result types: {analysis["result_types"]}')
                # outcome, executed
                return TaskOutcome('success')
            logger.error(f'config missing')
            return TaskOutcome('failure')
        except Exception:
            traceback.print_exc()
            return TaskOutcome('exception')
    
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
    
    def _calculate_ofile(self, ifile, odir):
        """Synthesize output file path+name."""
        ofile = ifile
        ofile = ofile.rsplit('.yaml')[0]
        ofile = ofile.rsplit('.yml')[0]
        ofile += '.oscal'
        if '/' in ofile:
            ofile = ofile.rsplit('/',1)[1]
        ofile = odir+'/'+ofile
        return ofile
        
    def _calculate_mfile(self, idir):
        """Synthesize meta file path+name."""
        mfile = idir+'/'+'oscal-metadata.yaml'
        return mfile
    
    def _get_metadata(self, mfile):
        metadata = {}
        try:
            with open(mfile, "r") as fp:
                metadata = yaml.full_load(fp)
        except:
            traceback.print_exc()
        return metadata
        