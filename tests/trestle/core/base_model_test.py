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

from pydantic import ValidationError

import tests.test_utils as test_utils

import trestle.common.const as const
import trestle.common.err as err
import trestle.core.base_model as ospydantic
import trestle.oscal
import trestle.oscal.assessment_plan as ap
import trestle.oscal.catalog as oscatalog
import trestle.oscal.common as common
import trestle.oscal.component as component
import trestle.oscal.profile as profile
import trestle.oscal.ssp as ssp
from trestle.core.base_model import OscalBaseModel, _format_validation_error


def test_echo_tmp_path(tmp_path) -> None:
    """Testing pytest."""
    print(tmp_path)  # noqa T001
    assert 1


def simple_catalog() -> oscatalog.Catalog:
    """Return a skeleton catalog with datetime.now()."""
    m = common.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(),
            'version': '0.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION,
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
            'oscal-version': trestle.oscal.OSCAL_VERSION,
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
            'oscal-version': trestle.oscal.OSCAL_VERSION,
        }
    )
    catalog = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))
    return catalog


def test_is_oscal_base() -> None:
    """Test that the typing information is as expected."""
    catalog = simple_catalog()

    assert isinstance(catalog, ospydantic.OscalBaseModel)


def test_optional_parameter_label_allows_empty_string() -> None:
    """Optional parameter labels should preserve blank values."""
    param = common.Parameter1(id='param1', label='', values=['one'])

    assert param.label == ''


def test_parameter_selection_label_allows_empty_string() -> None:
    """Selection-based parameters should also preserve blank labels."""
    param = common.Parameter2(id='param1', label='', select=common.ParameterSelection(choice=['one']))

    assert param.label == ''


def test_required_single_line_title_still_rejects_empty_string() -> None:
    """Required constrained strings should remain strict."""
    with pytest.raises(ValidationError):
        common.Role(id='role1', title='')


def test_parameter_label_assignment_allows_empty_string() -> None:
    """Assignment should behave the same as initialization for parameter labels."""
    param = common.Parameter1(id='param1', label='label1', values=['one'])
    param.label = ''

    assert param.label == ''


def test_profile_parameter_label_allows_empty_string() -> None:
    """Profile parameter settings should allow blank labels consistently."""
    param = profile.SetParameters(param_id='param1', label='', values=['one'])

    assert param.label == ''


def test_profile_selection_parameter_label_allows_empty_string() -> None:
    """Selection-based profile parameter settings should preserve blank labels."""
    param = profile.SetParameters1(param_id='param1', label='', select=common.ParameterSelection(choice=['one']))

    assert param.label == ''


def test_parameter_label_still_rejects_newlines() -> None:
    """Blank labels are allowed, but newline-containing values remain invalid."""
    with pytest.raises(ValidationError):
        common.Parameter1(id='param1', label='\n', values=['one'])

    with pytest.raises(ValidationError):
        common.Parameter1(id='param1', label='hello\n', values=['one'])

    with pytest.raises(ValidationError):
        common.Parameter2(id='param1', label='hello\n', select=common.ParameterSelection(choice=['one']))

    with pytest.raises(ValidationError):
        profile.SetParameters(param_id='param1', label='hello\n', values=['one'])

    with pytest.raises(ValidationError):
        profile.SetParameters1(param_id='param1', label='hello\n', select=common.ParameterSelection(choice=['one']))


def test_no_timezone_exception() -> None:
    """Test that an exception occurs when no timezone is passed in datetime."""
    # In Pydantic v2 with AwareDatetime, naive datetimes are rejected at validation time
    with pytest.raises(ValidationError):
        m = common.Metadata(
            **{
                'title': 'My simple catalog',
                'last-modified': datetime.now(),  # No timezone - should fail validation
                'version': '0.0.0',
                'oscal-version': trestle.oscal.OSCAL_VERSION,
            }
        )
        _ = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))


