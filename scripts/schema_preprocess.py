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
from typing import Any, Dict, List

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
    patch_schemas(fixup_dir_path)
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
def patch_schemas(fixup_dir_path: Path) -> None:
    """Patch json schemas."""
    for full_name in fixup_dir_path.glob(schema_file_name_search_template):
        model_name = str(full_name)
        patch_finding_target(model_name)
        patch_poam_origins(model_name)
        patch_poam_item(model_name, 'related-findings')
        patch_poam_item(model_name, 'related-observations')
        patch_profile(model_name)
        create_refs(model_name)


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


# With this patch the description in POAM slightly altered to match the other models.
# This may not be an acceptable solution!?
def patch_poam_item(model_name: str, k3: str) -> None:
    """Patch POAM item."""
    # POAM: change related-finding item description from "poam-item" to "finding" to avoid conflict
    if not model_name.endswith('oscal_poam_schema.json'):
        return
    data = json_data_get(model_name)
    k1 = 'oscal-poam-oscal-poam:poam-item'
    if k1 not in data['definitions'].keys():
        return
    k2 = 'properties'
    if k2 not in data['definitions'][k1]:
        return
    if k3 not in data['definitions'][k1][k2]:
        return
    k4 = 'items'
    if k4 not in data['definitions'][k1][k2][k3]:
        return
    k5 = 'description'
    if k5 not in data['definitions'][k1][k2][k3][k4]:
        return
    old_value = 'poam-item'
    if old_value not in data['definitions'][k1][k2][k3][k4][k5]:
        return
    new_value = 'finding'
    data['definitions'][k1][k2][k3][k4][k5] = data['definitions'][k1][k2][k3][k4][k5].replace(old_value, new_value)
    logger.info(f'patch: {model_name} {k1}.{k2}.{k3}.{k4}.{k5} {old_value} -> {new_value}')
    json_data_put(model_name, data)


def patch_profile(model_name: str) -> None:
    """Patch profile."""
    if not model_name.endswith('oscal_profile_schema.json'):
        return
    old_data = data_get(model_name)
    new_data = []
    old_value = 'select-control-by-id'
    new_value = 'select-control'
    count = 0
    for line in old_data:
        if old_value in line:
            count += 1
            line = line.replace(old_value, new_value)
        new_data.append(line)
    logger.info(f'patch: {model_name} {old_value} -> {new_value}, count={count}')
    data_put(model_name, new_data)
    # format
    data = json_data_get(model_name)
    json_data_put(model_name, data)


def _find(needle: str, haystack: Dict) -> Any:
    """Find needle in haystack."""
    for item in haystack:
        if item == needle:
            return haystack[item]
    return None


# Create refs for common elements
def create_refs(model_name: str) -> None:
    """Create refs."""
    # Task Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:task',
        'oscal-ar-oscal-assessment-common:task',
        'oscal-poam-oscal-assessment-common:task',
    ]
    for key in list_:
        create_ref_task_valid_values(model_name, key)
    # Threat Id Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:threat-id',
        'oscal-ar-oscal-assessment-common:threat-id',
        'oscal-poam-oscal-assessment-common:threat-id',
    ]
    for key in list_:
        create_ref_threat_id_valid_values(model_name, key)
    # Select Subject By Id Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:select-subject-by-id',
        'oscal-ar-oscal-assessment-common:select-subject-by-id',
        'oscal-poam-oscal-assessment-common:select-subject-by-id',
    ]
    for key in list_:
        create_ref_select_subject_by_id_valid_values(model_name, key)
    # Assessment Subject Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:assessment-subject',
        'oscal-ar-oscal-assessment-common:assessment-subject',
        'oscal-poam-oscal-assessment-common:assessment-subject',
    ]
    for key in list_:
        create_ref_assessment_subject_valid_values(model_name, key)
    # Naming System Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:characterization',
        'oscal-ar-oscal-assessment-common:characterization',
        'oscal-poam-oscal-assessment-common:characterization',
    ]
    for key in list_:
        create_ref_naming_system_valid_values(model_name, key)
    # Subject Reference Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:subject-reference',
        'oscal-ar-oscal-assessment-common:subject-reference',
        'oscal-poam-oscal-assessment-common:subject-reference',
    ]
    for key in list_:
        create_ref_subject_reference_valid_values(model_name, key)
    # Subject Reference Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:observation',
        'oscal-ar-oscal-assessment-common:observation',
        'oscal-poam-oscal-assessment-common:observation',
    ]
    for key in list_:
        create_ref_observation_type_valid_values(model_name, key)
    # Risk Status Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:risk-status',
        'oscal-ar-oscal-assessment-common:risk-status',
        'oscal-poam-oscal-assessment-common:risk-status',
    ]
    for key in list_:
        create_ref_risk_status_valid_values(model_name, key)
    # How Many Valid Values
    list_ = [
        'oscal-ap-oscal-control-common:parameter-selection',
        'oscal-ar-oscal-control-common:parameter-selection',
        'oscal-catalog-oscal-control-common:parameter-selection',
        'oscal-component-definition-oscal-control-common:parameter-selection',
        'oscal-poam-oscal-control-common:parameter-selection',
        'oscal-profile-oscal-control-common:parameter-selection',
        'oscal-ssp-oscal-control-common:parameter-selection',
    ]
    for key in list_:
        create_ref_how_many_valid_values(model_name, key)


