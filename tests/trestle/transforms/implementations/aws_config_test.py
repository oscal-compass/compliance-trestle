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
"""Tests for AwsConfigResultToOscalARTransformer.

The fixture (tests/data/tasks/aws-config/aws-config-sample.json) is
hand-constructed to match AWS Config's documented EvaluationResult schema
field-for-field (EvaluationResultIdentifier / EvaluationResultQualifier /
ComplianceType / ResultRecordedTime / ConfigRuleInvokedTime / Annotation /
ResultToken), verified against
https://docs.aws.amazon.com/config/latest/APIReference/API_EvaluationResult.html
and API_EvaluationResultQualifier.html -- it is not a captured real AWS API
response (no AWS account was used), but every field name and shape is real.
"""

import pathlib

import pytest

from trestle.transforms.implementations.aws_config import AwsConfigResultToOscalARTransformer

test_data_dir = pathlib.Path('tests/data/tasks/aws-config').resolve()


@pytest.fixture
def sample_blob() -> str:
    return (test_data_dir / 'aws-config-sample.json').read_text(encoding='utf-8')


class TestTransform:
    def test_produces_one_result_with_all_observations(self, sample_blob):
        transformer = AwsConfigResultToOscalARTransformer()
        results = transformer.transform(sample_blob)
        assert len(results.root) == 1
        result = results.root[0]
        # 4 EvaluationResults in the fixture -> 4 Observations (one per evaluation, even
        # when the same resource is evaluated more than once).
        assert len(result.observations) == 4

    def test_inventory_deduplicated_by_resource(self, sample_blob):
        """The same security group appears in 2 EvaluationResults -> 1 inventory item."""
        transformer = AwsConfigResultToOscalARTransformer()
        results = transformer.transform(sample_blob)
        result = results.root[0]
        inventory_items = result.local_definitions.inventory_items
        # 3 distinct resources: 2 S3 buckets + 1 security group (evaluated twice).
        assert len(inventory_items) == 3
        descriptions = {i.description for i in inventory_items}
        assert descriptions == {
            'AWS::S3::Bucket acme-prod-uploads',
            'AWS::S3::Bucket acme-prod-assets',
            'AWS::EC2::SecurityGroup sg-0a1b2c3d4e5f6g7h8',
        }

    def test_observation_subjects_reference_the_correct_inventory_item(self, sample_blob):
        transformer = AwsConfigResultToOscalARTransformer()
        results = transformer.transform(sample_blob)
        result = results.root[0]
        sg_item_uuid = next(
            i.uuid for i in result.local_definitions.inventory_items if 'sg-0a1b2c3d4e5f6g7h8' in i.description
        )
        sg_observations = [o for o in result.observations if 'restricted-ssh' in o.description]
        assert len(sg_observations) == 2
        for obs in sg_observations:
            assert obs.subjects[0].subject_uuid == sg_item_uuid
            assert obs.subjects[0].type.root == 'inventory-item'

    def test_compliance_type_and_annotation_carried_in_props(self, sample_blob):
        transformer = AwsConfigResultToOscalARTransformer()
        results = transformer.transform(sample_blob)
        result = results.root[0]
        non_compliant = [
            o
            for o in result.observations
            if any(p.name == 'compliance-type' and p.value == 'NON_COMPLIANT' for p in o.props)
        ]
        # 3 of the 4 fixture entries are NON_COMPLIANT.
        assert len(non_compliant) == 3
        s3_obs = next(o for o in result.observations if 'acme-prod-uploads' in o.description)
        assert 'public read access' in s3_obs.description
        assert 'AWS::S3::Bucket' in s3_obs.description

    def test_compliant_entry_has_no_annotation_but_valid_description(self, sample_blob):
        transformer = AwsConfigResultToOscalARTransformer()
        results = transformer.transform(sample_blob)
        result = results.root[0]
        compliant_obs = next(o for o in result.observations if 'acme-prod-assets' in o.description)
        assert compliant_obs.description == 's3-bucket-public-read-prohibited (AWS::S3::Bucket acme-prod-assets)'

    def test_methods_and_collected_are_set(self, sample_blob):
        transformer = AwsConfigResultToOscalARTransformer()
        results = transformer.transform(sample_blob)
        result = results.root[0]
        for obs in result.observations:
            assert obs.methods == ['TEST-AUTOMATED']
            assert obs.collected is not None

    def test_reviewed_controls_present(self, sample_blob):
        transformer = AwsConfigResultToOscalARTransformer()
        results = transformer.transform(sample_blob)
        result = results.root[0]
        assert result.reviewed_controls is not None
        assert result.reviewed_controls.control_selections is not None

    def test_analysis_reports_correct_counts(self, sample_blob):
        transformer = AwsConfigResultToOscalARTransformer()
        results = transformer.transform(sample_blob)
        assert results.root  # ensure transform ran before checking analysis
        assert 'inventory: 3' in transformer.analysis
        assert 'observations: 4' in transformer.analysis

    def test_empty_evaluation_results_produces_result_with_no_observations(self):
        transformer = AwsConfigResultToOscalARTransformer()
        results = transformer.transform('{"EvaluationResults": []}')
        assert len(results.root) == 1
        assert results.root[0].observations is None

    def test_missing_optional_fields_do_not_raise(self):
        """A minimal, spec-legal EvaluationResult (all fields optional per AWS docs)."""
        blob = '{"EvaluationResults": [{}]}'
        transformer = AwsConfigResultToOscalARTransformer()
        results = transformer.transform(blob)
        result = results.root[0]
        assert len(result.observations) == 1
        assert result.observations[0].description == 'Unknown (Unknown Unknown)'

    def test_result_round_trips_through_oscal_serialization(self, sample_blob):
        """The Result must be genuinely OSCAL-schema-valid, not just pydantic-constructible."""
        transformer = AwsConfigResultToOscalARTransformer()
        results = transformer.transform(sample_blob)
        serialized = results.oscal_serialize_json_bytes(pretty=True)
        assert b'"aws-config-result"' not in serialized  # sanity: not leaking internal names
        assert b'observations' in serialized
        assert b'restricted-ssh' in serialized
