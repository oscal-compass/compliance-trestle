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
"""Script reduces lists in the NIST 800-53 catalog to at most two elements."""

import argparse
import copy
import logging
import pathlib

import ilcli

import trestle.cli
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.oscal import catalog as oscatalog

logger = logging.getLogger(__name__)


def prune_lists(input_model: trestle.core.base_model.OscalBaseModel, list_cap: int) -> None:
    """Recurse down into models/dictionaries and prune lists down to N elements, where N is the given list_cap."""
    for _, v in input_model:
        fixed_cap = list_cap
        if isinstance(v, trestle.core.base_model.OscalBaseModel):
            prune_lists(v, list_cap)
        elif isinstance(v, list):
            if len(v) > fixed_cap:
                del v[-(len(v) - fixed_cap):]
            for x in range(len(v)):
                if isinstance(v[x], trestle.core.base_model.OscalBaseModel):
                    prune_lists(v[x], fixed_cap)


def add_needed_controls(input_model: oscatalog, main_cat: oscatalog) -> None:
    """Put back some of the original controls."""
    input_model.groups[0].controls = main_cat.groups[0].controls[:6]


class SimplifyCatalog(ilcli.Command):
    """
    Reduces lists in the NIST 800-53 catalog to at most two elements.

    This creates a simplified catalog with a number of ac controls left unchanged.
    Changes made here should be coordinated with the corresponding manually created simplified_nist_profile.json
    Currently this creates one group of controls and ideally it should be made a bit more complex than that.
    The Makefile invokes this script as rule simplified-catalog and creates the test file simplified_nist_catalog.json
    """

    def _init_arguments(self) -> None:
        self.add_argument('input', nargs=1, help='input json to read from')
        self.add_argument('output', nargs=1, help='output json to write to')
        self.add_argument('cap', nargs='?', type=int, default=None, help='max length of lists, default=2')

    def _run(self, args: argparse.Namespace) -> int:
        catalog_file = pathlib.Path(args.input[0])

        try:
            catalog = oscatalog.Catalog.oscal_read(catalog_file)
            orig_catalog = copy.deepcopy(catalog)
        except Exception as e:
            logger.error(f'Failure in oscal_read({catalog_file}): {e}\n')
            return CmdReturnCodes.COMMAND_ERROR.value

        if not catalog:
            logger.error('No data in input or input read failed.\n')
            return CmdReturnCodes.COMMAND_ERROR.value

        list_cap = args.cap if args.cap else 2
        try:
            prune_lists(input_model=catalog, list_cap=list_cap)
        except Exception as e:
            logger.error(f'Problem with prune_lists(): {e}\n')
            return CmdReturnCodes.COMMAND_ERROR.value

        simplified_catalog_file = pathlib.Path(args.output[0])

        add_needed_controls(catalog, orig_catalog)

        try:
            catalog.oscal_write(simplified_catalog_file)
        except Exception as e:
            logger.error(f'Problem with oscal_write: {e}\n')
            return CmdReturnCodes.COMMAND_ERROR.value

        return CmdReturnCodes.SUCCESS.value


if __name__ == '__main__':
    exit(SimplifyCatalog().run())
