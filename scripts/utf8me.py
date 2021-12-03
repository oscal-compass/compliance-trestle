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
"""Simple script for replacing non-utf8 characters."""

import argparse
import codecs
import logging
import pathlib

import ilcli

from trestle.core.commands.common.return_codes import CmdReturnCodes

logger = logging.getLogger(__name__)


class Utf8me(ilcli.Command):
    """Simple util to convert to utf8 destructively."""

    def _init_arguments(self) -> None:
        self.add_argument('input', nargs=1)
        self.add_argument('output', nargs='?', default=None)
        self.add_argument('-i', '--inplace', action='store_true')

    def _run(self, args: argparse.Namespace) -> int:
        outfile = args.input[0]
        if args.output:
            if args.inplace:
                logger.error('Output file cannot be named when attempting inplace write.')
                return CmdReturnCodes.COMMAND_ERROR.value
            outfile = args.output
        elif not args.inplace:
            logger.error('Either an output file or inplace replacement must be specified.')
            return CmdReturnCodes.COMMAND_ERROR.value

        input_path = pathlib.Path(args.input[0])
        if not input_path.is_file():
            logger.error('Input file does not exist or is a directory.')
        fh = codecs.open(str(input_path.resolve()), mode='r', encoding='utf8', errors='replace')
        content = fh.read()
        # Force flushing incase we are writing over the file)
        fh.flush()
        fh.close()
        output_file = pathlib.Path(outfile).resolve().open('w', encoding='utf8')
        output_file.write(content)
        output_file.flush()
        output_file.close()
        return CmdReturnCodes.SUCCESS.value


if __name__ == '__main__':
    exit(Utf8me().run())
