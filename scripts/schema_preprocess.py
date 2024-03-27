# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2024 IBM Corp. All rights reserved.
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
"""Script to pre-process OSCAL schemas."""
import json
import logging
import os
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def fixup_models(input_dir_name: str) -> Path:
    """Fix models."""
    fixup_dir_name = f'{input_dir_name}-fixup'
    input_dir_path = Path(input_dir_name)
    fixup_dir_path = Path(fixup_dir_name)
    fixup_dir_path.mkdir(exist_ok=True, parents=True)
    fixup_copy_schemas(input_dir_path, fixup_dir_path)
    fixup_json(fixup_dir_path)
    return fixup_dir_path


def json_data_get(model_name: str) -> Dict:
    """Get json data."""
    with open(model_name, 'r') as f:
        data = json.load(f)
    return data


def json_data_put(model_name: str, data: Dict) -> None:
    """Put json data."""
    with open(model_name, 'w') as f:
        json_object = json.dumps(data, indent=2)
        f.write(json_object)


def fixup_json(fixup_dir_path: Path) -> None:
    """Fixup json."""
    for full_name in fixup_dir_path.glob('oscal_*_schema.json'):
        model_name = str(full_name)
        data = json_data_get(model_name)
        move_metadata(data)
        assign_labels(data)
        json_data_put(model_name, data)


def assign_labels(data: Dict) -> None:
    """Assign labels."""
    if 'oscal-poam-oscal-poam:plan-of-action-and-milestones' in data['definitions'].keys():
        key = 'oscal-poam-oscal-assessment-common:assessment-subject'
        val = {'enum': ['component', 'inventory-item', 'location', 'party', 'user']}
        id_ = 'Type4'
        try:
            item = data['definitions'][key]['properties']['type']['anyOf'][1]
            if item == val:
                val = {id_: val}
                data['definitions'][key]['properties']['type']['anyOf'][1] = val
                logger.debug(f'{key} -> {val}')
        except Exception:
            logger.warning(f'Unable to assign {key}')


def move_metadata(data: Dict) -> None:
    """Move metadata."""
    if 'oscal-component-definition-oscal-component-definition:component-definition' in data['definitions'].keys():
        desc1 = {}
        desc2 = {}
        desc3 = {}
        for key in data['definitions'].keys():
            if key == 'json-schema-directive':
                desc1[key] = data['definitions'][key]
            elif key == 'oscal-component-definition-oscal-component-definition:component-definition':
                desc1[key] = data['definitions'][key]
            elif 'oscal-component-definition-oscal-metadata:' in key:
                desc2[key] = data['definitions'][key]
            else:
                desc3[key] = data['definitions'][key]
        data['definitions'] = {}
        for key in desc1.keys():
            data['definitions'][key] = desc1[key]
        for key in desc2.keys():
            data['definitions'][key] = desc2[key]
        for key in desc3.keys():
            data['definitions'][key] = desc3[key]


def fixup_copy_schemas(input_dir_path: Path, fixup_dir_path: Path) -> None:
    """Fixup copy schemas."""
    for full_name in input_dir_path.glob('oscal_*_schema.json'):
        model_name = str(full_name)
        if 'complete' in model_name:
            continue
        fixup_copy(model_name, fixup_dir_path)


def fixup_copy(model_name: str, fixup_dir_path: Path) -> None:
    """Fixup copy - no changes needed."""
    cmd = f'cp -p {model_name} {str(fixup_dir_path)}'
    logger.debug(cmd)
    os.system(cmd)
