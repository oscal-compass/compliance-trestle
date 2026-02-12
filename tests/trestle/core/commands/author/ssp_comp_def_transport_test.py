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
"""Tests for transporting ALL controls from component definition implemented requirements to SSP."""

import argparse
import pathlib

from tests import test_utils

from trestle.common.model_utils import ModelUtils
from trestle.core.commands.author.ssp import SSPAssemble, SSPGenerate
from trestle.oscal import catalog as cat
from trestle.oscal import component as comp
from trestle.oscal import profile as prof
from trestle.oscal import ssp as ossp


def test_ssp_assemble_scenario_a_no_rules(tmp_trestle_dir: pathlib.Path) -> None:
    """
    Test scenario (a): Component def has implemented requirements where NO rules are associated with ANY controls.

    Expected: Controls in the profile (ac-1, ac-2) should be transported to SSP with their complete structure
    (statements, set-parameters, responsible-roles, remarks) even without rules.
    Controls NOT in the profile (ac-5) should be filtered out.
    """
    comp_name = 'comp_def_no_rules'
    prof_name = 'comp_prof'
    ssp_name = 'test_ssp_no_rules'

    # Load test data
    test_utils.load_from_json(tmp_trestle_dir, comp_name, comp_name, comp.ComponentDefinition)
    test_utils.load_from_json(tmp_trestle_dir, prof_name, prof_name, prof.Profile)
    test_utils.load_from_json(tmp_trestle_dir, 'simplified_nist_catalog', 'simplified_nist_catalog', cat.Catalog)

    # Generate SSP markdown
    gen_args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        compdefs=comp_name,
        output=ssp_name,
        verbose=0,
        overwrite_header_values=False,
        yaml_header=None,
        allowed_sections=None,
        force_overwrite=None,
        leveraged_ssp='',
        include_all_parts=False,
    )

    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    # Assemble SSP
    assemble_args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=False,
        version=None,
        name=None,
        compdefs=comp_name,
    )

    ssp_assemble = SSPAssemble()
    assert ssp_assemble._run(assemble_args) == 0

    # Verify all controls are transported
    ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    imp_req_map = {imp_req.control_id: imp_req for imp_req in ssp.control_implementation.implemented_requirements}

    # Verify AC-1 (no rules, in profile)
    assert 'ac-1' in imp_req_map, 'AC-1 (no rules, in profile) should be transported'
    ac1 = imp_req_map['ac-1']
    assert ac1.statements is not None, 'AC-1 statements should be transported'
    assert any(stmt.statement_id == 'ac-1_smt.a' for stmt in ac1.statements), 'AC-1 statement a should be present'
    assert ac1.remarks == 'AC-1 remarks without rules', 'AC-1 remarks should be transported'

    # Verify AC-2 (no rules, in profile)
    assert 'ac-2' in imp_req_map, 'AC-2 (no rules, in profile) should be transported'
    ac2 = imp_req_map['ac-2']
    assert ac2.statements is not None, 'AC-2 statements should be transported'

    # Verify AC-5 (no rules, NOT in profile) - should NOT be transported due to profile filtering
    assert 'ac-5' not in imp_req_map, 'AC-5 (NOT in profile) should be filtered out'


