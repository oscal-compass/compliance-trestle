# -*- mode:python; coding:utf-8 -*-

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
"""Core constants module containing all constants."""

import string

PACKAGE_OSCAL = 'trestle.oscal'

TRESTLE_CONFIG_DIR = '.trestle'
TRESTLE_DIST_DIR = 'dist'
TRESTLE_CONFIG_FILE = 'config.ini'
TRESTLE_KEEP_FILE = '.keep'
"""Map of plural form of a model type to the oscal module that contains the classes related to it."""
MODEL_DIR_TO_MODEL_MODULE = {
    'catalogs': f'{PACKAGE_OSCAL}.catalog',
    'profiles': f'{PACKAGE_OSCAL}.profile',
    'component-definitions': f'{PACKAGE_OSCAL}.component',
    'system-security-plans': f'{PACKAGE_OSCAL}.ssp',
    'assessment-plans': f'{PACKAGE_OSCAL}.assessment_plan',
    'assessment-results': f'{PACKAGE_OSCAL}.assessment_results',
    'plan-of-action-and-milestones': f'{PACKAGE_OSCAL}.poam'
}
MODEL_TYPE_TO_MODEL_MODULE = {
    'catalog': f'{PACKAGE_OSCAL}.catalog',
    'profile': f'{PACKAGE_OSCAL}.profile',
    'component-definition': f'{PACKAGE_OSCAL}.component',
    'system-security-plan': f'{PACKAGE_OSCAL}.ssp',
    'assessment-plan': f'{PACKAGE_OSCAL}.assessment_plan',
    'assessment-results': f'{PACKAGE_OSCAL}.assessment_results',
    'plan-of-action-and-milestones': f'{PACKAGE_OSCAL}.poam'
}
MODEL_TYPE_TO_MODEL_DIR = {
    'catalog': 'catalogs',
    'profile': 'profiles',
    'component-definition': 'component-definitions',
    'system-security-plan': 'system-security-plans',
    'assessment-plan': 'assessment-plans',
    'assessment-results': 'assessment-results',
    'plan-of-action-and-milestones': 'plan-of-action-and-milestones'
}
"""Element path separator"""
ALIAS_PATH_SEPARATOR: str = '.'

MODEL_TYPE_LIST = [
    'catalog',
    'profile',
    'component-definition',
    'system-security-plan',
    'assessment-plan',
    'assessment-results',
    'plan-of-action-and-milestones'
]

MODEL_DIR_LIST = [
    'catalogs',
    'profiles',
    'component-definitions',
    'system-security-plans',
    'assessment-plans',
    'assessment-results',
    'plan-of-action-and-milestones',
]

# argument names
ARG_FILE = 'file'
ARG_FILE_SHORT = 'f'

ARG_ELEMENT = 'element'
ARG_ELEMENT_SHORT = 'e'

# argument descriptions
ARG_DESC_FILE = 'Path of the file'
ARG_DESC_ELEMENT = 'Path of the element in the OSCAL model'

# Index separater for naming directories representing collection properties
IDX_SEP = '__'

# Digit prefix for split files
FILE_DIGIT_PREFIX_LENGTH = 5

# Wildcard that can be used in the element path to represent all elements
ELEMENT_WILDCARD = '*'
ARG_VALIDATE = 'validate'
ARG_VALIDATE_SHORT = 'v'

ARG_MODE = 'mode'
ARG_MODE_SHORT = 'm'
ARG_DESC_MODE = 'Mode of the operation'

ARG_ITEM = 'item'
ARG_ITEM_SHORT = 'i'
ARG_DESC_ITEM = 'Item used'

VAL_MODE_DUPLICATES = 'duplicates'
VAL_MODE_REFS = 'refs'
VAL_MODE_ALL = 'all'
VAL_MODE_OSCAL_VERSION = 'oscal_version'

IOF_SHORT = '-iof'
IOF_LONG = '--include-optional-fields'
IOF_HELP = 'Include fields that are optional in the OSCAL model when generating the new object.'

FILE_ENCODING = 'utf8'

# ESCAPE CHARACTERS FOR MD heads
HEADER_L_ESCAPE = '{'
HEADER_R_ESCAPE = '}'

# Trestle documentation

WEBSITE_ROOT = 'https://ibm.github.io/compliance-trestle'

BUG_REPORT = 'https://github.com/IBM/compliance-trestle/issues/new/choose'

# Sample objects
SAMPLE_UUID_STR = 'A0000000-0000-4000-8000-000000000000'

WINDOWS_PLATFORM_STR = 'Windows'

# constants related to cache

TRESTLE_CACHE_DIR = TRESTLE_CONFIG_DIR + '/cache'

HOUR_SECONDS: int = 3600

DAY_SECONDS: int = 24 * HOUR_SECONDS

FILE_URI = 'file:///'

SFTP_URI = 'sftp://'

HTTPS_URI = 'https://'

# extracts letter, colon and single slash
WINDOWS_DRIVE_URI_REGEX = r'([A-Za-z]:[\\/]?)[^\\/]'

WINDOWS_DRIVE_LETTER_REGEX = r'[A-Za-z]:'

CACHE_ABS_DIR = '__abs__'

UNIX_CACHE_ROOT = '__root__'

TRESTLE_HREF_HEADING = 'trestle://'

TRESTLE_HREF_REGEX = '^trestle://[^/]'

# extracts foo and bar from ...[foo](bar)...
MARKDOWN_URL_REGEX = r'\[([^\]]+)\]\(([^)]+)\)'

# extracts standalone uuid's from anywhere in string
UUID_REGEX = r'(?:^|[0-9A-Za-f])([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12})(?:$|[^0-9A-Za-z])'  # noqa FS003 E501

SSP_MD_HRULE_LINE = '______________________________________________________________________'

SSP_MD_IMPLEMENTATION_QUESTION = 'What is the solution and how is it implemented?'

SSP_MD_LEAVE_BLANK_TEXT = '<!-- Please leave this section blank and enter implementation details in the parts below. -->'  # noqa E501

SSP_ADD_IMPLEMENTATION_PREFIX = 'Add control implementation description here for '

SSP_ADD_IMPLEMENTATION_FOR_STATEMENT_TEXT = SSP_ADD_IMPLEMENTATION_PREFIX + 'statement'

SSP_ADD_IMPLEMENTATION_FOR_ITEM_TEXT = SSP_ADD_IMPLEMENTATION_PREFIX + 'item'

SSP_ADD_IMPLEMENTATION_FOR_CONTROL_TEXT = SSP_ADD_IMPLEMENTATION_PREFIX + 'control'

SSP_SYSTEM_CONTROL_IMPLEMENTATION_TEXT = 'This is the control implementation for the system.'

NCNAME_REGEX = r'^[_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][_A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-\.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$'  # noqa FS003 E501

NCNAME_UTF8_FIRST_CHAR_OPTIONS = string.ascii_letters + '_'

NCNAME_UTF8_OTHER_CHAR_OPTIONS = string.ascii_letters + string.digits + '_.-'
