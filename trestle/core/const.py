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

FIELDS_SET = '__fields_set__'

ROOT = '__root__'

PACKAGE_OSCAL = 'trestle.oscal'

TRESTLE_CONFIG_DIR = '.trestle'
TRESTLE_DIST_DIR = 'dist'
TRESTLE_CONFIG_FILE = 'config.ini'
TRESTLE_KEEP_FILE = '.keep'

# these are hyphenated - no underscore - and mixed singular and plural
MODEL_TYPE_A_PLAN = 'assessment-plan'
MODEL_TYPE_A_RESULT = 'assessment-results'
MODEL_TYPE_CATALOG = 'catalog'
MODEL_TYPE_COMPDEF = 'component-definition'
MODEL_TYPE_POAM = 'plan-of-action-and-milestones'
MODEL_TYPE_PROFILE = 'profile'
MODEL_TYPE_SSP = 'system-security-plan'

# these are all plural and hyphenated - no underscore
MODEL_DIR_A_PLAN = 'assessment-plans'
MODEL_DIR_A_RESULT = 'assessment-results'
MODEL_DIR_CATALOG = 'catalogs'
MODEL_DIR_COMPDEF = 'component-definitions'
MODEL_DIR_POAM = 'plan-of-action-and-milestones'
MODEL_DIR_PROFILE = 'profiles'
MODEL_DIR_SSP = 'system-security-plans'

# these are singular except for assessment_results - and component, poam, and ssp are all abbreviated
# underscores here instead of hyphens
MODULE_NAME_A_PLAN = 'assessment_plan'
MODULE_NAME_A_RESULT = 'assessment_results'
MODULE_NAME_CATALOG = 'catalog'
MODULE_NAME_COMPDEF = 'component'
MODULE_NAME_POAM = 'poam'
MODULE_NAME_PROFILE = 'profile'
MODULE_NAME_SSP = 'ssp'

MODEL_MODULE_A_PLAN = f'{PACKAGE_OSCAL}.{MODULE_NAME_A_PLAN}'
MODEL_MODULE_A_RESULT = f'{PACKAGE_OSCAL}.{MODULE_NAME_A_RESULT}'
MODEL_MODULE_CATALOG = f'{PACKAGE_OSCAL}.{MODULE_NAME_CATALOG}'
MODEL_MODULE_COMPDEF = f'{PACKAGE_OSCAL}.{MODULE_NAME_COMPDEF}'
MODEL_MODULE_POAM = f'{PACKAGE_OSCAL}.{MODULE_NAME_POAM}'
MODEL_MODULE_PROFILE = f'{PACKAGE_OSCAL}.{MODULE_NAME_PROFILE}'
MODEL_MODULE_SSP = f'{PACKAGE_OSCAL}.{MODULE_NAME_SSP}'

MODEL_TYPE_LIST = [
    MODEL_TYPE_A_PLAN,
    MODEL_TYPE_A_RESULT,
    MODEL_TYPE_CATALOG,
    MODEL_TYPE_COMPDEF,
    MODEL_TYPE_POAM,
    MODEL_TYPE_PROFILE,
    MODEL_TYPE_SSP
]

MODEL_DIR_LIST = [
    MODEL_DIR_A_PLAN,
    MODEL_DIR_A_RESULT,
    MODEL_DIR_CATALOG,
    MODEL_DIR_COMPDEF,
    MODEL_DIR_POAM,
    MODEL_DIR_PROFILE,
    MODEL_DIR_SSP
]

