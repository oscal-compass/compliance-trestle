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
"""Validate by confirming no duplicate items."""

import argparse
import logging
import pathlib
import re

from trestle.core.base_model import OscalBaseModel
from trestle.core.const import NCNAME_REGEX
from trestle.core.err import TrestleError
from trestle.core.validator_helper import Validator, find_values_by_name
from trestle.utils import fs
from trestle.utils.load_distributed import load_distributed

logger = logging.getLogger(__name__)


def _roleids_are_valid(model: OscalBaseModel) -> bool:
    role_ids_list = find_values_by_name(model, 'role_ids')
    p = re.compile(NCNAME_REGEX)
    for role_id_list in role_ids_list:
        for role_id in role_id_list:
            s = str(role_id.__root__)
            matched = p.match(s)
            if matched is None:
                return False
    return True


class RoleIdValidator(Validator):
    """Check that all RoleId values conform to NCName regex."""

    def validate(self, args: argparse.Namespace) -> int:
        """Perform the validation."""
        trestle_root = fs.get_trestle_project_root(pathlib.Path.cwd())

        # validate by type - all of type or just specified by name
        if 'type' in args and args.type is not None:
            models = []
            if 'name' in args and args.name is not None:
                models = [args.name]
            else:
                models = fs.get_models_of_type(args.type)
            models_path = trestle_root / fs.model_type_to_model_dir(args.type)
            for m in models:
                model_path = models_path / m
                try:
                    _, _, model = load_distributed(model_path)
                except TrestleError as e:
                    logger.warning(f'File load error {e}')
                    return 1
                if not _roleids_are_valid(model):
                    return 1
            return 0

        # validate all
        if 'all' in args and args.all:
            model_tups = fs.get_all_models()
            for mt in model_tups:
                model_path = trestle_root / fs.model_type_to_model_dir(mt[0]) / mt[1]
                _, _, model = load_distributed(model_path)
                if not _roleids_are_valid(model):
                    return 1
            return 0

        # validate file
        if 'file' in args and args.file:
            file_path = trestle_root / args.file
            _, _, model = load_distributed(file_path)
            if not _roleids_are_valid(model):
                return 1
        return 0
