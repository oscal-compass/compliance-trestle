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

import logging
import pathlib
from typing import Dict, Iterator, List, Optional, Tuple

from pydantic import BaseModel

import trestle.core.const as const
import trestle.core.generators as gens
import trestle.oscal.catalog as cat
import trestle.oscal.ssp as ossp
from trestle.core.control_io import ControlIOReader, ControlIOWriter
from trestle.oscal import common
from trestle.oscal import profile as prof

logger = logging.getLogger(__name__)


class CatalogInterface():
    """
    Interface to query and modify catalog contents.

    The catalog is contained in two separate forms:  As an actual OSCAL catalog,
    and as a separate dict providing direct lookup of a control by id.

    The two representations should be converted as needed using provided routines:
    dict -> cat: update_catalog_controls
    cat -> dict: _create_control_dict

    In normal use the dict is created by the CatalogInterface constructor,
    changes are then made to controls in the dict,
    then the catalog controls are updated by pulling from the dict back into the catalog.

    This class does no direct file i/o.  i/o is performed via ControlIO.
    """

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

    def __init__(self, catalog: Optional[cat.Catalog] = None) -> None:
        """Initialize the interface with the catalog."""
        self._catalog = catalog
        self._param_dict: Dict[str, str] = {}
        self._control_dict = self._create_control_dict() if catalog else None

    def _add_params_to_dict(self, control: cat.Control) -> None:
        # this does not need to recurse because it is called for each control in the catalog
        if control.params is not None:
            for param in control.params:
                if param.id in self._param_dict:
                    logger.warning(
                        f'Duplicate param id {param.id} in control {control.id} and {self._param_dict[param.id]}.'
                    )
                self._param_dict[param.id] = control.id

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
            group_path = [const.MODEL_TYPE_CATALOG]
            for control in self._catalog.controls:
                new_path = group_path[:]
                new_path.append(control.id)
                control_handle = CatalogInterface.ControlHandle(
                    group_id=const.MODEL_TYPE_CATALOG,
                    group_title=const.MODEL_TYPE_CATALOG,
                    group_class=const.MODEL_TYPE_CATALOG,
                    control=control,
                    path=new_path
                )
                control_dict[control.id] = control_handle
                self._add_sub_controls(control_handle, control_dict, new_path)
        for handle in control_dict.values():
            self._add_params_to_dict(handle.control)
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

    def get_control(self, control_id: str) -> Optional[cat.Control]:
        """Get control from catalog with this id using the dict."""
        return None if control_id not in self._control_dict else self._control_dict[control_id].control

    def get_control_by_param_id(self, param_id: str) -> Optional[cat.Control]:
        """Get control from catalog that has this param id using the dict."""
        if param_id in self._param_dict:
            return self.get_control(self._param_dict[param_id])
        return None

    def get_control_part_prose(self, control_id: str, part_name: str) -> str:
        """Get the prose for a named part in the control."""
        control = self.get_control(control_id)
        return ControlIOWriter.get_part_prose(control, part_name)

    def get_all_controls_from_catalog(self, recurse: bool) -> Iterator[cat.Control]:
        """Yield all deep and individual controls from the actual catalog by group."""
        if self._catalog.groups:
            for group in self._catalog.groups:
                controls = self._get_all_controls_in_group(group, recurse)
                for control in controls:
                    yield control
        if self._catalog.controls:
            cat_controls = self._get_all_controls_in_list(self._catalog.controls, recurse)
            for control in cat_controls:
                yield control

    def get_all_controls_from_dict(self) -> Iterator[cat.Control]:
        """Yield individual controls from the dict."""
        return [handle.control for handle in self._control_dict.values()]

    def get_count_of_controls_in_dict(self) -> int:
        """Find number of controls in the dict."""
        return len(self._control_dict.keys())

    def get_count_of_controls_in_catalog(self, recurse: bool) -> int:
        """Get count of controls from the actual catalog."""
        return len(list(self.get_all_controls_from_catalog(recurse)))

    def get_group_info(self, control_id: str) -> Tuple[str, str, str]:
        """Get the group_id, title, class for this control from the dict."""
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

    def get_catalog(self, update=True) -> cat.Catalog:
        """Safe method to get catalog after forced update from catalog dict."""
        if update:
            self.update_catalog_controls()
        return self._catalog

    def _update_all_controls_in_list(self, controls: List[cat.Control]) -> List[cat.Control]:
        """Given a list of controls, create fresh list pulled from the control dict."""
        new_list: List[cat.Control] = []
        for control in controls:
            # first update the control itself by getting it from the dict
            control = self.get_control(control.id)
            # then update any controls it contains from the dict
            if control.controls:
                control.controls = self._update_all_controls_in_list(control.controls)
            new_list.append(control)
        return new_list

    def _update_all_controls_in_group(self, group: cat.Group) -> None:
        """Given a group of controls, create fresh version pulled from the control dict."""
        if group.controls:
            group.controls = self._update_all_controls_in_list(group.controls)
        if group.groups:
            new_groups: List[cat.Group] = []
            for sub_group in group.groups:
                self._update_all_controls_in_group(sub_group)
                new_groups.append(sub_group)
            group.groups = new_groups

    def update_catalog_controls(self) -> None:
        """Update the actual catalog by pulling fresh controls from the dict."""
        if self._catalog.groups:
            for group in self._catalog.groups:
                self._update_all_controls_in_group(group)
        if self._catalog.controls:
            self._catalog.controls = self._update_all_controls_in_list(self._catalog.controls)

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
        self,
        md_path: pathlib.Path,
        yaml_header: dict,
        sections: Optional[Dict[str, str]],
        responses: bool,
        additional_content: bool = False,
        profile: Optional[prof.Profile] = None,
        header_dont_merge: bool = False
    ) -> None:
        """Write out the catalog controls from dict as markdown to the given directory."""
        writer = ControlIOWriter()

        # create the directory in which to write the control markdown files
        md_path.mkdir(exist_ok=True, parents=True)
        catalog_interface = CatalogInterface(self._catalog)
        # write out the controls
        for control in catalog_interface.get_all_controls_from_catalog(True):
            group_id, group_title, _ = catalog_interface.get_group_info(control.id)
            group_dir = md_path if group_id == const.MODEL_TYPE_CATALOG else md_path / group_id
            if not group_dir.exists():
                group_dir.mkdir(parents=True, exist_ok=True)
            writer.write_control(
                group_dir,
                control,
                group_title,
                yaml_header,
                sections,
                additional_content,
                responses,
                profile,
                header_dont_merge
            )

    @staticmethod
    def _get_group_ids(md_path: pathlib.Path) -> List[str]:
        """Get the list of group ids from the directories in the markdown path."""
        group_ids: List[str] = []

        for gdir in md_path.glob('*/'):
            group_ids.append(str(gdir.stem))
        return group_ids

    def read_catalog_from_markdown(self, md_path: pathlib.Path) -> cat.Catalog:
        """
        Read the groups and catalog controls from the given directory.

        This will overwrite the existing groups and controls in the catalog.
        """
        if not self._catalog:
            self._catalog = gens.generate_sample_model(cat.Catalog)
        group_ids = self._get_group_ids(md_path)
        groups: List[cat.Group] = []
        # read each group dir
        for group_id in group_ids:
            new_group = cat.Group(id=group_id, title='')
            group_dir = md_path / group_id
            for control_path in group_dir.glob('*.md'):
                control = ControlIOReader.read_control(control_path)
                if not new_group.controls:
                    new_group.controls = []
                new_group.controls.append(control)
            groups.append(new_group)
        self._catalog.groups = groups if groups else None
        # now read any controls that aren't in a group
        controls: List[cat.Control] = []
        for control_path in md_path.glob('*.md'):
            control = ControlIOReader.read_control(control_path)
            controls.append(control)
        self._catalog.controls = controls if controls else None
        return self._catalog

    @staticmethod
    def read_catalog_imp_reqs(md_path: pathlib.Path,
                              component: ossp.SystemComponent) -> List[ossp.ImplementedRequirement]:
        """Read the full set of control implemented requirements from markdown.

        Args:
            md_path: Path to the markdown control files, with directories for each group
            component: The single system component that the implemented requirements will refer to by uuid

        Returns:
            list of implemented requirements gathered from each control
        """
        group_ids = CatalogInterface._get_group_ids(md_path)

        imp_reqs: List[ossp.ImplementedRequirement] = []
        for group_id in group_ids:
            group_path = md_path / group_id
            for control_file in group_path.glob('*.md'):
                imp_reqs.extend(ControlIOReader.read_implementations(control_file, component))
        return imp_reqs

    @staticmethod
    def read_additional_content(md_path: pathlib.Path) -> List[prof.Alter]:
        """Read all markdown controls and return list of alters."""
        group_ids = CatalogInterface._get_group_ids(md_path)

        new_alters: List[prof.Alter] = []
        for group_id in group_ids:
            group_path = md_path / group_id
            for control_file in group_path.glob('*.md'):
                new_alters.extend(ControlIOReader.read_new_alters(control_file))
        return new_alters

    @staticmethod
    def part_equivalent(a: common.Part, b: common.Part) -> bool:
        """Check if individual parts are equivalent."""
        # id's may be different because we create the id ourselves on read
        # FIXME should not need strip
        if a.name != b.name:
            return False
        if (a.prose is None) != (b.prose is None):
            return False
        if a.prose:
            if a.prose.strip() != b.prose.strip():
                return False
        if (a.parts is None) != (b.parts is None):
            return False
        if a.parts:
            if not CatalogInterface.parts_equivalent(a.parts, b.parts):
                return False
        return True

    @staticmethod
    def parts_equivalent(a: List[common.Part], b: List[common.Part]) -> bool:
        """Check if lists of parts are equivalent."""
        if len(a) != len(b):
            return False
        for pair in zip(a, b):
            if not CatalogInterface.part_equivalent(pair[0], pair[1]):
                return False
        return True

    @staticmethod
    def controls_equivalent(a: cat.Control, b: cat.Control) -> bool:
        """Check if the controls are equivalent."""
        if a.id != b.id:
            logging.error(f'ids differ: |{a.id}| |{b.id}|')
            return False
        if a.title != b.title:
            return False
        if (a.parts is None) != (b.parts is None):
            return False
        if a.parts:
            if not CatalogInterface.parts_equivalent(a.parts, b.parts):
                return False
        # FIXME cannot check controls until markdown lists sub-controls
        return True

    def equivalent_to(self, catalog: cat.Catalog) -> bool:
        """Test equivalence of catalog dict contents in various ways."""
        other = CatalogInterface(catalog)
        if other.get_count_of_controls_in_dict() != self.get_count_of_controls_in_dict():
            logging.error('count of controls is different')
            return False
        for a in self.get_all_controls_from_dict():
            try:
                b = other.get_control(a.id)
            except Exception as e:
                logging.error(f'error finding control {a.id} {e}')
            if not self.controls_equivalent(a, b):
                logging.error(f'controls differ: {a.id}')
                return False
        return True