MODEL_MODULE_LIST = [
    MODEL_MODULE_A_PLAN,
    MODEL_MODULE_A_RESULT,
    MODEL_MODULE_CATALOG,
    MODEL_MODULE_COMPDEF,
    MODEL_MODULE_POAM,
    MODEL_MODULE_PROFILE,
    MODEL_MODULE_SSP
]
"""Map of plural form of a model type to the oscal module that contains the classes related to it."""
MODEL_DIR_TO_MODEL_MODULE = {
    MODEL_DIR_A_PLAN: MODEL_MODULE_A_PLAN,
    MODEL_DIR_A_RESULT: MODEL_MODULE_A_RESULT,
    MODEL_DIR_CATALOG: MODEL_MODULE_CATALOG,
    MODEL_DIR_COMPDEF: MODEL_MODULE_COMPDEF,
    MODEL_DIR_POAM: MODEL_MODULE_POAM,
    MODEL_DIR_PROFILE: MODEL_MODULE_PROFILE,
    MODEL_DIR_SSP: MODEL_MODULE_SSP
}
"""Map of model type to oscal module."""
MODEL_TYPE_TO_MODEL_MODULE = {
    MODEL_TYPE_A_PLAN: MODEL_MODULE_A_PLAN,
    MODEL_TYPE_A_RESULT: MODEL_MODULE_A_RESULT,
    MODEL_TYPE_CATALOG: MODEL_MODULE_CATALOG,
    MODEL_TYPE_COMPDEF: MODEL_MODULE_COMPDEF,
    MODEL_TYPE_POAM: MODEL_MODULE_POAM,
    MODEL_TYPE_PROFILE: MODEL_MODULE_PROFILE,
    MODEL_TYPE_SSP: MODEL_MODULE_SSP
}
"""Map of model module to model type."""
MODEL_MODULE_TO_MODEL_TYPE = {
    MODEL_MODULE_A_PLAN: MODEL_TYPE_A_PLAN,
    MODEL_MODULE_A_RESULT: MODEL_TYPE_A_RESULT,
    MODEL_MODULE_CATALOG: MODEL_TYPE_CATALOG,
    MODEL_MODULE_COMPDEF: MODEL_TYPE_COMPDEF,
    MODEL_MODULE_POAM: MODEL_TYPE_POAM,
    MODEL_MODULE_PROFILE: MODEL_TYPE_PROFILE,
    MODEL_MODULE_SSP: MODEL_TYPE_SSP
}
"""Map of model type to model directory."""
MODEL_TYPE_TO_MODEL_DIR = {
    MODEL_TYPE_A_PLAN: MODEL_DIR_A_PLAN,
    MODEL_TYPE_A_RESULT: MODEL_DIR_A_RESULT,
    MODEL_TYPE_CATALOG: MODEL_DIR_CATALOG,
    MODEL_TYPE_COMPDEF: MODEL_DIR_COMPDEF,
    MODEL_TYPE_POAM: MODEL_DIR_POAM,
    MODEL_TYPE_PROFILE: MODEL_DIR_PROFILE,
    MODEL_TYPE_SSP: MODEL_DIR_SSP
}
"""Element path separator"""
ALIAS_PATH_SEPARATOR: str = '.'

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

DISPLAY_VERBOSE_OUTPUT = 'Display verbose output'

HELP_YAML_PATH = 'Path to the optional yaml header file'

HELP_PRESERVE_HEADER_VALUES = (
    'Flag to preserve values in a markdown control header.'
    + ' If provided, if a header currently exists the new header, passed with -y, will not change any existing'
    + ' values set in the header.  But new items passed in will always be added to the header read in.'
)

HELP_REGENERATE = 'Flag to force generation of new uuids in the model'

HELP_MARKDOWN_NAME = 'Name of the output generated profile markdown folder'

FILTER_BY_PROFILE = 'filter-by-profile'

FILTER_BY_COMPONENTS = 'filter-by-components'

FILTER_EXCLUDE_COMPONENTS = 'filter-exclude-components'

GENERATE_RESOLVED_CATALOG = 'generate-resolved-catalog'

TRANSFORM_TYPES = [FILTER_BY_PROFILE, FILTER_BY_COMPONENTS, FILTER_EXCLUDE_COMPONENTS, GENERATE_RESOLVED_CATALOG]

SSP_MAIN_COMP_NAME = 'This System'

TRESTLE_TAG = 'x-trestle-'

SSP_FEDRAMP_TAG = 'x-trestle-fedramp-props'

NAMESPACE_FEDRAMP = 'https://fedramp.gov/ns/oscal'

CONTROL_ORIGINATION = 'control-origination'

IMPLEMENTATION_STATUS = 'implementation-status'

RESPONSIBLE_ROLE = 'responsible-role'

RESPONSIBLE_ROLES = 'responsible-roles'

INHERITED = 'inherited'

LEV_AUTH_UUID = 'leveraged-authorization-uuid'

PLANNED = 'planned'

PLANNED_COMPLETION_DATE = 'planned-completion-date'

COMPLETION_DATE = 'completion-date'

HELP_SET_PARAMS = 'set profile parameter values based on the yaml header in control markdown'

SET_PARAMS_TAG = 'x-trestle-set-params'
