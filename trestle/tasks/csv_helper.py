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

from trestle.tasks.base_task import TaskBase

logger = logging.getLogger(__name__)


class Column():
    """Column."""

    def __init__(self) -> None:
        """Initialize."""
        self._columns_required = [
            'Rule_Id',
            'Rule_Description',
            'Profile_Reference_URL',
            'Profile_Description',
            'Component_Type',
            'Control_Mappings',
            'Resource',
        ]
        self._columns_optional = [
            'Parameter_Id',
            'Parameter_Description',
            'Parameter_Default_Value',
            'Parameter_Value_Alternatives',
            'Check_Id',
            'Check_Description',
            'Fetcher',
            'Fetcher_Description',
            'Resource_Instance_Type',
        ]
        self.help_list_required = []
        for column in self._columns_required:
            self.help_list_required.append(column)
        self.help_list_optional = []
        for column in self._columns_optional:
            self.help_list_optional.append(column)

    def is_user_column(self, column_name: str) -> bool:
        """Check if user column name."""
        rval = True
        if column_name in self._columns_required + self._columns_optional:
            rval = False
        return rval

    def get_required_column_names(self) -> List[str]:
        """Get required column names."""
        rval = []
        rval += self._columns_required
        return rval

    def get_optional_column_names(self) -> List[str]:
        """Get optional column names."""
        rval = []
        rval += self._columns_optional
        return rval

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

    eg_ns = 'https://ibm.github.io/compliance-trestle/schemas/oscal/cd'
    eg_ns_user = 'https://ibm.github.io/compliance-trestle/schemas/oscal/cd/user-defined'

    def __init__(self) -> None:
        """Initialize."""
        self._csv = []
        self._column = Column()
        self._filtered = [
            'Profile_Reference_URL',
            'Profile_Description',
            'Component_Type',
            'Control_Mappings',
            'Resource',
            'Parameter_Id',
            'Parameter_Description',
            'Parameter_Default_Value',
            'Parameter_Value_Alternatives',
        ]

    def print_info(self, name: str, oscal_name: str) -> None:
        """Print the help string."""
        logger.info(f'Help information for {name} task.')
        logger.info('')
        logger.info(f'Purpose: From csv produce OSCAL {oscal_name} file.')
        logger.info('')
        logger.info('')
        logger.info(f'Configuration flags sit under [task.{name}]:')
        text1 = '  title             = '
        text2 = '(required) the component definition title.'
        logger.info(text1 + text2)
        text1 = '  version           = '
        text2 = '(required) the component definition version.'
        logger.info(text1 + text2)
        text1 = '  csv-file          = '
        text2 = '(required) the path of the csv file.'
        logger.info(text1 + text2)
        text1 = '  required columns:   '
        for text2 in self._column.help_list_required:
            logger.info(text1 + text2)
            text1 = '                      '
        text1 = '  optional columns:   '
        for text2 in self._column.help_list_optional:
            logger.info(text1 + text2)
            text1 = '                      '
        text1 = '  output-dir        = '
        text2 = '(required) the path of the output directory for synthesized OSCAL .json files.'
        logger.info(text1 + text2)
        text1 = '  namespace         = '
        text2 = f'(optional) the namespace for properties, e.g. {self.eg_ns}'
        logger.info(text1 + text2)
        text1 = '  user-namespace    = '
        text2 = f'(optional) the user-namespace for properties, e.g. {self.eg_ns_user}'
        logger.info(text1 + text2)
        text1 = '  class.column-name = '
        text2 = '(optional) the class to associate with the specified column name, e.g. class.Rule_Id = scc_class'
        logger.info(text1 + text2)
        text1 = '  output-overwrite  = '
        text2 = '(optional) true [default] or false; replace existing output when true.'
        logger.info(text1 + text2)

    def configure(self, task: TaskBase) -> bool:
        """Configure."""
        self._config = task._config
        if not self._config:
            logger.warning('config missing')
            return False
        # config verbosity
        quiet = self._config.get('quiet', False)
        self._verbose = not quiet
        # title
        self._title = self._config.get('title')
        if self._title is None:
            logger.warning('title missing')
            return False
        # version
        self._version = self._config.get('version')
        if self._version is None:
            logger.warning('version missing')
            return False
        # config csv
        csv_file = self._config.get('csv-file')
        if csv_file is None:
            logger.warning('config missing "csv-file"')
            return False
        csv_path = pathlib.Path(csv_file)
        if not csv_path.exists():
            logger.warning('"csv-file" not found')
            return False
        # announce csv
        if self._verbose:
            logger.info(f'input: {csv_file}')
        # load spread sheet
        self.load(csv_file)
        rval = self.verify()
        return rval

    def load(self, csv_path: pathlib.Path) -> None:
        """Load."""
        with open(csv_path, 'r', newline='') as f:
            csv_reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for row in csv_reader:
                self._csv.append(row)
            if len(self._csv):
                self._column.map_head(self._csv[0])

    def verify(self) -> bool:
        """Verify."""
        rval = True
        required_columns = self._column.get_required_column_names()
        if len(self._csv):
            head_row = self._csv[0]
            for heading in head_row:
                if heading in required_columns:
                    required_columns.remove(heading)
        if len(required_columns):
            logger.warning(f'Missing columns: {required_columns}')
            rval = False
        return rval

    def row_count(self) -> int:
        """Row count."""
        return len(self._csv) - 1

    def row_generator(self) -> Iterator[List[str]]:
        """Generate rows."""
        index = -1
        for row in self._csv:
            index += 1
            if index == 0:
                continue
            logger.debug(f'{index} {row}')
            yield row

    def get_value(self, row: List[str], name: str) -> str:
        """Get value for specified name."""
        rval = ''
        index = self._column.get_index(name)
        if index >= 0:
            rval = row[index]
        return rval

    def get_class(self, name: str) -> str:
        """Get class value for specified name from config."""
        class_name_key = f'class.{name}'
        return self._config.get(class_name_key)

    def get_required_column_names(self) -> List[str]:
        """Get required column names."""
        rval = []
        for column_name in self._column.get_required_column_names():
            rval.append(column_name)
        return rval

    def get_filtered_required_column_names(self) -> List[str]:
        """Get filtered required column names."""
        rval = []
        for column_name in self._column.get_required_column_names():
            if column_name not in self._filtered:
                rval.append(column_name)
        return rval

    def get_filtered_optional_column_names(self) -> List[str]:
        """Get filtered optional column names."""
        rval = []
        for column_name in self._column.get_optional_column_names():
            if column_name not in self._filtered:
                rval.append(column_name)
        return rval

    def get_user_column_names(self) -> List[str]:
        """Get user column names."""
        user_column_names = []
        for column_name in self._csv[0]:
            if self._column.is_user_column(column_name):
                user_column_names.append(column_name)
        return user_column_names

    def get_title(self) -> bool:
        """Get title."""
        return self._title

    def get_version(self) -> bool:
        """Get version."""
        return self._version

    def report_issues(self) -> None:
        """Report issues."""
