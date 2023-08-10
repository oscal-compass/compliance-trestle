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
"""Provided interface to read inheritance statements from Markdown."""

import logging
import os
import pathlib
from typing import Dict, List, Tuple

import trestle.core.generators as gens
import trestle.oscal.ssp as ossp
from trestle.common.list_utils import as_list, none_if_empty
from trestle.core.crm.bycomp_interface import ByComponentInterface
from trestle.core.crm.leveraged_statements import InheritanceMarkdownReader

logger = logging.getLogger(__name__)

# Provide name for this type
# Containing dictionary that is keyed by by_component uuid with a tuple of inherited and satisfied statements
ByComponentDict = Dict[str, Tuple[List[ossp.Inherited], List[ossp.Satisfied]]]

# Provide name for this type
# Containing dictionary that is keyed by control id with a dictionary of by_component information
InheritanceViewDict = Dict[str, ByComponentDict]


class ExportReader:
    """
    By-Component Assembly Exports Markdown reader.

    Export reader handles all operations related to reading authored inherited and satisfied statements from exports
    in Markdown.
    """

    def __init__(self, root_path: pathlib.Path, ssp: ossp.SystemSecurityPlan):
        """
        Initialize export reader.

        Arguments:
            root_path: A root path object where an SSP's inheritance markdown is located.
            ssp: A system security plan with exports
        """
        self._ssp: ossp.SystemSecurityPlan = ssp
        self._root_path: pathlib.Path = root_path

    def read_exports_from_markdown(self) -> ossp.SystemSecurityPlan:
        """Read inheritance markdown and update the SSP with the inheritance information."""
        impl_requirements: List[ossp.ImplementedRequirement] = []
        markdown_dict: InheritanceViewDict = self._read_inheritance_markdown_directory()

        for implemented_requirement in as_list(self._ssp.control_implementation.implemented_requirements):

            # If the control id existing in the markdown, then update the by_components
            if implemented_requirement.control_id in markdown_dict:

                new_by_comp: List[ossp.ByComponent] = []
                by_comp_dict: ByComponentDict = markdown_dict[implemented_requirement.control_id]

                for by_comp in as_list(implemented_requirement.by_components):

                    if by_comp.component_uuid in by_comp_dict:
                        comp_inheritance_info = by_comp_dict[by_comp.component_uuid]

                        bycomp_interface = ByComponentInterface(by_comp)
                        by_comp = bycomp_interface.reconcile_inheritance_by_component(
                            comp_inheritance_info[0], comp_inheritance_info[1]
                        )

                        # Delete the entry from the by_comp_dict once processed to avoid duplicates
                        del by_comp_dict[by_comp.component_uuid]

                    new_by_comp.append(by_comp)

                # Add any new by_components that were not in the original implemented requirement
                new_by_comp.extend(ExportReader._add_new_by_comps(by_comp_dict))

                implemented_requirement.by_components = new_by_comp

            # Update any implemented requirements statements assemblies
            new_statements: List[ossp.Statement] = []

            for stm in as_list(implemented_requirement.statements):
                statement_id = getattr(stm, 'statement_id', f'{implemented_requirement.control_id}_smt')

                # If the statement id existing in the markdown, then update the by_components
                if statement_id in markdown_dict:

                    new_by_comp: List[ossp.ByComponent] = []
                    by_comp_dict: ByComponentDict = markdown_dict[statement_id]

                    for by_comp in as_list(stm.by_components):

                        if by_comp.component_uuid in by_comp_dict:
                            comp_inheritance_info = by_comp_dict[by_comp.component_uuid]

                            bycomp_interface = ByComponentInterface(by_comp)
                            by_comp = bycomp_interface.reconcile_inheritance_by_component(
                                comp_inheritance_info[0], comp_inheritance_info[1]
                            )

                            # Delete the entry from the by_comp_dict once processed to avoid duplicates
                            del by_comp_dict[by_comp.component_uuid]

                        new_by_comp.append(by_comp)

                    # Add any new by_components that were not in the original statement
                    new_by_comp.extend(ExportReader._add_new_by_comps(by_comp_dict))

                    stm.by_components = new_by_comp

                new_statements.append(stm)

            implemented_requirement.statements = none_if_empty(new_statements)
            impl_requirements.append(implemented_requirement)

        self._ssp.control_implementation.implemented_requirements = impl_requirements
        return self._ssp

    def _read_inheritance_markdown_directory(self) -> InheritanceViewDict:
        """Read all inheritance markdown files and return a dictionary of all the information."""
        markdown_dict: InheritanceViewDict = {}

        # Creating a dictionary to find the component uuid by title for faster lookup
        uuid_by_title: Dict[str, str] = {}
        for component in as_list(self._ssp.system_implementation.components):
            uuid_by_title[component.title] = component.uuid

        for comp_dir in os.listdir(self._root_path):
            for control_dir in os.listdir(self._root_path.joinpath(comp_dir)):

                # Initialize the by component dictionary for the control directory
                # If it exists in the markdown dictionary, then update it with the new information
                by_comp_dict: ByComponentDict = {}
                if control_dir in markdown_dict:
                    by_comp_dict = markdown_dict[control_dir]

                for file in os.listdir(self._root_path.joinpath(comp_dir, control_dir)):
                    reader = InheritanceMarkdownReader(self._root_path.joinpath(comp_dir, control_dir, file))
                    leveraged_info = reader.process_leveraged_statement_markdown()

                    # If there is no leveraged information, then skip this file
                    if leveraged_info is None:
                        continue

                    for comp in leveraged_info.leveraging_comp_titles:
                        comp_uuid = uuid_by_title[comp]
                        inherited: List[ossp.Inherited] = []
                        satisfied: List[ossp.Satisfied] = []

                        # If the component uuid exists in the by_component dictionary, then update it
                        if comp_uuid in by_comp_dict:
                            inherited = by_comp_dict[comp_uuid][0]
                            satisfied = by_comp_dict[comp_uuid][1]

                        if leveraged_info.inherited is not None:
                            inherited.append(leveraged_info.inherited)
                        if leveraged_info.satisfied is not None:
                            satisfied.append(leveraged_info.satisfied)

                        by_comp_dict[comp_uuid] = (inherited, satisfied)

                markdown_dict[control_dir] = by_comp_dict
        return markdown_dict

    @staticmethod
    def _add_new_by_comps(by_comp_dict: ByComponentDict) -> List[ossp.ByComponent]:
        """Add new by_components to the implemented requirement."""
        new_by_comp: List[ossp.ByComponent] = []
        for comp_uuid, inheritance_info in by_comp_dict.items():
            by_comp: ossp.ByComponent = gens.generate_sample_model(ossp.ByComponent)
            by_comp.component_uuid = comp_uuid
            by_comp.inherited = none_if_empty(inheritance_info[0])
            by_comp.satisfied = none_if_empty(inheritance_info[1])
            new_by_comp.append(by_comp)
        return new_by_comp