def test_with_timezone() -> None:
    """Test where serialzation should work."""
    tz_catalog = simple_catalog_with_tz()
    jsoned_catalog = tz_catalog.model_dump_json(exclude_none=True, by_alias=True, indent=2)

    popo_json = json.loads(jsoned_catalog)
    time = popo_json['metadata']['last-modified']
    assert isinstance(time, str)
    assert 'Z' in time or '+' in time or '-' in time


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

    # In Pydantic v2, timezone-aware validation happens at model creation
    # A datetime with a timezone that returns None for utcoffset is considered timezone-naive
    with pytest.raises(Exception):
        common.Metadata(
            **{
                'title': 'My simple catalog',
                'last-modified': datetime.now(tz=taz),
                'version': '0.0.0',
                'oscal-version': trestle.oscal.OSCAL_VERSION,
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
    if 'metadata' in sc_instance.__class__.model_fields.keys():
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
    if 'metadata' in sc_instance.__class__.model_fields.keys():
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
    """Test the copy to functionality."""
    # Complex variable
    c_m = common.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(),
            'version': '0.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION,
        }
    )

    target_metadata = c_m.copy_to(common.Metadata)
    assert target_metadata.title == c_m.title
    # Non matching object
    with pytest.raises(err.TrestleError):
        c_m.copy_to(component.DefinedComponent)

    # Testing of root fields. This is subject to change.
    # component.Remarks (type str)
    # poam.RiskStatus (type str)
    # note the testing conduction
    # Pydantic v2: RootModel uses 'root' instead of '__root__'
    # In Pydantic v2, RootModel doesn't inherit from OscalBaseModel, so copy_to is not available
    # Instead, we can convert between RootModels using model_validate on the root value
    # Remarks wraps MarkupMultilineDatatype which itself wraps str
    markup = common.MarkupMultilineDatatype(root='hello')
    remark = common.Remarks(root=markup)
    # RiskStatus wraps TokenDatatype | RiskStatusValidValues
    # We can create a RiskStatus from the enum value
    risk_status = common.RiskStatus(root=common.RiskStatusValidValues.open)
    assert isinstance(remark.root, common.MarkupMultilineDatatype)
    assert risk_status.root == common.RiskStatusValidValues.open


def test_copy_components() -> None:
    """Test copying across similar but different objects."""
    state_obj = 'under-development'
    sys_component = ssp.SystemComponent(
        uuid=const.SAMPLE_UUID_STR,
        type='Hello',
        title='My title',
        description='Hello world',
        status=ssp.Status(state=state_obj),
    )
    ap_component = sys_component.copy_to(ap.SystemComponent)
    assert sys_component.title == ap_component.title
    pass


def test_copy_from() -> None:
    """Test copy from function."""
    m = common.Metadata(
        **{
            'title': 'My simple catalog',
            'last-modified': datetime.now().astimezone(),
            'version': '0.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION,
        }
    )
    catalog = oscatalog.Catalog(metadata=m, uuid=str(uuid4()))

    target_md = common.Metadata(
        **{
            'title': 'My simple target_title',
            'last-modified': datetime.now().astimezone(),
            'version': '99.0.0',
            'oscal-version': trestle.oscal.OSCAL_VERSION,
        }
    )
    catalog.metadata.copy_from(target_md)

    assert catalog.metadata.title == target_md.title


def test_oscal_read() -> None:
    """Test ability to read and uwrap oscal object."""
    path_component_definition = pathlib.Path(test_utils.NIST_SAMPLE_CD_JSON)
    assert path_component_definition.exists()

    cd = component.ComponentDefinition.oscal_read(path_component_definition)
    assert len(str(cd.metadata.title)) > 1


def test_oscal_write(tmp_path: pathlib.Path) -> None:
    """Test Oscal write by repetitive operations."""
    path_target_definition = pathlib.Path(test_utils.NIST_SAMPLE_CD_JSON)
    assert path_target_definition.exists()

    component1 = component.ComponentDefinition.oscal_read(path_target_definition)

    temp_cd_json = pathlib.Path(tmp_path) / 'component_test.json'
    component1.oscal_write(temp_cd_json)

    component2 = component.ComponentDefinition.oscal_read(temp_cd_json)

    temp_cd_yaml = pathlib.Path(tmp_path) / 'component_test.yaml'
    component2.oscal_write(temp_cd_yaml)

    component.ComponentDefinition.oscal_read(temp_cd_yaml)

    temp_cd_canonical_json = pathlib.Path(tmp_path) / 'component_test.canonical.json'
    component2.oscal_write(temp_cd_canonical_json)
    canonical_json = temp_cd_canonical_json.read_text(encoding=const.FILE_ENCODING)
    assert canonical_json == component2.oscal_serialize_json(canonical=True)
    assert '\n' not in canonical_json
    component.ComponentDefinition.oscal_read(temp_cd_canonical_json)

    # test failure
    with pytest.raises(err.TrestleError):
        component2.oscal_write(tmp_path / 'target.borked')


