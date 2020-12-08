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
"""Tests for trestle import command."""
import argparse
import json
import pathlib
import sys
import tempfile
from unittest.mock import patch

from tests import test_utils

import trestle.core.commands.import_ as importcmd
import trestle.core.err as err
from trestle.cli import Trestle


def test_import_cmd(tmp_trestle_dir: pathlib.Path) -> None:
    """Happy path test at the cli level."""
    # 1. Input file, profile:
    profile_file = tempfile.NamedTemporaryFile(suffix='.json')
    sample_data = {
        'profile': {
            'uuid': '0611c5c3-436b-4506-9618-81fe7685a1c1',
            'metadata': {
                'title': 'Generic profile created by trestle.',
                'last-modified': '2020-12-07T06:18:11.311+00:00',
                'version': '0.0.0',
                'oscal-version': 'v1.0.0-milestone3'
            },
            'imports': [{
                'href': 'REPLACE_ME'
            }]
        }
    }
    profile_file.write(json.dumps(sample_data).encode('utf8'))
    # This seek is necessary to flush to file.
    profile_file.seek(0)
    # 2. Input file, target:
    target_definition_file = tempfile.NamedTemporaryFile(suffix='.json')
    sample_data = {
        'target-definition': {
            'metadata': {
                'title': 'Generic target-definition created by trestle.',
                'last-modified': '2020-12-07T06:18:07.435+00:00',
                'version': '0.0.0',
                'oscal-version': 'v1.0.0-milestone3'
            }
        }
    }
    target_definition_file.write(json.dumps(sample_data).encode('utf8'))
    target_definition_file.seek(0)
    # Test 1
    test_args = f'trestle import -f {str(profile_file.name)} -o imported'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 0
    # Test 2
    test_args = f'trestle import -f {str(target_definition_file.name)} -o imported'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 0


def test_import_run(tmp_trestle_dir: pathlib.Path) -> None:
    """Test successful _run() on valid and invalid."""
    catalog_file = tempfile.NamedTemporaryFile(suffix='.json')
    sample_data = {
        'catalog': {
            'uuid': 'ad0d0a7c-9634-48d9-ba90-fd10bcaf45b8',
            'metadata': {
                'title': 'Generic catalog created by trestle.',
                'last-modified': '2020-12-07T06:18:18.430+00:00',
                'version': '0.0.0',
                'oscal-version': 'v1.0.0-milestone3'
            }
        }
    }
    catalog_file.write(json.dumps(sample_data).encode('utf8'))
    catalog_file.seek(0)
    i = importcmd.ImportCmd()
    args = argparse.Namespace(file=catalog_file.name, output='imported', verbose=True)
    rc = i._run(args)
    assert rc == 0
    # A second import going to the same output as above should fail due to output file clash
    args = argparse.Namespace(file=catalog_file.name, output='imported', verbose=True)
    rc = i._run(args)
    assert rc == 1


