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
import pathlib
from abc import ABC, abstractmethod

from trestle.core.validator_helper import has_no_duplicate_values_by_name
from trestle.utils import fs
from trestle.utils.load_distributed import load_distributed


class Validator(ABC):
    """Abstract Validator interface."""

    @abstractmethod
    def validate(self, args: argparse.Namespace) -> int:
        """Validate the model."""


class DuplicatesValidator(Validator):
    """Find duplicate items in oscal object."""

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
                _, _, model = load_distributed(model_path)
                if not has_no_duplicate_values_by_name(model, args.item):
                    return 1
            return 0

        # validate all
        if 'all' in args and args.all:
            model_tups = fs.get_all_models()
            for mt in model_tups:
                model_path = trestle_root / fs.model_type_to_model_dir(mt[0]) / mt[1]
                _, _, model = load_distributed(model_path)
                if not has_no_duplicate_values_by_name(model, args.item):
                    return 1
            return 0

        # validate file
        if 'file' in args and args.file:
            file_path = trestle_root / args.file
            _, _, model = load_distributed(file_path)
            if not has_no_duplicate_values_by_name(model, args.item):
                return 1
        return 0
