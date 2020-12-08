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
import json
import pathlib
import sys
import tempfile
from unittest.mock import patch

from tests import test_utils

import trestle.core.err as err
from trestle.cli import Trestle


def test_import_cmd(tmp_trestle_dir: pathlib.Path) -> None:
    """Happy path test at the cli level."""
    # Input file, catalog:
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
    # Input file, profile:
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
    profile_file.seek(0)
    # Input file, target:
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
    test_args = f'trestle import -f {str(catalog_file.name)} -o imported'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 0
    # Import going to the same output should fail due to output file clash
    test_args = f'trestle import -f {str(catalog_file.name)} -o imported'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 1
    # Test
    test_args = f'trestle import -f {str(profile_file.name)} -o imported'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 0
    # Test
    test_args = f'trestle import -f {str(target_definition_file.name)} -o imported'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 0


def test_import_non_top_level_element(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for expected fail to import non-top level element, e.g., groups."""
    # Input file, catalog:
    groups_file = tempfile.NamedTemporaryFile(suffix='.json')
    sample_data = {'groups': [{'id': 'ac', 'class': 'family', 'title': 'Access Control'}]}
    groups_file.write(json.dumps(sample_data).encode('utf8'))
    groups_file.seek(0)
    test_args = f'trestle import -f {str(groups_file.name)} -o imported'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 1


def test_import_missing_input_file(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for missing input file."""
    # Test
    test_args = 'trestle import -f random_named_file.json -o catalog'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 1


def test_import_bad_working_directory(tmp_dir: pathlib.Path) -> None:
    """Test for working directory that is not a trestle initialized directory."""
    # DONE
    # Input file, catalog:
    catalog_file_path = pathlib.Path.joinpath(test_utils.JSON_TEST_DATA_PATH.absolute(), 'minimal_catalog.json')
    test_args = f'trestle import -f {str(catalog_file_path)} -o catalog'.split()
    with patch('trestle.utils.fs.get_trestle_project_root') as get_trestle_project_root_mock:
        get_trestle_project_root_mock.return_value = None
        with patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 1


def test_import_from_inside_trestle_project_is_bad(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for attempting import from a trestle project directory."""
    # DONE
    sample_file = open('infile.json', 'w+')
    sample_file.write('{}')
    sample_file.close()
    test_args = 'trestle import -f infile.json -o catalog'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 1


def test_import_bad_input_extension(tmp_trestle_dir: pathlib.Path) -> None:
    """Test for bad input extension."""
    # DONE
    # Some input file with bad extension.
    temp_file = tempfile.NamedTemporaryFile(suffix='.txt')
    test_args = f'trestle import -f {temp_file.name} -o catalog'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 1


def test_import_load_file_failure(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model failures throw errors and exit badly."""
    # DONE
    # Input file, bad json:
    json_file = tempfile.NamedTemporaryFile(suffix='.json')
    sample_data = '"star": {'
    json_file.write(sample_data.encode('utf8'))
    json_file.seek(0)
    test_args = f'trestle import -f {str(json_file.name)} -o imported'.split()
    with patch('trestle.utils.fs.load_file') as load_file_mock:
        load_file_mock.side_effect = err.TrestleError('stuff')
        with patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 1


def test_import_root_key_failure(tmp_trestle_dir: pathlib.Path) -> None:
    """Test root key is not found."""
    # DONE
    sample_file = tempfile.NamedTemporaryFile(suffix='.json')
    # Using dict to json to bytes, to keep flake8 quiet.
    sample_data = {'id': '0000', 'title': 'nothing'}
    sample_file.write(json.dumps(sample_data).encode('utf8'))
    # This seek is necessary to flush to file.
    sample_file.seek(0)
    test_args = f'trestle import -f {sample_file.name} -o catalog'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 1


def test_import_failure_parse_file(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model failures throw errors and exit badly."""
    # DONE
    sample_file = tempfile.NamedTemporaryFile(suffix='.json')
    # Using dict to json to bytes, to keep flake8 quiet.
    sample_data = {'id': '0000'}
    sample_file.write(json.dumps(sample_data).encode('utf8'))
    # This seek is necessary to flush to file.
    sample_file.seek(0)
    test_args = f'trestle import -f {sample_file.name} -o catalog'.split()
    with patch('trestle.core.parser.parse_file') as parse_file_mock:
        parse_file_mock.side_effect = err.TrestleError('stuff')
        with patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 1


def test_import_root_key_found(tmp_trestle_dir: pathlib.Path) -> None:
    """Test root key is found."""
    # DONE
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
    test_args = f'trestle import -f {catalog_file.name} -o catalog'.split()
    with patch.object(sys, 'argv', test_args):
        rc = Trestle().run()
        assert rc == 0


def test_import_failure_simulate_plan(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model failures throw errors and exit badly."""
    # DONE
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
    test_args = f'trestle import -f {str(catalog_file.name)} -o imported'.split()
    with patch('trestle.core.models.plans.Plan.simulate') as simulate_plan_mock:
        simulate_plan_mock.side_effect = err.TrestleError('stuff')
        with patch.object(sys, 'argv', test_args):
            rc = Trestle().run()
            assert rc == 1


def test_import_failure_execute_plan(tmp_trestle_dir: pathlib.Path) -> None:
    """Test model failures throw errors and exit badly."""
    # DONE
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
    test_args = f'trestle import -f {str(catalog_file.name)} -o imported'.split()
    with patch('trestle.core.models.plans.Plan.simulate'):
        with patch('trestle.core.models.plans.Plan.execute') as execute_plan_mock:
            execute_plan_mock.side_effect = err.TrestleError('stuff')
            with patch.object(sys, 'argv', test_args):
                rc = Trestle().run()
                assert rc == 1
