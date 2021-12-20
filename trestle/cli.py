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
"""Starting point for the Trestle CLI."""

import importlib
import inspect
import logging
import pathlib
import pkgutil

from trestle.core import const
from trestle.core.commands.add import AddCmd
from trestle.core.commands.assemble import AssembleCmd
from trestle.core.commands.author.command import AuthorCmd
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.create import CreateCmd
from trestle.core.commands.describe import DescribeCmd
from trestle.core.commands.href import HrefCmd
from trestle.core.commands.import_ import ImportCmd
from trestle.core.commands.init import InitCmd
from trestle.core.commands.merge import MergeCmd
from trestle.core.commands.partial_object_validate import PartialObjectValidate
from trestle.core.commands.remove import RemoveCmd
from trestle.core.commands.replicate import ReplicateCmd
from trestle.core.commands.split import SplitCmd
from trestle.core.commands.task import TaskCmd
from trestle.core.commands.validate import ValidateCmd
from trestle.core.commands.version import VersionCmd
from trestle.utils import log

logger = logging.getLogger('trestle')


class Trestle(CommandBase):
    """Manage OSCAL files in a human friendly manner."""

    subcommands = [
        AddCmd,
        AssembleCmd,
        AuthorCmd,
        CreateCmd,
        DescribeCmd,
        HrefCmd,
        ImportCmd,
        InitCmd,
        MergeCmd,
        PartialObjectValidate,
        RemoveCmd,
        ReplicateCmd,
        SplitCmd,
        TaskCmd,
        ValidateCmd,
        VersionCmd
    ]

    discovered_plugins = {
        name: importlib.import_module(name)
        for finder,
        name,
        ispkg in pkgutil.iter_modules()
        if name.startswith('trestle_')
    }

    logger.debug(discovered_plugins)
    # This block is uncovered as trestle cannot find plugins in it's unit tests - it is the base module.
    for plugin, value in discovered_plugins.items():  # pragma: nocover
        for _, module, _ in pkgutil.iter_modules([pathlib.Path(value.__path__[0], 'commands')]):
            logger.debug(module)
            command_module = importlib.import_module(f'{plugin}.commands.{module}')
            clsmembers = inspect.getmembers(command_module, inspect.isclass)
            logger.debug(clsmembers)
            for _, cmd_cls in clsmembers:
                # add commands (derived from CommandPlusDocs or CommandBase) to subcommands list
                if issubclass(cmd_cls, CommandBase):
                    # don't add CommandPlusDocs or CommandBase
                    if cmd_cls is not CommandPlusDocs and cmd_cls is not CommandBase:
                        subcommands.append(cmd_cls)
                        logger.info(f'{cmd_cls} added to subcommands from plugin {plugin}')

    def _init_arguments(self) -> None:
        self.add_argument('-v', '--verbose', help=const.DISPLAY_VERBOSE_OUTPUT, action='count', default=0)
        self.add_argument(
            '-tr', '--trestle-root', help='Path of trestle root dir', type=pathlib.Path, default=pathlib.Path.cwd()
        )


def run() -> None:
    """Run the trestle cli."""
    log.set_global_logging_levels()
    logger.debug('Main entry point.')

    exit(Trestle().run())
