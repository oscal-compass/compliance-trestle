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

import json
import pathlib
import uuid
from unittest.mock import patch

from trestle.lib import osco

import yaml

encoding = 'utf8'
loader = yaml.Loader
stem_in = 'tests/data/tasks/osco/input'
stem_out = 'tests/data/tasks/osco/output'

mock_uuid4_value = uuid.UUID('a8098c1a-f86e-11da-bd1a-00112444be1e')


def test_function_osco_get_observations(tmpdir):
    """Test OSCO to OSCAL transformation."""
    idata = _load_yaml(stem_in, 'ssg-ocp4-ds-cis-10.221.139.104-pod.yaml')
    metadata = _load_yaml(stem_in, 'oscal-metadata.yaml')
    with patch('uuid.uuid4') as mock_uuid4:
        mock_uuid4.return_value = mock_uuid4_value
        odata, analysis = osco.get_observations(idata, metadata)
    expected = _load_json(stem_out, 'ssg-ocp4-ds-cis-10.221.139.104-pod.oscal')
    tfile = tmpdir / 'ssg-ocp4-ds-cis-10.221.139.104-pod.oscal'
    _save_json(tfile, odata)
    actual = _load_json(tmpdir, 'ssg-ocp4-ds-cis-10.221.139.104-pod.oscal')
    assert actual == expected


def test_class_osco_rules(tmpdir):
    """Test class osco.Rules."""
    idata = _load_yaml(stem_in, 'ssg-ocp4-ds-cis-10.221.139.104-pod.yaml')
    rules = osco.Rules(idata)
    assert len(rules.instances) == 125
    assert len(rules.benchmark) == 2
    assert rules.benchmark['href'] == '/content/ssg-ocp4-ds.xml'
    assert rules.benchmark['id'] == 'xccdf_org.ssgproject.content_benchmark_OCP-4'
    assert len(rules.metadata) == 2
    assert rules.metadata['name'] == 'ssg-ocp4-ds-cis-10.221.139.104-pod'
    assert rules.metadata['namespace'] == 'openshift-compliance'
    assert len(rules.analysis) == 3
    assert rules.analysis['config_maps'] == ['ssg-ocp4-ds']
    assert rules.analysis['dispatched_rules'] == 125
    assert len(rules.analysis['result_types']) == 4
    assert rules.analysis['result_types']['notselected'] == 2
    assert rules.analysis['result_types']['notchecked'] == 47
    assert rules.analysis['result_types']['fail'] == 64
    assert rules.analysis['result_types']['pass'] == 12


def test_class_osco_observations(tmpdir):
    """Test class osco.Observations."""
    idata = _load_yaml(stem_in, 'ssg-ocp4-ds-cis-10.221.139.104-pod.yaml')
    rules = osco.Rules(idata)
    metadata = _load_yaml(stem_in, 'oscal-metadata.yaml')
    with patch('uuid.uuid4') as mock_uuid4:
        mock_uuid4.return_value = mock_uuid4_value
        observations = osco.Observations(rules, metadata)
    assert len(observations.instances) == 125
    instance = observations.instances[0]
    assert len(instance) == 6
    assert instance['uuid'] == str(mock_uuid4_value)
    assert instance['description'] == 'xccdf_org.ssgproject.content_rule_ocp_idp_no_htpasswd'
    assert instance['title'] == 'xccdf_org.ssgproject.content_rule_ocp_idp_no_htpasswd'
    assert len(instance['evidence-group']) == 1
    assert instance['evidence-group'][0]['description'] == 'Evidence location.'
    assert instance['evidence-group'][0]['href'] == 'https://github.ibm.com/degenaro/evidence-locker'
    assert len(instance['evidence-group'][0]['properties']) == 4
    assert instance['evidence-group'][0]['properties'][0]['ns'] == 'xccdf'
    assert instance['evidence-group'][0]['properties'][0]['class'] == 'id'
    assert instance['evidence-group'][0]['properties'][0]['name'] == 'rule'
    assert instance['evidence-group'][0]['properties'][0]['value'
                                                          ] == 'xccdf_org.ssgproject.content_rule_ocp_idp_no_htpasswd'
    assert instance['evidence-group'][0]['properties'][1]['ns'] == 'xccdf'
    assert instance['evidence-group'][0]['properties'][1]['class'] == 'timestamp'
    assert instance['evidence-group'][0]['properties'][1]['name'] == 'time'
    assert instance['evidence-group'][0]['properties'][1]['value'] == '2020-08-03T02:26:26+00:00'
    assert instance['evidence-group'][0]['properties'][2]['ns'] == 'xccdf'
    assert instance['evidence-group'][0]['properties'][2]['class'] == 'result'
    assert instance['evidence-group'][0]['properties'][2]['name'] == 'result'
    assert instance['evidence-group'][0]['properties'][2]['value'] == 'notselected'
    assert instance['evidence-group'][0]['properties'][3]['ns'] == 'xccdf'
    assert instance['evidence-group'][0]['properties'][3]['class'] == 'target'
    assert instance['evidence-group'][0]['properties'][3]['name'] == 'target'
    assert instance['evidence-group'][0]['properties'][3][
        'value'] == 'kube-br7qsa3d0vceu2so1a90-roksopensca-default-0000026b.iks.ibm'
    assert len(instance['subject-references']) == 2
    assert instance['subject-references'][0]['uuid-ref'] == '56666738-0f9a-4e38-9aac-c0fad00a5821'
    assert instance['subject-references'][0]['type'] == 'component'
    assert instance['subject-references'][0]['title'] == 'Red Hat OpenShift Kubernetes'
    assert instance['subject-references'][1]['uuid-ref'] == '46aADFAC-A1fd-4Cf0-a6aA-d1AfAb3e0d3e'
    assert instance['subject-references'][1]['type'] == 'inventory-item'
    assert instance['subject-references'][1]['title'] == 'Pod'
    assert len(instance['subject-references'][1]['properties']) == 4
    assert instance['subject-references'][1]['properties'][
        'target'] == 'kube-br7qsa3d0vceu2so1a90-roksopensca-default-0000026b.iks.ibm'
    assert instance['subject-references'][1]['properties']['cluster-name'] == 'ROKS-OpenSCAP-1'
    assert instance['subject-references'][1]['properties']['cluster-type'] == 'openshift'
    assert instance['subject-references'][1]['properties']['cluster-region'] == 'us-south'


def _load_yaml(stem, filename):
    ifile = pathlib.Path('') / stem / filename
    with open(ifile, 'r+') as fp:
        data = fp.read()
        content = yaml.full_load(data)
    return content


def _load_json(stem, filename):
    ifile = pathlib.Path('') / stem / filename
    with open(ifile, 'r', encoding='utf-8') as fp:
        content = json.load(fp)
    return content


def _save_json(ofile, content):
    with open(ofile, 'w', encoding='utf-8') as fp:
        json.dump(content, fp, ensure_ascii=False, indent=2)
