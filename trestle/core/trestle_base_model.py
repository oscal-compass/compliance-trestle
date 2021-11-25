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
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

from trestle.core.err import TrestleError

Model = TypeVar('Model', bound='BaseModel')


class TrestleBaseModel(BaseModel):
    """Trestle Base Model. Serves as wrapper around BaseModel for overriding methods."""

    @classmethod
    def parse_obj(cls: Type['Model'], obj: Any) -> 'Model':
        """Parse object to the given class."""
        try:
            return super().parse_obj(obj)
        except ValidationError as e:
            # check if failed due to the wrong OSCAL version:
            oscal_version_error = False
            for err in e.errors():
                for field in err['loc']:
                    if field == 'oscal-version':
                        message = err['msg']
                        oscal_version_error = True
                        break
            if oscal_version_error:
                raise TrestleError(f'{message}')
            else:
                raise
