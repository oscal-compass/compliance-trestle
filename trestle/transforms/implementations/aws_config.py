# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2026 IBM Corp. All rights reserved.
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
"""Facilitate OSCAL-AWS Config transformation.

Transforms AWS Config compliance evaluation results (the JSON shape returned
by the AWS Config ``get-compliance-details-by-config-rule`` /
``get-compliance-details-by-resource`` APIs: a top-level ``EvaluationResults``
list of ``EvaluationResult`` objects, see
https://docs.aws.amazon.com/config/latest/APIReference/API_EvaluationResult.html)
into OSCAL Assessment Results, following the same
Task + ResultsTransformer + private results-factory shape used by
``osco.py`` / ``tanium.py`` in this package.
"""

import json
import logging
import uuid
from typing import Any, Dict, List, ValuesView

from pydantic import AnyUrl

from trestle.oscal.assessment_results import LocalDefinitions1, Observation, Result
from trestle.oscal.common import (
    ControlSelectionsAll,
    IncludeAll,
    InventoryItem,
    Property,
    ReviewedControls,
    SubjectReference,
)
from trestle.transforms.results import Results
from trestle.transforms.transformer_factory import ResultsTransformer

logger = logging.getLogger(__name__)

_COMPLIANCE_TYPES = {'COMPLIANT', 'NON_COMPLIANT', 'NOT_APPLICABLE', 'INSUFFICIENT_DATA'}


class AwsConfigResultToOscalARTransformer(ResultsTransformer):
    """Interface for AWS Config transformer."""

    def __init__(self) -> None:
        """Initialize."""
        self._modes: Dict[str, Any] = {}

    def set_modes(self, modes: Dict[str, Any]) -> None:
        """Set the transformation modes."""
        if modes is not None:
            self._modes = modes

    @property
    def analysis(self) -> List[str]:
        """Return statistics."""
        return self._results_factory.analysis if hasattr(self, '_results_factory') else []

    def transform(self, blob: str) -> Results:
        """
        Transform AWS Config evaluation results into OSCAL results.

        Args:
            blob: text (json) blob containing AWS Config evaluation results,
                shaped as ``{"EvaluationResults": [EvaluationResult, ...]}``.

        Returns:
            Results containing a single OSCAL Result with one Observation
            per input EvaluationResult.
        """
        self._results_factory = _OscalResultsFactory(self.get_timestamp())
        data = json.loads(blob)
        for evaluation_result in data.get('EvaluationResults', []):
            self._results_factory.ingest(evaluation_result)
        results = Results.model_construct(root=[])
        results.root.append(self._results_factory.result)
        return results


