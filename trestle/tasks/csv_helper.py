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
from trestle.oscal.catalog import Catalog
from trestle.oscal.catalog import Control
from trestle.oscal.catalog import Group
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

    eg_ns = 'http://ibm.github.io/compliance-trestle/schemas/oscal/cd'
    eg_ns_user = 'http://abc.github.io/compliance-trestle/schemas/oscal/cd'

    def __init__(self) -> None:
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
        text2 = '(required) the path of the OSCAL catalog file used to determine Control_Mappings inclusion/exclusion.'
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
        # catalog
        catalog_file = self._config.get('catalog-file')
        if catalog_file is None:
            logger.warning('config missing "catalog-file"')
            return False
        catalog_path = pathlib.Path(catalog_file)
        if not catalog_path.exists():
            logger.warning('"catalog-file" not found')
            return False
        self._catalog_helper = OscalCatalogHelper(catalog_path)
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
        return True

    def load(self, csv_path: pathlib.Path) -> None:
        """Load."""
        with open(csv_path, 'r', newline='') as f:
            csv_reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for row in csv_reader:
                self._csv.append(row)
            if len(self._csv):
                self._column.map_head(self._csv[0])

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
        index = self._column.get_index(name)
        return row[index]

    def get_class(self, name: str) -> str:
        """Get class value for specified name from config."""
        class_name_key = f'class.{name}'
        return self._config.get(class_name_key)

    def get_user_column_names(self) -> List[str]:
        """Get user column names."""
        user_column_names = []
        for column_name in self._csv[0]:
            if column_name not in self._column.columns:
                user_column_names.append(column_name)
        return user_column_names

    def is_control_id_in_catalog(self, control_id: str) -> bool:
        """Determine of specified control is in catalog."""
        rval = self._catalog_helper.is_present(control_id)
        return rval

    def report_issues(self) -> None:
        """Report issues."""


class OscalCatalogHelper:
    """OSCAL Catalog Helper common functions and assistance."""

    def __init__(self, catalog_path: pathlib.Path) -> None:
        """Initialize."""
        # arrays
        self._control_ids_list = []
        # init
        catalog = Catalog.oscal_read(catalog_path)
        control_ids_list = []
        self._ingest_catalog_groups(catalog.groups, control_ids_list)
        self._ingest_catalog_controls(catalog.groups, control_ids_list, None, None)
        self._control_ids_list = control_ids_list
        logger.debug(f'{control_ids_list}')

    def _ingest_catalog_groups(self, groups: List[Group], control_ids: List[str]) -> None:
        if groups:
            for group in groups:
                self._ingest_catalog_groups(group.groups, control_ids)
                self._ingest_catalog_controls(group.controls, control_ids, group, None)

    def _ingest_catalog_controls(
        self, controls: List[Control], control_ids: List[str], group: Group, parent_control: Control
    ) -> None:
        if controls:
            for control in controls:
                control_ids.append(control.id)
                self._ingest_catalog_controls(control.controls, control_ids, group, control)

    def is_present(self, control_id) -> bool:
        """Check if catalog contains specified control id."""
        return control_id in self._control_ids_list
