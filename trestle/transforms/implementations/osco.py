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
"""Facilitate OSCAL-OSCO transformation."""

import json
import logging
from typing import Dict, List

from ruamel.yaml import YAML

from trestle.oscal.profile import Profile
from trestle.transforms.results import Results
from trestle.transforms.transformer_factory import FromOscalTransformer
from trestle.transforms.transformer_factory import ResultsTransformer
from trestle.transforms.utils.osco_helper import ResultsMgr

logger = logging.getLogger(__name__)


class OscoTransformer(ResultsTransformer):
    """Interface for Osco transformer."""

    def __init__(self) -> None:
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


class ProfileToOscoTransformer(FromOscalTransformer):
    """Interface for Profile to Osco transformer."""

    def __init__(
        self,
        extends='ocp4-cis-node',
        api_version='compliance.openshift.io/v1alpha1',
        kind='TailoredProfile',
        name='customized-tailored-profile',
        namespace='openshift-compliance',
    ) -> None:
        """Initialize."""
        self._extends = extends
        self._api_version = api_version
        self._kind = kind
        self._name = name
        self._namespace = namespace

    def transform(self, profile: Profile) -> str:
        """Transform the Profile into a OSCO yaml."""
        # set values
        set_values = self._get_set_values(profile)
        # spec
        spec = {
            'description': self._get_metadata_prop_value(profile, 'profile_mnemonic', self._name),
            'extends': self._get_metadata_prop_value(profile, 'base_profile_mnemonic', self._extends),
            'title': profile.metadata.title,
            'setValues': set_values,
        }
        disable_rules = self._get_disable_rules(profile)
        if len(disable_rules) > 0:
            spec['disableRules'] = disable_rules
        # yaml data
        ydata = {
            'apiVersion': self._api_version,
            'kind': self._kind,
            'metadata': {
                'name': self._get_metadata_prop_value(profile, 'profile_mnemonic', self._name),
                'namespace': self._namespace,
            },
            'spec': spec,
        }
        return json.dumps(ydata)

    def _get_set_values(self, profile) -> List[Dict]:
        """Extract set_paramater name/value pairs from profile."""
        set_values = []
        for set_parameter in profile.modify.set_parameters:
            name = set_parameter.param_id
            parameter_value = set_parameter.values[0]
            value = parameter_value.__root__
            rationale = self._get_rationale_for_set_value()
            set_value = {'name': name, 'value': value, 'rationale': rationale}
            set_values.append(set_value)
        return set_values

    def _get_metadata_prop_value(self, profile, name, default_) -> str:
        """Extract metadata prop or else default if not present."""
        if profile.metadata.props is not None:
            for prop in profile.metadata.props:
                if prop.name == name:
                    return prop.value
        logger.info(f'using default: {name} = {default_}')
        return default_

    def _get_disable_rules(self, profile) -> List[str]:
        """Extract disabled rules."""
        value = []
        if profile.imports is not None:
            for item in profile.imports:
                if item.exclude_controls is not None:
                    for control in item.exclude_controls:
                        if control.with_ids is not None:
                            for with_id in control.with_ids:
                                name = with_id.__root__
                                rationale = self._get_rationale_for_disable_rule()
                                entry = {'name': name, 'rationale': rationale}
                                value.append(entry)
        return value

    def _get_rationale_for_set_value(self) -> str:
        """Rationale for set value."""
        return 'not determinable from specification'

    def _get_rationale_for_disable_rule(self) -> str:
        """Rationale for disable rule."""
        return 'not determinable from specification'
