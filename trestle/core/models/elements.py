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

from trestle.core.base_model import OscalBaseModel

import yaml


class ElementPath:
    """Element path wrapper of an element."""

    PATH_SEPARATOR: str = '.'

    def __init__(self, element_path: str):
        """Initialize an element wrapper."""
        self._path: list[str] = element_path.split(self.PATH_SEPARATOR)

    def get(self) -> list:
        """Return the path components as a list."""
        return self._path

    def __str__(self):
        """Return string representation of element path."""
        return self.PATH_SEPARATOR.join(self._path)


class Element:
    """Element wrapper of an OSCAL model."""

    def __init__(self, elem: OscalBaseModel):
        """Initialize an element wrapper."""
        self._elem: OscalBaseModel = elem

    def get(self, element_path: ElementPath = None):
        """Get the element."""
        if element_path is None:
            return self._elem

        # return the sub-element at the specified path
        elm = self._elem
        for attr in element_path.get():
            elm = getattr(elm, attr, None)
            if elm is None:
                raise AttributeError(f'Element does not exists at path "{element_path}"')

        return elm

    def __str__(self):
        """Return string representation of element."""
        return type(self._elem).__name__

    def to_yaml(self):
        """Convert into YAML string."""
        return yaml.dump(yaml.safe_load(self._elem.json(exclude_none=True, by_alias=True)))

    def to_json(self):
        """Convert into JSON string."""
        json_data = self._elem.json(exclude_none=True, by_alias=True, indent=4)
        return json_data
