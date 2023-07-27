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
"""Tests for the ExportInterface class."""

from tests import test_utils

import trestle.oscal.ssp as ossp
from trestle.core.crm.export_interface import ExportInterface

test_profile = 'simple_test_profile'
test_ssp = 'leveraged_ssp'


def test_get_isolated_responsibilities() -> None:
    """Test retrieving isolated responsibilities statements."""
    by_comp: ossp.ByComponent = test_utils.generate_test_by_comp()
    expected_responsibility = 1
    expected_uuid = by_comp.export.responsibilities[0].uuid

    export_interface: ExportInterface = ExportInterface(by_comp)

    result = export_interface.get_isolated_responsibilities()

    assert len(result) == expected_responsibility
    assert result[0].uuid == expected_uuid


def test_get_isolated_provided() -> None:
    """Test retrieving isolated provided statements."""
    by_comp: ossp.ByComponent = test_utils.generate_test_by_comp()
    expected_provided = 1
    expected_uuid = by_comp.export.provided[0].uuid

    export_interface: ExportInterface = ExportInterface(by_comp)

    result = export_interface.get_isolated_provided()

    assert len(result) == expected_provided
    assert result[0].uuid == expected_uuid


def test_get_export_sets() -> None:
    """Test retrieving export set statements."""
    by_comp: ossp.ByComponent = test_utils.generate_test_by_comp()
    expected_set = 1
    expected_responsibility_uuid = by_comp.export.responsibilities[1].uuid
    expected_provided_uuid = by_comp.export.provided[1].uuid

    export_interface: ExportInterface = ExportInterface(by_comp)

    result = export_interface.get_export_sets()

    result_set = result[0]

    assert len(result) == expected_set
    assert result_set[0].uuid == expected_responsibility_uuid
    assert result_set[0].provided_uuid == expected_provided_uuid
    assert result_set[1].uuid == expected_provided_uuid
