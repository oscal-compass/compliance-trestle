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
"""Provide interface to catalog allowing queries and operations at control level."""

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
        for extra_id in extra_ids:
            self._catalog_interface._control_dict.pop(extra_id)

        self._catalog_interface.update_catalog_controls()

    def _merge_header_and_comp_dict(
        self, control: cat.Control, control_file_path: pathlib.Path, context: ControlContext
    ) -> None:
        """
        Merge the header and the comp_dict.

        x-trestle-comp-def-rules:
        - name: XCCDF
            description: The XCCDF must be compliant
        x-trestle-rules-params:
        - name: foo_length
            description: minimum_foo_length
            rule-id: XCCDF
            options: '["6", "9"]'
        x-trestle-comp-def-param-vals:
        quantity_available: '500'
        foo_length: '6'
        x-trestle-global:
        profile-title: NIST Special Publication 800-53 Revision 5 MODERATE IMPACT BASELINE
        x-trestle-set-params:
        ac-1_prm_1:
            values: Param_1_value_in_catalog
        ac-1_prm_2:
            values:
        ac-1_prm_3:
            values:
        ac-1_prm_4:
            values:
        ac-1_prm_5:
            values:
        ac-1_prm_6:
            values:
        ac-1_prm_7:
            values:
        ---

        # now have all rules in context.rules_dict and all rules_params in context.rules_params_dict
        # all set-params per component for each control are in the cat interface
        # all comp-infos by control and part are in the cat interface
        #
        # can now write out catalog and pull from the markdown:
        # header for param values to set during assem
        # prose and status for This System
        # status for all parts that still have rules

        set COMP_DEF_RULES_TAG, RULES_PARAMS_TAG, COMP_DEF_RULES_PARAM_VALS_TAG, SET_PARAMS_TAG

        """
        memory_header, memory_comp_dict = self._catalog_interface._get_control_memory_info(control.id, context)
        # FIXME confirm this merge behavior
        ControlInterface.merge_dicts_deep(memory_header, context.merged_header, True)
        md_header, md_comp_dict = CatalogReader._read_comp_info_from_md(control_file_path, context)
        # get select info from md and update the memory comp_dict
        if const.SSP_MAIN_COMP_NAME in md_comp_dict:
            sys_memory_dict = memory_comp_dict.get(const.SSP_MAIN_COMP_NAME, {})
            sys_md_dict = md_comp_dict[const.SSP_MAIN_COMP_NAME]
            # for This System the md completely replaces what is in memory
            # but only for items that are in memory, which means they have rules
            for label, comp_info in memory_comp_dict.items():
                if label in sys_md_dict:
                    sys_memory_dict[label] = comp_info
            md_comp_dict.pop(const.SSP_MAIN_COMP_NAME)
        for comp_name, md_label_dict in md_comp_dict.items():
            memory_label_dict = memory_comp_dict.get(comp_name, None)
            if not memory_label_dict:
                continue
            for label, comp_info in md_label_dict.items():
                if label in memory_label_dict:
                    memory_label_dict[label].status = comp_info.status

        memory_rules_param_vals = memory_header.get(const.COMP_DEF_RULES_PARAM_VALS_TAG, {})
        md_rules_param_vals = md_header.get(const.COMP_DEF_RULES_PARAM_VALS_TAG, {})
        ControlInterface.merge_dicts_deep(memory_rules_param_vals, md_rules_param_vals, True)

        set_or_pop(memory_header, const.COMP_DEF_RULES_PARAM_VALS_TAG, memory_rules_param_vals)
        context.merged_header = memory_header
