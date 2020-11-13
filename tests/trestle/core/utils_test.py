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
"""Tests for models util module."""
import pathlib
import uuid
from datetime import datetime
from typing import Any

from pydantic import ConstrainedStr, typing

import pytest

import trestle.core.err as err
import trestle.core.utils as mutils
import trestle.oscal.assessment_plan as assessment_plan
import trestle.oscal.assessment_results as assessment_results
import trestle.oscal.catalog as catalog
import trestle.oscal.component as component
import trestle.oscal.poam as poam
import trestle.oscal.profile as profile
import trestle.oscal.ssp as ssp
import trestle.oscal.target as target


def load_good_catalog():
    """Load nist 800-53 as a catalog example."""
    good_sample_path = pathlib.Path('nist-content/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json')

    assert (good_sample_path.exists())
    return catalog.Catalog.oscal_read(good_sample_path)


def test_get_elements():
    """Test getting flat list of elements."""
    good_sample = load_good_catalog()

    mdlist = mutils.get_elements_of_model_type(good_sample, catalog.Metadata)
    assert (type(mdlist) == list)
    # can only be 1 metadata
    assert (len(mdlist) == 1)
    assert (type(mdlist[0]) == catalog.Metadata)

    control_list = mutils.get_elements_of_model_type(good_sample, catalog.Control)
    assert (len(control_list) >= 1)
    group_list = mutils.get_elements_of_model_type(good_sample, catalog.Group)
    assert (len(group_list) >= 2)


def test_is_collection_field_type():
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
    roles_field = catalog.Metadata.alias_to_field_map()['roles']
    assert mutils.is_collection_field_type(roles_field.outer_type_) is True  # List[Role]
    assert mutils.is_collection_field_type(roles_field.type_) is False  # Role

    assert mutils.is_collection_field_type(type(good_catalog.metadata.responsible_parties)) is False  # list
    responsible_parties_field = catalog.Metadata.alias_to_field_map()['responsible-parties']
    assert mutils.is_collection_field_type(responsible_parties_field.outer_type_) is True  # Dict[str, ResponsibleParty]
    assert mutils.is_collection_field_type(responsible_parties_field.type_) is False  # ResponsibleParty

    assert mutils.is_collection_field_type(
        type(good_catalog.metadata.parties[0].addresses[0].postal_address)
    ) is False  # list
    postal_address_field = catalog.Address.alias_to_field_map()['postal-address']
    assert mutils.is_collection_field_type(postal_address_field.outer_type_) is True  # List[AddrLine]
    assert mutils.is_collection_field_type(postal_address_field.type_) is False  # AddrLine


def test_get_inner_type():
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
    roles_field = catalog.Metadata.alias_to_field_map()['roles']
    role_type = mutils.get_inner_type(roles_field.outer_type_)
    assert role_type == catalog.Role

    with pytest.raises(err.TrestleError):
        # Type of responsible_parties object is not a collection field type
        mutils.get_inner_type(type(good_catalog.metadata.responsible_parties))

    # Type of field responsible-parties is a collection field type
    responsible_parties_field = catalog.Metadata.alias_to_field_map()['responsible-parties']
    responsible_party_type = mutils.get_inner_type(responsible_parties_field.outer_type_)
    assert responsible_party_type == catalog.ResponsibleParty


def test_get_root_model():
    """Test looking for the root model of a trestle oscal module."""
    with pytest.raises(err.TrestleError):
        mutils.get_root_model('invalid')

    with pytest.raises(err.TrestleError):
        mutils.get_root_model('pydantic')

    malias_to_mtype = {
        'catalog': catalog.Catalog,
        'profile': profile.Profile,
        'target-definition': target.TargetDefinition,
        'component-definition': component.ComponentDefinition,
        'system-security-plan': ssp.SystemSecurityPlan,
        'assessment-plan': assessment_plan.AssessmentPlan,
        'assessment-results': assessment_results.AssessmentResults,
        'plan-of-action-and-milestones': poam.PlanOfActionAndMilestones
    }
    for key in malias_to_mtype:
        module_name = malias_to_mtype[key].__module__
        model_type, model_alias = mutils.get_root_model(module_name)
        assert model_type == malias_to_mtype[key]
        assert model_alias == key


def test_classname_to_alias():
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

    short_classname = catalog.ResponsibleParty.__name__
    full_classname = f'{module_name}.{short_classname}'
    json_alias = mutils.classname_to_alias(short_classname, 'json')
    assert json_alias == 'responsible-party'
    json_alias = mutils.classname_to_alias(full_classname, 'field')
    assert json_alias == 'responsible_party'

    short_classname = catalog.Prop.__name__
    full_classname = f'{module_name}.{short_classname}'
    json_alias = mutils.classname_to_alias(short_classname, 'json')
    assert json_alias == 'prop'
    json_alias = mutils.classname_to_alias(full_classname, 'field')
    assert json_alias == 'prop'

    short_classname = catalog.MemberOfOrganization.__name__
    full_classname = f'{module_name}.{short_classname}'
    json_alias = mutils.classname_to_alias(short_classname, 'json')
    assert json_alias == 'member-of-organization'
    json_alias = mutils.classname_to_alias(full_classname, 'field')
    assert json_alias == 'member_of_organization'


