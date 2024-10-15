# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2024 The OSCAL Compass Authors.
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
"""Trestle core.jinja extension loading functionality."""
import functools
import logging
from typing import List

from trestle.core.jinja import filters, tags
from trestle.core.jinja.base import Extension, TrestleJinjaExtension
from trestle.core.plugins import discovered_plugins

logger = logging.getLogger(__name__)


@functools.cache
def extensions() -> List[Extension]:
    """Return list of Jinja extensions packaged with compliance-trestle and included from plugins."""
    extensions = [tags.MDSectionInclude, tags.MDCleanInclude, tags.MDDatestamp, filters.JinjaSSPFilters]
    # This block is uncovered as trestle cannot find plugins in it's unit tests - it is the base module.
    for plugin, ext_cls in discovered_plugins('jinja_ext'):  # pragma: nocover
        # add extensions (derived from TrestleJinjaExtension) to extensions list
        if issubclass(ext_cls, Extension):
            # don't add Extension or TrestleJinjaExtension
            if ext_cls is not TrestleJinjaExtension and ext_cls is not Extension:
                extensions.append(ext_cls)
                logger.info(f'{ext_cls} added to jinja extensions from plugin {plugin}')
    return extensions
