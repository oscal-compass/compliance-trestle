# Copyright (c) 2022 IBM Corp. All rights reserved.
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
from typing import Dict, Iterator, List, Optional
from uuid import uuid4

import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_list, none_if_empty
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.pipeline import Pipeline
from trestle.oscal import common

logger = logging.getLogger(__name__)


class Prune(Pipeline.Filter):
    """Prune the catalog based on the import include rule."""

    def __init__(self, import_: prof.Import, profile: prof.Profile) -> None:
        """
        Inject the import.

        This needs to be created prior to knowing the catalog.
        The profile itself is only needed for debug messages.
        The import is one possibly several imports in that profile.
        """
        self._import = import_
        self._profile = profile
        self._catalog_interface: Optional[CatalogInterface] = None
        self._catalog: Optional[cat.Catalog] = None

    def _set_catalog(self, catalog: cat.Catalog) -> None:
        """Set the catalog used by the catalog interface."""
        self._catalog_interface = CatalogInterface(catalog)
        self._catalog = catalog

    def _controls_selected(self, select_list: Optional[List[prof.SelectControlById]]) -> List[str]:
        control_ids: List[str] = []
        if select_list is not None:
            for select_control in select_list:
                if select_control.matching is not None:
                    raise TrestleError('Profiles with SelectControlById based on matching are not supported.')
                include_children = select_control.with_child_controls == 'yes'
                if select_control.with_ids:
                    new_ids = select_control.with_ids
                    for id_ in new_ids:
                        control_ids.append(id_)
                        if include_children:
                            control_ids.extend(self._catalog_interface.get_dependent_control_ids(id_))
        return [control_id.__root__ for control_id in control_ids]

    def _find_needed_control_ids(self) -> List[str]:
        """Get list of control_ids needed by profile and corresponding groups."""
        if self._import.include_controls is not None:
            include_ids = self._controls_selected(self._import.include_controls)
        else:
            if self._import.include_all is None:
                logger.warning('Profile does not specify include-controls, so including all.')
            include_ids = self._catalog_interface.get_control_ids()

        exclude_ids = self._controls_selected(self._import.exclude_controls)

        if not set(include_ids).issuperset(set(exclude_ids)):
            logger.debug(f'include_ids is not a superset of exclude_ids in import {self._import.href}')
        return sorted([id_ for id_ in include_ids if id_ not in exclude_ids])

    def _prune_control(self, needed_ids: List[str], control: cat.Control, exclude_ids: List[str]) -> cat.Control:
        """
        Prune the control based on the Import requirements.

        This is only called if the control is needed
        Some or all of its sub_controls may not be needed
        This always returns the original control, possibly with fewer subcontrols
        """
        if control.controls is None:
            return control
        controls = []
        for sub_control in control.controls:
            if sub_control.id in needed_ids and sub_control.id not in exclude_ids:
                controls.append(self._prune_control(needed_ids, sub_control, exclude_ids))
                exclude_ids.append(sub_control.id)
        control.controls = none_if_empty(controls)
        return control

    def _prune_controls(self, needed_ids: List[str]) -> List[str]:
        loaded_ids = []
        final_ids: List[str] = []
        for control_id in needed_ids:
            if control_id not in loaded_ids:
                control = self._catalog_interface.get_control(control_id)
                if control is None:
                    msg = (
                        f'Profile titled "{self._profile.metadata.title}" references control {control_id} '
                        f'but it is not in catalog titled "{self._catalog.metadata.title}"'
                    )
                    raise TrestleError(msg)
                control = self._prune_control(needed_ids, control, loaded_ids)
                self._catalog_interface.replace_control(control)
                loaded_ids.append(control_id)
                final_ids.append(control_id)
        return final_ids

    def _re_insert_child_controls(self, control: cat.Control) -> cat.Control:
        """Re insert this control and its children recursively."""
        new_controls = []
        for sub_control in as_list(control.controls):
            new_control = self._re_insert_child_controls(sub_control)
            new_controls.append(new_control)
        control.controls = none_if_empty(new_controls)
        return control

    def _re_insert_children(self) -> None:
        """Go through all controls in control dict and load child controls from control dict."""
        for control in self._catalog_interface.get_all_controls_from_dict():
            _ = self._re_insert_child_controls(control)

    def _prune_catalog(self) -> cat.Catalog:
        """Prune the controls in the current catalog."""
        if self._import is None:
            return self._catalog

        needed_ids = self._find_needed_control_ids()

        # if a control includes controls - only include those that we know are needed
        final_control_ids = self._prune_controls(needed_ids)

        self._re_insert_children()

        cat_controls = []

        # build the needed groups of controls
        group_dict: Dict[str, cat.Group] = {}
        for control_id in final_control_ids:
            control = self._catalog_interface.get_control(control_id)
            group_id, group_title, group_class = self._catalog_interface.get_group_info_by_control(control_id)
            if not group_id:
                cat_controls.append(control)
                continue
            group = group_dict.get(group_id)
            if group is None:
                group = cat.Group(id=group_id, title=group_title, class_=group_class, controls=[control])
                group_dict[group_id] = group
            else:
                group_dict[group_id].controls.append(control)

        new_groups: Optional[List[cat.Group]] = list(group_dict.values())

        # should avoid empty lists so set to None if empty
        new_groups = none_if_empty(new_groups)
        cat_controls = none_if_empty(cat_controls)
        new_params = self._catalog.params

        new_cat = cat.Catalog(
            uuid=str(uuid4()),
            metadata=self._catalog.metadata,
            back_matter=common.BackMatter(),
            controls=cat_controls,
            groups=new_groups,
            params=new_params
        )

        # find all referenced uuids - they should be 1:1 with those in backmatter
        needed_uuid_refs = ModelUtils.find_uuid_refs(new_cat)

        # prune the list of resources to only those that are needed
        new_resources: Optional[List[common.Resource]] = []
        if self._catalog.back_matter and self._catalog.back_matter.resources:
            new_resources = [res for res in self._catalog.back_matter.resources if res.uuid in needed_uuid_refs]
        new_resources = none_if_empty(new_resources)
        new_cat.back_matter.resources = new_resources

        return new_cat

    def process(self, catalog_iter: Iterator[cat.Catalog]) -> Iterator[cat.Catalog]:
        """
        Prune the catalog based on the include rule in the import_.

        This only processes the one catalog yielded by the one import in this pipeline.
        It must yield in order to have the merge filter loop over available imported catalogs.
        """
        self._set_catalog(next(catalog_iter))
        logger.debug(f'prune yielding catalog {self._catalog.metadata.title} with import {self._import.href}')
        yield self._prune_catalog()
