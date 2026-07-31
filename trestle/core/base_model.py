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
from typing import Any, Dict, List, Optional, Type, cast

import orjson

from pydantic import AnyUrl, ConfigDict, Field, RootModel, ValidationError, create_model, field_serializer
from pydantic.fields import FieldInfo
from pydantic_core import ErrorDetails, from_json

from ruamel.yaml import YAML

import trestle.common.const as const
import trestle.common.err as err
from trestle.common.file_utils import load_file
from trestle.common.str_utils import AliasMode, classname_to_alias
from trestle.common.type_utils import get_origin, is_collection_field_type
from trestle.core.canonicalization import canonicalize_json_text
from trestle.core.models.file_content_type import FileContentType
from trestle.core.trestle_base_model import TrestleBaseModel

logger = logging.getLogger(__name__)


class FieldWrapper:
    """Wrapper for FieldInfo that includes the field name for Pydantic v2 compatibility.

    **Why this exists:** In Pydantic v1, ``ModelField`` carried both the field name and its
    metadata. Pydantic v2 replaced ``ModelField`` with ``FieldInfo``, which no longer stores
    the field name — only ``model_fields`` (a ``dict[name, FieldInfo]``) knows the mapping.
    ``FieldWrapper`` re-attaches that name so downstream code can treat it as a drop-in for
    the old ``ModelField``.

    **Call-site inventory (update when adding / removing uses):**
    * ``OscalBaseModel.alias_to_field_map`` — constructs wrappers from ``model_fields``
    * ``OscalBaseModel.get_field_value_by_alias`` — checks ``isinstance(x, FieldWrapper)``

    **TODO (migration):** If a future Pydantic release re-exposes the field name on
    ``FieldInfo`` directly, ``FieldWrapper`` can be removed. At that point:
    1. Replace every ``FieldWrapper(name, info)`` construction with plain ``info``.
    2. Replace ``attr_field.name`` accesses with whatever the new ``FieldInfo`` attribute is.
    3. Drop the ``isinstance(attr_field, FieldWrapper)`` guard in
       ``get_field_value_by_alias``.
    4. Remove this class.
    Track the upstream issue at https://github.com/pydantic/pydantic/issues.
    """

    def __init__(self, name: str, field_info: FieldInfo) -> None:
        """Initialize with field name and FieldInfo."""
        self.name = name
        self.field_info = field_info

    def __getattr__(self, item: str) -> Any:
        """Delegate attribute access to the wrapped FieldInfo."""
        return getattr(self.field_info, item)


def robust_datetime_serialization(input_dt: datetime.datetime) -> str:
    """Serialize a datetime to an OSCAL-compatible ISO-8601 string with explicit UTC offset.

    The output always uses ``+00:00`` (not ``Z``) as the UTC designator, which is the
    form expected by the OSCAL JSON schemas.

    **Precision behaviour (changed from trestle v1):**
    Previously all datetimes were serialized with millisecond precision, e.g.
    ``2024-01-01T00:00:00.000+00:00``. This function now omits sub-second precision
    when the microsecond component is zero, producing ``2024-01-01T00:00:00+00:00``
    instead. Both forms are valid ISO-8601 and accepted by OSCAL validators.
    Consumers that rely on exact string comparison of stored datetimes should be
    updated to use datetime-aware comparison instead.

    Args:
        input_dt: Input datetime to serialize. Must be timezone-aware.

    Returns:
        UTC ISO-8601 string with ``+00:00`` offset.
        Sub-second precision is included only when microseconds are non-zero.

    Raises:
        TrestleError: If the datetime has no timezone info or no UTC offset.
    """
    # fail if the input datetime is not aware - ie it has no associated timezone
    if input_dt.tzinfo is None:
        raise err.TrestleError('Missing timezone in datetime')
    if input_dt.tzinfo.utcoffset(input_dt) is None:
        raise err.TrestleError('Missing utcoffset in datetime')

    # Normalise to UTC so the offset is always +00:00 (not e.g. -05:00)
    dt_utc = input_dt.astimezone(datetime.timezone.utc)

    # Omit sub-second precision when microseconds are zero to keep output compact.
    # Include milliseconds when microseconds are set so no precision is lost.
    if dt_utc.microsecond == 0:
        return dt_utc.isoformat(timespec='seconds')
    else:
        return dt_utc.isoformat(timespec='milliseconds')


