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
"""Tests for trestle href command."""
import os
import pathlib
import sys

from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils

from trestle.cli import Trestle
from trestle.oscal import profile
from trestle.utils.fs import FileContentType


def test_href_cmd(
    tmp_path: pathlib.Path, keep_cwd: pathlib.Path, simplified_nist_profile: profile.Profile, monkeypatch: MonkeyPatch
) -> None:
    """Test basic cmd invocation of href."""
    # prepare trestle project dir with the file
    models_path, profile_path = test_utils.prepare_trestle_project_dir(
        tmp_path,
        FileContentType.JSON,
        simplified_nist_profile,
        test_utils.PROFILES_DIR)

    os.chdir(models_path)

    # just list the hrefs
    cmd_string = 'trestle href -n my_test_model'
    monkeypatch.setattr(sys, 'argv', cmd_string.split())
    rc = Trestle().run()
    assert rc == 0

    orig_href = simplified_nist_profile.imports[0].href

    new_href = 'trestle://catalogs/my_catalog/catalog.json'

    cmd_string = f'trestle href -n my_test_model -hr {new_href}'
    monkeypatch.setattr(sys, 'argv', cmd_string.split())
    rc = Trestle().run()
    assert rc == 0

    # confirm new href is correct
    new_profile: profile.Profile = profile.Profile.oscal_read(profile_path)
    assert new_profile.imports[0].href == new_href

    # restore orig href to confirm models are otherwise equivalent
    # only thing different should be last-modified
    new_profile.imports[0].href = orig_href
    assert test_utils.models_are_equivalent(new_profile, simplified_nist_profile)


def test_href_failures(
    tmp_path: pathlib.Path, keep_cwd: pathlib.Path, simplified_nist_profile: profile.Profile, monkeypatch: MonkeyPatch
) -> None:
    """Test href failure modes."""
    # prepare trestle project dir with the file
    models_path, profile_path = test_utils.prepare_trestle_project_dir(
        tmp_path,
        FileContentType.JSON,
        simplified_nist_profile,
        test_utils.PROFILES_DIR)

    cmd_string = 'trestle href -n my_test_model -hr foobar'

    # not in trestle project so fail
    monkeypatch.setattr(sys, 'argv', cmd_string.split())
    rc = Trestle().run()
    assert rc == 5

    os.chdir(models_path)

    cmd_string = 'trestle href -n my_test_model -hr foobar -i 2'

    # add extra import to the profile and ask for import number 2
    simplified_nist_profile.imports.append(simplified_nist_profile.imports[0])
    simplified_nist_profile.oscal_write(profile_path)
    monkeypatch.setattr(sys, 'argv', cmd_string.split())
    rc = Trestle().run()
    assert rc == 1
