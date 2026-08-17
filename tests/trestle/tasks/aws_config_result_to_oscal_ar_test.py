# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2026 IBM Corp. All rights reserved.
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
"""AWS Config to OSCAL task tests."""

import configparser
import json
import pathlib

from tests.test_utils import TEST_DIR

from trestle.tasks.aws_config_result_to_oscal_ar import AwsConfigResultToOscalAR
from trestle.tasks.base_task import TaskOutcome

test_data_dir = TEST_DIR / 'data/tasks/aws-config'


def _build_config(input_dir: pathlib.Path, output_dir: pathlib.Path) -> configparser.SectionProxy:
    config = configparser.ConfigParser()
    section = 'task.aws-config-result-to-oscal-ar'
    config.add_section(section)
    config.set(section, 'input-dir', str(input_dir))
    config.set(section, 'output-dir', str(output_dir))
    return config[section]


class TestAwsConfigResultToOscalAR:
    def test_print_info(self, capsys):
        task = AwsConfigResultToOscalAR(None)
        task.print_info()

    def test_missing_config_fails(self):
        task = AwsConfigResultToOscalAR(None)
        assert task.execute() == TaskOutcome.FAILURE

    def test_missing_required_keys_fails(self):
        config = configparser.ConfigParser()
        config.add_section('task.aws-config-result-to-oscal-ar')
        task = AwsConfigResultToOscalAR(config['task.aws-config-result-to-oscal-ar'])
        assert task.execute() == TaskOutcome.FAILURE

    def test_simulate_does_not_write_output(self, tmp_path):
        output_dir = tmp_path / 'out'
        config = _build_config(test_data_dir, output_dir)
        task = AwsConfigResultToOscalAR(config)
        outcome = task.simulate()
        assert outcome == TaskOutcome.SIM_SUCCESS
        assert not output_dir.exists() or not list(output_dir.iterdir())

    def test_execute_produces_valid_oscal_result(self, tmp_path):
        output_dir = tmp_path / 'out'
        config = _build_config(test_data_dir, output_dir)
        task = AwsConfigResultToOscalAR(config)
        outcome = task.execute()
        assert outcome == TaskOutcome.SUCCESS

        produced = list(output_dir.glob('*.oscal.json'))
        assert len(produced) == 1
        data = json.loads(produced[0].read_text(encoding='utf-8'))
        assert 'results' in data
        result = data['results'][0]
        assert len(result['observations']) == 4
        assert len(result['local-definitions']['inventory-items']) == 3

    def test_execute_respects_output_overwrite_false(self, tmp_path):
        output_dir = tmp_path / 'out'
        config = _build_config(test_data_dir, output_dir)
        task = AwsConfigResultToOscalAR(config)
        assert task.execute() == TaskOutcome.SUCCESS

        config2 = _build_config(test_data_dir, output_dir)
        config2['output-overwrite'] = 'false'
        task2 = AwsConfigResultToOscalAR(config2)
        assert task2.execute() == TaskOutcome.FAILURE
