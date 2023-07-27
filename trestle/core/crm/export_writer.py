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
"""Provided interface to write provided and responsibility exports statements to Markdown."""

import logging
import pathlib
import uuid
from typing import Dict

import trestle.common.const as const
import trestle.oscal.ssp as ossp
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_list
from trestle.core.crm.export_interface import ExportInterface
from trestle.core.inheritance_writer import (
    LeveragedStatements,
    StatementProvided,
    StatementResponsibility,
    StatementTree,
)

logger = logging.getLogger(__name__)


class ExportWriter:
    """
    Exported writer.

    Export writer handles all operation related writing provided and responsibility exported statements
    to Markdown.
    """

    def __init__(self, root_path: pathlib.Path, ssp: ossp.SystemSecurityPlan):
        """
        Initialize export writer.

        Arguments:
            root_path: A root path object where all markdown files and directories should be written.
            ssp: A system security plan with exports
        """
        self._ssp = ssp
        self._root_path = root_path

    def write_exports_as_markdown(self) -> None:
        """Write export statement for leveraged SSP as the inheritance Markdown view."""
        # Find all the components and create paths for name
        paths_by_comp: Dict[uuid.UUD, pathlib.Path] = {}
        for component in as_list(self._ssp.system_implementation.components):
            paths_by_comp[component.uuid] = self._root_path.joinpath(component.title)

        # Process all information under exports in control implementation
        for implemented_requirement in as_list(self._ssp.control_implementation.implemented_requirements):
            for by_comp in as_list(implemented_requirement.by_components):
                try:
                    comp_markdown_path: pathlib.Path = paths_by_comp[by_comp.component_uuid]
                    self._process_by_component(by_comp, comp_markdown_path, implemented_requirement.control_id)
                except KeyError:
                    raise TrestleError(f'Component id {by_comp.component_uuid} is not in the system implementation')

            for stm in as_list(implemented_requirement.statements):
                statement_id = getattr(stm, 'statement_id', f'{implemented_requirement.control_id}_smt')
                for by_comp in stm.by_components:
                    try:
                        comp_markdown_path: pathlib.Path = paths_by_comp[by_comp.component_uuid]
                        self._process_by_component(by_comp, comp_markdown_path, statement_id)
                    except KeyError:
                        raise TrestleError(f'Component id {by_comp.uuid} is not in the system implementation')

    def _process_by_component(self, by_comp: ossp.ByComponent, comp_path: pathlib.Path, control_id: str) -> None:
        """Complete the Markdown writing operations for each by-component assembly."""
        export_interface: ExportInterface = ExportInterface(by_comp=by_comp)

        leveraged_statements: Dict[str, LeveragedStatements] = self._statement_types_from_exports(export_interface)

        # Only create the directory if leveraged statements exist. If not return.
        if not leveraged_statements:
            logger.debug(f'Component {by_comp.component_uuid} has no exports for control {control_id}')
            return

        control_path: pathlib.Path = comp_path.joinpath(control_id)
        control_path.mkdir(exist_ok=True, parents=True)

        for statement_file_path, leveraged_stm in leveraged_statements.items():
            statement_path: pathlib.Path = control_path.joinpath(f'{statement_file_path}{const.MARKDOWN_FILE_EXT}')
            leveraged_stm.write_statement_md(statement_path)

    def _statement_types_from_exports(self, export_interface: ExportInterface) -> Dict[str, LeveragedStatements]:
        """Process all exports and return a file basename and LeveragedStatement object for each."""
        all_statements: Dict[str, LeveragedStatements] = {}

        for responsibility in export_interface.get_isolated_responsibilities():
            responsibility_stm = StatementResponsibility(responsibility.uuid, responsibility.description)
            all_statements[responsibility.uuid] = responsibility_stm

        for provided in export_interface.get_isolated_provided():
            provided_stm = StatementProvided(provided.uuid, provided.description)
            all_statements[provided.uuid] = provided_stm

        for responsibility, provided in export_interface.get_export_sets():
            set_stm = StatementTree(
                provided.uuid, provided.description, responsibility.uuid, responsibility.description
            )
            path = f'{provided.uuid}_{responsibility.uuid}'
            all_statements[path] = set_stm

        return all_statements
