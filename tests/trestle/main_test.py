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
"""Test calling as main."""

from unittest.mock import patch

import pytest


def test_init():
    """Test initialisation function for main."""
    import trestle.__main__ as main_mod
    with patch.object(main_mod, '__name__', '__main__'):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main_mod.init()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code > 0
