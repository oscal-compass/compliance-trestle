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
import traceback

import trestle.core.const as const
import trestle.utils.log as log
from trestle.core.commands.author.ssp import SSPFilter
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.profile_resolver import ProfileResolver
from trestle.oscal.profile import Profile
from trestle.utils import fs

logger = logging.getLogger(__name__)


class TransformCmd(CommandPlusDocs):
    """
    Transform an oscal model or models by filtering or aggregation.

    This is a prototype class for basic transform operations.  It is currently not included in the command
    line interface.  But if a number of transforms are needed in the future, this class can host the additional
    transforms in an extensible manner.
    """

    name = 'transform'

    def _init_arguments(self) -> None:
        self.add_argument('-t', '--type', help='Input model type', choices=const.MODEL_TYPE_LIST, required=True)
        self.add_argument('-tf', '--transform', help='Type of transform', choices=const.TRANSFORM_TYPES, required=True)
        self.add_argument(
            '-tb',
            '--transform-by',
            type=str,
            help='Model name or comma-separated item names used in the transform',
            required=False,
            default=''
        )
        self.add_argument('-i', '--input', help='Name of input model', type=str, required=True)
        self.add_argument('-o', '--output', help='Name of output model or directory', type=str, required=True)
        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)

    def _run(self, args: argparse.Namespace) -> int:
        logger.debug('Entering trestle transform.')
        log.set_log_level_from_args(args)
        trestle_root = args.trestle_root  # trestle root is set via command line in args. Default is cwd.

        try:
            return self.transform(
                trestle_root, args.type, args.transform, args.input, args.transform_by, args.output, args.regenerate
            )
        except Exception as e:
            logger.error(f'The transform operation failed with error: {e}')
            logger.debug(traceback.format_exc())
            return CmdReturnCodes.COMMAND_ERROR.value

    def transform(
        self,
        trestle_root: pathlib.Path,
        model_type: str,
        transform: str,
        input_name: str,
        transform_by: str,
        output_name: str,
        regenerate: bool
    ) -> int:
        """Transform the input file based on the profile and infer the output type."""
        if model_type == const.MODEL_TYPE_SSP:
            # anticipate more transform options here - switch to factory if it gets busy
            if transform == const.FILTER_BY_PROFILE:
                if not transform_by:
                    logger.warning('A profile name must be provided for transform-by in the command.')
                    return CmdReturnCodes.COMMAND_ERROR.value
                ssp_filter = SSPFilter()
                return ssp_filter.filter_ssp(trestle_root, input_name, transform_by, output_name, regenerate)
        elif model_type == const.MODEL_TYPE_PROFILE:
            # anticipate more transform options here
            if transform == const.GENERATE_RESOLVED_CATALOG:
                profile_path = fs.full_path_for_top_level_model(trestle_root, input_name, Profile)
                resolved_catalog = ProfileResolver.get_resolved_profile_catalog(trestle_root, profile_path)
                file_type = fs.FileContentType.path_to_content_type(profile_path)
                fs.save_top_level_model(resolved_catalog, trestle_root, output_name, file_type)
                return CmdReturnCodes.SUCCESS.value
        logger.warning(f'Transform operation not available for transform type {transform} and model type {model_type}')
        return CmdReturnCodes.COMMAND_ERROR.value
