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
import pathlib
import shutil
import sys
from unittest.mock import patch
from uuid import uuid4

import pytest

from tests import test_utils

import trestle.oscal.assessment_plan as ap
from trestle import cli
from trestle.core.generators import generate_sample_model

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
    (tmp_trestle_dir / test_utils.TARGET_DEFS_DIR / 'my_test_model').mkdir(exist_ok=True, parents=True)
    (tmp_trestle_dir / test_utils.TARGET_DEFS_DIR / 'my_test_model2').mkdir(exist_ok=True, parents=True)
    shutil.copyfile(
        test_data_dir / 'yaml/good_target.yaml',
        tmp_trestle_dir / test_utils.TARGET_DEFS_DIR / 'my_test_model/target-definition.yaml'
    )
    shutil.copyfile(
        test_data_dir / 'yaml/good_target.yaml',
        tmp_trestle_dir / test_utils.TARGET_DEFS_DIR / 'my_test_model2/target-definition.yaml'
    )

    model_def_file = tmp_trestle_dir / test_utils.TARGET_DEFS_DIR / name / ('target-definition.yaml')

    if mode == '-f':
        if not parent:
            testcmd = f'trestle validate {mode} {model_def_file} -m duplicates'
        else:
            testcmd = f'trestle validate {mode} {model_def_file.parent} -m duplicates'
    elif mode == '-n':
        testcmd = f'trestle validate -t target-definition -n {name} -m duplicates'
    elif mode == '-x':
        testcmd = f'trestle validate -t target-definition -n {name}'
    else:
        testcmd = 'trestle validate -a -m duplicates'

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
    (tmp_trestle_dir / test_utils.TARGET_DEFS_DIR / 'my_test_model').mkdir(exist_ok=True, parents=True)
    (tmp_trestle_dir / test_utils.TARGET_DEFS_DIR / 'my_test_model2').mkdir(exist_ok=True, parents=True)
    shutil.copyfile(
        test_data_dir / 'yaml/bad_target_dup_uuid.yaml',
        tmp_trestle_dir / test_utils.TARGET_DEFS_DIR / 'my_test_model/target-definition.yaml'
    )
    shutil.copyfile(
        test_data_dir / 'yaml/good_target.yaml',
        tmp_trestle_dir / test_utils.TARGET_DEFS_DIR / 'my_test_model2/target-definition.yaml'
    )

    model_def_file = tmp_trestle_dir / test_utils.TARGET_DEFS_DIR / ('my_test_model/target-definition.yaml')

    if mode == '-f':
        if not parent:
            testcmd = f'trestle validate {mode} {model_def_file} -m duplicates'
        else:
            testcmd = f'trestle validate {mode} {model_def_file.parent} -m duplicates'
    elif mode == '-n':
        testcmd = f'trestle validate -t target-definition -n {name} -m duplicates'
    elif mode == '-x':
        testcmd = f'trestle validate -t target-definition -n {name}'
    else:
        testcmd = 'trestle validate -a -m duplicates'

    with patch.object(sys, 'argv', testcmd.split()):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1


@pytest.mark.parametrize(
    'name, mode, parent, new_role, code',
    [
        ('my_ap', '-f', False, 'role', 0), ('my_ap', '-n', False, 'role', 0), ('my_ap', '-f', True, 'role', 0),
        ('my_ap', '-t', False, 'role', 0), ('my_ap', '-a', False, 'role', 0), ('my_ap', '-f', False, 'r:ole', 1),
        ('my_ap', '-n', False, 'r:ole', 1), ('my_ap', '-f', True, 'r:ole', 1), ('my_ap', '-t', False, 'r:ole', 1),
        ('my_ap', '-a', False, 'r:ole', 1), ('foo', '-n', False, 'role', 1)
    ]
)
def test_roleid_cases(name, mode, parent, new_role, code, tmp_trestle_dir: pathlib.Path) -> None:
    """Test good and bad roleid cases."""
    (tmp_trestle_dir / 'assessment-plans/my_ap').mkdir(exist_ok=True, parents=True)
    role_ids = [ap.RoleId(__root__='role1'), ap.RoleId(__root__=new_role), ap.RoleId(__root__='REPLACE_ME')]
    system_user = ap.SystemUser(role_ids=role_ids)
    local_definitions = ap.LocalDefinitions(users={'my_users': system_user})
    ap_obj = generate_sample_model(ap.AssessmentPlan)
    ap_obj.local_definitions = local_definitions
    ap_path = tmp_trestle_dir / 'assessment-plans/my_ap/assessment-plan.json'
    ap_obj.oscal_write(ap_path)

    if mode == '-f':
        if not parent:
            testcmd = f'trestle validate {mode} {ap_path} -m ncname'
        else:
            testcmd = f'trestle validate {mode} {ap_path.parent} -m ncname'
    elif mode == '-n':
        testcmd = f'trestle validate -t assessment-plan -n {name} -m ncname'
    elif mode == '-t':
        testcmd = 'trestle validate -t assessment-plan -m ncname'
    else:
        testcmd = 'trestle validate -a -m ncname'

    with patch.object(sys, 'argv', testcmd.split()):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == code


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
    roles = [ap.Role(id='id1', title='title1'), ap.Role(id='id2', title='title2'), ap.Role(id='id3', title='title3')]
    party1 = ap.ResponsibleParty(party_uuids=[ap.PartyUuid(__root__=str(uuid4()))])
    party2 = ap.ResponsibleParty(party_uuids=[ap.PartyUuid(__root__=str(uuid4()))])
    responsible_parties = {test_id: party1, 'id2': party2}
    ap_obj = generate_sample_model(ap.AssessmentPlan)
    ap_obj.metadata.roles = roles
    ap_obj.metadata.responsible_parties = responsible_parties
    ap_path = tmp_trestle_dir / 'assessment-plans/my_ap/assessment-plan.json'
    ap_obj.oscal_write(ap_path)

    if mode == '-f':
        if not parent:
            testcmd = f'trestle validate {mode} {ap_path} -m refs'
        else:
            testcmd = f'trestle validate {mode} {ap_path.parent} -m refs'
    elif mode == '-n':
        testcmd = f'trestle validate -t assessment-plan -n {name} -m refs'
    elif mode == '-t':
        testcmd = 'trestle validate -t assessment-plan -m refs'
    else:
        testcmd = 'trestle validate -a -m refs'

    with patch.object(sys, 'argv', testcmd.split()):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == code
