# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Create ssp from catalog and profile."""

import logging
import pathlib
import re
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union
from uuid import uuid4

from pydantic import BaseModel

import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.core.const import MARKDOWN_URL_REGEX, UUID_REGEX
from trestle.core.err import TrestleError
from trestle.core.pipeline import Pipeline
from trestle.core.remote import cache
from trestle.oscal import common

logger = logging.getLogger(__name__)


class PathNode(BaseModel):
    """Node in path to control in catalog."""

    id_: str
    is_control: bool


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
        path: List[PathNode]
        control: cat.Control

    def __init__(self, catalog: cat.Catalog) -> None:
        """Initialize the interface with the catalog."""
        self._catalog = catalog
        self._control_dict = self._create_control_dict()

    def _add_sub_controls(
        self, control_handle: ControlHandle, control_dict: Dict[str, ControlHandle], path: List[PathNode]
    ) -> None:
        """Get all controls contained in this control and add it to the growing dict."""
        # then add all its sub-controls to the dict recursively
        if control_handle.control.controls:
            group_id = control_handle.group_id
            group_title = control_handle.group_title
            group_class = control_handle.group_class
            for sub_control in control_handle.control.controls:
                new_path = path[:]
                new_path.append(PathNode(id_=sub_control.id, is_control=True))
                control_handle = CatalogInterface.ControlHandle(
                    group_id=group_id,
                    group_title=group_title,
                    group_class=group_class,
                    path=new_path,
                    control=sub_control
                )
                control_dict[sub_control.id] = control_handle
                self._add_sub_controls(control_handle, control_dict, new_path)

    def _add_group_controls(
        self, group: cat.Group, control_dict: Dict[str, ControlHandle], path: List[PathNode]
    ) -> None:
        if group.controls is not None:
            group_path = path[:]
            group_path.append(PathNode(id_=group.id, is_control=False))
            for control in group.controls:
                new_path = group_path[:]
                new_path.append(PathNode(id_=control.id, is_control=True))
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
            group_path.append(PathNode(id_=group.id, is_control=False))
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
            group_path = [PathNode(id_='catalog', is_control=False)]
            for control in self._catalog.controls:
                new_path = group_path[:]
                new_path.append(PathNode(id_=control.id, is_control=True))
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
        # return the list of all controls in this group
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

    def get_all_controls(self, recurse: bool) -> cat.Control:
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

    def get_path(self, control_id: str) -> List[PathNode]:
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
                new_groups.append(self._update_all_controls_in_group(sub_group))
            group.groups = new_groups

    def update_catalog_with_dict(self):
        """Update the actual catalog with changes made to the dict."""
        if self._catalog.groups:
            new_groups: List[cat.Group] = []
            for group in self._catalog.groups:
                self._update_all_controls_in_group(group)
                new_groups.append(group)
            self._catalog.groups = new_groups
        if self._catalog.controls:
            self._catalog.controls = self._update_all_controls_in_list(self._catalog.controls)

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
        if False:
            if control.controls:
                for con in control.controls:
                    hits.extend(self.find_string_in_control(con, seek_str))
        return hits

    def find_string_in_all_controls_prose(self, seek_str: str) -> List[Tuple[str, str]]:
        """Find all instances of this string in catalog prose and return with control id."""
        hits: List[Tuple[str, str]] = []
        for control in self.get_all_controls(True):
            hits.extend(self.find_string_in_control(control, seek_str))
        return hits


