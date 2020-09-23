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

TRESTLE_CONFIG_DIR = '.trestle'
TRESTLE_DIST_DIR = 'dist'
TRESTLE_MODEL_DIRS = [
    'catalogs',
    'profiles',
    'target-definitions',
    'component-definitions',
    'system-security-plans',
    'assessment-plans',
    'assessment-results',
    'plan-of-action-and-milestones'
]
TRESTLE_CONFIG_FILE = 'config.ini'

# list key to model name
# This is usually a map from plural names to singular
# However, there could be special cases and therefore we are maintaining this mapping here
LIST_KEY_TO_MODEL_NAME = {
    'groups': 'group',
    'controls': 'control',
    'targets': 'target',
    'target-control-implementations': 'target-control-implementation'
}

PACKAGE_OSCAL = 'trestle.oscal'
