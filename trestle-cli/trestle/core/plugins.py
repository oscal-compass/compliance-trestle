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
"""Plugin discovery code."""

import importlib
import inspect
import logging
import pathlib
import pkgutil
from typing import Any, Iterator, Tuple

logger = logging.getLogger(__name__)

_discovered_plugins = {
    name: importlib.import_module(name)
    for finder,
    name,
    ispkg in pkgutil.iter_modules()
    if name.startswith('trestle_')
}


def discovered_plugins(search_module: str) -> Iterator[Tuple[str, Any]]:
    """Yield discovered plugin classes within a given module name."""
    logger.debug(_discovered_plugins)
    # This block is uncovered as trestle cannot find plugins in it's unit tests - it is the base module.
    for plugin, value in _discovered_plugins.items():  # pragma: nocover
        for _, module, _ in pkgutil.iter_modules([pathlib.Path(value.__path__[0], search_module)]):
            logger.debug(module)
            plugin_module = importlib.import_module(f'{plugin}.{search_module}.{module}')
            clsmembers = inspect.getmembers(plugin_module, inspect.isclass)
            logger.debug(clsmembers)
            for _, plugin_cls in clsmembers:
                yield (plugin, plugin_cls)
