# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Basic test script to test whether each reference in a json scema is referred to presuming there is one root model."""
import argparse
import json
import logging
import pathlib
import traceback
from typing import Any, Dict, List

from ilcli import Command

logger = logging.getLogger(__name__)


class IntegrityCmd(Command):
    """Run arbitrary trestle tasks in a simple and extensible methodology."""

    name = 'schema_integrity'

    def _init_arguments(self) -> None:
        self.add_argument('directory', nargs='?', type=str, help='Path to the directory for oscal schema')

    def _run(self, args: argparse.Namespace) -> int:
        try:
            dir_of_schemas = pathlib.Path(args.directory)
            for path_of_schema in dir_of_schemas.glob('oscal_*_schema.json'):
                self.out(f'Examinining: {path_of_schema.name}')
                fp = path_of_schema.open('r')
                json_schema_raw = json.load(fp)
                fp.close()
                # get list of ID's
                # Cannot use this technique using latest OSCAL code drop
                # ids = list(set(self.recursive_ref('$id', json_schema_raw))) # noqa: E800
                # get list of ID's only from the top level elements in the definition structure.
                definitions = json_schema_raw['definitions']

                ids = []
                for _, value in definitions.items():
                    for key, vals in value.items():
                        if key == '$id':
                            ids.append(vals)

                refs = list(set(self.recursive_ref('$ref', json_schema_raw)))

                for id_ex in ids:
                    if (id_ex not in refs) and (id_ex[0] == '#'):
                        self.out(f'id {id_ex} not in use')

            return 0
        except Exception:
            self.err('Failure of script')
            self.err(traceback.format_exc())
            return 1

    def recursive_ref(self, ref_key: str, dict_of_interest: Dict[str, Any]) -> List[str]:
        """Return all values for keys where you look recursively.

        presume key of interest has a consistent type value
        """
        returner = []

        for key, value in dict_of_interest.items():
            if key == ref_key:
                returner.append(value)
            elif type(value) == dict:
                returner = returner + self.recursive_ref(ref_key, value)
            elif type(value) == list:
                for item in value:
                    if type(item) == dict:
                        returner = returner + self.recursive_ref(ref_key, item)
                    elif key == ref_key:
                        returner.append(value)
        return returner


if __name__ == '__main__':
    exit(IntegrityCmd().run())
