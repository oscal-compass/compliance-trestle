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
from typing import Dict, List, Optional, Tuple

from trestle.common.common_types import TypeWithByComps
from trestle.common.const import CONTROL_ORIGINATION, IMPLEMENTATION_STATUS, ITEM
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_list
from trestle.core.catalog import catalog_interface
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.control_interface import ControlInterface
from trestle.core.docs_control_writer import DocsControlWriter
from trestle.core.markdown.docs_markdown_node import DocsMarkdownNode
from trestle.core.markdown.md_writer import MDWriter
from trestle.oscal import ssp
from trestle.oscal.catalog import Catalog

logger = logging.getLogger(__name__)


class SSPMarkdownWriter():
    """
    Class to write control responses as markdown.

    Functions in this class are mainly used by jinja and not by the trestle code itself.
    """

    def __init__(self, trestle_root: pathlib.Path) -> None:
        """Initialize the class."""
        self._trestle_root = trestle_root
        self._ssp: ssp.SystemSecurityPlan = None
        self._resolved_catalog: Catalog = None
        self._catalog_interface: CatalogInterface = None

    def set_ssp(self, ssp: ssp.SystemSecurityPlan) -> None:
        """Set ssp."""
        self._ssp = ssp

    def set_catalog(self, resolved_catalog: Catalog) -> None:
        """Set catalog."""
        self._resolved_catalog = resolved_catalog
        self._catalog_interface = catalog_interface.CatalogInterface(self._resolved_catalog)

    def get_control_statement(self, control_id: str, level: int) -> str:
        """
        Get the control statement for an ssp - to be printed in markdown as a structured list.

        Args:
            control_id: The control_id to use.

        Returns:
            A markdown blob as a string.
        """
        if not self._resolved_catalog:
            raise TrestleError('Cannot get control statement, set resolved catalog first.')

        writer = DocsControlWriter()
        control = self._catalog_interface.get_control(control_id)
        if not control:
            return ''

        control_lines = writer.get_control_statement_ssp(control)

        return self._build_tree_and_adjust(control_lines, level)

    def get_control_part(self, control_id: str, part_name: str, level: int) -> str:
        """Get control part with given name."""
        control_part = self._catalog_interface.get_control_part_prose(control_id, part_name)

        md_list = self._write_str_with_header(
            f'Control Part: {part_name} for control: {control_id}', control_part, level
        )
        return self._build_tree_and_adjust(md_list.split('\n'), level)

    def get_fedramp_control_tables(self, control_id: str, level: int, label_column: bool = False) -> str:
        """Get the fedramp metadata as markdown tables, with optional third label column for params.

        The fedramp metadata has the following elements:
        - Responsible roles field
        - Parameter values table
        - Implementation status field
        - Control origination field

        Returns:
            tables as one coherent markdown blob.
        """
        resp_roles_table = self.get_responsible_roles_table(control_id, level)
        params_values = self._parameter_table(control_id, level, label_column)
        impl_status = self.get_fedramp_implementation_status(control_id, level)
        control_orig = self.get_fedramp_control_origination(control_id, level)

        final_output = ''
        if resp_roles_table:
            final_output += resp_roles_table
        if params_values:
            final_output += '\n' + params_values
        if impl_status:
            final_output += '\n' + impl_status
        if control_orig:
            final_output += '\n' + control_orig
        return final_output

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
                    resp_roles = as_list(impl_requirement.responsible_roles)
                    role_ids = [role.role_id.replace('_', ' ') for role in resp_roles]

                    # now check if this role exists in the metadata
                    role_titles = dict(zip(role_ids, role_ids))
                    roles = as_list(self._ssp.metadata.roles)
                    for role in roles:
                        if role.id in role_ids:
                            role_titles[role.id] = role.title

                    # dictionary to md table
                    md_list = self._write_table_with_header(
                        'Responsible Roles.', [[key, role_titles[key]] for key in role_titles.keys()],
                        ['Role ID', 'Title'],
                        level
                    )
                    return md_list
                else:
                    logger.warning(
                        f'No responsible roles were found for the control with id: {control_id} in given SSP.'
                    )
                    return ''

        return ''

    def _parameter_table(self, control_id: str, level: int, label_column: bool = False) -> str:
        """Print Param_id | ValueOrLabelOrChoices | Optional Label Column."""
        if not self._ssp:
            raise TrestleError('Cannot get parameter table, set SSP first.')

        writer = DocsControlWriter()
        control = self._catalog_interface.get_control(control_id)
        if not control:
            return ''
        params_lines = writer.get_param_table(control, label_column)
        # need to make sure no params still have moustaches.  convert to brackets to avoid jinja complaints
        clean_lines = []
        for line in params_lines:
            clean_lines.append(line.replace('{{', '[[').replace('}}', ']]'))

        tree = DocsMarkdownNode.build_tree_from_markdown(clean_lines)
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

        implementation_statuses: List[str] = []
        control_impl_req = self._control_implemented_req(control_id)
        if control_impl_req and control_impl_req.props:
            for prop in control_impl_req.props:
                if prop.name == IMPLEMENTATION_STATUS:
                    implementation_statuses.append(prop.value)

        md_list = self._write_list_with_header('FedRamp Implementation Status.', implementation_statuses, level)
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

        md_list = self._write_list_with_header('FedRamp Control Origination.', control_origination, level)
        return md_list

    @staticmethod
    def _write_component_prompt(
        md_writer: MDWriter,
        comp_name: str,
        prose: str,
        rules: List[str],
        status: str,
        show_rules: bool,
        show_status: bool,
        show_comp: bool,
        level: int
    ) -> None:
        if comp_name and show_comp:
            header = f'Component: {comp_name}'
            md_writer.new_header(level, header)
        md_writer.set_indent_level(-1)
        md_writer.new_line(prose)
        md_writer.set_indent_level(-1)
        if rules and show_rules:
            md_writer.new_header((level + 1), title='Rules:')
            md_writer.set_indent_level(-1)
            md_writer.new_list(rules)
            md_writer.set_indent_level(-1)
        if status and show_status:
            md_writer.new_header((level + 1), title=f'Implementation Status: {status}')

    def get_control_response(
        self,
        control_id: str,
        level: int,
        write_empty_responses: bool = False,
        show_comp: bool = True,
        show_rules: bool = False,
        show_status: bool = True
    ) -> str:
        """
        Get the full control implemented requirements, broken down based on the available control responses.

        Args:
            control_id: id of the control
            level: level of indentation
            write_empty_responses: write response even if empty
            show_comp: show the component name in the response

        Notes:
            This is intended to be invoked from a jinja template that has already written out the prompt for
            control response
        """
        if not self._resolved_catalog:
            raise TrestleError('Cannot get control response, set resolved catalog first.')

        control = self._catalog_interface.get_control(control_id)
        imp_req = self._control_implemented_req(control_id)
        if not imp_req:
            logger.info(f'No implemented requirements found for the control {control_id}')
            return ''

        md_writer = MDWriter(None)

        # write out top-level implementation statements, whether or not this control has parts
        imp_req_responses = self._get_responses_by_components(imp_req, write_empty_responses)
        for comp_name, comp_response in imp_req_responses.items():
            prose, rules, status = comp_response
            SSPMarkdownWriter._write_component_prompt(
                md_writer, comp_name, prose, rules, status, show_rules, show_status, show_comp, 1
            )

        # iterate over statements, if present, to write out each part
        has_bycomps = imp_req.statements if imp_req.statements else []
        for has_bycomp in has_bycomps:
            statement_id = getattr(has_bycomp, 'statement_id', f'{control_id}_smt')
            label = statement_id
            part_name = None

            # look up label for this statement
            if control.parts:
                found_label, part = self._catalog_interface.get_statement_label_if_exists(control_id, statement_id)
                if found_label:
                    label = found_label
                    part_name = part.name

            response_per_component = self._get_responses_by_components(has_bycomp, write_empty_responses)

            if response_per_component or write_empty_responses:
                if part_name and part_name == ITEM:
                    # print part header only if subitem
                    header = f'Implementation for part {label}'
                    md_writer.new_header(1, title=header)
                for comp_name, comp_response in response_per_component.items():
                    prose, rules, status = comp_response
                    SSPMarkdownWriter._write_component_prompt(
                        md_writer, comp_name, prose, rules, status, show_rules, show_status, show_comp, 2
                    )

        lines = md_writer.get_lines()

        tree = DocsMarkdownNode.build_tree_from_markdown(lines)
        tree.change_header_level_by(level)

        return tree.content.raw_text

    def _get_responses_by_components(self, has_bycomps: TypeWithByComps,
                                     write_empty_responses: bool) -> Dict[str, Tuple[str, List[str], str]]:
        """Get response per component, substitute component id with title if possible."""
        response_per_component: Dict[str, Tuple[str, str]] = {}
        for by_comp in as_list(has_bycomps.by_components):  # type: ignore
            # look up component title
            subheader = by_comp.component_uuid
            prose = ''
            status = ''
            rules = []
            if self._ssp.system_implementation.components:
                for comp in self._ssp.system_implementation.components:
                    if comp.uuid == by_comp.component_uuid:
                        title = comp.title
                        if title:
                            subheader = title
            if by_comp.description:
                prose = by_comp.description
            if by_comp.implementation_status:
                status = by_comp.implementation_status.state
            rules, _ = ControlInterface.get_rule_list_for_item(by_comp)

            if prose or write_empty_responses:
                if subheader:
                    response_per_component[subheader] = (prose, rules, status)

        return response_per_component

    def _control_implemented_req(self, control_id: str) -> Optional[ssp.ImplementedRequirement]:
        """Retrieve control implemented requirement by control-id."""
        requirements = self._ssp.control_implementation.implemented_requirements
        for requirement in requirements:
            if requirement.control_id == control_id:
                return requirement
        logger.debug(f'No implemented requirement found for control {control_id}')
        return None

    def _write_list_with_header(self, header: str, lines: List[str], level: int) -> str:
        if lines:
            md_writer = MDWriter(None)
            md_writer.new_paragraph()
            md_writer.new_header(level=1, title=header)
            md_writer.set_indent_level(-1)
            md_writer.new_list(lines)
            md_writer.set_indent_level(-1)

            return self._build_tree_and_adjust(md_writer.get_lines(), level)

        return ''

    def _write_table_with_header(
        self, header: str, values: List[List[str]], table_header: List[str], level: int
    ) -> str:
        if values and values[0]:
            md_writer = MDWriter(None)
            md_writer.new_paragraph()
            md_writer.new_header(level=1, title=header)
            md_writer.set_indent_level(-1)
            md_writer.new_table(values, table_header)
            md_writer.set_indent_level(-1)

            return self._build_tree_and_adjust(md_writer.get_lines(), level)
        return ''

    def _write_str_with_header(self, header: str, text: str, level: int) -> str:
        if text:
            md_writer = MDWriter(None)
            md_writer.new_paragraph()
            md_writer.new_header(level=1, title=header)
            md_writer.set_indent_level(-1)
            md_writer.new_line(text)
            md_writer.set_indent_level(-1)

            return self._build_tree_and_adjust(md_writer.get_lines(), level)
        return ''

    def _build_tree_and_adjust(self, lines: List[str], level: int) -> str:
        tree = DocsMarkdownNode.build_tree_from_markdown(lines)
        tree.change_header_level_by(level)

        return tree.content.raw_text
