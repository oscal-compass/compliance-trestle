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
"""Define Results class returned by transformers."""

import datetime
import pathlib
from typing import List

import orjson
from pydantic import Field, RootModel
from ruamel.yaml import YAML

import trestle.common.err as err
import trestle.common.const as const
from trestle.common.str_utils import AliasMode, classname_to_alias
from trestle.core.base_model import robust_datetime_serialization
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.assessment_results import Result


class Results(RootModel[List[Result]]):
    """Transformer results as a list.

    The OSCAL schema requires at least one Result (minItems: 1), enforced here via
    ``min_length=1`` so that ``model_validate`` (used by ``oscal_read``) rejects an
    empty list loaded from a file.

    When building a Results incrementally (as all transformer implementations do),
    use ``Results.model_construct(root=[])`` followed by ``.root.append(...)``.
    ``model_construct`` intentionally bypasses Pydantic field validation, so an
    empty list is allowed during construction before items are appended.
    """

    root: List[Result] = Field(default=[], min_length=1)

    def oscal_dict(self):
        """Return an 'oscal wrapped' dictionary."""
        class_name = self.__class__.__name__
        result = {}
        # For RootModel, model_dump() returns the root value directly (a list in this case)
        raw_data = self.model_dump(by_alias=True, exclude_none=True, mode='json')
        result[classname_to_alias(class_name, AliasMode.JSON)] = raw_data
        return result

    def oscal_serialize_json_bytes(self, pretty: bool = False, wrapped: bool = True) -> bytes:
        """
        Return an 'oscal wrapped' json object serialized in a compressed form as bytes.

        Args:
            pretty: Whether or not to pretty-print json output or have in compressed form.
            wrapped: Whether to wrap in OSCAL format.
        Returns:
            Oscal model serialized to a json object including packaging inside of a single top level key.
        """
        if wrapped:
            odict = self.oscal_dict()
        else:
            odict = self.model_dump(by_alias=True, exclude_none=True, mode='json')

        def default_encoder(obj):
            if isinstance(obj, datetime.datetime):
                return robust_datetime_serialization(obj)
            raise TypeError(f'Type {type(obj)} not serializable')

        if pretty:
            return orjson.dumps(odict, default=default_encoder, option=orjson.OPT_INDENT_2)
        return orjson.dumps(odict, default=default_encoder)

    def oscal_serialize_json(self, pretty: bool = False, wrapped: bool = True) -> str:
        """
        Return an 'oscal wrapped' json object serialized in a compressed form as string.

        Args:
            pretty: Whether or not to pretty-print json output or have in compressed form.
            wrapped: Whether to wrap in OSCAL format.
        Returns:
            Oscal model serialized to a json object including packaging inside of a single top level key.
        """
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
            err.TrestleError: If Results contains no items (OSCAL minItems: 1 violation).
            err.TrestleError: If an unknown file extension is provided.
        """
        if not self.root:
            raise err.TrestleError('Results must contain at least one Result before writing (OSCAL minItems: 1)')
        content_type = FileContentType.to_content_type(path.suffix)

        if content_type == FileContentType.YAML:
            with pathlib.Path(path).open('w', encoding=const.FILE_ENCODING) as write_file:
                yaml = YAML(typ='safe')
                yaml.dump(yaml.load(self.oscal_serialize_json()), write_file)
        elif content_type == FileContentType.JSON:
            with pathlib.Path(path).open('wb') as write_file:
                write_file.write(self.oscal_serialize_json_bytes(pretty=True))