def test_get_field_value_by_alias(sample_nist_component_def: component.ComponentDefinition) -> None:
    """Test get attribute by alias method."""
    assert (
        sample_nist_component_def.metadata.get_field_value_by_alias('last-modified')
        == sample_nist_component_def.metadata.last_modified
    )
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
    new_catalog = oscatalog.Catalog.parse_obj(jsoned['catalog'])

    assert simple_catalog_obj.metadata.title == new_catalog.metadata.title


def test_oscal_serialize_canonical_json() -> None:
    """Test Oscal canonical json serialization."""
    simple_catalog_obj = simple_catalog_utc()

    serialized = simple_catalog_obj.oscal_serialize_json(canonical=True)
    jsoned = json.loads(serialized)
    new_catalog = oscatalog.Catalog.parse_obj(jsoned['catalog'])

    assert serialized == simple_catalog_obj.oscal_serialize_json_bytes(canonical=True).decode(const.FILE_ENCODING)
    assert '\n' not in serialized
    assert simple_catalog_obj.metadata.title == new_catalog.metadata.title


def test_robust_datetime_serialization_error_paths() -> None:
    """Test error handling in robust_datetime_serialization."""
    from trestle.core.base_model import robust_datetime_serialization

    # Test with naive datetime (no timezone)
    naive_dt = datetime.now()
    with pytest.raises(err.TrestleError, match='Missing timezone in datetime'):
        robust_datetime_serialization(naive_dt)

    # Test with datetime with microseconds = 0 (seconds format)
    dt_no_micro = datetime(2024, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
    result = robust_datetime_serialization(dt_no_micro)
    assert '+00:00' in result
    assert '.' not in result  # No milliseconds

    # Test with datetime with microseconds != 0 (milliseconds format)
    dt_with_micro = datetime(2024, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc)
    result = robust_datetime_serialization(dt_with_micro)
    assert '+00:00' in result
    assert '.' in result  # Has milliseconds


def test_eq_non_trestle_base_model() -> None:
    """Test __eq__ with non-TrestleBaseModel objects."""
    catalog = simple_catalog()

    # Compare with non-TrestleBaseModel object
    assert catalog != 'not a model'
    assert catalog != 123
    assert catalog is not None
    assert catalog != {'uuid': catalog.uuid}


def test_resolve_excluded_fields_empty() -> None:
    """Test _resolve_excluded_fields with None stripped_fields_aliases."""
    from trestle.oscal.catalog import Catalog

    # Test with stripped_fields provided (normal path)
    result = Catalog._resolve_excluded_fields(['metadata'], None)
    assert result == ['metadata']

    # Test with stripped_fields_aliases provided
    result = Catalog._resolve_excluded_fields(None, ['metadata'])
    assert result == ['metadata']


def test_oscal_read_key_error() -> None:
    """Test oscal_read with missing top-level key."""
    import tempfile
    import json

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        # Write JSON without the expected top-level key
        json.dump({'wrong_key': {'uuid': 'test', 'metadata': {}}}, f)
        temp_path = pathlib.Path(f.name)

    try:
        with pytest.raises(err.TrestleError, match='does not have top level key'):
            oscatalog.Catalog.oscal_read(temp_path)
    finally:
        temp_path.unlink()


def test_is_collection_container() -> None:
    """Test is_collection_container method."""
    # Test with a regular model (not a collection container)
    assert not oscatalog.Catalog.is_collection_container()
    assert not common.Metadata.is_collection_container()

    # Create a dynamic model that wraps a list
    from pydantic import create_model, Field
    from typing import List

    # This simulates what happens in trestle when decomposing models
    list_model = create_model('TestListModel', __base__=OscalBaseModel, root=(List[str], Field(...)))

    # This should be detected as a collection container
    assert list_model.is_collection_container()

    # Test get_collection_type
    assert list_model.get_collection_type() == list

    # Test error when calling get_collection_type on non-collection
    with pytest.raises(err.TrestleError, match='not wrapping a collection type'):
        oscatalog.Catalog.get_collection_type()


def test_eq_same_name_same_content() -> None:
    """Test __eq__ for dynamically created models with same class name and identical content."""
    from pydantic import Field, create_model
    from typing import Optional
    from trestle.core.base_model import OscalBaseModel

    # Two separate create_model() calls with the same name — the scenario that
    # arises with create_stripped_model_type().
    model_a = create_model('MyModel', __base__=OscalBaseModel, x=(Optional[str], Field(None)))
    model_b = create_model('MyModel', __base__=OscalBaseModel, x=(Optional[str], Field(None)))

    assert model_a is not model_b, 'sanity: they are different class objects'
    assert model_a(x='hello') == model_b(x='hello')
    assert model_a(x=None) == model_b(x=None)


def test_eq_same_name_different_content() -> None:
    """Test __eq__ for dynamically created models with same class name but different field values."""
    from pydantic import Field, create_model
    from typing import Optional
    from trestle.core.base_model import OscalBaseModel

    model_a = create_model('MyModel', __base__=OscalBaseModel, x=(Optional[str], Field(None)))

    assert model_a(x='hello') != model_a(x='world')
    assert model_a(x='hello') != model_a(x=None)


def test_eq_different_class_names() -> None:
    """Test __eq__ returns False when class names differ, even if content is identical."""
    from pydantic import Field, create_model
    from typing import Optional
    from trestle.core.base_model import OscalBaseModel

    model_foo = create_model('Foo', __base__=OscalBaseModel, x=(Optional[str], Field(None)))
    model_bar = create_model('Bar', __base__=OscalBaseModel, x=(Optional[str], Field(None)))

    assert model_foo(x='hello') != model_bar(x='hello')


def test_eq_stripped_model() -> None:
    """Test __eq__ works correctly for stripped model instances (the primary use-case)."""
    import trestle.oscal.catalog as oscatalog

    catalog = simple_catalog()

    # Create two independently stripped instances — different class objects, same name & content
    stripped_a = catalog.stripped_instance(stripped_fields_aliases=['metadata'])
    stripped_b = catalog.stripped_instance(stripped_fields_aliases=['metadata'])

    assert stripped_a == stripped_b
    assert type(stripped_a) is not type(stripped_b), 'sanity: different class objects from separate calls'


def test_serialize_oscal_fields_datetime() -> None:
    """Test that serialize_oscal_fields emits +00:00 timezone offset (not Z) for datetime fields."""
    import trestle.oscal.common as common
    import json
    from datetime import datetime, timezone

    dt = datetime(2024, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
    # Use a model that has a datetime field (Remarks wraps markup, use OnDate which has AwareDatetime)
    on_date = common.OnDate(date=dt)
    serialized = json.loads(on_date.model_dump_json(by_alias=True))

    date_str = serialized['date']
    assert '+00:00' in date_str, f'Expected +00:00 in datetime output, got: {date_str}'
    assert not date_str.endswith('Z'), f'datetime should not end with Z, got: {date_str}'


def test_serialize_oscal_fields_anyurl() -> None:
    """Test that serialize_oscal_fields converts AnyUrl fields to plain strings."""
    import trestle.oscal.common as common
    import json

    # Property has an optional AnyUrl 'ns' field
    prop = common.Property(name='test', value='val', ns='https://example.com/ns')  # type: ignore[arg-type]
    serialized = json.loads(prop.model_dump_json(by_alias=True, exclude_none=True))

    ns_val = serialized.get('ns')
    assert isinstance(ns_val, str), f'AnyUrl should serialize to str, got {type(ns_val)}'
    assert ns_val == 'https://example.com/ns', f'Unexpected ns value: {ns_val}'


class TestFormatValidationError:
    """Unit tests for _format_validation_error()."""

    def test_pattern_message_is_humanized(self) -> None:
        """Pattern validation errors should use the friendly message path."""
        with pytest.raises(ValidationError) as exc_info:
            common.Parameter1(id='param1', label='ok', values=['bad\nvalue'])

        message = _format_validation_error(pathlib.Path('sample.json'), exc_info.value)
        assert 'value does not match required pattern:' in message

    def test_datetime_parse_error_is_humanized(self) -> None:
        """Datetime parsing errors should use the invalid date/time wording."""
        with pytest.raises(ValidationError) as exc_info:
            common.OnDate(date='not-a-date')

        message = _format_validation_error(pathlib.Path('sample.json'), exc_info.value)
        assert 'invalid date/time' in message

    def test_enum_error_is_humanized(self) -> None:
        """Enum validation errors should report allowed values."""
        with pytest.raises(ValidationError) as exc_info:
            common.ParameterSelection(how_many='bogus', choice=['one'])

        message = _format_validation_error(pathlib.Path('sample.json'), exc_info.value)
        assert 'invalid value; allowed:' in message
