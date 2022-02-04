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

from typing import List

from trestle.oscal.assessment_results import Observation
from trestle.oscal.common import Property


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
