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


class Element:
    """Element wrapper of an OSCAL model."""

    def __init__(self, element_type: str, element_alias: str, data: dict):
        """Initialize an element wrapper."""
        self._type: str = element_type
        self._alias: str = element_alias
        self._data: dict = data

    def validate():
        """Validate the element."""


class ElementPath:
    """Element path wrapper of an element."""

    def __init__(self, element_path: str):
        """Initialize an element wrapper."""
        self._path: str = element_path
