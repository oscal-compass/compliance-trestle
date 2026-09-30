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
"""Trestle Generate Manifest Command."""

import argparse
import logging
import pathlib
from typing import List, Optional

from trestle.common import log
from trestle.common.err import handle_generic_command_exception
from trestle.common.list_utils import comma_sep_to_list
from trestle.core.beta_features import beta_feature
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.signing_manifest_discovery import discover_signing_manifest, write_signing_manifest

logger = logging.getLogger(__name__)


class GenerateManifestCmd(CommandBase):
    """Generate a JSON package manifest from a primary OSCAL model.

    The command follows local and remote dependencies from any supported
    top-level OSCAL JSON model. Remote dependencies are fetched through Trestle
    and copied into the package. Catalogs are terminal artifacts. Additional
    supported models may be explicitly included. The generated manifest can be
    reviewed before it is passed to sign-manifest.
    """

    name = 'generate-manifest'

    def _init_arguments(self) -> None:
        self.add_argument(
            '-f', '--file', help='Path to the supported primary OSCAL JSON file.', required=True, type=pathlib.Path
        )
        self.add_argument(
            '--include',
            help='Optional comma-separated OSCAL JSON files to include when they cannot be discovered.',
            default=None,
        )
        self.add_argument(
            '--allow-private-uris', help='Allow dependencies hosted on trusted private networks.', action='store_true'
        )
        self.add_argument('--overwrite', help='Replace an existing output manifest.', action='store_true')
        self.add_argument('-o', '--output', help='Output JSON package manifest.', required=True, type=pathlib.Path)

    @beta_feature('json-manifest-signing')
    def _run(self, args: argparse.Namespace) -> int:
        """Generate a JSON package manifest."""
        try:
            log.set_log_level_from_args(args)
            self.generate_manifest(args.file, args.output, args.include, args.allow_private_uris, args.overwrite)
            return CmdReturnCodes.SUCCESS.value
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while generating package manifest')

    @classmethod
    def generate_manifest(
        cls,
        primary_path: pathlib.Path,
        output_path: pathlib.Path,
        include: Optional[str] = None,
        allow_private_uris: bool = False,
        overwrite: bool = False,
    ) -> None:
        """Discover OSCAL dependencies and write a package manifest."""
        include_paths: List[pathlib.Path] = [pathlib.Path(path) for path in comma_sep_to_list(include)]
        manifest = discover_signing_manifest(primary_path, output_path, include_paths, allow_private_uris)
        write_signing_manifest(manifest, overwrite)
