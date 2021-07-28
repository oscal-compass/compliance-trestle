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
"""Trestle Describe Command."""

import argparse
import logging
import pathlib

import trestle.utils.log as log
from trestle.core.commands.command_docs import CommandPlusDocs

logger = logging.getLogger(__name__)


class DescribeCmd(CommandPlusDocs):
    """Describe contents of a model file."""

    name = 'describe'

    def _init_arguments(self) -> None:
        logger.debug('Init arguments')
        self.add_argument('-f', '--file', help='OSCAL file to import.', type=str, required=True)

        self.add_argument(
            '-e', '--element', help='Optional name of element in file to describe.', type=str, required=True
        )

        self.add_argument(
            '-r', '--regenerate', action='store_true', help='Enable regeneration of uuids within the document'
        )

    def _run(self, args: argparse.Namespace) -> int:
        logger.debug('Entering trestle describe.')

        log.set_log_level_from_args(args)

        return self.describe(pathlib.Path.cwd())

    @classmethod
    def describe(cls, file_path: pathlib.Path) -> int:
        """Describe the contents of the file."""
        logger.debug(file_path)
        return 0
