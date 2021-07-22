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
"""Tests for cli module command validate."""
import argparse
import pathlib
import shutil
import sys
from unittest.mock import patch
from uuid import uuid4

import pytest

from tests import test_utils

import trestle.core.const as const
import trestle.oscal.assessment_plan as ap
from trestle import cli
from trestle.core.generators import generate_sample_model
from trestle.core.validator import Validator
from trestle.core.validator_factory import validator_factory
from trestle.oscal.catalog import Catalog
from trestle.oscal.common import PartyUuid, ResponsibleParty, Role
from trestle.oscal.component import ComponentDefinition, ControlImplementation

test_data_dir = pathlib.Path('tests/data').resolve()


@pytest.mark.parametrize(
    'name, mode, parent',
    [
        ('my_test_model', '-f', False), ('my_test_model', '-n', False), ('my_test_model', '-f', True),
        ('my_test_model', '-t', False), ('my_test_model', '-a', False), ('my_test_model', '-x', False)
    ]
)
def test_validation_happy(name, mode, parent, tmp_trestle_dir: pathlib.Path) -> None:
    """Test successful validation runs."""
    (tmp_trestle_dir / test_utils.CATALOGS_DIR / 'my_test_model').mkdir(exist_ok=True, parents=True)
    (tmp_trestle_dir / test_utils.CATALOGS_DIR / 'my_test_model2').mkdir(exist_ok=True, parents=True)
    shutil.copyfile(
        test_data_dir / 'json/minimal_catalog.json',
        tmp_trestle_dir / test_utils.CATALOGS_DIR / 'my_test_model/catalog.json'
    )
    shutil.copyfile(
        test_data_dir / 'json/minimal_catalog.json',
        tmp_trestle_dir / test_utils.CATALOGS_DIR / 'my_test_model2/catalog.json'
    )

    model_def_file = tmp_trestle_dir / test_utils.CATALOGS_DIR / ('my_test_model/catalog.json')

    if mode == '-f':
        if not parent:
            testcmd = f'trestle validate {mode} {model_def_file}'
        else:
            testcmd = f'trestle validate {mode} {model_def_file.parent}'
    elif mode == '-n':
        testcmd = f'trestle validate -t catalog -n {name}'
    elif mode == '-x':
        testcmd = f'trestle validate -t catalog -n {name}'
    else:
        testcmd = 'trestle validate -a'

    with patch.object(sys, 'argv', testcmd.split()):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0


@pytest.mark.parametrize(
    'name, mode, parent',
    [
        ('my_test_model', '-f', False), ('my_test_model', '-n', False), ('my_test_model', '-f', True),
        ('my_test_model', '-t', False), ('my_test_model', '-a', False), ('foo', '-n', False),
        ('my_test_model', '-x', False)
    ]
)
def test_validation_unhappy(name, mode, parent, tmp_trestle_dir: pathlib.Path) -> None:
    """Test failure modes of validation."""
    (tmp_trestle_dir / test_utils.CATALOGS_DIR / 'my_test_model').mkdir(exist_ok=True, parents=True)
    (tmp_trestle_dir / test_utils.CATALOGS_DIR / 'my_test_model2').mkdir(exist_ok=True, parents=True)
    shutil.copyfile(
        test_data_dir / 'json/minimal_catalog_bad_oscal_version.json',
        tmp_trestle_dir / test_utils.CATALOGS_DIR / 'my_test_model/catalog.json'
    )
    shutil.copyfile(
        test_data_dir / 'json/minimal_catalog.json',
        tmp_trestle_dir / test_utils.CATALOGS_DIR / 'my_test_model2/catalog.json'
    )

    model_def_file = tmp_trestle_dir / test_utils.CATALOGS_DIR / ('my_test_model/catalog.json')

    if mode == '-f':
        if not parent:
            testcmd = f'trestle validate {mode} {model_def_file}'
        else:
            testcmd = f'trestle validate {mode} {model_def_file.parent}'
    elif mode == '-n':
        testcmd = f'trestle validate -t catalog -n {name}'
    elif mode == '-x':
        testcmd = f'trestle validate -t catalog -n {name}'
    else:
        testcmd = 'trestle validate -a'

    with patch.object(sys, 'argv', testcmd.split()):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1


