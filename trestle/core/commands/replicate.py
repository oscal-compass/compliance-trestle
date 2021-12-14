# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Trestle Replicate Command."""
import argparse
import logging
import traceback

from trestle.core import const
from trestle.core import validator_helper
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs
from trestle.utils import log
from trestle.utils.load_distributed import load_distributed

logger = logging.getLogger(__name__)


class ReplicateCmd(CommandPlusDocs):
    """Replicate a top level model within the trestle directory structure."""

    name = 'replicate'

    def _init_arguments(self) -> None:
        logger.debug('Init arguments')

        self.add_argument('model', help='Choose OSCAL model', choices=const.MODEL_TYPE_LIST)
        self.add_argument('-n', '--name', help='Name of model to replicate.', type=str, required=True)

        self.add_argument('-o', '--output', help='Name of replicated model.', type=str, required=True)

        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)

    def _run(self, args: argparse.Namespace) -> int:
        """Execute and process the args."""
        try:
            log.set_log_level_from_args(args)
            return self.replicate_object(args.model, args)
        except TrestleError as e:
            logger.debug(traceback.format_exc())
            logger.error(f'Error while replicating model: {e}')
            return CmdReturnCodes.COMMAND_ERROR.value
        except Exception as e:  # pragma: no cover
            logger.debug(traceback.format_exc())
            logger.error(f'Unexpected error while replicating model: {e}')
            return CmdReturnCodes.UNKNOWN_ERROR.value

    @classmethod
    def replicate_object(cls, model_alias: str, args: argparse.Namespace) -> int:
        """
        Core replicate routine invoked by subcommands.

        Args:
            model_alias: Name of the top level model in the trestle directory.
            args: CLI arguments
        Returns:
            A return code that can be used as standard posix codes. 0 is success.
        """
        logger.debug('Entering replicate_object.')

        # 1 Bad working directory if not running from current working directory
        trestle_root = args.trestle_root  # trestle root is set via command line in args. Default is cwd.
        if not trestle_root or not fs.is_valid_project_root(trestle_root):
            logger.error(f'Given directory: {trestle_root} is not a trestle project.')
            return CmdReturnCodes.COMMAND_ERROR.value

        plural_path = fs.model_type_to_model_dir(model_alias)

        # 2 Check that input file given exists.

        input_file_stem = trestle_root / plural_path / args.name / model_alias
        content_type = FileContentType.path_to_content_type(input_file_stem)
        if content_type == FileContentType.UNKNOWN:
            logger.error(f'Input file {args.name} has no json or yaml file at expected location {input_file_stem}.')
            return CmdReturnCodes.COMMAND_ERROR.value

        input_file = input_file_stem.with_suffix(FileContentType.to_file_extension(content_type))

        # 3 Distributed load from file

        try:
            _, model_alias, model_instance = load_distributed(input_file, trestle_root)
        except TrestleError as err:
            logger.debug(f'load_distributed() failed: {err}')
            logger.warning(f'Replicate failed, error loading file: {err}')
            return CmdReturnCodes.COMMAND_ERROR.value
        except PermissionError as err:
            logger.debug(f'load_distributed() failed: {err}')
            logger.warning(f'Replicate failed, access permission error loading file: {err}')
            return CmdReturnCodes.AUTH_ERROR.value

        rep_model_path = trestle_root / plural_path / args.output / (
            model_alias + FileContentType.to_file_extension(content_type)
        )

        if rep_model_path.exists():
            logger.error(f'OSCAL file to be replicated here: {rep_model_path} exists.')
            logger.error('Aborting trestle replicate.')
            return CmdReturnCodes.COMMAND_ERROR.value

        if args.regenerate:
            logger.debug(f'regenerating uuids for model {input_file}')
            model_instance, uuid_lut, n_refs_updated = validator_helper.regenerate_uuids(model_instance)
            logger.debug(f'{len(uuid_lut)} uuids generated and {n_refs_updated} references updated')

        # 4 Prepare actions and plan
        top_element = Element(model_instance)
        create_action = CreatePathAction(rep_model_path, True)
        write_action = WriteFileAction(rep_model_path, top_element, content_type)

        # create a plan to create the directory and imported file.
        replicate_plan = Plan()
        replicate_plan.add_action(create_action)
        replicate_plan.add_action(write_action)

        try:
            replicate_plan.execute()
        except TrestleError as err:
            logger.debug(f'replicate_plan.execute() failed: {err}')
            logger.error(f'Replicate failed, error in executing replication operation: {err}')
            return CmdReturnCodes.COMMAND_ERROR.value

        return CmdReturnCodes.SUCCESS.value
