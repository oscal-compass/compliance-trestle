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
import pathlib

import pytest

import trestle.core.const as const
import trestle.core.err as err
import trestle.core.utils as mutils
import trestle.oscal.assessment_plan as assessment_plan
import trestle.oscal.assessment_results as assessment_results
import trestle.oscal.catalog as catalog
import trestle.oscal.common as common
import trestle.oscal.component as component
import trestle.oscal.poam as poam
import trestle.oscal.profile as profile
import trestle.oscal.ssp as ssp


def load_good_catalog() -> catalog.Catalog:
    """Load nist 800-53 as a catalog example."""
    good_sample_path = pathlib.Path('nist-content/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json')

    assert (good_sample_path.exists())
    return catalog.Catalog.oscal_read(good_sample_path)


def test_get_elements() -> None:
    """Test getting flat list of elements."""
    good_sample = load_good_catalog()

    mdlist = mutils.get_elements_of_model_type(good_sample, common.Metadata)
    assert (type(mdlist) == list)
    # can only be 1 metadata
    assert (len(mdlist) == 1)
    assert (type(mdlist[0]) == common.Metadata)

    control_list = mutils.get_elements_of_model_type(good_sample, catalog.Control)
    assert (len(control_list) >= 1)
    group_list = mutils.get_elements_of_model_type(good_sample, catalog.Group)
    assert (len(group_list) >= 2)


def test_is_collection_field_type() -> None:
    """Test for checking whether the type of a field in an OscalBaseModel object is a collection field."""
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
    assert mutils.is_collection_field_type(responsible_parties_field.outer_type_) is True  # Dict[str, ResponsibleParty]
    assert mutils.is_collection_field_type(responsible_parties_field.type_) is False  # ResponsibleParty

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
        mutils.get_root_model('invalid')

    with pytest.raises(err.TrestleError):
        mutils.get_root_model('pydantic')

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
        model_type, model_alias = mutils.get_root_model(module_name)
        assert model_type == malias_to_mtype[key]
        assert model_alias == key


def test_classname_to_alias() -> None:
    """Test conversion of class name to alias."""
    module_name = catalog.Catalog.__module__

    with pytest.raises(err.TrestleError):
        mutils.classname_to_alias('any', 'invalid_mode')

    short_classname = catalog.Catalog.__name__
    full_classname = f'{module_name}.{short_classname}'
    json_alias = mutils.classname_to_alias(short_classname, 'json')
    assert json_alias == 'catalog'
    json_alias = mutils.classname_to_alias(full_classname, 'field')
    assert json_alias == 'catalog'

    short_classname = common.ResponsibleParty.__name__
    full_classname = f'{module_name}.{short_classname}'
    json_alias = mutils.classname_to_alias(short_classname, 'json')
    assert json_alias == 'responsible-party'
    json_alias = mutils.classname_to_alias(full_classname, 'field')
    assert json_alias == 'responsible_party'

    short_classname = common.Property.__name__
    full_classname = f'{module_name}.{short_classname}'
    json_alias = mutils.classname_to_alias(short_classname, 'json')
    assert json_alias == 'property'
    json_alias = mutils.classname_to_alias(full_classname, 'field')
    assert json_alias == 'property'

    short_classname = common.MemberOfOrganization.__name__
    full_classname = f'{module_name}.{short_classname}'
    json_alias = mutils.classname_to_alias(short_classname, 'json')
    assert json_alias == 'member-of-organization'
    json_alias = mutils.classname_to_alias(full_classname, 'field')
    assert json_alias == 'member_of_organization'


def test_snake_to_upper_camel() -> None:
    """Ensure Snake to upper camel behaves correctly."""
    cammeled = mutils.snake_to_upper_camel('component_definition')
    assert cammeled == 'ComponentDefinition'
    cammeled = mutils.snake_to_upper_camel('control')
    assert cammeled == 'Control'
    cammeled = mutils.snake_to_upper_camel('')
    assert cammeled == ''


def test_camel_to_snake() -> None:
    """Ensure camel to snake behaves correctly."""
    snaked = mutils.camel_to_snake('ComponentDefinition')
    assert snaked == 'component_definition'
    snaked = mutils.camel_to_snake('Control')
    assert snaked == 'control'
    snaked = mutils.camel_to_snake('')
    assert snaked == ''


def test_alias_to_classname() -> None:
    """Test alias_to_classname function."""
    assert mutils.alias_to_classname('component-definition', 'json') == 'ComponentDefinition'
    assert mutils.alias_to_classname('component_definition', 'field') == 'ComponentDefinition'

    with pytest.raises(err.TrestleError):
        assert mutils.alias_to_classname('component-definition', 'invalid') == 'ComponentDefinition'
