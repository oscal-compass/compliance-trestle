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
"""Core constants module containing all constants."""

PACKAGE_OSCAL = 'trestle.oscal'

TRESTLE_CONFIG_DIR = '.trestle'
TRESTLE_DIST_DIR = 'dist'
TRESTLE_CONFIG_FILE = 'config.ini'
TRESTLE_KEEP_FILE = '.keep'
"""Map of plural form of a model type to the oscal module that contains the classes related to it."""
MODEL_TYPE_TO_MODEL_MODULE = {
    'catalogs': f'{PACKAGE_OSCAL}.catalog',
    'profiles': f'{PACKAGE_OSCAL}.profile',
    'component-definitions': f'{PACKAGE_OSCAL}.component',
    'system-security-plans': f'{PACKAGE_OSCAL}.ssp',
    'assessment-plans': f'{PACKAGE_OSCAL}.assessment_plan',
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

WINDOWS_DRIVE_URI_REGEX = r'([A-Za-z]:[\\/]?)[^\\/]'

WINDOWS_DRIVE_LETTER_REGEX = r'[A-Za-z]:'

CACHE_ABS_DIR = '__abs__'

UNIX_CACHE_ROOT = '__root__'

TRESTLE_HREF_HEADING = 'trestle://'

TRESTLE_HREF_REGEX = '^trestle://[^/]'
