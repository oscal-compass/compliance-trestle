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
from typing import List, Optional, Type

from pydantic import BaseModel, Extra, Field, create_model

import trestle.core.err as err
import trestle.core.utils as utils

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
        allow_population_by_field_name = True  # noqa: E800

        # Enforce strict schema
        extra = Extra.forbid

        # Validate on assignment of variables to ensure no escapes
        validate_assignment = True

    @classmethod
    def create_stripped_model_type(cls, fields: List[str]) -> 'OscalBaseModel':
        """Use introspection to create a model that removes the fields.

        Returns a model class definition that can be used to instanciate a model.
        """
        current_fields = cls.__fields__
        new_fields_for_model = {}
        # Build field list
        for current_mfield in current_fields.values():
            if current_mfield.name in fields:
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
        new_model = create_model('partial-' + cls.__class__.__name__, __base__=OscalBaseModel, **new_fields_for_model)

        return new_model

    def oscal_write(self, path: pathlib.Path, minimize_json=False) -> None:
        """
        Write oscal objects.

        OSCAL schema mandates that top level elements are wrapped in a singular
        json/yaml field. This function handles both json and yaml output as well
        as
        """
        class_name = self.__class__.__name__
        # It would be nice to pass through the description but I can't seem to and
        # it does not affect the output
        dynamic_passer = {}
        dynamic_passer[utils.class_to_oscal(class_name, 'field')] = (
            self.__class__,
            Field(
                self, title=utils.class_to_oscal(class_name, 'field'), alias=utils.class_to_oscal(class_name, 'json')
            )
        )
        wrapper_model = create_model(class_name, __base__=OscalBaseModel, **dynamic_passer)
        # Default behaviour is strange here.
        wrapped_model = wrapper_model(**{utils.class_to_oscal(class_name, 'json'): self})

        yaml_suffix = ['.yaml', '.yml']
        json_suffix = ['.json']
        encoding = 'utf8'
        write_file = pathlib.Path(path).open('w', encoding=encoding)
        if path.suffix in yaml_suffix:
            yaml.dump(yaml.safe_load(wrapped_model.json(exclude_none=True, by_alias=True)), write_file)
            pass
        elif path.suffix in json_suffix:
            write_file.write(wrapped_model.json(exclude_none=True, by_alias=True, indent=2))

        else:
            raise err.TrestleError('Unknown file type')

    @classmethod
    def oscal_read(cls, path: pathlib.Path) -> 'OscalBaseModel':
        """
        Read OSCAL objects.

        Handles the fact OSCAL wrap's top level elements and also deals with both yaml and json.
        """
        # Define valid extensions
        yaml_suffix = ['.yaml', '.yml']
        json_suffix = ['.json']
        # Create the wrapper model.
        class_name = cls.__name__
        dynamic_passer = {}
        dynamic_passer[utils.class_to_oscal(class_name, 'field')] = (
            cls,
            Field(..., title=utils.class_to_oscal(class_name, 'json'), alias=utils.class_to_oscal(class_name, 'json'))
        )
        wrapper_model = create_model('Wrapped' + class_name, __base__=OscalBaseModel, **dynamic_passer)

        if path.suffix in yaml_suffix:
            return wrapper_model.parse_obj(yaml.safe_load(path.open())
                                           ).__dict__[utils.class_to_oscal(class_name, 'field')]
        elif path.suffix in json_suffix:
            return wrapper_model.parse_file(path).__dict__[utils.class_to_oscal(class_name, 'field')]
        else:
            raise err.TrestleError('Unknown file type')

    def copy_to(self, new_oscal_type: Type['OscalBaseModel']) -> 'OscalBaseModel':
        """
        Copy operation that explicilty does type conversion.

        Input parameter is a class of type OscalBaseModel NOT a a class isntance.
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

    def copy_from(self, existing_oscal_object: 'OscalBaseModel') -> 'OscalBaseModel':
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
