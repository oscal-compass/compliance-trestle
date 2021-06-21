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
"""Trestle command abstraction.

Improves parsing until such a point as ILCLI is fixed.
"""

import logging
import pathlib

from ilcli import Command

from trestle.utils import fs

logger = logging.getLogger(__name__)


class CommandPlusDocs(Command):
    """Linear extension to the ILCLI interface to use documentation string more."""

    def __init__(self, parser=None, parent=None, name=None, out=None, err=None) -> None:
        """Override default ILCLI behaviour to include class documentation in command help description."""
        super(CommandPlusDocs, self).__init__(parser, parent, name, out, err)
        self.parser.description = self.__doc__

    def _init_arguments(self):
        self.add_argument(
            '-tr', '--trestle-root', help='Path of trestle root dir', type=pathlib.Path, default=pathlib.Path.cwd()
        )

    def _validate_arguments(self, args):
        root = fs.get_trestle_project_root(args.trestle_root)
        if root is None:
            logger.error(f'Given directory {args.trestle_root} is not in a valid trestle root directory')
            return 1
        else:
            args.trestle_root = root
            return 0
