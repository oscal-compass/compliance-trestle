# modified by FixAny.py
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
"""Pydantic base model and utility functions."""

import datetime
import logging
import pathlib
from typing import Any, Dict, List, Optional, Type, cast

from pydantic import BaseModel, Extra, Field, create_model
from pydantic.fields import ModelField
from pydantic.parse import load_file

import trestle.core.const as const
import trestle.core.err as err
from trestle.core.models.file_content_type import FileContentType
from trestle.core.utils import classname_to_alias

import yaml

logger = logging.getLogger(__name__)


def robust_datetime_serialization(input_dt: datetime.datetime) -> str:
    """Return a nicely formatted string for time as OSCAL likes it."""
    # fail if the input datetime is not aware - ie it has no associated timezone
    if input_dt.tzinfo is None:
        raise Exception('Missing timezone in datetime')
    if input_dt.tzinfo.utcoffset(input_dt) is None:
        raise Exception('Missing utcoffset in datetime')

    # use this leave in original timezone rather than utc
    # return input_dt.astimezone().isoformat(timespec='milliseconds')  noqa: E800

    # force it to be utc
    return input_dt.astimezone(datetime.timezone.utc).isoformat(timespec='milliseconds')


class OscalBaseModel(BaseModel):
    """Base model which overrides defaults for all OSCAL classes."""

    class Config:
        """Configuration for Oscal Models."""

        json_encoders = {datetime.datetime: lambda x: robust_datetime_serialization(x)}
        # this is not safe and caused class: nan in yaml output
        # TODO: Explore fix.
        allow_population_by_field_name = True

        # Enforce strict schema
        extra = Extra.forbid

        # Validate on assignment of variables to ensure no escapes
        validate_assignment = True

    @classmethod
    def create_stripped_model_type(cls,
                                   stripped_fields: List[str] = None,
                                   stripped_fields_aliases: List[str] = None) -> Type['OscalBaseModel']:
        """Use introspection to create a model that removes the fields.

        Either 'stripped_fields' or 'stripped_fields_aliases' need to be passed, not both.
        Returns a model class definition that can be used to instanciate a model.
        """
        if stripped_fields is not None and stripped_fields_aliases is not None:
            raise err.TrestleError('Either "stripped_fields" or "stripped_fields_aliases" need to be passed, not both.')

        # create alias to field_name mapping
        excluded_fields = []
        if stripped_fields is not None:
            excluded_fields = stripped_fields
        elif stripped_fields_aliases is not None:
            alias_to_field = cls.alias_to_field_map()
            try:
                excluded_fields = [alias_to_field[key].name for key in stripped_fields_aliases]
            except KeyError as e:
                raise err.TrestleError(f'Field {str(e)} does not exists in the model')

        current_fields = cls.__fields__
        new_fields_for_model = {}
        # Build field list
        for current_mfield in current_fields.values():
            if current_mfield.name in excluded_fields:
                continue
            # Validate name in the field
            # Cehcke behaviour with an alias
            if current_mfield.required:
                new_fields_for_model[
                    current_mfield.name
                ] = (current_mfield.outer_type_, Field(..., title=current_mfield.name, alias=current_mfield.alias))
            else:
                new_fields_for_model[current_mfield.name] = (
                    Optional[current_mfield.outer_type_],
                    Field(None, title=current_mfield.name, alias=current_mfield.alias)
                )
        new_model = create_model(cls.__name__, __base__=OscalBaseModel, **new_fields_for_model)  # type: ignore
        # TODO: This typing cast should NOT be necessary. Potentially fixable with a fix to pydantic. Issue #175
        new_model = cast(Type[OscalBaseModel], new_model)

        return new_model

    def get_field_value(self, field_name_or_alias: str) -> Any:
        """Get attribute value by field alias or field name."""
        if hasattr(self, field_name_or_alias):
            return getattr(self, field_name_or_alias, None)

        return self.get_field_value_by_alias(field_name_or_alias)

    def get_field_by_alias(self, field_alias: str) -> Any:
        """Convert field alias to a field."""
        attr_field = self.alias_to_field_map().get(field_alias, None)
        return attr_field

    def get_field_value_by_alias(self, attr_alias: str) -> Optional[Any]:
        """Get attribute value by field alias."""
        # TODO: can this be restricted beyond Any easily.
        attr_field = self.get_field_by_alias(attr_alias)
        if isinstance(attr_field, ModelField):
            return getattr(self, attr_field.name, None)

        return None

    def stripped_instance(
        self, stripped_fields: List[str] = None, stripped_fields_aliases: List[str] = None
    ) -> 'OscalBaseModel':
        """Return a new model instance with the specified fields being stripped.

        Either 'stripped_fields' or 'stripped_fields_aliases' need to be passed, not both.
        """
        # stripped class type
        stripped_class: Type[OscalBaseModel] = self.create_stripped_model_type(
            stripped_fields=stripped_fields, stripped_fields_aliases=stripped_fields_aliases
        )

        # remaining values
        remaining_values = {}
        for field in self.__fields__.values():
            if field.name in stripped_class.__fields__:
                remaining_values[field.name] = self.__dict__[field.name]

        # create stripped model instance
        # TODO: Not sure if we can avoid type escapes here
        stripped_instance = stripped_class(**remaining_values)  # type: ignore

        return stripped_instance

    def oscal_write(self, path: pathlib.Path, minimize_json: bool = False) -> None:
        """
        Write oscal objects.

        OSCAL schema mandates that top level elements are wrapped in a singular
        json/yaml field. This function handles both json and yaml output as well
        as
        """
        class_name = self.__class__.__name__
        # It would be nice to pass through the description but I can't seem to and
        # it does not affect the output
        dynamic_parser = {}
        dynamic_parser[classname_to_alias(class_name, 'field')] = (
            self.__class__,
            Field(self, title=classname_to_alias(class_name, 'field'), alias=classname_to_alias(class_name, 'json'))
        )
        wrapper_model = create_model(class_name, __base__=OscalBaseModel, **dynamic_parser)  # type: ignore
        # Default behaviour is strange here.
        wrapped_model = wrapper_model(**{classname_to_alias(class_name, 'json'): self})
        #
        content_type = FileContentType.to_content_type(path.suffix)
        write_file = pathlib.Path(path).open('w', encoding=const.FILE_ENCODING)
        if content_type == FileContentType.YAML:
            yaml.dump(yaml.safe_load(wrapped_model.json(exclude_none=True, by_alias=True)), write_file)
        elif content_type == FileContentType.JSON:
            write_file.write(wrapped_model.json(exclude_none=True, by_alias=True, indent=2))
        else:
            raise err.TrestleError('Unknown file type')

    @classmethod
    def oscal_read(cls, path: pathlib.Path) -> 'OscalBaseModel':
        """
        Read OSCAL objects.

        Handles the fact OSCAL wrap's top level elements and also deals with both yaml and json.
        """
        # Create the wrapper model.
        alias = classname_to_alias(cls.__name__, 'json')

        content_type = FileContentType.to_content_type(path.suffix)

        if content_type == FileContentType.YAML:
            return cls.parse_obj(yaml.safe_load(path.open())[alias])
        elif content_type == FileContentType.JSON:
            obj = load_file(
                path,
                json_loads=cls.__config__.json_loads,
            )
            return cls.parse_obj(obj[alias])
        else:
            raise err.TrestleError('Unknown file type')

    def copy_to(self, new_oscal_type: Type['OscalBaseModel']) -> 'OscalBaseModel':
        """
        Copy operation that explicilty does type conversion.

        Input parameter is a class of type OscalBaseModel NOT a a class instance.
        """
        logger.debug('Copy to started')

        if self.__class__.__name__ == new_oscal_type.__name__:
            logger.debug('Dict based copy too ')
            return new_oscal_type.parse_obj(self.dict(exclude_none=True, by_alias=True))

        if ('__root__' in self.__fields__ and len(self.__fields__) == 1 and '__root__' in new_oscal_type.__fields__
                and len(new_oscal_type.__fields__) == 1):
            logger.debug('Root element based copy too')
            return new_oscal_type.parse_obj(self.__root__)

        # bad place here.
        raise err.TrestleError('Provided inconsistent classes.')

    def copy_from(self, existing_oscal_object: 'OscalBaseModel') -> None:
        """
        Copy operation that implicitly does type conversion.

        Typically would
        be used to set an attribute, however, does not need to be.

        Deals with two scenarios:
        1) Casting across oscal models of equivalent type. The purpose if this
        is to cross class spaces.

        2) The same as above where the item is an array style object which does
        not correctly serialize to a dict.

        3) if the from and 'to' objects are root schema elements the copy operation
        will copy the root element to the value.

        """
        recast_object = existing_oscal_object.copy_to(self.__class__)
        # This is a sanity check
        assert (self.__class__ == recast_object.__class__)
        for raw_field in self.__dict__.keys():
            self.__dict__[raw_field] = recast_object.__dict__[raw_field]

    @classmethod
    def alias_to_field_map(cls) -> Dict[str, ModelField]:
        """Create a map from field alias to field."""
        alias_to_field: Dict[str, ModelField] = {}
        for field in cls.__fields__.values():
            alias_to_field[field.alias] = field

        return alias_to_field
