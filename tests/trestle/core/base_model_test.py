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
import pathlib
from datetime import datetime, timezone, tzinfo
from uuid import uuid4

import pytest

import trestle.core.base_model as ospydantic
import trestle.core.err as err
import trestle.oscal
import trestle.oscal.catalog as oscatalog
import trestle.oscal.component as component
import trestle.oscal.poam as poam
import trestle.oscal.target as ostarget
from trestle.core.base_model import OscalBaseModel


def test_echo_tmp_path(tmp_path) -> None:
    """Testing pytest."""
    print(tmp_path)  # noqa T001
    assert 1


def simple_catalog() -> oscatalog.Catalog:
    """Return a skeleton catalog with datetime.now()."""
    m = oscatalog.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now(),
            'version': '0.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION
        }
    )
    catalog = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))
    return catalog


def simple_catalog_utc() -> oscatalog.Catalog:
    """Return a skeleton catalog with datetime.now()."""
    m = oscatalog.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(timezone.utc),
            'version': '0.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION
        }
    )
    catalog = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))
    return catalog


def simple_catalog_with_tz() -> oscatalog.Catalog:
    """Return a skeleton catalog with datetime.now()."""
    m = oscatalog.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(),
            'version': '0.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION
        }
    )
    catalog = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))
    return catalog


def test_is_oscal_base() -> None:
    """Test that the typing information is as expected."""
    catalog = simple_catalog()

    assert (isinstance(catalog, ospydantic.OscalBaseModel))


def test_no_timezone_exception() -> None:
    """Test that an exception occurs when no timezone is passed in datetime."""
    no_tz_catalog = simple_catalog()
    with pytest.raises(Exception):
        jsoned_catalog = no_tz_catalog.json(exclude_none=True, by_alias=True, indent=2)
        type(jsoned_catalog)


def test_with_timezone() -> None:
    """Test where serialzation should work."""
    tz_catalog = simple_catalog_with_tz()
    jsoned_catalog = tz_catalog.json(exclude_none=True, by_alias=True, indent=2)

    popo_json = json.loads(jsoned_catalog)
    time = popo_json['metadata']['last-modified']
    assert (type(time) == str)
    assert ('Z' in time or '+' in time or '-' in time)


def test_broken_tz() -> None:
    """Deliberately break tz to trigger exception."""

    class BrokenTimezone(tzinfo):
        # TODO: Type annotations here.
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
            'oscal-version': trestle.oscal.OSCAL_VERSION
        }
    )
    catalog = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))
    with pytest.raises(Exception):
        jsoned_catalog = catalog.json(exclude_none=True, by_alias=True, indent=2)
        type(jsoned_catalog)


def test_stripped_model() -> None:
    """Test whether model is can be stripped when acting as an intstance function."""
    catalog = simple_catalog()

    stripped_catalog_object = catalog.create_stripped_model_type(stripped_fields=['metadata'])

    # TODO: Need to check best practice here
    if 'metadata' in stripped_catalog_object.__fields__.keys():
        raise Exception('Test failure')

    if 'controls' not in stripped_catalog_object.__fields__.keys():
        raise Exception('Test failure')

    # Create instance.
    sc_instance = stripped_catalog_object(uuid=str(uuid4()))
    if 'metadata' in sc_instance.__fields__.keys():
        raise Exception('Test failure')


def test_stripping_model_class() -> None:
    """Test as a class variable."""
    stripped_catalog_object = oscatalog.Catalog.create_stripped_model_type(stripped_fields=['metadata'])
    if 'metadata' in stripped_catalog_object.__fields__.keys():
        raise Exception('Test failure')

    if 'controls' not in stripped_catalog_object.__fields__.keys():
        raise Exception('Test failure')

    # Create instance.
    sc_instance = stripped_catalog_object(uuid=str(uuid4()))
    if 'metadata' in sc_instance.__fields__.keys():
        raise Exception('Test failure')


def test_stripped_model_type_failure() -> None:
    """Test for user failure conditions."""
    with pytest.raises(err.TrestleError):
        a = oscatalog.Catalog.create_stripped_model_type(
            stripped_fields=['metadata'], stripped_fields_aliases=['groups']
        )
        assert a is not None
    with pytest.raises(err.TrestleError):
        a = oscatalog.Catalog.create_stripped_model_type(stripped_fields=None)
        assert a is not None


