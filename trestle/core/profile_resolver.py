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
import re
import string
from typing import Dict, Iterator, List, Optional, Set, Tuple, Union
from uuid import uuid4

import trestle.core.const as const
import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.common_types import OBT
from trestle.core.const import MARKDOWN_URL_REGEX, UUID_REGEX
from trestle.core.control_io import ControlIOReader
from trestle.core.err import TrestleError
from trestle.core.pipeline import Pipeline
from trestle.core.remote import cache
from trestle.core.utils import as_list, none_if_empty
from trestle.oscal import common

logger = logging.getLogger(__name__)

ID = 'id'

NAME = 'name'

PART_EXCLUDE = [NAME]

PROPERTY_EXCLUDE = [NAME]

PARAMETER_EXCLUDE = [ID]

CONTROL_EXCLUDE = [ID]

CATALOG_EXCLUDE = ['uuid', 'metadata', 'back_matter']

ITEM_EXCLUDE_MAP = {
    'Part': PART_EXCLUDE,
    'Property': PROPERTY_EXCLUDE,
    'Parameter': PARAMETER_EXCLUDE,
    'Control': CONTROL_EXCLUDE,
    'Catalog': CATALOG_EXCLUDE
}


class ProfileResolver():
    """Class to resolve a catalog given a profile."""

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

        def _find_uuid_refs(self, control_id: str) -> Set[str]:
            """
            Find all needed resource refs buried in control links and prose.

            For any controls retained in the resolved profile catalog, if any
            prose references a document by uuid, that reference needs to be in backmatter.
            """
            control = self._catalog_interface.get_control(control_id)
            refs = set()
            if control.links is not None:
                for link in control.links:
                    uuid_str = link.href.replace('#', '')
                    refs.add(uuid_str)
            if control.parts is not None:
                for part in control.parts:
                    if part.prose is not None:
                        # find the two parts, label and ref, in each markdown url
                        # expecting form [label](#uuid)
                        # but if it is a control ref it may be e.g. [CM-7](#cm-7)
                        # for now label is not used
                        # the ref may be a uuid or control id
                        # currently only uuids are used to confirm needed presence in backmatter
                        # note that prose may be multi-line but findall searches all lines
                        matches = re.findall(MARKDOWN_URL_REGEX, part.prose)
                        for match in matches:
                            ref = match[1]
                            if len(ref) > 1 and ref[0] == '#':
                                uuid_match = re.findall(UUID_REGEX, ref[1:])
                                # there should be only one uuid in the parens
                                if uuid_match:
                                    refs.add(uuid_match[0])
            if control.controls is not None:
                for sub_control in control.controls:
                    refs.update(self._find_uuid_refs(sub_control.id))
            return refs

        def _find_all_uuid_refs(self, needed_control_ids: List[str]) -> Set[str]:
            """Find all references needed by controls."""
            refs = set()
            for control_id in needed_control_ids:
                refs.update(self._find_uuid_refs(control_id))
            return refs

        def _controls_selected(self, select_list: Optional[List[prof.SelectControlById]]) -> List[str]:
            control_ids: List[str] = []
            if select_list is not None:
                for select_control in select_list:
                    if select_control.matching is not None:
                        raise TrestleError('Profiles with SelectControlById based on matching are not supported.')
                    include_children = select_control.with_child_controls == prof.WithChildControls.yes
                    if select_control.with_ids:
                        new_ids = [withid.__root__ for withid in select_control.with_ids]
                        for id_ in new_ids:
                            control_ids.append(id_)
                            if include_children:
                                control_ids.extend(self._catalog_interface.get_dependent_control_ids(id_))
            return control_ids

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
            return [id_ for id_ in include_ids if id_ not in exclude_ids]

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

        def _prune_catalog(self) -> cat.Catalog:
            """Prune the controls in the current catalog."""
            if self._import is None:
                return self._catalog

            needed_ids = self._find_needed_control_ids()

            # if a control includes controls - only include those that we know are needed
            final_control_ids = self._prune_controls(needed_ids)

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

            # find all referenced uuids - they should be 1:1 with those in backmatter
            needed_uuid_refs: Set[str] = self._find_all_uuid_refs(final_control_ids)

            # prune the list of resources to only those that are needed
            new_resources: Optional[List[common.Resource]] = []
            if self._catalog.back_matter is not None and self._catalog.back_matter.resources is not None:
                new_resources = [res for res in self._catalog.back_matter.resources if res.uuid in needed_uuid_refs]

            new_groups: Optional[List[cat.Group]] = list(group_dict.values())

            # should avoid empty lists so set to None if empty
            new_resources = none_if_empty(new_resources)
            new_groups = none_if_empty(new_groups)
            cat_controls = none_if_empty(cat_controls)

            new_cat = cat.Catalog(
                uuid=str(uuid4()),
                metadata=self._catalog.metadata,
                back_matter=common.BackMatter(resources=new_resources),
                controls=cat_controls,
                groups=new_groups
            )

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

    class Merge(Pipeline.Filter):
        """
        Merge the incoming catalogs according to rules in the profile.

        The incoming catalogs have already been pruned based on the import.
        Now the controls must be gathered, merged, and grouped based on the merge settings.
        """

        def __init__(self, profile: prof.Profile) -> None:
            """Initialize the class with the profile."""
            logger.debug('merge filter initialize')
            self._profile = profile

        def _get_id(self, item: OBT) -> Optional[str]:
            id_ = getattr(item, ID, None)
            if id_ is None:
                id_ = getattr(item, NAME, None)
            return id_

        def _merge_lists(self, dest: List[OBT], src: List[OBT], merge_method: prof.Method) -> None:
            added_items = []
            if merge_method == prof.Method.keep:
                dest.extend(src)
                return
            for item in src:
                # if there is an exact copy of this in dest then ignore it
                if item not in dest:
                    merged = False
                    item_id = self._get_id(item)
                    if item_id is not None:
                        for other in dest:
                            other_id = self._get_id(other)
                            if other_id == item_id:
                                if merge_method == prof.Method.merge:
                                    self._merge_items(other, item, merge_method)
                                merged = True
                                break
                    # it isn't already in dest and no match was found for merge, so append
                    if not merged:
                        added_items.append(item)
            dest.extend(added_items)

        def _merge_attrs(
            self, dest: Union[OBT, List[OBT]], src: Union[OBT, List[OBT]], attr: str, merge_method: prof.Method
        ) -> None:
            """Merge this attr of src into the attr of dest."""
            src_attr = getattr(src, attr, None)
            if src_attr is None:
                return
            item_type = type(src).__name__
            if attr in ITEM_EXCLUDE_MAP.get(item_type, []):
                return
            dest_attr = getattr(dest, attr, None)
            if dest_attr is not None and merge_method == prof.Method.use_first:
                return
            if dest_attr == src_attr and merge_method != prof.Method.keep:
                return
            if isinstance(dest_attr, list):
                self._merge_lists(dest_attr, src_attr, merge_method)
            else:
                setattr(dest, attr, src_attr)

        def _merge_items(self, dest: OBT, src: OBT, merge_method: prof.Method) -> None:
            """Merge two items recursively."""
            for field in src.__fields_set__:
                self._merge_attrs(dest, src, field, merge_method)

        def _group_contents(self, group: cat.Group) -> Tuple[List[cat.Control], List[common.Parameter]]:
            """Get flattened content of group and its groups recursively."""
            controls = []
            params = []
            controls.extend(as_list(group.controls))
            params.extend(as_list(group.params))
            if group.groups is not None:
                for sub_group in group.groups:
                    new_controls, new_params = self._group_contents(sub_group)
                    controls.extend(new_controls)
                    params.extend(new_params)
            return controls, params

        def _flatten_catalog(self, catalog: cat.Catalog, as_is: bool) -> cat.Catalog:
            """Flatten the groups of the catalog if as_is is False."""
            if as_is or catalog.groups is None:
                return catalog

            # as_is is False so flatten the controls into a single list
            catalog.controls = as_list(catalog.controls)
            catalog.params = as_list(catalog.params)
            for group in catalog.groups:
                new_controls, new_params = self._group_contents(group)
                catalog.controls.extend(new_controls)
                catalog.params.extend(new_params)
            catalog.controls = none_if_empty(catalog.controls)
            catalog.params = none_if_empty(catalog.params)
            catalog.groups = None
            return catalog

        def _merge_two_catalogs(
            self, dest: cat.Catalog, src: cat.Catalog, merge_method: prof.Method, as_is: bool
        ) -> cat.Catalog:
            # merge_method is use_first, merge, or keep
            # if as_is is false, the result is flattened

            dest = self._flatten_catalog(dest, as_is)
            src = self._flatten_catalog(src, as_is)

            self._merge_items(dest, src, merge_method)

            return dest

        def _merge_catalog(self, merged: Optional[cat.Catalog], catalog: cat.Catalog) -> cat.Catalog:
            """Merge the controls in the catalog into merged catalog."""
            # no merge means keep, including dups
            # same for merge with no combine
            # groups are merged only if separate directive such as as-is is given
            # use-first is a merge combination rule
            # merge is a merge combination rule for controls.  groups are not merged by this rule
            # merge/as-is and merge/custom are used for merging groups
            # if neither as-is nor custom is specified - just get single list of controls
            # unstructured controls should appear after any loose params

            # make copies to avoid changing input objects
            local_cat = catalog.copy(deep=True)
            local_merged = merged.copy(deep=True) if merged else None

            merge_method = prof.Method.keep
            as_is = False
            if self._profile.merge is not None:
                if self._profile.merge.custom is not None:
                    raise TrestleError('Profile with custom merge is not supported.')
                if self._profile.merge.as_is is not None:
                    as_is = self._profile.merge.as_is
                if self._profile.merge.combine is None:
                    logger.warning('Profile has merge but no combine so defaulting to combine/merge.')
                    merge_method = prof.Method.merge
                else:
                    merge_combine = self._profile.merge.combine
                    if merge_combine.method is None:
                        logger.warning('Profile has merge combine but no method.  Defaulting to merge.')
                        merge_method = prof.Method.merge
                    else:
                        merge_method = merge_combine.method

            if local_merged is None:
                return self._flatten_catalog(local_cat, as_is)

            # merge the incoming catalog with merged based on merge_method and as_is
            return self._merge_two_catalogs(local_merged, local_cat, merge_method, as_is)

        def process(self, pipelines: List[Pipeline]) -> Iterator[cat.Catalog]:
            """
            Merge the incoming catalogs.

            This pulls from import and iterates over the incoming catalogs.
            The way groups, lists of controls, and controls themselves get merged is specified by the profile.
            """
            merged: Optional[cat.Catalog] = None
            logger.debug(f'merge entering process with {len(pipelines)} pipelines')
            for pipeline in pipelines:
                catalog = next(pipeline.process(None))
                merged = self._merge_catalog(merged, catalog)
            yield merged

    class Modify(Pipeline.Filter):
        """Modify the controls based on the profile."""

        def __init__(self, profile: prof.Profile, change_prose=False, block_adds=False) -> None:
            """Initialize the filter."""
            self._profile = profile
            self._catalog_interface: Optional[CatalogInterface] = None
            self._block_adds = block_adds
            self._change_prose = change_prose
            logger.debug(f'modify initialize filter with profile {profile.metadata.title}')

        @staticmethod
        def _replace_id_with_text(prose: str, param_dict: Dict[str, str]) -> str:
            """Find all instances of param_id in prose and replace with param_text.

            Need to check all values in dict for a match
            Reject matches where the string has an adjacent alphanumeric char: param_1 and param_10 or aparam_1
            """
            for param_id, param_value in param_dict.items():
                bad_chars = string.ascii_letters + string.digits + '._'
                new_prose = prose
                id_len = len(param_id)
                loc = 0
                if param_id not in prose:
                    continue
                # handle simple case directly
                if prose == param_id:
                    return param_value
                # it's there, but may be param_10 instead of param_1
                while True:
                    if loc >= len(new_prose):
                        return new_prose
                    next_loc = new_prose[loc:].find(param_id)
                    if next_loc < 0:
                        return new_prose
                    loc += next_loc
                    if loc > 0 and new_prose[loc - 1] in bad_chars:
                        loc += id_len
                        continue
                    end_loc = loc + id_len
                    if end_loc == len(new_prose) or new_prose[end_loc] not in bad_chars:
                        new_prose = new_prose[:loc] + param_value + new_prose[end_loc:]
                        loc += len(param_value)
                        continue
                    loc += id_len

        @staticmethod
        def _replace_params(text: str, param_dict: Dict[str, str]) -> str:
            """
            Replace params found in moustaches with values from the param_dict.

            A single line of prose may contain multiple moustaches.
            """
            # first check if there are any moustache patterns in the text
            staches = re.findall(r'{{.*?}}', text)
            if not staches:
                return text
            # now have list of all staches including braces, e.g. ['{{foo}}', '{{bar}}']
            # clean the staches so they just have the param ids
            param_ids = []
            for stache in staches:
                # remove braces so these are just param_ids but may have extra chars
                stache_contents = stache[2:(-2)]
                param_id = stache_contents.replace('insert: param,', '').strip()
                param_ids.append(param_id)

            # now replace original stache text with param values
            for i, _ in enumerate(staches):
                text = text.replace(staches[i], param_dict[param_ids[i]], 1)
            return text

        @staticmethod
        def _replace_part_prose(control: cat.Control, part: common.Part, param_dict: Dict[str, str]) -> None:
            """Replace the part prose according to set_param."""
            if part.prose is not None:
                fixed_prose = ProfileResolver.Modify._replace_params(part.prose, param_dict)
                # change the prose in the control itself
                part.prose = fixed_prose
            for prt in as_list(part.parts):
                ProfileResolver.Modify._replace_part_prose(control, prt, param_dict)
            for sub_control in as_list(control.controls):
                for prt in as_list(sub_control.parts):
                    ProfileResolver.Modify._replace_part_prose(sub_control, prt, param_dict)

        @staticmethod
        def _replace_control_prose(control: cat.Control, param_dict: Dict[str, str]) -> None:
            """Replace the control prose according to set_param."""
            for part in as_list(control.parts):
                if part.prose is not None:
                    fixed_prose = ProfileResolver.Modify._replace_params(part.prose, param_dict)
                    # change the prose in the control itself
                    part.prose = fixed_prose
                for prt in as_list(part.parts):
                    ProfileResolver.Modify._replace_part_prose(control, prt, param_dict)
            for sub_control in as_list(control.controls):
                for prt in as_list(sub_control.parts):
                    ProfileResolver.Modify._replace_part_prose(sub_control, prt, param_dict)

        @staticmethod
        def _add_contents_as_list(add: prof.Add) -> List[OBT]:
            add_list = []
            add_list.extend(as_list(add.props))
            add_list.extend(as_list(add.parts))
            add_list.extend(as_list(add.links))
            return add_list

        @staticmethod
        def _add_adds_to_part(part: common.Part, add: prof.Add) -> None:
            for attr in ['params', 'props', 'parts', 'links']:
                add_list = getattr(add, attr, None)
                if add_list:
                    ProfileResolver.Modify._add_attr_to_part(part, add_list, attr, add.position)

        @staticmethod
        def _add_to_list(input_list: List[OBT], add: prof.Add) -> bool:
            """Add the contents of the add according to its by_id and position.

            Return True on success or False if id needed and not found.

            If the add is not by_id then the insertion will happen immediately.
            But if the add is by_id it will insert if the id is found, or return False if not.
            This allows a separate recursive routine to search sub-lists for the id.

            Note: If a list can be none this method will fail
            """
            add_list = ProfileResolver.Modify._add_contents_as_list(add)
            # if by_id is not specified then OSCAL docs say to interpret before and after as starting or ending
            if not add.by_id:
                # if we are just adding to the list then the add contents should be of the same type
                if add.position in [prof.Position.before, prof.Position.starting]:
                    for offset, item in enumerate(add_list):
                        input_list.insert(offset, item)
                    return True
                else:
                    input_list.extend(add_list)
                    return True
            # Test here for matched by_id attribute.
            try:
                for index in range(len(input_list)):
                    if input_list[index].id == add.by_id:
                        if add.position == prof.Position.after:
                            for offset, new_item in enumerate(add_list):
                                input_list.insert(index + 1 + offset, new_item)
                            return True
                        elif add.position == prof.Position.before:
                            for offset, new_item in enumerate(add_list):
                                input_list.insert(index + offset, new_item)
                            return True
                        # if starting or ending, the adds go directly into this part according to type
                        ProfileResolver.Modify._add_adds_to_part(input_list[index], add)
                        return True
            except AttributeError:
                raise TrestleError(
                    'Cannot use "after" or "before" modifictions for a list where elements'
                    + ' do not contain the referenced by_id attribute.'
                )
            return False

        @staticmethod
        def _add_to_parts(parts: List[common.Part], add: prof.Add) -> bool:
            if ProfileResolver.Modify._add_to_list(parts, add):
                return True
            for part in parts:
                if part.parts is not None and ProfileResolver.Modify._add_to_parts(part.parts, add):
                    return True
            return False

        @staticmethod
        def _add_attr_to_part(part: common.Part, items: List[OBT], attr: str, position: prof.Position) -> None:
            attr_list = as_list(getattr(part, attr, None))
            if position in [prof.Position.starting, prof.Position.before]:
                items.extend(attr_list)
                attr_list = items
            else:
                attr_list.extend(items)
            setattr(part, attr, attr_list)

        @staticmethod
        def _add_attr_to_control(control: cat.Control, items: List[OBT], attr: str, position: prof.Position) -> None:
            attr_list = as_list(getattr(control, attr, None))
            if position in [prof.Position.starting, prof.Position.before]:
                items.extend(attr_list)
                attr_list = items
            else:
                attr_list.extend(items)
            setattr(control, attr, attr_list)

        @staticmethod
        def _add_to_control(control: cat.Control, add: prof.Add) -> None:
            control.parts = as_list(control.parts)
            if add.by_id is None or add.by_id == control.id:
                # add contents will be added to the control directly
                for attr in ['params', 'props', 'parts', 'links']:
                    add_list = getattr(add, attr, None)
                    if add_list:
                        ProfileResolver.Modify._add_attr_to_control(control, add_list, attr, add.position)
                return
            else:
                if not ProfileResolver.Modify._add_to_parts(control.parts, add):
                    logger.warning(f'Could not find id for add in control {control.id}: {add.by_id}')

        def _set_parameter_in_control(self, set_param: prof.SetParameter) -> None:
            """
            Find the control with the param_id in it and set the parameter value.

            This does not recurse because expectation is that only top level params will be set.
            """
            control = self._catalog_interface.get_control_by_param_id(set_param.param_id)
            if control is None:
                raise TrestleError(
                    f'Set parameter object in profile does not have a corresponding param-id: "{set_param.param_id}"'
                )  # noqa:
            control.params = as_list(control.params)
            param_ids = [param.id for param in control.params]
            index = param_ids.index(set_param.param_id)
            param = control.params[index]
            # FIXME these may need to merge
            if set_param.values:
                param.values = set_param.values
            if set_param.constraints:
                param.constraints = set_param.constraints
            if set_param.guidelines:
                param.guidelines = set_param.guidelines
            if set_param.links:
                param.links = set_param.links
            if set_param.props:
                param.props = set_param.props
            if set_param.select:
                param.select = set_param.select
            if set_param.usage:
                param.usage = set_param.usage
            control.params[index] = param
            self._catalog_interface.replace_control(control)

        def _change_prose_with_param_values(self):
            """Go through all controls and change prose based on param values."""
            param_dict: Dict[str, str] = {}
            # build the full mapping of params to values
            for control in self._catalog_interface.get_all_controls_from_dict():
                param_dict.update(ControlIOReader.get_control_param_dict(control, False))
            # insert param values into prose of all controls
            for control in self._catalog_interface.get_all_controls_from_dict():
                self._replace_control_prose(control, param_dict)

        def _modify_controls(self, catalog: cat.Catalog) -> cat.Catalog:
            """Modify the controls based on the profile."""
            logger.debug(f'modify specify catalog {catalog.metadata.title} for profile {self._profile.metadata.title}')
            self._catalog_interface = CatalogInterface(catalog)
            alters: Optional[List[prof.Alter]] = None
            # find the modify and alters
            if self._profile.modify is not None:
                # change all parameter values
                if self._profile.modify.set_parameters is not None:
                    param_list = self._profile.modify.set_parameters
                    for param in param_list:
                        self._set_parameter_in_control(param)
                alters = self._profile.modify.alters

            if alters is not None:
                title = self._profile.metadata.title
                for alter in alters:
                    if alter.control_id is None:
                        logger.warning(f'Alter must have control id specified in profile {title}.')
                        continue
                    id_ = alter.control_id
                    if alter.removes is not None:
                        logger.warning(f'Alter not supported for removes in profile {title} control {id_}')
                        continue
                    # we want a warning about adds even if adds are blocked, as in profile generate
                    if alter.adds is None:
                        logger.warning(f'Alter has no adds in profile {title} control {id_}')
                        continue
                    if not self._block_adds:
                        for add in alter.adds:
                            if add.position is None and add.parts is not None:
                                msg = f'Alter/Add position is not specified in profile {title} control {id_}'
                                msg += ' when adding part, so defaulting to ending.'
                                logger.warning(msg)
                                add.position = prof.Position.ending
                            control = self._catalog_interface.get_control(id_)
                            if control is None:
                                logger.warning(
                                    f'Alter/Add refers to control {id_} but it is not found in the import '
                                    + f'for profile {self._profile.metadata.title}'
                                )
                            else:
                                self._add_to_control(control, add)
                                self._catalog_interface.replace_control(control)

            if self._change_prose:
                # go through all controls and fix the prose based on param values
                self._change_prose_with_param_values()

            catalog = self._catalog_interface.get_catalog()

            # update the original profile metadata with new contents
            # roles and responsible-parties will be pulled in with new uuid's
            new_metadata = self._profile.metadata
            new_metadata.title = f'{catalog.metadata.title}: Resolved by profile {self._profile.metadata.title}'
            links: List[common.Link] = []
            for import_ in self._profile.imports:
                links.append(common.Link(**{'href': import_.href, 'rel': 'resolution-source'}))
            new_metadata.links = links

            # move catalog controls from dummy group '' into the catalog
            for group in as_list(catalog.groups):
                if not group.id:
                    catalog.controls = group.controls
                    catalog.groups.remove(group)
                    break

            catalog.metadata = new_metadata

            return catalog

        def process(self, catalog_iter: Iterator[cat.Catalog]) -> Iterator[cat.Catalog]:
            """Make the modifications to the controls based on the profile."""
            catalog = next(catalog_iter)
            logger.debug(
                f'modify process with catalog {catalog.metadata.title} using profile {self._profile.metadata.title}'
            )
            yield self._modify_controls(catalog)

    class Import(Pipeline.Filter):
        """Import filter class."""

        def __init__(
            self,
            trestle_root: pathlib.Path,
            import_: prof.Import,
            change_prose=False,
            block_adds: bool = False
        ) -> None:
            """Initialize and store trestle root for cache access."""
            self._trestle_root = trestle_root
            self._import = import_
            self._block_adds = block_adds
            self._change_prose = change_prose

        def process(self, input_=None) -> Iterator[cat.Catalog]:
            """Load href for catalog or profile and yield each import as catalog imported by its distinct pipeline."""
            logger.debug(f'import entering process with href {self._import.href}')
            fetcher = cache.FetcherFactory.get_fetcher(self._trestle_root, self._import.href)

            model: Union[cat.Catalog, prof.Profile]
            model, model_type = fetcher.get_oscal()

            if model_type == const.MODEL_TYPE_CATALOG:
                logger.debug(f'DIRECT YIELD in import of catalog {model.metadata.title}')
                yield model
            else:
                if model_type != const.MODEL_TYPE_PROFILE:
                    raise TrestleError(f'Improper model type {model_type} as profile import.')
                profile: prof.Profile = model

                pipelines: List[Pipeline] = []
                logger.debug(
                    f'import pipelines for sub_imports of profile {self._import.href} with title {model.metadata.title}'
                )
                for sub_import in profile.imports:
                    import_filter = ProfileResolver.Import(self._trestle_root, sub_import)
                    prune_filter = ProfileResolver.Prune(sub_import, profile)
                    pipeline = Pipeline([import_filter, prune_filter])
                    pipelines.append(pipeline)
                    logger.debug(
                        f'sub_import add pipeline for sub href {sub_import.href} of main href {self._import.href}'
                    )
                merge_filter = ProfileResolver.Merge(profile)
                modify_filter = ProfileResolver.Modify(profile, self._change_prose, self._block_adds)
                final_pipeline = Pipeline([merge_filter, modify_filter])
                yield next(final_pipeline.process(pipelines))

    @staticmethod
    def get_resolved_profile_catalog(
        trestle_root: pathlib.Path, profile_path: pathlib.Path, block_adds: bool = False
    ) -> cat.Catalog:
        """Create the resolved profile catalog given a profile path."""
        logger.debug(f'get resolved profile catalog for {profile_path} via generated Import.')
        import_ = prof.Import(href=str(profile_path), include_all={})
        import_filter = ProfileResolver.Import(trestle_root, import_, True, block_adds)
        logger.debug('launch pipeline')
        result = next(import_filter.process())
        return result
