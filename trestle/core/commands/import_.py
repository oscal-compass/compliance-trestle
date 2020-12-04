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
import pathlib
import warnings

from ilcli import Command  # type: ignore

from trestle.core import parser
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs
from trestle.utils import log

logger = log.get_logger()


class ImportCmd(Command):
    """Import an existing full OSCAL model into the trestle project."""

    # The line above comes with the doc string
    name = 'import'

    def _init_arguments(self) -> None:
        logger.debug('Init arguments')
        self.add_argument('-f', '--file', help='OSCAL file to import.', type=str, required=True)

        self.add_argument('-o', '--output', help='Name of output element.', type=str, required=True)

        self.add_argument(
            '-r', '--regenerate', type=bool, default=False, help='Enable to regenerate uuids within the document'
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Top level import run command."""
        logger.debug('Entering import run.')

        # 1. Validate input arguments are as expected. This code block may never be reached because cli.py enforces required args.
        if len(args.file) == 0:
            logger.error('trestle import requires a file to be provided with -f or --file.')
            return 1

        input_file = pathlib.Path(args.file)
        if not input_file.exists():
            logger.error(f'Input file {args.file} does not exist.')
            return 1

        cwd = pathlib.Path.cwd().resolve()
        trestle_root = fs.get_trestle_project_root(cwd)
        if trestle_root is None:
            logger.error(f'Current working directory: {cwd} is not within a trestle project.')
            return 1

        # 2. Ensure file is not in trestle dir
        trestle_root = trestle_root.resolve()
        try:
            input_file.absolute().relative_to(trestle_root)
        except Exception:
            pass
        else:
            logger.error('Input file cannot be from current trestle project. Use duplicate instead.')
            return 1

        # 3. Work out typing information from input suffix.
        try:
            content_type = FileContentType.to_content_type(input_file.suffix)
        except Exception as err:
            logger.debug(f'FileContentType.to_content_type() failed: {err}')
            logger.error(f'Import failed (FileContentType.to_content_type()): {err}')
            return 1

        # 4. Load input and parse for model
        data = fs.load_file(input_file.absolute())

        try:
            parent_alias = parser.root_key(data)
        except Exception as err:
            logger.debug(f'parser.root_key() failed: {err}')
            logger.error(f'Import failed (parser.root_key()): {err}')
            return 1

        parent_model_name = parser.to_full_model_name(parent_alias)
        try:
            parent_model = parser.parse_file(input_file.absolute(), parent_model_name)
        except Exception as err:
            logger.debug(f'parser.parse_file() failed: {err}')
            logger.error(f'Import failed (parser.parse_file()): {err}')
            return 1

        # 5. Work out output directory and file
        plural_path: str
        # Cater to POAM
        if parent_alias[-1] == 's':
            plural_path = parent_alias
        else:
            plural_path = parent_alias + 's'

        desired_model_dir = trestle_root / plural_path
        if args.output:
            desired_model_path = desired_model_dir / args.output / (parent_alias + input_file.suffix)
        else:
            logger.error('trestle import requires an output name to be provided with -o or --output.')
            return 1

        if desired_model_path.exists():
            logger.error(f'OSCAL file to be created here: {desired_model_path} exists.')
            logger.error('Aborting trestle import.')
            return 1

        # 6. Prepare actions and plan
        top_element = Element(parent_model.oscal_read(input_file))
        create_action = CreatePathAction(desired_model_path.absolute(), True)
        write_action = WriteFileAction(desired_model_path.absolute(), top_element, content_type)

        # create a plan to create the directory and imported file.
        import_plan = Plan()
        import_plan.add_action(create_action)
        import_plan.add_action(write_action)

        try:
            import_plan.simulate()
        except Exception as err:
            logger.debug(f'import_plan.simulate() failed: {err}')
            logger.error(f'Import failed (import_plan.simulate()): {err}')
            return 1

        try:
            import_plan.execute()
        except Exception as err:
            logger.debug(f'import_plan.execute() failed: {err}')
            logger.error(f'Import failed (import_plan.execute()): {err}')
            return 1

        # 7. Leave the rest to trestle split
        return 0
