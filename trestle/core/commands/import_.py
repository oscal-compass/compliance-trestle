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
"""Trestle Import Command."""
import argparse
import pathlib

from ilcli import Command  # type: ignore

from trestle.utils import fs
from trestle.utils import log

logger = log.get_logger()


class ImportCmd(Command):
    """Import an existing full OSCAL model into the trestle project."""

    # The line above comes with the doc string
    name = 'import'

    def _init_arguments(self) -> None:
        logger.debug('Init arguments')
        self.add_argument('-f', '--file', help='OSCAL file to import.', type=str, required=True)

        self.add_argument('-o', '--output', help='Name of output project.', type=str, required=True)

        self.add_argument(
            '-r', '--regenerate', type=bool, default=False, help='Enable to regenerate uuids within the document'
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Top level import run command."""
        logger.debug('Entering import run.')

        # Validate input arguments are as expected.
        if len(args.file) == 0:
            logger.error('trestle import requires a file to be provided with -f or --file.')
            return 1

        input_file = pathlib.Path(args.file)
        if not input_file.exists():
            logger.error(f'Input file {args.file} does not exist.')
            return 1

        cwd = pathlib.Path.cwd().resolve()
        trestle_root = fs.get_trestle_project_root(cwd)
        if trestle_root is None:
            # TODO: I think this should probably be handled as an exception not a none check.
            logger.error(f'Current working directory: {cwd} is not within a trestle project.')
            return 1

        # Ensure file is not in trestle dir
        trestle_root = trestle_root.resolve()
        try:
            input_file.relative_to(trestle_root)
        except Exception:
            logger.error('Input file cannot be from current trestle project. Use duplicate instead.')
            return 1

        # peek at file to get typing information.

        # throw errors on bad loads

        #
        return 0
