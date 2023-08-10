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
"""Provide interface to by-component allowing queries and operations for exports/inheritance statements."""

import copy
import logging
from typing import Dict, List, Tuple

import trestle.oscal.ssp as ossp
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_dict, as_list, none_if_empty

logger = logging.getLogger(__name__)


class ByComponentInterface:
    """
    Interface to query and modify by-component assembly inheritance contents.

    The by-component is contained in two separate forms:  As an actual OSCAL by-component assembly,
    and and multiple dicts providing direct lookup of inheritance statement by uuid.

    The dicts are created by the ByComponentInterface constructor, parsed and the responsibility and provided statements
    are separated into three catagories:

    isolated responsibilities - A responsibility with no provided statement
    isolated provided - A provided statement with no referring responsibility statements
    export set - A set with a single responsibility and referred provided statement

    For updating ByComponent inheritance and satisfied statements, the interface provides a method to reconcile the
    the by-component assembly and merge input inherited and satisfied statements.
    """

    def __init__(self, by_comp: ossp.ByComponent):
        """Initialize export writer for a single by-component assembly."""
        self._by_comp: ossp.ByComponent = by_comp

        self._provided_dict: Dict[str, ossp.Provided] = {}
        self._responsibility_dict: Dict[str, ossp.Responsibility] = {}
        self._responsibility_by_provided: Dict[str, List[ossp.Responsibility]] = {}

        self._inherited_dict: Dict[str, ossp.Inherited] = self._create_inherited_dict()
        self._satisfied_dict: Dict[str, ossp.Satisfied] = self._create_satisfied_dict()

        if by_comp.export:
            self._provided_dict = self._create_provided_dict()
            self._responsibility_dict = self._create_responsibility_dict()
            self._responsibility_by_provided = self._create_responsibility_by_provided_dict()

    def _create_provided_dict(self) -> Dict[str, ossp.Provided]:
        provided_dict: Dict[str, ossp.Provided] = {}
        for provided in as_list(self._by_comp.export.provided):
            provided_dict[provided.uuid] = provided
        return provided_dict

    def _create_responsibility_dict(self) -> Dict[str, ossp.Responsibility]:
        responsibility_dict: Dict[str, ossp.Responsibility] = {}
        for responsibility in as_list(self._by_comp.export.responsibilities):
            responsibility_dict[responsibility.uuid] = responsibility
        return responsibility_dict

    def _create_responsibility_by_provided_dict(self) -> Dict[str, List[ossp.Responsibility]]:
        responsibility_by_provided: Dict[str, List[ossp.Responsibility]] = {}
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

    def _create_inherited_dict(self) -> Dict[str, ossp.Inherited]:
        inherited_dict: Dict[str, ossp.Inherited] = {}
        for inherited in as_list(self._by_comp.inherited):
            inherited_dict[str(inherited.provided_uuid)] = inherited
        return inherited_dict

    def _create_satisfied_dict(self) -> Dict[str, ossp.Satisfied]:
        satisfied_dict: Dict[str, ossp.Satisfied] = {}
        for satisfied in as_list(self._by_comp.satisfied):
            satisfied_dict[str(satisfied.responsibility_uuid)] = satisfied
        return satisfied_dict

    def get_isolated_responsibilities(self) -> List[ossp.Responsibility]:
        """Return all isolated exported responsibilities."""
        all_responsibilities: List[ossp.Responsibility] = []
        for resp in as_dict(self._responsibility_dict).values():
            if resp.provided_uuid is None:
                all_responsibilities.append(resp)
        return all_responsibilities

    def get_isolated_provided(self) -> List[ossp.Provided]:
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

    def reconcile_inheritance_by_component(
        self, incoming_inherited: List[ossp.Inherited], incoming_satisfied: List[ossp.Satisfied]
    ) -> ossp.ByComponent:
        """
        Reconcile the inherited and satisfied statements in the by-component assembly with changes from the export.

        Notes:
            A statement is determined as existing if the provided uuid or responsibility uuid is in the existing in the
            by-component assembly. If existing, the description will be updated if it has changed.

            Any existing inherited or satisfied statements that are not in the incoming export will be removed.
            If a statement is in the incoming export, but not in the existing by-component assembly, it will be added.
        """
        new_inherited: List[ossp.Inherited] = []
        new_satisfied: List[ossp.Satisfied] = []

        # Create a copy of the input by-component assembly to reconcile and return
        new_by_comp: ossp.ByComponent = copy.deepcopy(self._by_comp)

        for statement in incoming_inherited:
            if statement.provided_uuid in self._inherited_dict:
                existing_statement = self._inherited_dict[str(statement.provided_uuid)]
                # Update the description if it has changed
                existing_statement.description = statement.description
                statement = existing_statement
            new_inherited.append(statement)

        new_by_comp.inherited = none_if_empty(new_inherited)

        for statement in incoming_satisfied:
            if statement.responsibility_uuid in self._satisfied_dict:
                existing_statement = self._satisfied_dict[str(statement.responsibility_uuid)]
                # Update the description if it has changed
                existing_statement.description = statement.description
                statement = existing_statement
            new_satisfied.append(statement)

        new_by_comp.satisfied = none_if_empty(new_satisfied)

        return new_by_comp

    def _provided_has_responsibilities(self, provided_uuid: str) -> bool:
        """Return whether a provided UUID has responsibilities."""
        return provided_uuid in self._responsibility_by_provided
