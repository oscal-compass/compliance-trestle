# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2021 IBM Corp. All rights reserved.
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

from pydantic import BaseModel, Field

import trestle
from trestle.core import const
from trestle.oscal import OSCAL_VERSION
from trestle.oscal.catalog import Catalog
from trestle.oscal.catalog import Control
from trestle.oscal.catalog import Group
from trestle.oscal.common import Link
from trestle.oscal.common import Metadata
from trestle.tasks.base_task import TaskBase
from trestle.tasks.base_task import TaskOutcome

logger = logging.getLogger(__name__)


class Node(BaseModel):
    """Representation of CIS profile entry."""

    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)


class CisToCatalog(TaskBase):
    """
    Task to CIS to catalog from standard (e.g. CIS benchmark).

    Attributes:
        name: Name of the task.
    """

    name = 'cis-to-catalog'

    def __init__(self, config_object: Optional[configparser.SectionProxy]) -> None:
        """
        Initialize trestle task cis-to-catalog.

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
        logger.info('Purpose: Create catalog from from standard (e.g. CIS benchmark).')
        logger.info('')
        logger.info('Configuration flags sit under [task.cis-to-catalog]:')
        text1 = '  input-dir              = '
        text2 = '(required) location to read the compliance-as-code profile files.'
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
            logger.error('config missing')
            return TaskOutcome('failure')
        try:
            idir = self._config['input-dir']
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
            logger.error(f'output: {ofile} already exists')
            return TaskOutcome('failure')
        # metadata links (optional)
        metadata_links = self._config.get('metadata-links')
        # get list or <name>.profile files
        filelist = self._get_filelist(idir)
        if len(filelist) < 1:
            logger.error(f'input: {idir} no .profile file found')
            return TaskOutcome('failure')
        # initialize node list
        self._node_map = {}
        # process files
        for fp in filelist:
            lines = self._get_content(fp)
            self._parse(lines)
        # get root nodes
        root_nodes = self._get_root_nodes()
        # groups and controls
        root = Group(title='root', groups=[])
        for node in root_nodes:
            group = Group(title=f'{node.name} {node.description}')
            root.groups.append(group)
            depth = self._depth(node.name)
            if depth == 3:
                self._add_groups(group, node.name, depth)
            if depth == 2:
                self._add_controls(group, node.name, depth)
        # metadata
        metadata = Metadata(
            title=self._title, last_modified=self._timestamp, oscal_version=OSCAL_VERSION, version=trestle.__version__
        )
        # metadata links
        if metadata_links is not None:
            metadata.links = []
            for item in metadata_links.split():
                link = Link(href=item)
                metadata.links.append(link)
        # catalog
        catalog = Catalog(uuid=_uuid(), metadata=metadata, groups=root.groups)
        # write OSCAL ComponentDefinition to file
        if verbose:
            logger.info(f'output: {ofile}')
        catalog.oscal_write(pathlib.Path(ofile))
        return TaskOutcome('success')

    def _get_filelist(self, idir: str) -> List[pathlib.Path]:
        """Get filelist."""
        return [x for x in pathlib.Path(idir).iterdir() if x.is_file() and x.suffix == '.profile']

    def _get_content(self, fp: pathlib.Path) -> List[str]:
        """Fetch content from file."""
        content = None
        try:
            f = fp.open('r', encoding=const.FILE_ENCODING)
            content = f.readlines()
            f.close()
            return content
        except Exception as e:
            logger.error(f'unable to process {fp.name}')
            raise e

    def _parse(self, lines: List[str]) -> None:
        """Parse lines to build data structure."""
        for line in lines:
            line = line.strip()
            if line.startswith('title: ') and "'" in line:
                self._title = line.split("'")[1]
                continue
            line_parts = line.split(None, 2)
            # must be 3 parts exactly
            if len(line_parts) < 3:
                continue
            # normalized name and description
            name = line_parts[1].rstrip('.')
            description = line_parts[2]
            # name must be numbers and decimal points
            if not set(name) <= set('0123456789.'):
                continue
            # derive desired sortable key from name
            key = self._get_key(name)
            self._node_map[key] = Node(name=name, description=description)

    def _get_key(self, name: str) -> (int, int, int):
        """Convert name to desired sortable key."""
        key = 0
        parts = name.split('.')
        if len(parts) == 1:
            key = (int(parts[0]), 0, 0)
        elif len(parts) == 2:
            key = (int(parts[0]), int(parts[1]), 0)
        elif len(parts) == 3:
            key = (int(parts[0]), int(parts[1]), int(parts[2]))
        return key

    def _get_root_nodes(self) -> ValuesView[Node]:
        """Get root nodes."""
        root_nodes = {}
        for node in self._node_map.values():
            if len(node.name) == 1:
                root_nodes[node.name] = node
        return root_nodes.values()

    def _depth(self, prefix: str) -> int:
        """Get maximum depth for prefix."""
        depth = 0
        for node in self._node_map.values():
            name = node.name
            if not name.startswith(prefix):
                continue
            dots = name.split('.')
            if len(dots) <= depth:
                continue
            depth = len(dots)
            if depth in [1, 2, 3]:
                continue
            text = f'Unexpected value: {name}'
            logger.error(text)
            raise RuntimeError(text)
        return depth

    def _add_controls(self, group: Group, prefix: str, depth: int):
        """Add controls to group."""
        controls = []
        for key in sorted(self._node_map.keys()):
            node = self._node_map[key]
            name = node.name
            if name.startswith(prefix):
                dots = name.split('.')
                if len(dots) == depth:
                    id_ = f'CIS-{node.name}'
                    title = f'{node.name} {node.description}'
                    control = Control(id=id_, title=title)
                    controls.append(control)
        if len(controls) > 0:
            group.controls = controls

    def _add_groups(self, group: Group, prefix: str, depth: int):
        """Add sub-groups to group."""
        groups = []
        for key in sorted(self._node_map.keys()):
            node = self._node_map[key]
            name = node.name
            if not name.startswith(prefix):
                continue
            if name == prefix:
                continue
            dots = name.split('.')
            if len(dots) != depth - 1:
                continue
            title = f'{node.name} {node.description}'
            sub_group = Group(title=title)
            groups.append(sub_group)
            sub_prefix = node.name
            self._add_controls(sub_group, sub_prefix, depth)
        if len(groups) > 0:
            group.groups = groups


def _uuid() -> str:
    """Create uuid."""
    return str(uuid.uuid4())
