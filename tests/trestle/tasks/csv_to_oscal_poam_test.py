# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2024 IBM Corp. All rights reserved.
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
"""Tests for csv_to_oscal_poam task."""

import configparser
import datetime
import pathlib
import uuid

from trestle.tasks.base_task import TaskOutcome
from trestle.tasks.csv_to_oscal_poam import (
    PoamBuilder,
    PoamValidator,
    PoamCsvHelper,
    UUIDManager,
    CsvToOscalPoam,
)


def _get_config_section(tmp_path: pathlib.Path, config_filename: str) -> configparser.SectionProxy:
    """
    Get config section for test.

    Args:
        tmp_path: Pytest tmp_path fixture
        config_filename: Name of config file in test data

    Returns:
        Config section proxy
    """
    config_path = pathlib.Path('tests/data/tasks/csv-to-oscal-poam') / config_filename
    config = configparser.ConfigParser()
    config.read(str(config_path))

    section = config['task.csv-to-oscal-poam']
    section['output-dir'] = str(tmp_path)

    return section


# UUIDManager Tests


def test_uuid_manager_deterministic():
    """Test that UUIDManager generates deterministic UUIDs."""
    poam_id = 'P001'

    # Generate UUIDs twice
    uuid1 = UUIDManager.poam_item_uuid(poam_id)
    uuid2 = UUIDManager.poam_item_uuid(poam_id)

    # Should be identical
    assert uuid1 == uuid2
    assert isinstance(uuid.UUID(uuid1), uuid.UUID)


def test_uuid_manager_different_ids():
    """Test that different POAM IDs generate different UUIDs."""
    uuid1 = UUIDManager.poam_item_uuid('P001')
    uuid2 = UUIDManager.poam_item_uuid('P002')

    assert uuid1 != uuid2


def test_uuid_manager_all_types():
    """Test UUID generation for all object types."""
    poam_id = 'P001'

    poam_item_uuid = UUIDManager.poam_item_uuid(poam_id)
    observation_uuid = UUIDManager.observation_uuid(poam_id)
    risk_uuid = UUIDManager.risk_uuid(poam_id)
    task_uuid = UUIDManager.task_uuid(poam_id, 0)
    actor_uuid = UUIDManager.actor_uuid('ACAS')

    # All should be different
    uuids = [poam_item_uuid, observation_uuid, risk_uuid, task_uuid, actor_uuid]
    assert len(set(uuids)) == 5


# PoamValidator Tests


def test_validator_parse_controls_valid():
    """Test parsing valid control IDs."""
    validator = PoamValidator()

    result = validator.parse_controls('AC-1, AC-2, SC-7(5)')
    assert result == ['AC-1', 'AC-2', 'SC-7(5)']


def test_validator_parse_controls_mixed_case():
    """Test parsing controls with mixed case."""
    validator = PoamValidator()

    result = validator.parse_controls('ac-1, Sc-7(5)')
    assert result == ['AC-1', 'SC-7(5)']


def test_validator_parse_controls_invalid():
    """Test parsing invalid control format."""
    validator = PoamValidator()

    result = validator.parse_controls('AC-1, INVALID, SC-7(5)')
    assert result == ['AC-1', 'SC-7(5)']  # Invalid one is skipped


def test_validator_parse_controls_empty():
    """Test parsing empty control string."""
    validator = PoamValidator()

    result = validator.parse_controls('')
    assert result == []


def test_validator_validate_row_valid():
    """Test validation of valid row."""
    validator = PoamValidator()
    row_data = {
        'POAM ID': 'P001',
        'Weakness Name': 'Test Weakness',
        'Weakness Description': 'Test Description',
        'Controls': 'AC-1',
        'Original Risk Rating': 'High',
    }

    errors = validator.validate_row(6, row_data)
    assert errors == []


def test_validator_validate_row_missing_poam_id():
    """Test validation with missing POAM ID."""
    validator = PoamValidator()
    row_data = {
        'POAM ID': '',
        'Weakness Name': 'Test Weakness',
        'Weakness Description': 'Test Description',
        'Controls': 'AC-1',
    }

    errors = validator.validate_row(6, row_data)
    assert len(errors) == 1
    assert 'POAM ID' in errors[0]


def test_validator_validate_row_missing_required_fields():
    """Test validation with all required fields missing."""
    validator = PoamValidator()
    row_data = {}

    errors = validator.validate_row(6, row_data)
    assert len(errors) == 4  # POAM ID, Weakness Name, Weakness Description, Controls


def test_validator_invalid_risk_rating():
    """Test validation with invalid risk rating."""
    validator = PoamValidator()
    row_data = {
        'POAM ID': 'P001',
        'Weakness Name': 'Test',
        'Weakness Description': 'Test',
        'Controls': 'AC-1',
        'Original Risk Rating': 'Invalid',
    }

    errors = validator.validate_row(6, row_data)
    assert len(errors) == 1
    assert 'Invalid Original Risk Rating' in errors[0]


# PoamCsvHelper Tests


