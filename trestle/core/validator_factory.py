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
    group = cmd.parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', help='Path of file in trestle directory to validate.')
    group.add_argument('-t', '--type', choices=const.MODEL_TYPE_LIST, help='Validate one or all models of this type.')
    group.add_argument('-a', '--all', action='store_true', help='Validate all models in trestle directory.')
    cmd.add_argument('-n', '--name', help='Name of single model to validate (with --type specified).', required=False)
    cmd.add_argument('-i', '--item', choices=['uuid'], help='Name of item in model to validate.', required=True)
    cmd.add_argument('-m', '--mode', choices=['duplicates'], help='Mode of validation to use.', required=True)
