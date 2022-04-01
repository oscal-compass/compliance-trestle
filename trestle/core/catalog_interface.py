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
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

import trestle.common.const as const
import trestle.core.generators as gens
import trestle.oscal.catalog as cat
import trestle.oscal.ssp as ossp
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_list
from trestle.common.model_utils import ModelUtils
from trestle.core.control_io import ControlIOReader, ControlIOWriter
from trestle.core.trestle_base_model import TrestleBaseModel
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
        path: path of parent groups leading to this control - without the final control_id, or [''] if in cat list
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
        self._param_control_map: Dict[str, str] = {}
        self._control_dict = self._create_control_dict() if catalog else None
        self.loose_param_dict: Dict[str, common.Parameter] = {param.id: param
                                                              for param in as_list(catalog.params)} if catalog else {}

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
        Get all controls contained in this control and add it to the growing dict.

        Add all its sub-controls to the dict recursively.
        The path does not change because only groups are in the path, and controls cannot contain groups.
        """
        if control_handle.control.controls:
            group_id = control_handle.group_id
            group_title = control_handle.group_title
            group_class = control_handle.group_class
            for sub_control in control_handle.control.controls:
                control_handle = CatalogInterface.ControlHandle(
                    group_id=group_id, group_title=group_title, group_class=group_class, path=path, control=sub_control
                )
                control_dict[sub_control.id] = control_handle
                self._add_sub_controls(control_handle, control_dict, path)

    def _add_group_controls(self, group: cat.Group, control_dict: Dict[str, ControlHandle], path: List[str]) -> None:
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
                    path=group_path
                )
                control_dict[control.id] = control_handle
                self._add_sub_controls(control_handle, control_dict, group_path)
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
                control_handle = CatalogInterface.ControlHandle(
                    group_id='', group_title='', group_class=const.MODEL_TYPE_CATALOG, control=control, path=group_path
                )
                control_dict[control.id] = control_handle
                self._add_sub_controls(control_handle, control_dict, group_path)
        for handle in control_dict.values():
            self._add_params_to_map(handle.control)
        return control_dict

    def _get_all_controls_in_list(self, controls: List[cat.Control], recurse: bool) -> List[cat.Control]:
        new_list: List[cat.Control] = []
        for control in controls:
            new_list.append(control)
            if recurse and control.controls:
                new_list.extend(self._get_all_controls_in_list(control.controls, recurse))
        return new_list

    def _get_all_controls_in_group(self, group: cat.Group, recurse: bool) -> List[cat.Control]:
        """
        Create a list of all controls in this group.

        recurse specifies to recurse within controls, but groups are always recursed
        """
        controls: List[cat.Control] = []
        if group.controls:
            controls.extend(self._get_all_controls_in_list(group.controls, recurse))
        for sub_group in as_list(group.groups):
            if sub_group.controls:
                controls.extend(self._get_all_controls_in_group(sub_group, recurse))
        return controls

    def get_sorted_controls_in_group(self, group_id: str) -> List[cat.Control]:
        """Get the list of controls in a group sorted by the control sort-id."""
        controls: List[cat.Control] = []
        for control in self.get_all_controls_from_dict():
            grp_id, _, _ = self.get_group_info_by_control(control.id)
            if grp_id == group_id:
                controls.append(control)
        return sorted(controls, key=lambda control: ControlIOWriter.get_sort_id(control))

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
        if param_id in self._param_control_map:
            return self.get_control(self._param_control_map[param_id])
        return None

    def get_control_id_and_status(self, control_name: str) -> Tuple[str, str]:
        """Get the control id and status using the control name."""
        for control in self.get_all_controls_from_dict():
            if ControlIOWriter.get_label(control).strip().lower() == control_name.strip().lower():
                status = ControlIOWriter.get_prop(control, 'status')
                return control.id, status
        return '', ''

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
        return ControlIOWriter.get_part_prose(control, part_name)

    def get_all_controls_from_catalog(self, recurse: bool) -> Iterator[cat.Control]:
        """
        Yield all deep and individual controls from the actual catalog by group.

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
        """Get all the group id's as a list of sorted strings."""
        return sorted(filter(lambda id: id, list({control.group_id for control in self._control_dict.values()})))

    def get_all_groups_from_catalog(self) -> List[cat.Group]:
        """Retrieve all groups in the catalog sorted by group_id."""
        groups: List[cat.Group] = []
        if self._catalog.groups:
            for my_group in self._catalog.groups:
                for res in CatalogInterface._get_groups_from_group(my_group):
                    groups.append(res)
        return sorted(groups, key=lambda group: group.id)

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
                        label = ControlIOWriter.get_label(part)
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
            if ControlIOWriter.is_withdrawn(control):
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
        """Return the path into the catalog for this control."""
        return self._control_dict[control_id].path

    def replace_control(self, control: cat.Control) -> None:
        """Replace the control in the control_dict after modifying it."""
        self._control_dict[control.id].control = control

    def delete_control(self, control_id: str) -> None:
        """Delete the control from the control_dict based on id."""
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
            The new list of updated controls, possibly with some missing if they have been removed from the dict
        """
        new_list: List[cat.Control] = []
        for control in controls:
            # first update the control itself by getting it from the dict
            control = self.get_control(control.id)
            # no warning given if control not found in dict.  it is assumed to have been removed from the catalog.
            if control is not None:
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
        self._catalog.params = list(self.loose_param_dict.values())

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
    def setparam_to_param(param_id: str, set_param: prof.SetParameter) -> common.Parameter:
        """
        Convert setparameter to parameter.

        Args:
            param_id: the id of the parameter
            set_param: the set_parameter from a profile

        Returns:
            a Parameter with param_id and content from the SetParameter
        """
        return common.Parameter(id=param_id, values=set_param.values, select=set_param.select, label=set_param.label)

    @staticmethod
    def _get_full_profile_param_dict(profile: prof.Profile) -> Dict[str, common.Parameter]:
        """Get the full mapping of param_id to modified value for this profiles set_params."""
        set_param_dict: Dict[str, common.Parameter] = {}
        if not profile.modify:
            return set_param_dict
        for set_param in as_list(profile.modify.set_parameters):
            param = CatalogInterface.setparam_to_param(set_param.param_id, set_param)
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
        param_dict = ControlIOReader.get_control_param_dict(control, values_only)
        for key in param_dict.keys():
            if key in profile_param_dict:
                param_dict[key] = profile_param_dict[key]
        return param_dict

    def write_catalog_as_markdown(
        self,
        md_path: pathlib.Path,
        yaml_header: dict,
        sections_dict: Optional[Dict[str, str]],
        prompt_responses: bool,
        additional_content: bool = False,
        profile: Optional[prof.Profile] = None,
        overwrite_header_values: bool = False,
        set_parameters: bool = False,
        required_sections: Optional[str] = None,
        allowed_sections: Optional[str] = None
    ) -> None:
        """
        Write out the catalog controls from dict as markdown files to the specified directory.

        Args:
            md_path: Path to directory in which to write the markdown
            yaml_header: Dictionary to write into the yaml header of the controls
            sections_dict: Optional dict mapping section short names to long
            prompt_responses: Whether to prompt for responses in the control markdown
            additional_content: Should the additional content be printed corresponding to profile adds
            profile: Optional profile containing the adds making up additional content
            overwrite_header_values: Overwrite existing values in markdown header content but add new content
            set_parameters: Set header values based on params in the control and in the profile
            required_sections: Optional string containing list of sections that should be prompted for prose
            allowed_sections: Optional string containing list of sections that should be included in markdown

        Returns:
            None

        Notes:
            The header should capture current values for parameters.
            Special handling is needed if a profile is provided, in which case the header should only have details
            captured in the set_params of the profile.  label, select, choice, how-many should only appear if they
            are specified explicitly in the profile's set_parameters.
        """
        writer = ControlIOWriter()
        required_section_list = required_sections.split(',') if required_sections else []
        allowed_section_list = allowed_sections.split(',') if allowed_sections else []

        # create the directory in which to write the control markdown files
        md_path.mkdir(exist_ok=True, parents=True)
        catalog_interface = CatalogInterface(self._catalog)
        # get the list of params for this profile from its set_params
        # this is just from the set_params
        full_profile_param_dict = CatalogInterface._get_full_profile_param_dict(profile) if profile else {}
        # write out the controls
        for control in catalog_interface.get_all_controls_from_catalog(True):
            # make copy of incoming yaml header
            new_header = copy.deepcopy(yaml_header)
            # here we do special handling of how set-parameters merge with the yaml header
            if set_parameters:
                # get all params for this control
                control_param_dict = ControlIOReader.get_control_param_dict(control, False)
                set_param_dict: Dict[str, str] = {}
                for param_id, param_dict in control_param_dict.items():
                    # if the param is in the profile set_params, load its contents first and mark as profile-values
                    if param_id in full_profile_param_dict:
                        # get the param from the profile set_param
                        param = full_profile_param_dict[param_id]
                        # assign its contents to the dict
                        new_dict = ModelUtils.parameter_to_dict(param, True)
                        profile_values = new_dict.get(const.VALUES, None)
                        if profile_values:
                            new_dict[const.PROFILE_VALUES] = profile_values
                            new_dict.pop(const.VALUES)
                        # then insert the original, incoming values as values
                        if param_id in control_param_dict:
                            orig_param = control_param_dict[param_id]
                            orig_dict = ModelUtils.parameter_to_dict(orig_param, True)
                            # pull only the values from the actual control dict
                            # all the other elements are from the profile set_param
                            new_dict[const.VALUES] = orig_dict.get(const.VALUES, None)
                    else:
                        new_dict = ModelUtils.parameter_to_dict(param_dict, True)
                    new_dict.pop('id')
                    set_param_dict[param_id] = new_dict
                if set_param_dict:
                    if const.SET_PARAMS_TAG not in new_header:
                        new_header[const.SET_PARAMS_TAG] = {}
                    if overwrite_header_values:
                        # update the control params with new values
                        for key, value in new_header[const.SET_PARAMS_TAG].items():
                            if key in control_param_dict:
                                set_param_dict[key] = value
                    else:
                        # update the control params with any values in yaml header not set in control
                        # need to maintain order in the set_param_dict
                        for key, value in new_header[const.SET_PARAMS_TAG].items():
                            if key in control_param_dict and key not in set_param_dict:
                                set_param_dict[key] = value
                    new_header[const.SET_PARAMS_TAG] = set_param_dict
                elif const.SET_PARAMS_TAG in new_header:
                    # need to cull any params that are not in control
                    pop_list: List[str] = []
                    for key in new_header[const.SET_PARAMS_TAG].keys():
                        if key not in control_param_dict:
                            pop_list.append(key)
                    for pop in pop_list:
                        new_header[const.SET_PARAMS_TAG].pop(pop)
            _, group_title, _ = catalog_interface.get_group_info_by_control(control.id)
            # control could be in sub-group of group so build path to it
            group_dir = md_path
            control_path = catalog_interface.get_control_path(control.id)
            for sub_dir in control_path:
                group_dir = group_dir / sub_dir
                if not group_dir.exists():
                    group_dir.mkdir(parents=True, exist_ok=True)
            writer.write_control_for_editing(
                group_dir,
                control,
                group_title,
                new_header,
                sections_dict,
                additional_content,
                prompt_responses,
                profile,
                overwrite_header_values,
                required_section_list,
                allowed_section_list
            )

    @staticmethod
    def _get_group_ids_and_dirs(md_path: pathlib.Path) -> Dict[str, pathlib.Path]:
        """
        Create a sorted map of group id to group dir that is ordered by group id.

        This includes '' as the root group id.
        """
        # manually insert the top dir as group ''
        id_map: Dict[str, pathlib.Path] = {'': md_path}
        for gdir in md_path.glob('*/'):
            if gdir.is_dir():
                id_map[gdir.stem] = gdir
        # rebuild the dict by inserting items in manner sorted by key
        sorted_id_map: Dict[str, pathlib.Path] = {}
        for key in sorted(id_map):
            sorted_id_map[key] = id_map[key]
        return sorted_id_map

    def read_catalog_from_markdown(self, md_path: pathlib.Path, set_parameters: bool) -> cat.Catalog:
        """
        Read the groups and catalog controls from the given directory.

        This will overwrite the existing groups and controls in the catalog.
        """
        if not self._catalog:
            self._catalog = gens.generate_sample_model(cat.Catalog)
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
                control, control_group_title = ControlIOReader.read_control(control_path, set_parameters)
                if control_group_title:
                    if group_title:
                        if control_group_title != group_title:
                            logger.warning(
                                f'Control {control.id} group title {control_group_title} differs from {group_title}'
                            )
                    else:
                        group_title = control_group_title
                control_list_raw.append(control)
            control_list = sorted(control_list_raw, key=lambda control: ControlIOWriter.get_sort_id(control))
            if group_id:
                if not group_title:
                    logger.warning(f'No group title found in controls for group {group_id}')
                new_group = cat.Group(id=group_id, title=group_title)
                new_group.controls = control_list
                groups.append(new_group)
            else:
                # if the list of controls has no group id it also has no title and is just the controls of the catalog
                self._catalog.controls = control_list
        self._catalog.groups = groups if groups else None
        self._create_control_dict()
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
        imp_req_map: Dict[str, ossp.ImplementRequirement] = {}
        for group_path in CatalogInterface._get_group_ids_and_dirs(md_path).values():
            for control_file in group_path.glob('*.md'):
                sort_id, imp_req = ControlIOReader.read_implemented_requirement(control_file, avail_comps)
                imp_req_map[sort_id] = imp_req
        return [imp_req_map[key] for key in sorted(imp_req_map.keys())]

    @staticmethod
    def read_additional_content(
        md_path: pathlib.Path, required_sections_list: List[str]
    ) -> Tuple[List[prof.Alter], Dict[str, Any], Dict[str, str]]:
        """Read all markdown controls and return list of alters plus control param dict and param sort map."""
        alters_map: Dict[str, prof.Alter] = {}
        final_param_dict: Dict[str, Any] = {}
        param_sort_map: Dict[str, str] = {}
        for group_path in CatalogInterface._get_group_ids_and_dirs(md_path).values():
            for control_file in group_path.glob('*.md'):
                sort_id, control_alters, control_param_dict = ControlIOReader.read_new_alters_and_params(
                    control_file,
                    required_sections_list
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

    def get_sections(self) -> List[str]:
        """Get the available sections by a full index of all controls."""
        sections: List[str] = []

        for control in self._control_dict.values():
            if not control.control.parts:
                continue
            for part in control.control.parts:
                if part.name not in sections and part.name != 'statement':
                    sections.append(part.name)
        return sections

    @staticmethod
    def merge_controls(dest: cat.Control, src: cat.Control, replace_params: bool) -> None:
        """
        Merge the src control into dest.

        Args:
            dest: destination control into which content will be added
            src: source control with new content
            replace_params: replace the control params with the new ones
        """
        dest.parts = src.parts
        if replace_params:
            dest.params = src.params

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
            dest = self.get_control(src.id)
            if dest:
                dest_group, _, _ = self.get_group_info_by_control(dest.id)
                if dest_group != group_id:
                    raise TrestleError(f'Markdown for control {src.id} has different group id.')
                CatalogInterface.merge_controls(dest, src, replace_params)
                self.replace_control(dest)
            else:
                # need to add the control knowing its group must already exist
                # get group info from an arbitrary control already present in group
                _, control_handle = self._find_control_in_group(group_id)
                # add the control and its handle to the param_dict
                self._control_dict[src.id] = control_handle

        # now need to cull any controls that are not in the src catalog
        handled_ids = set(cat_interface._control_dict.keys())
        orig_ids = set(self._control_dict.keys())
        extra_ids = orig_ids.difference(handled_ids)
        for extra_id in extra_ids:
            self._control_dict.pop(extra_id)

        self.update_catalog_controls()
