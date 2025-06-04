# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2022 IBM Corp. All rights reserved.
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
"""Function to load and validate files while avoiding circular imports."""
import argparse
import logging
from pathlib import Path
from typing import Optional, Tuple

from trestle.common import const
from trestle.common.common_types import TG, TopLevelOscalModel
from trestle.common.file_utils import FileContentType
from trestle.common.model_utils import ModelUtils
from trestle.core.validator import Validator
from trestle.core.validator_factory import validator_factory

logger = logging.getLogger(__name__)


def load_validate_model_path(trestle_root: Path, model_path: Path) -> TopLevelOscalModel:
    """Load a model by its path and validate it."""
    _, _, model = ModelUtils.load_distributed(model_path, trestle_root)
    args = argparse.Namespace(mode=const.VAL_MODE_ALL, quiet=True)
    validator: Validator = validator_factory.get(args)
    if not validator.model_is_valid(model, True, trestle_root):
        logger.warning(f'Model loaded at {model_path} fails validation, but is being loaded anyway.')
    return model


def load_validate_model_name(
    trestle_root: Path,
    model_name: str,
    model_class: TG,
    file_content_type: Optional[FileContentType] = None
) -> Tuple[TG, Path]:
    """Load a model by its name and type and validate it."""
    model_path = ModelUtils.get_model_path_for_name_and_class(trestle_root, model_name, model_class, file_content_type)
    model = load_validate_model_path(trestle_root, model_path)
    return model, model_path
