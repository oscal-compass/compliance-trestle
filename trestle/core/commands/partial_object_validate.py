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
"""Trestle schema-validate command."""

import argparse
import logging
import pathlib

import trestle.common.const as const
import trestle.core.models.elements as elements
from trestle.common import log
from trestle.common.err import TrestleError, handle_generic_command_exception
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.common.return_codes import CmdReturnCodes

logger = logging.getLogger(__name__)


class PartialObjectValidate(CommandBase):
    """Direct validation any oscal object in a file, including list objects."""

    name = 'partial-object-validate'

    def _init_arguments(self) -> None:
        self.add_argument(
            f'-{const.ARG_FILE_SHORT}',
            f'--{const.ARG_FILE}',
            help=const.ARG_DESC_FILE + ' to validate',
            required=True,
            type=pathlib.Path
        )

        self.add_argument(
            f'-{const.ARG_ELEMENT_SHORT}',
            f'--{const.ARG_ELEMENT}',
            help=const.ARG_DESC_ELEMENT + ' to validate.',
            required=True
        )

        self.add_argument(
            '-nv', '--no-validators', help='Only perform the most basic validation of the file', action='store_true'
        )

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            file_path: pathlib.Path = args.file.resolve()
            if not file_path.exists() or not file_path.is_file():
                raise TrestleError('File path provided does not exist or is a directory')

            element_str: str = args.element
            if ',' in element_str:
                logger.warning('Only a single element path is allowed.')

            return self.partial_object_validate(file_path, element_str)
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Error while validating OSCAL file')

    @classmethod
    def partial_object_validate(cls, file_path: pathlib.Path, element_string: str) -> int:
        """Run a schema validation on a file inferring file type based on element string."""
        # get model type
        logger.info(f'Validating {file_path}')
        element_path = elements.ElementPath(element_string)
        # get a wrapped object
        obm_type = element_path.get_obm_wrapped_type()
        obm_type.oscal_read(file_path)

        logger.info(f'VALID: {file_path} for {element_string}')
        return CmdReturnCodes.SUCCESS.value
