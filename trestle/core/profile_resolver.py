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
"""Create resolved catalog from profile."""

import logging
import pathlib
from typing import Any, Dict, List, Optional, Tuple

import trestle.oscal.catalog as cat
import trestle.oscal.common as com
import trestle.oscal.profile as prof
from trestle.common.const import TRESTLE_INHERITED_PROPS_TRACKER
from trestle.common.list_utils import as_list, pop_item_from_list
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.control_interface import ParameterRep
from trestle.core.resolver._import import Import

logger = logging.getLogger(__name__)


class ProfileResolver():
    """Class to resolve a catalog given a profile."""

    @staticmethod
    def _extract_inherited_props(res_cat: cat.Catalog) -> Tuple[cat.Catalog, Dict[str, Any]]:
        """
        Build the control dict of inherited props.

        Args:
            The resolved profile catalog with a possible temporary part in each control

        Returns:
            The temporary parts are removed from each control and a Dict of added props per control_id is returned

        Notes:
        If an upstream profile adds props to the control they are tracked in a special temporary part in the control
        called const.TRESTLE_INHERITED_PROPS_TRACKER.  If that part is present in a control its contents should be added
        to the dict entry for that control, and the part removed from the control.
        """
        prop_dict: Dict[str, Any] = {}
        cat_interface = CatalogInterface(res_cat)
        for control in cat_interface.get_all_controls_from_dict():
            part: com.Part = pop_item_from_list(control.parts, TRESTLE_INHERITED_PROPS_TRACKER, lambda p: p.name)
            if part:
                props_list: List[Dict[str, Any]] = []
                for prop in as_list(part.props):
                    props_list.append({'name': prop.name, 'value': prop.value})
                for sub_part in as_list(part.parts):
                    for prop in as_list(sub_part.props):
                        props_list.append({'name': prop.name, 'value': prop.value, 'part_name': sub_part.title})
                prop_dict[control.id] = props_list
        cat_interface.update_catalog_controls()
        clean_res_cat = cat_interface.get_catalog()
        return clean_res_cat, prop_dict

    @staticmethod
    def get_resolved_profile_catalog_and_inherited_props(
        trestle_root: pathlib.Path,
        profile_path: str,
        block_adds: bool = False,
        block_params: bool = False,
        params_format: Optional[str] = None,
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES,
        show_value_warnings: bool = False,
        value_assigned_prefix: Optional[str] = None,
        value_not_assigned_prefix: Optional[str] = None
    ) -> Tuple[cat.Catalog, Optional[Dict[str, Any]]]:
        """
        Create the resolved profile catalog given a profile path along with inherited props.

        Args:
            trestle_root: root directory of the trestle workspace
            profile_path: string path or uri of the profile being resolved
            block_adds: prevent the application of adds in the final profile
            block_params: prevent the application of setparams in the final profile
            params_format: optional pattern with dot to wrap the param string, where dot represents the param string
            param_rep: desired way to convert params to strings
            show_value_warnings: warn if prose references a value that has not been set
            value_assigned_prefix: Prefix placed in front of param string if a value was assigned
            value_not_assigned_prefix: Prefix placed in front of param string if a value was *not* assigned

        Returns:
            The resolved profile catalog and a control dict of inherited props
        """
        logger.debug(f'get resolved profile catalog and inherited props for {profile_path} via generated Import.')
        import_ = prof.Import(href=str(profile_path), include_all={})
        # The final Import has change_prose=True to force parameter substitution in the prose only at the last stage.
        import_filter = Import(
            trestle_root,
            import_, [],
            True,
            block_adds,
            block_params,
            params_format,
            param_rep,
            None,
            show_value_warnings,
            value_assigned_prefix,
            value_not_assigned_prefix
        )
        logger.debug('launch pipeline')
        resolved_profile_catalog = next(import_filter.process())
        resolved_profile_catalog, inherited_props = ProfileResolver._extract_inherited_props(resolved_profile_catalog)
        return resolved_profile_catalog, inherited_props

    @staticmethod
    def get_resolved_profile_catalog(
        trestle_root: pathlib.Path,
        profile_path: str,
        block_adds: bool = False,
        block_params: bool = False,
        params_format: Optional[str] = None,
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES,
        show_value_warnings: bool = False,
        value_assigned_prefix: Optional[str] = None,
        value_not_assigned_prefix: Optional[str] = None
    ) -> cat.Catalog:
        """
        Create the resolved profile catalog given a profile path.

        Args:
            trestle_root: root directory of the trestle workspace
            profile_path: string path or uri of the profile being resolved
            block_adds: prevent the application of adds in the final profile
            block_params: prevent the application of setparams in the final profile
            params_format: optional pattern with dot to wrap the param string, where dot represents the param string
            param_rep: desired way to convert params to strings
            show_value_warnings: warn if prose references a value that has not been set
            value_assigned_prefix: Prefix placed in front of param string if a value was assigned
            value_not_assigned_prefix: Prefix placed in front of param string if a value was *not* assigned

        Returns:
            The resolved profile catalog
        """
        logger.debug(f'get resolved profile catalog for {profile_path} via generated Import.')
        resolved_profile_catalog, _ = ProfileResolver.get_resolved_profile_catalog_and_inherited_props(
            trestle_root,
            profile_path,
            block_adds,
            block_params,
            params_format,
            param_rep,
            show_value_warnings,
            value_assigned_prefix,
            value_not_assigned_prefix
        )
        return resolved_profile_catalog
