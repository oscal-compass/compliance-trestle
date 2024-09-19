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
"""Script to pre-process OSCAL schemas.

This module serves 3 purposes:

1. reordering of original OSCAL schema

The order of the "common" elements in the schemas produced by OSCAL is not consistent,
which leads to mismatches during Python code generation and less things appearing in common.
Reordering works nicely to increase the number of common objects.

2. reproducible names

Even with reordering, some names changed. Type1 in previous release of trestle is no longer
Type1 in current release. And the names were not necessarily meaningful. Code now navigates
to valid values in schema and assign names. Although some manual effort was initially
required, the anticipated OSCAL changes in the future are few. The end result is more
consistent naming.

3. allOf construct not correctly handled

The allOf construct, newly employed by the OSCAL schemas, is not handled correctly by the
Python code generator. An issue has been opened with the Python code generator.
See https://github.com/koxudaxi/datamodel-code-generator/issues/1901 (and others).
This part of pre-processing can be removed once a fix from the Python code generator
materializes.

"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

schema_file_name_search_template = 'oscal_*_schema.json'

body_integrity_map = {}


def body_identical_check(token: str, title: str, content: Dict) -> None:
    """Check that common entries have identical bodies."""
    # derive common key
    key = token.split(':')[1] + title
    # if no common entry yet, add and return
    if key not in body_integrity_map.keys():
        body_integrity_map[key] = content
        logger.debug(f'initialize for {key}')
        return
    # check that existing common entry matches this entry
    entry = body_integrity_map[key]
    # existing and current content should be same size
    if len(content.keys()) != len(entry.keys()):
        logger.error(f'{token} size mismatch')
    # existing and current individual content should match
    for ekey in entry.keys():
        if ekey not in content.keys():
            logger.error(f'missing content key {token}')
        if entry[ekey] != content[ekey]:
            logger.error(f'mismatch content for key {token}')
        logger.debug(f'match for {token}')


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
    # create fixup dir
    fixup_dir_name = f'tmp/{input_dir_name}-fixup'
    input_dir_path = Path(input_dir_name)
    fixup_dir_path = Path(fixup_dir_name)
    fixup_dir_path.mkdir(exist_ok=True, parents=True)
    # copy original schemas to fixup dir
    fixup_copy_schemas(input_dir_path, fixup_dir_path)
    # schema reorder entries
    fixup_json(fixup_dir_path)
    # schema patching
    patch_schemas(fixup_dir_path)
    patch_allof(fixup_dir_path)
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


def traverse_dict(data, model_name):
    """Recursively traverse dict and replace allOf with ref."""
    for _, value in data.items():
        if isinstance(value, dict):
            if 'allOf' in value.keys():
                allof = value['allOf'][1]
                if '$ref' in allof.keys():
                    value['$ref'] = allof['$ref']
                    del value['allOf']
            traverse_dict(value, model_name)


# - https://github.com/koxudaxi/datamodel-code-generator/issues/1901
def patch_allof(fixup_dir_path: Path) -> None:
    """Patch allOf in schemas."""
    for full_name in fixup_dir_path.glob(schema_file_name_search_template):
        model_name = str(full_name)
        data = json_data_get(model_name)
        traverse_dict(data, model_name)
        json_data_put(model_name, data)


# patch_schemas introduced for migrating from OSCAL 1.0.4 to 1.1.2 due to missing/broken
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
            logger.debug(f'patch: {model_name} {key}')
            data['definitions'][key] = patch_json[patch_key]
    json_data_put(model_name, data)


def patch_finding_target(model_name: str) -> None:
    """Patch finding target."""
    # finding target: change property name "status" to "objectiveStatus" to avoid conflict
    # later, oscal_normalize will do the reverse to get the field name correct
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
        u3 = 'objective_status'
        data['definitions'][k1][k2][u3] = value
        logger.debug(f'patch: {model_name} {k1}.{k2}.{k3} -> {k1}.{k2}.{u3}')
        json_data_put(model_name, data)


def patch_poam_origins(model_name: str) -> None:
    """Patch POAM origins."""
    # POAM: change property name "origins" to "originations" to avoid conflict
    # later, oscal_normalize will do the reverse to get the field name correct
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
    logger.debug(f'patch: {model_name} {k1}.{k2}.{k3} -> {k1}.{k2}.{u3}')
    json_data_put(model_name, data)


# With this patch the description in POAM slightly altered to match the other models.
# This beneficially results in RelatedObservation being common in POAM (no need for RelatedObservation1).
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
    logger.debug(f'patch: {model_name} {k1}.{k2}.{k3}.{k4}.{k5} {old_value} -> {new_value}')
    json_data_put(model_name, data)


# Profile: change name "select-control-by-id" to "select-control" to avoid conflict
# This does not cause in any field name changes.
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
    logger.debug(f'patch: {model_name} {old_value} -> {new_value}, count={count}')
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
# This beneficially results in unnamed entities getting assigned pre-determined names,
# rather than letting datamodel-codegen tool assign names nondeterministically.
def create_refs(model_name: str) -> None:
    """Create refs."""
    # Task Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:task',
        'oscal-ar-oscal-assessment-common:task',
        'oscal-poam-oscal-assessment-common:task',
    ]
    navigation = ['properties', 'type', 'anyOf']
    ref_name = 'TaskValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Time Unit Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:task',
        'oscal-ar-oscal-assessment-common:task',
        'oscal-poam-oscal-assessment-common:task',
    ]
    navigation = ['properties', 'timing', 'properties', 'at-frequency', 'properties', 'unit', 'allOf']
    ref_name = 'TimeUnitValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Finding Target Type Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:finding-target',
        'oscal-ar-oscal-assessment-common:finding-target',
        'oscal-poam-oscal-assessment-common:finding-target',
    ]
    navigation = ['properties', 'type', 'allOf']
    ref_name = 'FindingTargetTypeValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Objective Status State Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:finding-target',
        'oscal-ar-oscal-assessment-common:finding-target',
        'oscal-poam-oscal-assessment-common:finding-target',
    ]
    navigation = ['properties', 'objective_status', 'properties', 'state', 'allOf']
    ref_name = 'ObjectiveStatusStateValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Threat Id Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:threat-id',
        'oscal-ar-oscal-assessment-common:threat-id',
        'oscal-poam-oscal-assessment-common:threat-id',
    ]
    navigation = ['properties', 'system', 'anyOf']
    ref_name = 'ThreatIdValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Select Subject By Id Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:select-subject-by-id',
        'oscal-ar-oscal-assessment-common:select-subject-by-id',
        'oscal-poam-oscal-assessment-common:select-subject-by-id',
    ]
    navigation = ['properties', 'type', 'anyOf']
    ref_name = 'SelectSubjectByIdValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Assessment Subject Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:assessment-subject',
        'oscal-ar-oscal-assessment-common:assessment-subject',
        'oscal-poam-oscal-assessment-common:assessment-subject',
    ]
    navigation = ['properties', 'type', 'anyOf']
    ref_name = 'AssessmentSubjectValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Naming System Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:characterization',
        'oscal-ar-oscal-assessment-common:characterization',
        'oscal-poam-oscal-assessment-common:characterization',
    ]
    navigation = ['properties', 'facets', 'items', 'properties', 'system', 'anyOf']
    ref_name = 'NamingSystemValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Subject Reference Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:subject-reference',
        'oscal-ar-oscal-assessment-common:subject-reference',
        'oscal-poam-oscal-assessment-common:subject-reference',
    ]
    navigation = ['properties', 'type', 'anyOf']
    ref_name = 'SubjectReferenceValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Subject Reference Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:observation',
        'oscal-ar-oscal-assessment-common:observation',
        'oscal-poam-oscal-assessment-common:observation',
    ]
    navigation = ['properties', 'types', 'items', 'anyOf']
    ref_name = 'ObservationTypeValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Risk Status Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:risk-status',
        'oscal-ar-oscal-assessment-common:risk-status',
        'oscal-poam-oscal-assessment-common:risk-status',
    ]
    navigation = ['anyOf']
    ref_name = 'RiskStatusValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
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
    navigation = ['properties', 'how-many', 'allOf']
    ref_name = 'HowManyValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Telephone Type Valid Values
    list_ = [
        'oscal-ap-oscal-metadata:telephone-number',
        'oscal-ar-oscal-metadata:telephone-number',
        'oscal-catalog-oscal-metadata:telephone-number',
        'oscal-component-definition-oscal-metadata:telephone-number',
        'oscal-poam-oscal-metadata:telephone-number',
        'oscal-profile-oscal-metadata:telephone-number',
        'oscal-ssp-oscal-metadata:telephone-number',
    ]
    navigation = ['properties', 'type', 'anyOf']
    ref_name = 'TelephoneTypeValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Address Type Valid Values
    list_ = [
        'oscal-ap-oscal-metadata:address',
        'oscal-ar-oscal-metadata:address',
        'oscal-catalog-oscal-metadata:address',
        'oscal-component-definition-oscal-metadata:address',
        'oscal-poam-oscal-metadata:address',
        'oscal-profile-oscal-metadata:address',
        'oscal-ssp-oscal-metadata:address',
    ]
    navigation = ['properties', 'type', 'anyOf']
    ref_name = 'AddressTypeValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # External Scheme Valid Values
    list_ = [
        'oscal-ap-oscal-metadata:metadata',
        'oscal-ar-oscal-metadata:metadata',
        'oscal-catalog-oscal-metadata:metadata',
        'oscal-component-definition-oscal-metadata:metadata',
        'oscal-poam-oscal-metadata:metadata',
        'oscal-profile-oscal-metadata:metadata',
        'oscal-ssp-oscal-metadata:metadata',
    ]
    navigation = [
        'properties', 'parties', 'items', 'properties', 'external-ids', 'items', 'properties', 'scheme', 'anyOf'
    ]
    ref_name = 'ExternalSchemeValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Party Type Valid Values
    list_ = [
        'oscal-ap-oscal-metadata:metadata',
        'oscal-ar-oscal-metadata:metadata',
        'oscal-catalog-oscal-metadata:metadata',
        'oscal-component-definition-oscal-metadata:metadata',
        'oscal-poam-oscal-metadata:metadata',
        'oscal-profile-oscal-metadata:metadata',
        'oscal-ssp-oscal-metadata:metadata',
    ]
    navigation = ['properties', 'parties', 'items', 'properties', 'type', 'allOf']
    ref_name = 'Party TypeValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Document Scheme Valid Values
    list_ = [
        'oscal-ap-oscal-metadata:document-id',
        'oscal-ar-oscal-metadata:document-id',
        'oscal-catalog-oscal-metadata:document-id',
        'oscal-component-definition-oscal-metadata:document-id',
        'oscal-poam-oscal-metadata:document-id',
        'oscal-profile-oscal-metadata:document-id',
        'oscal-ssp-oscal-metadata:document-id',
    ]
    navigation = ['properties', 'scheme', 'anyOf']
    ref_name = 'DocumentSchemeValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Defined Component Type Valid Values
    list_ = [
        'oscal-component-definition-oscal-component-definition:defined-component',
    ]
    navigation = ['properties', 'type', 'anyOf']
    ref_name = 'DefinedComponentTypeValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # System Component Type Valid Values
    list_ = [
        'oscal-ap-oscal-implementation-common:system-component',
        'oscal-ar-oscal-implementation-common:system-component',
        'oscal-catalog-oscal-implementation-common:system-component',
        'oscal-component-definition-oscal-implementation-common:system-component',
        'oscal-poam-oscal-implementation-common:system-component',
        'oscal-profile-oscal-implementation-common:system-component',
        'oscal-ssp-oscal-implementation-common:system-component',
    ]
    navigation = ['properties', 'type', 'anyOf']
    ref_name = 'SystemComponentTypeValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # System Component Operational State
    list_ = [
        'oscal-ap-oscal-implementation-common:system-component',
        'oscal-ar-oscal-implementation-common:system-component',
        'oscal-catalog-oscal-implementation-common:system-component',
        'oscal-component-definition-oscal-implementation-common:system-component',
        'oscal-poam-oscal-implementation-common:system-component',
        'oscal-profile-oscal-implementation-common:system-component',
        'oscal-ssp-oscal-implementation-common:system-component',
    ]
    navigation = ['properties', 'status', 'properties', 'state', 'allOf']
    ref_name = 'SystemComponentOperationalStateValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Origin Actor Type Valid Values
    list_ = [
        'oscal-ap-oscal-assessment-common:origin-actor',
        'oscal-ar-oscal-assessment-common:origin-actor',
        'oscal-poam-oscal-assessment-common:origin-actor',
    ]
    navigation = ['properties', 'type', 'allOf']
    ref_name = 'OriginActorValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Port Range Valid Values
    list_ = [
        'oscal-ap-oscal-implementation-common:port-range',
        'oscal-ar-oscal-implementation-common:port-range',
        'oscal-component-definition-oscal-implementation-common:port-range',
        'oscal-poam-oscal-implementation-common:port-range',
        'oscal-ssp-oscal-implementation-common:port-range',
    ]
    navigation = ['properties', 'transport', 'allOf']
    ref_name = 'PortRangeValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Operational State Valid Values
    list_ = [
        'oscal-ssp-oscal-ssp:status',
    ]
    navigation = ['properties', 'state', 'allOf']
    ref_name = 'OperationalStateValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Item Name Valid Values
    list_ = [
        'oscal-profile-oscal-profile:modify',
    ]
    navigation = [
        'properties', 'alters', 'items', 'properties', 'removes', 'items', 'properties', 'by-item-name', 'allOf'
    ]
    ref_name = 'ItemNameValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Order Valid Values
    list_ = [
        'oscal-profile-oscal-profile:insert-controls',
    ]
    navigation = ['properties', 'order', 'allOf']
    ref_name = 'OrderValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # With Child Controls Valid Values
    list_ = [
        'oscal-profile-oscal-profile:select-control',
    ]
    navigation = ['properties', 'with-child-controls', 'allOf']
    ref_name = 'WithChildControlsValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Position Valid Values
    list_ = [
        'oscal-profile-oscal-profile:modify',
    ]
    navigation = ['properties', 'alters', 'items', 'properties', 'adds', 'items', 'properties', 'position', 'allOf']
    ref_name = 'PositionValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)
    # Combination Method Valid Values
    list_ = [
        'oscal-profile-oscal-profile:merge',
    ]
    navigation = ['properties', 'combine', 'properties', 'method', 'allOf']
    ref_name = 'CombinationMethodValidValues'
    for root in list_:
        create_ref(model_name, root, navigation, ref_name)


def _fetch(tgt: Any, key: str) -> Any:
    """Fetch."""
    try:
        return tgt.get(key)
    except Exception:
        return _find(key, tgt)


def _get_title(model_name: str, root: str, navigation: List[str]) -> str:
    """Get title."""
    title = None
    data = json_data_get(model_name)
    tgt = data['definitions']
    tgt = tgt.get(root)
    if not tgt:
        return
    for leaf in navigation:
        tgt = _fetch(tgt, leaf)
    title = tgt
    return title


def create_ref(model_name: str, root: str, navigation: List[str], ref_name: str) -> None:
    """Create ref."""
    data = json_data_get(model_name)
    tgt = data['definitions']
    tgt = tgt.get(root)
    if not tgt:
        return
    for leaf in navigation:
        tgt = _fetch(tgt, leaf)
    item = tgt[1]
    replacement = {'$ref': f'#/definitions/{ref_name}'}
    tgt[1] = replacement
    tgt = data['definitions']
    tgt[ref_name] = item
    logger.debug(f'patch: {model_name} {replacement}')
    # title
    title_navigation = navigation
    title_navigation[-1] = 'title'
    title = _get_title(model_name, root, navigation)
    body_identical_check(root, title, replacement)
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
