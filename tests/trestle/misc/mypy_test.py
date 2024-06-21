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
"""Testing mypy."""

import pathlib
import subprocess

folder = pathlib.Path('tests') / 'trestle' / 'misc'
subject = folder / '_inventory.py'
config = folder / 'mypy.cfg'


def test_mypy(tmp_path) -> None:
    """Testing mypy."""
    cmd = ['trestle', 'version']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output_bytes, _ = process.communicate()
    output = output_bytes.decode('utf-8')
    assert 'Trestle version' in output
    assert 'based on OSCAL version' in output
    #
    cmd = ['mypy', '--config-file', f'{config}', f'{subject}']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output_bytes, _ = process.communicate()
    output = output_bytes.decode('utf-8')
    assert 'Success: no issues found in 1 source file' in output
