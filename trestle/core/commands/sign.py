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
"""Trestle Sign Command."""

import argparse
import logging
import pathlib
from typing import Optional

from trestle.common import log
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.signing import create_oscal_provenance_envelope, load_pem_private_key_signer, write_dsse_envelope

logger = logging.getLogger(__name__)


class SignCmd(CommandBase):
    """Sign an OSCAL JSON file as a detached DSSE provenance envelope.

    This command does not modify the input OSCAL file. It reads the JSON
    bytes, canonicalizes them using RFC 8785, computes a SHA-256 digest over
    the canonical JSON, and records that digest in an in-toto Statement. The
    Statement is then signed as a DSSE payload using the provided PEM private
    key and written as a detached sidecar envelope.

    The optional subject name is the name recorded in the in-toto Statement.
    If it is omitted, the input file name is used. Verification must use the
    same subject name when one was provided during signing.
    """

    name = 'sign'

    def _init_arguments(self) -> None:
        self.add_argument('-f', '--file', help='Path to the OSCAL JSON file to sign.', required=True, type=pathlib.Path)
        self.add_argument('--key', help='Path to the PEM private key for signing.', required=True, type=pathlib.Path)
        self.add_argument('-o', '--output', help='Output DSSE envelope file.', required=True, type=pathlib.Path)
        self.add_argument(
            '--subject-name',
            help='Subject name to record in the in-toto Statement. Defaults to the input file name.',
            default=None,
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Sign an OSCAL JSON file."""
        try:
            log.set_log_level_from_args(args)
            self.sign(args.file, args.key, args.output, args.subject_name)
            return CmdReturnCodes.SUCCESS.value
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while signing OSCAL JSON')

    @classmethod
    def sign(
        cls,
        input_path: pathlib.Path,
        key_path: pathlib.Path,
        output_path: pathlib.Path,
        subject_name: Optional[str] = None,
    ) -> None:
        """Write a detached DSSE provenance envelope for an OSCAL JSON file."""
        input_path = input_path.resolve()
        output_path = output_path.resolve()
        if input_path == output_path:
            raise TrestleError('DSSE output path must be different from input OSCAL JSON file.')

        signer = load_pem_private_key_signer(key_path.resolve())
        envelope = create_oscal_provenance_envelope(input_path, signer, subject_name)
        write_dsse_envelope(envelope, output_path)
