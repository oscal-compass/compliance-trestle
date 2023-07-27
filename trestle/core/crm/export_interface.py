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
"""Provide interface to ssp allowing queries and operations for exports, inherited, and satisfied statements."""

import logging
import uuid
from typing import Dict, List, Tuple

import trestle.oscal.ssp as ossp
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_dict, as_list

logger = logging.getLogger(__name__)


class ExportInterface:
    """
    Interface to query exported provided and responsibility statements from.

    The by-component export statement is parse and the responsibility and provided statement
    are separated into three catagories:

    isolated responsibilities - A responsibility with no provided statement
    isolated provided - A provided statement with no referring responsibility statements
    export set - A set with a single responsibility and referred provided statement
    """

    def __init__(self, by_comp: ossp.ByComponent):
        """Initialize export writer for a single by-component assembly."""
        self._by_comp: ossp.ByComponent = by_comp

        self._provided_dict: Dict[uuid.UUID, ossp.Provided] = {}
        self._responsibility_dict: Dict[uuid.UUID, ossp.Responsibility] = {}
        self._responsibility_by_provided: Dict[uuid.UUID, List[ossp.Responsibility]] = {}

        if by_comp.export:
            self._provided_dict = self._create_provided_dict()
            self._responsibility_dict = self._create_responsibility_dict()
            self._responsibility_by_provided = self._create_responsibility_by_provided_dict()

    def _create_provided_dict(self) -> Dict[uuid.UUID, ossp.Provided]:
        provided_dict: Dict[uuid.UUID, ossp.Provided] = {}
        for provided in as_list(self._by_comp.export.provided):
            provided_dict[provided.uuid] = provided
        return provided_dict

    def _create_responsibility_dict(self) -> Dict[uuid.UUID, ossp.Responsibility]:
        responsibility_dict: Dict[uuid.UUID, ossp.Provided] = {}
        for responsibility in as_list(self._by_comp.export.responsibilities):
            responsibility_dict[responsibility.uuid] = responsibility
        return responsibility_dict

    def _create_responsibility_by_provided_dict(self) -> Dict[uuid.UUID, List[ossp.Responsibility]]:
        responsibility_by_provided: Dict[uuid.UUID, List[ossp.Responsibility]] = {}
        for responsibility in as_list(self._by_comp.export.responsibilities):
            if responsibility.provided_uuid is None:
                continue
            if responsibility.provided_uuid not in responsibility_by_provided:
                responsibility_by_provided[responsibility.provided_uuid] = [responsibility]
            else:
                existing_list: List[ossp.Responsibility] = responsibility_by_provided[responsibility.provided_uuid]
                existing_list.append(responsibility)
                responsibility_by_provided[responsibility.provided_uuid] = existing_list
        return responsibility_by_provided

    def get_isolated_responsibilities(self) -> List[ossp.Responsibility]:
        """Return all isolated exported responsibilities."""
        all_responsibilities: List[ossp.Responsibility] = []
        for resp in as_dict(self._responsibility_dict).values():
            if resp.provided_uuid is None:
                all_responsibilities.append(resp)
        return all_responsibilities

    def get_isolated_provided(self) -> List[ossp.Responsibility]:
        """Return all isolated exported provided capabilities."""
        all_provided: List[ossp.Provided] = []
        for provided in as_dict(self._provided_dict).values():
            if not self._provided_has_responsibilities(provided.uuid):
                all_provided.append(provided)
        return all_provided

    def get_export_sets(self) -> List[Tuple[ossp.Responsibility, ossp.Provided]]:
        """Return a dictionary of every responsibility relationship with provided."""
        all_export_sets: List[Tuple[ossp.Responsibility, ossp.Provided]] = []
        for provided_uuid, responsibilities in as_dict(self._responsibility_by_provided).items():

            # Ensure the provided object exists in the dictionary.
            # If it doesn't this is a bug.
            try:
                provided = self._provided_dict[provided_uuid]
            except KeyError:
                raise TrestleError(f'Provided capability {provided_uuid} not found')

            for responsibility in responsibilities:
                shared_responsibility: Tuple[ossp.Responsibility, ossp.Provided] = (responsibility, provided)
                all_export_sets.append(shared_responsibility)
        return all_export_sets

    def _provided_has_responsibilities(self, provided_uuid: uuid.UUID) -> bool:
        """Return whether a provided UUID has responsibilities."""
        return provided_uuid in self._responsibility_by_provided
