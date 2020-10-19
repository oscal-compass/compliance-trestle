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

import pathlib

from ilcli import Command

import trestle.core.validater as validater
import trestle.oscal.target as ostarget
from trestle.core import const
from trestle.core.err import TrestleError, TrestleValidationError


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
        if args.file is None:
            raise TrestleError(f'Argument "-{const.ARG_FILE_SHORT}" is required')

        if args.mode is None:
            raise TrestleError(f'Argument "-{const.ARG_MODE_SHORT}" is required')
        mode = args.mode
        if mode != const.VAL_MODE_DUPLICATES:
            raise TrestleError(f'Mode value "{mode}" is not recognized.')

        if args.item is None:
            raise TrestleError(f'Argument "-{const.ARG_ITEM_SHORT}" is required')
        item = args.item

        model = ostarget.TargetDefinition.oscal_read(pathlib.Path(args.file))

        loe = validater.find_values_by_name(model, item)
        if loe:
            nitems = len(loe)
            is_valid = nitems == len(set(loe))
            if is_valid:
                self.out(f'The model is valid and contains no duplicates of item {args.item}')
            else:
                self.out(f'The model is invalid and contains duplicates of item {args.item}')
                raise TrestleValidationError(f'Model {args.file} is invalid with duplicate values of {args.item}')
        else:
            self.out(f'The model is valid but contains no items of name {args.item}')
