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
"""Tests for models util module."""
import copy
import pathlib

from _pytest.monkeypatch import MonkeyPatch

from pydantic import ValidationError

import pytest

from tests import test_utils

import trestle.common.const as const
import trestle.common.err as err
import trestle.common.file_utils as futils
import trestle.common.type_utils as mutils
import trestle.oscal.assessment_plan as assessment_plan
import trestle.oscal.assessment_results as assessment_results
import trestle.oscal.catalog as catalog
import trestle.oscal.common as common
import trestle.oscal.component as component
import trestle.oscal.poam as poam
import trestle.oscal.profile as profile
import trestle.oscal.ssp as ssp
from trestle.common import str_utils
from trestle.common.err import TrestleError
from trestle.common.model_utils import ModelUtils
from trestle.common.str_utils import AliasMode


def load_good_catalog() -> catalog.Catalog:
    """Load nist 800-53 as a catalog example."""
    good_sample_path = pathlib.Path('nist-content/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json')

    assert (good_sample_path.exists())
    return catalog.Catalog.oscal_read(good_sample_path)


def test_is_collection_field_type() -> None:
    """Test for checking whether the type of a field in an OscalBaseModel object is a collection field."""
    # originally Dicts were possible, but with Trestle 1.0.0 the only collection type is List
    # Dicts only appear for include_all, which only needs to be handled specially in the sample generator
    good_catalog = load_good_catalog()

    assert mutils.is_collection_field_type(type('this is a string')) is False

    assert mutils.is_collection_field_type(type(good_catalog)) is False  # Catalog
    catalog_field = catalog.Model.alias_to_field_map()['catalog']
    assert mutils.is_collection_field_type(catalog_field.outer_type_) is False  # Catalog

    assert mutils.is_collection_field_type(type(good_catalog.metadata)) is False  # Metadata
    metadata_field = catalog.Catalog.alias_to_field_map()['metadata']
    assert mutils.is_collection_field_type(metadata_field.outer_type_) is False  # Metadata

    assert mutils.is_collection_field_type(type(good_catalog.metadata.roles)) is False  # list
    roles_field = common.Metadata.alias_to_field_map()['roles']
    assert mutils.is_collection_field_type(roles_field.outer_type_) is True  # List[Role]
    assert mutils.is_collection_field_type(roles_field.type_) is False  # Role

    assert mutils.is_collection_field_type(type(good_catalog.metadata.responsible_parties)) is False  # list
    responsible_parties_field = common.Metadata.alias_to_field_map()['responsible-parties']
    assert mutils.is_collection_field_type(responsible_parties_field.outer_type_) is True  # List[ResponsibleParty]
    assert mutils.is_collection_field_type(responsible_parties_field.type_) is False  # ResponsibleParty

    dct = {'foo': responsible_parties_field}
    assert mutils.is_collection_field_type(dct) is False  # hand-created dict is not collection field type

    assert mutils.is_collection_field_type(
        type(good_catalog.metadata.parties[0].addresses[0].addr_lines)
    ) is False  # list
    postal_address_field = common.Address.alias_to_field_map()['addr-lines']
    assert mutils.is_collection_field_type(postal_address_field.outer_type_) is True  # List[AddrLine]
    assert mutils.is_collection_field_type(postal_address_field.type_) is False  # AddrLine


def test_get_inner_type() -> None:
    """Test retrievel of inner type of a model field representing a collection."""
    good_catalog = load_good_catalog()

    with pytest.raises(err.TrestleError):
        # Type of catalog is not a collection field type
        mutils.get_inner_type(type(good_catalog))

    with pytest.raises(err.TrestleError):
        # Type of field catalog is not a collection field type
        catalog_field = catalog.Model.alias_to_field_map()['catalog']
        mutils.get_inner_type(catalog_field.outer_type_)

    with pytest.raises(err.TrestleError):
        # Type of roles object is not a collection field type
        mutils.get_inner_type(type(good_catalog.metadata.roles))

    # Type of field roles is a collection field type
    roles_field = common.Metadata.alias_to_field_map()['roles']
    role_type = mutils.get_inner_type(roles_field.outer_type_)
    assert role_type == common.Role

    with pytest.raises(err.TrestleError):
        # Type of responsible_parties object is not a collection field type
        mutils.get_inner_type(type(good_catalog.metadata.responsible_parties))

    # Type of field responsible-parties is a collection field type
    responsible_parties_field = common.Metadata.alias_to_field_map()['responsible-parties']
    responsible_party_type = mutils.get_inner_type(responsible_parties_field.outer_type_)
    assert responsible_party_type == common.ResponsibleParty


