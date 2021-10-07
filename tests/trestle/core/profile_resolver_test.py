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
"""Tests profile_resolver module."""

import argparse
import logging
import pathlib
from typing import List, Tuple

from pydantic import ValidationError

import pytest

from tests import test_utils

from trestle.core.commands.author.ssp import SSPGenerate
from trestle.core.commands.import_ import ImportCmd
from trestle.core.profile_resolver import CatalogInterface, ProfileResolver
from trestle.utils import log


def find_string_in_all_controls_prose(interface: CatalogInterface, seek_str: str) -> List[Tuple[str, str]]:
    """Find all instances of this string in catalog prose and return with control id."""
    hits: List[Tuple[str, str]] = []
    for control in interface.get_all_controls(True):
        hits.extend(interface.find_string_in_control(control, seek_str))
    return hits


def test_profile_resolver(tmp_trestle_dir: pathlib.Path) -> None:
    """Test the resolver."""
    cat_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        file=str(cat_path),
        output='NIST_SP-800-53_rev5_catalog',
        verbose=False,
        regenerate=True
    )
    i = ImportCmd()
    assert i._run(args) == 0

    complex_cat_dir = tmp_trestle_dir / 'catalogs/complex_cat'

    complex_cat_dir.mkdir(exist_ok=True, parents=True)
    complex_cat = test_utils.generate_complex_catalog()
    complex_cat.oscal_write(complex_cat_dir / 'catalog.json')

    prof_a_path = test_utils.JSON_TEST_DATA_PATH / 'test_profile_a.json'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=str(prof_a_path), output='test_profile_a', verbose=False, regenerate=True
    )
    i = ImportCmd()
    assert i._run(args) == 0

    prof_b_path = test_utils.JSON_TEST_DATA_PATH / 'test_profile_b.json'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=str(prof_b_path), output='test_profile_b', verbose=False, regenerate=True
    )
    i = ImportCmd()
    assert i._run(args) == 0

    prof_c_path = test_utils.JSON_TEST_DATA_PATH / 'test_profile_c.json'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=str(prof_c_path), output='test_profile_c', verbose=False, regenerate=True
    )
    i = ImportCmd()
    assert i._run(args) == 0

    log.set_global_logging_levels(logging.DEBUG)

    cat = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_a_path)
    interface = CatalogInterface(cat)
    list1 = find_string_in_all_controls_prose(interface, 'Detailed evidence logs')
    list2 = find_string_in_all_controls_prose(interface, 'full and complete compliance')

    assert len(list1) == 1
    assert len(list2) == 1

    cat_dir = tmp_trestle_dir / 'catalogs/my_cat'
    cat_dir.mkdir(exist_ok=True, parents=True)
    cat.oscal_write(cat_dir / 'catalog.json')

    ssp_cmd = SSPGenerate()
    sections = 'ImplGuidance:Implementation Guidance,ExpectedEvidence:Expected Evidence,guidance:Guidance'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, profile='test_profile_a', output='my_ssp', verbose=True, sections=sections
    )
    assert ssp_cmd._run(args) == 0

    assert interface.get_count_of_controls(False) == 6

    assert interface.get_count_of_controls(True) == 7

    assert len(cat.controls) == 1

    assert interface.get_dependent_control_ids('ac-3') == ['ac-3.3']

    assert interface.get_control('a-1').parts[0].parts[0].parts[0].id == 'a-1_deep'
    assert interface.get_control('a-1').parts[0].parts[0].parts[0].prose == 'Extra added part in subpart'


def test_deep_catalog() -> None:
    """Test ssp generation with deep catalog."""
    catalog = test_utils.generate_complex_catalog()
    interface = CatalogInterface(catalog)
    assert interface.get_count_of_controls(False) == 10
    assert interface.get_count_of_controls(True) == 15


def test_fail_when_reference_id_is_not_given_after_or_before(tmp_trestle_dir: pathlib.Path) -> None:
    """Test when by_id is not given and position is set to after or before it fails."""
    cat_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        file=str(cat_path),
        output='NIST_SP-800-53_rev5_catalog',
        verbose=False,
        regenerate=True
    )
    i = ImportCmd()
    assert i._run(args) == 0

    prof_a_path = test_utils.JSON_TEST_DATA_PATH / 'profile_with_incorrect_alter.json'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=str(prof_a_path), output='incorrect_profile', verbose=False, regenerate=True
    )
    i = ImportCmd()

    with pytest.raises(ValidationError):
        i._run(args)


def test_all_positions_for_alter_can_be_resolved(tmp_trestle_dir: pathlib.Path) -> None:
    """Test that all alter adds positions can be resolved."""
    cat_path = test_utils.JSON_NIST_DATA_PATH / test_utils.JSON_NIST_CATALOG_NAME
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        file=str(cat_path),
        output='NIST_SP-800-53_rev5_catalog',
        verbose=False,
        regenerate=True
    )
    i = ImportCmd()
    assert i._run(args) == 0

    prof_a_path = test_utils.JSON_TEST_DATA_PATH / 'test_profile_d.json'
    args = argparse.Namespace(
        trestle_root=tmp_trestle_dir, file=str(prof_a_path), output='test_profile_d', verbose=False, regenerate=True
    )
    i = ImportCmd()
    assert i._run(args) == 0

    cat = ProfileResolver.get_resolved_profile_catalog(tmp_trestle_dir, prof_a_path)

    interface = CatalogInterface(cat)
    control_a1 = interface.get_control('ac-1')
    control_a2 = interface.get_control('ac-2')

    assert control_a1.parts[0].id == 'ac-1_first_lev1'
    assert control_a1.parts[1].parts[3].id == 'ac-1_last_lev2'
    assert control_a1.parts[2].id == 'ac-1_after1_ac-1_smt_lev1'
    assert control_a1.parts[3].id == 'ac-1_after2_ac-1_smt_lev1'
    assert control_a1.parts[1].parts[0].parts[1].id == 'ac-1_smt_before1_a.2_lev3'
    assert control_a1.parts[1].parts[0].parts[2].id == 'ac-1_smt_before2_a.2_lev3'
    assert control_a1.parts[1].parts[0].parts[3].parts[0].id == 'ac-1_smt_inside1_at_the_end_a.2_lev4'
    assert control_a1.parts[1].parts[0].parts[3].parts[1].id == 'ac-1_smt_inside2_at_the_end_a.2_lev4'
    assert control_a2.parts[0].id == 'ac-2_implgdn_lev1'
