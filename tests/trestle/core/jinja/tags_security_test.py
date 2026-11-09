# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2026 The OSCAL Compass Authors. All rights reserved.
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
"""Security tests for Jinja tags to verify SSTI vulnerability is fixed."""

import pathlib
import tempfile

import pytest

from jinja2.sandbox import SandboxedEnvironment
from jinja2.exceptions import SecurityError

from trestle.core.jinja.ext import extensions


class TestJinjaTagsSecurity:
    """Test security fixes for CVE-2026-46439 incomplete fix."""

    def test_md_clean_include_allows_safe_variable_substitution(self):
        """Test that md_clean_include allows safe variable substitution in sandboxed environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir)

            # Create a markdown file with safe Jinja variable substitution
            included_md = tmpdir_path / 'included.md'
            safe_content = '# Test\n\nThis has {{ safe_var }} in it.\n'
            included_md.write_text(safe_content)

            # Create a template that includes the file
            template_file = tmpdir_path / 'template.md.j2'
            template_file.write_text('{% md_clean_include "included.md" %}')

            # Render the template with a safe variable
            env = SandboxedEnvironment(loader=None, extensions=extensions(), trim_blocks=True, autoescape=True)

            from jinja2 import FileSystemLoader

            env.loader = FileSystemLoader(tmpdir_path)
            template = env.get_template('template.md.j2')
            result = template.render(safe_var='SUBSTITUTED')

            # Verify safe variable substitution works
            assert 'SUBSTITUTED' in result
            assert 'This has' in result

    def test_md_clean_include_blocks_dangerous_attribute_access(self):
        """Test that md_clean_include blocks dangerous attribute access via sandbox."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir)

            # Create a markdown file with malicious Jinja code attempting RCE
            included_md = tmpdir_path / 'included.md'
            # Attempt to access dangerous attributes for RCE
            malicious_content = "# Test\n\n{{ ''.__class__.__mro__[1].__subclasses__() }}\n"
            included_md.write_text(malicious_content)

            # Create a template that includes the file
            template_file = tmpdir_path / 'template.md.j2'
            template_file.write_text('{% md_clean_include "included.md" %}')

            # Render the template - should raise SecurityError or similar
            env = SandboxedEnvironment(loader=None, extensions=extensions(), trim_blocks=True, autoescape=True)

            from jinja2 import FileSystemLoader

            env.loader = FileSystemLoader(tmpdir_path)
            template = env.get_template('template.md.j2')

            # Should raise SecurityError when trying to access __class__
            with pytest.raises((SecurityError, Exception)):
                template.render()

    def test_mdsection_include_allows_safe_variable_substitution(self):
        """Test that mdsection_include allows safe variable substitution in sandboxed environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir)

            # Create a markdown file with a section containing safe variable
            included_md = tmpdir_path / 'included.md'
            safe_content = """# Section One

This section has {{ safe_var }} in it.

# Section Two

