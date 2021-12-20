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
"""Tests for trestle import command."""
import argparse
import json
import os
import pathlib
import random
import string
import sys
import tempfile
from json.decoder import JSONDecodeError

from _pytest.monkeypatch import MonkeyPatch

import pytest

from tests import test_utils

import trestle.core.commands.import_ as importcmd
import trestle.core.const as const
import trestle.core.err as err
import trestle.oscal
from trestle.cli import Trestle
from trestle.core import generators
from trestle.core import parser
from trestle.core.commands import create
from trestle.core.commands.validate import ValidateCmd
from trestle.core.models.plans import Plan
from trestle.oscal.catalog import Catalog, Group
from trestle.oscal.profile import Modify, Profile, SetParameter
from trestle.utils import fs


def test_import_cmd(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Happy path test at the cli level."""
    # 1. Input file, profile:
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    profile_file = f'{tmp_trestle_dir.parent}/{rand_str}.json'
    profile_data = generators.generate_sample_model(trestle.oscal.profile.Profile)
    profile_data.oscal_write(pathlib.Path(profile_file))
    # 2. Input file, target:
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    catalog_file = f'{tmp_trestle_dir.parent}/{rand_str}.json'
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(pathlib.Path(catalog_file))
    # Test 1
    test_args = f'trestle import -f {profile_file} -o imported'.split()
    monkeypatch.setattr(sys, 'argv', test_args)
    rc = Trestle().run()
    assert rc == 0
    # Test 2
    test_args = f'trestle import -f {catalog_file} -o imported'.split()
    monkeypatch.setattr(sys, 'argv', test_args)
    rc = Trestle().run()
    assert rc == 0


def test_import_profile_with_optional_added(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Create profile, add modify to it, and import."""
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    profile_file = f'{tmp_trestle_dir.parent}/{rand_str}.json'
    # create generic profile
    profile_data = generators.generate_sample_model(trestle.oscal.profile.Profile)
    # create special parameter and add it to profile
    set_parameter = SetParameter(param_id='my_param', depends_on='my_depends')
    modify = Modify(set_parameters=[set_parameter])
    profile_data.modify = modify
    # write it to place outside trestle directory
    profile_data.oscal_write(pathlib.Path(profile_file))
    # now do actual import into trestle directory with name 'imported'
    test_args = f'trestle import -f {profile_file} -o imported'.split()
    monkeypatch.setattr(sys, 'argv', test_args)
    rc = Trestle().run()
    assert rc == 0
    # then do a direct read of it and confirm our parameter is there
    profile_path = tmp_trestle_dir / 'profiles/imported/profile.json'
    profile: Profile = Profile.oscal_read(profile_path)
    params = profile.modify.set_parameters
    assert params
    assert len(params) == 1
    assert params[0].param_id == 'my_param'
    assert params[0].depends_on == 'my_depends'


@pytest.mark.parametrize('regen', [False, True])
def test_import_run(tmp_trestle_dir: pathlib.Path, regen: bool) -> None:
    """Test successful _run() on valid input."""
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    catalog_file = f'{tmp_trestle_dir.parent}/{rand_str}.json'
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(pathlib.Path(catalog_file))
    i = importcmd.ImportCmd()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=catalog_file, output='imported', verbose=True, regenerate=regen
    )
    rc = i._run(args)
    assert rc == 0


