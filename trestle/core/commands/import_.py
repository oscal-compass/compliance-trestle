# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
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
from json.decoder import JSONDecodeError

import trestle.core.commands.validate as validatecmd
from trestle.core import parser
from trestle.core import validator_helper
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs
from trestle.utils import log

logger = logging.getLogger(__name__)


class ImportCmd(CommandPlusDocs):
    """Import an existing full OSCAL model into the trestle project."""

    # The line above comes with the doc string
    name = 'import'

    def _init_arguments(self) -> None:
        logger.debug('Init arguments')
        self.add_argument('-f', '--file', help='OSCAL file to import.', type=str, required=True)

        self.add_argument('-o', '--output', help='Name of output element.', type=str, required=True)

        self.add_argument(
            '-r', '--regenerate', action='store_true', help='Enable regeneration of uuids within the document'
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Top level import run command."""
        log.set_log_level_from_args(args)

        logger.debug('Entering import run.')

        # 1. Validate input arguments are as expected.
        # This code block may never be reached as the argument is declared to be required.

        # 1.1 Check that input file given exists.
        input_file = pathlib.Path(args.file).resolve()
        if not input_file.exists():
            logger.error(f'Input file {args.file} does not exist.')
            return 1

        # 1.2 Bad working directory if not running from current working directory
        cwd = pathlib.Path.cwd().resolve()
        trestle_root = fs.get_trestle_project_root(cwd)
        if trestle_root is None:
            logger.error(f'Current working directory: {cwd} is not within a trestle project.')
            return 1

        # 2. Importing a file that is already inside a trestle-initialized dir is bad
        try:
            input_file.relative_to(trestle_root)
        except ValueError:
            # An exception here is good: it means that the input file is not inside a trestle dir.
            pass
        else:
            logger.error('Input file cannot be from current trestle project. Use duplicate instead.')
            return 1

        # 3. Work out typing information from input suffix.
        try:
            content_type = FileContentType.to_content_type(input_file.suffix)
        except TrestleError as err:
            logger.debug(f'FileContentType.to_content_type() failed: {err}')
            logger.error(f'Import failed, could not work out content type from file suffix: {err}')
            return 1

        # 4. Load input and parse for model

        # 4.1 Load from file
        try:
            data = fs.load_file(input_file.resolve())
        except JSONDecodeError as err:
            logger.debug(f'fs.load_file() failed: {err}')
            logger.error(f'Import failed, JSON error loading file: {err}')
            return 1
        except TrestleError as err:
            logger.debug(f'fs.load_file() failed: {err}')
            logger.error(f'Import failed, error loading file: {err}')
            return 1
        except PermissionError as err:
            logger.debug(f'fs.load_file() failed: {err}')
            logger.error(f'Import failed, access permission error loading file: {err}')
            return 1

        # 4.2 root key check
        try:
            parent_alias = parser.root_key(data)
        except TrestleError as err:
            logger.debug(f'parser.root_key() failed: {err}')
            logger.error(f'Import failed, failed to parse input file for root key: {err}')
            return 1

        # 4.3 parse the model
        parent_model_name = parser.to_full_model_name(parent_alias)
        try:
            parent_model = parser.parse_dict(data[parent_alias], parent_model_name)
        except TrestleError as err:
            logger.debug(f'parser.parse_file() failed: {err}')
            logger.error(f'Import failed, failed to parse valid contents of input file: {err}')
            return 1

        # 5. Work out output directory and file
        plural_path = fs.model_type_to_model_dir(parent_alias)

        desired_model_dir = trestle_root / plural_path
        # args.output is presumed to be assured as it is declared to be required
        if args.output:
            desired_model_path = desired_model_dir / args.output / (parent_alias + input_file.suffix)
            desired_model_path = desired_model_path.resolve()

        if desired_model_path.exists():
            logger.error(f'OSCAL file to be created here: {desired_model_path} exists.')
            logger.error('Aborting trestle import.')
            return 1

        # 6. Prepare actions and plan
        model_read = parent_model.oscal_read(input_file)
        if args.regenerate:
            logger.debug(f'regenerating uuids in {input_file}')
            model_read, lut, nchanged = validator_helper.regenerate_uuids(model_read)
            logger.debug(f'uuid lut has {len(lut.items())} entries and {nchanged} refs were updated')
        top_element = Element(model_read)
        create_action = CreatePathAction(desired_model_path, True)
        write_action = WriteFileAction(desired_model_path, top_element, content_type)

        # create a plan to create the directory and imported file.
        import_plan = Plan()
        import_plan.add_action(create_action)
        import_plan.add_action(write_action)

        try:
            import_plan.simulate()
        except TrestleError as err:
            logger.debug(f'import_plan.simulate() failed: {err}')
            logger.error(f'Import failed, error in testing import operation: {err}')
            return 1

        try:
            import_plan.execute()
        except TrestleError as err:
            logger.debug(f'import_plan.execute() failed: {err}')
            logger.error(f'Import failed, error in actual import operation: {err}')
            return 1

        # 7. Validate the imported file, rollback if unsuccessful:
        args = argparse.Namespace(file=desired_model_path, mode='duplicates', item='uuid', verbose=args.verbose)
        rollback = False
        try:
            rc = validatecmd.ValidateCmd()._run(args)
        except TrestleError as err:
            logger.debug(f'validator.validate() raised exception: {err}')
            logger.error(f'Import of {str(input_file.resolve())} failed, validation failed with error: {err}')
            rollback = True
        else:
            if rc > 0:
                logger.debug(f'validator.validate() found duplicates in {desired_model_path}')
                msg = f'Validation of imported file {desired_model_path} failed due to the presence of duplicate uuids'
                logger.error(msg)
                rollback = True

        if rollback:
            logger.debug(f'Rolling back import of {str(input_file.resolve())} to {desired_model_path}')
            try:
                import_plan.rollback()
            except TrestleError as err:
                logger.debug(f'Failed rollback attempt with error: {err}')
                logger.error(f'Failed to rollback: {err}. Remove {desired_model_path} to resolve state.')
            return 1
        else:
            logger.debug(f'Successful rollback of import to {desired_model_path}')
        # 8. Leave the rest to trestle split

        return 0
