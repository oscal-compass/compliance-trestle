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
import argparse
import pathlib

from _pytest.monkeypatch import MonkeyPatch

from tests.test_utils import setup_for_ssp

from trestle.core.commands.author.ssp import SSPAssemble, SSPGenerate
from trestle.core.remote import cache
from trestle.core.ssp_io import SSPMarkdownWriter

prof_name = 'main_profile'
ssp_name = 'my_ssp'


def test_ssp_writer(testdata_dir: pathlib.Path, tmp_trestle_dir: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Test ssp writer from cli."""
    gen_args, _, _ = setup_for_ssp(True, True, tmp_trestle_dir, prof_name, ssp_name)

    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, markdown=ssp_name, output=ssp_name, verbose=True, regenerate=False
    )
    assert ssp_assemble._run(args) == 0

    profile_path = tmp_trestle_dir / f'profiles/{prof_name}/profile.json'
    new_catalog_dir = tmp_trestle_dir / f'catalogs/{prof_name}_resolved_catalog'
    new_catalog_dir.mkdir(parents=True, exist_ok=True)

    ssp_writer = SSPMarkdownWriter(args.trestle_root)
    ssp_writer.set_profile(profile_path)
    md_text = ssp_writer.get_control_statement('au-8', 1)
    assert md_text is not None

    ssp_json = testdata_dir / 'author/ssp/ssp_example.json'
    fetcher = cache.FetcherFactory.get_fetcher(args.trestle_root, str(ssp_json))
    ssp_obj, parent_alias = fetcher.get_oscal(True)

    assert parent_alias == 'system-security-plan'
    ssp_writer.set_ssp(ssp_obj)
    roles_md = ssp_writer.get_responsible_roles_table('ac-2', 1)

    assert roles_md

    md_text1 = ssp_writer._parameter_table('au-8', 1)
    assert md_text1

    md_text2 = ssp_writer.get_control_response('au-8', 1)
    assert md_text2

    md_text3 = ssp_writer.get_fedramp_control_tables('ac-2', 1)
    assert md_text3

    md_text4 = ssp_writer.get_control_part('au-8', 'item', 1)
    assert md_text4
