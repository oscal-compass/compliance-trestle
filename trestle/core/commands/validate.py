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

import argparse

from ilcli import Command

from trestle.core import const
from trestle.core.validator_factory import validator_factory


class ValidateCmd(Command):
    """Validate contents of a trestle model."""

    name = 'validate'

    def _init_arguments(self) -> None:
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

    def _run(self, args: argparse.ArgumentParser) -> int:
        """Validate an OSCAL file in different modes."""
        args_raw = args.__dict__

        validator = validator_factory.create(args_raw[const.ARG_MODE])

        return validator.validate(**args_raw)
