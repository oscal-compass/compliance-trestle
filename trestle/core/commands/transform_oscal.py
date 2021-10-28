# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Trestle transform command for oscal files."""
import argparse
import logging
import pathlib

import trestle.core.const as const
import trestle.utils.log as log
from trestle.core.commands.author.ssp import SSPFilter
from trestle.core.commands.command_docs import CommandPlusDocs

logger = logging.getLogger(__name__)


class TransformCmd(CommandPlusDocs):
    """Transform one oscal model into another based on model type and profile."""

    name = 'transform'

    def _init_arguments(self) -> None:
        self.add_argument('-t', '--type', help='Type of input model', choices=const.MODEL_TYPE_LIST, required=True)
        self.add_argument('-i', '--input', help='Name of input model', type=str, required=True)
        self.add_argument('-o', '--output', help='Name of output file', type=str, required=True)
        self.add_argument('-p', '--profile', help='Name of profile defining the transform', type=str, required=True)

    def _run(self, args: argparse.Namespace) -> int:
        logger.debug('Entering trestle transform.')
        log.set_log_level_from_args(args)
        trestle_root = args.trestle_root  # trestle root is set via command line in args. Default is cwd.

        return self.transform(trestle_root, args.type, args.input, args.output, args.profile)

    def transform(
        self, trestle_root: pathlib.Path, model_type: str, model_name: str, output_name: str, profile_name: str
    ) -> int:
        """Transform the input file based on the profile and infer the output type."""
        if model_type == const.MODEL_TYPE_SSP:
            ssp_filter = SSPFilter()
            return ssp_filter.filter_ssp(trestle_root, model_name, profile_name, output_name)
        logger.warning(f'Transform operation not available for model type {model_type}')
        return 1
