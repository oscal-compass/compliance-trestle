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

schema_file_name_search_template = 'oscal_*_schema.json'


def get_oscal_release(input_dir_name: str) -> str:
    """Get OSCAL release."""
    release = '?'
    input_dir_path = Path(input_dir_name)
    for full_name in input_dir_path.glob(schema_file_name_search_template):
        model_name = str(full_name)
        if 'catalog' in model_name:
            data = json_data_get(model_name)
            release = data['$id'].split('/')[-2]
    return release


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
    for full_name in fixup_dir_path.glob(schema_file_name_search_template):
        model_name = str(full_name)
        data = json_data_get(model_name)
        names_reorder(data)
        json_data_put(model_name, data)


def get_order(key):
    """Get order."""
    if 'json-schema-directive' in key:
        return 0
    if key.endswith('ap:assessment-plan'):
        return 1
    if key.endswith('ar:assessment-results'):
        return 1
    if key.endswith('catalog:catalog'):
        return 1
    if key.endswith('component-definition:component-definition'):
        return 1
    if key.endswith('poam:plan-of-action-and-milestones'):
        return 1
    if key.endswith('profile:profile'):
        return 1
    if key.endswith('ssp:system-security-plan'):
        return 1
    if 'oscal-metadata:' in key:
        return 2
    if 'oscal-control-common:' in key:
        return 3
    if 'oscal-implementation-common:' in key:
        return 4
    return 5


def names_reorder(data: Dict) -> None:
    """Reorder."""
    reorder_defs = {}
    for index in range(6):
        for key in data['definitions'].keys():
            order = get_order(key)
            if order == index:
                reorder_defs[key] = data['definitions'][key]
    len_old = len(data['definitions'])
    len_new = len(reorder_defs)
    if len_old != len_new:
        raise RuntimeError(f'old: {len_old} new: {len_new}')
    data['definitions'] = reorder_defs


def fixup_copy_schemas(input_dir_path: Path, fixup_dir_path: Path) -> None:
    """Fixup copy schemas."""
    for full_name in input_dir_path.glob(schema_file_name_search_template):
        model_name = str(full_name)
        if 'complete' in model_name:
            continue
        cmd = f'cp -p {model_name} {str(fixup_dir_path)}'
        logger.debug(cmd)
        os.system(cmd)