def test_csv_helper_column_constants():
    """Test that all column constants are defined."""
    helper = PoamCsvHelper()

    assert helper.POAM_ID == 'POAM ID'
    assert helper.CONTROLS == 'Controls'
    assert helper.WEAKNESS_NAME == 'Weakness Name'
    assert helper.ORIGINAL_RISK_RATING == 'Original Risk Rating'


def test_csv_helper_parse_date_datetime():
    """Test parsing datetime object."""
    helper = PoamCsvHelper()
    dt = datetime.datetime(2024, 1, 15, 10, 30)

    result = helper.parse_date(dt)
    assert result is not None
    assert result.tzinfo is not None  # Should have timezone


def test_csv_helper_parse_date_string():
    """Test parsing ISO date string."""
    helper = PoamCsvHelper()

    result = helper.parse_date('2024-01-15T10:30:00Z')
    assert result is not None
    assert result.year == 2024
    assert result.month == 1
    assert result.day == 15


def test_csv_helper_parse_date_invalid():
    """Test parsing invalid date."""
    helper = PoamCsvHelper()

    result = helper.parse_date('invalid date')
    assert result is None


def test_csv_helper_parse_date_none():
    """Test parsing None date."""
    helper = PoamCsvHelper()

    result = helper.parse_date(None)
    assert result is None


def test_csv_helper_parse_milestones_single():
    """Test parsing single milestone."""
    helper = PoamCsvHelper()
    text = 'Milestone 1: Complete analysis by 2024-01-15'

    result = helper.parse_milestones(text)
    assert len(result) == 1
    assert result[0]['title'] == 'Complete analysis'
    assert result[0]['timing'] == '2024-01-15'


def test_csv_helper_parse_milestones_multiple():
    """Test parsing multiple milestones."""
    helper = PoamCsvHelper()
    text = 'Milestone 1: Complete analysis by 2024-01-15\nMilestone 2: Deploy fix by 2024-02-01'

    result = helper.parse_milestones(text)
    assert len(result) == 2
    assert result[0]['title'] == 'Complete analysis'
    assert result[1]['title'] == 'Deploy fix'


def test_csv_helper_parse_milestones_no_date():
    """Test parsing milestones without dates."""
    helper = PoamCsvHelper()
    text = 'Milestone 1: Complete analysis\nMilestone 2: Deploy fix'

    result = helper.parse_milestones(text)
    assert len(result) == 2
    assert 'timing' not in result[0] or result[0].get('timing') is None


def test_csv_helper_parse_milestones_empty():
    """Test parsing empty milestone string."""
    helper = PoamCsvHelper()

    result = helper.parse_milestones('')
    assert result == []


# PoamBuilder Tests


def test_builder_create_poam_item():
    """Test creating PoamItem."""
    validator = PoamValidator()
    builder = PoamBuilder('2024-01-15T10:00:00+00:00', validator)

    row_data = {
        'Weakness Name': 'Test Weakness',
        'Weakness Description': 'Test Description',
        'Controls': 'AC-1, AC-2',
        'Comments': 'Test comments',
    }

    item = builder.create_poam_item('P001', row_data)

    assert item.title == 'Test Weakness'
    assert item.description == 'Test Description'
    assert item.remarks == 'Test comments'
    assert item.props is not None
    assert len(item.props) == 3  # poam-id + 2 control-ids


def test_builder_create_observation():
    """Test creating Observation."""
    validator = PoamValidator()
    builder = PoamBuilder('2024-01-15T10:00:00+00:00', validator)
    helper = PoamCsvHelper()

    row_data = {
        'Weakness Name': 'Test Weakness',
        'Weakness Detector Source': 'ACAS',
        'Weakness Source Identifier': 'CVE-2024-1234',
        'Asset Identifier': 'server-01',
        'Original Detection Date': datetime.datetime(2024, 1, 10),
    }

    obs = builder.create_observation('P001', row_data, helper)

    assert obs.uuid is not None
    assert 'Test Weakness' in obs.description
    assert obs.methods == ['TEST']
    assert obs.collected is not None


def test_builder_create_risk():
    """Test creating Risk."""
    validator = PoamValidator()
    builder = PoamBuilder('2024-01-15T10:00:00+00:00', validator)
    helper = PoamCsvHelper()

    row_data = {
        'Weakness Name': 'Test Weakness',
        'Weakness Description': 'Test Description',
        'Overall Remediation Plan': 'Test remediation',
        'Original Risk Rating': 'High',
        'Adjusted Risk Rating': 'Moderate',
        'Risk Adjustment': 'Yes',
        'False Positive': 'No',
        'Scheduled Completion Date': datetime.datetime(2024, 6, 1),
    }

    risk = builder.create_risk('P001', row_data, helper)

    assert risk.title == 'Test Weakness'
    assert risk.description == 'Test Description'
    assert risk.statement == 'Test remediation'
    assert risk.status.__root__.__root__ == 'open'
    assert risk.props is not None
    assert risk.deadline is not None


