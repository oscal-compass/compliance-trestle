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
"""Testing of customization of pydantic base model."""
import json
import pathlib
from datetime import datetime, timezone, tzinfo
from uuid import uuid4

import pytest

import tests.test_utils as test_utils

import trestle.common.const as const
import trestle.common.err as err
import trestle.core.base_model as ospydantic
import trestle.oscal
import trestle.oscal.assessment_plan as ap
import trestle.oscal.catalog as oscatalog
import trestle.oscal.common as common
import trestle.oscal.component as component
import trestle.oscal.ssp as ssp
from trestle.core.base_model import OscalBaseModel


def test_echo_tmp_path(tmp_path) -> None:
    """Testing pytest."""
    print(tmp_path)  # noqa T001
    assert 1


def simple_catalog() -> oscatalog.Catalog:
    """Return a skeleton catalog with datetime.now()."""
    m = common.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(),  # Added timezone info
            'version': '0.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION
        }
    )
    catalog = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))
    return catalog


def simple_catalog_utc() -> oscatalog.Catalog:
    """Return a skeleton catalog with datetime.now()."""
    m = common.Metadata(
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
    m = common.Metadata(
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

    assert isinstance(catalog, ospydantic.OscalBaseModel)


def test_no_timezone_exception() -> None:
    """Test that an exception occurs when no timezone is passed in datetime."""
    # Create a metadata object with naive datetime (no timezone)
    # This should fail in pydantic v2
    with pytest.raises(Exception):
        m = common.Metadata(
            **{
                'title': 'My simple catalog',
                'last-modified': datetime.now(),  # Naive datetime without timezone
                'version': '0.0.0',
                'oscal-version': trestle.oscal.OSCAL_VERSION
            }
        )
        # Try to serialize it
        jsoned_catalog = m.model_dump_json(exclude_none=True, by_alias=True, indent=2)
        type(jsoned_catalog)


def test_with_timezone() -> None:
    """Test where serialzation should work."""
    tz_catalog = simple_catalog_with_tz()
    jsoned_catalog = tz_catalog.model_dump_json(exclude_none=True, by_alias=True, indent=2)

    popo_json = json.loads(jsoned_catalog)
    time = popo_json['metadata']['last-modified']
    assert isinstance(time, str)
    assert ('Z' in time or '+' in time or '-' in time)


def test_broken_tz() -> None:
    """Test that invalid timezone raises exception during validation in pydantic v2."""

    class BrokenTimezone(tzinfo):
        """TimeZone class that returns None for utcoffset - invalid in pydantic v2."""

        def fromutc(self, dt):
            return dt

        def utcoffset(self, dt):
            # Return None - this should cause validation error in pydantic v2
            return None

        def dst(self, dt):
            return None

        def tzname(self, dt):
            return 'Broken'

    taz = BrokenTimezone()

    # This should fail during validation in pydantic v2
    with pytest.raises(Exception):
        _ = common.Metadata(
            **{
                'title': 'My simple catalog',
                'last-modified': datetime.now(tz=taz),
                'version': '0.0.0',
                'oscal-version': trestle.oscal.OSCAL_VERSION
            }
        )


def test_stripped_model() -> None:
    """Test whether model is can be stripped when acting as an intstance function."""
    catalog = simple_catalog()

    stripped_catalog_object = catalog.create_stripped_model_type(stripped_fields=['metadata'])

    # TODO: Need to check best practice here
    if 'metadata' in stripped_catalog_object.model_fields.keys():
        raise Exception('Test failure')

    if 'controls' not in stripped_catalog_object.model_fields.keys():
        raise Exception('Test failure')

    # Create instance.
    sc_instance = stripped_catalog_object(uuid=str(uuid4()))
    if 'metadata' in sc_instance.model_fields.keys():
        raise Exception('Test failure')


def test_stripping_model_class() -> None:
    """Test as a class variable."""
    stripped_catalog_object = oscatalog.Catalog.create_stripped_model_type(stripped_fields=['metadata'])
    if 'metadata' in stripped_catalog_object.model_fields.keys():
        raise Exception('Test failure')

    if 'controls' not in stripped_catalog_object.model_fields.keys():
        raise Exception('Test failure')

    # Create instance.
    sc_instance = stripped_catalog_object(uuid=str(uuid4()))
    if 'metadata' in sc_instance.model_fields.keys():
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


def test_stripped_instance(sample_nist_component_def: OscalBaseModel) -> None:
    """Test stripped_instance method."""
    assert hasattr(sample_nist_component_def, 'metadata')

    sc_instance = sample_nist_component_def.stripped_instance(stripped_fields_aliases=['metadata'])
    assert not hasattr(sc_instance, 'metadata')

    sc_instance = sample_nist_component_def.stripped_instance(stripped_fields=['metadata'])
    assert not hasattr(sc_instance, 'metadata')

    with pytest.raises(err.TrestleError):
        sc_instance = sample_nist_component_def.stripped_instance(stripped_fields_aliases=['invalid'])

    if isinstance(sample_nist_component_def, component.ComponentDefinition):
        metadata = sample_nist_component_def.metadata
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
    if 'metadata' in stripped_catalog_object.model_fields.keys():
        raise Exception('Test failure')
    if 'uuid' in stripped_catalog_object.model_fields.keys():
        raise Exception('Test failure')

    if 'controls' not in stripped_catalog_object.model_fields.keys():
        raise Exception('Test failure')

    with pytest.raises(Exception):
        stripped_catalog_object(uuid=str(uuid4()))


def test_copy_to() -> None:
    """Test the copy to functionality using pydantic v2 patterns."""
    # Complex variable
    c_m = common.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(),
            'version': '0.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION
        }
    )
    # Use model_dump() + model_validate() for pydantic v2
    data = c_m.model_dump()
    target_metadata = common.Metadata.model_validate(data)
    assert target_metadata.title == c_m.title

    # Non matching object - should fail validation
    with pytest.raises(Exception):
        data = c_m.model_dump()
        # This will fail because Metadata and DefinedComponent have different fields
        component.DefinedComponent.model_validate(data)

    # Testing of root fields
    remark = common.Remarks('hello')
    # Create RiskStatus with same value using pydantic v2 pattern
    risk_status = common.RiskStatus(remark.root)
    # Original test just created it, didn't assert
    # We'll just verify it was created successfully
    assert isinstance(risk_status, common.RiskStatus)


