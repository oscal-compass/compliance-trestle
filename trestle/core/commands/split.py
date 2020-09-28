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
"""Trestle Split Command."""

from ilcli import Command

from trestle.core import const


class SplitCmd(Command):
    """Split subcomponents on a trestle model."""

    name = 'split'

    def _init_arguments(self):
        self.add_argument(
            '-f',
            '--file',
            help=const.ARG_DESC_FILE + ' to split.',
        )
        self.add_argument(
            '-e',
            '--element',
            help=const.ARG_DESC_ELEMENT + ' to split.',
        )

    def _run(self, args):
        """Split an OSCAL file into elements."""
