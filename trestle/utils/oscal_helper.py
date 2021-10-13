# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""OSCAL utilities."""

import logging
import pathlib

from trestle.oscal.catalog import Catalog
from trestle.oscal.catalog import Control
from trestle.oscal.profile import Profile

logger = logging.getLogger(__name__)

t_control = Control
t_control_id = str
t_control_name = str
t_control_prop = str
t_prop_name = str
t_status = str


class CatalogHelper():
    """Catalog Helper class to assist navigating catalog."""

    def __init__(self, catalog_file) -> None:
        """Initialize."""
        self._catalog = Catalog.oscal_read(pathlib.Path(catalog_file))
        logger.info(f'catalog: {catalog_file}')

    def exists(self) -> bool:
        """Catalog exists determination."""
        return self._catalog is not None

    def find_control_id(self, control_name: t_control_name) -> (t_control_id, t_status):
        """Find control_id for given control_name."""
        for group in self._catalog.groups:
            for control in group.controls:
                control_id, status = self._find_control_id(control, control_name)
                if control_id is not None:
                    return control_id, status
        return None, None

    def _find_control_prop(self, control: t_control, prop_name: t_prop_name) -> t_control_prop:
        for prop in control.props:
            if prop.name == prop_name:
                return prop.value
        return None

    def _find_control_id(self, control: t_control, control_name: t_control_name) -> (t_control_id, t_status):
        label = self._find_control_prop(control, 'label')
        if label.strip().upper() == control_name.strip().upper():
            control_id = control.id
            status = self._find_control_prop(control, 'status')
            return control_id, status
        if hasattr(control, 'controls'):
            if control.controls is not None:
                for embedded_control in control.controls:
                    control_id, status = self._find_control_id(embedded_control, control_name)
                    if control_id is not None:
                        return control_id, status
        return None, None


class ProfileHelper():
    """Profile Helper class to assist navigating profile."""

    def __init__(self, profile_file) -> None:
        """Initialize."""
        self._profile = Profile.oscal_read(pathlib.Path(profile_file))
        logger.info(f'profile: {profile_file}')

    def exists(self) -> bool:
        """Profile exists determination."""
        return self._profile is not None

    def get_metadata_properties(self) -> list:
        """Get metadata properties."""
        retval = []
        if self._profile.metadata is not None:
            if self._profile.metadata.props is not None:
                retval = self._profile.metadata.props
        return retval

    def is_filtered(self, rule) -> bool:
        """Determine if rule is to be filtered out."""
        retval = False
        if self._profile is not None:
            if self._profile.imports is not None:
                for entry in self._profile.imports:
                    if entry.include_controls is not None:
                        retval = True
                        if self._is_included(rule, entry.include_controls):
                            retval = False
                            break
        return retval

    def _is_included(self, rule, include_controls) -> bool:
        """Determine if rule is to be included."""
        for item in include_controls:
            if item.with_ids is not None:
                for with_id in item.with_ids:
                    if with_id.__root__ == rule:
                        return True
        return False
