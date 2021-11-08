# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""AuthorCommonCommands - reusable utilities to increase code base abstraction for author command."""
import argparse
import logging
import pathlib

import trestle.utils.fs as fs
import trestle.utils.log as log
from trestle.core.commands.author.consts import TRESTLE_RESOURCES
from trestle.core.commands.author.versioning.template_versioning import TemplateVersioning
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.const import TRESTLE_CONFIG_DIR

logger = logging.getLogger(__name__)


class AuthorCommonCommand(CommandPlusDocs):
    """Extension for the subset of commands that operate using the common mode structure."""

    trestle_root: pathlib.Path

    task_name: str

    def _initialize(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        # Externalize
        self.trestle_root = args.trestle_root
        self.task_name = args.task_name

        try:
            self.global_ = args.__getattribute__('global')
        except AttributeError:
            self.global_ = None

        _, all_versions = TemplateVersioning.get_versioned_template_resource(TRESTLE_RESOURCES)
        if args.template_version is None:
            args.template_version = max(all_versions)
        elif args.template_version and args.template_version is not all_versions:
            logger.error('Specified template version is invalid, please select other version.')
            return 1

        if not self.global_ and self.task_name is None:
            logger.error('At least a global flag or a task name should be provided.')
            return 1
        if self.global_:
            old_template_dir = self.trestle_root / TRESTLE_CONFIG_DIR / 'author' / '__global__'
            self.template_dir = old_template_dir / args.template_version
        elif self.task_name and not self.global_:
            old_template_dir = self.trestle_root / TRESTLE_CONFIG_DIR / 'author' / self.task_name
            self.template_dir = old_template_dir / args.template_version
        if self.task_name:
            self.task_path = self.trestle_root / self.task_name
            if not fs.allowed_task_name(self.task_name):
                logger.error(
                    f'Task name {self.task_name} is invalid as it interferes with OSCAL and trestle reserved names.'
                )
                return 1

        if old_template_dir.exists():
            TemplateVersioning.validate_template_folder(old_template_dir)
            self.template_dir = TemplateVersioning.update_template_folder_structure(old_template_dir)

        return 0

    def rel_dir(self, path: pathlib.Path) -> str:
        """Stringify a directory relative to trestle root."""
        return str(path.relative_to(self.trestle_root))
