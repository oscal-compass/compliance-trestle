# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""AuthorCommonCommands - reusable utilities to increase code base abstraction for author command."""
import argparse
import logging
import pathlib

import trestle.core.const as const
import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core.commands.command_docs import CommandPlusDocs

logger = logging.getLogger(__name__)


class AuthorCommonCommand(CommandPlusDocs):
    """Extension for the subset of commands that operate using the common mode structure."""

    trestle_root: pathlib.Path

    task_name: str

    def _initialize(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        # Externalize
        self.trestle_root = fs.get_trestle_project_root(pathlib.Path.cwd())
        if not self.trestle_root:
            logger.error(f'Current working directory {pathlib.Path.cwd()} is not within a trestle project.')
            return 1

        self.task_name = args.task_name
        if self.task_name:
            self.task_path = self.trestle_root / self.task_name
            self.template_dir = self.trestle_root / const.TRESTLE_CONFIG_DIR / 'author' / self.task_name
            if not fs.allowed_task_name(self.task_name):
                logger.error(
                    f'Task name {self.task_name} is invalid as it interferes with OSCAL and trestle reserved names.'
                )
                return 1
        try:
            self.global_ = args.__getattribute__('global')
        except AttributeError:
            self.global_ = None
        if self.global_:
            self.template_dir = self.trestle_root / const.TRESTLE_CONFIG_DIR / 'author' / '__global__'

        return 0

    def rel_dir(self, path: pathlib.Path) -> str:
        """Stringify a directory relative to trestle root."""
        return str(path.relative_to(self.trestle_root))
