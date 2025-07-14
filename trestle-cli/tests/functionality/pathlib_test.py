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
"""Example functionality test."""
import os
import pathlib

import pytest


@pytest.mark.skipif(not os.environ.get('FUNCTIONAL_TESTS', False), reason='Efficiency gating')
def test_resolve_virtual(tmp_empty_cwd):
    """Test resolve functionality in pathlib."""
    my_path = pathlib.Path('test.json')
    resolved_path_str = str(my_path.resolve())
    hand_assembled_str = str(tmp_empty_cwd / my_path)
    assert resolved_path_str == hand_assembled_str