def test_alias_to_classname() -> None:
    """Test alias_to_classname function."""
    assert mutils.alias_to_classname('target-definition', 'json') == 'TargetDefinition'
    assert mutils.alias_to_classname('target_definition', 'field') == 'TargetDefinition'

    with pytest.raises(err.TrestleError):
        assert mutils.alias_to_classname('target-definition', 'invalid') == 'TargetDefinition'


def is_valid_uuid(val: Any) -> bool:
    """Check if a string is a valid uuid."""
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def test_get_sample_value_by_type():
    """Test get_sample_value_by_type function."""
    assert type(mutils.get_sample_value_by_type(datetime, '')) == datetime
    assert mutils.get_sample_value_by_type(bool, '') is False
    assert mutils.get_sample_value_by_type(int, '') == 0
    assert mutils.get_sample_value_by_type(str, '') == 'REPLACE_ME'
    assert mutils.get_sample_value_by_type(float, '') == 0.0
    assert mutils.get_sample_value_by_type(ConstrainedStr, '') == '00000000-0000-4000-8000-000000000000'
    uuid_ = mutils.get_sample_value_by_type(ConstrainedStr, 'uuid')
    assert mutils.get_sample_value_by_type(ssp.SecuritySensitivityLevel, '') == ssp.SecuritySensitivityLevel('low')
    assert is_valid_uuid(uuid_) and str(uuid_) != '00000000-0000-4000-8000-000000000000'

    with pytest.raises(err.TrestleError):
        mutils.get_sample_value_by_type(list, 'uuid')


def test_get_target_model():
    """Test utils method get_target_model."""
    assert mutils.is_collection_field_type(
        mutils.get_target_model(['catalog', 'metadata', 'roles'], catalog.Catalog)
    ) is True
    assert (mutils.get_target_model(['catalog', 'metadata', 'roles'], catalog.Catalog)).__origin__ is list
    assert mutils.get_inner_type(
        mutils.get_target_model(['catalog', 'metadata', 'roles'], catalog.Catalog)
    ) is catalog.Role

    assert mutils.is_collection_field_type(
        mutils.get_target_model(['catalog', 'metadata', 'responsible-parties'], catalog.Catalog)
    ) is True
    assert mutils.get_target_model(['catalog', 'metadata', 'responsible-parties'], catalog.Catalog).__origin__ is dict
    assert mutils.get_inner_type(
        mutils.get_target_model(['catalog', 'metadata', 'responsible-parties'], catalog.Catalog)
    ) is catalog.ResponsibleParty

    assert mutils.is_collection_field_type(
        mutils.get_target_model(['catalog', 'metadata', 'responsible-parties', 'creator'], catalog.Catalog)
    ) is False
    assert mutils.get_target_model(
        ['catalog', 'metadata', 'responsible-parties', 'creator'], catalog.Catalog
    ) is catalog.ResponsibleParty

    assert mutils.get_target_model(['catalog', 'metadata', 'title'], catalog.Catalog) is catalog.Title

    with pytest.raises(err.TrestleError):
        mutils.get_target_model(['catalog', 'metadata', 'bad_element'], catalog.Catalog)


def test_get_sample_model():
    """Test utils method get_sample_model."""
    # Create the expected catalog first
    expected_ctlg_dict = {
        'uuid': 'ea784488-49a1-4ee5-9830-38058c7c10a4',
        'metadata': {
            'title': 'REPLACE_ME',
            'last-modified': '2020-10-21T06:52:10.387+00:00',
            'version': 'REPLACE_ME',
            'oscal-version': 'REPLACE_ME'
        }
    }
    expected_ctlg = catalog.Catalog(**expected_ctlg_dict)

    actual_ctlg = mutils.get_sample_model(catalog.Catalog)

    # Check if uuid is valid, then change to uuid of expected catalog, as newly generated
    # uuids will always be different
    assert is_valid_uuid(actual_ctlg.uuid)
    actual_ctlg.uuid = expected_ctlg.uuid
    # Check if last-modified datetime is of type datetime, and then equate in actual and expected
    assert type(actual_ctlg.metadata.last_modified) is catalog.LastModified
    actual_ctlg.metadata.last_modified = expected_ctlg.metadata.last_modified
    # Check that expected generated catalog is now same a actual catalog
    assert expected_ctlg == actual_ctlg

    # Test list type models
    expected_role = catalog.Role(**{'id': 'REPLACE_ME', 'title': 'REPLACE_ME'})
    list_role = mutils.get_sample_model(typing.List[catalog.Role])
    assert type(list_role) is list
    actual_role = list_role[0]
    assert expected_role == actual_role

    # Test dict type models
    expected_rp = {'party-uuids': ['00000000-0000-4000-8000-000000000000']}
    expected_rp = catalog.ResponsibleParty(**expected_rp)
    expected_rp_dict = {'REPLACE_ME': expected_rp}
    actual_rp_dict = mutils.get_sample_model(typing.Dict[str, catalog.ResponsibleParty])
    assert type(actual_rp_dict) is dict
    assert expected_rp_dict == actual_rp_dict
