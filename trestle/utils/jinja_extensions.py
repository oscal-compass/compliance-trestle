# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Jinja extensions to manage conflicts with OSCAL variable substitutions."""
import re
import typing as t

from jinja2.ext import Extension


class OSCALTags(Extension):
    """
    This adds a pre-proccessing step to eliminate badly behaving OSCAL statements.

    Currently covering:
    {{ insert: param, param_id }} -> {{ param_id }}
    """

    priority = 1

    def preprocess(self, source: str, name: t.Optional[str], filename: t.Optional[str] = None) -> str:
        """Preprocess files with jinja eliminating OSCAL substitution structures."""
        staches = re.findall(r'{{.*?}}', source)
        if not staches:
            return source
        new_staches = []
        # clean the staches so they just have the param text
        for stache in staches:
            stache = stache.replace('insert: param,', '').strip()
            new_staches.append(stache)
        for i, _ in enumerate(staches):
            source = source.replace(staches[i], new_staches[i], 1)
        return source
