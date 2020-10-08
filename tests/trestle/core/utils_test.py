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

import pytest

import trestle.core.parser as parser
import trestle.core.utils as mutils
import trestle.oscal.assessment_plan as assessment_plan
import trestle.oscal.assessment_results as assessment_results
import trestle.oscal.catalog as catalog
import trestle.oscal.component as component
import trestle.oscal.poam as poam
import trestle.oscal.profile as profile
import trestle.oscal.ssp as ssp
import trestle.oscal.target as target
from trestle.core.err import TrestleError


def load_good_catalog():
    """Load nist 800-53 as a catalog example."""
    good_sample_path = pathlib.Path('nist-source/content/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json')

    assert (good_sample_path.exists())
    return parser.wrap_for_input(catalog.Catalog).parse_file(good_sample_path).catalog


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
    catalog_field = catalog.Model.get_fields_by_alias()['catalog']
    assert mutils.is_collection_field_type(catalog_field.outer_type_) is False  # Catalog

    assert mutils.is_collection_field_type(type(good_catalog.metadata)) is False  # Metadata
    metadata_field = catalog.Catalog.get_fields_by_alias()['metadata']
    assert mutils.is_collection_field_type(metadata_field.outer_type_) is False  # Metadata

    assert mutils.is_collection_field_type(type(good_catalog.metadata.roles)) is False  # list
    roles_field = catalog.Metadata.get_fields_by_alias()['roles']
    assert mutils.is_collection_field_type(roles_field.outer_type_) is True  # List[Role]
    assert mutils.is_collection_field_type(roles_field.type_) is False  # Role

    assert mutils.is_collection_field_type(type(good_catalog.metadata.responsible_parties)) is False  # list
    responsible_parties_field = catalog.Metadata.get_fields_by_alias()['responsible-parties']
    assert mutils.is_collection_field_type(responsible_parties_field.outer_type_) is True  # Dict[str, ResponsibleParty]
    assert mutils.is_collection_field_type(responsible_parties_field.type_) is False  # ResponsibleParty

    assert mutils.is_collection_field_type(
        type(good_catalog.metadata.parties[0].addresses[0].postal_address)
    ) is False  # list
    postal_address_field = catalog.Address.get_fields_by_alias()['postal-address']
    assert mutils.is_collection_field_type(postal_address_field.outer_type_) is True  # List[AddrLine]
    assert mutils.is_collection_field_type(postal_address_field.type_) is False  # AddrLine


def test_get_inner_type():
    """Test retrievel of inner type of a model field representing a collection."""
    good_catalog = load_good_catalog()

    with pytest.raises(TrestleError):
        # Type of catalog is not a collection field type
        mutils.get_inner_type(type(good_catalog))

    with pytest.raises(TrestleError):
        # Type of field catalog is not a collection field type
        catalog_field = catalog.Model.get_fields_by_alias()['catalog']
        mutils.get_inner_type(catalog_field.outer_type_)

    with pytest.raises(TrestleError):
        # Type of roles object is not a collection field type
        mutils.get_inner_type(type(good_catalog.metadata.roles))

    # Type of field roles is a collection field type
    roles_field = catalog.Metadata.get_fields_by_alias()['roles']
    role_type = mutils.get_inner_type(roles_field.outer_type_)
    assert role_type == catalog.Role

    with pytest.raises(TrestleError):
        # Type of responsible_parties object is not a collection field type
        mutils.get_inner_type(type(good_catalog.metadata.responsible_parties))

    # Type of field responsible-parties is a collection field type
    responsible_parties_field = catalog.Metadata.get_fields_by_alias()['responsible-parties']
    responsible_party_type = mutils.get_inner_type(responsible_parties_field.outer_type_)
    assert responsible_party_type == catalog.ResponsibleParty


def test_get_root_model():
    """Test looking for the root model of a trestle oscal module."""
    with pytest.raises(TrestleError):
        mutils.get_root_model('invalid')

    with pytest.raises(TrestleError):
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
