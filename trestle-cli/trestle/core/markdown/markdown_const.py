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
GOVERNED_DOC_REGEX = r'.*:'
HEADER_REGEX = r'^[#]+'
HTML_COMMENT_START = '<!--'
HTML_COMMENT_END_REGEX = r'.*-->'
HTML_TAG_REGEX_START = r'^[ \t]*<.*>'
HTML_TAG_REGEX_END = r'<\/.*>'
INLINE_CODE_CHAR = r'^`'
JINJA_DATESTAMP_FORMAT = '%Y-%m-%d'
LIST_CHAR = '-'
SUBSTITUTION_REGEX = r'{(.*?)}'  # noqa: FS003
TABLE_REGEX = r'|'
TABLE_SYMBOL = '|'
