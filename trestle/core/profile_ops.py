# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Profile operations - allows operations from profiles."""

from typing import List

import trestle.oscal.component as component
import trestle.oscal.profile as profile
import trestle.oscal.target as target


class ProfileOps:
    """ProfileOps manipulation of OSCAL object centered around profile."""

    def __init__(self, profile: profile.Profile) -> None:
        """Instanciate profile ops with a profile."""
        self.profile = profile

    def echo(self, voice: str) -> str:
        """Dumb test echo."""
        return voice

    def set_reference_targets(self, targets: List[target.TargetDefinition]) -> None:
        """Stuff."""
        self.targets = targets

    def naive_copy(self) -> component.ComponentDefinition:
        """Create a naive copy of a target into a component."""
        pass

    def copy_metadata(self, target_def: target.TargetDefinition) -> component.ComponentDefinition:
        """Copy metadata from target-definition into component-definition."""
        tdm = target_def.metadata

        comp_def = component.ComponentDefinition(metadata=tdm)
        return comp_def

    def create_component(self, filter_by_controls=True, filter_by_catalogs=True) -> component.ComponentDefinition:
        """Create a component definition referencing one or more targets and one profile."""
        pass
