# -*- mode:python; coding:utf-8 -*-

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
"""Transformer helper functions."""
from typing import Any
from typing import Dict
from typing import List

from trestle.oscal.assessment_results import Observation
from trestle.oscal.common import Property

_segment_separator = '|'


class PropertyAccounting():
    """Property accounting class.

    Help transformers do accounting.

    > Each time a new record is processed the transformer calls count_group.
    > For each attribute on that record, the transformer calls count_property.
      - If the property already exactly exists, then its count is incremented.
      - Otherwise, a new entry is made and the count for that property is set to 1.
    > When the transformer wants to know if a property (name, value, ns, and class)
      is common to all records for the group, is_common_property is employed to check
      that the number of records in the group is equal to the number of duplicates
      there are for the property. If equal, then the property is common.
    """

    def __init__(self) -> None:
        """Initialize."""
        self._group_map: Dict[str, int] = {}
        self._property_map: Dict[str, Dict[str:int]] = {}

    def count_group(self, group: str = None) -> None:
        """Group accounting."""
        if group not in self._group_map:
            self._group_map[group] = 0
        self._group_map[group] += 1

    def count_property(
        self, group: str = None, name: str = None, value: str = None, class_: str = None, ns: str = None
    ) -> None:
        """Property accounting."""
        key = _segment_separator.join([str(name), str(value), str(class_), str(ns)])
        if group not in self._property_map:
            self._property_map[group] = {}
        if key not in self._property_map[group]:
            self._property_map[group][key] = 0
        self._property_map[group][key] += 1

    def is_common_property(
        self, group: str = None, name: str = None, value: str = None, class_: str = None, ns: str = None
    ) -> bool:
        """Check for common property."""
        rval = False
        key = _segment_separator.join([str(name), str(value), str(class_), str(ns)])
        if group in self._group_map and key in self._property_map[group]:
            rval = self._group_map[group] == self._property_map[group][key]
        return rval


class PropertyManager():
    """Property manager class.

    Help transformer manage properties.

    > Use materialize to: fetch a property from cache (if caching), else create a new
      property instance and keep in cache (if caching).
    > Use put_common_property to: keep common properties for each group.
    > Use get_common_properties to: recall the list of common properties for the group.
    """

    def __init__(self, caching: bool = True, checking: bool = False) -> None:
        """Initialize."""
        self._caching = caching
        self._checking = checking
        self._requests = 0
        self._hits = 0
        self._map_unique: Dict[str, Any] = {}
        self._map_common: Dict[str, Dict[str, Property]] = {}

    @property
    def requests(self) -> int:
        """Cache requests."""
        return self._requests

    @property
    def hits(self) -> int:
        """Cache hits."""
        return self._hits

    def materialize(self, name: str = None, value: str = None, class_: str = None, ns: str = None) -> Property:
        """Get property from cache or create new property."""
        self._requests += 1
        # try fetch from cache
        key = _segment_separator.join([str(name), str(value), str(class_), str(ns)])
        if key in self._map_unique:
            self._hits += 1
            return self._map_unique[key]
        # create new property and put into cache if caching
        prop = self._create(name=name, value=value, class_=class_, ns=ns)
        if self._caching:
            self._map_unique[key] = prop
        return prop

    def put_common_property(
        self, group: str = None, name: str = None, value: str = None, class_: str = None, ns: str = None
    ) -> Property:
        """Remember common property."""
        if group not in self._map_common:
            self._map_common[group] = {}
        key = _segment_separator.join([str(name), str(value), str(class_), str(ns)])
        if key not in self._map_common[group]:
            prop = self.materialize(name, value, class_, ns)
            self._map_common[group][key] = prop

    def get_common_properties(self, group: str = None) -> List[Property]:
        """Recall common properties for the group."""
        rval = None
        if group in self._map_common:
            rval = list(self._map_common[group].values())
        return rval

    def _create(self, name: str = None, value: str = None, class_: str = None, ns: str = None) -> Property:
        """Create new property."""
        if self._checking:
            return Property(name=name, value=value, class_=class_, ns=ns)
        return Property.construct(name=name, value=value, class_=class_, ns=ns)


class TransformerHelper():
    """OSCAL transformer helper."""

    def remove_common_observation_properties(self, observations: List[Observation]) -> List[Property]:
        """Remove common observation properties."""
        common_props = []
        props = {}
        # count each property occurrence in each observation
        props_occurrence_counts = self._get_property_occurrence_counts(observations)
        # remove common properties from observation
        for key in props_occurrence_counts.keys():
            # skip property if not identical for each and every observation
            if props_occurrence_counts[key] != len(observations):
                continue
            # remove property from each observation and keep one instance
            for observation in observations:
                for prop in observation.props:
                    if key == f'{prop.name}:{prop.value}:{prop.class_}':
                        props[key] = prop
                        observation.props.remove(prop)
                        break
        # formulate list of removed properties
        for key in props.keys():
            common_props.append(props[key])
        # return list of removed properties
        return common_props

    def _get_property_occurrence_counts(self, observations: List[Observation]):
        """Count each property occurrence in each observation."""
        property_occurences = {}
        for observation in observations:
            for prop in observation.props:
                key = f'{prop.name}:{prop.value}:{prop.class_}'
                if key not in property_occurences.keys():
                    property_occurences[key] = 0
                property_occurences[key] += 1
        return property_occurences
