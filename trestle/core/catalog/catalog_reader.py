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
"""Provide interface to read catalog from markdown back to OSCAL."""

import logging
import pathlib
from typing import Any, Dict, List, Optional, Tuple

import trestle.common.const as const
import trestle.core.generic_oscal as generic
import trestle.oscal.catalog as cat
from trestle.common.list_utils import none_if_empty
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.control_context import ControlContext
from trestle.core.control_interface import CompDict, ControlInterface
from trestle.core.control_reader import ControlReader
from trestle.oscal import profile as prof
from trestle.oscal import ssp as ossp

logger = logging.getLogger(__name__)


class CatalogReader():
    """
    Catalog reader.

    Catalog reader handles all operations related to
    reading catalog from markdown.
    """

    def __init__(self, catalog_interface: CatalogInterface):
        """Initialize catalog reader."""
        self._catalog_interface = catalog_interface

    def read_additional_content(
        self,
        md_path: pathlib.Path,
        required_sections_list: List[str],
        label_map: Dict[str, Dict[str, str]],
        sections_dict: Dict[str, str],
        write_mode: bool
    ) -> Tuple[List[prof.Alter], Dict[str, Any], Dict[str, str]]:
        """Read all markdown controls and return list of alters plus control param dict and param sort map."""
        alters_map: Dict[str, prof.Alter] = {}
        final_param_dict: Dict[str, Any] = {}
        param_sort_map: Dict[str, str] = {}
        for group_path in CatalogInterface._get_group_ids_and_dirs(md_path).values():
            for control_file in group_path.glob('*.md'):
                sort_id, control_alters, control_param_dict = ControlReader.read_editable_content(
                    control_file,
                    required_sections_list,
                    label_map,
                    sections_dict,
                    write_mode
                )
                alters_map[sort_id] = control_alters
                for param_id, param_dict in control_param_dict.items():
                    # if profile_values are present, overwrite values with them
                    if const.PROFILE_VALUES in param_dict:
                        param_dict[const.VALUES] = param_dict.pop(const.PROFILE_VALUES)
                        final_param_dict[param_id] = param_dict
                        param_sort_map[param_id] = sort_id
        new_alters: List[prof.Alter] = []
        # fill the alters according to the control sorting order
        for key in sorted(alters_map.keys()):
            new_alters.extend(alters_map[key])
        return new_alters, final_param_dict, param_sort_map

    def read_catalog_from_markdown(self, md_path: pathlib.Path, set_parameters_flag: bool) -> cat.Catalog:
        """
        Read the groups and catalog controls from the given directory.

        This will overwrite the existing groups and controls in the catalog.
        """
        id_map = CatalogInterface._get_group_ids_and_dirs(md_path)
        groups: List[cat.Group] = []
        # read each group dir
        for group_id, group_dir in id_map.items():
            control_list_raw = []
            group_title = ''
            # Need to get group title from at least one control in this directory
            # All controls in dir should have same group title
            # Set group title to the first one found and warn if different non-empty title appears
            # Controls with empty group titles are tolerated but at least one title must be present or warning given
            # The special group with no name that has the catalog as parent is just a list and has no title
            for control_path in group_dir.glob('*.md'):
                control, control_group_title = ControlReader.read_control(control_path, set_parameters_flag)
                if control_group_title:
                    if group_title:
                        if control_group_title != group_title:
                            logger.warning(
                                f'Control {control.id} group title {control_group_title} differs from {group_title}'
                            )
                    else:
                        group_title = control_group_title
                control_list_raw.append(control)
            control_list = sorted(control_list_raw, key=lambda control: ControlInterface.get_sort_id(control))
            if group_id:
                if not group_title:
                    logger.warning(f'No group title found in controls for group {group_id}')
                new_group = cat.Group(id=group_id, title=group_title)
                new_group.controls = none_if_empty(control_list)
                groups.append(new_group)
            else:
                # if the list of controls has no group id it also has no title and is just the controls of the catalog
                self._catalog_interface._catalog.controls = none_if_empty(control_list)
        self._catalog_interface._catalog.groups = none_if_empty(groups)
        self._catalog_interface._create_control_dict()
        self._catalog_interface._catalog.params = none_if_empty(self._catalog_interface._catalog.params)
        return self._catalog_interface._catalog

    @staticmethod
    def read_catalog_imp_reqs(
        md_path: pathlib.Path,
        avail_comps: Dict[str, generic.GenericComponent],
        catalog_interface: Optional[CatalogInterface],
        context: ControlContext
    ) -> List[generic.GenericImplementedRequirement]:
        """Read the full set of control implemented requirements from markdown.

        Args:
            md_path: Path to the markdown control files, with directories for each group
            avail_comps: Dict mapping component names to known components

        Returns:
            List of implemented requirements gathered from each control

        Notes:
            As the controls are read into the catalog the needed components are added if not already available.
            avail_comps provides the mapping of component name to the actual component.
            This is only used for ssp via catalog_interface
        """
        imp_req_map: Dict[str, generic.GenericImplementedRequirement] = {}
        for group_path in CatalogInterface._get_group_ids_and_dirs(md_path).values():
            for control_file in group_path.glob('*.md'):
                control_id = control_file.stem
                comp_dict = catalog_interface.get_comp_info(control_id) if catalog_interface else {}
                sort_id, imp_req = ControlReader.read_implemented_requirement(
                    control_file, avail_comps, comp_dict, context
                )
                imp_req_map[sort_id] = imp_req
        return [imp_req_map[key] for key in sorted(imp_req_map.keys())]

    @staticmethod
    def _read_comp_info_from_md(control_file_path: pathlib.Path,
                                context: ControlContext) -> Tuple[Dict[str, Any], CompDict]:
        md_header = {}
        comp_dict = {}
        if control_file_path.exists():
            md_header, comp_dict = ControlReader.read_control_info_from_md(control_file_path, context)
        return md_header, comp_dict

    @staticmethod
    def read_ssp_md_content(
        md_path: pathlib.Path,
        ssp: ossp.SystemSecurityPlan,
        catalog_interface: CatalogInterface,
        context: ControlContext
    ) -> None:
        """
        Read md content into the ssp.

        Args:
            md_path: path to the catalog markdown
            ssp: ssp in which to insert the md content
            catalog_interface: catalog interface for the resolved profile catalog
            context: control context for the procedure

        Notes:
            The ssp should already contain info from the comp defs and this fills in selected content from md.
            The only content read from md is:
                ssp values in the comp def rules param vals of the header
                ssp values in the set-params of the header
                all prose for implementaton responses
                all status values
        """
        for group_path in CatalogInterface._get_group_ids_and_dirs(md_path).values():
            for control_file in group_path.glob('*.md'):
                md_header, comp_dict = CatalogReader._read_comp_info_from_md(control_file, context)
                pass
