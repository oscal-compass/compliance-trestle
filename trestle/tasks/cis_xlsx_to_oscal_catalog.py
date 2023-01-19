# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2023 IBM Corp. All rights reserved.
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
from typing import List, Optional, ValuesView

from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.utils import get_column_letter

from pydantic import BaseModel, Field

import trestle
from trestle.common import const
from trestle.oscal import OSCAL_VERSION
from trestle.oscal.catalog import Catalog
from trestle.oscal.catalog import Control
from trestle.oscal.catalog import Group
from trestle.oscal.common import Link
from trestle.oscal.common import Metadata
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome

logger = logging.getLogger(__name__)


class CisXlsxToOscalCatalog(TaskBase):
    """
    Task to transform CIS .xlsx to OSCAL catalog.

    Attributes:
        name: Name of the task.
    """

    name = 'cis-xlsx-to-oscal-catalog'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task ocp4-cis-profile-to-oscal-catalog.

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
        logger.info('Purpose: Create catalog from standard (e.g. CIS benchmark).')
        logger.info('')
        logger.info('Configuration flags sit under [task.cis-xlsx-to-oscal-catalog]:')
        text1 = '  input-file             = '
        text2 = '(required) path to read the compliance-as-code .xlsx spread sheet file.'
        logger.info(text1 + text2)
        text1 = '  output-dir             = '
        text2 = '(required) location to write the generated catalog.json file.'
        logger.info(text1 + text2)
        text1 = '  output-overwrite       = '
        text2 = '(optional) true [default] or false; replace existing output when true.'
        logger.info(text1 + text2)

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
        """Wrap the execute for exception handling."""
        if not self._config:
            logger.warning('config missing')
            return TaskOutcome('failure')
        try:
            ifile = self._config['input-file']
            odir = self._config['output-dir']
        except KeyError as e:
            logger.info(f'key {e.args[0]} missing')
            return TaskOutcome('failure')
        # verbosity
        quiet = self._config.get('quiet', False)
        verbose = not quiet
        # output
        overwrite = self._config.getboolean('output-overwrite', True)
        opth = pathlib.Path(odir)
        # insure output dir exists
        opth.mkdir(exist_ok=True, parents=True)
        # calculate output file name & check writability
        oname = 'catalog.json'
        ofile = opth / oname
        if not overwrite and pathlib.Path(ofile).exists():
            logger.warning(f'output: {ofile} already exists')
            return TaskOutcome('failure')
        
        return TaskOutcome('success')
