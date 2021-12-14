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
"""Trestle Create CommandPlusDocs."""

import argparse
import logging
import traceback
from datetime import datetime
from typing import Type

import trestle.oscal
from trestle.core import const
from trestle.core import generators
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.common_types import TopLevelOscalModel
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.utils import fs
from trestle.utils import log

logger = logging.getLogger(__name__)


class CreateCmd(CommandPlusDocs):
    """Create a sample OSCAL model in trestle project."""

    name = 'create'

    def _init_arguments(self) -> None:
        self.add_argument('model', help='', choices=const.MODEL_TYPE_LIST)
        self.add_argument('-o', '--output', help='Name of the output created model.', required=True)
        self.add_argument(const.IOF_SHORT, const.IOF_LONG, help=const.IOF_HELP, action='store_true')
        self.add_argument(
            '-x', '--extension', help='Type of file output.', choices=['json', 'yaml', 'yml'], default='json'
        )

    def _run(self, args: argparse.Namespace) -> int:
        """Execute."""
        try:
            object_type = ElementPath(args.model).get_type()
            return self.create_object(args.model, object_type, args)
        except TrestleError as e:
            logger.debug(traceback.format_exc())
            logger.error(f'Error while creating a sample OSCAL model: {e}')
            return CmdReturnCodes.COMMAND_ERROR.value
        except Exception as e:  # pragma: no cover
            logger.debug(traceback.format_exc())
            logger.error(f'Unexpected error while creating a sample OSCAL model: {e}')
            return CmdReturnCodes.UNKNOWN_ERROR.value

    @classmethod
    def create_object(cls, model_alias: str, object_type: Type[TopLevelOscalModel], args: argparse.Namespace) -> int:
        """Create a top level OSCAL object within the trestle directory, leveraging functionality in add."""
        log.set_log_level_from_args(args)
        trestle_root = args.trestle_root  # trestle root is set via command line in args. Default is cwd.
        if not trestle_root or not fs.is_valid_project_root(args.trestle_root):
            logger.error(f'Given directory {trestle_root} is not a trestle project.')
            return CmdReturnCodes.TRESTLE_ROOT_ERROR.value
        plural_path = fs.model_type_to_model_dir(model_alias)

        desired_model_dir = trestle_root / plural_path / args.output

        desired_model_path = desired_model_dir / (model_alias + '.' + args.extension)

        if desired_model_path.exists():
            logger.error(f'OSCAL file to be created here: {desired_model_path} exists.')
            logger.error('Aborting trestle create.')
            return CmdReturnCodes.COMMAND_ERROR.value

        # Create sample model.
        sample_model = generators.generate_sample_model(object_type, include_optional=args.include_optional_fields)
        # Presuming top level level model not sure how to do the typing for this.
        sample_model.metadata.title = f'Generic {model_alias} created by trestle named {args.output}.'  # type: ignore
        sample_model.metadata.last_modified = datetime.now().astimezone()
        sample_model.metadata.oscal_version = trestle.oscal.OSCAL_VERSION
        sample_model.metadata.version = '0.0.0'

        top_element = Element(sample_model, model_alias)

        create_action = CreatePathAction(desired_model_path.resolve(), True)
        write_action = WriteFileAction(
            desired_model_path.resolve(), top_element, FileContentType.to_content_type(desired_model_path.suffix)
        )

        # create a plan to write the directory and file.
        try:
            create_plan = Plan()
            create_plan.add_action(create_action)
            create_plan.add_action(write_action)
            create_plan.execute()
            return CmdReturnCodes.SUCCESS.value
        except Exception as e:
            logger.error('Unknown error executing trestle create operations. Rolling back.')
            logger.debug(e)
            return CmdReturnCodes.COMMAND_ERROR.value
