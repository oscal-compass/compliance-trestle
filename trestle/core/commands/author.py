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

from trestle.core.commands.author_subs.cidd import CIDD
from trestle.core.commands.author_subs.docs import Docs
from trestle.core.commands.author_subs.folders import Folders
from trestle.core.commands.author_subs.headers import Headers
from trestle.core.commands.command_docs import CommandPlusDocs

logger = logging.getLogger(__name__)


class AuthorCmd(CommandPlusDocs):
    """trestle author, a collection of commands for authoring compliance content outside of OSCAL."""

    name = 'author'

    subcommands = [CIDD, Docs, Folders, Headers]

    def _init_arguments(self) -> None:
        heading_help = """Governed heading: Heading where for each line is a superset of the template's content."""
        self.add_argument('-gh', '--governed-heading', help=heading_help, default=None, type=str)
        header_help = """Validate that a yaml header provides the same keys as the template."""
        self.add_argument('-hv', '--header-validate', help=header_help, action='store_true')
        header_only_help = """Validate only the yaml header."""
        self.add_argument('-hov', '--header-only-validate', help=header_only_help, action='store_true')
        recurse_help = """Recurse and validate any subdirectories."""
        self.add_argument('-r', '--recurse', help=recurse_help, action='store_true')
        self.add_argument('mode', choices=['validate', 'template-validate', 'setup', 'create-sample'])
