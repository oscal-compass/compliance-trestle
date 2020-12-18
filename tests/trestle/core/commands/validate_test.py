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

import pytest

from tests import test_utils

from trestle import cli
from trestle.core import utils
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal import target as ostarget


def test_target_dups(tmp_path: pathlib.Path) -> None:
    """Test model validation."""
    content_type = FileContentType.YAML
    models_dir_name = test_utils.TARGET_DEFS_DIR
    model_ref = ostarget.TargetDefinition

    test_utils.ensure_trestle_config_dir(tmp_path)

    file_ext = FileContentType.to_file_extension(content_type)
    models_full_path = tmp_path / models_dir_name / 'my_test_model'
    model_alias = utils.classname_to_alias(model_ref.__name__, 'json')
    model_def_file = models_full_path / f'{model_alias}{file_ext}'
    models_full_path.mkdir(exist_ok=True, parents=True)

    shutil.copyfile('tests/data/yaml/good_target.yaml', model_def_file)

    testcmd = f'trestle validate -f {model_def_file} -m duplicates -i uuid'
    with patch.object(sys, 'argv', testcmd.split()):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

    shutil.copyfile('tests/data/yaml/bad_target_dup_uuid.yaml', model_def_file)

    testcmd = f'trestle validate -f {model_def_file} -m duplicates -i uuid'
    with patch.object(sys, 'argv', testcmd.split()):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    shutil.copyfile('tests/data/yaml/good_target.yaml', model_def_file)

    testcmd = f'trestle validate -f {model_def_file} -m duplicates -i foobar'
    with patch.object(sys, 'argv', testcmd.split()):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.run()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0
