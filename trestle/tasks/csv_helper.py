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
"""CSV utilities."""
import csv
import logging
import pathlib
from typing import Iterator, List

from trestle import __version__
from trestle.tasks.base_task import TaskBase

logger = logging.getLogger(__name__)


def get_trestle_version() -> str:
    """Get trestle version wrapper."""
    return __version__


class Column():
    """Column."""

    def __init__(self) -> None:
        """Initialize."""
        self.columns = [
            'Rule_Id',
            'Rule_Description',
            'Profile_Reference_URL',
            'Profile_Description',
            'Component_Type',
            'Control_Mappings',
            'Resource',
            'Parameter_Id',
            'Parameter_Description',
            'Parameter_Default_Value',
            'Parameter_Value_Alternatives'
        ]
        self.help_list = []
        for column in self.columns:
            self.help_list.append(column)

    def map_head(self, head_row: str) -> None:
        """Keep head row."""
        self.head_row = head_row

    def get_index(self, name: str) -> int:
        """Get index for column name."""
        rval = -1
        index = 0
        for column in self.head_row:
            if column == name:
                rval = index
                break
            index += 1
        return rval


class CsvHelper:
    """Csv Helper common functions and assistance."""

    def __init__(self):
        """Initialize."""
        self._csv = []
        self._column = Column()

    def print_info(self, name, oscal_name) -> None:
        """Print the help string."""
        logger.info(f'Help information for {name} task.')
        logger.info('')
        logger.info(f'Purpose: From csv produce OSCAL {oscal_name} file.')
        logger.info('')
        logger.info('')
        logger.info(f'Configuration flags sit under [task.{name}]:')
        text1 = '  catalog-file      = '
        text2 = '(required) the path of the OSCAL catalog file.'
        logger.info(text1 + text2)
        text1 = '  csv-file          = '
        text2 = '(required) the path of the csv file.'
        logger.info(text1 + text2)
        text1 = '  expected columns:   '
        for text2 in self._column.help_list:
            logger.info(text1 + text2)
            text1 = '                      '
        text1 = '  output-dir        = '
        text2 = '(required) the path of the output directory for synthesized OSCAL .json files.'
        logger.info(text1 + text2)
        text1 = '  output-overwrite  = '
        text2 = '(optional) true [default] or false; replace existing output when true.'
        logger.info(text1 + text2)

    def configure(self, task: TaskBase) -> bool:
        """Configure."""
        if not task._config:
            logger.warning('config missing')
        # config verbosity
        quiet = task._config.get('quiet', False)
        task._verbose = not quiet
        # config csv
        csv_file = task._config.get('csv-file')
        if csv is None:
            logger.warning('config missing "csv"')
            return False
        csv_path = pathlib.Path(csv_file)
        if not csv_path.exists():
            logger.warning('"csv" not found')
            return False
        # announce csv
        if task._verbose:
            logger.info(f'input: {csv_file}')
        # load spread sheet
        self.load(csv_file)
        return True

    def load(self, csv_path: pathlib.Path) -> None:
        """Load."""
        with open(csv_path, 'r', newline='') as f:
            csv_reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for row in csv_reader:
                self._csv.append(row)
        self._column.map_head(self._csv[0])

    def row_generator(self) -> Iterator[List[str]]:
        """Generate rows."""
        index = -1
        for row in self._csv:
            index += 1
            if index == 0:
                continue
            logger.debug(f'{index} {row}')
            yield row

    def get_value(self, row: List[str], name: str):
        """Get value for specified name."""
        index = self._column.get_index(name)
        return row[index]

    def report_issues(self) -> None:
        """Report issues."""