def test_get_root_model() -> None:
    """Test looking for the root model of a trestle oscal module."""
    with pytest.raises(err.TrestleError):
        ModelUtils.get_root_model('invalid')

    with pytest.raises(err.TrestleError):
        ModelUtils.get_root_model('pydantic')

    malias_to_mtype = {
        const.MODEL_TYPE_CATALOG: catalog.Catalog,
        const.MODEL_TYPE_PROFILE: profile.Profile,
        const.MODEL_TYPE_COMPDEF: component.ComponentDefinition,
        const.MODEL_TYPE_SSP: ssp.SystemSecurityPlan,
        const.MODEL_TYPE_A_PLAN: assessment_plan.AssessmentPlan,
        const.MODEL_TYPE_A_RESULT: assessment_results.AssessmentResults,
        const.MODEL_TYPE_POAM: poam.PlanOfActionAndMilestones
    }
    for key in malias_to_mtype:
        module_name = malias_to_mtype[key].__module__
        model_type, model_alias = ModelUtils.get_root_model(module_name)
        assert model_type == malias_to_mtype[key]
        assert model_alias == key


def test_classname_to_alias() -> None:
    """Test conversion of class name to alias."""
    module_name = catalog.Catalog.__module__

    short_classname = catalog.Catalog.__name__
    full_classname = f'{module_name}.{short_classname}'
    json_alias = str_utils.classname_to_alias(short_classname, AliasMode.JSON)
    assert json_alias == 'catalog'
    json_alias = str_utils.classname_to_alias(full_classname, AliasMode.FIELD)
    assert json_alias == 'catalog'

    short_classname = common.ResponsibleParty.__name__
    full_classname = f'{module_name}.{short_classname}'
    json_alias = str_utils.classname_to_alias(short_classname, AliasMode.JSON)
    assert json_alias == 'responsible-party'
    json_alias = str_utils.classname_to_alias(full_classname, AliasMode.FIELD)
    assert json_alias == 'responsible_party'

    short_classname = common.Property.__name__
    full_classname = f'{module_name}.{short_classname}'
    json_alias = str_utils.classname_to_alias(short_classname, AliasMode.JSON)
    assert json_alias == 'property'
    json_alias = str_utils.classname_to_alias(full_classname, AliasMode.FIELD)
    assert json_alias == 'property'


def test_snake_to_upper_camel() -> None:
    """Ensure Snake to upper camel behaves correctly."""
    cammeled = str_utils._snake_to_upper_camel('component_definition')
    assert cammeled == 'ComponentDefinition'
    cammeled = str_utils._snake_to_upper_camel('control')
    assert cammeled == 'Control'
    cammeled = str_utils._snake_to_upper_camel('')
    assert cammeled == ''


def test_camel_to_snake() -> None:
    """Ensure camel to snake behaves correctly."""
    snaked = str_utils._camel_to_snake('ComponentDefinition')
    assert snaked == 'component_definition'
    snaked = str_utils._camel_to_snake('Control')
    assert snaked == 'control'
    snaked = str_utils._camel_to_snake('')
    assert snaked == ''


def test_spaces_and_caps_to_snake() -> None:
    """Ensure spaces and caps to snake behaves correctly."""
    assert str_utils.spaces_and_caps_to_snake('  Foo  BAr  ') == 'foo_bar'


