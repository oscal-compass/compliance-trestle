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
import re
from typing import Callable, Dict, Iterator, List, Optional, Tuple

from pydantic import BaseModel

import trestle.core.const as const
import trestle.core.generators as gens
import trestle.oscal.catalog as cat
import trestle.oscal.ssp as ossp
from trestle.core.control_io import ControlIOReader, ControlIOWriter
from trestle.core.trestle_base_model import TrestleBaseModel
from trestle.core.utils import as_list
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

    class ControlHandle(TrestleBaseModel):
        """Convenience class for handling controls as members of a group.

        group_id: id of parent group or '' if not in a group
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
        for param in as_list(control.params):
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
            group_path = ['']
            for control in self._catalog.controls:
                new_path = group_path[:]
                new_path.append(control.id)
                control_handle = CatalogInterface.ControlHandle(
                    group_id='',
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

    def _get_all_controls_in_group(self, group: cat.Group, recurse: bool) -> List[cat.Control]:
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

    def get_group_ids(self) -> List[str]:
        """Get all the group id's as a string."""
        return list(filter(lambda id: id, list({control.group_id for control in self._control_dict.values()})))

    def get_all_groups_from_catalog(self) -> Iterator[cat.Group]:
        """Retrieve all groups in the catalog."""
        if self._catalog.groups:
            for my_group in self._catalog.groups:
                for res in CatalogInterface._get_groups_from_group(my_group):
                    yield res

    def get_statement_label_if_exists(self, control_id: str,
                                      statement_id: str) -> Tuple[Optional[str], Optional[common.Part]]:
        """Get statement label if given."""

        def does_part_exists(part: common.Part) -> bool:
            does_match = False
            if part.name and part.name in {'statement', 'item'} and part.id == statement_id:
                does_match = True
            return does_match

        control = self.get_control(control_id)
        if not control:
            return '', None
        label = None
        found_part = None
        if control.parts:
            for part in as_list(control.parts):
                # Performance OSCAL assumption, ids are nested so recurse only if prefix
                if part.id and statement_id.startswith(part.id):
                    part = self.find_part_with_condition(part, does_part_exists)
                    if part:
                        label = self.get_label(part)
                        found_part = part
                        break

        return label, found_part

    def find_part_with_condition(self, part: common.Part, condition: Callable) -> Optional[common.Part]:
        """Traverse part and find subpart that satisfies given condition."""
        if condition(part):
            # Part that satisfies the condition is found.
            return part
        else:
            if part.parts:
                for subpart in part.parts:
                    found_part = self.find_part_with_condition(subpart, condition)
                    if found_part:
                        return found_part

        return None

    @staticmethod
    def _get_groups_from_group(group: cat.Group) -> Iterator[cat.Group]:
        yield group
        if group.groups:
            for new_group in group.groups:
                for res in CatalogInterface._get_groups_from_group(new_group):
                    yield res

    @staticmethod
    def get_label(object_with_props: BaseModel) -> str:
        """Get the label from an object with properties (such as a control)."""
        label = ''
        if object_with_props.props:
            for prop in as_list(object_with_props.props):
                if prop.name == 'label':
                    label = prop.value
                    break
        return label

    def get_group_info_by_control(self, control_id: str) -> Tuple[str, str, str]:
        """Get the group_id, title, class for this control from the dict."""
        return (
            self._control_dict[control_id].group_id,
            self._control_dict[control_id].group_title,
            self._control_dict[control_id].group_class
        )

    def get_control_path(self, control_id: str) -> List[str]:
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

    @staticmethod
    def get_full_profile_param_dict(profile: prof.Profile) -> Dict[str, str]:
        """Get the full mapping of param_id to modified value for this profile."""
        set_param_dict: Dict[str, str] = {}
        for set_param in as_list(profile.modify.set_parameters):
            value_str = ControlIOReader.param_values_as_string(set_param)
            set_param_dict[set_param.param_id] = value_str
        return set_param_dict

    @staticmethod
    def get_profile_param_dict(control: cat.Control, profile_param_dict: Dict[str, str]) -> Dict[str, str]:
        """Get the list of params for this control and any set by the profile."""
        param_dict = ControlIOReader.get_control_param_dict(control, True)
        for key in param_dict.keys():
            if key in profile_param_dict:
                param_dict[key] = profile_param_dict[key]
        return param_dict

    def write_catalog_as_markdown(
        self,
        md_path: pathlib.Path,
        yaml_header: dict,
        sections: Optional[Dict[str, str]],
        responses: bool,
        additional_content: bool = False,
        profile: Optional[prof.Profile] = None,
        preserve_header_values: bool = False,
        set_parameters: bool = False
    ) -> None:
        """Write out the catalog controls from dict as markdown to the given directory."""
        writer = ControlIOWriter()

        # create the directory in which to write the control markdown files
        md_path.mkdir(exist_ok=True, parents=True)
        catalog_interface = CatalogInterface(self._catalog)
        if set_parameters:
            full_profile_param_dict = CatalogInterface.get_full_profile_param_dict(profile)
        # write out the controls
        for control in catalog_interface.get_all_controls_from_catalog(True):
            new_header = copy.deepcopy(yaml_header)
            if set_parameters:
                param_dict = CatalogInterface.get_profile_param_dict(control, full_profile_param_dict)
                if param_dict:
                    new_header[const.SET_PARAMS_TAG] = param_dict
            group_id, group_title, _ = catalog_interface.get_group_info_by_control(control.id)
            # this works also for the catalog controls with group_id=''
            group_dir = md_path / group_id
            if not group_dir.exists():
                group_dir.mkdir(parents=True, exist_ok=True)
            writer.write_control(
                group_dir,
                control,
                group_title,
                new_header,
                sections,
                additional_content,
                responses,
                profile,
                preserve_header_values
            )

    @staticmethod
    def _get_group_ids(md_path: pathlib.Path) -> List[str]:
        """Get the list of group ids from the directories in the markdown path."""
        # need to start with empty list to find controls not in group
        group_ids: List[str] = ['']

        for gdir in md_path.glob('*/'):
            if gdir.is_dir():
                group_ids.append(str(gdir.stem))
        return sorted(group_ids)

    @staticmethod
    def _get_control_paths(group_path: pathlib.Path) -> List[pathlib.Path]:
        """Need to parse control id and sort based on internals."""
        control_paths = list(group_path.glob('*.md'))
        control_map = {}
        for control_path in control_paths:
            control_id = control_path.stem
            # set the label to be the control_id at start
            # if the id doesn't fit the expected pattern it will just be sorted alphabetically based on the id string
            label = control_id
            digits = 0
            frac = 0
            extra = ''
            # now try to break off ac as label from ac-11.21xy
            if '-' in control_id:
                dash_split = control_id.split('-', 1)
                label = dash_split[0]
                remainder = dash_split[1]
                # now try to extract 11 and 21
                matches = re.search(r'([0-9]+)\.([0-9]+)(.*)', remainder)
                if matches:
                    tup = matches.groups()
                    digits = int(tup[0])
                    frac = int(tup[1])
                    extra = tup[2]
                else:
                    # look for 11 with no decimal
                    # this is needed so ac-2 comes before ac-11
                    matches = re.search(r'([0-9]+)(.*)', remainder)
                    if matches:
                        tup = matches.groups()
                        digits = int(tup[0])
                        # extra will now contain xy
                        extra = tup[1]
                    else:
                        extra = remainder
            # create the 4 keys used for sorting
            control_map[control_path] = (label, digits, frac, extra)

        return sorted(control_paths, key=lambda x: control_map[x])

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
            group_dir = md_path / group_id
            control_list = []
            for control_path in CatalogInterface._get_control_paths(group_dir):
                control = ControlIOReader.read_control(control_path)
                control_list.append(control)
            if group_id:
                new_group = cat.Group(id=group_id, title='')
                new_group.controls = control_list
                groups.append(new_group)
            else:
                self._catalog.controls = control_list
        self._catalog.groups = groups if groups else None
        return self._catalog

    @staticmethod
    def read_catalog_imp_reqs(md_path: pathlib.Path,
                              avail_comps: Dict[str, ossp.SystemComponent]) -> List[ossp.ImplementedRequirement]:
        """Read the full set of control implemented requirements from markdown.

        Args:
            md_path: Path to the markdown control files, with directories for each group
            avail_comps: Dict mapping component names to known components

        Returns:
            List of implemented requirements gathered from each control

        Notes:
            As the controls are read into the catalog the needed components are added if not already available.
            avail_comps provides the mapping of component name to the actual component.
        """
        group_ids = CatalogInterface._get_group_ids(md_path)

        imp_reqs: List[ossp.ImplementedRequirement] = []
        for group_id in group_ids:
            group_path = md_path / group_id
            for control_file in CatalogInterface._get_control_paths(group_path):
                imp_reqs.append(ControlIOReader.read_implemented_requirement(control_file, avail_comps))
        return imp_reqs

    @staticmethod
    def read_additional_content(md_path: pathlib.Path) -> Tuple[List[prof.Alter], Dict[str, str]]:
        """Read all markdown controls and return list of alters."""
        group_ids = CatalogInterface._get_group_ids(md_path)

        new_alters: List[prof.Alter] = []
        param_dict: Dict[str, str] = {}
        for group_id in group_ids:
            group_path = md_path / group_id
            for control_file in group_path.glob('*.md'):
                control_alters, control_param_dict = ControlIOReader.read_new_alters_and_params(control_file)
                new_alters.extend(control_alters)
                param_dict.update(control_param_dict)
        return new_alters, param_dict

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

    def get_sections(self) -> List[str]:
        """Get the available sections by a full index of all controls."""
        sections: List[str] = []

        for control in self._control_dict.values():
            if not control.control.parts:
                continue
            for part in control.control.parts:
                if part.name not in sections:
                    sections.append(part.name)
        return sections
