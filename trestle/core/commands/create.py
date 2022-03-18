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
from datetime import datetime
from typing import Type

import trestle.common.err as err
import trestle.common.file_utils
import trestle.oscal
from trestle.common import const, file_utils, log
from trestle.common.common_types import TopLevelOscalModel
from trestle.common.model_utils import ModelUtils
from trestle.core import generators
from trestle.core.commands.add import Add
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan

logger = logging.getLogger(__name__)


class CreateCmd(CommandPlusDocs):
    """Create a sample OSCAL model in trestle project or create new elements within a given model."""

    name = 'create'

    def _init_arguments(self) -> None:
        self.add_argument('-t', '--type', help='Type of model if created anew.', choices=const.MODEL_TYPE_LIST)
        self.add_argument('-o', '--output', help='Name of the output created model.')
        self.add_argument(const.IOF_SHORT, const.IOF_LONG, help=const.IOF_HELP, action='store_true')
        self.add_argument(
            '-x', '--extension', help='Type of file output.', choices=['json', 'yaml', 'yml'], default='json'
        )
        self.add_argument(
            '-f', '--file', help='Optional existing OSCAL file that will have elements created within it.', type=str
        )
        self.add_argument(
            '-e', '--element', help='Optional path of element to be created whithin the specified file.', type=str
        )

    def _run(self, args: argparse.Namespace) -> int:
        """
        Execute the create command.

        Notes
            Either a new model will be created of the specified type,
            or an existing file will have new elements added within it.
        """
        try:
            # Normal create path
            if args.type and args.output:
                object_type = ElementPath(args.type).get_type()
                return self.create_object(args.type, object_type, args)
            # Add path
            elif args.file and args.element:
                add = Add()
                return add.add_from_args(args)

            raise err.TrestleIncorrectArgsError(
                'Create requires either a model type and output name, or a file and element path.'
            )

        except Exception as e:  # pragma: no cover
            return err.handle_generic_command_exception(e, logger, 'Error while creating a sample OSCAL model')

    @classmethod
    def create_object(cls, model_alias: str, object_type: Type[TopLevelOscalModel], args: argparse.Namespace) -> int:
        """Create a top level OSCAL object within the trestle directory, leveraging functionality in add."""
        log.set_log_level_from_args(args)
        trestle_root = args.trestle_root  # trestle root is set via command line in args. Default is cwd.
        if not trestle_root or not file_utils.is_valid_project_root(args.trestle_root):
            raise err.TrestleRootError(f'Given directory {trestle_root} is not a trestle project.')

        plural_path = ModelUtils.model_type_to_model_dir(model_alias)

        desired_model_dir = trestle_root / plural_path / args.output

        desired_model_path = desired_model_dir / (model_alias + '.' + args.extension)

        if desired_model_path.exists():
            raise err.TrestleError(f'OSCAL file to be created here: {desired_model_path} exists.')

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
        create_plan = Plan()
        create_plan.add_action(create_action)
        create_plan.add_action(write_action)
        create_plan.execute()
        return CmdReturnCodes.SUCCESS.value