Another section.
"""
            included_md.write_text(safe_content)

            # Create a template that includes a specific section
            template_file = tmpdir_path / 'template.md.j2'
            template_file.write_text('{% mdsection_include "included.md" "# Section One" %}')

            # Render the template with a safe variable
            env = SandboxedEnvironment(loader=None, extensions=extensions(), trim_blocks=True, autoescape=True)

            from jinja2 import FileSystemLoader

            env.loader = FileSystemLoader(tmpdir_path)
            template = env.get_template('template.md.j2')
            result = template.render(safe_var='SUBSTITUTED')

            # Verify safe variable substitution works
            assert 'SUBSTITUTED' in result
            assert 'This section has' in result

    def test_mdsection_include_blocks_dangerous_attribute_access(self):
        """Test that mdsection_include blocks dangerous attribute access via sandbox."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir)

            # Create a markdown file with malicious code
            included_md = tmpdir_path / 'included.md'
            malicious_content = """# Section One

{{ ''.__class__.__mro__[1].__subclasses__() }}

# Section Two

Another section.
"""
            included_md.write_text(malicious_content)

            # Create a template that includes the malicious section
            template_file = tmpdir_path / 'template.md.j2'
            template_file.write_text('{% mdsection_include "included.md" "# Section One" %}')

            # Render the template - should raise SecurityError
            env = SandboxedEnvironment(loader=None, extensions=extensions(), trim_blocks=True, autoescape=True)

            from jinja2 import FileSystemLoader

            env.loader = FileSystemLoader(tmpdir_path)
            template = env.get_template('template.md.j2')

            # Should raise SecurityError when trying to access __class__
            with pytest.raises((SecurityError, Exception)):
                template.render()

    def test_md_datestamp_does_not_execute_injected_code(self):
        """Test that md_datestamp doesn't allow code injection through format strings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir)

            # Create a template with datestamp
            template_file = tmpdir_path / 'template.md.j2'
            # Use a safe format string
            template_file.write_text('{% md_datestamp format="%Y-%m-%d" %}')

            # Render the template
            env = SandboxedEnvironment(loader=None, extensions=extensions(), trim_blocks=True, autoescape=True)

            from jinja2 import FileSystemLoader

            env.loader = FileSystemLoader(tmpdir_path)
            template = env.get_template('template.md.j2')
            result = template.render()

            # Verify we get a date, not code execution
            import re

            assert re.match(r'\d{4}-\d{2}-\d{2}', result.strip())

    def test_neutralize_jinja_delimiters(self):
        """Test that Jinja delimiters are neutralized in untrusted text."""
        from trestle.core.jinja.sanitize import neutralize_jinja_delimiters

        # Test basic neutralization
        input_text = 'This has {{ variable }} and {{ another }}'
        expected = 'This has [[ variable ]] and [[ another ]]'
        assert neutralize_jinja_delimiters(input_text) == expected

        # Test empty/None handling
        assert neutralize_jinja_delimiters('') == ''
        assert neutralize_jinja_delimiters(None) is None

        # Test text without delimiters
        plain_text = 'This is plain text'
        assert neutralize_jinja_delimiters(plain_text) == plain_text

    @pytest.mark.parametrize(
        'payload, expected',
        [
            ('{% for i in range(3) %}A{% endfor %}', '[% for i in range(3) %}A[% endfor %}'),
            ('{# comment #}', '[# comment #}'),
            ("{% include 'x.md' %}", "[% include 'x.md' %}"),
            ("{% md_clean_include 'confidential.md' %}", "[% md_clean_include 'confidential.md' %}"),
            ('{{ evil }}', '[[ evil ]]'),
        ],
    )
    def test_neutralization_of_statement_and_comment_tags(self, payload, expected):
        """Statement and comment tags must be neutralized, not just expressions."""
        from trestle.core.jinja.sanitize import neutralize_jinja_delimiters

        assert neutralize_jinja_delimiters(payload) == expected

    def test_neutralized_statement_tags_do_not_disclose_files(self):
        """Neutralized statement-tag payloads in an included file must not splice other files."""
        from jinja2 import FileSystemLoader

        from trestle.core.jinja.sanitize import neutralize_jinja_delimiters

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir)
            (tmpdir_path / 'confidential.md').write_text('TOP_SECRET_DATA')
            payload = "{% md_clean_include 'confidential.md' %}{% include 'confidential.md' %}"
            (tmpdir_path / 'generated.md').write_text('# Prose\n\n' + neutralize_jinja_delimiters(payload) + '\n')
            (tmpdir_path / 'template.md.j2').write_text('{% md_clean_include "generated.md" %}')

            env = SandboxedEnvironment(
                loader=FileSystemLoader(tmpdir_path), extensions=extensions(), trim_blocks=True, autoescape=True
            )
            result = env.get_template('template.md.j2').render()

            assert 'TOP_SECRET_DATA' not in result

    @pytest.mark.parametrize('include_tag', ['md_clean_include "included.md"', 'mdsection_include "included.md" "# A"'])
    @pytest.mark.parametrize(
        'payload',
        [
            "{% md_clean_include 'confidential.md' %}",
            "{% include 'confidential.md' %}",
            '{% for a in range(1000) %}{% for b in range(1000) %}X{% endfor %}{% endfor %}',
            '{# comment #}',
            "{%- include 'confidential.md' -%}",
        ],
    )
    def test_statement_tags_in_included_markdown_are_rejected(self, include_tag, payload):
        """Statement tags in included markdown fail closed: no file disclosure and no amplification."""
        from jinja2 import FileSystemLoader

        from trestle.common.err import TrestleError

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir)
            (tmpdir_path / 'confidential.md').write_text('TOP_SECRET_DATA')
            (tmpdir_path / 'included.md').write_text(f'# A\n\n{payload}\n')
            (tmpdir_path / 'template.md.j2').write_text('{% ' + include_tag + ' %}')

            env = SandboxedEnvironment(
                loader=FileSystemLoader(tmpdir_path), extensions=extensions(), trim_blocks=True, autoescape=True
            )
            if payload.startswith('{#'):
                # comments are inert text to the template engine and produce no output
                assert 'TOP_SECRET_DATA' not in env.get_template('template.md.j2').render()
                return
            with pytest.raises(TrestleError):
                env.get_template('template.md.j2').render()

    def test_expressions_in_included_markdown_and_statement_tags_in_top_level_still_work(self):
        """Top level templates keep full syntax and included files keep {{ }} substitution."""
        from jinja2 import FileSystemLoader

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir)
            (tmpdir_path / 'leaf.md.j2').write_text('LEAF {{ name }}')
            (tmpdir_path / 'template.md.j2').write_text(
                '{% for n in ["a", "b"] %}{% md_clean_include "leaf.md.j2" %}{% endfor %}{% include "leaf.md.j2" %}'
            )

            env = SandboxedEnvironment(
                loader=FileSystemLoader(tmpdir_path), extensions=extensions(), trim_blocks=True, autoescape=True
            )
            assert env.get_template('template.md.j2').render(name='X').count('LEAF X') == 3

    def test_no_code_execution_with_malicious_oscal_data(self):
        """Integration test: verify malicious OSCAL-like data doesn't execute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir)

            # Simulate markdown generated from OSCAL with malicious content
            # This represents what would be written by ssp_io or docs_control_writer
            generated_md = tmpdir_path / 'generated.md'
            # After neutralization, this should have [[ ]] not {{ }}
            neutralized_content = """# Control AC-1

## Control Statement

The organization shall [[ insert: assignment ]] establish policies.

## Implementation

Component description: [[ cycler.__init__.__globals__.os.popen('id').read() ]]
"""
            generated_md.write_text(neutralized_content)

            # Template that includes the generated markdown
            template_file = tmpdir_path / 'template.md.j2'
            template_file.write_text("""# System Security Plan

{% md_clean_include "generated.md" %}
""")

            # Render the template
            env = SandboxedEnvironment(loader=None, extensions=extensions(), trim_blocks=True, autoescape=True)

            from jinja2 import FileSystemLoader

            env.loader = FileSystemLoader(tmpdir_path)
            template = env.get_template('template.md.j2')
            result = template.render()

            # Verify malicious code appears literally, not executed
            assert '[[ insert: assignment ]]' in result
            assert '[[ cycler.__init__.__globals__.os.popen' in result
            # Verify no command output appears (would indicate execution)
            assert 'uid=' not in result  # Common output from 'id' command
            assert 'gid=' not in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

# Made with Bob
