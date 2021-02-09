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
"""OSCO transformation tests."""

import base64
import bz2
import json
import pathlib
import uuid
from unittest.mock import patch

from trestle.utils import osco

import yaml

stem_in = pathlib.Path('tests/data/tasks/osco/input')
stem_in_no_metadata = pathlib.Path('tests/data/tasks/osco/input-no-metadata')
stem_out = pathlib.Path('tests/data/tasks/osco/output')

mock_uuid4_value = uuid.UUID('d4cf7a88-cea7-4667-9924-8d278dc843df')


def test_function_osco_get_observations(tmp_path):
    """Test OSCO to OSCAL transformation."""
    idata = _load_yaml(stem_in, 'ssg-ocp4-ds-cis-111.222.333.444-pod.yaml')
    metadata = _load_yaml(stem_in, 'oscal-metadata.yaml')
    with patch('uuid.uuid4') as mock_uuid4:
        mock_uuid4.return_value = mock_uuid4_value
        observations, analysis = osco.get_observations(idata, metadata)
    expected = _load_json(stem_out, 'osco-pod-oscal-arp.json')
    tfile = tmp_path / 'osco-pod-oscal-arp.json'
    observations.oscal_write(tfile)
    actual = _load_json(tmp_path, 'osco-pod-oscal-arp.json')
    assert actual == expected


def test_function_osco_get_observations_json(tmp_path):
    """Test OSCO to OSCAL transformation."""
    idata = _load_yaml(stem_in, 'ssg-ocp4-ds-cis-111.222.333.444-pod.yaml')
    metadata = _load_yaml(stem_in, 'oscal-metadata.yaml')
    with patch('uuid.uuid4') as mock_uuid4:
        mock_uuid4.return_value = mock_uuid4_value
        observations, analysis = osco.get_observations_json(idata, metadata)
    expected = _load_json(stem_out, 'osco-pod-oscal.json')
    _dump_json(tmp_path, 'osco-pod-oscal.json', observations)
    actual = _load_json(tmp_path, 'osco-pod-oscal.json')
    assert actual == expected


def test_class_osco_rules(tmp_path):
    """Test class osco.Rules."""
    idata = _load_yaml(stem_in, 'ssg-ocp4-ds-cis-111.222.333.444-pod.yaml')
    rules = osco.Rules(idata)
    assert len(rules.instances) == 125
    assert len(rules.benchmark) == 2
    assert rules.benchmark['href'] == '/content/ssg-ocp4-ds.xml'
    assert rules.benchmark['id'] == 'xccdf_org.ssgproject.content_benchmark_OCP-4'
    assert len(rules.rule_metadata) == 2
    assert rules.rule_metadata['name'] == 'ssg-ocp4-ds-cis-111.222.333.444-pod'
    assert rules.rule_metadata['namespace'] == 'openshift-compliance'
    assert len(rules.analysis) == 3
    assert rules.analysis['config_maps'] == ['ssg-ocp4-ds']
    assert rules.analysis['dispatched_rules'] == 125
    assert len(rules.analysis['result_types']) == 4
    assert rules.analysis['result_types']['notselected'] == 2
    assert rules.analysis['result_types']['notchecked'] == 47
    assert rules.analysis['result_types']['fail'] == 64
    assert rules.analysis['result_types']['pass'] == 12


def test_class_osco_rules_none(tmp_path):
    """Test class osco.Rules when None."""
    rules = osco.Rules(None)
    assert len(rules.instances) == 0


def test_class_osco_rules_empty(tmp_path):
    """Test class osco.Rules when empty."""
    rules = osco.Rules({})
    assert len(rules.instances) == 0


def test_class_osco_rules_kind(tmp_path):
    """Test class osco.Rules when no kind==Config."""
    rules = osco.Rules({'kind': 'notConfigMap'})
    assert len(rules.instances) == 0


def test_class_osco_rules_no_results(tmp_path):
    """Test class osco.Rules when no results."""
    rules = osco.Rules({'kind': 'ConfigMap', 'data': {'not-results': ''}})
    assert len(rules.instances) == 0


def test_class_osco_rules_no_metadata(tmp_path):
    """Test class osco.Rules when no metadata."""
    idata = _load_yaml(stem_in_no_metadata, 'ssg-ocp4-ds-cis-111.222.333.444-pod.yaml')
    rules = osco.Rules(idata)
    assert len(rules.instances) == 125


def test_class_osco_rules_compressed(tmp_path):
    """Test class osco.Rules when compressed."""
    ipath = stem_in / 'ssg-ocp4-ds-cis-111.222.333.444-pod.yaml'
    opath = tmp_path / 'ssg-ocp4-ds-cis-111.222.333.444-pod.yaml'
    make_compressed(ipath, opath)
    idata = _load_yaml(tmp_path, 'ssg-ocp4-ds-cis-111.222.333.444-pod.yaml')
    rules = osco.Rules(idata)
    assert len(rules.instances) == 125


def make_compressed(ipath, opath):
    """Make an OSCO compressed XML version of the input file."""
    with open(ipath, 'r') as f:
        content = yaml.load(f, Loader=yaml.FullLoader)
    raw_string = content['data']['results']
    bytes_value = bytes(raw_string, 'utf-8')
    compressed_value = bz2.compress(bytes_value)
    encoded_value = base64.b64encode(compressed_value)
    strval = str(encoded_value, 'utf-8')
    content['data']['results'] = strval
    with open(opath, 'w') as f:
        yaml.dump(content, f)


def _load_yaml(stem, filename):
    """Provide utility to load yaml."""
    ifile = pathlib.Path('') / stem / filename
    with open(ifile, 'r+') as fp:
        data = fp.read()
        content = yaml.full_load(data)
    return content


def _load_json(stem, filename):
    """Provide utility to load json."""
    ifile = pathlib.Path('') / stem / filename
    with open(ifile, 'r', encoding='utf-8') as fp:
        content = json.load(fp)
    return content


def _dump_json(stem, filename, content):
    """Provide utility to dump json."""
    ifile = pathlib.Path('') / stem / filename
    with open(ifile, 'w', encoding='utf-8') as fp:
        content = json.dump(content, fp, indent=2)