@pytest.mark.parametrize(
    'name, mode, parent, test_id, code',
    [
        ('my_ap', '-f', False, 'id1', 0), ('my_ap', '-n', False, 'id1', 0), ('my_ap', '-f', True, 'id1', 0),
        ('my_ap', '-t', False, 'id1', 0), ('my_ap', '-a', False, 'id1', 0), ('my_ap', '-f', False, 'foo', 1),
        ('my_ap', '-n', False, 'foo', 1), ('my_ap', '-f', True, 'foo', 1), ('my_ap', '-t', False, 'foo', 1),
        ('my_ap', '-a', False, 'foo', 1), ('foo', '-n', False, 'id1', 1)
    ]
)
def test_role_refs_validator(name, mode, parent, test_id, code, tmp_trestle_dir: pathlib.Path) -> None:
    """Test validation of roles and references to them in responsible-parties."""
    (tmp_trestle_dir / 'assessment-plans/my_ap').mkdir(exist_ok=True, parents=True)
    roles = [Role(id='id1', title='title1'), Role(id='id2', title='title2'), Role(id='id3', title='title3')]
    party1 = ResponsibleParty(role_id=test_id, party_uuids=[PartyUuid(__root__=str(uuid4()))])
    party2 = ResponsibleParty(role_id='id2', party_uuids=[PartyUuid(__root__=str(uuid4()))])
    responsible_parties = [party1, party2]
    ap_obj = generate_sample_model(ap.AssessmentPlan)
    ap_obj.metadata.roles = roles
    ap_obj.metadata.responsible_parties = responsible_parties
    ap_path = tmp_trestle_dir / 'assessment-plans/my_ap/assessment-plan.json'
    ap_obj.oscal_write(ap_path)

    if mode == '-f':
        if not parent:
            testcmd = f'trestle validate {mode} {ap_path}'
        else:
            testcmd = f'trestle validate {mode} {ap_path.parent}'
    elif mode == '-n':
        testcmd = f'trestle validate -t assessment-plan -n {name}'
    elif mode == '-t':
        testcmd = 'trestle validate -t assessment-plan'
    else:
        testcmd = 'trestle validate -a'

    with patch.object(sys, 'argv', testcmd.split()):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == code


@pytest.mark.parametrize('code', [0, 1])
def test_oscal_version_validator(tmp_trestle_dir: pathlib.Path, sample_catalog_minimal: Catalog, code: int) -> None:
    """Test oscal version validator."""
    if code:
        sample_catalog_minimal.metadata.oscal_version.__root__ = '1.0.0-rc1'
    mycat_dir = tmp_trestle_dir / 'catalogs/mycat'
    mycat_dir.mkdir()
    sample_catalog_minimal.oscal_write(mycat_dir / 'catalog.json')
    testcmd = 'trestle validate -t catalog'
    with patch.object(sys, 'argv', testcmd.split()):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == code


def test_validate_direct(sample_catalog_minimal: Catalog) -> None:
    """Test a validator by invoking it directly without CLI."""
    args = argparse.Namespace(mode=const.VAL_MODE_ALL)
    validator: Validator = validator_factory.get(args)
    assert validator.model_is_valid(sample_catalog_minimal)


def test_validate_dup_uuids(sample_component_definition: ComponentDefinition) -> None:
    """Test validation of comp def with duplicate uuids."""
    args = argparse.Namespace(mode=const.VAL_MODE_ALL)
    validator = validator_factory.get(args)

    # confirm the comp_def is valid
    assert validator.model_is_valid(sample_component_definition)

    # force two components to have same uuid and confirm invalid
    sample_component_definition.components[1].uuid = sample_component_definition.components[0].uuid
    assert not validator.model_is_valid(sample_component_definition)

    # restore uuid to unique value and confirm it is valid again
    sample_component_definition.components[1].uuid = str(uuid4())
    assert validator.model_is_valid(sample_component_definition)

    # add a control implementation to one of the components and confirm valid
    control_imp: ControlImplementation = generate_sample_model(ControlImplementation)
    sample_component_definition.components[1].control_implementations = [control_imp]
    assert validator.model_is_valid(sample_component_definition)

    # force the control implementation to have same uuid as the first component and confirm invalid
    sample_component_definition.components[1].control_implementations[0].uuid = sample_component_definition.components[
        0].uuid
    assert not validator.model_is_valid(sample_component_definition)
