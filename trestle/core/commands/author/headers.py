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
"""Trestle md governed-docs sub-command."""
import logging

import trestle.core.commands.author_subs.consts as author_const
from trestle.core.commands.command_docs import CommandPlusDocs

logger = logging.getLogger(__name__)


class Headers(CommandPlusDocs):
    """Enforce header / metadata across file types supported by author (markdown and drawio)."""

    name = 'headers'

    def _init_arguments(self) -> None:
        self.add_argument(
            author_const.recurse_short, author_const.recurse_long, help=author_const.recurse_help, action='store_true'
        )
        self.add_argument(author_const.mode_arg_name, choices=author_const.mode_choices)
        tn_help_str = 'The name of the the task to be governed.'\
            ''\
            'The template file is at .trestle/author/[task-name]/template.md'\
            'Note that by default this will automatically enforce the task.'

        self.add_argument(
            author_const.task_name_short, author_const.task_name_long, help=tn_help_str, required=True, type=str
        )        
        pass

    def _run(self, args: argparse.Namespace) -> int:
        pass