def test_spaces_and_caps_to_lower_single_spaces() -> None:
    """Ensure spaces and caps to lower single spaces behaves correctly."""
    assert str_utils.spaces_and_caps_to_lower_single_spaces('  Foo  BAr  ') == 'foo bar'


def test_alias_to_classname() -> None:
    """Test alias_to_classname function."""
    assert str_utils.alias_to_classname('component-definition', AliasMode.JSON) == 'ComponentDefinition'
    assert str_utils.alias_to_classname('component_definition', AliasMode.FIELD) == 'ComponentDefinition'


def test_parameter_to_dict() -> None:
    """Test parameter to dict conversion."""
    test1 = common.Test(expression='not too big', remarks='test for 1')
    test2 = common.Test(expression='keep it small', remarks='test for 2')
    constraints = [common.ParameterConstraint(description='my constraints', tests=[test1, test2])]
    sel = common.ParameterSelection(how_many=const.ONE_OR_MORE_HYPHENED, choice=['one', 'two', 'three'])
    values = ['one', 'two']
    prop1 = common.Property(name='prop1', value='value1')
    prop2 = common.Property(name='prop2', value='value2', remarks='remark2')
    param = common.Parameter(
        id='param1',
        label='label1',
        values=values,
        props=[prop1, prop2],
        select=sel,
        remarks='remarks1',
        constraints=constraints
    )
    param_dict = ModelUtils.parameter_to_dict(param, False)
    dict_copy = copy.deepcopy(param_dict)
    new_param = ModelUtils.dict_to_parameter(dict_copy)
    assert param == new_param

    # confirm it strips items properly to partial form
    partial_dict = ModelUtils.parameter_to_dict(param, True)
    new_partial_param = ModelUtils.dict_to_parameter(partial_dict)
    partial_param = common.Parameter(id='param1', label='label1', values=values, select=sel)
    assert new_partial_param == partial_param

    # confirm that disallowed attributes raise exception
    dict_copy = copy.deepcopy(param_dict)
    dict_copy['foo'] = 'bar'
    with pytest.raises(ValidationError):
        _ = ModelUtils.dict_to_parameter(dict_copy)

    # confirm that bad string for how-many raises exception
    dict_copy = copy.deepcopy(param_dict)
    dict_copy['select']['how_many'] = 'seven'
    with pytest.raises(err.TrestleError):
        _ = ModelUtils.dict_to_parameter(dict_copy)

    # confirm values must be among allowed choices or give warning
    sel = common.ParameterSelection(how_many=const.ONE_OR_MORE_HYPHENED, choice=['one', 'two', 'three'])
    param = common.Parameter(id='param1', label='label1', select=sel, values=['two', 'five'])
    param_dict = ModelUtils.parameter_to_dict(param, False)
    new_param = ModelUtils.dict_to_parameter(param_dict)
    assert param == new_param

    # confirm only one item if HowMany is one or give warning
    sel = common.ParameterSelection(how_many='one', choice=['one', 'two', 'three'])
    param = common.Parameter(id='param1', label='label1', select=sel, values=['two', 'three'])
    param_dict = ModelUtils.parameter_to_dict(param, False)
    new_param = ModelUtils.dict_to_parameter(param_dict)
    assert param == new_param

    # confirm special handling for one value works
    sel = common.ParameterSelection(how_many='one', choice=['one', 'two', 'three'])
    param = common.Parameter(id='param1', label='label1', select=sel, values=['two'])
    param_dict = ModelUtils.parameter_to_dict(param, False)
    assert param == ModelUtils.dict_to_parameter(param_dict)


def test_find_all_prose(simplified_nist_catalog: catalog.Catalog) -> None:
    """Test get all prose from catalog."""
    prose_list = ModelUtils.find_values_by_name(simplified_nist_catalog, 'prose')
    n_lines = len(prose_list)
    assert n_lines == 225


