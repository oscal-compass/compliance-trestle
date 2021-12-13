# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Tests for the ssp_io."""
import pathlib
from typing import Tuple

from _pytest.monkeypatch import MonkeyPatch

from tests.test_utils import execute_command_and_assert, setup_for_ssp
from tests.trestle.core.commands.author.ssp_test import insert_prose

from trestle.core.remote import cache
from trestle.core.ssp_io import SSPMarkdownWriter
from trestle.oscal.ssp import SystemSecurityPlan

prof_name = 'main_profile'
ssp_name = 'my_ssp'


def setup_test(tmp_trestle_dir: pathlib.Path, testdata_dir: pathlib.Path,
               trestle_root: str) -> Tuple[pathlib.Path, SystemSecurityPlan]:
    """Prepare ssp test."""
    profile_path = tmp_trestle_dir / f'profiles/{prof_name}/profile.json'
    new_catalog_dir = tmp_trestle_dir / f'catalogs/{prof_name}_resolved_catalog'
    new_catalog_dir.mkdir(parents=True, exist_ok=True)

    ssp_json = testdata_dir / 'author/ssp/ssp_example.json'
    fetcher = cache.FetcherFactory.get_fetcher(trestle_root, str(ssp_json))
    ssp_obj, parent_alias = fetcher.get_oscal(True)

    assert parent_alias == 'system-security-plan'

    return profile_path, ssp_obj


def test_ssp_writer(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test ssp writer from cli."""
    gen_args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir, prof_name, ssp_name)

    profile_path, ssp_obj = setup_test(tmp_trestle_dir, testdata_dir, gen_args.trestle_root)
    ssp_writer = SSPMarkdownWriter(gen_args.trestle_root)
    ssp_writer.set_profile(profile_path)
    md_text = ssp_writer.get_control_statement('au-8', 1)
    assert md_text is not None

    ssp_writer.set_ssp(ssp_obj)
    roles_md = ssp_writer.get_responsible_roles_table('ac-2', 1)
    assert roles_md

    md_text1 = ssp_writer._parameter_table('au-8', 1)
    assert md_text1

    md_text3 = ssp_writer.get_fedramp_control_tables('ac-2', 1)
    assert md_text3

    md_text4 = ssp_writer.get_control_part('au-8', 'item', 1)
    assert md_text4


def test_ssp_from_samples_e2e(
    testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Test generating SSP from the sample profile and generate markdown representation of it."""
    profile_path = testdata_dir / 'author/ssp/sample_profile.json'
    catalog_1_path = testdata_dir / 'author/ssp/sample_nist_catalog.json'
    catalog_2_path = testdata_dir / 'author/ssp/sample_security_catalog.json'

    command_import_catalog = f'trestle import -f {catalog_1_path} -o sample_nist_catalog'
    execute_command_and_assert(command_import_catalog, 0, monkeypatch)

    command_import_catalog = f'trestle import -f {catalog_2_path} -o sample_security_catalog'
    execute_command_and_assert(command_import_catalog, 0, monkeypatch)

    command_import_profile = f'trestle import -f {profile_path} -o test_profile'
    execute_command_and_assert(command_import_profile, 0, monkeypatch)

    # generate SSP from the profile
    command_ssp_gen = 'trestle author ssp-generate -p test_profile -o my_ssp'
    execute_command_and_assert(command_ssp_gen, 0, monkeypatch)

    # set responses
    assert insert_prose(tmp_trestle_dir, 'at-1_smt.b', 'This is a response')
    assert insert_prose(tmp_trestle_dir, 'at-1_smt.c', 'This is also a response.')
    assert insert_prose(tmp_trestle_dir, 'ac-1_smt.a', 'This is a response.')

    command_ssp_gen = 'trestle author ssp-assemble -m my_ssp -o ssp_json'
    execute_command_and_assert(command_ssp_gen, 0, monkeypatch)

    ssp_json_path = tmp_trestle_dir / 'system-security-plans/ssp_json/system-security-plan.json'
    fetcher = cache.FetcherFactory.get_fetcher(tmp_trestle_dir, str(ssp_json_path))
    ssp_obj, parent_alias = fetcher.get_oscal(True)

    ssp_io = SSPMarkdownWriter(tmp_trestle_dir)
    ssp_io.set_profile(profile_path)
    ssp_io.set_ssp(ssp_obj)

    md_text = ssp_io.get_control_response('at-1', 1, True)
    assert md_text
