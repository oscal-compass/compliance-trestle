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

DIR_TRESTLE = '_trestle'
DIR_TRESTLE_BACKUP = f'{DIR_TRESTLE}/backup'
DIR_TRESTLE_DIST = f'{DIR_TRESTLE}/dist'

# list key to model name
# This is usually a map from plural names to singular
# However, there could be special cases and therefore we are maintaining this mapping here
LIST_KEY_TO_MODEL_NAME = {
    'groups': 'group',
    'controls': 'control',
}

ALLOWED_MODELS_FOR_SPLIT = LIST_KEY_TO_MODEL_NAME.keys()

PACKAGE_OSCAL = 'trestle.oscal'
