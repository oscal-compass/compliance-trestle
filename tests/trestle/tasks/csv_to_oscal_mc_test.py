# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2025 The OSCAL Compass Authors. All rights reserved.
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
"""csv-to-oscal-mc task tests."""

import configparser
import pathlib
import shutil

import pytest

from tests import test_utils
from tests.test_utils import set_cwd_unsafe

import trestle.tasks.csv_to_oscal_mc as csv_to_oscal_mc
from trestle.oscal.mapping import MappingCollection
from trestle.tasks.base_task import TaskOutcome

root_dir = test_utils.TEST_DIR / '../'


def _test_init(tmp_path: pathlib.Path):
    """Test init."""
    test_utils.ensure_trestle_config_dir(tmp_path)


def _get_config_section(tmp_path: pathlib.Path, fname: str) -> tuple:
    """Get config section."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(f'tests/data/trestle.ws/{fname}')
    config.read(config_path)
    section = config['task.csv-to-oscal-mc']
    section['output-dir'] = str(tmp_path)
    # Set csv-file to absolute path
    csv_file = section.get('csv-file', '')
    if csv_file:
        csv_path = pathlib.Path('tests/data/trestle.ws') / csv_file
        section['csv-file'] = str(csv_path)
    return (config, section)


def _get_config_section_init(tmp_path: pathlib.Path, fname: str) -> tuple:
    """Get config section."""
    _test_init(tmp_path)
    return _get_config_section(tmp_path, fname)


def _setup_test_catalogs(tmp_path: pathlib.Path) -> None:
    """Setup test catalogs."""
    # Copy PCI catalog
    src_pci = pathlib.Path('tests/data/trestle.ws/catalogs/PCI')
    dst_pci = tmp_path / 'catalogs' / 'PCI'
    dst_pci.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src_pci, dst_pci)

    # Copy FedRAMP catalog
    src_fedramp = pathlib.Path('tests/data/trestle.ws/catalogs/FedRAMP_rev5_HIGH')
    dst_fedramp = tmp_path / 'catalogs' / 'FedRAMP_rev5_HIGH'
    shutil.copytree(src_fedramp, dst_fedramp)


def _validate_pci_mapping(tmp_path: pathlib.Path) -> None:
    """Validate PCI mapping collection."""
    # Read mapping-collection
    fp = pathlib.Path(tmp_path) / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(fp)

    # Spot check metadata
    assert mc.metadata.title == 'Mapping collection for PCI to FedRAMP'
    assert mc.metadata.version == '1.0.0'

    # Check provenance
    assert mc.provenance is not None
    assert mc.provenance.method == 'manual'
    assert mc.provenance.matching_rationale == 'semantic'
    assert mc.provenance.status == 'complete'

    # Check mappings
    assert mc.mappings is not None
    if isinstance(mc.mappings, list):
        assert len(mc.mappings) > 0
        mapping = mc.mappings[0]
    else:
        mapping = mc.mappings

    # Check mapping structure
    assert mapping.source_resource is not None
    assert mapping.target_resource is not None
    assert mapping.maps is not None
    assert len(mapping.maps) > 0

    # Check first map entry
    map_entry = mapping.maps[0]
    assert map_entry.relationship is not None
    assert map_entry.sources is not None
    assert len(map_entry.sources) > 0
    assert map_entry.targets is not None

    # Check confidence score with percentage field
    if map_entry.confidence_score:
        assert hasattr(map_entry.confidence_score, 'percentage')
        assert map_entry.confidence_score.percentage is not None

    if map_entry.coverage:
        assert hasattr(map_entry.coverage, 'STRVALUE')
        assert map_entry.coverage.STRVALUE is not None


def _validate_soc2_mapping(tmp_path: pathlib.Path) -> None:
    """Validate SOC2 mapping collection."""
    # Read mapping-collection
    fp = pathlib.Path(tmp_path) / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(fp)

    # Spot check metadata
    assert mc.metadata.title == 'Mapping collection for SOC2 to FedRAMP'
    assert mc.metadata.version == '1.0.0'

    # Check provenance
    assert mc.provenance is not None
    assert mc.provenance.method == 'manual'
    assert mc.provenance.matching_rationale == 'semantic'
    assert mc.provenance.status == 'complete'

    # Check mappings
    assert mc.mappings is not None
    if isinstance(mc.mappings, list):
        assert len(mc.mappings) > 0
        mapping = mc.mappings[0]
    else:
        mapping = mc.mappings

    # Check mapping structure
    assert mapping.source_resource is not None
    assert mapping.target_resource is not None
    assert mapping.maps is not None
    assert len(mapping.maps) > 0

    # Check first map entry
    map_entry = mapping.maps[0]
    assert map_entry.relationship is not None
    assert map_entry.sources is not None
    assert len(map_entry.sources) > 0
    assert map_entry.targets is not None

    # Check confidence score with percentage field
    if map_entry.confidence_score:
        assert hasattr(map_entry.confidence_score, 'percentage')
        assert map_entry.confidence_score.percentage is not None

    if map_entry.coverage:
        assert hasattr(map_entry.coverage, 'STRVALUE')
        assert map_entry.coverage.STRVALUE is not None


@set_cwd_unsafe(root_dir)
def test_print_info(tmp_path: pathlib.Path) -> None:
    """Test print_info."""
    _, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.pci.config')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.print_info()
    assert retval is None


@set_cwd_unsafe(root_dir)
def test_simulate(tmp_path: pathlib.Path) -> None:
    """Test simulate."""
    _test_init(tmp_path)
    _setup_test_catalogs(tmp_path)
    _, section = _get_config_section(tmp_path, 'test-csv-to-oscal-mc.pci.config')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_execute_pci(tmp_path: pathlib.Path) -> None:
    """Test execute with PCI mapping."""
    # Run from trestle.ws where catalogs exist
    config = configparser.ConfigParser()
    config_path = pathlib.Path('test-csv-to-oscal-mc.pci.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-mc']
    section['output-dir'] = str(tmp_path)

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_pci_mapping(tmp_path)


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_execute_soc2(tmp_path: pathlib.Path) -> None:
    """Test execute with SOC2 mapping."""
    # Run from trestle.ws where catalogs exist
    config = configparser.ConfigParser()
    config_path = pathlib.Path('test-csv-to-oscal-mc.soc2.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-mc']
    section['output-dir'] = str(tmp_path)

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    _validate_soc2_mapping(tmp_path)


@set_cwd_unsafe(root_dir)
def test_config_missing(tmp_path: pathlib.Path) -> None:
    """Test config missing."""
    section = None
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


@set_cwd_unsafe(root_dir)
def test_config_missing_title(tmp_path: pathlib.Path) -> None:
    """Test config missing title."""
    _, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.pci.config')
    section.pop('title')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


@set_cwd_unsafe(root_dir)
def test_config_missing_version(tmp_path: pathlib.Path) -> None:
    """Test config missing version."""
    _, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.pci.config')
    section.pop('version')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


@set_cwd_unsafe(root_dir)
def test_config_missing_csv_file(tmp_path: pathlib.Path) -> None:
    """Test config missing csv-file."""
    _, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.pci.config')
    section.pop('csv-file')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


@set_cwd_unsafe(root_dir)
def test_config_missing_output_dir(tmp_path: pathlib.Path) -> None:
    """Test config missing output-dir."""
    _, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.pci.config')
    section.pop('output-dir')
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


@set_cwd_unsafe(root_dir)
def test_config_csv_file_not_found(tmp_path: pathlib.Path) -> None:
    """Test config with csv file that doesn't exist."""
    _, section = _get_config_section_init(tmp_path, 'test-csv-to-oscal-mc.pci.config')
    section['csv-file'] = 'nonexistent.csv'
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_output_overwrite_false(tmp_path: pathlib.Path) -> None:
    """Test output-overwrite=false with existing file."""
    # First create the output file
    config = configparser.ConfigParser()
    config_path = pathlib.Path('test-csv-to-oscal-mc.pci.config')
    config.read(config_path)
    section = config['task.csv-to-oscal-mc']
    section['output-dir'] = str(tmp_path)

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS

    # Now try again with overwrite=false
    section['output-overwrite'] = 'false'
    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


