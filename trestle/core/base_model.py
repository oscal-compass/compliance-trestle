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
from typing import List, Optional

from pydantic import BaseModel, Extra, Field, create_model


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
        # allow_population_by_field_name = True  noqa: E800

        # Enforce strict schema
        extra = Extra.forbid

        # Validate on assignment of variables to ensure no escapes
        validate_assignment = True

    @classmethod
    def create_stripped_model_type(cls, fields: List[str]):
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

    @classmethod
    def clone_from(cls, oscal_object):
        """
        Clone from a semantically similar pydantic object in a different python module to this module.

        OSCAL has objects that are replicated across schemas. These objects need to be converted into a new type

        e.g.
        profile_metadata: profile.Metadata = profile.Metadata.clone_from(catalog_metadata)

        where
        type(catalog_metadata) == catalog.Metadata.

        Presumes 'exact' matching support throughout the tree.
        """
        pass
