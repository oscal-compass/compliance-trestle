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
"""Tests for the transform_oscal module."""

import argparse
import pathlib
from typing import Tuple

from tests import test_utils

from trestle.core import const
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.ssp import SSPAssemble, SSPGenerate
from trestle.core.commands.transform_oscal import TransformCmd
from trestle.oscal.catalog import Catalog
from trestle.utils import fs

prof_name = 'main_profile'
ssp_name = 'my_ssp'
cat_name = 'nist_cat'
resolved_cat_name = 'resolved_cat'


def setup_for_ssp(include_header: bool,
                  big_profile: bool,
                  tmp_trestle_dir: pathlib.Path,
                  import_nist_cat: bool = True) -> Tuple[argparse.Namespace, str]:
    """Create the markdown ssp content from catalog and profile."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, big_profile, import_nist_cat)

    yaml_path = test_utils.YAML_TEST_DATA_PATH / 'good_simple.yaml'
    sections = 'ImplGuidance:Implementation Guidance,ExpectedEvidence:Expected Evidence,guidance:Guidance'
    if include_header:
        args = argparse.Namespace(
            trestle_root=tmp_trestle_dir,
            profile=prof_name,
            output=ssp_name,
            verbose=True,
            sections=sections,
            yaml_header=str(yaml_path)
        )
    else:
        args = argparse.Namespace(
            trestle_root=tmp_trestle_dir,
            profile=prof_name,
            output=ssp_name,
            verbose=True,
            sections=sections,
            preserve_header_values=False
        )
    return args, sections, yaml_path


def test_ssp_transform(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the transform of an ssp."""
    # install the catalog and profiles
    gen_args, _, _ = setup_for_ssp(False, False, tmp_trestle_dir, True)
    # create markdown with profile a
    gen_args.profile = 'test_profile_a'
    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    # create ssp from the markdown
    ssp_assemble = SSPAssemble()
    args = argparse.Namespace(trestle_root=tmp_trestle_dir, markdown=ssp_name, output=ssp_name, verbose=True)
    assert ssp_assemble._run(args) == 0

    # now transform it with: trestle transform -t system-security-plan -i my_ssp -p test_profile_d -o xformed_ssp
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        type=const.MODEL_TYPE_SSP,
        transform=const.FILTER_BY_PROFILE,
        input=ssp_name,
        transform_by='test_profile_d',
        output='xformed_ssp',
        regenerate=False,
        verbose=True
    )
    transform_oscal = TransformCmd()
    rc = transform_oscal._run(args)
    assert rc == 0

    assert transform_oscal.transform(
        tmp_trestle_dir, const.MODEL_TYPE_SSP, const.FILTER_BY_PROFILE, 'bar', 'myout', 'myprof', False
    ) == 1


def test_transform_failure(tmp_trestle_dir: pathlib.Path) -> None:
    """Test exception paths."""
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        type=const.MODEL_TYPE_PROFILE,
        transform=const.GENERATE_RESOLVED_CATALOG,
        input=prof_name,
        transform_by='',
        output=resolved_cat_name,
        regenerate=False,
        verbose=True
    )
    transform_oscal = TransformCmd()
    assert transform_oscal._run(args) == 1


def test_resolved_catalog_transform(tmp_trestle_dir: pathlib.Path) -> None:
    """Test generation of resolved catalog from profile."""
    test_utils.setup_for_multi_profile(tmp_trestle_dir, False, False)

    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        type=const.MODEL_TYPE_PROFILE,
        transform=const.GENERATE_RESOLVED_CATALOG,
        input=prof_name,
        transform_by='',
        output=resolved_cat_name,
        regenerate=False,
        verbose=True
    )
    transform_oscal = TransformCmd()
    rc = transform_oscal._run(args)
    assert rc == 0

    resolved_catalog, _ = fs.load_top_level_model(tmp_trestle_dir, resolved_cat_name, Catalog)
    catalog_interface = CatalogInterface(resolved_catalog)
    n_controls = catalog_interface.get_count_of_controls_in_dict()
    assert n_controls == 3
