# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2026 The OSCAL Compass Authors.
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
"""Trestle core.jinja sanitization of untrusted text."""


def neutralize_jinja_delimiters(text: str) -> str:
    """Neutralize Jinja2 template delimiters to prevent SSTI attacks.

    Replaces {{ and }} with [[ and ]], and the statement ({%) and comment ({#)
    openers with [% and [#, to prevent untrusted OSCAL data from being
    interpreted as Jinja2 template code when included in markdown files that
    are later processed by Jinja2 include tags.

    Statement tags must be neutralized as well as expressions because a sandboxed
    environment still permits tags such as include and for, which allow in-tree
    file disclosure and output amplification.

    Args:
        text: The text to neutralize

    Returns:
        Text with Jinja delimiters replaced
    """
    if not text:
        return text
    return text.replace('{{', '[[').replace('}}', ']]').replace('{%', '[%').replace('{#', '[#')
