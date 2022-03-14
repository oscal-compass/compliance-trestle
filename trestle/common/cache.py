# -*- mode:python; coding:utf-8 -*-
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
"""Cached objects."""
from trestle.oscal.common import Property


class CacheBase():
    """Cache base class."""

    def __init__(self, caching: bool = True, checking: bool = False) -> None:
        """Initialize."""
        self._caching = caching
        self._checking = checking
        self._requests = 0
        self._hits = 0
        self._map = {}

    @property
    def requests(self) -> int:
        """Cache requests."""
        return self._requests

    @property
    def hits(self) -> int:
        """Cache hits."""
        return self._hits


class CacheProperties(CacheBase):
    """Creator and cache of Property objects."""

    def __init__(self, caching: bool = True, checking: bool = False) -> None:
        """Initialize."""
        super().__init__(caching, checking)

    def get(self, name: str, value: str, class_: str = None, ns: str = None) -> Property:
        """Get property from cache or create new property."""
        self._requests += 1
        # try fetch from cache
        key = str(name) + '|' + str(value) + '|' + str(class_) + '|' + str(ns)
        if key in self._map.keys():
            self._hits += 1
            return self._map[key]
        # create new property and put into cache if caching
        prop = self._create(name=name, value=value, class_=class_, ns=ns)
        if self._caching:
            self._map[key] = prop
        return prop

    def _create(self, name: str, value: str, class_: str, ns: str) -> Property:
        """Create new property."""
        if self._checking:
            return Property(name=name, value=value, class_=class_, ns=ns)
        return Property.construct(name=name, value=value, class_=class_, ns=ns)
