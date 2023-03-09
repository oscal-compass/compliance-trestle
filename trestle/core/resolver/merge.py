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
from typing import Iterator, List, Optional, Tuple, Union

import trestle.oscal.catalog as cat
import trestle.oscal.common as com
import trestle.oscal.profile as prof
from trestle.common.common_types import OBT
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_list, none_if_empty
from trestle.core.pipeline import Pipeline

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

    def _merge_lists(self, dest: List[OBT], src: List[OBT], merge_method: Optional[prof.Method]) -> None:
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
        self, dest: Union[OBT, List[OBT]], src: Union[OBT, List[OBT]], attr: str, merge_method: Optional[prof.Method]
    ) -> None:
        """Merge this attr of src into the attr of dest."""
        src_attr = getattr(src, attr, None)
        if src_attr is None:
            return
        item_type = type(src).__name__
        if attr in ITEM_EXCLUDE_MAP.get(item_type, []):
            return
        dest_attr = getattr(dest, attr, None)
        if dest_attr and isinstance(dest_attr, list):
            self._merge_lists(dest_attr, src_attr, merge_method)
            setattr(dest, attr, dest_attr)
            return
        if dest_attr and merge_method == prof.Method.use_first:
            return
        if dest_attr == src_attr and merge_method not in [None, prof.Method.keep]:
            return
        setattr(dest, attr, src_attr)

    def _merge_items(self, dest: OBT, src: OBT, merge_method: Optional[prof.Method]) -> None:
        """Merge two items recursively."""
        for field in src.__fields_set__:
            self._merge_attrs(dest, src, field, merge_method)

    def _group_contents(self, group: cat.Group) -> Tuple[List[cat.Control], List[com.Parameter]]:
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
        self, dest: cat.Catalog, src: cat.Catalog, merge_method: Optional[prof.Method], as_is: bool
    ) -> cat.Catalog:
        # merge_method is use_first, merge, keep
        # no combine or merge_method equates to merge_method=keep
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
                logger.debug('Profile has merge but no combine so defaulting to combine/merge.')
                merge_method = prof.Method.merge
            else:
                merge_combine = self._profile.merge.combine
                if merge_combine.method is None:
                    logger.debug('Profile has merge combine but no method.  Defaulting to merge.')
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
