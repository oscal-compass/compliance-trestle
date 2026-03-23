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
"""Trestle Sign Command.

Signs an OSCAL JSON document with a detached cryptographic signature,
writing the signature envelope to a companion ``.sig`` file.

Usage examples::

    # Sign with an ECDSA P-256 private key
    trestle sign -f assessment-results.json -k private.pem

    # Sign and specify the output path and signer identity
    trestle sign -f ssp.json -k private.pem -o ssp.json.sig --signer ci-pipeline

    # Sign with an RSA private key
    trestle sign -f catalog.json -k rsa_private.pem
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


class SignCmd(CommandBase):
    """Sign an OSCAL JSON document with a detached cryptographic signature.

    Produces a companion .sig file containing the signature envelope.  The
    original OSCAL document is NOT modified.  Supports ECDSA (P-256) and
    RSA-PSS private keys in PEM format.
    """

    name = 'sign'

    def _init_arguments(self) -> None:
        self.add_argument('-f', '--file', help='Path to the OSCAL JSON file to sign.', type=pathlib.Path, required=True)
        self.add_argument(
            '-k',
            '--key',
            help='Path to the PEM-encoded private key file (ECDSA P-256 or RSA).',
            type=pathlib.Path,
            required=True,
        )
        self.add_argument(
            '-o',
            '--output',
            help='Destination path for the .sig file.  Defaults to <file>.sig.',
            type=pathlib.Path,
            required=False,
            default=None,
        )
        self.add_argument(
            '--signer',
            help='Optional human-readable signer identity embedded in metadata (e.g. an email address or CI job name).',
            type=str,
            required=False,
            default=None,
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Execute the sign command."""
        try:
            log.set_log_level_from_args(args)

            oscal_path = args.file.resolve()
            key_path = args.key.resolve()
            sig_path = args.output.resolve() if args.output else None

            sig_file = oscal_sign.sign_oscal_file(
                oscal_path=oscal_path, key_path=key_path, sig_path=sig_path, signer=args.signer
            )

            logger.info(f'SUCCESS: Signature written to {sig_file}')
            return CmdReturnCodes.SUCCESS.value

        except TrestleError as e:
            logger.error(f'Error signing OSCAL file: {e}')
            return CmdReturnCodes.COMMAND_ERROR.value
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Unexpected error while signing OSCAL file')
