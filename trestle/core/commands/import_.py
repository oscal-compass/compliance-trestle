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
"""Trestle Import Command."""
import argparse
import logging
import pathlib

import trestle.core.commands.validate as validatecmd
from trestle.core import const
from trestle.core import validator_helper
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.core.remote import cache
from trestle.utils import fs
from trestle.utils import log

logger = logging.getLogger(__name__)


class ImportCmd(CommandPlusDocs):
    """Import an existing full OSCAL model into the trestle project."""

    name = 'import'

    def _init_arguments(self) -> None:
        logger.debug('Init arguments')
        self.add_argument(
            '-f', '--file', help='OSCAL file to import - either file path or url.', type=str, required=True
        )

        self.add_argument('-o', '--output', help='Name of output element.', type=str, required=True)

        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)

    def _run(self, args: argparse.Namespace) -> int:
        """Top level import run command."""
        log.set_log_level_from_args(args)

        logger.debug('Entering import run.')

        trestle_root = args.trestle_root
        if not fs.is_valid_project_root(trestle_root):
            logger.warning(f'Attempt to import from non-valid trestle project root {trestle_root}')
            return CmdReturnCodes.TRESTLE_ROOT_ERROR.value

        input_uri = args.file
        if cache.FetcherFactory.in_trestle_directory(trestle_root, input_uri):
            logger.warning(f'Imported file {input_uri} cannot be from current trestle project. Use duplicate instead.')
            return CmdReturnCodes.COMMAND_ERROR.value

        try:
            content_type = FileContentType.to_content_type('.' + input_uri.split('.')[-1])
        except TrestleError as err:
            logger.debug(f'FileContentType.to_content_type() failed: {err}')
            logger.warning(f'Import failed, could not work out content type from file suffix: {err}')
            return CmdReturnCodes.COMMAND_ERROR.value

        fetcher = cache.FetcherFactory.get_fetcher(trestle_root, str(input_uri))
        try:
            model_read, parent_alias = fetcher.get_oscal(True)
        except TrestleError as err:
            logger.warning(f'Error importing file: {err}')
            return CmdReturnCodes.COMMAND_ERROR.value
        except Exception as e:
            logger.warning(f'Error importing file: {e}')
            return CmdReturnCodes.COMMAND_ERROR.value

        plural_path = fs.model_type_to_model_dir(parent_alias)

        output_name = args.output

        desired_model_dir = trestle_root / plural_path
        desired_model_path: pathlib.Path = desired_model_dir / output_name / parent_alias
        desired_model_path = desired_model_path.with_suffix(FileContentType.to_file_extension(content_type)).resolve()

        if desired_model_path.exists():
            logger.warning(f'Cannot import because file to be imported here: {desired_model_path} already exists.')
            return CmdReturnCodes.COMMAND_ERROR.value

        if args.regenerate:
            logger.debug(f'regenerating uuids in imported file {input_uri}')
            model_read, lut, nchanged = validator_helper.regenerate_uuids(model_read)
            logger.debug(f'uuid lut has {len(lut.items())} entries and {nchanged} refs were updated')

        top_element = Element(model_read)
        create_action = CreatePathAction(desired_model_path, True)
        write_action = WriteFileAction(desired_model_path, top_element, content_type)

        # create a plan to create the directory and write the imported file.
        import_plan = Plan()
        import_plan.add_action(create_action)
        import_plan.add_action(write_action)

        try:
            import_plan.execute()
        except TrestleError as err:
            logger.debug(f'import_plan.execute() failed: {err}')
            logger.error(f'Import plan execution failed with error: {err}')
            return CmdReturnCodes.COMMAND_ERROR.value

        args = argparse.Namespace(file=desired_model_path, verbose=args.verbose, trestle_root=args.trestle_root)
        rollback = False
        try:
            rc = validatecmd.ValidateCmd()._run(args)
        except TrestleError as err:
            logger.debug(f'validator.validate() raised exception: {err}')
            logger.error(f'Import of {str(input_uri)} failed with validation error: {err}')
            rollback = True
        else:
            if rc > 0:
                logger.debug(f'validator.validate() did not pass for {desired_model_path}')
                msg = f'Validation of imported file {desired_model_path} did not pass'
                logger.warning(msg)
                rollback = True

        if rollback:
            logger.debug(f'Rolling back import of {str(input_uri)} to {desired_model_path}')
            try:
                import_plan.rollback()
            except TrestleError as err:
                logger.debug(f'Failed rollback attempt with error: {err}')
                logger.error(f'Import failed in plan rollback: {err}. Manually remove {desired_model_path} to recover.')
            return CmdReturnCodes.COMMAND_ERROR.value
        logger.debug(f'Successful rollback of import to {desired_model_path}')

        return CmdReturnCodes.SUCCESS.value
