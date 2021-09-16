# Copyright (c) 2021 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Create resolved catalog from profile."""

import logging
import pathlib
from typing import Dict, Iterator, List, Optional, Tuple

from pydantic import BaseModel

import trestle.oscal.catalog as cat
import trestle.oscal.ssp as ossp
from trestle.core.control_io import ControlIo
from trestle.oscal import common

logger = logging.getLogger(__name__)


class CatalogInterface():
    """Interface to query and modify catalog contents."""

    class ControlHandle(BaseModel):
        """Convenience class for handling controls as members of a group.

        group_id: id of parent group or 'catalog' if not in a group
        group_title: title of the group
        group_class: class of the group
        path: path of parent controls leading to this child control
        control: the control itself
        """

        group_id: str
        group_title: Optional[str]
        group_class: Optional[str]
        path: List[str]
        control: cat.Control

    def __init__(self, catalog: cat.Catalog) -> None:
        """Initialize the interface with the catalog."""
        self._catalog = catalog
        self._control_dict = self._create_control_dict()

    def _add_sub_controls(
        self, control_handle: ControlHandle, control_dict: Dict[str, ControlHandle], path: List[str]
    ) -> None:
        """
        Get all controls contained in this control and add it to the growing dict.

        Add all its sub-controls to the dict recursively.
        """
        if control_handle.control.controls:
            group_id = control_handle.group_id
            group_title = control_handle.group_title
            group_class = control_handle.group_class
            for sub_control in control_handle.control.controls:
                new_path = path[:]
                new_path.append(sub_control.id)
                control_handle = CatalogInterface.ControlHandle(
                    group_id=group_id,
                    group_title=group_title,
                    group_class=group_class,
                    path=new_path,
                    control=sub_control
                )
                control_dict[sub_control.id] = control_handle
                self._add_sub_controls(control_handle, control_dict, new_path)

    def _add_group_controls(self, group: cat.Group, control_dict: Dict[str, ControlHandle], path: List[str]) -> None:
        if group.controls is not None:
            group_path = path[:]
            group_path.append(group.id)
            for control in group.controls:
                new_path = group_path[:]
                new_path.append(control.id)
                control_handle = CatalogInterface.ControlHandle(
                    group_id=group.id,
                    group_title=group.title,
                    group_class=group.class_,
                    control=control,
                    path=new_path
                )
                control_dict[control.id] = control_handle
                self._add_sub_controls(control_handle, control_dict, new_path)
        if group.groups is not None:
            group_path = path[:]
            group_path.append(group.id)
            for sub_group in group.groups:
                new_path = group_path[:]
                new_path.append(sub_group.id)
                self._add_group_controls(sub_group, control_dict, new_path)

    def _create_control_dict(self) -> Dict[str, ControlHandle]:
        control_dict: Dict[str, CatalogInterface.ControlHandle] = {}
        # add controls by group
        if self._catalog.groups is not None:
            for group in self._catalog.groups:
                self._add_group_controls(group, control_dict, [])
        # now add controls not in a group, if any
        if self._catalog.controls is not None:
            group_path = ['catalog']
            for control in self._catalog.controls:
                new_path = group_path[:]
                new_path.append(control.id)
                control_handle = CatalogInterface.ControlHandle(
                    group_id='catalog', group_title='catalog', group_class='catalog', control=control, path=new_path
                )
                control_dict[control.id] = control_handle
                self._add_sub_controls(control_handle, control_dict, new_path)
        return control_dict

    def _get_all_controls_in_list(self, controls: List[cat.Control], recurse: bool) -> List[cat.Control]:
        new_list: List[cat.Control] = []
        for control in controls:
            new_list.append(control)
            if recurse and control.controls:
                new_list.extend(self._get_all_controls_in_list(control.controls, recurse))
        return new_list

    def _get_all_controls_in_group(self, group: cat.Group, recurse: bool) -> cat.Control:
        """Create a list of all controls in this group."""
        controls: List[cat.Control] = []
        if group.controls:
            controls.extend(self._get_all_controls_in_list(group.controls, recurse))
        if recurse and group.groups:
            for group in group.groups:
                if group.controls:
                    controls.extend(self._get_all_controls_in_group(group, recurse))
        return controls

    def get_dependent_control_ids(self, control_id: str) -> List[str]:
        """Find all children of this control."""
        children: List[str] = []
        control = self.get_control(control_id)
        if control.controls:
            new_controls = self._get_all_controls_in_list(control.controls, True)
            children.extend([con.id for con in new_controls])
        return children

    def get_control_ids(self) -> List[str]:
        """Get all control ids in catalog using the dict."""
        return self._control_dict.keys()

    def get_control(self, control_id: str) -> cat.Control:
        """Get control from catalog with this id using the dict."""
        return self._control_dict[control_id].control

    def get_all_controls(self, recurse: bool) -> Iterator[cat.Control]:
        """Yield all deep and individual controls from the catalog by group."""
        if self._catalog.groups:
            for group in self._catalog.groups:
                controls = self._get_all_controls_in_group(group, recurse)
                for control in controls:
                    yield control
        if self._catalog.controls:
            cat_controls = self._get_all_controls_in_list(self._catalog.controls, recurse)
            for control in cat_controls:
                yield control

    def get_count_of_controls(self, recurse: bool) -> int:
        """Find number of controls in the catalog with or without recursion."""
        return len(list(self.get_all_controls(recurse)))

    def get_group_info(self, control_id: str) -> Tuple[str, str, str]:
        """Get the group_id, title, class for this control."""
        return (
            self._control_dict[control_id].group_id,
            self._control_dict[control_id].group_title,
            self._control_dict[control_id].group_class
        )

    def get_path(self, control_id: str) -> List[str]:
        """Return the path into the catalog for this control."""
        return self._control_dict[control_id].path

    def replace_control(self, control: cat.Control) -> None:
        """Replace the control in the control_dict after modifying it."""
        self._control_dict[control.id].control = control

    def _update_all_controls_in_list(self, controls: List[cat.Control]) -> List[cat.Control]:
        new_list: List[cat.Control] = []
        for control in controls:
            new_list.append(self.get_control(control.id))
        return new_list

    def _update_all_controls_in_group(self, group: cat.Group) -> None:
        if group.controls:
            group.controls = self._update_all_controls_in_list(group.controls)
        if group.groups:
            new_groups: List[cat.Group] = []
            for sub_group in group.groups:
                self._update_all_controls_in_group(sub_group)
                new_groups.append(sub_group)
            group.groups = new_groups

    # below are utility functions

    def _find_string_in_part(self, control_id: str, part: common.Part, seek_str: str) -> List[str]:
        hits: List[str] = []
        if part.prose:
            if part.prose.find(seek_str) >= 0:
                hits.append((control_id, part.prose))
        if part.parts:
            for sub_part in part.parts:
                hits.extend(self._find_string_in_part(control_id, sub_part, seek_str))
        return hits

    def find_string_in_control(self, control: cat.Control, seek_str: str) -> List[Tuple[str, str]]:
        """Find all instances of this string in prose of control."""
        hits: List[Tuple[str, str]] = []
        if control.parts:
            for part in control.parts:
                hits.extend(self._find_string_in_part(control.id, part, seek_str))
        return hits

    def write_catalog_as_markdown(
        self, md_path: pathlib.Path, yaml_header: dict, sections: Optional[Dict[str, str]], all_details: bool
    ) -> None:
        """Write out the catalog controls as markdown to the given directory."""
        control_io = ControlIo()

        # create the directory in which to write the control markdown files
        md_path.mkdir(exist_ok=True, parents=True)
        catalog_interface = CatalogInterface(self._catalog)
        # write out the controls
        for control in catalog_interface.get_all_controls(True):
            group_id, group_title, _ = catalog_interface.get_group_info(control.id)
            out_path = md_path / group_id
            control_io.write_control(out_path, control, group_title, yaml_header, sections)

    @staticmethod
    def _get_group_ids(md_path: pathlib.Path) -> List[str]:
        """Get the list of group ids from the directories in the markdown path."""
        group_ids: List[str] = []

        for gdir in md_path.glob('*/'):
            group_ids.append(str(gdir.stem))
        return group_ids

    def read_catalog_from_markdown(self, md_path: pathlib.Path, component: ossp.SystemComponent) -> None:
        """Read the catalog controls from the given directory."""
        # create implementation requirements for each control, linked to the dummy component uuid
        control_io = ControlIo()
        group_ids = self._get_group_ids(md_path)
        for group_id in group_ids:
            group_path = md_path / group_id
            for control_file in group_path.glob('*.md'):
                control = control_io.read_control_full(control_file)
                self.replace_control(control)

    @staticmethod
    def read_catalog_imp_reqs(md_path: pathlib.Path, component: ossp.SystemComponent) -> None:
        """Read the full set of control implemented requirements from markdown."""
        # create implementation requirements for each control, linked to the dummy component uuid
        # find all groups in the markdown dir
        group_ids = CatalogInterface._get_group_ids(md_path)

        imp_reqs: List[ossp.ImplementedRequirement] = []
        control_io = ControlIo()
        for group_id in group_ids:
            group_path = md_path / group_id
            for control_file in group_path.glob('*.md'):
                imp_reqs.extend(control_io.get_implementations(control_file, component))
        return imp_reqs
