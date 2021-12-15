# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""OSCAL Profile to OSCO task tests."""

import configparser
import json
import os
import pathlib

from ruamel.yaml import YAML

from tests.test_utils import text_files_equal

import trestle.tasks.profile_to_osco as profile_to_osco
from trestle.oscal.profile import Profile
from trestle.tasks.base_task import TaskOutcome
from trestle.transforms.implementations.osco import ProfileToOscoTransformer


def test_profile_to_osco_print_info(tmp_path):
    """Test print_info call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco.config')
    config.read(config_path)
    section = config['task.profile-to-osco']
    section['output-dir'] = str(tmp_path)
    tgt = profile_to_osco.ProfileToOsco(section)
    retval = tgt.print_info()
    assert retval is None


def test_profile_to_osco_simulate(tmp_path):
    """Test simulate call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco.config')
    config.read(config_path)
    section = config['task.profile-to-osco']
    section['output-dir'] = str(tmp_path)
    tgt = profile_to_osco.ProfileToOsco(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_profile_to_osco_execute(tmp_path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco.config')
    config.read(config_path)
    _test_profile_to_osco_execute_common(tmp_path, config)


def test_profile_to_osco_execute_osco_0_1_39_parms_no(tmp_path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-0.1.39-parms-no.config')
    config.read(config_path)
    _test_profile_to_osco_execute_common(tmp_path, config)


def test_profile_to_osco_execute_osco_0_1_39_parms_yes(tmp_path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-0.1.39-parms-yes.config')
    config.read(config_path)
    _test_profile_to_osco_execute_common(tmp_path, config)


def test_profile_to_osco_execute_osco_0_1_40_parms_no(tmp_path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-0.1.40-parms-no.config')
    config.read(config_path)
    _test_profile_to_osco_execute_common(tmp_path, config)


def test_profile_to_osco_execute_osco_0_1_40_parms_yes(tmp_path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-0.1.40-parms-yes.config')
    config.read(config_path)
    _test_profile_to_osco_execute_common(tmp_path, config)


def test_profile_to_osco_execute_osco_0_2_0_parms_no(tmp_path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-0.2.0-parms-no.config')
    config.read(config_path)
    _test_profile_to_osco_execute_common(tmp_path, config)


def test_profile_to_osco_execute_osco_1_0_0_parms_yes(tmp_path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-1.0.0-parms-yes.config')
    config.read(config_path)
    _test_profile_to_osco_execute_common(tmp_path, config)


def test_profile_to_osco_execute_osco_parms_no(tmp_path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-parms-no.config')
    config.read(config_path)
    _test_profile_to_osco_execute_common(tmp_path, config)


def test_profile_to_osco_execute_osco_parms_yes(tmp_path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-parms-yes.config')
    config.read(config_path)
    _test_profile_to_osco_execute_common(tmp_path, config)


def test_profile_to_osco_execute_osco_scc(tmp_path):
    """Test execute call."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-scc.config')
    config.read(config_path)
    _test_profile_to_osco_execute_common(tmp_path, config)


def _test_profile_to_osco_execute_common(tmp_path, config):
    """Test execute call."""
    section = config['task.profile-to-osco']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    tgt = profile_to_osco.ProfileToOsco(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    assert d_expected != d_produced
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)


def test_profile_to_osco_execute_bogus_profile(tmp_path):
    """Test execute call bogus profile."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-bogus.config')
    config.read(config_path)
    section = config['task.profile-to-osco']
    section['output-dir'] = str(tmp_path)
    tgt = profile_to_osco.ProfileToOsco(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_profile_to_osco_execute_bogus_config(tmp_path):
    """Test execute call bogus config."""
    section = None
    tgt = profile_to_osco.ProfileToOsco(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_profile_to_osco_execute_no_input_file(tmp_path):
    """Test execute call no input file."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-no-input-file.config')
    config.read(config_path)
    section = config['task.profile-to-osco']
    section['output-dir'] = str(tmp_path)
    tgt = profile_to_osco.ProfileToOsco(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_profile_to_osco_execute_no_output_dir(tmp_path):
    """Test execute call no output file."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-no-output-dir.config')
    config.read(config_path)
    section = config['task.profile-to-osco']
    tgt = profile_to_osco.ProfileToOsco(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_profile_to_osco_execute_no_overwrite(tmp_path):
    """Test execute call no overwrite."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-no-overwrite.config')
    config.read(config_path)
    section = config['task.profile-to-osco']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    tgt = profile_to_osco.ProfileToOsco(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0
    retval = tgt.execute()
    assert retval == TaskOutcome.SUCCESS
    list_dir = os.listdir(d_produced)
    assert len(list_dir) == 1
    assert d_expected != d_produced
    for fn in list_dir:
        f_expected = d_expected / fn
        f_produced = d_produced / fn
        result = text_files_equal(f_expected, f_produced)
        assert (result)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_profile_to_osco_execute_set(tmp_path):
    """Test execute call with set variables."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path('tests/data/tasks/profile-to-osco/profile-to-osco-set.config')
    config.read(config_path)
    section = config['task.profile-to-osco']
    input_file = section['input-file']
    input_path = pathlib.Path(input_file)
    f_expected = pathlib.Path(section['output-dir'], 'osco-profile.yaml')
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    f_produced = pathlib.Path(d_produced, 'osco-profile.yaml')
    # read input
    profile = Profile.oscal_read(input_path)
    # transform
    transformer = ProfileToOscoTransformer(
        extends='extends', api_version='api_version', kind='kind', name='name', namespace='namespace'
    )
    ydata = json.loads(transformer.transform(profile))
    # write output
    yaml = YAML(typ='safe')
    yaml.default_flow_style = False
    with open(f_produced, 'w') as outfile:
        yaml.dump(ydata, outfile)
    assert f_expected != f_produced
    result = text_files_equal(f_expected, f_produced)
    assert (result)
