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
from typing import Any, Dict, Iterable, List, Optional, Set, Union
from uuid import uuid4

import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.core.const import MARKDOWN_URL_REGEX, UUID_REGEX
from trestle.core.err import TrestleError
from trestle.core.pipeline import Pipeline
from trestle.core.remote import cache
from trestle.oscal import common

logger = logging.getLogger(__name__)


class ControlHandle():
    """Convenience class for handling controls as member of a group."""

    def __init__(self, group_id: str, group_title: str, group_class: str, control: cat.Control):
        """Initialize the control handle."""
        self.group_id = group_id
        self.group_title = group_title
        self.group_class = group_class
        self.control = control


class CatalogResolver():
    """Class to resolve a catalog given a profile."""

    class Prune(Pipeline.Filter):
        """Prune the catalog based on include rule."""

        def __init__(self, import_: prof.Import) -> None:
            """Inject the import."""
            self._import = import_

        def _get_controls(self, control_handle: ControlHandle,
                          control_dict: Dict[str, ControlHandle]) -> Dict[str, ControlHandle]:
            control_dict[control_handle.control.id] = control_handle
            if control_handle.control.controls is not None:
                group_id = control_handle.group_id
                group_title = control_handle.group_title
                group_class = control_handle.group_class
                for sub_control in control_handle.control.controls:
                    control_handle = ControlHandle(group_id, group_title, group_class, sub_control)
                    control_dict = self._get_controls(control_handle, control_dict)
            return control_dict

        def _prune_control(self, needed_ids: list[str], control: cat.Control, exclude_ids: List[str]) -> cat.Control:
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

        def _prune_controls(self, needed_controls: List[ControlHandle]) -> List[ControlHandle]:
            needed_ids = [control_handle.control.id for control_handle in needed_controls]
            exclude_ids = []
            final_controls: List[ControlHandle] = []
            for control_handle in needed_controls:
                if control_handle.control.id not in exclude_ids:
                    control_handle.control = self._prune_control(needed_ids, control_handle.control, exclude_ids)
                    exclude_ids.append(control_handle.control.id)
                    final_controls.append(control_handle)
            return final_controls

        def _find_uuid_refs(self, control: cat.Control) -> Set[str]:
            refs = set()
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
                        # currently only uuids used to confirm presence in backmatter
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
                    refs.update(self._find_uuid_refs(sub_control))
            return refs

        def _find_all_uuid_refs(self, needed_controls: List[ControlHandle]) -> Set[str]:
            # uuid refs can either be in links or prose.  find all needed by controls
            refs = set()
            for control_handle in needed_controls:
                refs.update(self._find_uuid_refs(control_handle.control))
            return refs

        def _prune_catalog(self, catalog: cat.Catalog) -> cat.Catalog:
            """Merge the controls with the current catalog based on the profile."""
            # build a convenience dictionary to access all catalog control handles by name
            control_dict: Dict[str, ControlHandle] = {}
            if catalog.groups is not None:
                for group in catalog.groups:
                    if group.controls is not None:
                        for control in group.controls:
                            control_handle = ControlHandle(group.id, group.title, group.class_, control)
                            control_dict = self._get_controls(control_handle, control_dict)

            # get list of control_ids needed by profile
            control_ids: List[str] = []
            if self._import.include_controls is not None:
                for include_control in self._import.include_controls:
                    new_ids = [withid.__root__ for withid in include_control.with_ids]
                    control_ids.extend(new_ids)
            else:
                control_ids = control_dict.keys()

            # get list of group id's and associated controls
            needed_group_ids: Set[str] = set()
            needed_controls: List[ControlHandle] = []
            for control_id in control_ids:
                control_handle = control_dict[control_id]
                needed_group_ids.add(control_handle.group_id)
                needed_controls.append(control_handle)

            # if a control includes controls - only include those that we know are needed
            final_controls: List[ControlHandle] = self._prune_controls(needed_controls)

            # find all referenced uuids - they should be 1:1 with those in backmatter
            needed_uuid_refs: Set[str] = self._find_all_uuid_refs(final_controls)

            # build the needed groups of controls
            group_dict: Dict[str, cat.Group] = {}
            for control_handle in final_controls:
                group_id = control_handle.group_id
                group = group_dict.get(group_id)
                if group is None:
                    group = cat.Group(
                        id=group_id,
                        title=control_handle.group_title,
                        class_=control_handle.group_class,
                        controls=[control_handle.control]
                    )
                    group_dict[group_id] = group
                else:
                    group_dict[group_id].controls.append(control_handle.control)

            # assemble the final resolved profile catalog

            # prune the list of resources to only those that are needed
            new_resources: List[common.Resource] = []
            for resource in catalog.back_matter.resources:
                if resource.uuid in needed_uuid_refs:
                    new_resources.append(resource)

            new_groups = list(group_dict.values())

            new_cat = cat.Catalog(
                uuid=str(uuid4()),
                metadata=catalog.metadata,
                back_matter=common.BackMatter(resources=new_resources),
                groups=new_groups
            )

            return new_cat

        def prune_catalog(self, catalog: cat.Catalog) -> cat.Catalog:
            """Just prune it and return catalog."""
            return self._prune_catalog(catalog)

        def process(self, models: Iterable[Union[cat.Catalog, prof.Profile]]) -> cat.Catalog:
            """Prune the catalog based on the include rule in import_."""
            for model in models:
                yield self._prune_catalog(model)

    class Merge(Pipeline.Filter):
        """Merge the incoming catalogs according to rules in the profile."""

        def __init__(self, profile) -> None:
            """Initialize the class with the profile."""
            self._profile: prof.Profile = profile

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

        def process(self, catalogs: Iterable[cat.Catalog]) -> cat.Catalog:
            """Merge the incoming catalogs based on the profile."""
            # this pulls from import and iterates over the incoming catalogs
            merged: Optional[cat.Catalog] = None
            for catalog in catalogs:
                merged = self._merge_catalog(merged, catalog)
            return merged

    class Modify(Pipeline.Filter):
        """Modify the controls based on the profile."""

        def __init__(self, profile: prof.Profile) -> None:
            """Initialize the filter."""
            self._profile = profile

        def _modify_controls(self, catalog: cat.Catalog) -> cat.Catalog:
            """Modify the controls based on the profile."""
            if False:
                if self._profile.modify is not None:
                    if self._profile.modify.set_parameters is not None:
                        param_list = self._profile.modify.set_parameters
                        self._param_dict = {}
                        for param in param_list:
                            self._param_dict[param.param_id] = param
                    self._alters = self._profile.modify.alters
                # update the original profile metadata with new contents
                # roles and responsible-parties will be pulled in with new uuid's
                new_metadata = self._profile.metadata
                new_metadata.title = f'{catalog.metadata.title}: Resolved by profile {self._profile.metadata.title}'
                new_metadata.links = [
                    common.Link(**{
                        'href': self._profile.imports[0].href, 'rel': 'resolution-source'
                    })
                ]

            return catalog

        def process(self, catalog: cat.Catalog) -> cat.Catalog:
            """Make the modifications to the controls based on the profile."""
            return self._modify_controls(catalog)

    class Import(Pipeline.Filter):
        """Profile filter class."""

        def __init__(self, trestle_root: pathlib.Path, import_: prof.Import) -> None:
            """Initialize and store trestle root for cache access."""
            self._trestle_root = trestle_root
            self._import = import_

        def process(self, import_: prof.Import, initializing=False) -> Any:
            """Load href for catalog or profile and yield each import as catalog imported its distinct pipeline."""
            fetcher = cache.FetcherFactory.get_fetcher(self._trestle_root, import_.href)

            model: Union[cat.Catalog, prof.Profile]
            model, model_type = fetcher.get_oscal()

            if model_type == 'catalog':
                # just yield a catalog for later pruning
                yield model
            else:
                if model_type != 'profile':
                    raise TrestleError(f'Improper model type {model_type} as profile import.')
                profile: prof.Profile = model

                # it is a profile, so yield each import into the pipeline to be merged as a catalog
                merge_filter = CatalogResolver.Merge(profile)
                modify_filter = CatalogResolver.Modify(profile)

                if initializing:
                    import_filter = CatalogResolver.Import(self._trestle_root, import_)
                    pipeline = Pipeline([import_filter, merge_filter, modify_filter])
                    yield pipeline.process(import_)

                for sub_import in profile.imports:
                    import_filter = CatalogResolver.Import(self._trestle_root, sub_import)
                    prune_filter = CatalogResolver.Prune(sub_import)
                    pipeline = Pipeline([import_filter, prune_filter, merge_filter, modify_filter])
                    yield pipeline.process(sub_import)

    @staticmethod
    def get_resolved_profile_catalog(trestle_root: pathlib.Path, profile_path: pathlib.Path) -> cat.Catalog:
        """Create the resolved profile catalog given a profile path."""
        import_ = prof.Import(href=str(profile_path), include_all={})
        import_filter = CatalogResolver.Import(trestle_root, import_)
        # the first time we just import the profile and launch pipelines from there
        result = next(import_filter.process(import_, True))
        return result
