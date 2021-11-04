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
from typing import Dict, Iterator, List, Optional, Set, Union
from uuid import uuid4

import trestle.core.const as const
import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.common_types import OBT
from trestle.core.const import MARKDOWN_URL_REGEX, UUID_REGEX
from trestle.core.err import TrestleError
from trestle.core.pipeline import Pipeline
from trestle.core.remote import cache
from trestle.oscal import common

logger = logging.getLogger(__name__)


class ProfileResolver():
    """Class to resolve a catalog given a profile."""

    class Prune(Pipeline.Filter):
        """Prune the catalog based on the import include rule."""

        def __init__(self, import_: prof.Import) -> None:
            """
            Inject the import.

            This needs to be created prior to knowing the catalog.
            """
            self._import: prof.Import = import_
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

        def _find_needed_control_ids(self) -> List[str]:
            """Get list of control_ids needed by profile and corresponding groups."""
            control_ids: List[str] = []

            if self._import.include_controls is not None:
                for include_control in self._import.include_controls:
                    new_ids = [withid.__root__ for withid in include_control.with_ids]
                    control_ids.extend(new_ids)
            else:
                control_ids = self._catalog_interface.get_control_ids()

            if self._import.exclude_controls is not None:
                raise TrestleError('exclude controls is not currently supported')

            return control_ids

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
            control.controls = controls if controls else None
            return control

        def _prune_controls(self, needed_ids: List[str]) -> List[str]:
            exclude_ids = []
            final_ids: List[str] = []
            for control_id in needed_ids:
                if control_id not in exclude_ids:
                    control = self._catalog_interface.get_control(control_id)
                    control = self._prune_control(needed_ids, control, exclude_ids)
                    self._catalog_interface.replace_control(control)
                    exclude_ids.append(control_id)
                    final_ids.append(control_id)
            return final_ids

        def _prune_catalog(self) -> cat.Catalog:
            """Prune the controls in the current catalog."""
            if self._import is None:
                return self._catalog

            needed_ids = self._find_needed_control_ids()

            # if a control includes controls - only include those that we know are needed
            final_control_ids = self._prune_controls(needed_ids)

            # build the needed groups of controls
            group_dict: Dict[str, cat.Group] = {}
            for control_id in final_control_ids:
                group_id, group_title, group_class = self._catalog_interface.get_group_info(control_id)
                group = group_dict.get(group_id)
                control = self._catalog_interface.get_control(control_id)
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
                for resource in self._catalog.back_matter.resources:
                    if resource.uuid in needed_uuid_refs:
                        new_resources.append(resource)

            new_groups: Optional[List[cat.Group]] = list(group_dict.values())

            # should avoid empty lists so set to None if empty
            new_resources = new_resources if new_resources else None
            new_groups = new_groups if new_groups else None

            new_cat = cat.Catalog(
                uuid=str(uuid4()),
                metadata=self._catalog.metadata,
                back_matter=common.BackMatter(resources=new_resources),
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
        """Merge the incoming catalogs according to rules in the profile."""

        def __init__(self, profile: prof.Profile) -> None:
            """Initialize the class with the profile."""
            logger.debug('merge filter initialize')
            self._profile = profile

        def _merge_controls(self, dest: cat.Control, src: cat.Control) -> None:
            """Use when the merge method is merge."""
            dest_parts = []
            if dest.parts:
                dest_parts = [part.name for part in dest.parts]
            if src.parts:
                for part in src.parts:
                    if part.name not in dest_parts:
                        dest.parts.append(part)
            if src.controls:
                if not dest.controls:
                    dest.controls = src.controls
                else:
                    self._merge_lists(dest.controls, src.controls, prof.Method.merge)

        def _merge_lists(
            self, merged_list: List[cat.Control], src_list: List[cat.Control], method: prof.Method
        ) -> None:
            merged_ids = [control.id for control in merged_list]
            for src in src_list:
                if src.id not in merged_ids:
                    # this applies to all methods: keep, use-first and merge
                    merged_list.append(src)
                else:
                    if method == prof.Method.merge:
                        index = merged_ids.index(src.id)
                        self._merge_controls(merged_list[index], src)
                    elif method == prof.Method.keep:
                        merged_list.append(src)
                    # if anything else regard as use-first and only keep first one, ignoring new one

        def _merge_catalog(self, merged: cat.Catalog, catalog: cat.Catalog) -> cat.Catalog:
            """Merge the controls in the catalog into merged catalog."""
            merge_method = prof.Method.keep
            if self._profile.merge is not None:
                if self._profile.merge.combine is None:
                    logger.warning('Profile has merge but no combine so defaulting to combine/merge.')
                    merge_method = prof.Method.merge
                else:
                    merge_combine = self._profile.merge.combine
                    if merge_combine.method is None:
                        logger.warning('Profile has merge combine but no method.  Defaulting to merge.')
                        merge_method = prof.Method.merge
                    else:
                        # use-first, merge, or keep
                        merge_method = merge_combine.method

            if merged is None:
                return catalog
            if catalog.groups is not None:
                if merged.groups is None:
                    merged.groups = []
                for group in catalog.groups:
                    # FIXME this should recurse for groups containing groups
                    if group.id not in [g.id for g in merged.groups]:
                        merged.groups.append(cat.Group(id=group.id, title=group.title, controls=[]))
                    index = [g.id for g in merged.groups].index(group.id)
                    self._merge_lists(merged.groups[index].controls, group.controls, merge_method)
            if catalog.controls:
                if not merged.controls:
                    merged.controls = catalog.controls
                else:
                    self._merge_lists(merged.controls, catalog.controls, merge_method)
            return merged

        def process(self, pipelines: List[Pipeline]) -> Iterator[cat.Catalog]:
            """
            Merge the incoming catalogs.

            This pulls from import and iterates over the incoming catalogs.
            Currently this does not use the profile but it may in the future.
            """
            merged: Optional[cat.Catalog] = None
            logger.debug(f'merge entering process with {len(pipelines)} pipelines')
            for pipeline in pipelines:
                catalog = next(pipeline.process(None))
                merged = self._merge_catalog(merged, catalog)
            yield merged

    class Modify(Pipeline.Filter):
        """Modify the controls based on the profile."""

        def __init__(self, profile: prof.Profile, block_adds: bool = False) -> None:
            """Initialize the filter."""
            self._profile = profile
            self._catalog_interface: Optional[CatalogInterface] = None
            self._block_adds = block_adds
            logger.debug(f'modify initialize filter with profile {profile.metadata.title}')

        @staticmethod
        def _replace_id_with_text(prose, param_id, param_text):
            """Find all instances of param_id in prose and replace with param_text.

            Reject matches where the string has an adjacent alphanumeric char: param_1 and param_10 or aparam_1
            """
            bad_chars = string.ascii_letters + string.digits
            new_prose = prose
            id_len = len(param_id)
            loc = 0
            # handle simple case directly
            if prose == param_id:
                return param_text
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
                    new_prose = new_prose[:loc] + param_text + new_prose[end_loc:]
                    loc += len(param_text)
                    continue
                loc += id_len

        @staticmethod
        def _replace_params(text: str, control: cat.Control, param_dict: Dict[str, prof.SetParameter]) -> str:
            """Replace params found in moustaches with assignments for this control from profile or description info."""
            # first check if there are any moustache patterns in the text
            staches = re.findall(r'{{.*?}}', text)
            if not staches:
                return text
            # now have list of all staches including braces, e.g. ['{{foo}}', '{{bar}}']
            new_staches = []
            # clean the staches so they just have the param text
            for stache in staches:
                # remove braces
                stache = stache[2:(-2)]
                stache = stache.replace('insert: param,', '').strip()
                new_staches.append(stache)
            if control.params is not None:
                for param in control.params:
                    # need to find the param_text that requires substitution.  It can be in a few places.
                    # set default if no information available for text
                    param_text = f'[{param.id} = no description available]'
                    set_param = param_dict.get(param.id, None)
                    # param value provided so just replace it
                    if set_param is not None and set_param.values is not None:
                        # TODO: Fix with issue #824
                        # If there is no value set - continue using default parameter info for now.
                        values = [value.__root__ for value in set_param.values]
                        param_text = values[0] if len(values) == 1 else f"[{', '.join(values)}]"
                    else:
                        if param.values is not None:
                            values = [value.__root__ for value in param.values]
                            param_text = values[0] if len(values) == 1 else f"[{', '.join(values)}]"
                        # if select present, use it
                        if param.select is not None:
                            param_text = '['
                            if param.select.how_many is not None:
                                param_text += f'{param.select.how_many.value}: '
                            if param.select.choice is not None:
                                param_text += ', '.join(param.select.choice)
                            param_text = f'{param_text}]'
                        # else use the label
                        elif param.label is not None:
                            param_text = f'[{param.label}]'
                        # replace this pattern in all the staches with the new param_text
                    fixed_staches = []
                    for stache in new_staches:
                        fixed = ProfileResolver.Modify._replace_id_with_text(stache, param.id, param_text)
                        fixed_staches.append(fixed)
                    new_staches = fixed_staches

            # now replace original stache text with new versions
            for i, _ in enumerate(staches):
                text = text.replace(staches[i], new_staches[i], 1)
            return text

        @staticmethod
        def _replace_part_prose(
            control: cat.Control, part: common.Part, param_dict: Dict[str, prof.SetParameter]
        ) -> None:
            """Replace the params using the _param_dict."""
            if part.prose is not None:
                fixed_prose = ProfileResolver.Modify._replace_params(part.prose, control, param_dict)
                # change the prose in the control itself
                part.prose = fixed_prose
            if part.parts is not None:
                for prt in part.parts:
                    ProfileResolver.Modify._replace_part_prose(control, prt, param_dict)
            if control.controls:
                for sub_control in control.controls:
                    if sub_control.parts:
                        for prt in sub_control.parts:
                            ProfileResolver.Modify._replace_part_prose(sub_control, prt, param_dict)

        @staticmethod
        def _add_to_parts_given_position(
            control_parts: List[common.Part], id_: str, new_parts: List[common.Part], position: prof.Position
        ) -> bool:
            """Add new elements at the given position."""
            if position in {prof.Position.after, prof.Position.before} and id_ is None:
                raise TrestleError('Reference ID (by_id) must be given when position is set to before or after.')
            for idx, child_part in enumerate(control_parts):
                if child_part.id == id_:
                    if not child_part.parts:
                        child_part.parts = []

                    if position == prof.Position.after:
                        for offset, new_part in enumerate(new_parts):
                            control_parts.insert(idx + 1 + offset, new_part)
                    elif position == prof.Position.before:
                        for offset, new_part in enumerate(new_parts):
                            control_parts.insert(idx + offset, new_part)
                    elif position == prof.Position.starting:
                        for offset, new_part in enumerate(new_parts):
                            child_part.parts.insert(offset, new_part)
                    elif position == prof.Position.ending:
                        child_part.parts.extend(new_parts)
                    else:
                        raise TrestleError(f'Add position not recognized: {position}')

                    return True
                else:
                    if child_part.parts is not None:
                        if ProfileResolver.Modify._add_to_parts_given_position(child_part.parts,
                                                                               id_,
                                                                               new_parts,
                                                                               position):
                            return True
            return False

        @staticmethod
        def _add_to_parts(
            control: cat.Control, id_: str, new_parts: List[common.Part], position: prof.Position
        ) -> None:
            """Find part in control and add to the specified position.

            Update the control with the new parts - otherwise error.
            """
            # handle simplest case first
            if position == prof.Position.starting and id_ is None:
                # add inside the control at the start
                for offset, new_part in enumerate(new_parts):
                    control.parts.insert(offset, new_part)
            elif position == prof.Position.ending and id_ is None:
                # add inside the control at the end
                if control.parts is None:
                    control.parts = new_parts
                else:
                    control.parts.extend(new_parts)
            else:
                # id is given, add by reference
                if control.parts is None:
                    if not new_parts:
                        return
                    control.parts = []
                if not ProfileResolver.Modify._add_to_parts_given_position(control.parts, id_, new_parts, position):
                    raise TrestleError(f'Unable to add parts for control {control.id} and part {id_} is not found.')

        @staticmethod
        def _add_to_list(
            input_list: Optional[List[OBT]],
            new: List[OBT],
            position: prof.Position,
            by_id: Optional[str] = None
        ) -> bool:
            """Add to a list based on a position, for the list or its direct sublist."""
            if input_list is None:
                input_list: List[OBT] = []
            if not by_id:
                if position == prof.Position.starting:
                    for offset, new_part in enumerate(new):
                        input_list.insert(offset, new_part)
                    return True
                elif position == prof.Position.ending:
                    input_list.extend(new)
                    return True
                raise TrestleError('Position argument must be starting or ending if ID is not provided')
            for index in range(len(input_list)):
                if input_list[index].id == by_id:
                    if position == prof.Position.after:
                        for offset, new_item in enumerate(new):
                            input_list.insert(index + 1 + offset, new_item)
                        return True
                    elif position == prof.Position.before:
                        for offset, new_item in enumerate(new):
                            input_list.insert(index + offset, new_item)
                        return True
            return False

        @staticmethod
        def _add_props_to_parts(parts: List[common.Part], add: prof.Add) -> bool:
            """
            Recursively add props to parts as required. In place operation.

            Assume the ID can either be of the part of a prop in the part.
            """
            # try on parts first
            updated = False
            for idx, part in enumerate(parts):
                if add.by_id == part.id:
                    updated = ProfileResolver.Modify._add_to_list(part.props, add.props, add.position)
                    if updated:
                        parts[idx] = part
                        return updated
                # Need to check here on empty lists being returned.
                if part.parts is not None:
                    updated = ProfileResolver.Modify._add_props_to_parts(part.parts, add)
                    # Add here as well
                    if updated:
                        parts[idx] = part
                        return updated
            return updated

        @staticmethod
        def _add_props_to_control(control: cat.Control, add: prof.Add) -> None:
            """Add the props to the control param by_id in the Add."""
            updated = False
            # Always default to ending.
            if add.position is None:
                add.position = prof.Position.ending
            if add.by_id == control.id:
                updated = ProfileResolver.Modify._add_to_list(control.props, add.props, add.position)
            else:
                # Try props in params
                if control.params:
                    for idx, param in enumerate(control.params):
                        if param.id == add.by_id:
                            updated = ProfileResolver.Modify._add_to_list(param.props, add.props, add.position)
                            if updated:
                                control.params[idx] = param
                                continue
                if control.parts and not updated:
                    updated = ProfileResolver.Modify._add_props_to_parts(control.parts, add)
            if not updated:
                # FIXME:
                logger.warning(f'Did not find the correct ID to add props for control {control.id} and id {add.by_id}')

        @staticmethod
        def _add_to_control(add: prof.Add, control: cat.Control) -> None:
            """Add altered parts and properties to the control."""
            if not add.parts and not add.props:
                raise TrestleError('Alter must add parts or props, however none were given.')

            # Add parts
            if add.parts is not None:
                if add.position is None:
                    logger.error(f'Add for parts has no position.  Defaulting to after for control {control.id}')
                    add.position = prof.Position.after
                ProfileResolver.Modify._add_to_parts(control, add.by_id, add.parts, add.position)

            # Add properties
            if add.props is not None:
                if add.by_id is not None:
                    ProfileResolver.Modify._add_props_to_control(control, add)
                elif not control.props:
                    control.props = []
                    control.props.extend(add.props)

        def _modify_controls(self, catalog: cat.Catalog) -> cat.Catalog:
            """Modify the controls based on the profile."""
            logger.debug(f'modify specify catalog {catalog.metadata.title} for profile {self._profile.metadata.title}')
            self._catalog_interface = CatalogInterface(catalog)
            param_dict: Dict[str, prof.SetParameter] = {}
            alters: Optional[List[prof.Alter]] = None
            # find the modify and alters
            # build a param_dict for all the modifys
            if self._profile.modify is not None:
                if self._profile.modify.set_parameters is not None:
                    param_list = self._profile.modify.set_parameters
                    for param in param_list:
                        param_dict[param.param_id] = param
                alters = self._profile.modify.alters

            if alters is not None:
                for alter in alters:
                    if alter.control_id is None:
                        raise TrestleError('Alters must have control id specified.')
                    if alter.removes is not None:
                        raise TrestleError('Alters not supported for removes.')
                    if alter.adds is None and not self._block_adds:
                        raise TrestleError('Alter has no adds to perform.')
                    if not self._block_adds:
                        for add in alter.adds:
                            if add.position is None and add.parts is not None:
                                msg = f'Alter/Add position is not specified in control {alter.control_id}'
                                msg += ' when adding part, so defaulting to after.'
                                logger.warning(msg)
                                add.position = prof.Position.after
                            control = self._catalog_interface.get_control(alter.control_id)
                            self._add_to_control(add, control)
                            self._catalog_interface.replace_control(control)
            # use the param_dict to apply all modifys
            control_ids = self._catalog_interface.get_control_ids()
            for control_id in control_ids:
                control = self._catalog_interface.get_control(control_id)
                if control.parts is not None:
                    for part in control.parts:
                        self._replace_part_prose(control, part, param_dict)
                self._catalog_interface.replace_control(control)

            catalog = self._catalog_interface._catalog

            # update the original profile metadata with new contents
            # roles and responsible-parties will be pulled in with new uuid's
            new_metadata = self._profile.metadata
            new_metadata.title = f'{catalog.metadata.title}: Resolved by profile {self._profile.metadata.title}'
            links: List[common.Link] = []
            for import_ in self._profile.imports:
                links.append(common.Link(**{'href': import_.href, 'rel': 'resolution-source'}))
            new_metadata.links = links
            # move catalog controls from dummy group 'catalog' into the catalog
            if catalog.groups:
                for group in catalog.groups:
                    if group.id == const.MODEL_TYPE_CATALOG:
                        catalog.controls = group.controls
                        catalog.groups = [group for group in catalog.groups if group.id != const.MODEL_TYPE_CATALOG]
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

        def __init__(self, trestle_root: pathlib.Path, import_: prof.Import, block_adds: bool = False) -> None:
            """Initialize and store trestle root for cache access."""
            self._trestle_root = trestle_root
            self._import = import_
            self._block_adds = block_adds

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
                    prune_filter = ProfileResolver.Prune(sub_import)
                    pipeline = Pipeline([import_filter, prune_filter])
                    pipelines.append(pipeline)
                    logger.debug(
                        f'sub_import add pipeline for sub href {sub_import.href} of main href {self._import.href}'
                    )
                merge_filter = ProfileResolver.Merge(profile)
                modify_filter = ProfileResolver.Modify(profile, self._block_adds)
                final_pipeline = Pipeline([merge_filter, modify_filter])
                yield next(final_pipeline.process(pipelines))

    @staticmethod
    def get_resolved_profile_catalog(
        trestle_root: pathlib.Path, profile_path: pathlib.Path, block_adds: bool = False
    ) -> cat.Catalog:
        """Create the resolved profile catalog given a profile path."""
        logger.debug(f'get resolved profile catalog for {profile_path} via generated Import.')
        import_ = prof.Import(href=str(profile_path), include_all={})
        import_filter = ProfileResolver.Import(trestle_root, import_, block_adds)
        logger.debug('launch pipeline')
        result = next(import_filter.process())
        return result
