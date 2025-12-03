# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2025 The OSCAL Compass Authors.
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

import datetime
import logging
import pathlib
from typing import Any, Dict, List, Optional, Type, cast

import orjson
from pydantic import Field, create_model
from pydantic import ConfigDict
from pydantic.fields import FieldInfo
from pydantic_core import from_json

from ruamel.yaml import YAML

import trestle.common.const as const
import trestle.common.err as err
from trestle.common.str_utils import AliasMode, classname_to_alias
from trestle.common.type_utils import get_origin, is_collection_field_type
from trestle.core.models.file_content_type import FileContentType
from trestle.core.trestle_base_model import TrestleBaseModel

logger = logging.getLogger(__name__)


def robust_datetime_serialization(input_dt: datetime.datetime) -> str:
    """Return ISO-8601 UTC string with milliseconds and TZ offset required."""
    if input_dt.tzinfo is None:
        raise err.TrestleError('Missing timezone in datetime')
    if input_dt.tzinfo.utcoffset(input_dt) is None:
        raise err.TrestleError('Missing utcoffset in datetime')

    # Force UTC, keep milliseconds
    return input_dt.astimezone(datetime.timezone.utc).isoformat(timespec='milliseconds')


class OscalBaseModel(TrestleBaseModel):
    """
    OSCAL Pydantic base model (updated for Pydantic v2).

    Provides strict schema enforcement, OSCAL serialization, and field manipulation helpers.
    """

    # Pydantic v2 model configuration
    model_config = ConfigDict(
        json_loads=orjson.loads,
        extra='forbid',
        validate_assignment=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={datetime.datetime: robust_datetime_serialization}
    )

    #
    # ─────────────── MODEL CREATION (STRIPPED MODELS) ───────────────
    #

    @classmethod
    def create_stripped_model_type(
        cls,
        stripped_fields: Optional[List[str]] = None,
        stripped_fields_aliases: Optional[List[str]] = None
    ) -> Type['OscalBaseModel']:
        """Create a new runtime model type with certain fields removed."""
        if stripped_fields and stripped_fields_aliases:
            raise err.TrestleError(
                'Provide only one: stripped_fields OR stripped_fields_aliases.'
            )
        if not stripped_fields and not stripped_fields_aliases:
            raise err.TrestleError(
                'Exactly one of stripped_fields or stripped_fields_aliases must be provided.'
            )

        # Convert aliases → field names if needed
        if stripped_fields_aliases is not None:
            alias_map = cls.alias_to_field_map()
            try:
                stripped_fields = [alias_map[a].name for a in stripped_fields_aliases]
            except KeyError as e:
                raise err.TrestleError(f'Alias {str(e)} does not exist in model')

        stripped_fields = stripped_fields or []

        new_fields: Dict[str, Any] = {}
        for name, field in cls.model_fields.items():
            if name in stripped_fields:
                continue

            annotation = field.annotation

            if field.is_required():
                new_fields[name] = (
                    annotation,
                    Field(..., alias=field.alias or name)
                )
            else:
                new_fields[name] = (
                    Optional[annotation],
                    Field(None, alias=field.alias or name)
                )

        new_model = create_model(
            cls.__name__,
            __base__=OscalBaseModel,
            **new_fields
        )

        return cast(Type[OscalBaseModel], new_model)

    #
    # ─────────────── FIELD LOOKUP HELPERS ───────────────
    #

    @classmethod
    def alias_to_field_map(cls) -> Dict[str, FieldInfo]:
        """Return mapping of alias → FieldInfo."""
        return {
            (field.alias or name): field
            for name, field in cls.model_fields.items()
        }

    def get_field_by_alias(self, alias: str) -> Optional[FieldInfo]:
        return self.alias_to_field_map().get(alias)

    def get_field_value_by_alias(self, alias: str) -> Optional[Any]:
        field = self.get_field_by_alias(alias)
        if field:
            return getattr(self, field.name, None)
        return None

    #
    # ─────────────── STRIPPED INSTANCE CONSTRUCTION ───────────────
    #

    def stripped_instance(
        self,
        stripped_fields: Optional[List[str]] = None,
        stripped_fields_aliases: Optional[List[str]] = None
    ) -> 'OscalBaseModel':
        stripped_class = self.create_stripped_model_type(
            stripped_fields=stripped_fields,
            stripped_fields_aliases=stripped_fields_aliases
        )

        remaining = {
            name: getattr(self, name)
            for name in stripped_class.model_fields
        }

        return stripped_class(**remaining)

    #
    # ─────────────── OSCAL SERIALIZATION ───────────────
    #

    def oscal_dict(self) -> Dict[str, Any]:
        """Return OSCAL-wrapped dict with top-level alias key."""
        class_name = self.__class__.__name__
        wrapped = classname_to_alias(class_name, AliasMode.JSON)
        raw = self.model_dump(by_alias=True, exclude_none=True)

        if '__root__' in raw:
            return {wrapped: raw['__root__']}

        return {wrapped: raw}

    def oscal_serialize_json_bytes(self, pretty: bool = False, wrapped: bool = True) -> bytes:
        obj = self.oscal_dict() if wrapped else self.model_dump(
            by_alias=True, exclude_none=True
        )
        if pretty:
            return orjson.dumps(obj, option=orjson.OPT_INDENT_2)
        return orjson.dumps(obj)

    def oscal_serialize_json(self, pretty: bool = False, wrapped: bool = True) -> str:
        return self.oscal_serialize_json_bytes(pretty, wrapped).decode(
            const.FILE_ENCODING
        )

    #
    # ─────────────── FILE IO ───────────────
    #

    def oscal_write(self, path: pathlib.Path) -> None:
        """Write this object to JSON or YAML in OSCAL-wrapped format."""
        content_type = FileContentType.to_content_type(path.suffix)

        if content_type == FileContentType.YAML:
            yaml = YAML(typ='safe')
            with path.open('w', encoding=const.FILE_ENCODING) as f:
                yaml.dump(yaml.load(self.oscal_serialize_json()), f)

        elif content_type == FileContentType.JSON:
            with path.open('wb') as f:
                f.write(self.oscal_serialize_json_bytes(pretty=True))

    @classmethod
    def oscal_read(cls, path: pathlib.Path) -> Optional['OscalBaseModel']:
        """Load an OSCAL-wrapped object from YAML or JSON."""
        alias = classname_to_alias(cls.__name__, AliasMode.JSON)
        content_type = FileContentType.to_content_type(path.suffix)

        if not path.exists():
            logger.warning(f'path does not exist in oscal_read: {path}')
            return None

        try:
            if content_type == FileContentType.YAML:
                yaml = YAML(typ='safe')
                with path.open('r', encoding=const.FILE_ENCODING) as f:
                    obj = yaml.load(f)
            else:
                with path.open('rb') as f:
                    obj = orjson.loads(f.read())
        except Exception as e:
            raise err.TrestleError(f'Error loading file {path}: {str(e)}')

        if not isinstance(obj, dict) or len(obj) != 1:
            raise err.TrestleError(
                f'Invalid OSCAL structure: requires single top-level key, found {len(obj)}.'
            )

        if alias not in obj:
            raise err.TrestleError(
                f'Missing top-level OSCAL wrapper key: {alias}'
            )

        try:
            return cls.model_validate(obj[alias])
        except Exception as e:
            raise err.TrestleError(f'Error parsing OSCAL model: {str(e)}')

    #
    # ─────────────── COPY OPERATIONS ───────────────
    #

    def copy_to(self, new_oscal_type: Type['OscalBaseModel']) -> 'OscalBaseModel':
        """Copy fields into another OSCAL model type."""
        if self.__class__.__name__ == new_oscal_type.__name__:
            return new_oscal_type.model_validate_json(
                self.oscal_serialize_json_bytes(
                    pretty=False, wrapped=False
                )
            )

        # __root__ → __root__
        if (
            '__root__' in self.model_fields
            and '__root__' in new_oscal_type.model_fields
            and len(self.model_fields) == 1
            and len(new_oscal_type.model_fields) == 1
        ):
            return new_oscal_type.model_validate(self.__root__)

        raise err.TrestleError('Provided inconsistent classes to copy.')

    def copy_from(self, existing_oscal_object: 'OscalBaseModel') -> None:
        """Copy-by-recast from another OSCAL model."""
        recast = existing_oscal_object.copy_to(self.__class__)
        for name in self.model_fields:
            setattr(self, name, getattr(recast, name))

    #
    # ─────────────── COLLECTION TYPE HANDLING ───────────────
    #

    @classmethod
    def is_collection_container(cls) -> bool:
        """Check if this model wraps a collection (via __root__)."""
        if len(cls.model_fields) == 1 and '__root__' in cls.model_fields:
            field = cls.model_fields['__root__']
            return is_collection_field_type(field.annotation)
        return False

    @classmethod
    def get_collection_type(cls) -> Optional[type]:
        if not cls.is_collection_container():
            raise err.TrestleError('OscalBaseModel is not wrapping a collection type')
        return get_origin(cls.model_fields['__root__'].annotation)
