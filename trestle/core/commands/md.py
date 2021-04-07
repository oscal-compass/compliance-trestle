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
"""
Trestle MD command.

Umbrella command for all markdown related transformations
"""
import logging

from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.md_subs.cidd import CIDD
from trestle.core.commands.md_subs.governed_docs import GovernedDocs
from trestle.core.commands.md_subs.governed_folders import GovernedFolders

logger = logging.getLogger(__name__)


class MDCmd(CommandPlusDocs):
    """trestle md, a collection of commands for managing markdown objects related to compliance."""

    name = 'md'

    subcommands = [CIDD, GovernedDocs, GovernedFolders]

    def _init_arguments(self) -> None:
        heading_help = """Governed heading: Heading where for each line is a superset of the template's content."""
        self.add_argument('-gh', '--governed-heading', help=heading_help, default=None, type=str)
        header_help = """Validate that a yaml header provides the same keys as the template."""
        self.add_argument('-hv', '--header-validate', help=header_help, action='store_true')
        self.add_argument('mode', choices=['validate', 'template-validate', 'setup', 'create-sample'])
