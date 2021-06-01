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
"""Tests for the ssp_generator module."""

import pathlib

from trestle.core.commands.md_subs.ssp_generator import SSPGenerator
from trestle.oscal.catalog import Catalog
from trestle.oscal.profile import Profile


def test_ssp_generator(tmp_trestle_dir, sample_catalog, sample_profile):
    """Test the ssp generator."""
    v_cat = Catalog.oscal_read(pathlib.Path('/tmp/cat/catalogs/v_cat/catalog.json'))
    v_prof = Profile.oscal_read(pathlib.Path('/tmp/cat/profiles/v_prof/profile.json'))
    dest_path = pathlib.Path('/tmp/cat/my_ssp')
    dest_path.mkdir(exist_ok=True)
    ssp_gen = SSPGenerator()
    rc = ssp_gen.generate_ssp(v_cat, v_prof, dest_path, ['ImplGuidance', 'ExpectedEvidence'])
    assert rc == 0
