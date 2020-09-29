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
"""Element wrapper of an OSCAL model element."""

import yaml

from trestle.core.base_model import OscalBaseModel


class Element:
    """Element wrapper of an OSCAL model."""

    def __init__(self, elem: OscalBaseModel):
        """Initialize an element wrapper."""
        self._elem: OscalBaseModel = elem

    def get(self):
        """Get the element."""
        return self._elem

    def __str__(self):
        """Return string representation of element."""
        return f'{self._elem.__class__}'

    def to_yaml(self):
        """Convert into YAML string."""
        return yaml.dump(yaml.safe_load(self._elem.json(exclude_none=True, by_alias=True)))

    def to_json(self):
        """Convert into JSON string."""
        json_data = self._elem.json(exclude_none=True, by_alias=True, indent=4)
        return json_data


class ElementPath:
    """Element path wrapper of an element."""

    def __init__(self, element_path: str):
        """Initialize an element wrapper."""
        self._path: str = element_path

    def __str__(self):
        """Return string representation of element path."""
        return f'{self._path}'
