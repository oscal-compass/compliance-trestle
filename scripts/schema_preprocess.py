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
    patch_dir_name = 'schema-patch'
    patch_file_path = Path(patch_dir_name) / 'schema-substitutes.json'
    fixup_dir_name = f'{input_dir_name}-fixup'
    input_dir_path = Path(input_dir_name)
    fixup_dir_path = Path(fixup_dir_name)
    fixup_dir_path.mkdir(exist_ok=True, parents=True)
    fixup_copy_schemas(input_dir_path, fixup_dir_path)
    fixup_json(fixup_dir_path)
    patch_schemas(fixup_dir_path, patch_file_path)
    return fixup_dir_path


def fixup_copy_schemas(input_dir_path: Path, fixup_dir_path: Path) -> None:
    """Fixup copy schemas."""
    for full_name in input_dir_path.glob(schema_file_name_search_template):
        model_name = str(full_name)
        if 'complete' in model_name:
            continue
        cmd = f'cp -p {model_name} {str(fixup_dir_path)}'
        logger.debug(cmd)
        os.system(cmd)


# patch_schemas introduced for migrating from OSCAL 1.0.4 to 1.2.2 due to missing/broken
# support in datamodel-codegen tool. See issue(s):
# - https://github.com/koxudaxi/datamodel-code-generator/issues/1901
def patch_schemas(fixup_dir_path: Path, patch_file_path: Path) -> None:
    """Patch json schemas."""
    # Patch file contains "old-style" defintions which are used temporarily
    # until datamodel-codegen tool issues are resolved.
    pf = f'{patch_file_path}'
    patch_json = json_data_get(pf)
    for full_name in fixup_dir_path.glob(schema_file_name_search_template):
        model_name = str(full_name)
        patch_model(model_name, patch_json)
        patch_finding_target(model_name)
        patch_poam_origins(model_name)


def calculate_patch_key(key: str) -> str:
    """Calculate patch key."""
    patch_key = key
    patch_key = patch_key.replace('oscal-ap-', '')
    patch_key = patch_key.replace('oscal-ar-', '')
    patch_key = patch_key.replace('oscal-catalog-', '')
    patch_key = patch_key.replace('oscal-component-definition-', '')
    patch_key = patch_key.replace('oscal-poam-', '')
    patch_key = patch_key.replace('oscal-profile-', '')
    patch_key = patch_key.replace('oscal-ssp-', '')
    return patch_key


def patch_model(model_name: str, patch_json: Dict):
    """Patch model."""
    data = json_data_get(model_name)
    for key in data['definitions'].keys():
        patch_key = calculate_patch_key(key)
        if patch_key in patch_json.keys():
            logger.info(f'patch: {model_name} {key}')
            data['definitions'][key] = patch_json[patch_key]
    json_data_put(model_name, data)


def patch_finding_target(model_name: str) -> None:
    """Patch finding target."""
    # finding target: change property name "status" to "objectiveStatus" to avoid conflict
    data = json_data_get(model_name)
    for k1 in data['definitions'].keys():
        if not k1.endswith('-common:finding-target'):
            continue
        k2 = 'properties'
        if k2 not in data['definitions'][k1]:
            continue
        k3 = 'status'
        if k3 not in data['definitions'][k1][k2]:
            continue
        value = data['definitions'][k1][k2][k3]
        del data['definitions'][k1][k2][k3]
        u3 = 'objectiveStatus'
        data['definitions'][k1][k2][u3] = value
        logger.info(f'patch: {model_name} {k1}.{k2}.{k3} -> {k1}.{k2}.{u3}')
        json_data_put(model_name, data)


def patch_poam_origins(model_name: str) -> None:
    """Patch POAM origins."""
    # POAM: change property name "origins" to "originations" to avoid conflict
    if not model_name.endswith('oscal_poam_schema.json'):
        return
    data = json_data_get(model_name)
    k1 = 'oscal-poam-oscal-poam:poam-item'
    if k1 not in data['definitions'].keys():
        return
    k2 = 'properties'
    if k2 not in data['definitions'][k1]:
        return
    k3 = 'origins'
    if k3 not in data['definitions'][k1][k2]:
        return
    value = data['definitions'][k1][k2][k3]
    del data['definitions'][k1][k2][k3]
    u3 = 'originations'
    data['definitions'][k1][k2][u3] = value
    logger.info(f'patch: {model_name} {k1}.{k2}.{k3} -> {k1}.{k2}.{u3}')
    json_data_put(model_name, data)


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


def get_order(key: str) -> int:
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