class OscalBaseModel(TrestleBaseModel):
    """
    Trestle defined pydantic base model for use with OSCAL pydantic dataclasses.

    This BaseModel provides two types of functionality:
    1. Overrides default configuation of the pydantic library with behaviours required for trestle
    2. Provides utility functions for trestle which are specific to OSCAL and the naming schema associated with it.
    """

    model_config = ConfigDict(
        # Allow population by field name
        populate_by_name=True,
        # Enforce strict schema
        extra='forbid',
        # Validate on assignment of variables to ensure no escapes
        validate_assignment=True,
        # Configure timedelta serialization to ISO 8601
        ser_json_timedelta='iso8601',
        # Note: orjson is used for JSON *output* only (see oscal_serialize_json_bytes).
        # Pydantic v2 removed json_loads from ConfigDict; parsing is handled by pydantic-core.
    )

    @field_serializer('*', mode='wrap', when_used='json')
    def serialize_oscal_fields(self, value: Any, handler: Any, _info: Any) -> Any:
        """Targeted serializer for the two OSCAL-specific output concerns.

        - datetime → robust_datetime_serialization (+00:00 offset, not Z)
        - AnyUrl   → str  (Pydantic v2 AnyUrl is no longer a str subclass)

        All other field types are passed straight through to Pydantic's default
        handler via handler(value), so only these two types incur extra work.
        """
        if isinstance(value, datetime.datetime):
            return robust_datetime_serialization(value)
        if isinstance(value, AnyUrl):
            return str(value)
        return handler(value)

    def __eq__(self, other: object) -> bool:
        """Override equality to compare model content for dynamically created models.

        Pydantic v2 changed equality behavior to be stricter - it checks isinstance(other, self.__class__)
        which fails for dynamically created models from different create_model() calls (e.g.
        stripped models returned by create_stripped_model_type).

        This override restores Pydantic v1 behavior: compare by class name and field values,
        allowing dynamically created models with the same name and identical content to be equal.

        Uses __dict__ for field comparison — it holds the already-in-memory field values
        and avoids the O(n) deep serialization cost of model_dump().
        """
        if not isinstance(other, TrestleBaseModel):
            return False

        if self.__class__.__name__ != other.__class__.__name__:
            return False

        # Compare field values directly from __dict__ — no serialization needed.
        # __pydantic_fields_set__ is excluded; we compare only the field values themselves.
        self_fields = {k: v for k, v in self.__dict__.items() if not k.startswith('__')}
        other_fields = {k: v for k, v in other.__dict__.items() if not k.startswith('__')}
        return self_fields == other_fields

    @classmethod
    def _validate_stripped_fields_params(
        cls, stripped_fields: Optional[List[str]], stripped_fields_aliases: Optional[List[str]]
    ) -> None:
        """Validate that exactly one of stripped_fields or stripped_fields_aliases is provided."""
        if stripped_fields is not None and stripped_fields_aliases is not None:
            raise err.TrestleError('Either "stripped_fields" or "stripped_fields_aliases" need to be passed, not both.')
        if stripped_fields is None and stripped_fields_aliases is None:
            raise err.TrestleError('Exactly one of "stripped_fields" or "stripped_fields_aliases" must be provided')

    @classmethod
    def _resolve_excluded_fields(
        cls, stripped_fields: Optional[List[str]], stripped_fields_aliases: Optional[List[str]]
    ) -> List[str]:
        """Resolve the list of field names to exclude from aliases or direct field names."""
        if stripped_fields is not None:
            return stripped_fields

        # At this point, stripped_fields_aliases must be non-None due to validation
        if stripped_fields_aliases is None:
            return []

        # Map aliases to field names
        alias_to_name = {}
        for field_name, field_info in cls.model_fields.items():
            alias = field_info.alias if field_info.alias else field_name
            alias_to_name[alias] = field_name

        try:
            return [alias_to_name[key] for key in stripped_fields_aliases]
        except KeyError as e:
            raise err.TrestleError(f'Field {str(e)} does not exist in the model')

    @classmethod
    def _build_new_field_definition(cls, field_name: str, field_info: FieldInfo) -> tuple[Any, Any]:
        """Build a field definition tuple for create_model."""
        if field_info.is_required():
            return (field_info.annotation, Field(..., title=field_name, alias=field_info.alias))
        return (Optional[field_info.annotation], Field(None, title=field_name, alias=field_info.alias))

    @classmethod
    def _build_fields_dict(cls, excluded_fields: List[str]) -> Dict[str, tuple[Any, Any]]:
        """Build dictionary of fields excluding specified field names.

        Args:
            excluded_fields: List of field names to exclude from the model.

        Returns:
            Dictionary mapping field names to their field definitions.
        """
        new_fields = {}
        for field_name, field_info in cls.model_fields.items():
            if field_name not in excluded_fields:
                new_fields[field_name] = cls._build_new_field_definition(field_name, field_info)
        return new_fields

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
        cls._validate_stripped_fields_params(stripped_fields, stripped_fields_aliases)
        excluded_fields = cls._resolve_excluded_fields(stripped_fields, stripped_fields_aliases)
        new_fields_for_model = cls._build_fields_dict(excluded_fields)

        new_model = create_model(cls.__name__, __base__=OscalBaseModel, **new_fields_for_model)  # type: ignore
        # TODO: This typing cast should NOT be necessary. Potentially fixable with a fix to pydantic. Issue #175
        return cast(Type[OscalBaseModel], new_model)

    def get_field_by_alias(self, field_alias: str) -> Any:
        """Convert field alias to a field."""
        return self.alias_to_field_map().get(field_alias, None)

    def get_field_value_by_alias(self, attr_alias: str) -> Optional[Any]:
        """Get attribute value by field alias."""
        # TODO: can this be restricted beyond Any easily.
        attr_field = self.get_field_by_alias(attr_alias)
        if isinstance(attr_field, FieldWrapper):
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
        for field_name in self.__class__.model_fields.keys():
            if field_name in stripped_class.model_fields:
                remaining_values[field_name] = self.__dict__[field_name]

        # create stripped model instance
        # TODO: Not sure if we can avoid type escapes here
        stripped_instance = stripped_class(**remaining_values)

        return stripped_instance

    def oscal_dict(self) -> Dict[str, Any]:
        """Return a dictionary including the root wrapping object key."""
        class_name = self.__class__.__name__
        result = {}
        # Use mode='json' to properly serialize all types including AnyUrl
        # The field_serializer handles datetime formatting
        raw_dict = self.model_dump(by_alias=True, exclude_none=True, mode='json')
        # Additional check to avoid root serialization (Pydantic v2 RootModel uses 'root')
        if 'root' in raw_dict.keys():
            result[classname_to_alias(class_name, AliasMode.JSON)] = raw_dict['root']
        else:
            result[classname_to_alias(class_name, AliasMode.JSON)] = raw_dict
        return result

    def oscal_serialize_json_bytes(self, pretty: bool = False, wrapped: bool = True, canonical: bool = False) -> bytes:
        """
        Return an 'oscal wrapped' json object serialized in a compressed form as bytes.

        Args:
            pretty: Whether or not to pretty-print json output or have in compressed form.
            canonical: Whether or not to return RFC 8785 canonical JSON bytes.
        Returns:
            Oscal model serialized to a json object including packaging inside of a single top level key.
        """
        if wrapped:
            odict = self.oscal_dict()
        else:
            # Use mode='json' to properly serialize all types including AnyUrl
            # The field_serializer handles datetime formatting
            odict = self.model_dump(by_alias=True, exclude_none=True, mode='json')
        if canonical:
            json_bytes = orjson.dumps(odict)
            _, canonical_bytes = canonicalize_json_text(json_bytes.decode(const.FILE_ENCODING))
            return canonical_bytes
        if pretty:
            return orjson.dumps(odict, option=orjson.OPT_INDENT_2)
        return orjson.dumps(odict)

    def oscal_serialize_json(self, pretty: bool = False, wrapped: bool = True, canonical: bool = False) -> str:
        """
        Return an 'oscal wrapped' json object serialized in a compressed form as bytes.

        Args:
            pretty: Whether or not to pretty-print json output or have in compressed form.
            canonical: Whether or not to return RFC 8785 canonical JSON.
        Returns:
            Oscal model serialized to a json object including packaging inside of a single top level key.
        """
        # This function is provided for backwards compatibility
        return self.oscal_serialize_json_bytes(pretty, wrapped, canonical).decode(const.FILE_ENCODING)

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
        content_type = FileContentType.path_suffix_to_content_type(path)
        # The output will have \r\n newlines on windows and \n newlines elsewhere

        if content_type == FileContentType.YAML:
            with pathlib.Path(path).open('w', encoding=const.FILE_ENCODING) as write_file:
                yaml = YAML(typ='safe')
                yaml.dump(yaml.load(self.oscal_serialize_json()), write_file)
        elif content_type == FileContentType.JSON:
            with pathlib.Path(path).open('wb') as write_file:
                write_file.write(self.oscal_serialize_json_bytes(pretty=True))
        elif content_type == FileContentType.CANONICAL_JSON:
            with pathlib.Path(path).open('wb') as write_file:
                write_file.write(self.oscal_serialize_json_bytes(canonical=True))

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

        content_type = FileContentType.path_suffix_to_content_type(path)
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
            elif content_type in [FileContentType.JSON, FileContentType.CANONICAL_JSON]:
                obj = load_file(path)
        except Exception as e:
            raise err.TrestleError(f'Error loading file {path} {str(e)}')
        try:
            if not len(obj) == 1:
                raise err.TrestleError(
                    f'Invalid OSCAL file structure, oscal file '
                    f'does not have a single top level key wrapping it. It has {len(obj)} keys.'
                )
            parsed = cls.model_validate(obj[alias])
        except KeyError:
            raise err.TrestleError(f'Provided oscal file does not have top level key key: {alias}')
        except ValidationError as e:
            raise err.TrestleError(_format_validation_error(path, e))
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

        if (
            'root' in self.__class__.model_fields
            and len(self.__class__.model_fields) == 1
            and 'root' in new_oscal_type.model_fields
            and len(new_oscal_type.model_fields) == 1
        ):
            logger.debug('Root element based copy too (Pydantic v2 RootModel)')
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
    def alias_to_field_map(cls) -> Dict[str, FieldWrapper]:
        """Create a map from field alias to field.

        Returns:
            A dict which has key's of aliases and FieldWrapper as values.
        """
        alias_to_field: Dict[str, FieldWrapper] = {}
        for field_name, field_info in cls.model_fields.items():
            wrapper = FieldWrapper(field_name, field_info)
            if field_info.alias:
                alias_to_field[field_info.alias] = wrapper
            else:
                alias_to_field[field_name] = wrapper

        return alias_to_field

    @classmethod
    def is_collection_container(cls) -> bool:
        """
        Determine whether a pydantic model has being created to wrap a collection primitive (e.g a list or dict).

        In performing model decomposition it is possible using trestle framework to automatically generate a model
        which looks like

        class Foo(OscalBaseModel):
            root: List[Bar]  # Pydantic v2 RootModel uses 'root' field

        Returns:
            Boolean on if it meets the above criteria

        When these cases exist we need special handling of the type information.
        """
        # Additional sanity check on field length (Pydantic v2 RootModel uses 'root')
        if len(cls.model_fields) == 1 and 'root' in cls.model_fields:
            # This is now a root key only model (RootModel in Pydantic v2)
            annotation = cls.model_fields['root'].annotation
            if annotation is not None and is_collection_field_type(annotation):
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
        annotation = cls.model_fields['root'].annotation
        if annotation is None:
            raise err.TrestleError('root field has no annotation (Pydantic v2 RootModel)')
        return get_origin(annotation)


