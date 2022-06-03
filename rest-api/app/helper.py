# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2022 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""OSCAL REST API."""

from ruamel.yaml import YAML


class Helper():
    """Helper functions."""

    def __init__(self):
        """Initialize."""
        yaml = YAML(typ='safe')
        with open('./app.yaml', 'r') as f:
            self.config = yaml.load(f)

    def get_version(self):
        """Get version."""
        return self.config['app-version']


helper = Helper()