def test_builder_link_objects():
    """Test linking POAM objects."""
    validator = PoamValidator()
    builder = PoamBuilder('2024-01-15T10:00:00+00:00', validator)
    helper = PoamCsvHelper()

    row_data = {
        'Weakness Name': 'Test',
        'Weakness Description': 'Test',
        'Overall Remediation Plan': 'Test',
        'Controls': 'AC-1',
    }

    poam_item = builder.create_poam_item('P001', row_data)
    observation = builder.create_observation('P001', row_data, helper)
    risk = builder.create_risk('P001', row_data, helper)

    builder.link_objects(poam_item, observation, risk)

    assert poam_item.related_observations is not None
    assert len(poam_item.related_observations) == 1
    assert poam_item.related_risks is not None
    assert len(poam_item.related_risks) == 1
    assert risk.related_observations is not None


# CsvToOscalPoam Task Tests


def test_print_info():
    """Test print_info method."""
    task = CsvToOscalPoam(None)
    task.print_info()  # Should not raise


def test_simulate():
    """Test simulate method."""
    task = CsvToOscalPoam(None)
    result = task.simulate()
    assert result == TaskOutcome('simulated-success')


def test_configure_missing_config():
    """Test configure with missing config."""
    task = CsvToOscalPoam(None)
    result = task.configure()
    assert result is False


def test_configure_missing_xlsx_file(tmp_path: pathlib.Path):
    """Test configure with missing csv-file parameter."""
    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-poam')
    config['task.csv-to-oscal-poam']['output-dir'] = str(tmp_path)
    config['task.csv-to-oscal-poam']['title'] = 'Test'
    config['task.csv-to-oscal-poam']['version'] = '1.0'

    task = CsvToOscalPoam(config['task.csv-to-oscal-poam'])
    result = task.configure()
    assert result is False


def test_configure_missing_output_dir(tmp_path: pathlib.Path):
    """Test configure with missing output-dir parameter."""
    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-poam')
    config['task.csv-to-oscal-poam']['csv-file'] = 'test.csv'
    config['task.csv-to-oscal-poam']['title'] = 'Test'
    config['task.csv-to-oscal-poam']['version'] = '1.0'

    task = CsvToOscalPoam(config['task.csv-to-oscal-poam'])
    result = task.configure()
    assert result is False


def test_configure_missing_title(tmp_path: pathlib.Path):
    """Test configure with missing title parameter."""
    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-poam')
    config['task.csv-to-oscal-poam']['csv-file'] = 'test.csv'
    config['task.csv-to-oscal-poam']['output-dir'] = str(tmp_path)
    config['task.csv-to-oscal-poam']['version'] = '1.0'

    task = CsvToOscalPoam(config['task.csv-to-oscal-poam'])
    result = task.configure()
    assert result is False


def test_configure_missing_version(tmp_path: pathlib.Path):
    """Test configure with missing version parameter."""
    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-poam')
    config['task.csv-to-oscal-poam']['csv-file'] = 'test.csv'
    config['task.csv-to-oscal-poam']['output-dir'] = str(tmp_path)
    config['task.csv-to-oscal-poam']['title'] = 'Test'

    task = CsvToOscalPoam(config['task.csv-to-oscal-poam'])
    result = task.configure()
    assert result is False


def test_configure_valid(tmp_path: pathlib.Path):
    """Test configure with all required parameters."""
    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-poam')
    config['task.csv-to-oscal-poam']['csv-file'] = 'test.csv'
    config['task.csv-to-oscal-poam']['output-dir'] = str(tmp_path)
    config['task.csv-to-oscal-poam']['title'] = 'Test POAM'
    config['task.csv-to-oscal-poam']['version'] = '1.0'

    task = CsvToOscalPoam(config['task.csv-to-oscal-poam'])
    result = task.configure()
    assert result is True
    assert task._csv_file == 'test.csv'
    assert task._title == 'Test POAM'
    assert task._version == '1.0'


def test_configure_optional_parameters(tmp_path: pathlib.Path):
    """Test configure with optional parameters."""
    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-poam')
    config['task.csv-to-oscal-poam']['csv-file'] = 'test.csv'
    config['task.csv-to-oscal-poam']['output-dir'] = str(tmp_path)
    config['task.csv-to-oscal-poam']['title'] = 'Test'
    config['task.csv-to-oscal-poam']['version'] = '1.0'
    config['task.csv-to-oscal-poam']['system-id'] = 'sys-123'
    config['task.csv-to-oscal-poam']['output-overwrite'] = 'false'
    config['task.csv-to-oscal-poam']['validate-required-fields'] = 'on'
    config['task.csv-to-oscal-poam']['quiet'] = 'true'

    task = CsvToOscalPoam(config['task.csv-to-oscal-poam'])
    result = task.configure()
    assert result is True
    assert task._system_id == 'sys-123'
    assert task._overwrite is False
    assert task._validate_mode == 'on'
    assert task._quiet is True


def test_set_timestamp():
    """Test set_timestamp method."""
    task = CsvToOscalPoam(None)
    test_timestamp = '2024-01-15T10:00:00+00:00'
    task.set_timestamp(test_timestamp)
    assert task._timestamp == test_timestamp


# Note: Integration tests would require actual CSV test fixtures
# which have been created in tests/data/tasks/csv-to-oscal-poam/
