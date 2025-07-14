# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Abstract base class for pipelines and filters."""

from abc import ABC, abstractclassmethod
from typing import Any, List


class Pipeline():
    """Pipeline base class."""

    class Filter(ABC):
        """Filter class used by pipeline."""

        @abstractclassmethod
        def process(self, input_: Any) -> Any:
            """Process the input to output."""
            return input_

    def __init__(self, filters: List[Filter]) -> None:
        """Initialize the class."""
        self._filters = filters

    def process(self, input_: Any) -> Any:
        """Process the filter pipeline."""
        for filter_ in self._filters:
            input_ = filter_.process(input_)
        return input_
