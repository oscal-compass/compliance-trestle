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
"""Handle direct IO for writing SSP responses as markdown."""
import logging
import pathlib
from typing import List, Optional

from trestle.core import catalog_interface
from trestle.core import profile_resolver
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.const import CONTROL_ORIGINATION, IMPLEMENTATION_STATUS
from trestle.core.control_io import ControlIOWriter
from trestle.core.err import TrestleError
from trestle.core.markdown.markdown_node import MarkdownNode
from trestle.core.markdown.md_writer import MDWriter
from trestle.oscal import ssp
from trestle.oscal.catalog import Catalog

logger = logging.getLogger(__name__)


class SSPMarkdownWriter():
    """Class to write control responses as markdown."""

    def __init__(self, trestle_root: pathlib.Path):
        """Initialize the class."""
        self._trestle_root = trestle_root
        self._ssp: ssp.SystemSecurityPlan = None
        self._profile_path: pathlib.Path = None
        self._resolve_catalog: Catalog = None
        self._catalog_interface: CatalogInterface = None

    def set_ssp(self, ssp: ssp.SystemSecurityPlan):
        """Set ssp."""
        self._ssp = ssp

    def set_profile(self, profile_path: pathlib.Path):
        """Set profile."""
        self._profile_path = profile_path
        self._resolve_catalog = profile_resolver.ProfileResolver.get_resolved_profile_catalog(
            self._trestle_root, self._profile_path
        )
        self._catalog_interface = catalog_interface.CatalogInterface(self._resolve_catalog)

    def get_control_statement(self, control_id: str, level: int) -> str:
        """
        Get the control statement for an ssp - to be printed in markdown as a structured list.

        Args:
            control_id: The control_id to use.

        Returns:
            A markdown blob as a string.
        """
        if not self._profile_path:
            raise TrestleError('Cannot get control statement, set profile first.')

        writer = ControlIOWriter()
        control = self._catalog_interface.get_control(control_id)
        group_id, group_title, _ = self._catalog_interface.get_group_info_by_control(control.id)

        control_lines = writer.get_control_statement(control, group_title)

        return self._build_tree_and_adjust(control_lines, level)

    def get_control_part(self, control_id: str, part_name: str, level: int):
        """Get control part with given name."""
        control_part = self._catalog_interface.get_control_part_prose(control_id, part_name)

        md_list = self._write_text_with_header(
            f'Control Part: {part_name} for control: {control_id}', control_part, level
        )
        return md_list

    def get_fedramp_control_tables(self, control_id: str, level: int) -> str:
        """Get the fedramp metadata as markdown tables.

        The fedramp metadata has the following elements:
        - Responsible roles field
        - Parameter values table
        - Implementation status field
        - Control origination field

        Returns:
            tables as one coherent markdown blob.
        """
        resp_roles_table = self.get_responsible_roles_table(control_id, level)
        params_values = self._parameter_table(control_id, level)
        impl_status = self.get_fedramp_implementation_status(control_id, level)
        control_orig = self.get_fedramp_control_origination(control_id, level)

        return resp_roles_table + params_values + impl_status + control_orig

    # TODO: Ensure
    # 1 Get parameters from catalog
    # 2 update param with set parameter if required at
    # a. the control implementation level
    # b. The implemented requirement level
    # 3. Get responsible role ID's from implememented_requirement.roles
    # 4. Resolve responsible role-id to a human readable name.

    def get_responsible_roles_table(self, control_id: str, level: int) -> str:
        """
        For each role id - if the role exists in metadata use the title as what gets printed in the roles table.

        If not (for now) warn and use the role-id as the printed text.
        """
        if self._ssp is None:
            raise TrestleError('Cannot get responsible roles, SSP is not set.')

        for impl_requirement in self._ssp.control_implementation.implemented_requirements:
            if impl_requirement.control_id == control_id:
                if impl_requirement.responsible_roles:
                    role_ids = []
                    for resp_role in impl_requirement.responsible_roles:
                        role_ids.append(resp_role.role_id)

                    # now check if this role exists in the metadata
                    role_titles = dict(zip(role_ids, role_ids))
                    if self._ssp.metadata.roles:
                        for role in self._ssp.metadata.roles:
                            if role.id in role_ids:
                                role_titles[role.id] = role.title

                    # dictionary to md table
                    md_list = self._write_table_with_header(
                        f'Responsible Roles for control: {control_id}',
                        [[key, role_titles[key]] for key in role_titles.keys()],
                        level
                    )
                    return md_list
                else:
                    logger.warning(
                        f'No responsible roles were found for the control with id: {control_id} in given SSP.'
                    )
                    return ''

        return ''

    def _parameter_table(self, control_id: str, level: int) -> str:
        """Print Param_id | Default (aka label) | Value or set to 'none'."""
        writer = ControlIOWriter()
        control = self._catalog_interface.get_control(control_id)

        params_lines = writer.get_params(control)

        tree = MarkdownNode.build_tree_from_markdown(params_lines)
        tree.change_header_level_by(level)
        return tree.content.raw_text

    def get_fedramp_implementation_status(self, control_id: str, level: int) -> str:
        """
        Print implementation status as a list of items, only showing those that are applicable for the control.

        This is unlike the word document FedRAMP which uses checkboxes on standard set of options.
        Using a LUT to map between structured data fields, defined by FedRAMP and historical text.
        """
        if not self._ssp:
            raise TrestleError('Cannot get Fedramp implementation status, set SSP first.')

        implementation_statuses = []
        control_impl_req = self._control_implemented_req(control_id)
        if control_impl_req and control_impl_req.props:
            for prop in control_impl_req.props:
                if prop.name == IMPLEMENTATION_STATUS:
                    implementation_statuses.append(prop.value)

        md_list = self._write_list_with_header(
            f'FedRamp Implementation Status: {control_id}', implementation_statuses, level
        )
        return md_list

    def get_fedramp_control_origination(self, control_id: str, level: int) -> str:
        """
        Print control origination, as a list of items, only showing those that are applicable for the control.

        Using a LUT to map between structured data fields, defined by FedRAMP and historical text.
        """
        if not self._ssp:
            raise TrestleError('Cannot get FedRamp control origination, set SSP first.')

        control_origination = []
        control_impl_req = self._control_implemented_req(control_id)

        if control_impl_req and control_impl_req.props:
            for prop in control_impl_req.props:
                if prop.name == CONTROL_ORIGINATION:
                    control_origination.append(prop.value)

        md_list = self._write_list_with_header(
            f'FedRamp control origination for control: {control_id}', control_origination, level
        )
        return md_list

    def get_control_response(self, control_id: str, level: int) -> str:
        # Adjust the header levels
        """
        Get the full control implemented requirements, broken down based on the available control responses.

        For components the following structure is assumed:

        'The System' is the default response, and all other components are treated as sub-headings per response item.
        """
        if not self._profile_path:
            raise TrestleError('Cannot get control statement, set profile first.')

        writer = ControlIOWriter()
        control = self._catalog_interface.get_control(control_id)
        group_id, group_title, _ = self._catalog_interface.get_group_info_by_control(control.id)
        response_lines = writer.get_response(control)

        tree = MarkdownNode.build_tree_from_markdown(response_lines)
        tree.change_header_level_by(level)

        return tree.content.raw_text

    def does_have_control_part(self, control_id: str, part_name: str) -> bool:
        """Check if control have a part with given name."""
        if self.get_control_part(control_id, part_name, 0):
            return True
        else:
            return False

    def _component_uuid_by_title(self, title: str) -> Optional[str]:
        """Get component uuid from the component title."""
        components = self._ssp.system_implementation.components

        for component in components:
            if component.title == title:
                return component.uuid
        return None

    def _control_implemented_req(self, control_id: str) -> ssp.ImplementedRequirement:
        """Retrieve control implemented requirement by control-id."""
        requirements = self._ssp.control_implementation.implemented_requirements
        for requirement in requirements:
            if requirement.control_id == control_id:
                return requirement

    def _write_list_with_header(self, header: str, lines: List[str], level: int):
        md_writer = MDWriter(None)
        md_writer.new_paragraph()
        md_writer.new_header(level=level, title=header)
        md_writer.set_indent_level(-1)
        md_writer.new_list(lines)
        md_writer.set_indent_level(-1)

        return self._build_tree_and_adjust(md_writer.get_lines(), level)

    def _write_table_with_header(self, header: str, values: List[List[str]], level: int):
        md_writer = MDWriter(None)
        md_writer.new_paragraph()
        md_writer.new_header(level=level, title=header)
        md_writer.set_indent_level(-1)
        md_writer.new_table(values)
        md_writer.set_indent_level(-1)

        return self._build_tree_and_adjust(md_writer.get_lines(), level)

    def _write_text_with_header(self, header: str, text: str, level: int):
        md_writer = MDWriter(None)
        md_writer.new_paragraph()
        md_writer.new_header(level=level, title=header)
        md_writer.set_indent_level(-1)
        md_writer.new_line(text)
        md_writer.set_indent_level(-1)

        return self._build_tree_and_adjust(md_writer.get_lines(), level)

    def _build_tree_and_adjust(self, lines: List[str], level: int) -> str:
        tree = MarkdownNode.build_tree_from_markdown(lines)
        tree.change_header_level_by(level)

        return tree.content.raw_text
