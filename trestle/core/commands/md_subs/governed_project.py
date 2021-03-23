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
"""Trestle md governed-project sub-command."""
import argparse
import logging
import pathlib

import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core.commands.command_docs import CommandPlusDocs
logger = logging.getLogger(__name__)


class GovernedProject(CommandPlusDocs):
    """Markdown governed projects - enforcing requirements at the project level.

    Governed projects are executed as a special template leveraging the Governed-Folders template.
    """

    name = 'governed-projects'

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = fs.get_trestle_project_root(pathlib.Path.cwd())
        if not trestle_root:
            logger.error(f'Current working directory {pathlib.Path.cwd()} is not with a trestle project.')
            return 1
        if not fs.allowed_task_name(args.task_name):
            logger.error(
                f'Task name {args.task_name} is invalid as it interferes with OSCAL and trestle reserved names.'
            )
            return 1
        status = 1
        # setup governed projects instance:

        if args.mode == 'create-sample':
            status = self.create_sample(args.task_name, trestle_root)

        elif args.mode == 'template-validate':
            status = self.template_validate(args.task_name, trestle_root, args.governed_heading, args.header_validate)
        elif args.mode == 'setup':
            status = self.setup_template(args.task_name, trestle_root)
        elif args.mode == 'validate':
            # mode is validate
            status = self.validate(args.task_name, trestle_root, args.governed_heading, args.header_validate)
        else:
            logger.error('Unknown mode for trestle markdown functionality')
        return status

    def setup_template(self, trestle_root: pathlib.Path) -> int:
        """Create template for the governed project.

        Args:
            trestle_root: path of trestle root project.

        Returns:
            Unix return code.
        """
        pass
