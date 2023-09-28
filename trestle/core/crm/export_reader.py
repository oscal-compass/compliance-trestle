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
from trestle.common.common_types import TypeWithByComps
from trestle.common.err import TrestleError
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
    in Markdown. The reader will read all the markdown files in the exports directory and update the SSP with the
    inheritance.
    """

    def __init__(self, root_path: pathlib.Path, ssp: ossp.SystemSecurityPlan):
        """
        Initialize export reader.

        Arguments:
            root_path: A root path object where an SSP's inheritance markdown is located.
            ssp: A system security plan object that will be updated with the inheritance information.

        Notes:
            The mapped components list is used to track which components have been mapped to controls in the markdown.
            It can be retrieved with the get_leveraged_components method. This will be empty until the
            read_exports_from_markdown method is called.
        """
        self._ssp: ossp.SystemSecurityPlan = ssp

        # Create a dictionary of implemented requirements keyed by control id for merging operations
        self._implemented_requirements: Dict[str, ossp.ImplementedRequirement] = self._create_impl_req_dict()

        # List of component titles that have been mapped to controls in the Markdown
        self._mapped_components: List[str] = []

        self._root_path: pathlib.Path = root_path

    def _create_impl_req_dict(self) -> Dict[str, ossp.ImplementedRequirement]:
        """Create a dictionary of implemented requirements keyed by control id."""
        impl_req_dict: Dict[str, ossp.ImplementedRequirement] = {}
        for impl_req in as_list(self._ssp.control_implementation.implemented_requirements):
            impl_req_dict[impl_req.control_id] = impl_req
        return impl_req_dict

    def read_exports_from_markdown(self) -> ossp.SystemSecurityPlan:
        """Read inheritance markdown and update the SSP with the inheritance information."""
        # Read the information from the markdown files into a dictionary for quick lookup
        markdown_dict: InheritanceViewDict = self._read_inheritance_markdown_directory()

        # Merge the markdown information into existing the implemented requirements
        self._merge_exports_implemented_requirements(markdown_dict)

        # Process remaining markdown information that was not in the implemented requirements
        for control_id, by_comp_dict in markdown_dict.items():
            if by_comp_dict:
                logging.debug(f'Adding control mapping {control_id} to implemented requirements')
                self._add_control_mappings_to_implemented_requirements(control_id, by_comp_dict)

        self._ssp.control_implementation.implemented_requirements = list(self._implemented_requirements.values())
        return self._ssp

    def get_leveraged_ssp_href(self) -> str:
        """Get the href of the leveraged SSP from a markdown file."""
        comp_dirs = os.listdir(self._root_path)
        if len(comp_dirs) == 0:
            raise TrestleError('No components were found in the markdown.')

        control_dirs = os.listdir(self._root_path.joinpath(comp_dirs[0]))
        if len(control_dirs) == 0:
            raise TrestleError('No controls were found in the markdown for component {comp_dirs[0]}.')

        control_dir = self._root_path.joinpath(comp_dirs[0], control_dirs[0])

        files = [f for f in os.listdir(control_dir) if os.path.isfile(os.path.join(control_dir, f))]
        if len(files) == 0:
            raise TrestleError(f'No files were found in the markdown for control {control_dirs[0]}.')

        markdown_file_path = control_dir.joinpath(files[0])
        reader = InheritanceMarkdownReader(markdown_file_path)
        return reader.get_leveraged_ssp_reference()

    def get_leveraged_components(self) -> List[str]:
        """Get a list of component titles that have been mapped to controls in the Markdown."""
        return self._mapped_components

    def _merge_exports_implemented_requirements(self, markdown_dict: InheritanceViewDict) -> None:
        """Merge all exported inheritance info from the markdown into the implemented requirement dict."""
        for implemented_requirement in self._implemented_requirements.values():

            # If the control id existing in the markdown, then update the by_components
            if implemented_requirement.control_id in markdown_dict:

                # Delete the entry from the markdown_dict once processed to avoid duplicates
                by_comp_dict: ByComponentDict = markdown_dict.pop(implemented_requirement.control_id)

                self._update_type_with_by_comp(implemented_requirement, by_comp_dict)

            # Update any implemented requirements statements assemblies
            new_statements: List[ossp.Statement] = []

            for stm in as_list(implemented_requirement.statements):
                statement_id = getattr(stm, 'statement_id', f'{implemented_requirement.control_id}_smt')

                # If the statement id existing in the markdown, then update the by_components
                if statement_id in markdown_dict:

                    # Delete the entry from the markdown_dict once processed to avoid duplicates
                    by_comp_dict: ByComponentDict = markdown_dict.pop(statement_id)

                    self._update_type_with_by_comp(stm, by_comp_dict)

                new_statements.append(stm)

            implemented_requirement.statements = none_if_empty(new_statements)

    def _update_type_with_by_comp(self, with_bycomp: TypeWithByComps, by_comp_dict: ByComponentDict) -> None:
        """Update the by_components for a type with by_components."""
        new_by_comp: List[ossp.ByComponent] = []

        by_comp: ossp.ByComponent
        comp_inheritance_info: Tuple[List[ossp.Inherited], List[ossp.Satisfied]]
        for by_comp in as_list(with_bycomp.by_components):

            # If the by_component uuid exists in the by_comp_dict, then update it
            # If not, clear the by_component inheritance information
            comp_inheritance_info = by_comp_dict.pop(by_comp.component_uuid, ([], []))

            bycomp_interface = ByComponentInterface(by_comp)
            by_comp = bycomp_interface.reconcile_inheritance_by_component(
                comp_inheritance_info[0], comp_inheritance_info[1]
            )

            new_by_comp.append(by_comp)

        # Add any new by_components that were not in the original statement
        new_by_comp.extend(ExportReader._add_new_by_comps(by_comp_dict))
        with_bycomp.by_components = none_if_empty(new_by_comp)

    def _add_control_mappings_to_implemented_requirements(
        self, control_mapping: str, by_comps: ByComponentDict
    ) -> None:
        """Add control mappings to implemented requirements."""
        # Determine if the control id is actually a statement id
        if '_smt.' in control_mapping:
            control_id = control_mapping.split('_smt')[0]
            implemented_req = self._add_or_get_implemented_requirement(control_id)
            statement = gens.generate_sample_model(ossp.Statement)
            statement.statement_id = control_mapping
            statement.by_components = ExportReader._add_new_by_comps(by_comps)
            implemented_req.statements = as_list(implemented_req.statements)
            implemented_req.statements.append(statement)
            implemented_req.statements = sorted(implemented_req.statements, key=lambda x: x.statement_id)
        else:
            implemented_req = self._add_or_get_implemented_requirement(control_mapping)
            implemented_req.by_components = as_list(implemented_req.by_components)
            implemented_req.by_components.extend(ExportReader._add_new_by_comps(by_comps))

    def _add_or_get_implemented_requirement(self, control_id: str) -> ossp.ImplementedRequirement:
        """Add or get implemented requirement from implemented requirements dictionary."""
        if control_id in self._implemented_requirements:
            return self._implemented_requirements[control_id]

        implemented_requirement = gens.generate_sample_model(ossp.ImplementedRequirement)
        implemented_requirement.control_id = control_id
        self._implemented_requirements[control_id] = implemented_requirement
        return implemented_requirement

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

    def _read_inheritance_markdown_directory(self) -> InheritanceViewDict:
        """Read all inheritance markdown files and return a dictionary of all the information."""
        markdown_dict: InheritanceViewDict = {}

        # Creating a dictionary to find the component uuid by title for faster lookup
        uuid_by_title: Dict[str, str] = {}
        for component in as_list(self._ssp.system_implementation.components):
            uuid_by_title[component.title] = component.uuid

        for comp_dir in os.listdir(self._root_path):
            is_comp_leveraged = False
            for control_dir in os.listdir(os.path.join(self._root_path, comp_dir)):
                control_dir_path = os.path.join(self._root_path, comp_dir, control_dir)

                # Initialize the by_component dictionary for the control directory
                # If it exists in the markdown dictionary, then update it with the new information
                by_comp_dict = markdown_dict.get(control_dir, {})

                for file in os.listdir(control_dir_path):
                    file_path = pathlib.Path(control_dir_path).joinpath(file)
                    reader = InheritanceMarkdownReader(file_path)
                    leveraged_info = reader.process_leveraged_statement_markdown()

                    # If there is no leveraged information, then skip this file
                    if leveraged_info is None:
                        continue

                    # If a file has leveraged information, then set the flag to indicate the component is leveraged
                    is_comp_leveraged = True

                    for comp in leveraged_info.leveraging_comp_titles:
                        if comp not in uuid_by_title:
                            keys_as_string = ', '.join(uuid_by_title.keys())
                            raise TrestleError(
                                f'Component "{comp}" does not exist in the {self._ssp.metadata.title} SSP. '
                                f'Please use options: {keys_as_string}.'
                            )

                        comp_uuid = uuid_by_title[comp]
                        inherited, satisfied = by_comp_dict.get(comp_uuid, ([], []))

                        if leveraged_info.inherited is not None:
                            inherited.append(leveraged_info.inherited)
                        if leveraged_info.satisfied is not None:
                            satisfied.append(leveraged_info.satisfied)

                        by_comp_dict[comp_uuid] = (inherited, satisfied)

                markdown_dict[control_dir] = by_comp_dict

            if is_comp_leveraged:
                self._mapped_components.append(comp_dir)

        return markdown_dict
