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
"""Trestle Verify Manifest Command."""

import argparse
import logging
import pathlib

from trestle.common import log
from trestle.common.err import handle_generic_command_exception
from trestle.core.beta_features import beta_feature
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.signing import load_dsse_envelope, load_pem_public_key
from trestle.core.signing_manifest import load_signing_manifest, verify_manifest_envelope

logger = logging.getLogger(__name__)


class VerifyManifestCmd(CommandBase):
    """Verify a JSON package manifest against a detached DSSE envelope.

    Verification checks the package DSSE signature, validates the signed
    in-toto package Statement, and confirms every current JSON artifact digest
    matches the digest recorded in the signed manifest envelope.
    """

    name = 'verify-manifest'

    def _init_arguments(self) -> None:
        self.add_argument(
            '--manifest', help='Path to the JSON package manifest to verify.', required=True, type=pathlib.Path
        )
        self.add_argument(
            '--signature', help='Path to the detached DSSE package envelope.', required=True, type=pathlib.Path
        )
        self.add_argument(
            '--public-key', help='Path to the PEM public key for verification.', required=True, type=pathlib.Path
        )

    @beta_feature('json-manifest-signing')
    def _run(self, args: argparse.Namespace) -> int:
        """Verify a JSON package manifest."""
        try:
            log.set_log_level_from_args(args)
            self.verify_manifest(args.manifest, args.signature, args.public_key)
            return CmdReturnCodes.SUCCESS.value
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while verifying package manifest signature')

    @classmethod
    def verify_manifest(
        cls, manifest_path: pathlib.Path, signature_path: pathlib.Path, public_key_path: pathlib.Path
    ) -> None:
        """Verify a detached DSSE envelope for a JSON package manifest."""
        manifest = load_signing_manifest(manifest_path.resolve())
        public_key = load_pem_public_key(public_key_path.resolve())
        envelope = load_dsse_envelope(signature_path.resolve())
        verify_manifest_envelope(manifest, envelope, public_key)
