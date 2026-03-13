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

from pydantic.v1 import BaseModel, ValidationError

from trestle.common.err import TrestleError

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

    def __str__(self) -> str:
        """Return string representation, unwrapping __root__ if present."""
        if hasattr(self, '__root__'):
            return str(self.__root__)
        return super().__str__()

    def __eq__(self, other: Any) -> bool:
        """Compare with unwrapped __root__ value if present."""
        # Only use custom comparison for __root__ models
        if hasattr(self, '__root__') and '__root__' in self.__fields__:
            if isinstance(other, type(self)):
                return self.__root__ == other.__root__
            return self.__root__ == other
        # For non-__root__ models, use default Pydantic comparison
        return super().__eq__(other)

    def __hash__(self) -> int:
        """Hash the __root__ value if present."""
        if hasattr(self, '__root__'):
            try:
                return hash(self.__root__)
            except TypeError:
                # If __root__ is unhashable, fall back to object hash
                return super().__hash__()
        return super().__hash__()

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to __root__ if present and attribute not found."""
        # Avoid infinite recursion by checking if __root__ exists via __dict__
        if '__root__' in self.__dict__ and name != '__root__':
            try:
                return getattr(self.__root__, name)
            except AttributeError:
                pass
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