def test_stripped_instance(sample_target_def: OscalBaseModel) -> None:
    """Test stripped_instance method."""
    assert hasattr(sample_target_def, 'metadata')

    sc_instance = sample_target_def.stripped_instance(stripped_fields_aliases=['metadata'])
    assert not hasattr(sc_instance, 'metadata')

    sc_instance = sample_target_def.stripped_instance(stripped_fields=['metadata'])
    assert not hasattr(sc_instance, 'metadata')

    with pytest.raises(err.TrestleError):
        sc_instance = sample_target_def.stripped_instance(stripped_fields_aliases=['invalid'])

    if isinstance(sample_target_def, ostarget.TargetDefinition):
        metadata = sample_target_def.metadata
        assert hasattr(metadata, 'last_modified')

        instance = metadata.stripped_instance(stripped_fields_aliases=['last-modified'])
        assert not hasattr(instance, 'last_modified')

        instance = metadata.stripped_instance(stripped_fields=['last_modified'])
        assert not hasattr(sc_instance, 'last_modified')
    else:
        raise Exception('Test failure')


def test_multiple_variable_strip() -> None:
    """Test mutliple fields can be stripped and checking strict schema enforcement."""
    stripped_catalog_object = oscatalog.Catalog.create_stripped_model_type(['metadata', 'uuid'])
    if 'metadata' in stripped_catalog_object.__fields__.keys():
        raise Exception('Test failure')
    if 'uuid' in stripped_catalog_object.__fields__.keys():
        raise Exception('Test failure')

    if 'controls' not in stripped_catalog_object.__fields__.keys():
        raise Exception('Test failure')

    with pytest.raises(Exception):
        stripped_catalog_object(uuid=str(uuid4()))


def test_copy_to() -> None:
    """Test the copy to functionality."""
    # Complex variable
    c_m = oscatalog.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now(),
            'version': '0.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION
        }
    )

    target_metadata = c_m.copy_to(ostarget.Metadata)
    assert (target_metadata.title == c_m.title)
    # Non matching object
    with pytest.raises(err.TrestleError):
        c_m.copy_to(ostarget.DefinedTarget)

    # Testing of root fields. This is is subject to change.
    # component.Remarks (type str)
    # poam.RiskStatus (type str)
    # note the testing conduction
    remark = component.Remarks(__root__='hello')
    _ = remark.copy_to(poam.RiskStatus)


def test_copy_from() -> None:
    """Test copy from function."""
    m = oscatalog.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(),
            'version': '0.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION
        }
    )
    catalog = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))

    target_md = ostarget.Metadata(
        **{
            'title': 'My simple target_title',
            'last-modified': datetime.now().astimezone(),
            'version': '99.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION
        }
    )
    catalog.metadata.copy_from(target_md)

    assert catalog.metadata.title == target_md.title


def test_oscal_read() -> None:
    """Test ability to read and uwrap oscal object."""
    path_target_definition = pathlib.Path('tests/data/json/sample-target-definition.json')
    assert (path_target_definition.exists())

    target = ostarget.TargetDefinition.oscal_read(path_target_definition)
    assert (len(str(target.metadata.title)) > 1)


def test_oscal_write(tmp_path: pathlib.Path) -> None:
    """Test Oscal write by repetitive operations."""
    path_target_definition = pathlib.Path('tests/data/json/sample-target-definition.json')
    assert (path_target_definition.exists())

    target = ostarget.TargetDefinition.oscal_read(path_target_definition)

    temp_td_json = pathlib.Path(tmp_path) / 'target_test.json'
    target.oscal_write(temp_td_json)

    target2 = ostarget.TargetDefinition.oscal_read(temp_td_json)

    temp_td_yaml = pathlib.Path(tmp_path) / 'target_test.yaml'
    target2.oscal_write(temp_td_yaml)

    ostarget.TargetDefinition.oscal_read(temp_td_yaml)
    # test failure
    with pytest.raises(err.TrestleError):
        target2.oscal_write(tmp_path / 'target.borked')


def test_get_field_value(sample_target_def: ostarget.TargetDefinition) -> None:
    """Test get field value method."""
    assert sample_target_def.metadata.get_field_value('last-modified') == sample_target_def.metadata.last_modified
    assert sample_target_def.metadata.get_field_value('last_modified') == sample_target_def.metadata.last_modified


def test_get_field_value_by_alias(sample_target_def: ostarget.TargetDefinition) -> None:
    """Test get attribute by alias method."""
    assert sample_target_def.metadata.get_field_value_by_alias(
        'last-modified'
    ) == sample_target_def.metadata.last_modified
    assert sample_target_def.metadata.get_field_value_by_alias('last_modified') is None


def test_get_field_by_alias(sample_target_def: ostarget.TargetDefinition) -> None:
    """Test get field for field alias."""
    assert sample_target_def.metadata.get_field_by_alias('last-modified').name == 'last_modified'
    assert sample_target_def.metadata.get_field_by_alias('last_modified') is None


def test_oscal_serialize_json() -> None:
    """Test Oscal serialize json by a circular parse."""
    simple_catalog_obj = simple_catalog_utc()
    serialized = simple_catalog_obj.oscal_serialize_json()
    jsoned = json.loads(serialized)
    new_catalog = oscatalog.Catalog.parse_obj(jsoned['catalog'])

    assert simple_catalog_obj.metadata.title == new_catalog.metadata.title
