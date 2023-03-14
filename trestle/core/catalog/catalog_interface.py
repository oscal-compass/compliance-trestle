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
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple

import trestle.common.const as const
import trestle.oscal.catalog as cat
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_dict, as_filtered_list, as_list, deep_append, deep_get, deep_set, deep_update, delete_item_from_list, get_item_from_list, none_if_empty, set_or_pop  # noqa E501
from trestle.common.model_utils import ModelUtils
from trestle.core.control_context import ControlContext
from trestle.core.control_interface import CompDict, ComponentImpInfo, ControlInterface
from trestle.oscal import common
from trestle.oscal import component as comp
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

    @dataclass
    class ControlHandle:
        """Convenience class for handling controls as members of a group.

        group_id: id of parent group or '' if not in a group
        group_title: title of the group
        group_class: class of the group
        path: path of parent groups leading to this control - without the final control_id, or [''] if in cat list
        important to remember that controls may not be in a group and are directly attached to cat
        control: the control itself
        """

        group_id: str
        group_title: Optional[str]
        group_class: Optional[str]
        group_path: List[str]
        control_path: List[str]
        control: cat.Control

    def __init__(self, catalog: Optional[cat.Catalog] = None) -> None:
        """Initialize the interface with the catalog."""
        self._catalog = catalog
        self._param_control_map: Dict[str, str] = {}
        self._generate_group_index: int = 0
        self._control_dict = self._create_control_dict() if catalog else None
        self.loose_param_dict: Dict[str, common.Parameter] = {param.id: param
                                                              for param in as_list(catalog.params)} if catalog else {}
        # map control id to CompDict
        self._control_comp_dicts: Dict[str, CompDict] = {}
        # map control id to dict containing set parameters by component
        self._control_comp_set_params: Dict[str, Dict[str, comp.SetParameter]] = {}

    def add_comp_info(self, control_id: str, comp_name: str, label: str, comp_info: ComponentImpInfo) -> None:
        """Add comp_info for a control."""
        deep_set(self._control_comp_dicts, [control_id, comp_name, label], comp_info)

    def get_comp_info(self, control_id: str) -> CompDict:
        """Get comp_dict for this control."""
        return self._control_comp_dicts.get(control_id, {})

    def clear_comp_dicts(self) -> None:
        """Clear the control component dicts."""
        self._control_comp_dicts = {}

    def add_comp_set_param(self, control_id: str, comp_name: str, set_param: comp.SetParameter) -> None:
        """Add component setparam for control with overwrite."""
        deep_append(self._control_comp_set_params, [control_id, comp_name], set_param)

    def get_control_comp_set_params(self, control_id: str) -> Dict[str, List[comp.SetParameter]]:
        """Get dict of setparams list per component."""
        return self._control_comp_set_params.get(control_id, {})

    def clear_set_params(self) -> None:
        """Clear the control set params."""
        self._control_comp_set_params = {}

    def _generate_group_id(self, group: cat.Group) -> str:
        """Generate sequential group ids."""
        group_id = f'trestle_group_{self._generate_group_index:04d}'
        self._generate_group_index += 1
        logger.warning(f'Group titled "{group.title}" has no id and has been assigned id: {group_id}')
        return group_id

    def _add_params_to_map(self, control: cat.Control) -> None:
        # this does not need to recurse because it is called for each control in the catalog
        for param in as_list(control.params):
            if param.id in self._param_control_map:
                logger.warning(
                    f'Duplicate param id {param.id} in control {control.id} and {self._param_control_map[param.id]}.'
                )
            self._param_control_map[param.id] = control.id

    def _add_sub_controls(
        self, control_handle: ControlHandle, control_dict: Dict[str, ControlHandle], path: List[str]
    ) -> None:
        """
        Get all controls contained in this control and add it to the growing control dict.

        Add all its sub-controls to the dict recursively.
        The path does not change because only groups are in the path, and controls cannot contain groups.
        """
        if control_handle.control.controls:
            group_id = control_handle.group_id
            group_title = control_handle.group_title
            group_class = control_handle.group_class
            group_path = control_handle.group_path
            control_path = path[:]
            control_path.append(control_handle.control.id)
            for sub_control in control_handle.control.controls:
                control_handle = CatalogInterface.ControlHandle(
                    group_id=group_id,
                    group_title=group_title,
                    group_class=group_class,
                    group_path=group_path,
                    control_path=control_path,
                    control=sub_control
                )
                control_dict[sub_control.id] = control_handle
                self._add_sub_controls(control_handle, control_dict, control_path)

    def _add_group_controls(self, group: cat.Group, control_dict: Dict[str, ControlHandle], path: List[str]) -> None:
        """Add all controls in the group recursively, including sub groups and sub controls."""
        group.id = self._generate_group_id(group) if group.id is None else group.id
        if group.controls is not None:
            group_path = path[:]
            if not group_path or group_path[-1] != group.id:
                group_path.append(group.id)
            for control in group.controls:
                control_handle = CatalogInterface.ControlHandle(
                    group_id=group.id,
                    group_title=group.title,
                    group_class=group.class_,
                    control=control,
                    group_path=group_path,
                    control_path=group_path
                )
                control_dict[control.id] = control_handle
                self._add_sub_controls(control_handle, control_dict, group_path)
        if group.groups is not None:
            group_path = path[:]
            group_path.append(group.id)
            for sub_group in group.groups:
                new_path = group_path[:]
                sub_group.id = self._generate_group_id(sub_group) if sub_group.id is None else sub_group.id
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
                control_handle = CatalogInterface.ControlHandle(
                    group_id='',
                    group_title='',
                    group_class=const.MODEL_TYPE_CATALOG,
                    control=control,
                    group_path=group_path,
                    control_path=group_path
                )
                control_dict[control.id] = control_handle
                self._add_sub_controls(control_handle, control_dict, group_path)
        for handle in control_dict.values():
            self._add_params_to_map(handle.control)
        return control_dict

    @staticmethod
    def _get_all_controls_in_list(controls: List[cat.Control], recurse: bool) -> List[cat.Control]:
        """Get all controls in a list with optional recursion for sub controls."""
        new_list: List[cat.Control] = []
        for control in controls:
            new_list.append(control)
            if recurse and control.controls:
                new_list.extend(CatalogInterface._get_all_controls_in_list(control.controls, recurse))
        return new_list

    @staticmethod
    def _get_all_controls_in_group(group: cat.Group, recurse: bool) -> List[cat.Control]:
        """
        Create a list of all controls in this group.

        recurse specifies to recurse within controls, but groups are always recursed
        """
        controls: List[cat.Control] = []
        if group.controls:
            controls.extend(CatalogInterface._get_all_controls_in_list(group.controls, recurse))
        for sub_group in as_list(group.groups):
            controls.extend(CatalogInterface._get_all_controls_in_group(sub_group, recurse))
        return controls

    def get_sorted_controls_in_group(self, group_id: str) -> List[cat.Control]:
        """Get the list of controls in a group sorted by the control sort-id."""
        controls: List[cat.Control] = []
        for control in self.get_all_controls_from_dict():
            grp_id, _, _ = self.get_group_info_by_control(control.id)
            if grp_id == group_id:
                controls.append(control)
        return sorted(controls, key=lambda control: ControlInterface.get_sort_id(control))

    def get_dependent_control_ids(self, control_id: str) -> List[str]:
        """Find all child ids of this control from the dict with recursion."""
        children: List[str] = []
        control = self.get_control(control_id)
        if control:
            new_controls = self._get_all_controls_in_list(as_list(control.controls), True)
            children.extend([con.id for con in new_controls])
        return children

    def get_control_ids(self) -> List[str]:
        """Get all control ids from the control dict."""
        return self._control_dict.keys()

    def get_control(self, control_id: str) -> Optional[cat.Control]:
        """Get control from the control dict with this id."""
        return None if control_id not in self._control_dict else self._control_dict[control_id].control

    @staticmethod
    def get_control_ids_from_catalog(catalog: cat.Catalog) -> List[str]:
        """
        Get all control ids from a catalog.

        This is intended to provide a quick list of all controls in a catalog without the expense of building the
        control dict.  So, if repeated queries are made into a catalog, it is worth instantiating a CatalogInterface
        and associated control dict.  Otherwise just use this to get a list of all controls.

        This function is needed within the CatalogInterface in order to determine if new controls have been added
        to the dict and need to be inserted in the actual catalog during update.
        """
        controls = CatalogInterface._get_all_controls_in_list(as_list(catalog.controls), True)
        id_list = [control.id for control in controls]
        for group in as_list(catalog.groups):
            controls = CatalogInterface._get_all_controls_in_group(group, True)
            id_list.extend([control.id for control in as_list(controls)])
        return id_list

    def get_control_by_param_id(self, param_id: str) -> Optional[cat.Control]:
        """Get control from catalog that has this param id using the dict."""
        if param_id in self._param_control_map:
            return self.get_control(self._param_control_map[param_id])
        return None

    def get_control_id_and_status(self, control_name: str) -> Tuple[str, str]:
        """
        Get the control id and status using the control name.

        Returns empty string if status not found.
        """
        for control in self.get_all_controls_from_dict():
            if ControlInterface.get_label(control).strip().lower() == control_name.strip().lower():
                status = ControlInterface.get_prop(control, 'status')
                return control.id, status
        return '', ''

    def get_catalog_title(self) -> str:
        """Get the title of the catalog."""
        return self._catalog.metadata.title

    def get_statement_part_id_map(self, label_as_key: bool) -> Dict[str, Dict[str, str]]:
        """Create mapping of label to part_id for top level parts in statement of all controls."""
        id_map = {}
        for control in self.get_all_controls_from_catalog(True):
            statement_part = get_item_from_list(control.parts, const.STATEMENT, lambda p: p.name)
            if statement_part:
                id_dict: Dict[str, str] = {}
                for sub_part in as_list(statement_part.parts):
                    label = ControlInterface.get_label(sub_part)
                    if label_as_key:
                        id_dict[label] = sub_part.id
                    else:
                        id_dict[sub_part.id] = label
                if id_dict:
                    id_map[control.id] = id_dict
        return id_map

    @staticmethod
    def _get_statement_sub_parts(part: common.Part, indent: int) -> List[Dict[str, str]]:
        items = []
        # this may be '' if no label
        label = ControlInterface.get_label(part)
        prose = '' if part.prose is None else part.prose
        items.append({'indent': indent, 'label': label, 'prose': prose})
        for prt in as_filtered_list(part.parts, lambda p: p.name == 'item'):
            items.extend(CatalogInterface._get_statement_sub_parts(prt, indent + 1))
        return items

    def get_statement_parts(self, control_id: str) -> List[Dict[str, str]]:
        """Get list of statement parts as dicts with indentation, label and prose."""
        items = []
        control = self.get_control(control_id)

        # control may have no statement or parts
        # but if statement present it is first part
        if control is None:
            logger.warning(f'No control found for id {control_id}')
        elif control.parts:
            part = control.parts[0]
            if part.name == 'statement':
                items.extend(CatalogInterface._get_statement_sub_parts(part, 0))
            else:
                logger.warning(f'Control {control_id} has parts but first part name is {part.name} - not statement')
        return items

    def get_control_part_prose(self, control_id: str, part_name: str) -> str:
        """
        Get the prose for a named part in the control.

        Args:
            control_id: id of the control
            part_name: name of the part

        Returns:
            Single string concatenating prose from all parts and sub-parts in control with that name.
        """
        control = self.get_control(control_id)
        return ControlInterface.get_part_prose(control, part_name)

    def get_all_controls_from_catalog(self, recurse: bool) -> Iterator[cat.Control]:
        """
        Yield all controls from the actual catalog by group including optional sub controls.

        Args:
            recurse: Whether to recurse within controls, but groups are always recursed

        Returns:
            iterator of the controls in the catalog

        Notes:
            This follows the actual structure of the catalog and groups
        """
        if self._catalog.groups:
            for group in self._catalog.groups:
                controls = self._get_all_controls_in_group(group, recurse)
                for control in controls:
                    yield control
        if self._catalog.controls:
            cat_controls = self._get_all_controls_in_list(self._catalog.controls, recurse)
            for control in cat_controls:
                yield control

    def get_all_controls_from_dict(self) -> List[cat.Control]:
        """Yield individual controls from the dict."""
        return [handle.control for handle in self._control_dict.values()]

    def get_count_of_controls_in_dict(self) -> int:
        """Find number of controls in the dict."""
        return len(self._control_dict.keys())

    def get_count_of_controls_in_catalog(self, recurse: bool) -> int:
        """Get count of controls from the actual catalog including optional sub controls."""
        return len(list(self.get_all_controls_from_catalog(recurse)))

    def get_group_ids(self) -> List[str]:
        """Get all the group id's as a list of sorted strings."""
        return sorted(filter(lambda id: id, list({control.group_id for control in self._control_dict.values()})))

    def get_all_groups_from_catalog(self) -> List[cat.Group]:
        """
        Retrieve all groups in the catalog sorted by group_id.

        This ignores controls that are direct children of the catalog.
        """
        groups: List[cat.Group] = []
        if self._catalog.groups:
            for my_group in self._catalog.groups:
                for res in CatalogInterface._get_groups_from_group(my_group):
                    groups.append(res)
        return sorted(groups, key=lambda group: group.id)

    def get_statement_label_if_exists(self, control_id: str,
                                      statement_id: str) -> Tuple[Optional[str], Optional[common.Part]]:
        """Get statement label if available."""

        def does_part_exists(part: common.Part) -> bool:
            does_match = False
            if part.name and part.name in {const.STATEMENT, 'item'} and part.id == statement_id:
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
                        label = ControlInterface.get_label(part)
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

    def delete_withdrawn_controls(self) -> None:
        """Delete all withdrawn controls from the catalog."""
        delete_list = []
        for control in self.get_all_controls_from_dict():
            if ControlInterface.is_withdrawn(control):
                delete_list.append(control.id)
        for id_ in delete_list:
            self.delete_control(id_)

    @staticmethod
    def _get_groups_from_group(group: cat.Group) -> Iterator[cat.Group]:
        yield group
        if group.groups:
            for new_group in group.groups:
                for res in CatalogInterface._get_groups_from_group(new_group):
                    yield res

    def get_group_info_by_control(self, control_id: str) -> Tuple[str, str, str]:
        """Get the group_id, title, class for this control from the dict."""
        return (
            self._control_dict[control_id].group_id,
            self._control_dict[control_id].group_title,
            self._control_dict[control_id].group_class
        )

    def get_control_path(self, control_id: str) -> List[str]:
        """Return the path into the markdown directory for this control based only on the groups."""
        return self._control_dict[control_id].group_path

    def get_control_file_path(self, md_root: pathlib.Path, control_id: str) -> Optional[pathlib.Path]:
        """Get the path to the control from the given root."""
        if control_id not in self._control_dict:
            return None
        path = md_root
        for item in self.get_control_path(control_id):
            path = path / item
        return path / f'{control_id}.md'

    def get_full_control_path(self, control_id: str) -> List[str]:
        """Return the path to the control including groups and sub-controls."""
        return self._control_dict[control_id].control_path

    def replace_control(self, control: cat.Control) -> None:
        """
        Replace the control in the control_dict.

        This only replaces the parent control and not its children.
        """
        self._control_dict[control.id].control = control

    def delete_control(self, control_id: str) -> None:
        """
        Delete the control from the control_dict based on id.

        Delete all its dependent children also.
        """
        control = self.get_control(control_id)
        if control:
            for sub_control_id in self.get_dependent_control_ids(control.id):
                self._control_dict.pop(sub_control_id, None)
            self._control_dict.pop(control_id, None)

    def get_catalog(self, update=True) -> cat.Catalog:
        """Safe method to get catalog after forced update from catalog dict."""
        if update:
            self.update_catalog_controls()
        return self._catalog

    def _update_all_controls_in_list(self, controls: List[cat.Control]) -> List[cat.Control]:
        """
        Given a list of controls, create fresh list pulled from the control dict.

        Args:
            controls: a list of controls in the original catalog

        Returns:
            The new list of updated controls, possibly with some missing if they have been removed from the dict.
            Children are inserted as needed into parent controls.
        """
        new_list: List[cat.Control] = []
        for control in controls:
            # first update the control itself by getting it from the dict
            new_control = self.get_control(control.id)
            if new_control:
                # this overrides any sub controls in the control itself
                # any added sub-controls should add to the skipped list
                new_control.controls = self._update_all_controls_in_list(as_list(control.controls))
                new_control.controls = none_if_empty(new_control.controls)
                new_list.append(new_control)
        return new_list

    def _update_all_controls_in_group(self, group: cat.Group) -> None:
        """Given a group of controls, create fresh version pulled from the control dict."""
        group.controls = self._update_all_controls_in_list(as_list(group.controls))
        group.controls = none_if_empty(group.controls)
        new_groups: List[cat.Group] = []
        for sub_group in as_list(group.groups):
            self._update_all_controls_in_group(sub_group)
            new_groups.append(sub_group)
        group.groups = none_if_empty(new_groups)

    def _insert_control_in_catalog(self, control_handle: ControlHandle) -> None:
        """Insert the control into the catalog based on its path."""
        path = control_handle.group_path
        node = self._catalog
        if path[0] != '':
            for group_id in path:
                found_group = None
                for group in as_list(node.groups):
                    if group.id == group_id:
                        found_group = group
                        break
                if found_group:
                    node = found_group
                else:
                    raise TrestleError(f'No controls found in catalog for group {group.id}')
            node.title = control_handle.group_title
            node.class_ = control_handle.group_class
        node.controls = delete_item_from_list(
            as_list(node.controls), control_handle.control.id, lambda control: control.id
        )
        node.controls.append(control_handle.control)
        node.controls = none_if_empty(sorted(node.controls, key=lambda control: ControlInterface.get_sort_id(control)))

    def update_catalog_controls(self) -> None:
        """
        Update the actual catalog by pulling fresh controls from the dict.

        During assembly, controls may be added, but not children of controls.
        New groups may not be added.
        A control containing controls cannot be added.  Controls containing controls are only available if
        the parent catalog was loaded from json.
        """
        # first go through the catalog and pull existing controls from the dict
        for group in as_list(self._catalog.groups):
            self._update_all_controls_in_group(group)

        new_list = []
        for control in as_list(self._catalog.controls):
            new_control = self.get_control(control.id)
            new_control.controls = self._update_all_controls_in_list(as_list(control.controls))
            new_control.controls = none_if_empty(new_control.controls)
            new_list.append(new_control)
        self._catalog.controls = none_if_empty(new_list)

        # now add any new controls that are discovered in the dict
        ids_in_catalog = CatalogInterface.get_control_ids_from_catalog(self._catalog)
        for control_handle in self._control_dict.values():
            if control_handle.control.id not in ids_in_catalog:
                self._insert_control_in_catalog(control_handle)

        self._catalog.params = none_if_empty(list(self.loose_param_dict.values()))

    def _find_string_in_part(self, control_id: str, part: common.Part, seek_str: str) -> List[str]:
        hits: List[str] = []
        if part.prose and part.prose.find(seek_str) >= 0:
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
    def _get_full_profile_param_dict(profile: Optional[prof.Profile]) -> Dict[str, common.Parameter]:
        """Get the full mapping of param_id to modified value for this profiles set_params."""
        set_param_dict: Dict[str, common.Parameter] = {}
        if profile and profile.modify:
            for set_param in as_list(profile.modify.set_parameters):
                param = ControlInterface.setparam_to_param(set_param.param_id, set_param)
                set_param_dict[set_param.param_id] = param
        return set_param_dict

    @staticmethod
    def _get_profile_param_dict(
        control: cat.Control, profile_param_dict: Dict[str, common.Parameter], values_only: bool
    ) -> Dict[str, common.Parameter]:
        """
        Get the dict of params for this control including possible overrides made by the profile modifications.

        Args:
            control: The control being queried
            profile_param_dict: The full dict of params and modified values made by the profile

        Returns:
            mapping of param ids to their final parameter states after possible modify by the profile setparameters
        """
        # get the mapping of param_id's to params for this control, excluding those with no value set
        param_dict = ControlInterface.get_control_param_dict(control, values_only)
        for key in param_dict.keys():
            if key in profile_param_dict:
                param_dict[key] = profile_param_dict[key]
        return param_dict

    def _get_full_param_dict(self) -> Dict[str, common.Parameter]:
        param_dict: Dict[str, common.Parameter] = {}
        # build the full mapping of params to values from the catalog interface
        for control in self.get_all_controls_from_dict():
            param_dict.update(ControlInterface.get_control_param_dict(control, False))
        return param_dict

    def _change_prose_with_param_values(
        self,
        param_format,
        param_rep,
        show_value_warnings: bool,
        value_assigned_prefix: Optional[str] = None,
        value_not_assigned_prefix: Optional[str] = None
    ) -> None:
        """Go through all controls and change prose based on param values."""
        param_dict = self._get_full_param_dict()
        # insert param values into prose of all controls
        for control in self.get_all_controls_from_dict():
            ControlInterface.replace_control_prose(
                control,
                param_dict,
                param_format,
                param_rep,
                show_value_warnings,
                value_assigned_prefix,
                value_not_assigned_prefix
            )

    @staticmethod
    def _get_display_name_and_ns(param: common.Parameter) -> Tuple[Optional[str], Optional[str]]:
        for prop in as_list(param.props):
            if prop.name == const.DISPLAY_NAME:
                ns = str(prop.ns) if prop.ns else None
                return prop.value, ns
        return None, None

    @staticmethod
    def _prune_controls(md_path: pathlib.Path, written_controls: Set[str]) -> List[str]:
        """Search directory and remove any controls that were not written out."""
        deleted_controls = []
        for control_file in md_path.rglob('*.md'):
            if control_file.stem not in written_controls:
                logger.debug(
                    f'Existing control markdown {control_file} deleted since it was not written out during generate'
                )  # noqa E501
                control_file.unlink()
                deleted_controls.append(control_file.stem)
        return sorted(deleted_controls)

    def _extend_rules_param_list(
        self, control_id: str, header: Dict[str, Any], param_id_rule_name_map: Dict[str, str]
    ) -> None:
        """Go through all set_params and put in rules param list if name matches."""
        control_comp_set_params = {}
        rules_set_params = {}
        all_set_params = self.get_control_comp_set_params(control_id)
        for comp_name, param_list in all_set_params.items():
            for param in param_list:
                param_vals = none_if_empty(as_list(param.values))
                rule_name = deep_get(param_id_rule_name_map, [comp_name, param.param_id], None)
                if rule_name:
                    param_dict = {'name': param.param_id}
                    if param_vals:
                        param_dict['values'] = param_vals
                    deep_append(rules_set_params, [comp_name], param_dict)
        set_or_pop(header, const.COMP_DEF_RULES_PARAM_VALS_TAG, rules_set_params)
        set_or_pop(header, const.SET_PARAMS_TAG, control_comp_set_params)

    def _get_control_memory_info(self, control_id: str, context: ControlContext) -> Tuple[Dict[str, Any], CompDict]:
        """Build the rule info for the control into the header."""
        header = {}
        rule_names_list: List[str] = []
        comp_dict = self.get_comp_info(control_id)
        # find the rule names that are needed by the control
        for _, value in comp_dict.items():
            for comp_info in value.values():
                rule_names_list.extend(as_list(comp_info.rules))
        if rule_names_list:
            header_rules_dict = {}
            rule_ids = {}
            param_id_rule_name_map = {}
            rule_id_rule_name_map = {}
            # only include rules needed by control in the header
            for comp_name, rules_dict in context.rules_dict.items():
                for rule_id, rule_dict in rules_dict.items():
                    if rule_dict['name'] in rule_names_list:
                        deep_append(rule_ids, [comp_name], rule_id)
                        deep_append(header_rules_dict, [comp_name], rule_dict)
                        deep_set(rule_id_rule_name_map, [comp_name, rule_id], rule_dict['name'])
            set_or_pop(header, const.COMP_DEF_RULES_TAG, header_rules_dict)
            rules_params = {}
            rules_param_names = []
            for comp_name, rules_params_dict in as_dict(context.rules_params_dict).items():
                for rule_id, rules_param in rules_params_dict.items():
                    if rule_id in rule_ids.get(comp_name, []):
                        param_name = rules_param['name']
                        rules_param_names.append(param_name)
                        rules_param[const.HEADER_RULE_ID] = rule_id_rule_name_map[comp_name].get(rule_id, None)
                        deep_append(rules_params, [comp_name], rules_param)
                        deep_set(
                            param_id_rule_name_map, [comp_name, rules_param['name']],
                            rule_id_rule_name_map[comp_name][rule_id]
                        )
            set_or_pop(header, const.RULES_PARAMS_TAG, rules_params)

            self._extend_rules_param_list(control_id, header, param_id_rule_name_map)

        return header, comp_dict

    @staticmethod
    def _get_group_ids_and_dirs(md_path: pathlib.Path) -> Dict[str, pathlib.Path]:
        """
        Create a sorted map of group id to group dir that is ordered by group id.

        This includes '' as the root group id.
        """
        # manually insert the top dir as group ''
        id_map: Dict[str, pathlib.Path] = {'': md_path}
        for gdir in md_path.rglob('*'):
            if gdir.is_dir():
                dir_name = gdir.parts[-1]
                id_map[dir_name] = gdir
        # rebuild the dict by inserting items in manner sorted by key
        sorted_id_map: Dict[str, pathlib.Path] = {}
        for key in sorted(id_map):
            sorted_id_map[key] = id_map[key]
        return sorted_id_map

    def get_sections(self) -> List[str]:
        """Get the available sections by a full index of all controls."""
        return list(
            {
                part.name
                for control_handle in self._control_dict.values()
                for part in as_list(control_handle.control.parts)
                if part.name != const.STATEMENT
            }
        )

    def _find_control_in_group(self, group_id: str) -> Tuple[str, ControlHandle]:
        """
        Find a representative control for this group and its control handle.

        This is a simple way to get group info (title etc.) given only group id.
        It is not intended for high performance loops.  Use only as needed.
        """
        for control_id, control_handle in self._control_dict.items():
            if control_handle.group_id == group_id:
                return control_id, control_handle
        raise TrestleError(f'No controls found for group {group_id}')

    def _add_control_imp_comp_info(
        self, context: ControlContext, part_id_map: Dict[str, Dict[str, str]], comp_rules_props: List[common.Property]
    ) -> None:
        """Add component info to the impreqs of the control implementation based on applied rules."""
        control_imp_rules_dict, control_imp_rules_params_dict, ci_rules_props = ControlInterface.get_rules_and_params_dict_from_item(context.control_implementation)  # noqa E501
        context.rules_dict[context.comp_name].update(control_imp_rules_dict)
        comp_rules_params_dict = context.rules_params_dict.get(context.comp_name, {})
        comp_rules_params_dict.update(control_imp_rules_params_dict)
        context.rules_params_dict[context.comp_name] = comp_rules_params_dict
        ci_set_params = ControlInterface.get_set_params_from_item(context.control_implementation)
        catalog_control_ids = self.get_control_ids()
        for imp_req in as_list(context.control_implementation.implemented_requirements):
            if imp_req.control_id not in catalog_control_ids:
                logger.warning(
                    f'Component {context.component.title} references control {imp_req.control_id} not in profile.'
                )
            control_part_id_map = part_id_map.get(imp_req.control_id, {})
            # find if any rules apply to this control, including in statements
            control_rules, statement_rules, ir_props = ControlInterface.get_rule_list_for_imp_req(imp_req)
            rule_props = comp_rules_props[:]
            rule_props.extend(ci_rules_props)
            rule_props.extend(ir_props)
            rule_props = ControlInterface.clean_props(rule_props, remove_imp_status=False)
            if control_rules:
                status = ControlInterface.get_status_from_props(imp_req)
                final_props = ControlInterface.cull_props_by_rules(rule_props, control_rules)
                comp_info = ComponentImpInfo(imp_req.description, control_rules, final_props, status)
                self.add_comp_info(imp_req.control_id, context.comp_name, '', comp_info)
            set_params = copy.deepcopy(ci_set_params)
            set_params.update(ControlInterface.get_set_params_from_item(imp_req))
            for set_param in set_params.values():
                # add to control_comp_set_params dict
                self.add_comp_set_param(imp_req.control_id, context.comp_name, set_param)
            for statement in as_list(imp_req.statements):
                rule_list, stat_props = ControlInterface.get_rule_list_for_item(statement)
                if rule_list:
                    status = ControlInterface.get_status_from_props(statement)
                    if statement.statement_id not in control_part_id_map:
                        label = statement.statement_id
                        logger.warning(
                            f'No statement label found for statement id {label}.  Defaulting to {label}.'  # noqa E501
                        )
                    else:
                        label = control_part_id_map[statement.statement_id]
                    all_props = rule_props[:]
                    all_props.extend(stat_props)
                    final_props = ControlInterface.cull_props_by_rules(all_props, rule_list)
                    comp_info = ComponentImpInfo(statement.description, rule_list, final_props, status)
                    self.add_comp_info(imp_req.control_id, context.comp_name, label, comp_info)

    def generate_control_rule_info(self, part_id_map: Dict[str, Dict[str, str]], context: ControlContext) -> None:
        """
        Generate rule info for controls directly from the components.

        Args:
            part_id_map: Mapping of label to part in the control
            context: Control context for the current operation

        Returns:
            Returns nothing but places the rules_dict and rules_params_dict in the context for each component
        """
        context.rules_dict = {}
        context.rules_params_dict = {}
        for comp_def_name in context.comp_def_name_list:
            context.comp_def, _ = ModelUtils.load_model_for_class(
                context.trestle_root,
                comp_def_name,
                comp.ComponentDefinition
            )
            for component in as_list(context.comp_def.components):
                context.component = component
                context.comp_name = component.title
                # get top level rule info applying to all controls from the component props
                comp_rules_dict, comp_rules_params_dict, comp_rules_props = ControlInterface.get_rules_and_params_dict_from_item(component)  # noqa E501
                context.rules_dict[context.comp_name] = comp_rules_dict
                deep_update(context.rules_params_dict, [context.comp_name], comp_rules_params_dict)
                for control_imp in as_list(component.control_implementations):
                    context.control_implementation = control_imp
                    self._add_control_imp_comp_info(context, part_id_map, comp_rules_props)
                # add the rule_id to the param_dict
                for param_comp_name, rule_param_dict in context.rules_params_dict.items():
                    for rule_tag, param_dict in rule_param_dict.items():
                        rule_dict = deep_get(context.rules_dict, [param_comp_name, rule_tag], {})
                        param_dict[const.HEADER_RULE_ID] = rule_dict.get(const.NAME, 'unknown_rule')
