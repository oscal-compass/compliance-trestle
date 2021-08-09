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
"""Tests for trestle href command."""
import os
import pathlib
import sys
from unittest.mock import patch

from tests import test_utils

from trestle.cli import Trestle
from trestle.oscal import profile
from trestle.utils.fs import FileContentType


def test_href_cmd(tmp_path: pathlib.Path, keep_cwd: pathlib.Path, sample_profile: profile.Profile) -> None:
    """Test basic cmd invocation of href."""
    # prepare trestle project dir with the file
    models_path, profile_path = test_utils.prepare_trestle_project_dir(
        tmp_path,
        FileContentType.JSON,
        sample_profile,
        test_utils.PROFILES_DIR)

    os.chdir(models_path)

    orig_href = sample_profile.imports[0].href

    new_href = 'trestle://catalogs/my_catalog/catalog.json'

    cmd_string = f'trestle href -n my_test_model -hr {new_href}'
    with patch.object(sys, 'argv', cmd_string.split()):
        rc = Trestle().run()
        assert rc == 0

    # confirm new href is correct
    new_profile: profile.Profile = profile.Profile.oscal_read(profile_path)
    assert new_profile.imports[0].href == new_href

    # restore orig href to confirm models are otherwise equivalent
    # only thing different should be last-modified
    new_profile.imports[0].href = orig_href
    assert test_utils.models_are_equivalent(new_profile, sample_profile)


def test_href_failures(tmp_path: pathlib.Path, keep_cwd: pathlib.Path, sample_profile: profile.Profile) -> None:
    """Test href failure modes."""
    # prepare trestle project dir with the file
    models_path, profile_path = test_utils.prepare_trestle_project_dir(
        tmp_path,
        FileContentType.JSON,
        sample_profile,
        test_utils.PROFILES_DIR)

    cmd_string = 'trestle href -n my_test_model -hr foobar'

    # not in trestle project so fail
    with patch.object(sys, 'argv', cmd_string.split()):
        rc = Trestle().run()
        assert rc == 1

    os.chdir(models_path)

    # add extra import to the profile to force failure
    # currently only one import is allowed
    sample_profile.imports.append(sample_profile.imports[0])
    sample_profile.oscal_write(profile_path)
    with patch.object(sys, 'argv', cmd_string.split()):
        rc = Trestle().run()
        assert rc == 1