def _format_validation_error(path: pathlib.Path, exc: ValidationError) -> str:
    """Translate a pydantic ValidationError into actionable human-readable lines.

    Produces one deduplicated line per unique (field-path, error-type) pair:
        <json-path>: <plain-english problem> (got: <value>)

    Pydantic union-variant labels (e.g. "ConfidenceScore1", "list[Mapping]")
    are stripped from paths — they are internal type names, not OSCAL field names.
    """
    import re as _re

    def _loc_to_path(loc: tuple[int | str, ...]) -> str:
        parts: list[str] = []
        for seg in loc:
            if isinstance(seg, int):
                parts.append(f'[{seg}]')
            else:
                s = str(seg)
                # Skip pydantic union-variant labels: uppercase class names or "list[...]"
                if _re.match(r'^[A-Z]|^list\[', s):
                    continue
                parts.append(s)
        result = ''
        for part in parts:
            if part.startswith('['):
                result += part
            elif result:
                result += '.' + part
            else:
                result = part
        return result or '(root)'

    def _human_message(error: ErrorDetails) -> str:
        etype = error['type']
        ctx = error.get('ctx', {})
        if etype == 'missing':
            return 'required field is missing'
        if etype == 'extra_forbidden':
            return f'unexpected field — remove "{error["loc"][-1]}"'
        if etype == 'model_type':
            cls_name = ctx.get('class_name', 'object')
            return f'must be a JSON object ({cls_name}), not {type(error["input"]).__name__}'
        if etype in ('string_pattern_mismatch', 'string_pattern'):
            pattern = ctx.get('pattern', '')
            if len(pattern) > 40:
                return 'value does not match the required format (e.g. UUID or token)'
            return f'value does not match required pattern: {pattern}'
        if etype in ('datetime_from_date_parsing', 'datetime_parsing'):
            detail = ctx.get('error', error['msg'])
            return f'invalid date/time — {detail}'
        if etype == 'list_type':
            return 'must be a JSON array'
        if etype == 'enum':
            allowed = ctx.get('expected', '')
            return f'invalid value; allowed: {allowed}'
        return error['msg']

    lines = [f'Schema validation failed — {path}:']
    seen: set[tuple[str, str]] = set()
    for error in exc.errors():
        loc_str = _loc_to_path(error['loc'])
        etype = error['type']
        key = (loc_str, etype)
        if key in seen:
            continue
        seen.add(key)
        msg = _human_message(error)
        raw = error.get('input')
        input_repr = repr(raw)
        if len(input_repr) > 60:
            input_repr = input_repr[:57] + '...'
        lines.append(f'  {loc_str}: {msg} (got: {input_repr})')
    return '\n'.join(lines)


