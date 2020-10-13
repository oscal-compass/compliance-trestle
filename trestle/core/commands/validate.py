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
"""Trestle Validate Command."""
from typing import List

from ilcli import Command

from trestle.core import const
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.core.models.elements import ElementPath
from trestle.core.models.plans import Plan

from . import cmd_utils


class ValidateCmd(Command):
    """Validate contents of a trestle model."""

    name = 'validate'

    def _init_arguments(self):
        self.add_argument(
            f'-{const.ARG_FILE_SHORT}',
            f'--{const.ARG_FILE}',
            help=const.ARG_DESC_FILE + ' to validate.',
        )
        self.add_argument(
            f'-{const.ARG_ITEM_SHORT}',
            f'--{const.ARG_ITEM}',
            help=const.ARG_DESC_ITEM + ' to validate.',
        )
        self.add_argument(
            f'-{const.ARG_MODE_SHORT}',
            f'--{const.ARG_MODE}',
            help=const.ARG_DESC_MODE + ' to validate.',
        )

    def _run(self, args):
        """Validate an OSCAL file in different modes."""
        # get the Model
        if args[const.ARG_FILE] is None:
            raise TrestleError(f'Argument "-{const.ARG_FILE_SHORT}" is required')

        model: OscalBaseModel = cmd_utils.get_model(args[const.ARG_FILE])
        element_paths: List[ElementPath] = cmd_utils.parse_element_args(args[const.ARG_ELEMENT])

        split_plan = self._split_model(model, element_paths)

        try:
            split_plan.execute()
        except Exception as ex:
            split_plan.rollback()
            raise TrestleError(f'Could not perform operation: {ex}')

    def _split_model(self, model: OscalBaseModel, element_paths: List[ElementPath]) -> Plan:
        """Split the model at the provided element paths."""
        raise NotImplementedError()
