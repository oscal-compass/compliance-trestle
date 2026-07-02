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
"""Trestle Verify Command."""

import argparse
import logging
import pathlib
from typing import Optional

from trestle.common import log
from trestle.common.err import handle_generic_command_exception
from trestle.core.beta_features import beta_feature
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.signing import load_dsse_envelope, load_pem_public_key, verify_oscal_provenance_envelope

logger = logging.getLogger(__name__)


class VerifyCmd(CommandBase):
    """Verify a JSON file against a detached DSSE provenance envelope.

    Verification performs two checks. First, it verifies the DSSE signature
    over the DSSE pre-authentication encoding for the in-toto Statement payload
    using the provided PEM public key. Second, it canonicalizes the input JSON
    using RFC 8785, computes its SHA-256 digest, and confirms that the
    digest matches the subject digest recorded in the signed Statement.

    Both checks are required: the digest proves the file matches the signed
    subject, and the DSSE signature proves the Statement was signed by the
    corresponding private key. If the envelope was signed with a custom subject
    name, pass that same value with --subject-name.
    """

    name = 'verify'

    def _init_arguments(self) -> None:
        self.add_argument('-f', '--file', help='Path to the JSON file to verify.', required=True, type=pathlib.Path)
        self.add_argument('--signature', help='Path to the detached DSSE envelope.', required=True, type=pathlib.Path)
        self.add_argument(
            '--key', help='Path to the PEM public key for verification.', required=True, type=pathlib.Path
        )
        self.add_argument(
            '--subject-name',
            help='Subject name expected in the in-toto Statement. Defaults to the input file name.',
            default=None,
        )

    @beta_feature('json-signing')
    def _run(self, args: argparse.Namespace) -> int:
        """Verify a JSON file."""
        try:
            log.set_log_level_from_args(args)
            self.verify(args.file, args.signature, args.key, args.subject_name)
            return CmdReturnCodes.SUCCESS.value
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while verifying JSON signature')

    @classmethod
    def verify(
        cls,
        input_path: pathlib.Path,
        signature_path: pathlib.Path,
        key_path: pathlib.Path,
        subject_name: Optional[str] = None,
    ) -> None:
        """Verify a detached DSSE provenance envelope for a JSON file."""
        public_key = load_pem_public_key(key_path.resolve())
        envelope = load_dsse_envelope(signature_path.resolve())
        verify_oscal_provenance_envelope(input_path.resolve(), envelope, public_key, subject_name)
