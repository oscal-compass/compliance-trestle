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
"""Tests for the ExportWriter class."""

import os
import pathlib
from typing import List, Tuple
from unittest.mock import Mock, patch

import pytest

from tests import test_utils

import trestle.core.generators as gens
import trestle.oscal.ssp as ossp
from trestle.common.err import TrestleError
from trestle.common.model_utils import ModelUtils
from trestle.core.crm.export_interface import ExportInterface
from trestle.core.crm.export_writer import ExportWriter
from trestle.core.inheritance_writer import (
    LeveragedStatements,
    StatementProvided,
    StatementResponsibility,
    StatementTree,
)
from trestle.core.models.file_content_type import FileContentType

test_profile = 'simple_test_profile'
test_ssp = 'leveraged_ssp'


def custom_side_effect(file_path: pathlib.Path) -> None:
    """Write a test file."""
    with open(file_path, 'w') as file:
        file.write('test')


def test_write_exports_as_markdown(tmp_trestle_dir: pathlib.Path) -> None:
    """Test happy path for writing markdown with a mock LeveragedStatement."""
    _ = test_utils.setup_for_inherit(tmp_trestle_dir, test_profile, '', test_ssp)
    ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, test_ssp, ossp.SystemSecurityPlan, FileContentType.JSON)

    inherited_path = tmp_trestle_dir.joinpath('inherited')
    writer = ExportWriter(inherited_path, ssp)

    mock = Mock(spec=LeveragedStatements)
    mock.write_statement_md.side_effect = custom_side_effect

    with patch('trestle.core.crm.export_writer.ExportWriter._statement_types_from_exports') as mock_process:
        return_value: List[Tuple[str, LeveragedStatements]] = {'filepath': mock}
        mock_process.return_value = return_value
        writer.write_exports_as_markdown()

        assert os.path.exists(inherited_path.joinpath('This System', 'ac-2.1', 'filepath.md'))
        # Check that directory are not created when no exports exists
        assert not os.path.exists(inherited_path.joinpath('Application', 'ac2'))


def test_write_exports_as_markdown_invalid_ssp(tmp_trestle_dir: pathlib.Path) -> None:
    """Test triggering an error with an invalid SSP input."""
    _ = test_utils.setup_for_inherit(tmp_trestle_dir, test_profile, '', test_ssp)
    ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, test_ssp, ossp.SystemSecurityPlan, FileContentType.JSON)

    # Delete a component that is used to create an invalid SSP
    ssp.system_implementation.components.remove(ssp.system_implementation.components[2])

    inherited_path = tmp_trestle_dir.joinpath('inherited')
    writer = ExportWriter(inherited_path, ssp)

    with pytest.raises(TrestleError, match=r'Component .* is not in the system implementation'):
        writer.write_exports_as_markdown()


def test_statement_types_from_exports(tmp_trestle_dir: pathlib.Path) -> None:
    """Test generated LeveragedStatements and filenames with SSP input."""
    expected_provided = 1
    expected_responsibility = 1
    expected_set = 1

    ssp = gens.generate_sample_model(ossp.SystemSecurityPlan)

    inherited_path = tmp_trestle_dir.joinpath('inherited')
    writer = ExportWriter(inherited_path, ssp)

    by_comp: ossp.ByComponent = test_utils.generate_test_by_comp()
    export_interface: ExportInterface = ExportInterface(by_comp)

    result_leveraged_statements = writer._statement_types_from_exports(export_interface)
    provided: List[StatementProvided] = []
    responsibility: List[StatementResponsibility] = []
    sets: List[StatementTree] = []

    for leveraged_stm in result_leveraged_statements.values():
        if isinstance(leveraged_stm, StatementProvided):
            provided.append(leveraged_stm)
        elif isinstance(leveraged_stm, StatementResponsibility):
            responsibility.append(leveraged_stm)
        elif isinstance(leveraged_stm, StatementTree):
            sets.append(leveraged_stm)

    assert len(provided) == expected_provided
    assert len(responsibility) == expected_responsibility
    assert len(sets) == expected_set


def test_statement_types_no_exports(tmp_trestle_dir: pathlib.Path) -> None:
    """Test generated LeveragedStatements and filenames with no exports."""
    ssp = gens.generate_sample_model(ossp.SystemSecurityPlan)

    inherited_path = tmp_trestle_dir.joinpath('inherited')
    writer = ExportWriter(inherited_path, ssp)

    by_comp = gens.generate_sample_model(ossp.ByComponent)
    export_interface: ExportInterface = ExportInterface(by_comp)

    result_leveraged_statements = writer._statement_types_from_exports(export_interface)

    assert len(result_leveraged_statements) == 0
