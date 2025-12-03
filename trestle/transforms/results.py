# -*- mode:python; coding:utf-8 -*-

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
"""Define Results class returned by transformers."""

from typing import List

from pydantic import RootModel

from trestle.oscal.assessment_results import Result


class Results(RootModel):
    """Transformer results as a list."""
    
    root: List[Result] = []
    
    def __iter__(self):
        """Iterate over results."""
        return iter(self.root)
    
    def __getitem__(self, item):
        """Get item from results."""
        return self.root[item]
    
    def __len__(self):
        """Get length of results."""
        return len(self.root)
    
    def append(self, item):
        """Append item to results."""
        self.root.append(item)
    
    def extend(self, items):
        """Extend results with items."""
        self.root.extend(items)