@set_cwd_unsafe(root_dir)
def test_parse_percentage(tmp_path: pathlib.Path) -> None:
    """Test percentage parsing."""
    # Create a minimal _McMgr instance to test the method
    mc_path = tmp_path / 'test.json'
    mgr = csv_to_oscal_mc._McMgr(mc_path, 'Test', '1.0.0')

    # Test valid percentages
    assert mgr._parse_percentage('50%') == 0.5
    assert mgr._parse_percentage('100%') == 1.0
    assert mgr._parse_percentage('0%') == 0.0
    assert mgr._parse_percentage('75.5%') == 0.755

    # Test decimal values
    assert mgr._parse_percentage('0.5') == 0.5
    assert mgr._parse_percentage('1.0') == 1.0
    assert mgr._parse_percentage('0') == 0.0

    # Test invalid values
    assert mgr._parse_percentage('invalid') is None
    assert mgr._parse_percentage('') is None
    assert mgr._parse_percentage('150%') is None  # Out of range
    assert mgr._parse_percentage('-10%') is None  # Negative
    assert mgr._parse_percentage('abc%') is None  # Non-numeric with %
    assert mgr._parse_percentage('1.2.3') is None  # Invalid decimal format


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_execute_with_user_columns(tmp_path: pathlib.Path) -> None:
    """Test execute with CSV containing user-defined columns."""
    # Create a CSV with extra user columns - use valid PCI control ID
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage,User_Column_1,User_Column_2
A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage,Custom field 1,Custom field 2
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.1,ac-1_smt,subset-of,90%,90%,custom_value_1,custom_value_2
"""
    csv_path = tmp_path / 'test_user_columns.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test with User Columns'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS

    # Verify user columns are in properties
    mc_file = tmp_path / 'output' / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(mc_file)
    if isinstance(mc.mappings, list):
        mapping = mc.mappings[0]
    else:
        mapping = mc.mappings

    # Check that properties exist with user columns
    if mapping.maps and len(mapping.maps) > 0:
        map_entry = mapping.maps[0]
        if map_entry.props:
            prop_names = [p.name for p in map_entry.props]
            assert 'User_Column_1' in prop_names or 'user_column_1' in prop_names


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_missing_required_columns(tmp_path: pathlib.Path) -> None:
    """Test CSV with missing required columns."""
    # Create CSV with missing Map_Target_ID_Ref_list column
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list
A reference to a resource,A reference to a resource,A list of source IDs
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.1
"""
    csv_path = tmp_path / 'test_missing_columns.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test Missing Columns'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_invalid_control_ids(tmp_path: pathlib.Path) -> None:
    """Test CSV with invalid source control IDs."""
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage
A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,invalid_control_id,ac-1_smt,subset-of,90%,90%
"""
    csv_path = tmp_path / 'test_invalid_controls.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test Invalid Controls'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    # Should fail because invalid_control_id doesn't exist in PCI catalog
    assert retval == TaskOutcome.FAILURE


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_invalid_target_control_ids(tmp_path: pathlib.Path) -> None:
    """Test CSV with invalid target control IDs."""
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage
A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.1,invalid_target_id,subset-of,90%,90%
"""
    csv_path = tmp_path / 'test_invalid_target.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test Invalid Target Controls'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    # Should fail because invalid_target_id doesn't exist in FedRAMP catalog
    assert retval == TaskOutcome.FAILURE


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_empty_user_column_value(tmp_path: pathlib.Path) -> None:
    """Test CSV with empty user column values."""
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage,User_Column_1,User_Column_2
A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage,Custom field 1,Custom field 2
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.1,ac-1_smt,subset-of,90%,90%,,empty_value
"""
    csv_path = tmp_path / 'test_empty_column.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test Empty User Column'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    # Should succeed - empty values are skipped
    assert retval == TaskOutcome.SUCCESS

    # Verify only non-empty user column is in properties
    mc_file = tmp_path / 'output' / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(mc_file)
    if isinstance(mc.mappings, list):
        mapping = mc.mappings[0]
    else:
        mapping = mc.mappings

    if mapping.maps and len(mapping.maps) > 0:
        map_entry = mapping.maps[0]
        if map_entry.props:
            prop_names = [p.name for p in map_entry.props]
            # User_Column_2 should be present, User_Column_1 should not (empty)
            assert 'User_Column_2' in prop_names or 'user_column_2' in prop_names


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_source_gap_summary(tmp_path: pathlib.Path) -> None:
    """Test CSV with unmapped source controls generates source-gap-summary."""
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage
A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.1,ac-1_smt,subset-of,90%,90%
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.2,,,
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.2.1,,,
"""
    csv_path = tmp_path / 'test_source_gap.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test Source Gap Summary'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS

    # Verify source-gap-summary is present in the first mapping
    mc_file = tmp_path / 'output' / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(mc_file)

    assert mc.mappings is not None
    if isinstance(mc.mappings, list):
        first_mapping = mc.mappings[0]
    else:
        first_mapping = mc.mappings

    assert first_mapping.source_gap_summary is not None
    assert first_mapping.source_gap_summary.unmapped_controls is not None

    # Check that unmapped controls list contains our unmapped source controls
    unmapped_list = first_mapping.source_gap_summary.unmapped_controls
    if isinstance(unmapped_list, list):
        assert len(unmapped_list) > 0
        # Get with-ids from first element
        with_ids = unmapped_list[0].with_ids
    else:
        with_ids = unmapped_list.with_ids

    assert with_ids is not None
    assert 'PCI-1.1.2' in with_ids
    assert 'PCI-1.2.1' in with_ids
    # PCI-1.1.1 should NOT be in unmapped (it has a target)
    assert 'PCI-1.1.1' not in with_ids


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_target_gap_summary(tmp_path: pathlib.Path) -> None:
    """Test CSV with unmapped target controls generates target-gap-summary."""
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage
A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.1,ac-1_smt,subset-of,90%,90%
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,,ac-2_smt,,
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,,ac-3_smt,,
"""
    csv_path = tmp_path / 'test_target_gap.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test Target Gap Summary'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS

    # Verify target-gap-summary is present in the first mapping
    mc_file = tmp_path / 'output' / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(mc_file)

    assert mc.mappings is not None
    if isinstance(mc.mappings, list):
        first_mapping = mc.mappings[0]
    else:
        first_mapping = mc.mappings

    assert first_mapping.target_gap_summary is not None
    assert first_mapping.target_gap_summary.unmapped_controls is not None

    # Check that unmapped controls list contains our unmapped target controls
    unmapped_list = first_mapping.target_gap_summary.unmapped_controls
    if isinstance(unmapped_list, list):
        assert len(unmapped_list) > 0
        with_ids = unmapped_list[0].with_ids
    else:
        with_ids = unmapped_list.with_ids

    assert with_ids is not None
    assert 'ac-2_smt' in with_ids
    assert 'ac-3_smt' in with_ids
    # ac-1_smt should NOT be in unmapped (it has a source)
    assert 'ac-1_smt' not in with_ids


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_both_gap_summaries(tmp_path: pathlib.Path) -> None:
    """Test CSV with both unmapped source and target controls."""
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage
A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.1,ac-1_smt,subset-of,90%,90%
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.2,,,
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,,ac-2_smt,,
"""
    csv_path = tmp_path / 'test_both_gaps.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test Both Gap Summaries'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS

    # Verify both gap summaries are present in the first mapping
    mc_file = tmp_path / 'output' / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(mc_file)

    assert mc.mappings is not None
    if isinstance(mc.mappings, list):
        first_mapping = mc.mappings[0]
    else:
        first_mapping = mc.mappings

    assert first_mapping.source_gap_summary is not None
    assert first_mapping.target_gap_summary is not None


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_no_gap_summary_when_all_mapped(tmp_path: pathlib.Path) -> None:
    """Test that no gap summary is generated when all controls are mapped."""
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage
A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.1,ac-1_smt,subset-of,90%,90%
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.2,ac-2_smt,subset-of,90%,90%
"""
    csv_path = tmp_path / 'test_no_gaps.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test No Gap Summary'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS

    # Verify no gap summaries are present in mappings
    mc_file = tmp_path / 'output' / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(mc_file)

    assert mc.mappings is not None
    if isinstance(mc.mappings, list):
        first_mapping = mc.mappings[0]
    else:
        first_mapping = mc.mappings

    # Gap summaries should be None when all controls are mapped
    assert first_mapping.source_gap_summary is None
    assert first_mapping.target_gap_summary is None


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_duplicate_unmapped_controls(tmp_path: pathlib.Path) -> None:
    """Test that duplicate unmapped controls are only listed once."""
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage
A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.1,ac-1_smt,subset-of,90%,90%
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.2,,,
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.2,,,
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.2.1,,,
"""
    csv_path = tmp_path / 'test_duplicate_unmapped.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test Duplicate Unmapped'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS

    # Verify source-gap-summary has unique controls only
    mc_file = tmp_path / 'output' / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(mc_file)

    assert mc.mappings is not None
    if isinstance(mc.mappings, list):
        first_mapping = mc.mappings[0]
    else:
        first_mapping = mc.mappings

    assert first_mapping.source_gap_summary is not None
    unmapped_list = first_mapping.source_gap_summary.unmapped_controls
    if isinstance(unmapped_list, list):
        with_ids = unmapped_list[0].with_ids
    else:
        with_ids = unmapped_list.with_ids

    # PCI-1.1.2 should appear only once despite being in CSV twice
    assert with_ids.count('PCI-1.1.2') == 1
    assert 'PCI-1.2.1' in with_ids


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_mixed_mapped_and_unmapped(tmp_path: pathlib.Path) -> None:
    """Test CSV with mix of mapped and unmapped controls from both sides."""
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage
A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.1,ac-1_smt,subset-of,90%,90%
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.2,ac-2_smt,subset-of,90%,90%
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.2.1,,,
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,,ac-3_smt,,
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.2.2,ac-4_smt,subset-of,90%,90%
"""
    csv_path = tmp_path / 'test_mixed.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test Mixed Mapped and Unmapped'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS

    mc_file = tmp_path / 'output' / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(mc_file)

    assert mc.mappings is not None
    if isinstance(mc.mappings, list):
        first_mapping = mc.mappings[0]
    else:
        first_mapping = mc.mappings

    # Verify source gap summary
    assert first_mapping.source_gap_summary is not None
    source_unmapped = first_mapping.source_gap_summary.unmapped_controls
    if isinstance(source_unmapped, list):
        source_ids = source_unmapped[0].with_ids
    else:
        source_ids = source_unmapped.with_ids

    assert 'PCI-1.2.1' in source_ids
    assert 'PCI-1.1.1' not in source_ids  # This one is mapped
    assert 'PCI-1.1.2' not in source_ids  # This one is mapped

    # Verify target gap summary
    assert first_mapping.target_gap_summary is not None
    target_unmapped = first_mapping.target_gap_summary.unmapped_controls
    if isinstance(target_unmapped, list):
        target_ids = target_unmapped[0].with_ids
    else:
        target_ids = target_unmapped.with_ids

    assert 'ac-3_smt' in target_ids
    assert 'ac-1_smt' not in target_ids  # This one is mapped
    assert 'ac-2_smt' not in target_ids  # This one is mapped


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_only_unmapped_sources(tmp_path: pathlib.Path) -> None:
    """Test CSV with only unmapped source controls (no regular mappings)."""
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage
A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.1,,,
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.2,,,
"""
    csv_path = tmp_path / 'test_only_unmapped.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test Only Unmapped Sources'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS

    mc_file = tmp_path / 'output' / 'mapping-collection.json'
    mc = MappingCollection.oscal_read(mc_file)

    # Should have mappings list but it will be empty since no actual mappings exist
    # The gap summary logic only runs if there are mappings
    assert mc.mappings is not None


