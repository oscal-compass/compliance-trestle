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
"""Trestle Describe Command."""

import argparse
import logging
import pathlib

import trestle.utils.log as log
from trestle.core.base_model import OscalBaseModel
from trestle.core.commands import cmd_utils as utils
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.models.elements import Element
from trestle.utils import fs

logger = logging.getLogger(__name__)


class DescribeCmd(CommandPlusDocs):
    """Describe contents of a model file."""

    name = 'describe'

    def _init_arguments(self) -> None:
        logger.debug('Init arguments')
        self.add_argument('-f', '--file', help='OSCAL file to import.', type=str, required=True)

        self.add_argument(
            '-e', '--element', help='Optional name of element in file to describe.', type=str, required=False
        )

    def _run(self, args: argparse.Namespace) -> int:
        logger.debug('Entering trestle describe.')

        log.set_log_level_from_args(args)

        if 'file' in args and args.file:
            model_file = pathlib.Path(args.file)

            element = '' if 'element' not in args else args.element

            return self.describe(model_file, element)

        logger.warning('No file specified for command describe.')
        return 1

    @classmethod
    def describe(cls, file_path: pathlib.Path, element_path_str: str) -> int:
        """Describe the contents of the file.

        Args:
            file_path: pathlib.Path for model file to describe.
            element: optional element path of element in model to describe.

        Returns:
            0 on success, 1 on failure.
        """
        model_type, _ = fs.get_stripped_contextual_model(file_path)

        model: OscalBaseModel = model_type.oscal_read(file_path)

        element_paths = utils.parse_element_arg(model, element_path_str)

        sub_model_element = Element(model)

        for element_path in element_paths:
            sub_model_element = Element(sub_model_element.get_at(element_path, False))

        return 0
