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
"""Register all validators here in the validator_factory."""

from ilcli import Command

from trestle.core import const
from trestle.core import duplicates_validator
from trestle.core.object_factory import ObjectFactory

# Create the singleton validator factory
validator_factory: ObjectFactory = ObjectFactory()

# Register all validators here
validator_factory.register_object(const.VAL_MODE_DUPLICATES, duplicates_validator.DuplicatesValidator)


def init_arguments(cmd: Command) -> None:
    """Feed the arguments to the argument parser."""
    cmd.add_argument(
        f'-{const.ARG_FILE_SHORT}',
        f'--{const.ARG_FILE}',
        help=const.ARG_DESC_FILE + ' to validate.',
        required=True,
    )
    cmd.add_argument(
        f'-{const.ARG_ITEM_SHORT}',
        f'--{const.ARG_ITEM}',
        help=const.ARG_DESC_ITEM + ' to validate.',
        required=True,
    )
    cmd.add_argument(
        f'-{const.ARG_MODE_SHORT}',
        f'--{const.ARG_MODE}',
        help=const.ARG_DESC_MODE + ' of the validation.',
        choices=[const.VAL_MODE_DUPLICATES],
        default=const.VAL_MODE_DUPLICATES,
    )
