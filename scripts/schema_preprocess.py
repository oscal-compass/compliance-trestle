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
"""Script to generate python models from oscal using datamodel-code-generator."""
import logging
import os
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def fixup_models(input_dir_name: str) -> Path:
    """Fix models."""
    fixup_dir_name = f'{input_dir_name}-fixup'
    input_dir_path = Path(input_dir_name)
    fixup_dir_path = Path(fixup_dir_name)
    fixup_dir_path.mkdir(exist_ok=True, parents=True)
    for full_name in input_dir_path.glob('oscal_*_schema.json'):
        model_name = str(full_name)
        if 'complete' in model_name:
            continue
        if 'component_schema' in model_name:
            fixup_component_schema(model_name, fixup_dir_path)
        else:
            fixup_copy(model_name, fixup_dir_path)
    return fixup_dir_path


def fixup_copy(model_name: str, fixup_dir_path: Path) -> None:
    """Fixup copy - no changes needed."""
    cmd = f'cp -p {model_name} {str(fixup_dir_path)}'
    logger.debug(cmd)
    os.system(cmd)


def fixup_component_schema(model_name: str, fixup_dir_path: Path) -> None:
    """Fixup component schema."""
    model_path = Path(model_name)
    model_file = model_path.name
    fixup_path = fixup_dir_path / model_file
    # move location of embedded metadata stanza, to be compatible with the other models
    lines = []
    relocate = []
    # ingest original
    with open(model_name, 'r') as f:
        mode = 'keep'
        while line := f.readline():
            if '"oscal-component-definition-oscal-metadata:metadata" :' in line:
                mode = 'delete'
            elif '"oscal-component-definition-oscal-control-common:part" : ' in line:
                mode = 'keep'
            if 'keep' in mode:
                lines.append(line)
            else:
                # delete
                relocate.append(line)
    # rewrite revised
    with open(fixup_path, 'w') as f:
        for line in lines:
            if '"oscal-component-definition-oscal-component-definition:import-component-definition" : ' in line:
                # insert
                for item in relocate:
                    f.write(item)
            f.write(line)
    text = f'fixup {model_name} -> {str(fixup_path)}'
    logger.info(text)

