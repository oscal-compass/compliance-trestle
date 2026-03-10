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
"""Trestle canonicalize command.

Produces the RFC 8785 (JSON Canonicalization Scheme) representation of an
OSCAL JSON document.  The canonical form is deterministic and suitable as a
pre-image for cryptographic signatures.

Usage examples::

    # Write JCS output to stdout
    trestle canonicalize -f catalogs/mycatalog/catalog.json

    # Write JCS output to a file
    trestle canonicalize -f catalogs/mycatalog/catalog.json -o canonical.json
"""

import argparse
import logging
import pathlib
import sys

from trestle.common import log
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes

logger = logging.getLogger(__name__)


class CanonicalizeCmd(CommandPlusDocs):
    """Output the RFC 8785 (JCS) canonical JSON form of an OSCAL document.

    Reads any OSCAL JSON file from the current trestle workspace and writes
    its RFC 8785 canonical representation.  The output is compact, has all
    object keys sorted by their UTF-16 code-unit sequence, and contains no
    insignificant whitespace — making it suitable as a stable pre-image for
    cryptographic signing.

    YAML and XML documents are out of scope for canonicalization.
    """

    name = 'canonicalize'

    def _init_arguments(self) -> None:
        self.add_argument(
            '-f',
            '--file',
            help='Path to the OSCAL JSON file to canonicalize (relative to the trestle root).',
            type=pathlib.Path,
            required=True,
        )
        self.add_argument(
            '-o',
            '--output',
            help='Output file path for the canonical JSON.  If omitted the result is written to stdout.',
            type=pathlib.Path,
            default=None,
        )

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root: pathlib.Path = args.trestle_root

            input_path = pathlib.Path(args.file)
            if not input_path.is_absolute():
                input_path = trestle_root / input_path

            if not input_path.exists():
                raise TrestleError(f'File not found: {input_path}')

            if input_path.suffix.lower() in ('.yaml', '.yml'):
                raise TrestleError(
                    'Canonicalization is only supported for JSON files (RFC 8785). '
                    'YAML is out of scope per issue #2013.'
                )

            logger.debug(f'Loading OSCAL model from {input_path}')
            _, _, oscal_object = ModelUtils.load_distributed(input_path, trestle_root)

            if oscal_object is None:
                raise TrestleError(f'Could not load OSCAL model from {input_path}')

            jcs_bytes = oscal_object.oscal_serialize_jcs()

            if args.output is None:
                # Write to stdout as UTF-8 text
                sys.stdout.buffer.write(jcs_bytes)
                sys.stdout.buffer.write(b'\n')
            else:
                out_path = pathlib.Path(args.output)
                if not out_path.is_absolute():
                    out_path = trestle_root / out_path
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(jcs_bytes)
                logger.info(f'Canonical JSON written to {out_path}')

            return CmdReturnCodes.SUCCESS.value

        except Exception as e:
            return handle_generic_command_exception(e, logger, 'Error while canonicalizing OSCAL file')
