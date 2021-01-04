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
        logger.info('')
        logger.info('Purpose: Transform OpenShift Compliance Operator (OSCO) produced .yaml files into Open Security Controls Assessment Language (OSCAL) .json partial results files.')
        logger.info('')
        logger.info('Configuration flags sit under [task.osco-to-oscal]:')
        logger.info('  input-dir = (required) the path of the input directory comprising osco .yaml files.')
        logger.info('  input-metadata = (optional) the name of the input directory metadata .yaml file, default = oscal-metadata.yaml.')
        logger.info('  output-dir = (required) the path of the output directory comprising synthesized OSCAL .json files.')
        logger.info('  output-overwrite = (optional) true [default] or false; replace existing output when true.')
        logger.info('  quiet = (optional) true or false [default]; display file creations and rules analysis when false.')
        logger.info('')
        logger.info('Operation: All the .yaml files in the input-dir are processed, each producing a corresponding .json output-dir file.')
        logger.info('The exception is the input-metadata .yaml file which, if present, is used to augment all produced .json output directory files.')
        logger.info('')

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        if self._config:
            # initialize
            default_metadata = {}
            # process config
            idir = self._config.get('input-dir')
            if idir is None:
                logger.error(f'[simluate] config missing "input-dir"')
                return TaskOutcome('simulated-failure')
            ipth = pathlib.Path(idir)
            odir = self._config.get('output-dir')
            if odir is None:
                logger.error(f'[simluate] config missing "output-dir"')
                return TaskOutcome('simulated-failure')
            imeta = self._config.get('input-metadata', 'oscal-metadata.yaml')
            opth = pathlib.Path(odir)
            overwrite = self._config.getboolean('output-overwrite', True)
            quiet = self._config.getboolean('quiet', False)
            # insure output folder exists
            opth.mkdir(exist_ok=True, parents=True)
            # fetch enhancing oscal metadata
            mfile = ipth / imeta
            metadata = self._get_metadata(mfile, default_metadata)
            if len(metadata) == 0:
                logger.debug(f'no metadata: {imeta}.')
            # examine each file in the input folder
            for ifile in sorted(ipth.iterdir()):
                # skip enhancing oscal metadata
                if ifile.name == imeta:
                    continue
                # ignore non-yaml files
                if ifile.suffix != '.yml':
                    if ifile.suffix != '.yaml':
                        logger.debug(f'[simluate] skipping {ifile.name}')
                        continue
                # calculate the output file, including path
                ofile = self._calculate_ofile(ifile.name, opth)
                # only allow writing output file if either:
                # a) it does not already exist, or
                # b) output-overwrite flag is True
                if not overwrite:
                    if ofile.exists():
                        logger.error(f'simluate: file exists: {ofile}')
                        return TaskOutcome('simulated-failure')
                if not quiet:
                    logger.debug(f'[simluate]  create {ofile}')
                # fetch the contents of the subject OSCO .yaml/.yml file
                idata = self._read_content(ifile)
                # create the OSCAL .json file from the OSCO and the optional osco-metadata files
                odata, analysis = osco.get_observations(idata, metadata)
                # write the OSCAL to the output file
                self._write_content(ofile, odata, True)
                # display analysis
                if not quiet:
                    logger.debug(f'[simluate] Rules Analysis:')
                    logger.debug(f'[simluate] config_maps: {analysis["config_maps"]}')
                    logger.debug(f'[simluate] dispatched rules: {analysis["dispatched_rules"]}')
                    logger.debug(f'[simluate] result types: {analysis["result_types"]}')
            return TaskOutcome('simulated-success')
        logger.error(f'config missing')
        return TaskOutcome('simulated-failure')

    def execute(self) -> TaskOutcome:
        """Provide an actual outcome."""
        if self._config:
            # initialize
            default_metadata = {}
            # process config
            idir = self._config.get('input-dir')
            if idir is None:
                logger.error(f'config missing "input-dir"')
                return TaskOutcome('failure')
            ipth = pathlib.Path(idir)
            odir = self._config.get('output-dir')
            if odir is None:
                logger.error(f'config missing "output-dir"')
                return TaskOutcome('failure')
            imeta = self._config.get('input-metadata', 'oscal-metadata.yaml')
            opth = pathlib.Path(odir)
            overwrite = self._config.getboolean('output-overwrite', True)
            quiet = self._config.getboolean('quiet', False)
            # insure output folder exists
            opth.mkdir(exist_ok=True, parents=True)
            # fetch enhancing oscal metadata
            mfile = ipth / imeta
            metadata = self._get_metadata(mfile, default_metadata)
            if len(metadata) == 0:
                logger.info(f'no metadata: {imeta}.')
            # examine each file in the input folder
            for ifile in sorted(ipth.iterdir()):
                # skip enhancing oscal metadata
                if ifile.name == imeta:
                    continue
                # ignore non-yaml files
                if ifile.suffix != '.yml':
                    if ifile.suffix != '.yaml':
                        logger.debug(f'skipping {ifile.name}')
                        continue
                # calculate the output file, including path
                ofile = self._calculate_ofile(ifile.name, opth)
                # only allow writing output file if either:
                # a) it does not already exist, or
                # b) output-overwrite flag is True
                if not overwrite:
                    if ofile.exists():
                        logger.error(f'file exists: {ofile}')
                        return TaskOutcome('failure')
                if not quiet:
                    logger.info(f'create: {ofile}')
                # fetch the contents of the subject OSCO .yaml/.yml file
                idata = self._read_content(ifile)
                # create the OSCAL .json file from the OSCO and the optional osco-metadata files
                odata, analysis = osco.get_observations(idata, metadata)
                # write the OSCAL to the output file
                self._write_content(ofile, odata)
                # display analysis
                if not quiet:
                    logger.info(f'Rules Analysis:')
                    logger.info(f'config_maps: {analysis["config_maps"]}')
                    logger.info(f'dispatched rules: {analysis["dispatched_rules"]}')
                    logger.info(f'result types: {analysis["result_types"]}')
            return TaskOutcome('success')
        logger.error(f'config missing')
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
    
    def _calculate_ofile(self, ifn, opth):
        """Synthesize output file path+name."""
        ofn = ifn
        ofn = ofn.rsplit('.yaml')[0]
        ofn = ofn.rsplit('.yml')[0]
        ofn += '-oscal.json'
        ofile = opth / ofn
        return ofile
    
    def _get_metadata(self, mfile, default_metadata):
        """Get metadata, if it exists."""
        metadata = default_metadata
        try:
            with open(mfile, "r") as fp:
                metadata = yaml.full_load(fp)
        except:
            logger.debug(traceback.format_exc())
        return metadata
        