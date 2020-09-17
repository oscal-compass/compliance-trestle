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
"""Starting point for the Trestle CLI."""

from ilcli import Command

from trestle.__init__ import __version__
from trestle.core.commands.add_cmd import Add
from trestle.core.commands.assemble_cmd import Assemble
from trestle.core.commands.create_cmd import Create
from trestle.core.commands.import_cmd import Import
from trestle.core.commands.init_cmd import Init
from trestle.core.commands.merge_cmd import Merge
from trestle.core.commands.replicate_cmd import Replicate
from trestle.core.commands.split_cmd import Split
from trestle.core.commands.validate_cmd import Validate


class Trestle(Command):
    """Manage OSCAL files in a human friendly manner."""

    subcommands = [Init, Create, Split, Merge, Replicate, Add, Validate, Import, Assemble]

    def _init_arguments(self):
        self.add_argument(
            '-V',
            '--version',
            help='Displays the version of trestle.',
            action='version',
            version=f'Trestle version v{__version__}'
        )
        self.add_argument('-v', '--verbose', help='Displays verbose output.', action='store_const', const=2, default=1)


def run():
    """Run the test cli."""
    exit(Trestle().run())


if __name__ == '__main__':
    run()