def test_strip_lower_equals() -> None:
    """Test strip lower equals."""
    assert str_utils.strip_lower_equals('  Foo Bar  ', 'FOO baR')
    assert str_utils.strip_lower_equals('  Foo Bar  ', '  FOO baR  ')
    assert not str_utils.strip_lower_equals('  Foo Bar  ', '  FOO  baR  ')
    assert not str_utils.strip_lower_equals(None, '  ')
    assert not str_utils.strip_lower_equals(None, None)
    assert str_utils.strip_lower_equals('', '')


def test_objects_differ(simplified_nist_catalog: catalog.Catalog) -> None:
    """Test objects differ."""
    cat_b = copy.deepcopy(simplified_nist_catalog)
    assert not ModelUtils._objects_differ(simplified_nist_catalog, cat_b, [], [], False)
    ModelUtils.update_last_modified(cat_b)
    assert ModelUtils._objects_differ(simplified_nist_catalog, cat_b, [], [], False)
    assert not ModelUtils._objects_differ(
        simplified_nist_catalog, cat_b, [common.LastModified], ['last_modified'], False
    )
    cat_c, _, _ = ModelUtils.regenerate_uuids(cat_b)
    assert ModelUtils._objects_differ(simplified_nist_catalog, cat_c, [common.LastModified], ['last_modified'], False)
    assert not ModelUtils._objects_differ(
        simplified_nist_catalog, cat_c, [common.LastModified], ['last_modified', 'uuid', 'party_uuids'], False
    )
    assert not ModelUtils._objects_differ(
        simplified_nist_catalog, cat_c, [common.LastModified], ['last_modified'], True
    )


def test_fields_set_non_none() -> None:
    """Confirm that using fields_set can be bad."""
    prop = common.Property(name='foo', value='bar')
    assert prop.__fields_set__ == {'name', 'value'}
    prop.ns = None
    # fields_set lists value even though it was set as None
    assert prop.__fields_set__ == {'name', 'value', 'ns'}
    assert ModelUtils.fields_set_non_none(prop) == {'name', 'value'}


def test_models_are_equivalent(simplified_nist_catalog: catalog.Catalog) -> None:
    """Test models are equivalent."""
    cat_b = copy.deepcopy(simplified_nist_catalog)
    assert ModelUtils.models_are_equivalent(simplified_nist_catalog, cat_b)
    ModelUtils.update_last_modified(cat_b)
    # different last-modified is ignored
    assert ModelUtils.models_are_equivalent(simplified_nist_catalog, cat_b)
    cat_b, _, _ = ModelUtils.regenerate_uuids(cat_b)
    # different uuids fail comparison
    assert not ModelUtils.models_are_equivalent(simplified_nist_catalog, cat_b)
    # ignoring uuids passes comparison
    assert ModelUtils.models_are_equivalent(simplified_nist_catalog, cat_b, True)


def test_get_title_from_source(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test get source title."""
    prof_uri = str(test_utils.JSON_TEST_DATA_PATH / 'simple_test_profile.json')
    assert ModelUtils.get_title_from_model_uri(tmp_trestle_dir, prof_uri) == 'Trestle test profile'
    with pytest.raises(TrestleError):
        ModelUtils.get_title_from_model_uri(tmp_trestle_dir, 'foo_bar')


def test_prune_empty_dirs(tmp_path: pathlib.Path) -> None:
    """Test prune empty dirs."""
    (tmp_path / 'sub1/sub11/sub111').mkdir(parents=True)
    (tmp_path / 'sub2/sub21/sub211').mkdir(parents=True)
    (tmp_path / 'sub3/sub31/sub311/sub3111').mkdir(parents=True)
    foo_path = tmp_path / 'sub1/sub11/foo.md'
    foo_path.touch()
    txt_path = tmp_path / 'sub1/sub11/sub111/readme.txt'
    txt_path.touch()
    bar_path = tmp_path / 'sub2/bar.md'
    bar_path.touch()
    futils.prune_empty_dirs(tmp_path, '*.md')
    assert not (tmp_path / 'sub3').exists()
    assert not (tmp_path / 'sub1/sub11/sub111').exists()
    assert foo_path.exists()
    assert bar_path.exists()
