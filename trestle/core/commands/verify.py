# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2024 The OSCAL Compass Authors. All rights reserved.
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
"""Trestle Verify Command.

Verifies the detached cryptographic signature of an OSCAL JSON document,
reading the signature from a companion ``.sig`` file.

Usage examples::

    # Verify using the default companion .sig path
    trestle verify -f assessment-results.json -k public.pem

    # Verify with an explicit signature file path
    trestle verify -f ssp.json -k public.pem -s ssp.json.sig
"""

import argparse
import logging
import pathlib

import trestle.common.log as log
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.core import oscal_sign
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.common.return_codes import CmdReturnCodes

logger = logging.getLogger(__name__)


class VerifyCmd(CommandBase):
    """Verify the detached cryptographic signature on an OSCAL JSON document.

    Checks both the SHA-256 digest of the current document content and the
    cryptographic signature stored in the companion .sig file.  Exits with a
    non-zero status code if verification fails for any reason.
    """

    name = 'verify'

    def _init_arguments(self) -> None:
        self.add_argument(
            '-f', '--file', help='Path to the OSCAL JSON file to verify.', type=pathlib.Path, required=True
        )
        self.add_argument(
            '-k',
            '--key',
            help='Path to the PEM-encoded public key file corresponding to the signing key.',
            type=pathlib.Path,
            required=True,
        )
        self.add_argument(
            '-s',
            '--sig',
            help='Path to the .sig file.  Defaults to <file>.sig.',
            type=pathlib.Path,
            required=False,
            default=None,
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Execute the verify command."""
        try:
            log.set_log_level_from_args(args)

            oscal_path = args.file.resolve()
            key_path = args.key.resolve()
            sig_path = args.sig.resolve() if args.sig else None

            metadata = oscal_sign.verify_oscal_file(oscal_path=oscal_path, key_path=key_path, sig_path=sig_path)

            logger.info('SUCCESS: Signature verification PASSED.')
            if metadata:
                tool = metadata.get('tool', 'unknown')
                version = metadata.get('tool_version', '')
                logger.info(f'  Tool        : {tool} {version}'.rstrip())
                logger.info(f'  OSCAL model : {metadata.get("oscal_model", "unknown")}')
                logger.info(f'  Signed at   : {metadata.get("signed_at", "unknown")}')
                signer = metadata.get('signer', '')
                if signer:
                    logger.info(f'  Signer      : {signer}')

            return CmdReturnCodes.SUCCESS.value

        except TrestleError as e:
            logger.error(f'FAILED: Signature verification did not pass: {e}')
            return CmdReturnCodes.COMMAND_ERROR.value
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Unexpected error while verifying OSCAL file')
