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
"""Tests of exchange protocol models."""
import inspect

import trestle.core.generators as gens
import trestle.third_party.exchange_protocol
from trestle.core.base_model import OscalBaseModel


def test_EP_models() -> None:
    """Test we can get all models which exist."""
    clsmembers = inspect.getmembers(trestle.third_party.exchange_protocol, inspect.isclass)
    for _, oscal_cls in clsmembers:
         # This removes some enums and other objects.
        if issubclass(oscal_cls, OscalBaseModel):
            gens.generate_sample_model(oscal_cls)