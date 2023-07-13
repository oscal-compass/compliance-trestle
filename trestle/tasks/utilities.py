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
"""OSCAL utilities."""

import logging
from pathlib import Path
from typing import List, Optional

from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.profile_resolver import ProfileResolver
from trestle.oscal.catalog import Catalog
from trestle.oscal.catalog import Control
from trestle.oscal.common import Part

logger = logging.getLogger(__name__)


class HrefManager:
    """Href manager."""

    def __init__(self, root: str = '.') -> None:
        """Initialize."""
        self._root = root
        self._map_href_ci = {}
        self._map_href_type = {}

    def add(self, href: str) -> None:
        """Add."""
        if href not in self._map_href_ci.keys():
            if self.add_catalog(href):
                return
            if self.add_resolved_profile(href):
                return
            raise RuntimeError(f'Error loading href: {href}')

    def add_catalog(self, href: str) -> bool:
        """Add catalog."""
        try:
            catalog_path = Path(href)
            catalog = Catalog.oscal_read(catalog_path)
            catalog_interface = CatalogInterface(catalog)
            self._map_href_ci[href] = catalog_interface
            self._map_href_type[href] = 'catalog'
            logger.info(f'add catalog href: {href}')
            rval = True
        except Exception as e:
            logger.info(f'{e}')
            rval = False
        return rval

    def add_resolved_profile(self, href: str) -> bool:
        """Add resolved profile."""
        try:
            catalog, i_props = ProfileResolver().get_resolved_profile_catalog_and_inherited_props(
                Path(self._root),
                href,
            )
            catalog_interface = CatalogInterface(catalog)
            self._map_href_ci[href] = catalog_interface
            self._map_href_type[href] = 'profile'
            logger.info(f'add resolved profile href: {href}')
            rval = True
        except Exception as e:
            logger.info(f'{e}')
            rval = False
        return rval

    def _get_subpart(self, part: Part, id_name: str) -> Optional[Part]:
        """Get subpart."""
        rval = None
        if part.parts:
            for subpart in part.parts:
                if 'smt' not in subpart.id:
                    continue
                if subpart.id == id_name:
                    rval = subpart
                    break
        if rval:
            logger.debug(f'id_name: {id_name} part.id: {rval.id}')
        return rval

    def _get_part(self, control: Control, id_name: str) -> Optional[Part]:
        """Get part."""
        rval = None
        if control.parts:
            for part in control.parts:
                if 'smt' not in part.id:
                    continue
                if part.id == id_name:
                    rval = part
                    break
                subpart = self._get_subpart(part, id_name)
                if subpart is not None:
                    rval = subpart
                    break
        if rval:
            logger.debug(f'id_name: {id_name} part.id: {rval.id}')
        return rval

    def get_type(self, href: str) -> Optional[str]:
        """Get type."""
        return self._map_href_type[href]

    def get_id(self, href: str, id_name: str) -> Optional[str]:
        """Get id."""
        rval = None
        try:
            ctl_name = id_name.split('_smt')[0]
            catalog_interface = self._map_href_ci[href]
            control = catalog_interface.get_control(ctl_name)
            # insure control exists
            if control is None:
                text = f'control {ctl_name} not found in {href}'
                raise RuntimeError(text)
            if id_name == ctl_name:
                rval = control.id
            else:
                part = self._get_part(control, id_name)
                if part:
                    rval = part.id
        except Exception as e:
            logger.debug(f'{e}')
        return rval

    def get_id_list(self, href: str, id_name_list: List[str]) -> List[str]:
        """Get id list."""
        id_list = []
        for id_name in id_name_list:
            id_ = self.get_id(href, id_name)
            if id_:
                id_list.append(id_)
        return id_list
