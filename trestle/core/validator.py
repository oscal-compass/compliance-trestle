# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Base class for all validators."""

import argparse
import logging
from abc import ABC, abstractmethod
from typing import TypeVar

from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.utils import fs
from trestle.utils.load_distributed import load_distributed

logger = logging.getLogger(__name__)

# Generic type var
TG = TypeVar('TG')


class Validator(ABC):
    """Validator base class."""

    def error_msg(self) -> str:
        """Error message used to describe this validator."""
        # subclasses can override as needed
        return self.__doc__

    @abstractmethod
    def model_is_valid(self, model: OscalBaseModel) -> bool:
        """
        Validate the model.

        args:
            model: An Oscal model that can be passed to the validator.

        returns:
            Whether or not the model passed this validation test.
        """

    def validate(self, args: argparse.Namespace) -> int:
        """Perform the validation according to user options."""
        trestle_root = args.trestle_root  # trestle root is set via command line in args. Default is cwd.

        # validate by type - all of type or just specified by name
        if 'type' in args and args.type is not None:
            models = []
            if 'name' in args and args.name is not None:
                models = [args.name]
            else:
                models = fs.get_models_of_type(args.type, trestle_root)
            models_path = trestle_root / fs.model_type_to_model_dir(args.type)
            for m in models:
                model_path = models_path / m
                try:
                    _, _, model = load_distributed(model_path)
                except TrestleError as e:
                    logger.warning(f'File load error {e}')
                    return 1
                if not self.model_is_valid(model):
                    logger.info(f'INVALID: Model {model_path} did not pass the {self.error_msg()}')
                    return 1
                logger.info(f'VALID: Model {model_path} passed the {self.error_msg()}')
            return 0

        # validate all
        if 'all' in args and args.all:
            model_tups = fs.get_all_models(trestle_root)
            for mt in model_tups:
                model_path = trestle_root / fs.model_type_to_model_dir(mt[0]) / mt[1]
                _, _, model = load_distributed(model_path)
                if not self.model_is_valid(model):
                    logger.info(f'INVALID: Model {model_path} did not pass the {self.error_msg()}')
                    return 1
                logger.info(f'VALID: Model {model_path} passed the {self.error_msg()}')
            return 0

        # validate file
        if 'file' in args and args.file:
            file_path = trestle_root / args.file
            _, _, model = load_distributed(file_path)
            if not self.model_is_valid(model):
                logger.info(f'INVALID: Model {file_path} did not pass the {self.error_msg()}')
                return 1
            logger.info(f'VALID: Model {file_path} passed the {self.error_msg()}')
        return 0
