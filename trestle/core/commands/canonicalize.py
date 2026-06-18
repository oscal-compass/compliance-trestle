# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2026 The OSCAL Compass Authors. All rights reserved.
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
"""Trestle Canonicalize Command."""

import argparse
import logging
import pathlib
import sys
from typing import Optional

from trestle.common import log
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.core.canonicalization import load_canonical_json_file
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.common.return_codes import CmdReturnCodes

logger = logging.getLogger(__name__)


class CanonicalizeCmd(CommandBase):
    """Canonicalize a JSON document using RFC 8785.

    This command reads the raw JSON input directly and writes canonical JSON
    bytes. It is designed for OSCAL artifacts, but it does not load the input
    through OSCAL models and can canonicalize any valid JSON document.
    """

    name = 'canonicalize'

    def _init_arguments(self) -> None:
        self.add_argument(
            '-f', '--file', help='Path to the JSON document to canonicalize.', required=True, type=pathlib.Path
        )
        self.add_argument(
            '-o',
            '--output',
            help='Output file for canonical JSON. If omitted, output is written to stdout.',
            type=pathlib.Path,
            default=None,
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Canonicalize a JSON document."""
        try:
            log.set_log_level_from_args(args)
            self.canonicalize(args.file, args.output)
            return CmdReturnCodes.SUCCESS.value
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while canonicalizing JSON')

    @classmethod
    def canonicalize(cls, input_path: pathlib.Path, output_path: Optional[pathlib.Path] = None) -> None:
        """Write RFC 8785 canonical JSON bytes for input_path to output_path or stdout."""
        input_path = input_path.resolve()
        if input_path.suffix.lower() != '.json':
            raise TrestleError('Canonicalization is only supported for JSON files.')

        _, canonical_bytes = load_canonical_json_file(input_path)

        if output_path is None:
            cls._write_stdout(canonical_bytes)
            return

        output_path = output_path.resolve()
        if output_path.exists() and output_path.is_dir():
            raise TrestleError(f'Canonical JSON output path is a directory: {output_path}')

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(canonical_bytes)

    @staticmethod
    def _write_stdout(canonical_bytes: bytes) -> None:
        """Write canonical bytes to stdout."""
        try:
            sys.stdout.buffer.write(canonical_bytes)
        except AttributeError:
            sys.stdout.write(canonical_bytes.decode())
