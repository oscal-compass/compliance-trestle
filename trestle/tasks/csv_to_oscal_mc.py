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
import csv
import datetime
import logging
import os
import pathlib
import traceback
import uuid
from typing import Dict, Iterator, List, Optional

from trestle.oscal import OSCAL_VERSION
from trestle.oscal.common import Map
from trestle.oscal.common import MappingItem
from trestle.oscal.common import MappingResourceReference
from trestle.oscal.common import Metadata
from trestle.oscal.common import Property
from trestle.oscal.common import Relationship
from trestle.oscal.mapping import Mapping
from trestle.oscal.mapping import MappingCollection
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome
from trestle.tasks.utilities import HrefManager

HEADER_DECORATION_CHAR = '$'
SOURCE_RESOURCE = 'Source_Resource'
TARGET_RESOURCE = 'Target_Resource'
MAP_SOURCE_ID_REF = 'Map_Source_Id_Ref'
MAP_TARGET_ID_REF_LIST = 'Map_Target_Id_Ref_List'
MAP_RELATIONSHIP = 'Map_Relationship'

L_SOURCE_RESOURCE = SOURCE_RESOURCE.lower()
L_TARGET_RESOURCE = TARGET_RESOURCE.lower()
L_MAP_SOURCE_ID_REF = MAP_SOURCE_ID_REF.lower()
L_MAP_TARGET_ID_REF_LIST = MAP_TARGET_ID_REF_LIST.lower()
L_MAP_RELATIONSHIP = MAP_RELATIONSHIP.lower()

logger = logging.getLogger(__name__)

timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc).isoformat()


