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
Pydantic base model for use within a trestle workspace and associated configuration.

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
import types
from typing import Any, Dict, List, Optional, Type, Union, cast, get_args

import orjson

from pydantic import AnyUrl, ConfigDict, Field, RootModel, create_model
from pydantic_core import PydanticUndefined

from ruamel.yaml import YAML

import trestle.common.const as const
import trestle.common.err as err
from trestle.common.str_utils import AliasMode, classname_to_alias
from trestle.common.type_utils import get_origin, is_collection_field_type
from trestle.core.models.file_content_type import FileContentType
from trestle.core.trestle_base_model import TrestleBaseModel

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


def _orjson_default(obj: Any) -> Any:
    """Default handler for orjson serialization of non-standard types."""
    if isinstance(obj, datetime.datetime):
        return robust_datetime_serialization(obj)
    if isinstance(obj, AnyUrl):
        return str(obj)
    raise TypeError(f'Object of type {type(obj).__name__} is not JSON serializable')


class OscalBaseModel(TrestleBaseModel):
    """
    Trestle defined pydantic base model for use with OSCAL pydantic dataclasses.

    This BaseModel provides two types of functionality:
    1. Overrides default configuation of the pydantic library with behaviours required for trestle
    2. Provides utility functions for trestle which are specific to OSCAL and the naming schema associated with it.
    """

    model_config = ConfigDict(
        # TODO: json_dumps with orjson.dumps see #840
        json_encoders={datetime.datetime: lambda x: robust_datetime_serialization(x)},
        populate_by_name=True,
        # Enforce strict schema
        extra='forbid',
        # Validate on assignment of variables to ensure no escapes
        validate_assignment=True,
    )

    def __eq__(self, other: Any) -> bool:
        """Compare two OscalBaseModel instances, treating stripped model variants of the same type as equal."""
        if not isinstance(other, OscalBaseModel):
            return NotImplemented
        # If both have the same class, use the standard pydantic comparison
        if type(self) is type(other):
            return super().__eq__(other)
        # For stripped model variants (same __name__, different class objects), compare by data
        if self.__class__.__name__ == other.__class__.__name__:
            return self.model_dump(by_alias=True) == other.model_dump(by_alias=True)
        return False

    @classmethod
    def create_stripped_model_type(
        cls, stripped_fields: Optional[List[str]] = None, stripped_fields_aliases: Optional[List[str]] = None
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

        new_fields_for_model = {}
        # Build field list
        for field_name, field_info in cls.model_fields.items():
            if field_name in excluded_fields:
                continue
            field_alias = field_info.alias or field_name
            is_required = field_info.default is PydanticUndefined and field_info.default_factory is None
            if is_required:
                new_fields_for_model[field_name] = (
                    field_info.annotation,
                    Field(..., title=field_name, alias=field_alias),
                )
            else:
                new_fields_for_model[field_name] = (
                    Optional[field_info.annotation],
                    Field(None, title=field_name, alias=field_alias),
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
        if attr_field is not None:
            return getattr(self, attr_field.name, None)

        return None

    def stripped_instance(
        self, stripped_fields: Optional[List[str]] = None, stripped_fields_aliases: Optional[List[str]] = None
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
        for field_name in self.model_fields:
            if field_name in stripped_class.model_fields:
                remaining_values[field_name] = getattr(self, field_name)

        # create stripped model instance
        # TODO: Not sure if we can avoid type escapes here
        stripped_instance = stripped_class(**remaining_values)

        return stripped_instance

    def oscal_dict(self) -> Dict[str, Any]:
        """Return a dictionary including the root wrapping object key."""
        class_name = self.__class__.__name__
        data = self.model_dump(by_alias=True, exclude_none=True)
        # For OscalBaseModel collection containers, unwrap the 'root' key to avoid extra nesting
        if not isinstance(self, RootModel) and type(self).is_collection_container():
            return {classname_to_alias(class_name, AliasMode.JSON): data.get('root', [])}
        # RootModel.model_dump() returns the root value directly; regular models return a field dict
        return {classname_to_alias(class_name, AliasMode.JSON): data}

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
            odict = self.model_dump(by_alias=True, exclude_none=True)
        if pretty:
            return orjson.dumps(odict, default=_orjson_default, option=orjson.OPT_INDENT_2)
        return orjson.dumps(odict, default=_orjson_default)

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
            with pathlib.Path(path).open('w', encoding=const.FILE_ENCODING) as write_file:
                yaml = YAML(typ='safe')
                yaml.dump(yaml.load(self.oscal_serialize_json()), write_file)
        elif content_type == FileContentType.JSON:
            with pathlib.Path(path).open('wb') as write_file:
                write_file.write(self.oscal_serialize_json_bytes(pretty=True))

    @classmethod
    def oscal_read(cls, path: pathlib.Path) -> Optional['OscalBaseModel']:
        """
        Read OSCAL objects.

        Handles the fact OSCAL wraps top level elements and also deals with both yaml and json.

        Args:
            path: The path of the oscal object to read.
        Returns:
            The oscal object read into trestle oscal models.
        """
        # Create the wrapper model.
        alias = classname_to_alias(cls.__name__, AliasMode.JSON)

        content_type = FileContentType.to_content_type(path.suffix)
        logger.debug(f'oscal_read content type {content_type} and alias {alias} from {path}')

        if not path.exists():
            logger.warning(f'path does not exist in oscal_read: {path}')
            return None

        obj: Dict[str, Any] = {}
        try:
            if content_type == FileContentType.YAML:
                yaml = YAML(typ='safe')
                with path.open('r', encoding=const.FILE_ENCODING) as fh:
                    obj = yaml.load(fh)
            elif content_type == FileContentType.JSON:
                obj = orjson.loads(path.read_bytes())
        except Exception as e:
            raise err.TrestleError(f'Error loading file {path} {str(e)}')
        try:
            if not len(obj) == 1:
                raise err.TrestleError(
                    f'Invalid OSCAL file structure, oscal file '
                    f'does not have a single top level key wrapping it. It has {len(obj)} keys.'
                )
            model_fields = getattr(cls, 'model_fields', {})
            is_collection_container = False
            if hasattr(cls, 'is_collection_container'):
                is_collection_container = cls.is_collection_container()
            elif len(model_fields) == 1 and 'root' in model_fields:
                is_collection_container = is_collection_field_type(model_fields['root'].annotation)
            payload = obj[alias]
            # RootModel wrappers validate against the raw payload, while legacy BaseModel
            # wrappers still expect the value under the root field name.
            if is_collection_container:
                parsed = cls.model_validate(payload if issubclass(cls, RootModel) else {'root': payload})
            else:
                parsed = cls.model_validate(payload)
        except KeyError:
            raise err.TrestleError(f'Provided oscal file does not have top level key key: {alias}')
        except Exception as e:
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
            return new_oscal_type.model_validate_json(self.oscal_serialize_json(pretty=False, wrapped=False))

        if isinstance(self, RootModel) and issubclass(new_oscal_type, RootModel):
            logger.debug('Root element based copy too')
            return new_oscal_type.model_validate(self.root)

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
    def alias_to_field_map(cls) -> Dict[str, Any]:
        """Create a map from field alias to field.

        Returns:
            A dict with aliases as keys and SimpleNamespace objects (with .name and .alias attributes) as values.
        """
        alias_to_field: Dict[str, Any] = {}
        for field_name, field_info in cls.model_fields.items():
            alias = field_info.alias or field_name
            outer_type = field_info.annotation
            if get_origin(outer_type) is Union:
                non_none_types = [arg for arg in get_args(outer_type) if arg is not type(None)]
                if len(non_none_types) == 1:
                    outer_type = non_none_types[0]
            inner_type = outer_type
            if get_origin(outer_type) in (list, dict):
                collection_args = get_args(outer_type)
                if collection_args:
                    inner_type = collection_args[-1]
            # Maintain v1-style attributes used by older utility code/tests.
            alias_to_field[alias] = types.SimpleNamespace(
                name=field_name,
                alias=alias,
                field_info=field_info,
                outer_type_=outer_type,
                type_=inner_type,
            )

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
        if len(cls.model_fields) == 1 and 'root' in cls.model_fields:
            # This is a RootModel wrapping a collection
            if is_collection_field_type(cls.model_fields['root'].annotation):
                return True
        return False

    @classmethod
    def get_collection_type(cls) -> Optional[type]:
        """
        If the type wraps an collection, return the collection type.

        Returns:
            The collection type.

        Raises:
            err.TrestleError: if not a wrapper of the collection type.
        """
        if not cls.is_collection_container():
            raise err.TrestleError('OscalBaseModel is not wrapping a collection type')
        return get_origin(cls.model_fields['root'].annotation)


class OscalRootModel(RootModel):  # type: ignore[type-arg]
    """Base class for OSCAL root-model types, providing copy_to/copy_from analogous to OscalBaseModel."""

    def copy_to(self, new_oscal_type: Type['OscalRootModel']) -> 'OscalRootModel':
        """Copy root value to a compatible root-model type."""
        if issubclass(new_oscal_type, RootModel):
            return new_oscal_type.model_validate(self.root)
        raise err.TrestleError(f'Cannot copy_to {new_oscal_type.__name__} from {self.__class__.__name__}')

    def copy_from(self, existing_oscal_object: 'OscalRootModel') -> None:
        """Copy root value from another root-model object."""
        recast = existing_oscal_object.copy_to(self.__class__)
        self.root = recast.root
