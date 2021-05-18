# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Facilitate Tanium report to NIST OSCAL transformation."""

import json
import logging
from typing import List

from trestle.transforms.results import Results
from trestle.transforms.transformer_factory import ResultsTransformer
from trestle.transforms.utils.osco_helper import ResultsMgr

import yaml

logger = logging.getLogger(__name__)


class OscoTransformer(ResultsTransformer):
    """Interface for Osco transformer."""

    def __init__(self):
        """Initialize."""
        self._results_mgr = ResultsMgr(self.get_timestamp())

    @property
    def analysis(self) -> List[str]:
        """Analysis."""
        return self._results_mgr.analysis

    def transform(self, blob: str) -> Results:
        """Transform the blob into a Results.

        The expected Osco blob is a string that is either json (from auditree)
        or yaml (from OpenSHift Compliance Operator).
        """
        results = Results()
        try:
            # auditree data
            jdata = json.loads(blob)
            for key in jdata.keys():
                for group in jdata[key]:
                    for cluster in jdata[key][group]:
                        if 'resources' in cluster:
                            for resource in cluster['resources']:
                                self._results_mgr.ingest(resource)
        except json.decoder.JSONDecodeError:
            # osco data
            resource = yaml.load(blob, Loader=yaml.Loader)
            self._results_mgr.ingest(resource)
        results.__root__.append(self._results_mgr.result)
        return results
