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


from pydantic import BaseModel


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
        json_encoders = {
            datetime.datetime: lambda x: robust_datetime_serialization(x)
        }
        # this is not safe and caused class: nan in yaml output
        # TODO: Explore fix.
        # allow_population_by_field_name = True  noqa: E800
