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

import argparse
from typing import Any, Dict


class ObjectFactory:
    """Allow registration and creation of factory objects."""

    def __init__(self) -> None:
        """Initialize the objects dictionary as empty."""
        self._objects: Dict[str, Any] = {}

    def register_object(self, mode: str, obj: Any) -> None:
        """Register the object."""
        self._objects[mode] = obj

    def get(self, args: argparse.Namespace) -> Any:
        """Create the object from the args."""
        return self._objects.get(args.mode)
