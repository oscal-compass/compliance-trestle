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
"""Starting point for the Trestle CLI."""
import logging
import pathlib

from trestle.core.commands.add import AddCmd
from trestle.core.commands.assemble import AssembleCmd
from trestle.core.commands.author.command import AuthorCmd
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


class Trestle(CommandPlusDocs):
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

    def _init_arguments(self) -> None:
        self.add_argument('-v', '--verbose', help='Display verbose output.', action='count', default=0)
        self.add_argument(
            '-tr', '--trestle-root', help='Path of trestle root dir', type=pathlib.Path, default=pathlib.Path.cwd()
        )


def run() -> None:
    """Run the trestle cli."""
    log.set_global_logging_levels()
    logger.debug('Main entry point.')

    exit(Trestle().run())