def create_ref_task_valid_values(model_name: str, k1: str) -> None:
    """Create ref for Task Valid Values."""
    data = json_data_get(model_name)
    tgt = data['definitions']
    tgt = tgt.get(k1)
    if not tgt:
        return
    k2 = 'properties'
    tgt = tgt.get(k2)
    k3 = 'type'
    tgt = _find(k3, tgt)
    k4 = 'anyOf'
    tgt = tgt.get(k4)
    key = 'TaskValidValues'
    item = tgt[1]
    replacement = {'$ref': f'#/definitions/{key}'}
    tgt[1] = replacement
    tgt = data['definitions']
    tgt[key] = item
    logger.info(f'patch: {model_name} {replacement}')
    json_data_put(model_name, data)


def create_ref_threat_id_valid_values(model_name: str, k1: str) -> None:
    """Create ref for Threat Id Valid Values."""
    data = json_data_get(model_name)
    tgt = data['definitions']
    tgt = tgt.get(k1)
    if not tgt:
        return
    k2 = 'properties'
    tgt = tgt.get(k2)
    k3 = 'system'
    tgt = _find(k3, tgt)
    k4 = 'anyOf'
    tgt = tgt.get(k4)
    key = 'ThreatIdValidValues'
    item = tgt[1]
    replacement = {'$ref': f'#/definitions/{key}'}
    tgt[1] = replacement
    tgt = data['definitions']
    tgt[key] = item
    logger.info(f'patch: {model_name} {replacement}')
    json_data_put(model_name, data)


def create_ref_select_subject_by_id_valid_values(model_name: str, k1: str) -> None:
    """Create ref for Select Subject By Id Valid Values."""
    data = json_data_get(model_name)
    tgt = data['definitions']
    tgt = tgt.get(k1)
    if not tgt:
        return
    k2 = 'properties'
    tgt = tgt.get(k2)
    k3 = 'type'
    tgt = _find(k3, tgt)
    k4 = 'anyOf'
    tgt = tgt.get(k4)
    key = 'SelectSubjectByIdValidValues'
    item = tgt[1]
    replacement = {'$ref': f'#/definitions/{key}'}
    tgt[1] = replacement
    tgt = data['definitions']
    tgt[key] = item
    logger.info(f'patch: {model_name} {replacement}')
    json_data_put(model_name, data)


def create_ref_assessment_subject_valid_values(model_name: str, k1: str) -> None:
    """Create ref for Assessment Subject Valid Values."""
    data = json_data_get(model_name)
    tgt = data['definitions']
    tgt = tgt.get(k1)
    if not tgt:
        return
    k2 = 'properties'
    tgt = tgt.get(k2)
    k3 = 'type'
    tgt = _find(k3, tgt)
    k4 = 'anyOf'
    tgt = tgt.get(k4)
    key = 'AssessmentSubjectValidValues'
    item = tgt[1]
    replacement = {'$ref': f'#/definitions/{key}'}
    tgt[1] = replacement
    tgt = data['definitions']
    tgt[key] = item
    logger.info(f'patch: {model_name} {replacement}')
    json_data_put(model_name, data)