class CsvToOscalMappingCollection(TaskBase):
    """
    Task to create OSCAL mc.json.

    Attributes:
        name: Name of the task.
    """

    name = 'csv-to-oscal-mc'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task csv-to-oscal-mc.

        Args:
            config_object: Config section associated with the task.
        """
        super().__init__(config_object)

    def print_info(self) -> None:
        """Print the help string."""
        name = self.name
        oscal_name = 'mapping-collection'
        #
        logger.info(f'Help information for {name} task.')
        logger.info('')
        logger.info(f'Purpose: From csv produce OSCAL {oscal_name} file.')
        logger.info('')
        logger.info('')
        logger.info(f'Configuration flags sit under [task.{name}]:')
        text1 = '  title                = '
        text2 = '(required) the mapping collection title.'
        logger.info(text1 + text2)
        text1 = '  version              = '
        text2 = '(required) the mapping collection version.'
        logger.info(text1 + text2)
        text1 = '  csv-file             = '
        text2 = '(required) the path of the csv file.'
        text3 = ' [1st row are column headings; 2nd row are column descriptions; 3rd row and beyond is data]'
        logger.info(text1 + text2 + text3)
        text1 = '  required columns:      '
        for text2 in CsvColumn.columns_required:
            logger.info(text1 + text2)
            text1 = '                         '
        text1 = '  optional columns:      '
        for text2 in CsvColumn.columns_optional:
            logger.info(text1 + text2)
            text1 = '                         '
        text1 = '  output-dir           = '
        text2 = '(required) the path of the output directory for synthesized OSCAL .json files.'
        logger.info(text1 + text2)
        text1 = '  output-overwrite     = '
        text2 = '(optional) true [default] or false; replace existing output when true.'
        logger.info(text1 + text2)

    def configure(self) -> bool:
        """Configure."""
        self._timestamp = datetime.datetime.utcnow().replace(microsecond=0).replace(tzinfo=datetime.timezone.utc
                                                                                    ).isoformat()
        # config verbosity
        self._quiet = self._config.get('quiet', False)
        self._verbose = not self._quiet
        # title
        self._title = self._config.get('title')
        if self._title is None:
            logger.warning('config missing "title"')
            return False
        # version
        self._version = self._config.get('version')
        if self._version is None:
            logger.warning('config missing "version"')
            return False
        # config csv
        self._csv_file = self._config.get('csv-file')
        if self._csv_file is None:
            logger.warning('config missing "csv-file"')
            return False
        self._csv_path = pathlib.Path(self._csv_file)
        if not self._csv_path.exists():
            logger.warning('"csv-file" not found')
            return False
        # announce csv
        if self._verbose:
            logger.info(f'input: {self._csv_file}')
        # workspace
        self._workspace = os.getcwd()
        return True

    def simulate(self) -> TaskOutcome:
        """Provide a simulated outcome."""
        return TaskOutcome('simulated-success')

    def execute(self) -> TaskOutcome:
        """Provide an executed outcome."""
        try:
            return self._execute()
        except Exception:
            logger.error(traceback.format_exc())
            return TaskOutcome('failure')

    def _execute(self) -> TaskOutcome:
        """Execute path core."""
        if not self.configure():
            return TaskOutcome('failure')
        # config output
        odir = self._config.get('output-dir')
        opth = pathlib.Path(odir)
        self._overwrite = self._config.getboolean('output-overwrite', True)
        # insure output dir exists
        opth.mkdir(exist_ok=True, parents=True)
        # calculate output file name & check writability
        oname = 'mapping-collection.json'
        ofile = opth / oname
        if not self._overwrite and pathlib.Path(ofile).exists():
            logger.warning(f'output: {ofile} already exists')
            return TaskOutcome('failure')
        # title
        title = self._config.get('title')
        # title
        version = self._config.get('version')
        # fetch csv
        self._csv_mgr = _CsvMgr(self._csv_path)
        # Mapping Collection manager
        self._mc_mgr = _McMgr(ofile, title, version)
        # href manager
        href_manager = HrefManager()
        # accumulators for missing ids
        ctl_missing_src = []
        ctl_missing_tgt = []
        # process each row of mapping csv
        for row in self._csv_mgr.row_generator():
            # tgt
            tgt_resource_href = self._csv_mgr.get_cell(row, L_TARGET_RESOURCE)
            href_manager.add(tgt_resource_href)
            tgt_id_list = self._csv_mgr.get_cell(row, L_MAP_TARGET_ID_REF_LIST).split()
            tgt_id_ref_list = href_manager.get_id_list(tgt_resource_href, tgt_id_list)
            # src
            src_resource_href = self._csv_mgr.get_cell(row, L_SOURCE_RESOURCE)
            href_manager.add(src_resource_href)
            src_id = self._csv_mgr.get_cell(row, MAP_SOURCE_ID_REF)
            src_id_ref = href_manager.get_id(src_resource_href, src_id)
            # relationship mapping
            if tgt_id_ref_list and src_id_ref:
                src_resource_type = href_manager.get_type(src_resource_href)
                tgt_resource_type = href_manager.get_type(tgt_resource_href)
                relationship_type = self._csv_mgr.get_cell(row, L_MAP_RELATIONSHIP)
                kvp_set = {}
                for user_column_name in self._csv_mgr.get_user_column_names():
                    value = self._csv_mgr.get_cell(row, user_column_name)
                    kvp_set[user_column_name] = value
                self._mc_mgr.add_mapping(
                    src_resource_type,
                    src_resource_href,
                    tgt_resource_type,
                    tgt_resource_href,
                    src_id_ref,
                    tgt_id_ref_list,
                    relationship_type,
                    kvp_set,
                )
            else:
                # keep track of ids not found in specified corresponding href
                if not tgt_id_ref_list:
                    for tgt_id in tgt_id_list:
                        if tgt_id not in ctl_missing_tgt:
                            ctl_missing_tgt.append(tgt_id)
                if not src_id_ref:
                    if src_id not in ctl_missing_src:
                        ctl_missing_src.append(src_id)
        # issues?
        text = ''
        if ctl_missing_src:
            text += f'source(s) missing from href: {ctl_missing_src}\n'
        if ctl_missing_tgt:
            text += f'target(s) missing from href: {ctl_missing_tgt}\n'
        if text:
            raise RuntimeError(text)
        # fetch synthesized mapping collection
        mapping_collection = self._mc_mgr.get_mapping_collection()
        # write OSCAL mc to file
        if self._verbose:
            logger.info(f'output: {ofile}')
        mapping_collection.oscal_write(pathlib.Path(ofile))
        return TaskOutcome('success')


class _McMgr():
    """Mapping col Manager."""

    def __init__(self, mc_path: pathlib.Path, title: str, version: str) -> None:
        """Initialize."""
        self._title = title
        self._timestamp = timestamp
        self._version = version
        self._map = {}

    def _derive_id_ref_type(self, id_ref: str) -> str:
        """Derive id_ref type."""
        if 'smt' in id_ref:
            rval = 'statement'
        else:
            rval = 'control'
        return rval

    def add_mapping(
        self,
        src_resource_type: str,
        src_resource_href: str,
        tgt_resource_type: str,
        tgt_resource_href: str,
        src_id_ref: str,
        tgt_id_ref_list: List[str],
        relationship_type: str,
        kvp_set: Dict,
    ) -> None:
        """Add mapping."""
        mapping = self._get_mapping(src_resource_type, src_resource_href, tgt_resource_type, tgt_resource_href)
        sources = []
        targets = []
        id_ref_type = self._derive_id_ref_type(src_id_ref)
        src_item = MappingItem(type=id_ref_type, id_ref=src_id_ref)
        sources.append(src_item)
        for tgt_id_ref in tgt_id_ref_list:
            id_ref_type = self._derive_id_ref_type(tgt_id_ref)
            tgt_item = MappingItem(type=id_ref_type, id_ref=tgt_id_ref)
            targets.append(tgt_item)
        relationship = Relationship(type=relationship_type)
        map_ = Map(
            uuid=str(uuid.uuid4()),
            relationship=relationship,
            sources=sources,
            targets=targets,
        )
        props = []
        if kvp_set:
            for name in kvp_set:
                value = kvp_set[name]
                if not value:
                    continue
                prop = Property(name=name, value=value)
                props.append(prop)
        if props:
            map_.props = props
        mapping.maps.append(map_)

    def _get_mapping(
        self, src_resource_type: str, src_resource_href: str, tgt_resource_type: str, tgt_resource_href: str
    ) -> Mapping:
        """Get mapping."""
        key = f'{src_resource_type};{src_resource_href}:{tgt_resource_type};{tgt_resource_href}'
        if key not in self._map.keys():
            source_item = MappingResourceReference(type=src_resource_type, href=src_resource_href)
            target_item = MappingResourceReference(type=tgt_resource_type, href=tgt_resource_href)
            mapping = Mapping(
                uuid=str(uuid.uuid4()),
                source_resource=source_item,
                target_resource=target_item,
                maps=[],
            )
            self._map[key] = mapping
        return self._map[key]

    def get_mapping_collection(self) -> MappingCollection:
        """Get mapping collection."""
        # metadata
        metadata = Metadata(
            title=self._title,
            last_modified=timestamp,
            oscal_version=OSCAL_VERSION,
            version=self._version,
        )
        # mapping collection
        mapping_collection = MappingCollection(
            uuid=str(uuid.uuid4()),
            metadata=metadata,
            mappings=list(self._map.values()),
        )
        return mapping_collection


class CsvColumn():
    """CsvColumn."""

    columns_required = [
        f'{L_SOURCE_RESOURCE}',
        f'{L_TARGET_RESOURCE}',
        f'{L_MAP_SOURCE_ID_REF}',
        f'{L_MAP_TARGET_ID_REF_LIST}',
    ]

    columns_optional = [
        f'{L_MAP_RELATIONSHIP}',
    ]

    @staticmethod
    def get_required_column_names() -> List[str]:
        """Get required column names."""
        rval = []
        rval += CsvColumn.columns_required
        return rval

    @staticmethod
    def get_optional_column_names() -> List[str]:
        """Get optional column names."""
        rval = []
        rval += CsvColumn.columns_optional
        return rval


class _CsvMgr():
    """Csv Manager."""

    expected_encoding = 'utf-8'
    alternate_encoding = 'Latin1'

    def __init__(self, csv_path: pathlib.Path) -> None:
        """Initialize."""
        self._ingest(csv_path)
        self._undecorate_header()
        self._verify()

    def _ingest(self, csv_path: pathlib.Path) -> None:
        try:
            self._csv = []
            with open(csv_path, 'r', newline='', encoding=self.expected_encoding) as f:
                csv_reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                for row in csv_reader:
                    self._csv.append(row)
        except Exception:
            logger.warning(f'{csv_path} not {self.expected_encoding}')
            self._csv = []
            with open(csv_path, 'r', newline='', encoding=self.alternate_encoding) as f:
                csv_reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                for row in csv_reader:
                    self._csv.append(row)

    def _get_normalized_column_name(self, column_name: str) -> str:
        """Get normalized column name."""
        return column_name.lower().lstrip('$')

    def _undecorate_header(self) -> None:
        """Undecorate header."""
        head_row = self._csv[0]
        self._csv[0] = []
        for column_name in head_row:
            heading = self._get_normalized_column_name(column_name)
            self._csv[0].append(heading)

    def _verify(self) -> None:
        """Verify."""
        required_columns = CsvColumn.get_required_column_names()
        if len(self._csv):
            head_row = self._csv[0]
            for heading in head_row:
                heading = heading.lower()
                if heading in required_columns:
                    required_columns.remove(heading)
        if len(required_columns):
            text = f'Missing columns: {required_columns}'
            raise RuntimeError(text)

    def row_generator(self) -> Iterator[int]:
        """Generate rows until max reached."""
        begin = 2
        for row, _ in enumerate(self._csv):
            if row < begin:
                continue
            yield row

    def get_cell(self, row: int, col: str) -> str:
        """Get value for specified row number, column name."""
        rval = ''
        index = self._get_col_index(col)
        if index >= 0:
            rval = self._csv[row][index]
        return rval

    def _get_col_index(self, column_name: str) -> int:
        """Get index for column name."""
        rval = -1
        index = 0
        head_row = self._csv[0]
        col_name = self._get_normalized_column_name(column_name)
        for heading in head_row:
            head_name = self._get_normalized_column_name(heading)
            if head_name == col_name:
                rval = index
                break
            index += 1
        return rval

    def get_user_column_names(self) -> List[str]:
        """Get user column names."""
        user_column_names = []
        for column_name in self._csv[0]:
            col_name = self._get_normalized_column_name(column_name)
            if col_name in CsvColumn.get_required_column_names():
                continue
            if col_name in CsvColumn.get_optional_column_names():
                continue
            user_column_names.append(col_name)
        return user_column_names