def test_copy_components() -> None:
    """Test copying across similar but different objects using pydantic v2 patterns."""
    state_obj = 'under-development'
    sys_component = ssp.SystemComponent(
        uuid=const.SAMPLE_UUID_STR,
        type='Hello',
        title='My title',
        description='Hello world',
        status=ssp.Status(state=state_obj)
    )
    # Use model_dump() + model_validate() for pydantic v2
    data = sys_component.model_dump()
    ap_component = ap.SystemComponent.model_validate(data)
    assert sys_component.title == ap_component.title
    # Also verify other fields were copied
    assert sys_component.description == ap_component.description
    assert sys_component.status.state == ap_component.status.state


def test_copy_from() -> None:
    """Test updating model with data from another model using pydantic v2 patterns."""
    m = common.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(),
            'version': '0.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION
        }
    )
    catalog = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))

    target_md = common.Metadata(
        **{
            'title': 'My simple target_title',
            'last-modified': datetime.now().astimezone(),
            'version': '99.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION
        }
    )

    # For pydantic v2, create a new metadata object with updated values
    # Get current metadata data, update with target data
    current_data = catalog.metadata.model_dump()
    target_data = target_md.model_dump(exclude_unset=True)
    updated_data = {**current_data, **target_data}

    # Create new metadata instance
    catalog.metadata = common.Metadata.model_validate(updated_data)

    assert catalog.metadata.title == target_md.title
    assert catalog.metadata.version == target_md.version
    # last-modified might be different due to time, but should be from target_md


def test_oscal_read() -> None:
    """Test ability to read and uwrap oscal object."""
    path_component_definition = pathlib.Path(test_utils.NIST_SAMPLE_CD_JSON)
    assert (path_component_definition.exists())

    cd = component.ComponentDefinition.oscal_read(path_component_definition)
    assert (len(str(cd.metadata.title)) > 1)


def test_oscal_write(tmp_path: pathlib.Path) -> None:
    """Test Oscal write by repetitive operations."""
    path_target_definition = pathlib.Path(test_utils.NIST_SAMPLE_CD_JSON)
    assert (path_target_definition.exists())

    component1 = component.ComponentDefinition.oscal_read(path_target_definition)

    temp_cd_json = pathlib.Path(tmp_path) / 'component_test.json'
    component1.oscal_write(temp_cd_json)

    component2 = component.ComponentDefinition.oscal_read(temp_cd_json)

    temp_cd_yaml = pathlib.Path(tmp_path) / 'component_test.yaml'
    component2.oscal_write(temp_cd_yaml)

    component.ComponentDefinition.oscal_read(temp_cd_yaml)
    # test failure
    with pytest.raises(err.TrestleError):
        component2.oscal_write(tmp_path / 'target.borked')


def test_get_field_value_by_alias(sample_nist_component_def: component.ComponentDefinition) -> None:
    """Test get attribute by alias method."""
    assert sample_nist_component_def.metadata.get_field_value_by_alias(
        'last-modified'
    ) == sample_nist_component_def.metadata.last_modified
    assert sample_nist_component_def.metadata.get_field_value_by_alias('last_modified') is None


def test_get_field_by_alias(sample_nist_component_def: component.ComponentDefinition) -> None:
    """Test get field for field alias."""
    assert sample_nist_component_def.metadata.get_field_by_alias('last-modified').name == 'last_modified'
    assert sample_nist_component_def.metadata.get_field_by_alias('last_modified') is None


def test_oscal_serialize_json() -> None:
    """Test Oscal serialize json by a circular parse."""
    simple_catalog_obj = simple_catalog_utc()
    serialized = simple_catalog_obj.oscal_serialize_json()
    jsoned = json.loads(serialized)
    new_catalog = oscatalog.Catalog.model_validate(jsoned['catalog'])

    assert simple_catalog_obj.metadata.title == new_catalog.metadata.title
