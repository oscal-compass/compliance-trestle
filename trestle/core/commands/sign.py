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
import os
import pathlib
from typing import Optional

from trestle.common import log
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.core.beta_features import beta_feature
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.signing import create_oscal_provenance_envelope, load_pem_private_key_signer, write_dsse_envelope

logger = logging.getLogger(__name__)


class SignCmd(CommandBase):
    """Sign a JSON file as a detached DSSE provenance envelope.

    This command does not modify the input JSON file. It reads the JSON
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
        self.add_argument('-f', '--file', help='Path to the JSON file to sign.', required=True, type=pathlib.Path)
        self.add_argument(
            '--private-key',
            dest='key',
            help='Path to the PEM private key for signing.',
            required=True,
            type=pathlib.Path,
        )
        self.add_argument(
            '--key-password-env',
            help='Environment variable containing the password for an encrypted PEM private key.',
            default=None,
        )
        self.add_argument('-o', '--output', help='Output DSSE envelope file.', required=True, type=pathlib.Path)
        self.add_argument('--overwrite', help='Replace an existing DSSE envelope.', action='store_true')
        self.add_argument(
            '--subject-name',
            help='Subject name to record in the in-toto Statement. Defaults to the input file name.',
            default=None,
        )

    @beta_feature('json-signing')
    def _run(self, args: argparse.Namespace) -> int:
        """Sign a JSON file."""
        try:
            log.set_log_level_from_args(args)
            self.sign(args.file, args.key, args.output, args.subject_name, args.key_password_env, args.overwrite)
            return CmdReturnCodes.SUCCESS.value
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while signing JSON')

    @classmethod
    def sign(
        cls,
        input_path: pathlib.Path,
        key_path: pathlib.Path,
        output_path: pathlib.Path,
        subject_name: Optional[str] = None,
        key_password_env: Optional[str] = None,
        overwrite: bool = False,
    ) -> None:
        """Write a detached DSSE provenance envelope for a JSON file."""
        input_path = input_path.resolve()
        key_path = key_path.resolve()
        resolved_output_path = output_path.resolve()
        if input_path == resolved_output_path:
            raise TrestleError('DSSE output path must be different from input JSON file.')
        if key_path == resolved_output_path:
            raise TrestleError('DSSE output path must be different from private key file.')

        key_password = None
        if key_password_env is not None:
            if key_password_env not in os.environ:
                raise TrestleError(f'Key password environment variable is not set: {key_password_env}')
            key_password = os.environ[key_password_env]

        signer = load_pem_private_key_signer(key_path, key_password)
        envelope = create_oscal_provenance_envelope(input_path, signer, subject_name)
        write_dsse_envelope(envelope, output_path, overwrite)
