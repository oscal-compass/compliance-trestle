# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""API for updating inheritance information in SSPs."""

import logging
import pathlib
from typing import Dict, List, Optional

import trestle.core.generators as gens
import trestle.oscal.common as common
import trestle.oscal.ssp as ossp
from trestle.common import const
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_list, none_if_empty
from trestle.core.catalog.catalog_api import CatalogAPI
from trestle.core.crm.export_reader import ExportReader
from trestle.core.crm.export_writer import ExportWriter
from trestle.core.remote.cache import FetcherFactory

logger = logging.getLogger(__name__)


class SSPInheritanceAPI():
    """API for updating inheritance information in SSPs through inheritance markdown."""

    def __init__(self, inheritance_md_path: pathlib.Path, trestle_root: pathlib.Path) -> None:
        """Initialize the SSP Inheritance API class."""
        self._inheritance_markdown_path: pathlib.Path = inheritance_md_path
        self._trestle_root: pathlib.Path = trestle_root

    def write_inheritance_as_markdown(
        self, leveraged_ssp_reference: str, catalog_api: Optional[CatalogAPI] = None
    ) -> None:
        """
        Write inheritance information to markdown.

        Args:
            leveraged_ssp: SSP to write inheritance information from.
            catalog_api: Catalog API to filter inheritance information by catalog.

        Notes:
            If a catalog API is provided, the written controls in the markdown will be filtered by the catalog.
        """
        fetcher = FetcherFactory.get_fetcher(self._trestle_root, leveraged_ssp_reference)
        leveraged_ssp: ossp.SystemSecurityPlan
        try:
            leveraged_ssp, _ = fetcher.get_oscal()
        except TrestleError as e:
            raise TrestleError(f'Unable to fetch ssp from {leveraged_ssp_reference}: {e}')

        if catalog_api is not None:
            control_imp: ossp.ControlImplementation = leveraged_ssp.control_implementation

            new_imp_requirements: List[ossp.ImplementedRequirement] = []
            for imp_requirement in as_list(control_imp.implemented_requirements):
                control = catalog_api._catalog_interface.get_control(imp_requirement.control_id)
                if control is not None:
                    new_imp_requirements.append(imp_requirement)
            control_imp.implemented_requirements = new_imp_requirements

            leveraged_ssp.control_implementation = control_imp

        export_writer: ExportWriter = ExportWriter(
            self._inheritance_markdown_path, leveraged_ssp, leveraged_ssp_reference
        )
        export_writer.write_exports_as_markdown()

    def update_ssp_inheritance(self, ssp: ossp.SystemSecurityPlan) -> None:
        """
        Update inheritance information in SSP.

        Args:
            ssp: SSP to update with inheritance information.
        """
        logger.debug('Reading inheritance information from markdown.')
        reader = ExportReader(self._inheritance_markdown_path, ssp)
        ssp = reader.read_exports_from_markdown()

        # Reader get reference
        leveraged_ssp_reference = reader.get_leveraged_ssp_href()

        fetcher = FetcherFactory.get_fetcher(self._trestle_root, leveraged_ssp_reference)
        leveraged_ssp: ossp.SystemSecurityPlan
        try:
            leveraged_ssp, _ = fetcher.get_oscal()
        except TrestleError as e:
            raise TrestleError(f'Unable to fetch ssp from {leveraged_ssp_reference}: {e}')

        link: common.Link = common.Link(href=leveraged_ssp_reference)
        leveraged_auths: List[ossp.LeveragedAuthorization] = []
        leveraged_auth: ossp.LeveragedAuthorization = gens.generate_sample_model(ossp.LeveragedAuthorization)
        leveraged_components: List[str] = reader.get_leveraged_components()

        if not leveraged_components:
            logger.warn(
                'No leveraged components mapped in inheritance view.',
                'No leveraged authorization will be added to the ssp'
            )
        else:
            if self._is_present_in_ssp(ssp, link):
                if ssp.system_implementation.leveraged_authorizations is not None:
                    leveraged_auth = ssp.system_implementation.leveraged_authorizations[0]
            else:
                leveraged_auth.links = as_list(leveraged_auth.links)
                leveraged_auth.links.append(link)

            # Set the title of the leveraged authorization
            leveraged_auth.title = f'Leveraged Authorization for {leveraged_ssp.metadata.title}'
            leveraged_auths.append(leveraged_auth)
        # Overwrite the leveraged authorization in the SSP. The only leveraged authorization should be the one
        # coming from inheritance view
        ssp.system_implementation.leveraged_authorizations = none_if_empty(leveraged_auths)

        # Reconcile the current leveraged components with the leveraged components in the inheritance view
        mapped_components: Dict[str, ossp.SystemComponent] = {}
        for component in as_list(leveraged_ssp.system_implementation.components):
            if component.title in leveraged_components:
                mapped_components[component.uuid] = component

        new_components: List[ossp.SystemComponent] = []
        for component in as_list(ssp.system_implementation.components):
            props_dict: Dict[str, str] = {}
            for prop in as_list(component.props):
                props_dict[prop.name] = prop.value

            # If this component is part of the original SSP components, add
            # and continue
            if const.LEV_AUTH_UUID not in props_dict:
                new_components.append(component)
                continue

            # If the leveraged component already exists, update the title, description, type, and status
            original_comp_uuid = props_dict[const.INHERITED_UUID]
            if original_comp_uuid in mapped_components:
                original_component = mapped_components.pop(original_comp_uuid)
                self._update_leveraged_system_component(component, original_component, leveraged_auth.uuid)
                new_components.append(component)

        # Add any remaining components to the new components
        for component in mapped_components.values():
            new_component: ossp.SystemComponent = gens.generate_sample_model(ossp.SystemComponent)
            self._update_leveraged_system_component(new_component, component, leveraged_auth.uuid)
            logger.debug(f'Adding component {new_component.title} to components.')
            new_components.append(new_component)

        ssp.system_implementation.components = new_components

    @staticmethod
    def _update_leveraged_system_component(
        new_comp: ossp.SystemComponent, original_comp: ossp.SystemComponent, leveraged_auth_id: str
    ) -> None:
        """Create a leveraged system component in the context of a leveraging system component."""
        new_comp.type = original_comp.type
        new_comp.title = original_comp.title
        new_comp.description = original_comp.description
        new_comp.status = original_comp.status

        new_comp.props = []
        new_comp.props.append(
            common.Property(name=const.IMPLEMENTATION_POINT, value=const.IMPLEMENTATION_POINT_EXTERNAL)
        )
        new_comp.props.append(common.Property(name=const.LEV_AUTH_UUID, value=leveraged_auth_id))
        new_comp.props.append(common.Property(name=const.INHERITED_UUID, value=original_comp.uuid))

    def _is_present_in_ssp(self, ssp: ossp.SystemSecurityPlan, link: common.Link) -> bool:
        if (ssp.system_implementation.leveraged_authorizations is not None
                and ssp.system_implementation.leveraged_authorizations[0].links is not None
                and ssp.system_implementation.leveraged_authorizations[0].links[0].href == link.href):
            return True
        else:
            return False