class ProfileResolver():
    """Class to resolve a catalog given a profile."""

    class Prune(Pipeline.Filter):
        """Prune the catalog based on the import include rule."""

        def __init__(self, import_: prof.Import) -> None:
            """Inject the import."""
            # This needs to be created prior to knowing the catalog.
            self._import: prof.Import = import_
            self._catalog_interface: Optional[CatalogInterface] = None
            self._catalog: Optional[cat.Catalog] = None

        def _set_catalog(self, catalog: cat.Catalog) -> None:
            """Set the catalog used by the catalog interface."""
            self._catalog_interface = CatalogInterface(catalog)
            self._catalog = catalog

        def _find_uuid_refs(self, control_id: str) -> Set[str]:
            # find all needed resource refs buried in control links and prose
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
            # uuid refs can either be in links or prose.  find all needed by controls
            refs = set()
            for control_id in needed_control_ids:
                refs.update(self._find_uuid_refs(control_id))
            return refs

        def _find_needed_control_ids(self) -> List[str]:
            # get list of control_ids needed by profile and corresponding groups
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
            # this is only called if the control is needed
            # but some or all of its sub_controls may not be needed
            # this always returns the original control, possibly with fewer subcontrols
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
            """Merge the controls with the current catalog based on the profile."""
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
            new_resources: List[common.Resource] = []
            if self._catalog.back_matter is not None and self._catalog.back_matter.resources is not None:
                for resource in self._catalog.back_matter.resources:
                    if resource.uuid in needed_uuid_refs:
                        new_resources.append(resource)

            new_groups = list(group_dict.values())

            if new_resources and new_groups:
                new_cat = cat.Catalog(
                    uuid=str(uuid4()),
                    metadata=self._catalog.metadata,
                    back_matter=common.BackMatter(resources=new_resources),
                    groups=new_groups
                )
            elif new_resources:
                new_cat = cat.Catalog(
                    uuid=str(uuid4()),
                    metadata=self._catalog.metadata,
                    back_matter=common.BackMatter(resources=new_resources)
                )
            elif new_groups:
                new_cat = cat.Catalog(uuid=str(uuid4()), metadata=self._catalog.metadata, groups=new_groups)
            else:
                new_cat = cat.Catalog(uuid=str(uuid4()), metadata=self._catalog.metadata)

            return new_cat

        def process(self, catalog_iter: Iterable[cat.Catalog]) -> cat.Catalog:
            """Prune the catalog based on the include rule in the import_."""
            # this only processes the one catalog yielded by the one import in this pipeline.
            # it must yield in order to have the merge filter loop over available imported catalogs.
            self._set_catalog(next(catalog_iter))
            logger.debug(f'prune yielding catalog {self._catalog.metadata.title} with import {self._import.href}')
            yield self._prune_catalog()

    class Merge(Pipeline.Filter):
        """Merge the incoming catalogs according to rules in the profile."""

        def __init__(self, profile: prof.Profile) -> None:
            """Initialize the class with the profile."""
            logger.debug('merge filter initialize')
            self._profile = profile

        def _merge_catalog(self, merged: cat.Catalog, catalog: cat.Catalog) -> cat.Catalog:
            if merged is None:
                return catalog
            if catalog.groups is not None:
                for group in catalog.groups:
                    if group.id not in [g.id for g in merged.groups]:
                        merged.groups.append(cat.Group(id=group.id, controls=[]))
                    index = [g.id for g in merged.groups].index(group.id)
                    merged.groups[index].controls.extend(group.controls)
            return merged

        def process(self, pipelines: List[Pipeline]) -> cat.Catalog:
            """Merge the incoming catalogs."""
            # this pulls from import and iterates over the incoming catalogs
            merged: Optional[cat.Catalog] = None
            logger.debug(f'merge entering process with {len(pipelines)} pipelines')
            for pipeline in pipelines:
                catalog = next(pipeline.process(None))
                merged = self._merge_catalog(merged, catalog)
            yield merged

    class Modify(Pipeline.Filter):
        """Modify the controls based on the profile."""

        def __init__(self, profile: prof.Profile) -> None:
            """Initialize the filter."""
            self._profile = profile
            self._catalog_interface: Optional[CatalogInterface] = None
            logger.debug(f'modify initialize filter with profile {profile.metadata.title}')

        def _replace_params(self, text: str, control: cat.Control, param_dict: Dict[str, prof.SetParameter]) -> str:
            # replace params in control prose with assignments for this control from the profile or description info
            if control.params is not None:
                for param in control.params:
                    # set default if no information available for text
                    param_text = f'[{param.id} = no description available]'
                    set_param = param_dict.get(param.id, None)
                    # param value provided so just replace it
                    if set_param is not None:
                        values = [value.__root__ for value in set_param.values]
                        param_text = values[0] if len(values) == 1 else f"[{', '.join(values)}]"
                    else:
                        # if select present, use it
                        if param.select is not None:
                            param_text = '['
                            if param.select.how_many is not None:
                                param_text += f'{param.select.how_many.value}: '
                            if param.select.choice is not None:
                                param_text += ', '.join(param.select.choice)
                            param_text = f'{param_text}]'
                        # else use the label
                        if param.label is not None:
                            param_text = f'[{param.label}]'
                    # this needs to be a regex match to distinguish param_1 from param_10
                    pattern = re.compile(f'{param.id}(?:[^0-9a-zA-Z._\-#@])')
                    text = pattern.sub(param_text, text)

            # strip {{ }}
            pattern = re.compile('( *{{| *}})')
            text = pattern.sub('', text)
            text = text.replace('insert: param, ', '').strip()

            return text

        def _replace_part_prose(
            self, control: cat.Control, part: common.Part, param_dict: Dict[str, prof.SetParameter]
        ) -> None:
            # for a part in a control replace the params using the _param_dict
            if part.prose is not None:
                fixed_prose = self._replace_params(part.prose, control, param_dict)
                # change the prose in the control itself
                part.prose = fixed_prose
            if part.parts is not None:
                for prt in part.parts:
                    self._replace_part_prose(control, prt, param_dict)
            if control.controls:
                for sub_control in control.controls:
                    if sub_control.parts:
                        for prt in sub_control.parts:
                            self._replace_part_prose(sub_control, prt, param_dict)

        def _add_to_part(self, part: common.Part, id_: str, new_parts: List[common.Part]) -> bool:
            if part.id == id_:
                if not part.parts:
                    part.parts = []
                part.parts.extend(new_parts)
                return True
            if part.parts is not None:
                for ii, part in enumerate(part.parts):
                    if self._add_to_part(part, id_, new_parts):
                        part.parts[ii] = part
                        return True
            return False

        def _add_to_parts(self, control: cat.Control, id_: str, new_parts: List[common.Part]) -> None:
            """Find part in control and add to end of its list of parts."""
            # Update the control with the new parts - otherwise error
            for ii, part in enumerate(control.parts):
                if self._add_to_part(part, id_, new_parts):
                    control.parts[ii] = part
                    return True
            raise TrestleError(f'Unable to add parts for control {control.id} and part {id_}')

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
                    if alter.adds is None:
                        raise TrestleError('Alter has no adds to perform.')
                    for add in alter.adds:
                        if add.position is not None and add.position.name is not None and add.position.name != 'after':
                            raise TrestleError('Alter position must be "after" or None.')
                        control = self._catalog_interface.get_control(alter.control_id)
                        if add.by_id is not None:
                            self._add_to_parts(control, add.by_id, add.parts)
                            self._catalog_interface.replace_control(control)
                            continue
                        if add.props is not None:
                            if add.by_id is not None:
                                TrestleError('Alter cannot add props by id.')
                            if not control.props:
                                control.props = []
                            control.props.extend(add.props)
                            continue
                        TrestleError('Alter must either add parts or props')

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
            catalog.metadata = new_metadata
            return catalog

        def process(self, catalog_iter: Iterable[cat.Catalog]) -> cat.Catalog:
            """Make the modifications to the controls based on the profile."""
            catalog = next(catalog_iter)
            logger.debug(
                f'modify process with catalog {catalog.metadata.title} using profile {self._profile.metadata.title}'
            )
            yield self._modify_controls(catalog)

    class Import(Pipeline.Filter):
        """Profile filter class."""

        def __init__(self, trestle_root: pathlib.Path, import_: prof.Import) -> None:
            """Initialize and store trestle root for cache access."""
            self._trestle_root = trestle_root
            self._import = import_

        def process(self, input_=None) -> Any:
            """Load href for catalog or profile and yield each import as catalog imported by its distinct pipeline."""
            logger.debug(f'import entering process with href {self._import.href}')
            fetcher = cache.FetcherFactory.get_fetcher(self._trestle_root, self._import.href)

            model: Union[cat.Catalog, prof.Profile]
            model, model_type = fetcher.get_oscal()

            if model_type == 'catalog':
                logger.debug(f'DIRECT YIELD in import of catalog {model.metadata.title}')
                yield model
            else:
                if model_type != 'profile':
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
                modify_filter = ProfileResolver.Modify(profile)
                final_pipeline = Pipeline([merge_filter, modify_filter])
                yield next(final_pipeline.process(pipelines))

    @staticmethod
    def get_resolved_profile_catalog(trestle_root: pathlib.Path, profile_path: pathlib.Path) -> cat.Catalog:
        """Create the resolved profile catalog given a profile path."""
        logger.debug(f'get resolved profile catalog for {profile_path} via generated Import.')
        import_ = prof.Import(href=str(profile_path), include_all={})
        import_filter = ProfileResolver.Import(trestle_root, import_)
        logger.debug('launch pipeline')
        result = next(import_filter.process())
        return result