def test_ssp_assemble_scenario_b_mixed_rules(tmp_trestle_dir: pathlib.Path) -> None:
    """
    Test scenario (b): Component def has implemented requirements where SOME controls have rules.

    Expected: Controls in the profile should be transported with their complete structure regardless of rules:
    - ac-1 (with rules, in profile) - transported
    - ac-2 (without rules, in profile) - transported
    Controls NOT in the profile (ac-5) should be filtered out even if they have rules.
    """
    comp_name = 'comp_def_mixed_rules'
    prof_name = 'comp_prof'
    ssp_name = 'test_ssp_mixed_rules'

    # Load test data
    test_utils.load_from_json(tmp_trestle_dir, comp_name, comp_name, comp.ComponentDefinition)
    test_utils.load_from_json(tmp_trestle_dir, prof_name, prof_name, prof.Profile)
    test_utils.load_from_json(tmp_trestle_dir, 'simplified_nist_catalog', 'simplified_nist_catalog', cat.Catalog)

    # Generate and assemble
    gen_args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        compdefs=comp_name,
        output=ssp_name,
        verbose=0,
        overwrite_header_values=False,
        yaml_header=None,
        allowed_sections=None,
        force_overwrite=None,
        leveraged_ssp='',
        include_all_parts=False,
    )

    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    assemble_args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=False,
        version=None,
        name=None,
        compdefs=comp_name,
    )

    ssp_assemble = SSPAssemble()
    assert ssp_assemble._run(assemble_args) == 0

    # Verify
    ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    imp_req_map = {imp_req.control_id: imp_req for imp_req in ssp.control_implementation.implemented_requirements}

    # Verify AC-1 (with rules, in profile)
    assert 'ac-1' in imp_req_map, 'AC-1 (with rules, in profile) should be transported'
    ac1 = imp_req_map['ac-1']
    assert ac1.statements is not None, 'AC-1 statements should be transported'
    assert ac1.by_components is not None, 'AC-1 should have by_components from rules'
    assert ac1.remarks == 'AC-1 with rules', 'AC-1 remarks should be transported'

    # Verify AC-2 (no rules, in profile)
    assert 'ac-2' in imp_req_map, 'AC-2 (no rules, in profile) should be transported'
    ac2 = imp_req_map['ac-2']
    assert ac2.statements is not None, 'AC-2 statements should be transported'
    assert ac2.remarks == 'AC-2 without rules', 'AC-2 remarks should be transported'

    # Verify AC-5 (no rules, NOT in profile) - should NOT be transported due to profile filtering
    assert 'ac-5' not in imp_req_map, 'AC-5 (NOT in profile) should be filtered out'


def test_ssp_assemble_scenario_c_all_rules(tmp_trestle_dir: pathlib.Path) -> None:
    """
    Test scenario (c): Component def has implemented requirements where ALL controls have rules.

    Expected: Controls in the profile (ac-1, ac-2) should be transported with their complete structure.
    Controls NOT in the profile (ac-5) should be filtered out even though they have rules.
    This confirms that profile membership takes precedence over rules affiliation.
    """
    comp_name = 'comp_def_all_rules'
    prof_name = 'comp_prof'
    ssp_name = 'test_ssp_all_rules'

    # Load test data
    test_utils.load_from_json(tmp_trestle_dir, comp_name, comp_name, comp.ComponentDefinition)
    test_utils.load_from_json(tmp_trestle_dir, prof_name, prof_name, prof.Profile)
    test_utils.load_from_json(tmp_trestle_dir, 'simplified_nist_catalog', 'simplified_nist_catalog', cat.Catalog)

    # Generate and assemble
    gen_args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        profile=prof_name,
        compdefs=comp_name,
        output=ssp_name,
        verbose=0,
        overwrite_header_values=False,
        yaml_header=None,
        allowed_sections=None,
        force_overwrite=None,
        leveraged_ssp='',
        include_all_parts=False,
    )

    ssp_gen = SSPGenerate()
    assert ssp_gen._run(gen_args) == 0

    assemble_args = argparse.Namespace(
        trestle_root=tmp_trestle_dir,
        markdown=ssp_name,
        output=ssp_name,
        verbose=0,
        regenerate=False,
        version=None,
        name=None,
        compdefs=comp_name,
    )

    ssp_assemble = SSPAssemble()
    assert ssp_assemble._run(assemble_args) == 0

    # Verify
    ssp, _ = ModelUtils.load_model_for_class(tmp_trestle_dir, ssp_name, ossp.SystemSecurityPlan)
    imp_req_map = {imp_req.control_id: imp_req for imp_req in ssp.control_implementation.implemented_requirements}

    # Verify AC-1 (with rules, in profile)
    assert 'ac-1' in imp_req_map, 'AC-1 (with rules, in profile) should be transported'
    ac1 = imp_req_map['ac-1']
    assert ac1.statements is not None, 'AC-1 statements should be transported'
    assert ac1.by_components is not None, 'AC-1 should have by_components from rules'
    assert ac1.remarks == 'AC-1 with rules', 'AC-1 remarks should be transported'

    # Verify AC-2 (with rules, in profile)
    assert 'ac-2' in imp_req_map, 'AC-2 (with rules, in profile) should be transported'
    ac2 = imp_req_map['ac-2']
    assert ac2.statements is not None, 'AC-2 statements should be transported'
    assert ac2.by_components is not None, 'AC-2 should have by_components from rules'
    assert ac2.remarks == 'AC-2 with rules', 'AC-2 remarks should be transported'

    # Verify AC-5 (with rules, NOT in profile) - should NOT be transported due to profile filtering
    assert 'ac-5' not in imp_req_map, 'AC-5 (NOT in profile) should be filtered out even with rules'


# Made with Bob
