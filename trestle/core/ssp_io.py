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

from typing import Optional

from trestle.core import catalog_interface
from trestle.core import profile_resolver
from trestle.oscal import profile, ssp


class SSPMarkdownRenderer():
    """Class to write control responses as markdown."""

    def __init__(self, ssp: ssp.SystemSecurityPlan, profile: profile.Profile):
        """Initialize the class."""
        self._ssp = ssp
        # resolve the catalog
        self._profile = profile
        self._resolve_catalog = profile_resolver.ProfileResolver.get_resolved_profile_catalog(self._profile)
        self._catalog_interface = catalog_interface.CatalogInterface(self._resolve_catalog)

    def _component_uuid_by_title(self, title: str) -> Optional[str]:
        """Get component uuid from the component title."""
        # FIXME: Clarify whether required or not.
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

    def control_statement(self, control_id: str) -> str:
        """
        Get the control statement for an ssp - to be printed in markdown as a structured list.

        Args:
            control_id: The control_id to use.

        Returns:
            A markdown blob as a string.
        """
        pass

    def fedramp_control_tables(self, control_id: str) -> str:
        """Get the fedramp metadata as markdown tables.

        The fedramp metadata has the following elements:
        - Responsible roles field
        - Parameter values table
        - Implementation status field
        - Control origination field

        Returns:
            tables as one coherent markdown blob.
        """

    # TODO: Ensure
    # 1 Get parameters from catalog
    # 2 update param with set parameter if required at
    # a. the control implementation level
    # b. The implemented requirement level
    # 3. Get responsible role ID's from implememented_requirement.roles
    # 4. Resolve responsible role-id to a human readable name.

    def _responsible_roles(self, control_id: str) -> str:
        """
        For each role id - if the role exists in metadata use the title as what gets printed in the roles table.

        If not (for now) warn and use the role-id as the printed text.
        """
        pass

    def _parameter_table(self, control_id: str) -> str:
        """Print Param_id | Default (aka label) | Value or set to 'none'."""
        pass

    def _fr_implementation_status(self, control_id: str) -> str:
        """
        Print implementation status as a list of items, only showing those that are applicable for the control.

        This is unlike the word document FedRAMP which uses checkboxes on standard set of options.
        Using a LUT to map between structured data fields, defined by FedRAMP and historical text.
        """
        pass

    def _fr_control_origination(self, control_id: str) -> str:
        """
        Print control origination, as a list of items, only showing those that are applicable for the control.

        Using a LUT to map between structured data fields, defined by FedRAMP and historical text.
        """
        pass

    def control_response(self, control_id) -> str:
        """
        Get the full control implemented requirements, broken down based on the available control responses.

        For components the following structure is assumed:

        'The System' is the default response, and all other components are treated as sub-headings per response item.
        """
        pass