def create_ref_naming_system_valid_values(model_name: str, k1: str) -> None:
    """Create ref for Naming System Valid Values."""
    data = json_data_get(model_name)
    tgt = data['definitions']
    tgt = tgt.get(k1)
    if not tgt:
        return
    k2 = 'properties'
    tgt = tgt.get(k2)
    k3 = 'facets'
    tgt = _find(k3, tgt)
    k4 = 'items'
    tgt = _find(k4, tgt)
    k5 = 'properties'
    tgt = _find(k5, tgt)
    k6 = 'system'
    tgt = _find(k6, tgt)
    k7 = 'anyOf'
    tgt = tgt.get(k7)
    key = 'NamingSystemValidValues'
    item = tgt[1]
    replacement = {'$ref': f'#/definitions/{key}'}
    tgt[1] = replacement
    tgt = data['definitions']
    tgt[key] = item
    logger.info(f'patch: {model_name} {replacement}')
    json_data_put(model_name, data)


def create_ref_subject_reference_valid_values(model_name: str, k1: str) -> None:
    """Create ref for Subject Reference Valid Values."""
    data = json_data_get(model_name)
    tgt = data['definitions']
    tgt = tgt.get(k1)
    if not tgt:
        return
    k2 = 'properties'
    tgt = tgt.get(k2)
    k3 = 'type'
    tgt = _find(k3, tgt)
    k4 = 'anyOf'
    tgt = tgt.get(k4)
    key = 'SubjectReferenceValidValues'
    item = tgt[1]
    replacement = {'$ref': f'#/definitions/{key}'}
    tgt[1] = replacement
    tgt = data['definitions']
    tgt[key] = item
    logger.info(f'patch: {model_name} {replacement}')
    json_data_put(model_name, data)


def create_ref_observation_type_valid_values(model_name: str, k1: str) -> None:
    """Create ref for Observation Type Valid Values."""
    data = json_data_get(model_name)
    tgt = data['definitions']
    tgt = tgt.get(k1)
    if not tgt:
        return
    k2 = 'properties'
    tgt = tgt.get(k2)
    k3 = 'types'
    tgt = _find(k3, tgt)
    k4 = 'items'
    tgt = tgt.get(k4)
    k5 = 'anyOf'
    tgt = tgt.get(k5)
    key = 'ObservationTypeValidValues'
    item = tgt[1]
    replacement = {'$ref': f'#/definitions/{key}'}
    tgt[1] = replacement
    tgt = data['definitions']
    tgt[key] = item
    logger.info(f'patch: {model_name} {replacement}')
    json_data_put(model_name, data)


def create_ref_risk_status_valid_values(model_name: str, k1: str) -> None:
    """Create ref for Risk Status Valid Values."""
    data = json_data_get(model_name)
    tgt = data['definitions']
    tgt = tgt.get(k1)
    if not tgt:
        return
    k2 = 'anyOf'
    tgt = tgt.get(k2)
    key = 'RiskStatusValidValues'
    item = tgt[1]
    replacement = {'$ref': f'#/definitions/{key}'}
    tgt[1] = replacement
    tgt = data['definitions']
    tgt[key] = item
    logger.info(f'patch: {model_name} {replacement}')
    json_data_put(model_name, data)


def create_ref_how_many_valid_values(model_name: str, k1: str) -> None:
    """Create ref for How Many Valid Values."""
    data = json_data_get(model_name)
    tgt = data['definitions']
    tgt = tgt.get(k1)
    if not tgt:
        return
    k2 = 'properties'
    tgt = tgt.get(k2)
    k3 = 'how-many'
    tgt = _find(k3, tgt)
    k4 = 'allOf'
    tgt = tgt.get(k4)
    key = 'HowManyValidValues'
    item = tgt[1]
    replacement = {'$ref': f'#/definitions/{key}'}
    tgt[1] = replacement
    tgt = data['definitions']
    tgt[key] = item
    logger.info(f'patch: {model_name} {replacement}')
    json_data_put(model_name, data)


def data_get(model_name: str) -> List:
    """Get data."""
    data = []
    with open(model_name, 'r') as f:
        for line in f:
            data.append(line.strip())
    return data


def data_put(model_name: str, data: List) -> None:
    """Put data."""
    with open(model_name, 'w') as f:
        for line in data:
            f.write(f'{line}\n')


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
    if key != 'range':
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
        if 'oscal-assessment-common:' in key:
            return 5
        return 6
    else:
        # range = 1 + the highest number above
        return 7


def names_reorder(data: Dict) -> None:
    """Reorder."""
    reorder_defs = {}
    for index in range(get_order('range')):
        for key in data['definitions'].keys():
            order = get_order(key)
            if order == index:
                reorder_defs[key] = data['definitions'][key]
    len_old = len(data['definitions'])
    len_new = len(reorder_defs)
    if len_old != len_new:
        raise RuntimeError(f'old: {len_old} new: {len_new}')
    data['definitions'] = reorder_defs
