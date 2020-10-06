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
"""Trestle command related utilities."""
from typing import List

from trestle.core.base_model import OscalBaseModel
from trestle.core.models.elements import ElementPath


def get_model(file_path: str) -> OscalBaseModel:
    """Get the model specified by the file."""
    raise NotImplementedError()


def parse_element_args(element_args: List[str]) -> List[ElementPath]:
    """Parse element args into a list of ElementPath."""
    raise NotImplementedError()
