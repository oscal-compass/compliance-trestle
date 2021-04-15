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
from typing import Any, Dict, Optional

import yaml

import trestle.core.const as const
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome
from trestle.utils import osco

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

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)

    def print_info(self) -> None:
        """Print the help string."""
        logger.info(f'Help information for {self.name} task.')
        logger.info('')
        logger.info('Purpose: Transform OpenShift Compliance Operator (OSCO) files into Open Security Controls Assessment Language (OSCAL) partial results files.')
        logger.info('')
        logger.info('Configuration flags sit under [task.osco-to-oscal]:')
        logger.info('  input-dir = (required) the path of the input directory comprising OSCO .yaml and/or .json files.')
        logger.info('  input-metadata = (optional) the name of the input directory metadata .yaml file, default = oscal-metadata.yaml.')
        logger.info('  output-dir = (required) the path of the output directory comprising synthesized OSCAL .json files.')
        logger.info('  output-overwrite = (optional) true [default] or false; replace existing output when true.')
        logger.info('  quiet = (optional) true or false [default]; display file creations and rules analysis when false.')
        logger.info('')
        logger.info('Operation: A transformation is performed on one or more OSCO input files to produce corresponding output files in OSCAL partial results format. Input files are typically OSCO .yaml files or Arboretum .json files, the latter constructed by a fetcher/check (see https://github.com/ComplianceAsCode/auditree-arboretum).')
        logger.info('')
        logger.info('All the .yaml files in the input-dir are processed, each producing a corresponding .json output-dir file. The exception is the input-metadata .yaml file which, if present, is used to augment all produced .json output directory files. Similarly, all the .json files in the input-dir are processed, each producing one or more corresponding .json output-dir files.')
        logger.info('')
        logger.info('The format of the input-metadata .yaml file comprises one or more entries as follows:')
        logger.info('<name>:')
        logger.info('  locker: <locker>')
        logger.info('  namespace: <namespace>')
        logger.info('  benchmark: <benchmark>')
        logger.info('  subject-references:')
        logger.info('    component:')
        logger.info('      uuid-ref: <uuid-ref>')
        logger.info('      type: <type>')
        logger.info('      title: <title>')
        logger.info('    inventory-item:')
        logger.info('      uuid-ref: <uuid-ref>')
        logger.info('      type: <type>')
        logger.info('      title: <title>')
        logger.info('      properties: ')
        logger.info('        target: <target>')
        logger.info('        cluster-name: <cluster-name>')
        logger.info('        cluster-type: <cluster-type>')
        logger.info('        cluster-region: <cluster-region>')
        logger.info('')
        logger.info('Augmentation occurs when the name specified in the metadata entry of the osco .yaml file matches an entry <name> specified in the input-metadata .yaml file, if any. All entries in the input-metadata .yaml are optional. For example, locker and its value can be omitted. Likewise, any or all of cluster-name, -type, and -region may be omitted if not applicable.')

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
                # assemble collection comprising output file name to unprocessed content
                collection = self._assemble(ifile)
                # formulate each output OSCAL partial results file
                for oname in collection.keys():
                    ofile = opth / pathlib.Path(oname)
                    # only allow writing output file if either:
                    # a) it does not already exist, or
                    # b) output-overwrite flag is True
                    if not overwrite:
                        if ofile.exists():
                            logger.error(f'file exists: {ofile}')
                            return TaskOutcome('simulated-failure')
                    if not quiet:
                        logger.debug(f'create: {ofile}')
                    # create the OSCAL .json file from the OSCO and the optional osco-metadata files
                    observations, analysis = osco.get_observations(collection[oname], metadata)
                    # write the OSCAL to the output file
                    self._write_content(ofile, observations, True)
                    # display analysis
                    if not quiet:
                        logger.debug(f'[simulate] Rules Analysis:')
                        logger.debug(f'[simulate] config_maps: {analysis["config_maps"]}')
                        logger.debug(f'[simulate] dispatched rules: {analysis["dispatched_rules"]}')
                        logger.debug(f'[simulate] result types: {analysis["result_types"]}')
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
                # assemble collection comprising output file name to unprocessed content
                collection = self._assemble(ifile)
                # formulate each output OSCAL partial results file
                for oname in collection.keys():
                    ofile = opth / pathlib.Path(oname)
                    # only allow writing output file if either:
                    # a) it does not already exist, or
                    # b) output-overwrite flag is True
                    if not overwrite:
                        if ofile.exists():
                            logger.error(f'file exists: {ofile}')
                            return TaskOutcome('failure')
                    if not quiet:
                        logger.info(f'create: {ofile}')
                    # create the OSCAL .json file from the OSCO and the optional osco-metadata files
                    observations, analysis = osco.get_observations(collection[oname], metadata)
                    # write the OSCAL to the output file
                    self._write_content(ofile, observations)
                    # display analysis
                    if not quiet:
                        logger.info(f'Rules Analysis:')
                        logger.info(f'config_maps: {analysis["config_maps"]}')
                        logger.info(f'dispatched rules: {analysis["dispatched_rules"]}')
                        logger.info(f'result types: {analysis["result_types"]}')
            return TaskOutcome('success')
        logger.error(f'config missing')
        return TaskOutcome('failure')
    
    def _assemble(self, ifile: pathlib.Path) -> Dict[str, osco.t_osco]:
        """Formulate collection comprising output file name to unprocessed content."""
        collection = {}
        #  handle OSCO individual yaml files (just one pairing)
        if ifile.suffix in ['.yml', '.yaml']:
            ydict = yaml.load(ifile.open('r+'), Loader=yaml.Loader)
            oname = ifile.stem+'.json'
            logger.debug(f'========== <{oname}> ==========')
            logger.debug(ydict)
            logger.debug(f'========== </{oname}> ==========')
            collection[oname] = ydict
        #  handle arboretum  OSCO fetcher/check composite json files (one or more pairings)
        elif ifile.suffix in ['.jsn', '.json']:
            idata = json.load(ifile.open('r+'))
            if idata is not None:
                for key in idata.keys():
                    for group in idata[key]:
                        # for each cluster create an individual yaml-like unprocessed data set
                        for cluster in idata[key][group]:
                            if 'resources' not in cluster.keys():
                                continue
                            for resource in cluster['resources']:
                                if 'kind' not in resource.keys():
                                    continue
                                if resource['kind'] != 'ConfigMap':
                                    continue
                                if 'data' not in resource.keys():
                                    continue
                                if 'results' not in resource['data'].keys():
                                    continue
                                if 'metadata' not in resource.keys():
                                    continue
                                if 'name' not in resource['metadata'].keys():
                                    continue
                                # add yaml-like data set to collection indexed by ConfigMap identity
                                ydict = {}
                                ydict['kind'] = resource['kind']                       
                                data = {}
                                data['results'] = resource['data']['results']                        
                                ydict['data'] = data
                                ydict['metadata'] = resource['metadata']
                                oname = resource['metadata']['name']+'.json'
                                collection[oname] = ydict
                                logger.debug(f'========== <{oname}> ==========')
                                logger.debug(ydict)
                                logger.debug(f'========== </{oname}> ==========')
        else:                                               
            logger.debug(f'skipping {ifile.name}')
        logger.debug(f'collection: {len(collection)}')
        return collection

    def _write_content(self, ofile: pathlib.Path, observations: osco.AssessmentResultsPartial, simulate:bool=False) -> None:
        """Write the contents of a json file."""
        if simulate:
            return
        write_file = pathlib.Path(ofile).open('w', encoding=const.FILE_ENCODING)
        write_file.write(observations.json(exclude_none=True, by_alias=True, indent=2))
    
    def _get_metadata(self, mfile: pathlib.Path, default_metadata: osco.t_metadata) -> osco.t_metadata:
        """Get metadata, if it exists."""
        metadata = default_metadata
        try:
            metadata = yaml.load(mfile.open('r+'),  Loader=yaml.Loader)
        except:
            logger.debug(traceback.format_exc())
        return metadata
        