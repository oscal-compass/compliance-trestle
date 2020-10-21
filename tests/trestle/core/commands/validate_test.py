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
"""Tests for cli module."""

import shutil
import sys
from unittest.mock import patch

import pytest

from tests import test_utils

from trestle import cli
from trestle.core.err import TrestleValidationError
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal import target as ostarget


def test_target_dups(tmp_dir, sample_target_def: ostarget.TargetDefinition):
    """Test model validation."""
    content_type = FileContentType.YAML

    # prepare trestle project dir with the file
    target_def_dir, target_def_file = test_utils.prepare_trestle_project_dir(
        tmp_dir,
        content_type,
        sample_target_def,
        test_utils.TARGET_DEFS_DIR)

    shutil.copyfile('tests/data/yaml/good_target.yaml', target_def_file)

    testcmd = f'trestle validate -f {target_def_file} -m duplicates -i uuid'
    with patch.object(sys, 'argv', testcmd.split()):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code is None

    shutil.copyfile('tests/data/yaml/bad_target_dup_uuid.yaml', target_def_file)

    testcmd = f'trestle validate -f {target_def_file} -m duplicates -i uuid'
    with patch.object(sys, 'argv', testcmd.split()):
        with pytest.raises(TrestleValidationError) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == TrestleValidationError
