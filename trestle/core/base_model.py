# modified by FixAny.py
# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""
Pydantic base model for use within trestle project and associated configuration.

The heart of the current OSCAL model within trestle is based on pydantic
(https://pydantic-docs.helpmanual.io/) which itself is a veneer on-top of python
data classes.

Functionality here defines a base-model which all trestle oscal data models inherit
from. This allows additional functionality to be easily inserted.

I can write a comment in here and you can even edit on the same line.
"""

import datetime
import logging
import pathlib
from typing import Any, Dict, List, Optional, Type, Union, cast

import orjson

from pydantic import Extra, Field, create_model
from pydantic.fields import ModelField
from pydantic.parse import load_file

from ruamel.yaml import YAML

import trestle.core.const as const
import trestle.core.err as err
from trestle.core.models.file_content_type import FileContentType
from trestle.core.trestle_base_model import TrestleBaseModel
from trestle.core.utils import classname_to_alias, get_origin, is_collection_field_type

logger = logging.getLogger(__name__)


def robust_datetime_serialization(input_dt: datetime.datetime) -> str:
    """Return a nicely formatted string for in a format compatible with OSCAL specifications.

    Args:
        input_dt: Input datetime to convert to a string.

    Returns:
        String in isoformat to the millisecond enforcing that timezone offset is provided.

    Raises:
        TrestleError: Error is raised if datetime object does not contain sufficient timezone information.
    """
    # fail if the input datetime is not aware - ie it has no associated timezone
    if input_dt.tzinfo is None:
        raise err.TrestleError('Missing timezone in datetime')
    if input_dt.tzinfo.utcoffset(input_dt) is None:
        raise err.TrestleError('Missing utcoffset in datetime')

    # use this leave in original timezone rather than utc
    # return input_dt.astimezone().isoformat(timespec='milliseconds')  noqa: E800

    # force it to be utc
    return input_dt.astimezone(datetime.timezone.utc).isoformat(timespec='milliseconds')


class OscalBaseModel(TrestleBaseModel):
    """
    Trestle defined pydantic base model for use with OSCAL pydantic dataclasses.

    This BaseModel provides two types of functionality:
    1. Overrides default configuation of the pydantic library with behaviours required for trestle
    2. Provides utility functions for trestle which are specific to OSCAL and the naming schema associated with it.
    """

    class Config:
        """Overriding configuration class for pydantic base model, for use with OSCAL data classes."""

        json_loads = orjson.loads
        # TODO: json_dumps with orjson.dumps see #840

        json_encoders = {datetime.datetime: lambda x: robust_datetime_serialization(x)}
        allow_population_by_field_name = True

        # Enforce strict schema
        extra = Extra.forbid

        # Validate on assignment of variables to ensure no escapes
        validate_assignment = True

    @classmethod
    def create_stripped_model_type(
        cls,
        stripped_fields: Optional[List[str]] = None,
        stripped_fields_aliases: Optional[List[str]] = None
    ) -> Type['OscalBaseModel']:
        """Create a pydantic model, which is derived from the current model, but missing certain fields.

        OSCAL mandates a 'strict' schema (e.g. unless otherwise stated no additional fields), and certain fields
        are mandatory. Given this the corresponding dataclasses are also strict. Workflows with trestle require missing
        mandatory fields. This allows creation of derivative models missing certain fields.

        Args:
            stripped_fields: The fields to be removed from the current data class.
            stripped_fields_aliases: The fields to be removed from the current data class provided by alias.

        Returns:
            Pydantic data class thta can be used to instanciate a model.

        Raises:
            TrestleError: If user provided both stripped_fields and stripped_field_aliases or neither.
            TrestleError: If incorrect aliases or field names are provided.
        """
        if stripped_fields is not None and stripped_fields_aliases is not None:
            raise err.TrestleError('Either "stripped_fields" or "stripped_fields_aliases" need to be passed, not both.')
        if stripped_fields is None and stripped_fields_aliases is None:
            raise err.TrestleError('Exactly one of "stripped_fields" or "stripped_fields_aliases" must be provided')

        # create alias to field_name mapping
        excluded_fields = []
        if stripped_fields is not None:
            excluded_fields = stripped_fields
        elif stripped_fields_aliases is not None:
            alias_to_field = cls.alias_to_field_map()
            try:
                excluded_fields = [alias_to_field[key].name for key in stripped_fields_aliases]
            except KeyError as e:
                raise err.TrestleError(f'Field {str(e)} does not exist in the model')

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

        Args:
            stripped_fields: The fields to be removed from the current data class.
            stripped_fields_aliases: The fields to be removed from the current data class provided by alias.

        Returns:
            The current datamodel with the fields provided removed in a derivate (run time created) data model.

        Raises:
            err.TrestleError: If user provided both stripped_fields and stripped_field_aliases or neither.
            err.TrestleError: If incorrect aliases or field names are provided.
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

    def oscal_dict(self) -> Dict[str, Any]:
        """Return a dictionary including the root wrapping object key."""
        class_name = self.__class__.__name__
        result = {}
        raw_dict = self.dict(by_alias=True, exclude_none=True)
        # Additional check to avoid root serialization
        if '__root__' in raw_dict.keys():
            result[classname_to_alias(class_name, 'json')] = raw_dict['__root__']
        else:
            result[classname_to_alias(class_name, 'json')] = raw_dict
        return result

    def oscal_serialize_json_bytes(self, pretty: bool = False, wrapped: bool = True) -> bytes:
        """
        Return an 'oscal wrapped' json object serialized in a compressed form as bytes.

        Args:
            pretty: Whether or not to pretty-print json output or have in compressed form.
        Returns:
            Oscal model serialized to a json object including packaging inside of a single top level key.
        """
        if wrapped:
            odict = self.oscal_dict()
        else:
            odict = self.dict(by_alias=True, exclude_none=True)
        if pretty:
            return orjson.dumps(odict, default=self.__json_encoder__, option=orjson.OPT_INDENT_2)
        return orjson.dumps(odict, default=self.__json_encoder__)

    def oscal_serialize_json(self, pretty: bool = False, wrapped: bool = True) -> str:
        """
        Return an 'oscal wrapped' json object serialized in a compressed form as bytes.

        Args:
            pretty: Whether or not to pretty-print json output or have in compressed form.
        Returns:
            Oscal model serialized to a json object including packaging inside of a single top level key.
        """
        # This function is provided for backwards compatibility
        return self.oscal_serialize_json_bytes(pretty, wrapped).decode(const.FILE_ENCODING)

    def oscal_write(self, path: pathlib.Path) -> None:
        """
        Write out a pydantic data model in an oscal friendly way.

        OSCAL schema mandates that top level elements are wrapped in a singular
        json/yaml field. This function handles both json and yaml output as well
        as formatting of the json.

        Args:
            path: The output file location for the oscal object.

        Raises:
            err.TrestleError: If a unknown file extension is provided.
        """
        content_type = FileContentType.to_content_type(path.suffix)
        # The output will have \r\n newlines on windows and \n newlines elsewhere

        if content_type == FileContentType.YAML:
            write_file = pathlib.Path(path).open('w', encoding=const.FILE_ENCODING)
            yaml = YAML(typ='safe')
            yaml.dump(yaml.load(self.oscal_serialize_json()), write_file)
            write_file.flush()
            write_file.close()
        elif content_type == FileContentType.JSON:
            write_file = pathlib.Path(path).open('wb')
            write_file.write(self.oscal_serialize_json_bytes(pretty=True))
            # Flush / close required (by experience) due to flushing issues in tests.
            write_file.flush()
            write_file.close()

    @classmethod
    def oscal_read(cls, path: pathlib.Path) -> 'OscalBaseModel':
        """
        Read OSCAL objects.

        Handles the fact OSCAL wraps top level elements and also deals with both yaml and json.

        Args:
            path: The path of the oscal object to read.
        Returns:
            The oscal object read into trestle oscal models.
        """
        # Create the wrapper model.
        alias = classname_to_alias(cls.__name__, 'json')

        content_type = FileContentType.to_content_type(path.suffix)
        logger.debug(f'oscal_read content type {content_type} and alias {alias} from {path}')

        if not path.exists():
            logger.warning(f'path does not exist in oscal_read: {path}')
            return None

        obj: Dict[str, Any] = {}
        try:
            if content_type == FileContentType.YAML:
                yaml = YAML(typ='safe')
                fh = path.open('r', encoding=const.FILE_ENCODING)
                obj = yaml.load(fh)
                fh.close()
            elif content_type == FileContentType.JSON:
                obj = load_file(
                    path,
                    json_loads=cls.__config__.json_loads,
                )
        except Exception as e:
            raise err.TrestleError(f'Error loading file {path} {str(e)}')
        try:
            if not len(obj) == 1:
                logger.error('Provided oscal file does not have a single top level key wrapping it.')
                logger.error(f'It has {len(obj)} keys.')
                raise err.TrestleError('Invalid OSCAL file structure, multiple base keys.')
            parsed = cls.parse_obj(obj[alias])
        except KeyError:
            logger.error(f'Provided oscal file does not have top level key: {alias}')
            raise err.TrestleError(f'Provided oscal file does not have top level key key: {alias}')
        except Exception as e:
            logger.error(f'Failed to parse OSCAL object: {e}')
            raise err.TrestleError(f'Error parsing file {path} {str(e)}')
        return parsed

    def copy_to(self, new_oscal_type: Type['OscalBaseModel']) -> 'OscalBaseModel':
        """
        Opportunistic copy operation between similar types of data classes.

        Due to the way in which oscal is constructed we get a set of similar / the same definition across various
        oscal models. Due to the lack of guarantees that they are the same we cannot easily 'collapse' the mode.

        Args:
            new_oscal_type: The desired type of oscal model

        Returns:
            Opportunistic copy of the data into the new model type.
        """
        logger.debug('Copy to started')
        if self.__class__.__name__ == new_oscal_type.__name__:
            logger.debug('Json based copy')
            # Note: Json based oppportunistic copy
            # Dev notes: Do not change this from json. Due to enums (in particular) json is the closest we can get.
            return new_oscal_type.parse_raw(self.oscal_serialize_json(pretty=False, wrapped=False))

        if ('__root__' in self.__fields__ and len(self.__fields__) == 1 and '__root__' in new_oscal_type.__fields__
                and len(new_oscal_type.__fields__) == 1):
            logger.debug('Root element based copy too')
            return new_oscal_type.parse_obj(self.__root__)

        # bad place here.
        raise err.TrestleError('Provided inconsistent classes to copy to methodology.')

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

        Args:
            existing_oscal_object: The oscal object where fields are copied from.

        """
        recast_object = existing_oscal_object.copy_to(self.__class__)
        for raw_field in self.__dict__:
            self.__dict__[raw_field] = recast_object.__dict__[raw_field]

    @classmethod
    def alias_to_field_map(cls) -> Dict[str, ModelField]:
        """Create a map from field alias to field.

        Returns:
            A dict which has key's of aliases and Fields as values.
        """
        alias_to_field: Dict[str, ModelField] = {}
        for field in cls.__fields__.values():
            alias_to_field[field.alias] = field

        return alias_to_field

    @classmethod
    def is_collection_container(cls) -> bool:
        """
        Determine whether a pydantic model has being created to wrap a collection primitive (e.g a list or dict).

        In performing model decomposition it is possible using trestle framework to automatically generate a model
        which looks like

        class Foo(OscalBaseModel):
            __root__: List[Bar]

        Returns:
            Boolean on if it meets the above criteria

        When these cases exist we need special handling of the type information.
        """
        # Additional sanity check on field length
        if len(cls.__fields__) == 1 and '__root__' in cls.__fields__:
            # This is now a __root__ key only model
            if is_collection_field_type(cls.__fields__['__root__'].outer_type_):
                return True
        return False

    @classmethod
    def get_collection_type(cls) -> Union[Type[List[Any]], Type[Dict[Any, Any]]]:
        """
        If the type wraps an collection, return the collection type.

        Returns:
            The collection type.

        Raises:
            err.TrestleError: if not a wrapper of the collection type.
        """
        if not cls.is_collection_container():
            raise err.TrestleError('OscalBaseModel is not wrapping a collection type')
        return get_origin(cls.__fields__['__root__'].outer_type_)
