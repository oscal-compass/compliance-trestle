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
"""Tests for cli module command validate."""
import argparse
import pathlib
import shutil
import sys
from uuid import uuid4

from _pytest.monkeypatch import MonkeyPatch

import pytest

from tests import test_utils
from tests.test_utils import setup_for_ssp

import trestle.common.const as const
import trestle.core.generators as gens
import trestle.oscal.assessment_plan as ap
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ossp
from trestle import cli
from trestle.cli import Trestle
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.commands.split import SplitCmd
from trestle.core.generators import generate_sample_model
from trestle.core.models.file_content_type import FileContentType
from trestle.core.validator import Validator
from trestle.core.validator_factory import validator_factory
from trestle.oscal.catalog import Catalog
from trestle.oscal.common import ResponsibleParty, Role
from trestle.oscal.component import ComponentDefinition, ControlImplementation

test_data_dir = pathlib.Path('tests/data').resolve()

md_path = 'md_comp'


@pytest.mark.parametrize(
    'name, mode, parent',
    [
        ('my_test_model', '-f', False), ('my_test_model', '-n', False), ('my_test_model', '-f', True),
        ('my_test_model', '-t', False), ('my_test_model', '-a', False), ('my_test_model', '-x', False)
    ]
)
def test_validation_happy(name, mode, parent, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
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

    monkeypatch.setattr(sys, 'argv', testcmd.split())
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.run()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0


@pytest.mark.parametrize(
    'name, mode, parent, status',
    [
        ('my_test_model', '-f', False, 1), ('my_test_model', '-n', False, 4), ('my_test_model', '-f', True, 1),
        ('my_test_model', '-t', False, 1), ('my_test_model', '-a', False, 1), ('foo', '-n', False, 4),
        ('my_test_model', '-x', False, 4)
    ]
)
def test_validation_unhappy(
    name, mode, parent, status, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
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

    monkeypatch.setattr(sys, 'argv', testcmd.split())
    rc = Trestle().run()
    assert rc == status


@pytest.mark.parametrize(
    'name, mode, parent, test_id, code',
    [
        ('my_ap', '-f', False, 'id1', 0), ('my_ap', '-n', False, 'id1', 0), ('my_ap', '-f', True, 'id1', 0),
        ('my_ap', '-t', False, 'id1', 0), ('my_ap', '-a', False, 'id1', 0), ('my_ap', '-f', False, 'foo', 4),
        ('my_ap', '-n', False, 'foo', 4), ('my_ap', '-f', True, 'foo', 4), ('my_ap', '-t', False, 'foo', 4),
        ('my_ap', '-a', False, 'foo', 4), ('foo', '-n', False, 'id1', 4)
    ]
)
def test_role_refs_validator(
    name, mode, parent, test_id, code, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test validation of roles and references to them in responsible-parties."""
    (tmp_trestle_dir / 'assessment-plans/my_ap').mkdir(exist_ok=True, parents=True)
    roles = [Role(id='id1', title='title1'), Role(id='id2', title='title2'), Role(id='id3', title='title3')]
    party1 = ResponsibleParty(role_id=test_id, party_uuids=[str(uuid4())])
    party2 = ResponsibleParty(role_id='id2', party_uuids=[str(uuid4())])
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

    monkeypatch.setattr(sys, 'argv', testcmd.split())
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.run()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == code


def test_oscal_version_validator(
    tmp_trestle_dir: pathlib.Path, sample_catalog_minimal: Catalog, monkeypatch: MonkeyPatch
) -> None:
    """
    Test oscal version validator.

    There is no actual validator for oscal version but it happens in base_model when a file is loaded.
    """
    mycat_dir = tmp_trestle_dir / 'catalogs/mycat'
    mycat_dir.mkdir()
    mycat_path = mycat_dir / 'catalog.json'
    sample_catalog_minimal.oscal_write(mycat_path)
    testcmd = 'trestle validate -t catalog'
    monkeypatch.setattr(sys, 'argv', testcmd.split())
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.run()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == CmdReturnCodes.SUCCESS.value


def test_oscal_version_incorrect_validator(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test validation fails for bad oscal version. Short pydantic message should be printed."""
    catalog_path = test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog_bad_oscal_version.json'
    mycat_dir = tmp_trestle_dir / 'catalogs/mycat'
    mycat_dir.mkdir()
    mycat_path = mycat_dir / 'catalog.json'
    shutil.copyfile(catalog_path, mycat_path)
    testcmd = f'trestle validate -f {mycat_path}'
    monkeypatch.setattr(sys, 'argv', testcmd.split())
    rc = Trestle().run()
    assert rc == 1


def test_oscal_incorrect_fields_validator(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test validation fails for oscal with extra fields. Full pydantic message should be printed."""
    catalog_path = test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog_extra_fields.json'
    mycat_dir = tmp_trestle_dir / 'catalogs/mycat'
    mycat_dir.mkdir()
    catalog = mycat_dir / 'catalog.json'
    catalog.touch()
    shutil.copyfile(catalog_path, catalog)
    testcmd = f'trestle validate -f {catalog}'
    monkeypatch.setattr(sys, 'argv', testcmd.split())
    rc = Trestle().run()
    assert rc == 1


def test_validate_direct(sample_catalog_minimal: Catalog, tmp_trestle_dir: pathlib.Path) -> None:
    """Test a validator by invoking it directly without CLI."""
    args = argparse.Namespace(mode=const.VAL_MODE_ALL, quiet=True)
    validator: Validator = validator_factory.get(args)
    assert validator.model_is_valid(sample_catalog_minimal, True, tmp_trestle_dir)


def test_validate_dup_uuids(
    sample_component_definition: ComponentDefinition, sample_trestle_profile: prof.Profile
) -> None:
    """Test validation of comp def with duplicate uuids."""
    args = argparse.Namespace(mode=const.VAL_MODE_ALL, quiet=True)
    validator = validator_factory.get(args)

    # confirm the comp_def has duplicate param_ids (REPLACE_ME)
    ci = sample_component_definition.components[0].control_implementations[0]
    assert ci.set_parameters[0].param_id == ci.implemented_requirements[0].set_parameters[0].param_id

    # confirm the comp_def is valid despite duplicate param_ids (this is allowed for compdef and ssp)
    assert validator.model_is_valid(sample_component_definition, False)

    # force two components to have same uuid and confirm invalid
    sample_component_definition.components[1].uuid = sample_component_definition.components[0].uuid
    assert not validator.model_is_valid(sample_component_definition, True, None)

    # restore uuid to unique value and confirm it is valid again
    sample_component_definition.components[1].uuid = str(uuid4())
    assert validator.model_is_valid(sample_component_definition, False, None)

    # add a control implementation to one of the components and confirm valid
    control_imp: ControlImplementation = generate_sample_model(ControlImplementation)
    sample_component_definition.components[1].control_implementations = [control_imp]
    assert validator.model_is_valid(sample_component_definition, True, None)

    # force the control implementation to have same uuid as the first component and confirm invalid
    sample_component_definition.components[1].control_implementations[0].uuid = sample_component_definition.components[
        0].uuid
    assert not validator.model_is_valid(sample_component_definition, True, None)

    assert validator.model_is_valid(sample_trestle_profile, True)

    # add extra set_param with duplicate param_id and confirm it is not valid
    # only profile has this additional test
    set_param = sample_trestle_profile.modify.set_parameters[0].copy()
    set_param.values = ['foo']
    sample_trestle_profile.modify.set_parameters.append(set_param)
    assert not validator.model_is_valid(sample_trestle_profile, True)


def test_validate_distributed(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Check that validate will run correctly when exploiting load distributed."""
    test_utils.ensure_trestle_config_dir(tmp_trestle_dir)
    # Clean up.
    test_data_source = testdata_dir / 'split_merge/step0-merged_catalog/catalogs'
    catalogs_dir = tmp_trestle_dir / 'catalogs'
    shutil.rmtree(catalogs_dir)
    shutil.copytree(test_data_source, catalogs_dir)

    args = argparse.Namespace(
        name='split',
        file='catalogs/mycatalog/catalog.json',
        verbose=1,
        element='catalog.groups.*.controls.*',
        trestle_root=tmp_trestle_dir
    )
    _ = SplitCmd()._run(args)
    test_args = 'trestle validate -a -v'.split(' ')
    monkeypatch.setattr(sys, 'argv', test_args)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli.run()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0


def test_validate_catalog_params(sample_catalog_rich_controls: Catalog) -> None:
    """Test validation of unique param ids in catalog."""
    args = argparse.Namespace(mode=const.VAL_MODE_CATALOG)
    validator: Validator = validator_factory.get(args)
    assert validator.model_is_valid(sample_catalog_rich_controls, True, None)
    param_0_id = sample_catalog_rich_controls.groups[0].controls[0].params[0].id
    sample_catalog_rich_controls.groups[0].controls[0].params[1].id = param_0_id
    assert not validator.model_is_valid(sample_catalog_rich_controls, False, None)


def test_rule_param_values_validator_happy(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test validation of rules in SSP."""
    args = argparse.Namespace(mode=const.VAL_MODE_RULES)
    validator: Validator = validator_factory.get(args)
    prof_name = 'comp_prof'
    ssp_name = 'new_ssp'

    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    test_utils.gen_and_assemble_first_ssp(prof_name, ssp_name, gen_args, monkeypatch)

    new_ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    imp_reqs = new_ssp.control_implementation.implemented_requirements
    imp_req = next((i_req for i_req in imp_reqs if i_req.control_id == 'ac-3'), None)
    imp_req.by_components[0].set_parameters[1].values[0] = 'shared_param_1_aa_opt_1'
    ModelUtils.save_top_level_model(new_ssp, tmp_trestle_dir, ssp_name, FileContentType.JSON)

    assert validator.model_is_valid(new_ssp, True, tmp_trestle_dir)


def test_rule_param_values_validator_unhappy(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test validation of rules in SSP."""
    args = argparse.Namespace(mode=const.VAL_MODE_RULES)
    validator: Validator = validator_factory.get(args)
    prof_name = 'comp_prof'
    ssp_name = 'my_ssp'

    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    args_compdefs = gen_args.compdefs
    test_utils.gen_and_assemble_first_ssp(prof_name, ssp_name, gen_args, monkeypatch)

    orig_ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    # starts editing by grabbing by components from second imp req
    imp_reqs = orig_ssp.control_implementation.implemented_requirements
    imp_req = next((i_req for i_req in imp_reqs if i_req.control_id == 'ac-3'), None)
    by_components = imp_req.by_components
    # changes values for set parameter to test inequality
    by_components[0].set_parameters[1].values = ['shared_param_1_ab_opt_3']

    ModelUtils.save_top_level_model(orig_ssp, tmp_trestle_dir, ssp_name, FileContentType.JSON)
    assert not validator.model_is_valid(orig_ssp, True, tmp_trestle_dir)

    # test a by_component statement param value is added and
    # reassemble ssp
    ssp_assemble = f'trestle author ssp-assemble -m {ssp_name} -o {ssp_name} -cd {args_compdefs}'
    test_utils.execute_command_and_assert(ssp_assemble, 0, monkeypatch)
    # load new ssp
    new_ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    # grabs by component elements at statement level
    imp_reqs = new_ssp.control_implementation.implemented_requirements
    imp_req_ac = next((i_req for i_req in imp_reqs if i_req.control_id == 'ac-1'), None)
    by_components = imp_req_ac.statements[0].by_components
    by_components[1].set_parameters = []

    new_set_parameter_a = gens.generate_sample_model(ossp.SetParameter)
    new_set_parameter_a.values = ['shared_param_1_ab_opt_3']
    new_set_parameter_a.param_id = 'shared_param_1'
    # addes new value to current set parameter values
    # adds a new set parameter to set parameters array for current by component in statement
    by_components[1].set_parameters.append(new_set_parameter_a)
    imp_reqs = new_ssp.control_implementation.implemented_requirements
    imp_req_at = next((i_req for i_req in imp_reqs if i_req.control_id == 'at-1'), None)
    by_components = imp_req_at.statements[0].by_components
    by_components[0].set_parameters = []
    new_set_parameter_b = gens.generate_sample_model(ossp.SetParameter)
    new_set_parameter_b.values = ['shared_param_1_ab_opt_1']
    new_set_parameter_b.param_id = 'shared_param_1'
    by_components[0].set_parameters.append(new_set_parameter_b)

    ModelUtils.save_top_level_model(new_ssp, tmp_trestle_dir, ssp_name, FileContentType.JSON)
    assert not validator.model_is_valid(new_ssp, True, tmp_trestle_dir)
    # cleaning up the mess
    test_utils.gen_and_assemble_first_ssp(prof_name, ssp_name, gen_args, monkeypatch)


def test_validate_ssp_with_no_profile(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test validation of rules in SSP."""
    args = argparse.Namespace(mode=const.VAL_MODE_RULES)
    validator: Validator = validator_factory.get(args)
    prof_name = 'comp_prof'
    ssp_name = 'new_ssp'

    gen_args, _ = setup_for_ssp(tmp_trestle_dir, prof_name, ssp_name)
    test_utils.gen_and_assemble_first_ssp(prof_name, ssp_name, gen_args, monkeypatch)

    new_ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)

    original_href = new_ssp.import_profile.href
    # sets href for given profile to empty to test if no given profile has been given to an ssp
    new_ssp.import_profile.href = ''
    ModelUtils.save_top_level_model(new_ssp, tmp_trestle_dir, ssp_name, FileContentType.JSON)

    assert not validator.model_is_valid(new_ssp, True, tmp_trestle_dir)

    validate_command = f'trestle validate -t system-security-plan -n {ssp_name}'
    test_utils.execute_command_and_assert(validate_command, 4, monkeypatch)

    new_ssp.import_profile.href = original_href
    ModelUtils.save_top_level_model(new_ssp, tmp_trestle_dir, ssp_name, FileContentType.JSON)