# Made with Bob


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_both_invalid_controls_no_relationship(tmp_path: pathlib.Path) -> None:
    """Test CSV with both invalid source and target controls but no relationship - should fail."""
    csv_content = """$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage
A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage
catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,invalid_source_id,invalid_target_id,,,
"""
    csv_path = tmp_path / 'test_both_invalid_no_rel.csv'
    csv_path.write_text(csv_content)

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test Both Invalid No Relationship'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    # Should fail because both controls are invalid
    assert retval == TaskOutcome.FAILURE


@set_cwd_unsafe(root_dir / 'tests/data/trestle.ws')
def test_alternate_encoding(tmp_path: pathlib.Path) -> None:
    """Test CSV with non-UTF-8 encoding to trigger alternate encoding path."""
    # Create a CSV header and data rows
    csv_lines = [
        '$$Source_Resource,$$Target_Resource,$$Map_Source_ID_Ref_list,$$Map_Target_ID_Ref_list,$$Map_Relationship,$Map_Confidence_Score,$Map_Coverage\n',
        'A reference to a resource,A reference to a resource,A list of source IDs,A list of target IDs,The relationship type,Confidence score,Coverage percentage\n',
        'catalogs/PCI/catalog.json,catalogs/FedRAMP_rev5_HIGH/catalog.json,PCI-1.1.1,ac-1_smt,subset-of,90%,90%\n',
    ]

    csv_path = tmp_path / 'test_latin1.csv'
    # Write with latin-1 encoding including a character that's invalid in UTF-8
    # Using 0xE9 (é in latin-1) which will cause UTF-8 decode to fail
    with open(csv_path, 'wb') as f:
        for line in csv_lines:
            # Replace a character with latin-1 specific byte to trigger encoding error
            if 'reference' in line:
                line = line.replace('reference', 'ref\xe9rence')
            f.write(line.encode('latin-1'))

    config = configparser.ConfigParser()
    config.add_section('task.csv-to-oscal-mc')
    section = config['task.csv-to-oscal-mc']
    section['title'] = 'Test Alternate Encoding'
    section['version'] = '1.0.0'
    section['csv-file'] = str(csv_path)
    section['output-dir'] = str(tmp_path / 'output')
    section['output-overwrite'] = 'true'

    tgt = csv_to_oscal_mc.CsvToOscalMappingCollection(section)
    retval = tgt.execute()
    # Should succeed with alternate encoding
    assert retval == TaskOutcome.SUCCESS
