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

import trestle.tasks.oscal_profile_to_osco_profile as oscal_profile_to_osco_profile
from trestle.oscal.profile import Profile
from trestle.tasks.base_task import TaskOutcome
from trestle.transforms.implementations.osco import OscalProfileToOscoProfileTransformer


def setup_config(path: str):
    """Config."""
    config = configparser.ConfigParser()
    config_path = pathlib.Path(path)
    config.read(config_path)
    return config


def test_oscal_profile_to_osco_profile_print_info(tmp_path):
    """Test print_info call."""
    config = setup_config('tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile.config')
    section = config['task.oscal-profile-to-osco-profile']
    section['output-dir'] = str(tmp_path)
    tgt = oscal_profile_to_osco_profile.ProfileToOsco(section)
    retval = tgt.print_info()
    assert retval is None


def test_oscal_profile_to_osco_profile_simulate(tmp_path):
    """Test simulate call."""
    config = setup_config('tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile.config')
    section = config['task.oscal-profile-to-osco-profile']
    section['output-dir'] = str(tmp_path)
    tgt = oscal_profile_to_osco_profile.ProfileToOsco(section)
    retval = tgt.simulate()
    assert retval == TaskOutcome.SIM_SUCCESS
    assert len(os.listdir(str(tmp_path))) == 0


def test_oscal_profile_to_osco_profile_execute(tmp_path):
    """Test execute call."""
    config = setup_config('tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile.config')
    _test_oscal_profile_to_osco_profile_execute_common(tmp_path, config)


def test_oscal_profile_to_osco_profile_execute_osco_0_1_39_parms_no(tmp_path):
    """Test execute call."""
    config = setup_config(
        'tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-0.1.39-parms-no.config'
    )
    _test_oscal_profile_to_osco_profile_execute_common(tmp_path, config)


def test_oscal_profile_to_osco_profile_execute_osco_0_1_39_parms_yes(tmp_path):
    """Test execute call."""
    config = setup_config(
        'tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-0.1.39-parms-yes.config'
    )
    _test_oscal_profile_to_osco_profile_execute_common(tmp_path, config)


def test_oscal_profile_to_osco_profile_execute_osco_0_1_40_parms_no(tmp_path):
    """Test execute call."""
    config = setup_config(
        'tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-0.1.40-parms-no.config'
    )
    _test_oscal_profile_to_osco_profile_execute_common(tmp_path, config)


def test_oscal_profile_to_osco_profile_execute_osco_0_1_40_parms_yes(tmp_path):
    """Test execute call."""
    config = setup_config(
        'tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-0.1.40-parms-yes.config'
    )
    _test_oscal_profile_to_osco_profile_execute_common(tmp_path, config)


def test_oscal_profile_to_osco_profile_execute_osco_0_2_0_parms_no(tmp_path):
    """Test execute call."""
    config = setup_config(
        'tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-0.2.0-parms-no.config'
    )
    _test_oscal_profile_to_osco_profile_execute_common(tmp_path, config)


def test_oscal_profile_to_osco_profile_execute_osco_1_0_0_parms_yes(tmp_path):
    """Test execute call."""
    config = setup_config(
        'tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-1.0.0-parms-yes.config'
    )
    _test_oscal_profile_to_osco_profile_execute_common(tmp_path, config)


def test_oscal_profile_to_osco_profile_execute_osco_parms_no(tmp_path):
    """Test execute call."""
    config = setup_config(
        'tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-parms-no.config'
    )
    _test_oscal_profile_to_osco_profile_execute_common(tmp_path, config)


def test_oscal_profile_to_osco_profile_execute_osco_parms_yes(tmp_path):
    """Test execute call."""
    config = setup_config(
        'tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-parms-yes.config'
    )
    _test_oscal_profile_to_osco_profile_execute_common(tmp_path, config)


def test_oscal_profile_to_osco_profile_execute_osco_scc(tmp_path):
    """Test execute call."""
    config = setup_config('tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-scc.config')
    _test_oscal_profile_to_osco_profile_execute_common(tmp_path, config)


def _test_oscal_profile_to_osco_profile_execute_common(tmp_path, config):
    """Test execute call."""
    section = config['task.oscal-profile-to-osco-profile']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    tgt = oscal_profile_to_osco_profile.ProfileToOsco(section)
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


def test_oscal_profile_to_osco_profile_execute_bogus_profile(tmp_path):
    """Test execute call bogus profile."""
    config = setup_config('tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-bogus.config')
    section = config['task.oscal-profile-to-osco-profile']
    section['output-dir'] = str(tmp_path)
    tgt = oscal_profile_to_osco_profile.ProfileToOsco(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_oscal_profile_to_osco_profile_execute_bogus_config(tmp_path):
    """Test execute call bogus config."""
    section = None
    tgt = oscal_profile_to_osco_profile.ProfileToOsco(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_oscal_profile_to_osco_profile_execute_no_input_file(tmp_path):
    """Test execute call no input file."""
    config = setup_config(
        'tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-no-input-file.config'
    )
    section = config['task.oscal-profile-to-osco-profile']
    section['output-dir'] = str(tmp_path)
    tgt = oscal_profile_to_osco_profile.ProfileToOsco(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_oscal_profile_to_osco_profile_execute_no_output_dir(tmp_path):
    """Test execute call no output file."""
    config = setup_config(
        'tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-no-output-dir.config'
    )
    section = config['task.oscal-profile-to-osco-profile']
    tgt = oscal_profile_to_osco_profile.ProfileToOsco(section)
    retval = tgt.execute()
    assert retval == TaskOutcome.FAILURE


def test_oscal_profile_to_osco_profile_execute_no_overwrite(tmp_path):
    """Test execute call no overwrite."""
    config = setup_config(
        'tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-no-overwrite.config'
    )
    section = config['task.oscal-profile-to-osco-profile']
    d_expected = pathlib.Path(section['output-dir'])
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    tgt = oscal_profile_to_osco_profile.ProfileToOsco(section)
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


def test_oscal_profile_to_osco_profile_execute_set(tmp_path):
    """Test execute call with set variables."""
    config = setup_config('tests/data/tasks/oscal-profile-to-osco-profile/oscal-profile-to-osco-profile-set.config')
    section = config['task.oscal-profile-to-osco-profile']
    input_file = section['input-file']
    input_path = pathlib.Path(input_file)
    f_expected = pathlib.Path(section['output-dir'], 'osco-profile.yaml')
    d_produced = tmp_path
    section['output-dir'] = str(d_produced)
    f_produced = pathlib.Path(d_produced, 'osco-profile.yaml')
    # read input
    profile = Profile.oscal_read(input_path)
    # transform
    transformer = OscalProfileToOscoProfileTransformer(
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
