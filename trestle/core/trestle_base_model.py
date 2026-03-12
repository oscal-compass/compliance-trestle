# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Trestle Base Model."""

import copy
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

from trestle.common.err import TrestleError

Model = TypeVar('Model', bound='BaseModel')


class TrestleBaseModel(BaseModel):
    """Trestle Base Model. Serves as wrapper around BaseModel for overriding methods."""

    @staticmethod
    def _snapshot_model_inputs(obj: Any) -> Any:
        """Recursively copy model values so callers don't retain mutable shared references."""
        if isinstance(obj, BaseModel):
            return obj.model_copy(deep=True)
        if isinstance(obj, list):
            return [TrestleBaseModel._snapshot_model_inputs(item) for item in obj]
        if isinstance(obj, tuple):
            return tuple(TrestleBaseModel._snapshot_model_inputs(item) for item in obj)
        if isinstance(obj, set):
            return {TrestleBaseModel._snapshot_model_inputs(item) for item in obj}
        if isinstance(obj, dict):
            return {key: TrestleBaseModel._snapshot_model_inputs(value) for key, value in obj.items()}
        return copy.deepcopy(obj)

    def __init__(self, **data: Any) -> None:
        """Initialize models from a snapshot of input values to avoid shared nested state."""
        snapshot = {key: self._snapshot_model_inputs(value) for key, value in data.items()}
        super().__init__(**snapshot)

    @classmethod
    def model_validate(cls: Type['Model'], obj: Any, *args, **kwargs) -> 'Model':
        """Parse object to the given class (pydantic v2 API)."""
        try:
            return super().model_validate(obj, *args, **kwargs)
        except ValidationError as e:
            # check if failed due to the wrong OSCAL version:
            oscal_version_error = False
            message = ''
            for error in e.errors():
                for field in error['loc']:
                    if field == 'oscal-version':
                        message = error['msg']
                        oscal_version_error = True
                        break
            if oscal_version_error:
                raise TrestleError(f'{message}')
            else:
                raise
