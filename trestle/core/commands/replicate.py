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
"""Trestle Replicate Command."""
import argparse
import logging
import pathlib
from json.decoder import JSONDecodeError

from ilcli import Command  # type: ignore

# from trestle.core import parser
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs
from trestle.utils import log
from trestle.utils.load_distributed import load_distributed

logger = logging.getLogger(__name__)


class ReplicateCmd(Command):
    """Replicate an existing full OSCAL model into the trestle project."""

    name = 'replicate'

    def _init_arguments(self) -> None:
        logger.debug('Init arguments')
        self.add_argument('-f', '--file', help='OSCAL file to replicate.', type=str, required=True)

        self.add_argument('-o', '--output', help='Name of output model.', type=str, required=True)

        self.add_argument(
            '-r', '--regenerate', type=bool, default=False, help='Enable to regenerate uuids within the document'
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Top level replicate run command."""
        log.set_log_level_from_args(args)

        logger.debug('Entering replicate run.')

        # 1. Validate input arguments are as expected.

        # 1.1 Check that input file given exists.
        input_file = pathlib.Path(args.file)
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
        # trestle_root = trestle_root.resolve()
        # try:
        #     input_file.absolute().relative_to(trestle_root)
        # except ValueError:
        #     # An exception here is good: it means that the input file is not inside a trestle dir.
        #     pass
        # else:
        #     logger.error('Input file cannot be from current trestle project. Use duplicate instead.')
        #     return 1

        # 3. Work out typing information from input suffix.
        try:
            content_type = FileContentType.to_content_type(input_file.suffix)
        except TrestleError as err:
            logger.debug(f'FileContentType.to_content_type() failed: {err}')
            logger.error(f'Import failed, could not work out content type from file suffix: {err}')
            return 1

        # 4. Load input and parse for model

        # 4.1 Distributed load from file
        model_instance: OscalBaseModel

        try:
            model_type, model_alias, model_instance = load_distributed(input_file.absolute())
        except JSONDecodeError as err:
            logger.debug(f'load_distributed() failed: {err}')
            logger.error(f'Replicate failed, JSON error loading file: {err}')
            return 1
        except TrestleError as err:
            logger.debug(f'load_distributed() failed: {err}')
            logger.error(f'Replicate failed, error loading file: {err}')
            return 1
        except PermissionError as err:
            logger.debug(f'load_distributed() failed: {err}')
            logger.error(f'Replicate failed, access permission error loading file: {err}')
            return 1

        # 4.2 root key check
        # try:
        #     parent_alias = parser.root_key(model)
        # except TrestleError as err:
        #     logger.debug(f'parser.root_key() failed: {err}')
        #     logger.error(f'Import failed, failed to parse input file for root key: {err}')
        #     return 1

        # 4.3 parse the model
        # parent_model_name = parser.to_full_model_name(parent_alias)
        # try:
        #     parent_model = parser.parse_file(input_file.absolute(), parent_model_name)
        # except TrestleError as err:
        #     logger.debug(f'parser.parse_file() failed: {err}')
        #     logger.error(f'Import failed, failed to parse valid contents of input file: {err}')
        #     return 1

        # 5. Work out output directory and file
        plural_path: str
        plural_path = model_alias
        # Cater to POAM
        if model_alias[-1] != 's':
            plural_path = model_alias + 's'

        desired_model_dir = trestle_root / plural_path
        # args.output is presumed to be assured as it is declared to be required
        if args.output:
            desired_model_path = desired_model_dir / args.output / (model_alias + input_file.suffix)

        if desired_model_path.exists():
            logger.error(f'OSCAL file to be created here: {desired_model_path} exists.')
            logger.error('Aborting trestle replicate.')
            return 1

        # 6. Prepare actions and plan
        # top_element = Element(model_instance.oscal_read(input_file))
        top_element = Element(model_instance)
        create_action = CreatePathAction(desired_model_path.absolute(), True)
        write_action = WriteFileAction(desired_model_path.absolute(), top_element, content_type)

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

        # 7. Leave the rest to trestle split
        return 0
