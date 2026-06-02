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

from pydantic import BaseModel, ValidationError, model_validator

from trestle.common.err import TrestleError

Model = TypeVar('Model', bound='BaseModel')


class TrestleBaseModel(BaseModel):
    """Trestle Base Model. Serves as wrapper around BaseModel for overriding methods."""

    @classmethod
    def model_validate(
        cls: Type['Model'],
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: dict[str, Any] | None = None,
        extra: Any = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> 'Model':
        """Validate object to the given class."""
        try:
            return super().model_validate(
                obj,
                strict=strict,
                from_attributes=from_attributes,
                context=context,
                extra=extra,
                by_alias=by_alias,
                by_name=by_name,
            )
        except ValidationError as e:
            # check if failed due to the wrong OSCAL version:
            oscal_version_error = False
            message = ''
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

    @classmethod
    def parse_obj(cls: Type['Model'], obj: Any) -> 'Model':
        """Parse object to the given class. Deprecated: use model_validate instead."""
        return cls.model_validate(obj)

    def __str__(self) -> str:
        """Return string representation, unwrapping root if present (Pydantic v2 RootModel)."""
        if hasattr(self, 'root'):
            return str(self.root)
        return super().__str__()

    def __eq__(self, other: Any) -> bool:
        """Compare with unwrapped root value if present (Pydantic v2 RootModel)."""
        # Only use custom comparison for root models
        # Access model_fields from class to avoid deprecation warning in Pydantic v2.11+
        if hasattr(self, 'root') and 'root' in self.__class__.model_fields:
            if isinstance(other, type(self)):
                return self.root == other.root
            return self.root == other
        # For non-root models, use default Pydantic comparison
        return super().__eq__(other)

    def __hash__(self) -> int:
        """Hash the root value if present (Pydantic v2 RootModel)."""
        if hasattr(self, 'root'):
            try:
                return hash(self.root)
            except TypeError:
                # If root is unhashable, fall back to id-based hash
                return hash(id(self))
        # For Pydantic v2, use id-based hash for non-frozen models
        return hash(id(self))

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to root if present and attribute not found (Pydantic v2 RootModel)."""
        # Avoid infinite recursion by checking if root exists via __dict__
        if 'root' in self.__dict__ and name != 'root':
            try:
                return getattr(self.root, name)
            except AttributeError:
                pass
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
