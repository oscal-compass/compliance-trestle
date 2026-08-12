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
"""Trestle Sign Manifest Command."""

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
from trestle.core.signing import load_pem_private_key_signer, write_dsse_envelope
from trestle.core.signing_manifest import create_manifest_envelope, load_signing_manifest

logger = logging.getLogger(__name__)


class SignManifestCmd(CommandBase):
    """Sign a JSON package manifest as a detached DSSE envelope.

    The manifest lists local JSON artifacts that belong to a package. This
    command canonicalizes each listed JSON artifact with RFC 8785, records each
    SHA-256 digest in an in-toto Statement, signs the Statement using the
    provided PEM private key, and writes the detached package envelope.
    """

    name = 'sign-manifest'

    def _init_arguments(self) -> None:
        self.add_argument(
            '--manifest', help='Path to the JSON package manifest to sign.', required=True, type=pathlib.Path
        )
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
        self.add_argument('-o', '--output', help='Output DSSE package envelope file.', required=True, type=pathlib.Path)
        self.add_argument('--overwrite', help='Replace an existing DSSE package envelope.', action='store_true')

    @beta_feature('json-manifest-signing')
    def _run(self, args: argparse.Namespace) -> int:
        """Sign a JSON package manifest."""
        try:
            log.set_log_level_from_args(args)
            self.sign_manifest(args.manifest, args.key, args.output, args.key_password_env, args.overwrite)
            return CmdReturnCodes.SUCCESS.value
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while signing package manifest')

    @classmethod
    def sign_manifest(
        cls,
        manifest_path: pathlib.Path,
        key_path: pathlib.Path,
        output_path: pathlib.Path,
        key_password_env: Optional[str] = None,
        overwrite: bool = False,
    ) -> None:
        """Write a detached DSSE envelope for a JSON package manifest."""
        manifest_path = manifest_path.resolve()
        key_path = key_path.resolve()
        resolved_output_path = output_path.resolve()
        if manifest_path == resolved_output_path:
            raise TrestleError('DSSE output path must be different from package manifest file.')
        if key_path == resolved_output_path:
            raise TrestleError('DSSE output path must be different from private key file.')

        key_password = None
        if key_password_env is not None:
            if key_password_env not in os.environ:
                raise TrestleError(f'Key password environment variable is not set: {key_password_env}')
            key_password = os.environ[key_password_env]

        signer = load_pem_private_key_signer(key_path, key_password)
        manifest = load_signing_manifest(manifest_path)
        envelope = create_manifest_envelope(manifest, signer)
        write_dsse_envelope(envelope, output_path, overwrite)
