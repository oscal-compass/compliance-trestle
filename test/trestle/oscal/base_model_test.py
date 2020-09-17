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
"""Testing of customization of pydantic base model."""
import json
from datetime import datetime, tzinfo
from uuid import uuid4

import pytest

import trestle.core.parser as p
import trestle.oscal.catalog as oscatalog
import trestle.oscal.base_model as ospydantic


def test_echo_tmppath(tmp_path):
    """Testing pytest."""
    print(tmp_path) # noqa T001
    assert 1


def simple_catalog() -> oscatalog.Catalog:
    """Return a skeleton catalog with datetime.now()."""
    m = oscatalog.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now(),
            'version': '0.0.0',
            'oscal-version': '1.0.0-Milestone3'
        })
    catalog = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))
    return catalog


def simple_catalog_with_tz() -> oscatalog.Catalog:
    """Return a skeleton catalog with datetime.now()."""
    m = oscatalog.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(),
            'version': '0.0.0',
            'oscal-version': '1.0.0-Milestone3'
        })
    catalog = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))
    return catalog


def test_is_oscal_base():
    """Test that the typing information is as expected."""
    catalog = simple_catalog()

    assert(isinstance(catalog, ospydantic.OscalBaseModel))


def test_wrapper_is_oscal_base():
    """Test a wrapped class is still a instance of OscalBaseModel."""
    catalog = simple_catalog()
    wrapped_catalog = p.wrap_for_output(catalog)
    assert(isinstance(wrapped_catalog, ospydantic.OscalBaseModel))


def test_no_timezone_exception():
    """Test that an exception occurs when no timezone is passed in datetime."""
    no_tz_catalog = simple_catalog()
    with pytest.raises(Exception):
        jsoned_catalog = no_tz_catalog.json(exclude_none=True, by_alias=True, indent=2)
        type(jsoned_catalog)


def test_with_timezone():
    """Test where serialzation should work."""
    tz_catalog = simple_catalog_with_tz()
    jsoned_catalog = tz_catalog.json(exclude_none=True, by_alias=True, indent=2)

    popo_json = json.loads(jsoned_catalog)
    time = popo_json['metadata']['last-modified']
    assert(type(time) == str)
    assert('Z' in time or '+' in time or '-' in time)


def test_broken_tz():
    """Deliberately break tz to trigger exception."""
    class BrokenTimezone(tzinfo):
        """Broken TZ class which returns null offset."""

        def fromutc(self, dt):
            return dt

        def utcoffset(self, dt):
            return None

        def dst(self, dt):
            return dt

        def tzname(self, dt):
            return 'Broken'

        def _isdst(self, dt):
            return True
    taz = BrokenTimezone()

    m = oscatalog.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now(tz=taz),
            'version': '0.0.0',
            'oscal-version': '1.0.0-Milestone3'
        })
    catalog = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))
    with pytest.raises(Exception):
        jsoned_catalog = catalog.json(exclude_none=True, by_alias=True, indent=2)
        type(jsoned_catalog)


def test_stripped_model():
    catalog = simple_catalog()

    stripped_catalog = catalog.create_stripped_model_type(['metadata'])
    
    # FIXME: Need to check best practice here
    if 'metadata' in stripped_catalog.__fields__.keys():
        raise Exception('Test failure')

    if 'controls' not in stripped_catalog.__fields__.keys():
        raise Exception('Test failure')