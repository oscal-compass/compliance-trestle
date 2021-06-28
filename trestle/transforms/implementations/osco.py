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

from ruamel.yaml import YAML

from trestle.transforms.results import Results
from trestle.transforms.transformer_factory import ResultsTransformer
from trestle.transforms.utils.osco_helper import ResultsMgr

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

    def _ingest_xml(self, blob: str) -> Results:
        """Ingest xml data."""
        # ?xml data
        if blob.startswith('<?xml'):
            resource = blob
            self._results_mgr.ingest_xml(resource)
        else:
            return None
        results = Results()
        results.__root__.append(self._results_mgr.result)
        return results

    def _ingest_json(self, blob: str) -> Results:
        """Ingest json data."""
        try:
            # ? configmaps or auditree data
            jdata = json.loads(blob)
            # https://docs.openshift.com/container-platform/3.7/rest_api/api/v1.ConfigMap.html#Get-api-v1-namespaces-namespace-configmaps-name
            if 'kind' in jdata.keys() and jdata['kind'] == 'ConfigMapList' and 'items' in jdata.keys():
                items = jdata['items']
                for item in items:
                    if 'data' in item.keys():
                        data = item['data']
                        if 'results' in data:
                            resource = item
                            self._results_mgr.ingest(resource)
            # https://github.com/ComplianceAsCode/auditree-arboretum/blob/main/arboretum/kubernetes/fetchers/fetch_cluster_resource.py
            else:
                for key in jdata.keys():
                    for group in jdata[key]:
                        for cluster in jdata[key][group]:
                            if 'resources' in cluster:
                                for resource in cluster['resources']:
                                    self._results_mgr.ingest(resource)
        except json.decoder.JSONDecodeError:
            return None
        results = Results()
        results.__root__.append(self._results_mgr.result)
        return results

    def _ingest_yaml(self, blob: str) -> Results:
        """Ingest yaml data."""
        try:
            # ? yaml data
            yaml = YAML(typ='safe')
            resource = yaml.load(blob)
            self._results_mgr.ingest(resource)
        except Exception as e:
            raise e
        results = Results()
        results.__root__.append(self._results_mgr.result)
        return results

    def transform(self, blob: str) -> Results:
        """Transform the blob into a Results.

        The expected blob is a string that is one of:
            - data from OpenShift Compliance Operator (json, yaml, xml)
            - data from Auditree OSCO fetcher/check (json)
        """
        results = None
        if results is None:
            results = self._ingest_xml(blob)
        if results is None:
            results = self._ingest_json(blob)
        if results is None:
            results = self._ingest_yaml(blob)
        return results