class OscalRootModel(RootModel[Any]):
    """
    Trestle defined pydantic RootModel for wrapping collection types.

    This is used for dynamically created models that wrap List or Dict types.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        # Note: RootModel does not support extra='forbid'
    )

    @classmethod
    def oscal_read(cls, path: pathlib.Path) -> Optional['OscalRootModel']:
        """Read from OSCAL JSON/YAML file."""
        return OscalBaseModel.oscal_read.__func__(cls, path)

    def oscal_write(self, path: pathlib.Path) -> None:
        """Write to OSCAL JSON/YAML file."""
        return OscalBaseModel.oscal_write(cast(Any, self), path)

    @classmethod
    def alias_to_field_map(cls) -> Dict[str, FieldWrapper]:
        """Get alias to field mapping."""
        return OscalBaseModel.alias_to_field_map.__func__(cls)

    def stripped_instance(
        self, stripped_fields: Optional[List[str]] = None, stripped_fields_aliases: Optional[List[str]] = None
    ) -> 'OscalBaseModel':
        """Return a new model instance with the specified fields being stripped."""
        return OscalBaseModel.stripped_instance(cast(Any, self), stripped_fields, stripped_fields_aliases)

    @classmethod
    def create_stripped_model_type(
        cls, stripped_fields: Optional[List[str]] = None, stripped_fields_aliases: Optional[List[str]] = None
    ) -> Type['OscalBaseModel']:
        """Create a stripped model type."""
        # Use the helper methods from OscalBaseModel to reduce complexity
        OscalBaseModel._validate_stripped_fields_params(stripped_fields, stripped_fields_aliases)
        excluded_fields = OscalBaseModel._resolve_excluded_fields.__func__(
            cls, stripped_fields, stripped_fields_aliases
        )
        new_fields_for_model = OscalBaseModel._build_fields_dict.__func__(cls, excluded_fields)

        new_model = create_model(cls.__name__, __base__=OscalBaseModel, **new_fields_for_model)
        return cast(Type[OscalBaseModel], new_model)
