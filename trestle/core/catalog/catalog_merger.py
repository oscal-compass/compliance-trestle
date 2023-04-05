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
"""Provide interface to merge one catalog to another."""

import copy
import logging
import pathlib

import trestle.common.const as const
import trestle.oscal.catalog as cat
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_dict, as_filtered_list, as_list, delete_item_from_list, deep_set, get_item_from_list, none_if_empty, set_or_pop  # noqa E501
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.catalog.catalog_reader import CatalogReader
from trestle.core.control_context import ControlContext
from trestle.core.control_interface import ControlInterface

logger = logging.getLogger(__name__)


class CatalogMerger():
    """
    Catalog merger.

    Catalog merger handles all operations related to
    merging contents of one catalog to another.
    """

    def __init__(self, catalog_interface: CatalogInterface):
        """Initialize catalog merger."""
        self._catalog_interface = catalog_interface

    @staticmethod
    def merge_controls(dest: cat.Control, src: cat.Control, replace_params: bool) -> None:
        """
        Merge the src control into dest.

        Args:
            dest: destination control into which content will be added
            src: source control with new content
            replace_params: replace the control params with the new ones
        """
        ControlInterface.merge_parts(dest, src)
        if replace_params:
            dest.params = src.params

    def merge_catalog(self, catalog: cat.Catalog, replace_params: bool) -> None:
        """
        Merge the provided new catalog controls into the original catalog in this catalog interface.

        Args:
            catalog: catalog containing controls that are merged into the current catalog of the interface
            replace_params: replace all params in the control with the new ones

        Notes:
            This is mainly to support the reading of a catalog from markdown.  It allows retention of content such as
            metadata and backmatter, along with labels and other parameter attributes that aren't in markdown.
            The list of controls and group structure is specified by the markdown structure - but this doesn't allow
            controls to contain controls.  Group lists are specified per directory.

            Reading the markdown tells you groups and controls in them - and groups in groups.
            Controls cannot change groups.  If the control was in the original json, its parts are replaced,
            including its parameters.  Only values may be specified.  If no value specified, the value is unset in json.
        """
        cat_interface = CatalogInterface(catalog)
        for src in cat_interface.get_all_controls_from_dict():
            group_id, _, _ = cat_interface.get_group_info_by_control(src.id)
            dest = self._catalog_interface.get_control(src.id)
            if dest:
                dest_group, _, _ = self._catalog_interface.get_group_info_by_control(dest.id)
                if dest_group != group_id:
                    raise TrestleError(f'Markdown for control {src.id} has different group id.')
                CatalogMerger.merge_controls(dest, src, replace_params)
                self._catalog_interface.replace_control(dest)
            else:
                # this is a new control that isn't already in the merge destination
                # need to add the control knowing its group must already exist
                # get group info from an arbitrary control already present in group
                _, control_handle = self._catalog_interface._find_control_in_group(group_id)
                new_control_handle = copy.deepcopy(control_handle)
                new_control_handle.control = src
                # add the control and its handle to the param_dict
                self._catalog_interface._control_dict[src.id] = new_control_handle

        # now need to cull any controls that are not in the src catalog
        handled_ids = set(cat_interface._control_dict.keys())
        orig_ids = set(self._catalog_interface._control_dict.keys())
        extra_ids = orig_ids.difference(handled_ids)
        for extra_id in sorted(extra_ids):
            self._catalog_interface._control_dict.pop(extra_id)

        self._catalog_interface.update_catalog_controls()

    def _merge_header_and_comp_dict(
        self, control: cat.Control, control_file_path: pathlib.Path, context: ControlContext
    ) -> None:
        """
        Merge the header and the comp_dict.

        Notes:
            now have all rules in context.rules_dict and all rules_params in context.rules_params_dict
            all set-params per component for each control are in the cat interface
            all comp-infos by control and part are in the cat interface

            can now write out catalog and pull from the markdown:
            header for param values to set during assem
            prose and status for This System
            status for all parts that still have rules
        """
        memory_header, memory_comp_dict = self._catalog_interface._get_control_memory_info(control.id, context)
        ControlInterface.merge_dicts_deep(memory_header, context.merged_header, True)
        md_header, md_comp_dict = CatalogReader._read_comp_info_from_md(control_file_path, context)
        # md content replaces memory content but unless memory has no rules for it and the content is removed
        # but This System doesn't require rules, so its content is always kept

        # go through the just-read md_comp_dict and update the memory dict with contents in md
        if const.SSP_MAIN_COMP_NAME in md_comp_dict:
            memory_comp_dict[const.SSP_MAIN_COMP_NAME] = md_comp_dict[const.SSP_MAIN_COMP_NAME]
        for comp_name, md_label_dict in md_comp_dict.items():
            memory_label_dict = memory_comp_dict.get(comp_name, None)
            if comp_name != const.SSP_MAIN_COMP_NAME:
                if not memory_label_dict:
                    continue
                for label, comp_info in md_label_dict.items():
                    if label in memory_label_dict:
                        memory_label_dict[label] = comp_info

        memory_rules_param_vals = memory_header.get(const.COMP_DEF_RULES_PARAM_VALS_TAG, {})
        md_rules_param_vals = md_header.get(const.COMP_DEF_RULES_PARAM_VALS_TAG, {})
        for comp_name, val_list in md_rules_param_vals.items():
            val_dict = {val['name']: val for val in val_list}
            if comp_name not in memory_rules_param_vals:
                memory_rules_param_vals[comp_name] = val_list
            else:
                # merge the lists with priority to md
                new_list = []
                mem_list = memory_rules_param_vals[comp_name]
                mem_names = [mem['name'] for mem in mem_list]
                for val in mem_list:
                    new_list.append(val_dict.get(val['name'], val))
                for key, val in val_dict.items():
                    if key not in mem_names:
                        new_list.append(val)
                memory_rules_param_vals[comp_name] = new_list

        set_or_pop(memory_header, const.COMP_DEF_RULES_PARAM_VALS_TAG, memory_rules_param_vals)
        context.merged_header = memory_header
