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

from trestle.common import const, file_utils, log
from trestle.common.err import TrestleError, TrestleRootError, handle_generic_command_exception
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.core.remote import cache
from trestle.core.validator import Validator
from trestle.core.validator_factory import validator_factory

logger = logging.getLogger(__name__)


class ImportCmd(CommandPlusDocs):
    """Import an existing full OSCAL model into the trestle workspace."""

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
        try:
            log.set_log_level_from_args(args)
            trestle_root = args.trestle_root
            if not file_utils.is_valid_project_root(trestle_root):
                raise TrestleRootError(f'Attempt to import from non-valid trestle project root {trestle_root}')

            input_uri = args.file
            if cache.FetcherFactory.in_trestle_directory(trestle_root, input_uri):
                raise TrestleError(
                    f'Imported file {input_uri} cannot be from current trestle project. Use duplicate instead.'
                )

            content_type = FileContentType.to_content_type('.' + input_uri.split('.')[-1])

            fetcher = cache.FetcherFactory.get_fetcher(trestle_root, str(input_uri))

            model_read, parent_alias = fetcher.get_oscal(True)

            # validate the loaded model in memory before writing out
            # this will do any needed fixes to the file, such as assign missing catalog group ids
            args_validate = argparse.Namespace(mode=const.VAL_MODE_ALL)
            validator: Validator = validator_factory.get(args_validate)
            if not validator.model_is_valid(model_read, True, trestle_root):
                logger.warning(f'Validation of file to be imported {input_uri} did not pass.  Import failed.')
                return CmdReturnCodes.COMMAND_ERROR.value

            plural_path = ModelUtils.model_type_to_model_dir(parent_alias)

            output_name = args.output

            desired_model_dir = trestle_root / plural_path
            desired_model_path: pathlib.Path = desired_model_dir / output_name / parent_alias
            desired_model_path = desired_model_path.with_suffix(FileContentType.to_file_extension(content_type)
                                                                ).resolve()

            if desired_model_path.exists():
                logger.warning(f'Cannot import because file to be imported here: {desired_model_path} already exists.')
                return CmdReturnCodes.COMMAND_ERROR.value

            if args.regenerate:
                logger.debug(f'regenerating uuids in imported file {input_uri}')
                model_read, lut, nchanged = ModelUtils.regenerate_uuids(model_read)
                logger.debug(f'uuid lut has {len(lut.items())} entries and {nchanged} refs were updated')

            top_element = Element(model_read)
            create_action = CreatePathAction(desired_model_path, True)
            write_action = WriteFileAction(desired_model_path, top_element, content_type)

            # create a plan to create the directory and write the imported file.
            import_plan = Plan()
            import_plan.add_action(create_action)
            import_plan.add_action(write_action)

            import_plan.execute()

            args = argparse.Namespace(
                file=desired_model_path,
                verbose=args.verbose,
                trestle_root=args.trestle_root,
                type=None,
                all=None,
                quiet=True
            )
            return CmdReturnCodes.SUCCESS.value

        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while importing OSCAL file')
