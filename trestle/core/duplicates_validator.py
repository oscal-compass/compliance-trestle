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

import pathlib
from typing import Any, Dict

from trestle.core.base_model import OscalBaseModel
from trestle.core.validator_helper import find_values_by_name
from trestle.utils import fs


class DuplicatesValidator:
    """Find duplicate items in oscal object."""

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """No initialization needed."""
        pass

    def validate(self, **kwargs: Dict[str, Any]) -> int:
        """Perform the validation."""
        oscal_object_name = kwargs['file']
        item_name = kwargs['item']

        file_path = pathlib.Path(oscal_object_name).absolute()
        model_type, _ = fs.get_contextual_model_type(file_path)
        model: OscalBaseModel = model_type.oscal_read(file_path)

        loe = find_values_by_name(model, item_name)
        if loe:
            nitems = len(loe)
            return 0 if nitems == len(set(loe)) else 1
        return 0


class DuplicatesValidatorBuilder:
    """Builder for the validator."""

    def __init__(self) -> None:
        """Initialize the instance as None."""
        self._instance = None

    def __call__(self, **kwargs: Dict[str, Any]) -> Any:
        """Do the validation call."""
        if not self._instance:
            self._instance = DuplicatesValidator(**kwargs)
        return self._instance