class _OscalResultsFactory:
    """Build OSCAL entities from AWS Config EvaluationResult objects."""

    def __init__(self, timestamp: str | None = None) -> None:
        """Initialize."""
        self._timestamp = timestamp if timestamp is not None else ResultsTransformer.get_timestamp()
        self._observation_list: List[Observation] = []
        self._inventory_map: Dict[str, InventoryItem] = {}
        self._ns = AnyUrl('https://oscal-compass.github.io/compliance-trestle/schemas/oscal/ar/aws-config')

    @property
    def inventory(self) -> ValuesView[InventoryItem]:
        """OSCAL inventory."""
        return self._inventory_map.values()

    @property
    def local_definitions(self) -> LocalDefinitions1:
        """OSCAL local definitions."""
        local_def_data = {'inventory-items': list(self.inventory)}
        return LocalDefinitions1.model_validate(local_def_data)

    @property
    def observations(self) -> List[Observation]:
        """OSCAL observations."""
        return self._observation_list

    @property
    def reviewed_controls(self) -> ReviewedControls:
        """OSCAL reviewed controls.

        AWS Config rules are not, by default, mapped to a specific OSCAL
        catalog's control identifiers -- that mapping is organization- and
        catalog-specific. Following the same approach as the OSCO
        transformer for the analogous case, an include-all control
        selection is emitted here; downstream tooling that has the
        rule-to-control mapping can refine this.
        """
        include_all = IncludeAll()
        control_sel_all = ControlSelectionsAll.model_validate({'include-all': include_all})
        reviewed_controls_data = {'control-selections': [control_sel_all]}
        return ReviewedControls.model_validate(reviewed_controls_data)

    @property
    def result(self) -> Result:
        """OSCAL result."""
        result_data = {
            'uuid': str(uuid.uuid4()),
            'title': 'AWS Config Compliance Evaluation',
            'description': 'AWS Config Rule Compliance Evaluation Results',
            'start': self._timestamp,
            'end': self._timestamp,
            'reviewed-controls': self.reviewed_controls,
        }
        if self.inventory:
            result_data['local-definitions'] = self.local_definitions
        if self.observations:
            result_data['observations'] = self.observations
        return Result.model_validate(result_data)

    @property
    def analysis(self) -> List[str]:
        """OSCAL statistics."""
        return [f'inventory: {len(self.inventory)}', f'observations: {len(self.observations)}']

    def _inventory_key(self, resource_type: str, resource_id: str) -> str:
        return f'{resource_type}::{resource_id}'

    def _inventory_extract(self, resource_type: str, resource_id: str) -> str:
        """Get (or create) the inventory-item uuid for an AWS resource, returning its uuid."""
        key = self._inventory_key(resource_type, resource_id)
        if key not in self._inventory_map:
            props = [
                Property.model_construct(name='resource-type', value=resource_type, ns=self._ns),
                Property.model_construct(name='resource-id', value=resource_id, ns=self._ns),
            ]
            item = InventoryItem.model_validate(
                {'uuid': str(uuid.uuid4()), 'description': f'{resource_type} {resource_id}', 'props': props}
            )
            self._inventory_map[key] = item
        return self._inventory_map[key].uuid

    def _observation_properties(self, evaluation_result: Dict[str, Any]) -> List[Property]:
        """Build the props list for one EvaluationResult."""
        props = []
        qualifier = evaluation_result.get('EvaluationResultIdentifier', {}).get('EvaluationResultQualifier', {})
        compliance_type = evaluation_result.get('ComplianceType')
        if compliance_type is not None and compliance_type not in _COMPLIANCE_TYPES:
            logger.warning(f'unexpected ComplianceType {compliance_type!r}')
        for name, value in (
            ('config-rule-name', qualifier.get('ConfigRuleName')),
            ('evaluation-mode', qualifier.get('EvaluationMode')),
            ('compliance-type', compliance_type),
            ('config-rule-invoked-time', evaluation_result.get('ConfigRuleInvokedTime')),
            ('result-token', evaluation_result.get('ResultToken')),
        ):
            if value is not None:
                # Only compliance-type is classed for downstream filtering,
                # matching osco.py's scc_result pattern. Prop names stay
                # hyphenated (OSCAL); class_ uses the underscored identifier
                # style of osco's scc_* values.
                class_ = 'aws_config_compliance' if name == 'compliance-type' else None
                if class_:
                    props.append(Property.model_construct(name=name, value=str(value), ns=self._ns, class_=class_))
                else:
                    props.append(Property.model_construct(name=name, value=str(value), ns=self._ns))
        return props

    def ingest(self, evaluation_result: Dict[str, Any]) -> None:
        """Ingest one AWS Config EvaluationResult, producing an Observation."""
        qualifier = evaluation_result.get('EvaluationResultIdentifier', {}).get('EvaluationResultQualifier', {})
        resource_type = qualifier.get('ResourceType', 'Unknown')
        resource_id = qualifier.get('ResourceId', 'Unknown')
        rule_name = qualifier.get('ConfigRuleName', 'Unknown')
        inventory_ref = self._inventory_extract(resource_type, resource_id)

        subject_reference = SubjectReference.model_validate({'subject-uuid': inventory_ref, 'type': 'inventory-item'})
        annotation = evaluation_result.get('Annotation')
        description = f'{rule_name} ({resource_type} {resource_id})'
        if annotation:
            description = f'{description}: {annotation}'
        collected = (
            evaluation_result.get('ResultRecordedTime')
            or evaluation_result.get('ConfigRuleInvokedTime')
            or self._timestamp
        )
        observation_data = {
            'uuid': str(uuid.uuid4()),
            'description': description,
            'methods': ['TEST-AUTOMATED'],
            'collected': collected,
            'subjects': [subject_reference],
        }
        props = self._observation_properties(evaluation_result)
        if props:
            observation_data['props'] = props
        observation = Observation.model_validate(observation_data)
        self._observation_list.append(observation)
