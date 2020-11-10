# -*- mode:python; coding:utf-8 -*-

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
"""Generic object factory."""

from typing import Any, Dict


class ObjectFactory:
    """Allow registration and creation of validators."""

    def __init__(self) -> None:
        """Initialize the builders dictionary as empty."""
        self._builders: Dict[str, Any] = {}

    def register_builder(self, key: str, builder: Any) -> None:
        """Register the builder."""
        self._builders[key] = builder

    def create(self, key: str, **kwargs: Dict[str, Any]) -> Any:
        """Create the builder."""
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)
