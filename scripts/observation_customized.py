# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""
This script creates the IBM custom interchange json schema.

It uses an observations list to convey results from some source collection.
The default output target is either (/dev/)stdout or, if that does not exists,
e.g., in Windows environments, then save to file ./output.json.

Arguments:
output_file: str
    Indicates the file to write the schema to.
    If omitted, defaults to /dev/stdout or, if that does not exist, ./output.json.
schema_title: str (optional)
    The title to set. If omitted, a default is used.
"""
import argparse
import json
import pathlib
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from trestle.oscal.assessment_results import Metadata
from trestle.oscal.assessment_results import Observation
from trestle.oscal.assessment_results import Remediation
from trestle.oscal.ssp import SetParameter


class Observation(Observation):
    """This is a custom Observation class for IBM interchange purposes.

    It is extended with remediation_group and parameter_settings properties.
    """

    remediation_group: Optional[List[Remediation]] = Field(..., alias='remediation-group')
    parameter_settings: Dict[str, SetParameter] = Field(None, alias='parameter-settings')


class IBMObservationsInterchange(BaseModel):
    """This is the OSCAL-like interchange class."""

    observations: List[Observation] = ...
    metadata: Metadata = Field(None, alias='metadata')


preferred_title = 'ibm_observations_interchange'
default_output = '/dev/stdout' if pathlib.Path('/dev/stdout').exists() else './output.json'

parser = argparse.ArgumentParser(description='Generate custom schema.')
parser.add_argument(
    '--out',
    dest='output_file',
    action='store',
    default=default_output,
    help=f'output target for schema, defaults to {default_output} if omitted'
)
parser.add_argument(
    '--title',
    dest='schema_title',
    action='store',
    default=preferred_title,
    help=f'title for schema, defaults to "{preferred_title}" if omitted'
)
args = parser.parse_args()

interchange_schema_dict = json.loads(IBMObservationsInterchange.schema_json())
interchange_schema_dict['title'] = args.schema_title

outfile = open(args.output_file, 'w')
try:
    outfile.write(json.dumps(interchange_schema_dict, indent=4))
except Exception as err:
    raise err.Exception(f'Error writing out to: {args.output_file}')
outfile.close()