def test_import_run_rollback(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test successful _run() on invalid input with good or failed rollback."""

    def validate_import_mock(*args, **kwargs):
        raise err.TrestleError('validate run error')

    def rollback_mock(*args, **kwargs):
        return [None, err.TrestleError('rollback error')]

    dup_cat = {
        'catalog': {
            'uuid': '525f94af-8007-4376-8069-aa40179e0f6e',
            'metadata': {
                'title': 'Generic catalog created by trestle.',
                'last-modified': '2020-12-11T02:04:51.053+00:00',
                'version': '0.0.0',
                'oscal-version': trestle.oscal.OSCAL_VERSION
            },
            'back-matter': {
                'resources': [
                    {
                        'uuid': 'b1101385-9e36-44a3-ba03-98b6ebe0a367'
                    }, {
                        'uuid': 'b1101385-9e36-44a3-ba03-98b6ebe0a367'
                    }
                ]
            }
        }
    }
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    dup_file_name = f'{tmp_trestle_dir.parent}/dup-{rand_str}.json'
    dup_file = pathlib.Path(dup_file_name).open('w+', encoding=const.FILE_ENCODING)
    dup_file.write(json.dumps(dup_cat, ensure_ascii=False))
    dup_file.close()
    j = importcmd.ImportCmd()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=dup_file_name, output=f'dup-{rand_str}', verbose=True, regenerate=False
    )
    # 1. Validation rejects above import, which results in non-zero exit code for import.
    rc = j._run(args)
    assert rc > 0
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    # 2. ValidateCmd raises run (mocked), so import returns non-zero exit code.
    j = importcmd.ImportCmd()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=dup_file_name, output=f'dup-{rand_str}', verbose=True, regenerate=False
    )
    monkeypatch.setattr(ValidateCmd, '_run', validate_import_mock)
    rc = j._run(args)
    assert rc > 0
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    # 3. Rollback raises exception, so import returns non-zero exit code:
    j = importcmd.ImportCmd()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=dup_file_name, output=f'dup-{rand_str}', verbose=True, regenerate=False
    )
    monkeypatch.setattr(Plan, 'rollback', rollback_mock)
    rc = j._run(args)
    assert rc > 0


def test_import_clash_on_output(tmp_trestle_dir: pathlib.Path) -> None:
    """Test an attempt to import into an existing trestle file."""
    # 1. Create a sample catalog,
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        output='my-catalog',
        extension='json',
        verbose=True,
        include_optional_fields=False
    )
    create.CreateCmd.create_object('catalog', Catalog, args)
    # 2. Create a valid oscal object in tmp_trestle_dir.parent,
    sample_data = generators.generate_sample_model(Catalog)
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    sample_data.oscal_write(pathlib.Path(f'{tmp_trestle_dir.parent}/{rand_str}.json'))
    # 3. then attempt to import that out to the previously created catalog, forcing the clash:
    i = importcmd.ImportCmd()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        file=f'{tmp_trestle_dir.parent}/{rand_str}.json',
        output='my-catalog',
        verbose=True
    )
    rc = i._run(args)
    assert rc == 1


def test_import_non_top_level_element(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for expected fail to import non-top level element, e.g., groups."""
    # Input file, catalog:
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    groups_file = f'{tmp_trestle_dir.parent}/{rand_str}.json'
    groups_data = generators.generate_sample_model(Group)
    groups_data.oscal_write(pathlib.Path(groups_file))
    args = argparse.Namespace(trestle_root=tmp_trestle_dir, file=groups_file, output='imported', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1


def test_import_missing_input_file(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for missing input file."""
    # Test
    args = argparse.Namespace(
        file='/dummy_path/random_named_file.json', output='catalog', verbose=True, trestle_root=tmp_trestle_dir
    )
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1


def test_import_bad_working_directory(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test for working directory that is not a trestle initialized directory."""

    def get_trestle_project_root_mock(*args, **kwargs):
        return None

    # Input file, catalog:
    catalog_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH.resolve(), 'minimal_catalog.json')
    args = argparse.Namespace(trestle_root=tmp_path, file=str(catalog_file_path), output='catalog', verbose=True)
    i = importcmd.ImportCmd()
    monkeypatch.setattr(fs, 'get_trestle_project_root', get_trestle_project_root_mock)
    rc = i._run(args)
    assert rc == 5


def test_import_from_inside_trestle_project_is_bad(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for attempting import from a trestle project directory."""
    sample_file = open('infile.json', 'w+', encoding=const.FILE_ENCODING)
    sample_file.write('{}')
    sample_file.close()
    args = argparse.Namespace(trestle_root=tmp_trestle_dir, file='infile.json', output='catalog', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1


def test_import_bad_input_extension(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for bad input extension."""
    # Some input file with bad extension.
    temp_file = tempfile.NamedTemporaryFile(suffix='.txt')
    args = argparse.Namespace(trestle_root=tmp_trestle_dir, file=temp_file.name, output='catalog', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1


def test_import_load_file_failure(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test model load failures."""

    def load_file_mock(*args, **kwargs):
        raise err.TrestleError('stuff')

    def load_file_permission_error_mock(*args, **kwargs):
        raise PermissionError

    def load_file_json_decode_error_mock(*args, **kwargs):
        raise JSONDecodeError(msg='Extra data:', doc=bad_file.name, pos=0)

    # Create a file with bad json
    sample_data = '"star": {'
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    bad_file = pathlib.Path(f'{tmp_trestle_dir.parent}/{rand_str}.json').open('w+', encoding=const.FILE_ENCODING)
    bad_file.write(sample_data)
    bad_file.close()
    monkeypatch.setattr(fs, 'load_file', load_file_mock)
    args = argparse.Namespace(trestle_root=tmp_trestle_dir, file=bad_file.name, output='imported', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1
    # Force PermissionError:
    monkeypatch.setattr(fs, 'load_file', load_file_permission_error_mock)
    args = argparse.Namespace(trestle_root=tmp_trestle_dir, file=bad_file.name, output='imported', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1
    # Force JSONDecodeError:
    monkeypatch.setattr(fs, 'load_file', load_file_json_decode_error_mock)
    args = argparse.Namespace(trestle_root=tmp_trestle_dir, file=bad_file.name, output='imported', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1
    # This is in case the same tmp_trestle_dir.parent is used, as across succeeding scopes of one pytest
    os.chmod(bad_file.name, 0o600)
    os.remove(bad_file.name)


def test_import_root_key_failure(tmp_trestle_dir: pathlib.Path) -> None:
    """Test root key is not found."""
    sample_data = {'id': '0000', 'title': 'nothing'}
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    sample_file = pathlib.Path(f'{tmp_trestle_dir.parent}/{rand_str}.json').open('w+', encoding=const.FILE_ENCODING)
    sample_file.write(json.dumps(sample_data, ensure_ascii=False))
    sample_file.close()
    args = argparse.Namespace(trestle_root=tmp_trestle_dir, file=sample_file.name, output='catalog', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1


def test_import_failure_parse_file(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test model failures throw errors and exit badly."""

    def parse_file_mock(*args, **kwargs):
        raise err.TrestleError('stuff')

    sample_data = {'id': '0000'}
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    sample_file = pathlib.Path(f'{tmp_trestle_dir.parent}/{rand_str}.json').open('w+', encoding=const.FILE_ENCODING)
    sample_file.write(json.dumps(sample_data, ensure_ascii=False))
    sample_file.close()
    monkeypatch.setattr(parser, 'parse_file', parse_file_mock)
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        file=f'{tmp_trestle_dir.parent}/{rand_str}.json',
        output='catalog',
        verbose=True,
        regenerate=False
    )
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1


def test_import_root_key_found(tmp_trestle_dir: pathlib.Path) -> None:
    """Test root key is found."""
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    catalog_file = f'{tmp_trestle_dir.parent}/{rand_str}.json'
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(pathlib.Path(catalog_file))
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=catalog_file, output='catalog', verbose=True, regenerate=False
    )
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 0


def test_import_failure_execute_plan(tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test model failures throw errors and exit badly."""

    def execute_plan_mock(*args, **kwargs):
        raise err.TrestleError('stuff')

    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(16))
    catalog_file = f'{tmp_trestle_dir.parent}/{rand_str}.json'
    catalog_data = generators.generate_sample_model(Catalog)
    catalog_data.oscal_write(pathlib.Path(catalog_file))
    monkeypatch.setattr(Plan, 'execute', execute_plan_mock)
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=catalog_file, output='imported', verbose=True, regenerate=False
    )
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1


def test_import_from_url(tmp_trestle_dir: pathlib.Path) -> None:
    """Test import via url."""
    uri = 'https://raw.githubusercontent.com/IBM/compliance-trestle/develop/tests/data/json/minimal_catalog.json'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=uri, output='my_catalog', verbose=True, regenerate=False
    )
    i = importcmd.ImportCmd()
    assert i._run(args) == 0
    imported_catalog = Catalog.oscal_read(tmp_trestle_dir / 'catalogs/my_catalog/catalog.json')

    test_catalog = test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json'
    catalog_data = Catalog.oscal_read(test_catalog)

    assert test_utils.models_are_equivalent(catalog_data, imported_catalog)


def test_import_from_nist(tmp_trestle_dir: pathlib.Path) -> None:
    """Test import via url from nist."""
    uri = 'https://raw.githubusercontent.com/usnistgov/oscal-content/master/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_HIGH-baseline_profile-min.json'  # noqa: E501
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=uri, output='my_catalog', verbose=True, regenerate=False
    )
    i = importcmd.ImportCmd()
    assert i._run(args) == 0


def test_import_load_profile(tmp_trestle_dir: pathlib.Path) -> None:
    """Test load of profile and contents."""
    external_prof_path = test_utils.JSON_TEST_DATA_PATH / 'test_profile_e.json'
    read_profile: Profile = Profile.oscal_read(external_prof_path)
    assert len(read_profile.modify.set_parameters[1].constraints) == 1

    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=str(external_prof_path), output='my_prof', verbose=True, regenerate=False
    )
    i = importcmd.ImportCmd()
    assert i._run(args) == 0

    loaded_profile, _ = fs.load_top_level_model(tmp_trestle_dir, 'my_prof', Profile)
    assert len(loaded_profile.modify.set_parameters[1].constraints) == 1


def test_import_wrong_oscal_version(tmp_trestle_dir: pathlib.Path) -> None:
    """Test import of the wrong OSCAL version."""
    catalog_path = test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog_bad_oscal_version.json'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=str(catalog_path), output='my_catalog', verbose=True, regenerate=False
    )
    i = importcmd.ImportCmd()
    assert i._run(args) == 1
