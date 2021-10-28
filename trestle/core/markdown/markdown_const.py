# -*- mode:python; coding:utf-8 -*-

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
"""Markdown specific constants."""

BLOCKQUOTE_CHAR = '>'
CODEBLOCK_DEF = '```'
HEADER_REGEX = r'^[#]+'
INLINE_CODE_CHAR = r'^`'
LIST_CHAR = '-'
TABLE_SYMBOL = '|'
HTML_COMMENT_START = '<!--'
HTML_COMMENT_END_REGEX = r'.*-->'
HTML_TAG_REGEX_START = r'^[ \t]*<.*>'
HTML_TAG_REGEX_END = r'<\/.*>'
TABLE_REGEX = r'|'
GOVERNED_DOC_REGEX = r'.*:'
SUBSTITUTION_REGEX = r'{(.*?)}'  # noqa: FS003
