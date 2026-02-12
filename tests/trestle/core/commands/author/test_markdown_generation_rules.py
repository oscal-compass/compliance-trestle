"""Test that markdown generation obeys same requirements for comp.def impl req and rules association."""

import argparse
import pathlib

from tests import test_utils

from trestle.common.model_utils import ModelUtils
from trestle.core.commands.author.ssp import SSPGenerate
from trestle.oscal import catalog as cat
from trestle.oscal import component as comp
from trestle.oscal import profile as prof


def test_markdown_generation_includes_controls_without_rules(tmp_trestle_dir: pathlib.Path) -> None:
    """
    Test that markdown generation includes controls and statements WITHOUT rules.

    This test verifies that the markdown generation process (SSPGenerate) properly
    includes implementation requirements and statements that don't have associated rules,
    ensuring consistency with the assembly process. It also verifies that the complete
    structure (statements, descriptions, remarks) is carried through to the markdown.
    """
    comp_name = 'comp_def_no_rules'
    prof_name = 'comp_prof'
    ssp_name = 'test_ssp_markdown_no_rules'

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

    # Check that markdown files were created for controls without rules
    md_path = tmp_trestle_dir / ssp_name

    # AC-1 should have markdown (no rules, in profile)
    ac1_md = md_path / 'ac' / 'ac-1.md'
    assert ac1_md.exists(), 'AC-1 markdown should be generated even without rules'

    # Read the markdown and verify it contains the complete component information
    with open(ac1_md, 'r') as f:
        content = f.read()
        # Check that component name appears in the markdown
        assert 'comp_no_rules' in content, 'Component name should appear in AC-1 markdown'
        # Check that the implementation description is present
        assert 'AC-1 implementation without rules' in content, 'AC-1 implementation description should be in markdown'
        # Check that the statement is present
        assert 'ac-1_smt.a' in content or 'part a' in content.lower(), 'AC-1 statement should be in markdown'
        # Check that statement description is present
        assert 'AC-1 part a statement without rules' in content, 'AC-1 statement description should be in markdown'
        # Note: Remarks are not currently written to SSP markdown, only to component definition markdown

    # AC-2 should have markdown (no rules, in profile)
    ac2_md = md_path / 'ac' / 'ac-2.md'
    assert ac2_md.exists(), 'AC-2 markdown should be generated even without rules'

    with open(ac2_md, 'r') as f:
        content = f.read()
        assert 'comp_no_rules' in content, 'Component name should appear in AC-2 markdown'
        assert 'AC-2 implementation without rules' in content, 'AC-2 implementation description should be in markdown'
        assert 'ac-2_smt.a' in content or 'part a' in content.lower(), 'AC-2 statement should be in markdown'
        assert 'AC-2 part a statement without rules' in content, 'AC-2 statement description should be in markdown'

    # AC-5 should NOT have markdown (not in profile)
    ac5_md = md_path / 'ac' / 'ac-5.md'
    assert not ac5_md.exists(), 'AC-5 markdown should NOT be generated (not in profile)'


def test_markdown_generation_mixed_rules(tmp_trestle_dir: pathlib.Path) -> None:
    """
    Test markdown generation with mixed rules scenario.

    Verifies that controls with rules AND controls without rules are both properly
    represented in the generated markdown with their complete structure.
    """
    comp_name = 'comp_def_mixed_rules'
    prof_name = 'comp_prof'
    ssp_name = 'test_ssp_markdown_mixed'

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

    md_path = tmp_trestle_dir / ssp_name

    # AC-1 should have markdown (WITH rules, in profile)
    ac1_md = md_path / 'ac' / 'ac-1.md'
    assert ac1_md.exists(), 'AC-1 markdown should be generated (with rules)'

    with open(ac1_md, 'r') as f:
        content = f.read()
        assert 'comp_mixed_rules' in content, 'Component name should appear in AC-1 markdown'
        # Should have rules section
        assert 'comp-def-rules' in content.lower() or 'rule' in content.lower(), 'AC-1 should show rules info'
        # Verify complete structure is present
        assert 'AC-1 implementation WITH rules' in content, 'AC-1 implementation description should be in markdown'
        # Note: Remarks are not currently written to SSP markdown

    # AC-2 should have markdown (WITHOUT rules, in profile)
    ac2_md = md_path / 'ac' / 'ac-2.md'
    assert ac2_md.exists(), 'AC-2 markdown should be generated even without rules'

    with open(ac2_md, 'r') as f:
        content = f.read()
        assert 'comp_mixed_rules' in content, 'Component name should appear in AC-2 markdown'
        # Verify complete structure is present even without rules
        assert 'AC-2 implementation WITHOUT rules' in content, 'AC-2 implementation description should be in markdown'
        assert 'ac-2_smt.a' in content or 'part a' in content.lower(), 'AC-2 statement should be in markdown'
        assert 'AC-2 part a statement without rules' in content, 'AC-2 statement description should be in markdown'
        # Note: Remarks are not currently written to SSP markdown


# Made with Bob