def test_import_non_top_level_element(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for expected fail to import non-top level element, e.g., groups."""
    # Input file, catalog:
    groups_file = tempfile.NamedTemporaryFile(suffix='.json')
    sample_data = {'groups': [{'id': 'ac', 'class': 'family', 'title': 'Access Control'}]}
    groups_file.write(json.dumps(sample_data).encode('utf8'))
    groups_file.seek(0)
    args = argparse.Namespace(file=groups_file.name, output='imported', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1


def test_import_missing_input_file(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for missing input file."""
    # Test
    args = argparse.Namespace(file='random_named_file.json', output='catalog', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1


def test_import_bad_working_directory(tmp_dir: pathlib.Path) -> None:
    """Test for working directory that is not a trestle initialized directory."""
    # Input file, catalog:
    catalog_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH.absolute(), 'minimal_catalog.json')
    args = argparse.Namespace(file=str(catalog_file_path), output='catalog', verbose=True)
    i = importcmd.ImportCmd()
    with patch('trestle.utils.fs.get_trestle_project_root') as get_trestle_project_root_mock:
        get_trestle_project_root_mock.return_value = None
        rc = i._run(args)
        assert rc == 1


def test_import_from_inside_trestle_project_is_bad(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for attempting import from a trestle project directory."""
    sample_file = open('infile.json', 'w+')
    sample_file.write('{}')
    sample_file.close()
    args = argparse.Namespace(file='infile.json', output='catalog', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1


def test_import_bad_input_extension(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for bad input extension."""
    # Some input file with bad extension.
    temp_file = tempfile.NamedTemporaryFile(suffix='.txt')
    args = argparse.Namespace(file=temp_file.name, output='catalog', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1


def test_import_load_file_failure(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model failures throw errors and exit badly."""
    # Input file, bad json:
    json_file = tempfile.NamedTemporaryFile(suffix='.json')
    sample_data = '"star": {'
    json_file.write(sample_data.encode('utf8'))
    json_file.seek(0)
    with patch('trestle.utils.fs.load_file') as load_file_mock:
        load_file_mock.side_effect = err.TrestleError('stuff')
        args = argparse.Namespace(file=json_file.name, output='imported', verbose=True)
        i = importcmd.ImportCmd()
        rc = i._run(args)
        assert rc == 1


def test_import_root_key_failure(tmp_trestle_dir: pathlib.Path) -> None:
    """Test root key is not found."""
    sample_file = tempfile.NamedTemporaryFile(suffix='.json')
    sample_data = {'id': '0000', 'title': 'nothing'}
    sample_file.write(json.dumps(sample_data).encode('utf8'))
    sample_file.seek(0)
    args = argparse.Namespace(file=sample_file.name, output='catalog', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 1


def test_import_failure_parse_file(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model failures throw errors and exit badly."""
    sample_file = tempfile.NamedTemporaryFile(suffix='.json')
    sample_data = {'id': '0000'}
    sample_file.write(json.dumps(sample_data).encode('utf8'))
    sample_file.seek(0)
    with patch('trestle.core.parser.parse_file') as parse_file_mock:
        parse_file_mock.side_effect = err.TrestleError('stuff')
        args = argparse.Namespace(file=sample_file.name, output='catalog', verbose=True)
        i = importcmd.ImportCmd()
        rc = i._run(args)
        assert rc == 1


def test_import_root_key_found(tmp_trestle_dir: pathlib.Path) -> None:
    """Test root key is found."""
    catalog_file = tempfile.NamedTemporaryFile(suffix='.json')
    sample_data = {
        'catalog': {
            'uuid': 'ad0d0a7c-9634-48d9-ba90-fd10bcaf45b8',
            'metadata': {
                'title': 'Generic catalog created by trestle.',
                'last-modified': '2020-12-07T06:18:18.430+00:00',
                'version': '0.0.0',
                'oscal-version': 'v1.0.0-milestone3'
            }
        }
    }
    catalog_file.write(json.dumps(sample_data).encode('utf8'))
    catalog_file.seek(0)
    args = argparse.Namespace(file=catalog_file.name, output='catalog', verbose=True)
    i = importcmd.ImportCmd()
    rc = i._run(args)
    assert rc == 0


def test_import_failure_simulate_plan(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model failures throw errors and exit badly."""
    catalog_file = tempfile.NamedTemporaryFile(suffix='.json')
    sample_data = {
        'catalog': {
            'uuid': 'ad0d0a7c-9634-48d9-ba90-fd10bcaf45b8',
            'metadata': {
                'title': 'Generic catalog created by trestle.',
                'last-modified': '2020-12-07T06:18:18.430+00:00',
                'version': '0.0.0',
                'oscal-version': 'v1.0.0-milestone3'
            }
        }
    }
    catalog_file.write(json.dumps(sample_data).encode('utf8'))
    catalog_file.seek(0)
    with patch('trestle.core.models.plans.Plan.simulate') as simulate_plan_mock:
        simulate_plan_mock.side_effect = err.TrestleError('stuff')
        args = argparse.Namespace(file=catalog_file.name, output='imported', verbose=True)
        i = importcmd.ImportCmd()
        rc = i._run(args)
        assert rc == 1


def test_import_failure_execute_plan(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model failures throw errors and exit badly."""
    catalog_file = tempfile.NamedTemporaryFile(suffix='.json')
    sample_data = {
        'catalog': {
            'uuid': 'ad0d0a7c-9634-48d9-ba90-fd10bcaf45b8',
            'metadata': {
                'title': 'Generic catalog created by trestle.',
                'last-modified': '2020-12-07T06:18:18.430+00:00',
                'version': '0.0.0',
                'oscal-version': 'v1.0.0-milestone3'
            }
        }
    }
    catalog_file.write(json.dumps(sample_data).encode('utf8'))
    catalog_file.seek(0)
    with patch('trestle.core.models.plans.Plan.simulate'):
        with patch('trestle.core.models.plans.Plan.execute') as execute_plan_mock:
            execute_plan_mock.side_effect = err.TrestleError('stuff')
            args = argparse.Namespace(file=catalog_file.name, output='imported', verbose=True)
            i = importcmd.ImportCmd()
            rc = i._run(args)
            assert rc == 1
