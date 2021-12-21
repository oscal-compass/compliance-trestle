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
"""
Trestle author command.

Umbrella command for all markdown related transformations
"""
import logging

from trestle.core.commands.author.catalog import CatalogAssemble, CatalogGenerate
from trestle.core.commands.author.docs import Docs
from trestle.core.commands.author.folders import Folders
from trestle.core.commands.author.headers import Headers
from trestle.core.commands.author.jinja import JinjaCmd
from trestle.core.commands.author.profile import ProfileAssemble, ProfileGenerate
from trestle.core.commands.author.ssp import SSPAssemble, SSPFilter, SSPGenerate
from trestle.core.commands.command_docs import CommandPlusDocs

logger = logging.getLogger(__name__)


class AuthorCmd(CommandPlusDocs):
    """trestle author, a collection of commands for authoring compliance content outside of OSCAL."""

    name = 'author'

    subcommands = [
        CatalogAssemble,
        CatalogGenerate,
        Docs,
        Folders,
        Headers,
        JinjaCmd,
        ProfileAssemble,
        ProfileGenerate,
        SSPAssemble,
        SSPFilter,
        SSPGenerate
    ]
