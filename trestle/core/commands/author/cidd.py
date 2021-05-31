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
"""Trestle md CIDD sub-command."""
import argparse
import logging
import pathlib

import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core.commands.command_docs import CommandPlusDocs

logger = logging.getLogger(__name__)


class CIDD(CommandPlusDocs):
    """
    Control Information Description Document management.

    Control descriptions are a critical reviewable component of the compliance lifecycle - and are typically managed by
    *ISO teams. This command supports a set of actions for writing control descriptions as markdown and assembling into
    an SSP-like construct.

    Insert notes w.r.t. spreadsheet templates format (control family, control-id, information , current description?)
    """

    name = 'cidd'

    def _init_arguments(self) -> None:
        self.add_argument('--pave', action='store_true', help='Create tree of control templates')
        self.add_argument('--cidd', default=None, help='Create Control Implementation Description Document')
        self.add_argument('--parse', action='store_true', help='Parse templates')
        # Add as appropriate
        # catalog(s) should be addressed by name assuming the 800-53 content is in the trestle directory tree.
        # May need to simplify the model for spreadsheets.

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = fs.get_trestle_project_root(pathlib.Path.cwd())
        if not trestle_root:
            logger.error(f'Current working directory {pathlib.Path.cwd()} is not with a trestle project.')
            return 1
        logger.info(f'Are we paving? {args.pave}')

        logger.debug('Done')
        return 0
