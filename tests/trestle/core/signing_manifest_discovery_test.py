# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2026 The OSCAL Compass Authors. All rights reserved.
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
"""Tests for automatic OSCAL signing manifest discovery."""

import json
import pathlib
from typing import Any, Dict, List

import pytest
from _pytest.monkeypatch import MonkeyPatch

from tests import test_utils
import trestle.core.signing_manifest_discovery as discovery
from trestle.common import const, file_utils
from trestle.common.err import TrestleError
from trestle.core import generators
from trestle.core.remote.cache import FetcherFactory
from trestle.core.signing_manifest import load_signing_manifest
from trestle.core.signing_manifest_discovery import (
    SigningManifestDiscovery,
    discover_signing_manifest,
    write_signing_manifest,
)
from trestle.oscal import assessment_plan, assessment_results, common, poam


def _read_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding=const.FILE_ENCODING))


def _write_json(path: pathlib.Path, data: Dict[str, Any]) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding=const.FILE_ENCODING)
    return path


def _write_catalog(path: pathlib.Path) -> pathlib.Path:
    return _write_json(path, _read_json(test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json'))


def _write_profile(path: pathlib.Path, hrefs: List[str], back_matter: Dict[str, Any] | None = None) -> pathlib.Path:
    data = _read_json(test_utils.JSON_TEST_DATA_PATH / 'simple_test_profile.json')
    profile = data['profile']
    profile['imports'] = [{'href': href, 'include-all': {}} for href in hrefs]
    profile.pop('back_matter', None)
    profile.pop('back-matter', None)
    if back_matter is not None:
        profile['back-matter'] = back_matter
    return _write_json(path, data)


def _write_ssp(path: pathlib.Path, profile_href: str) -> pathlib.Path:
    source = test_utils.TEST_DIR / 'data/author/ssp/ssp_example.json'
    data = _read_json(source)
    data['system-security-plan']['import-profile']['href'] = profile_href
    return _write_json(path, data)


def _write_component_definition(
    path: pathlib.Path,
    hrefs: List[str] | None = None,
    component_source: str | None = None,
    capability_source: str | None = None,
) -> pathlib.Path:
    source = test_utils.TEST_DIR / 'data/validate/component-definitions/x1/component-definition.json'
    data = _read_json(source)
    component_definition = data['component-definition']
    if hrefs:
        component_definition['import-component-definitions'] = [{'href': href} for href in hrefs]
    else:
        component_definition.pop('import-component-definitions', None)
    if component_source:
        component_definition['components'][0]['control-implementations'] = [
            {
                'uuid': '00000000-0000-4000-8000-000000000001',
                'source': component_source,
                'description': 'Component control implementation.',
                'implemented-requirements': [
                    {
                        'uuid': '00000000-0000-4000-8000-000000000004',
                        'control-id': 'ac-1',
                        'description': 'Component implemented requirement.',
                    }
                ],
            }
        ]
    if capability_source:
        component_definition['capabilities'] = [
            {
                'uuid': '00000000-0000-4000-8000-000000000002',
                'name': 'test-capability',
                'description': 'Test capability.',
                'control-implementations': [
                    {
                        'uuid': '00000000-0000-4000-8000-000000000003',
                        'source': capability_source,
                        'description': 'Capability control implementation.',
                        'implemented-requirements': [
                            {
                                'uuid': '00000000-0000-4000-8000-000000000005',
                                'control-id': 'ac-1',
                                'description': 'Capability implemented requirement.',
                            }
                        ],
                    }
                ],
            }
        ]
    return _write_json(path, data)


def _write_assessment_plan(path: pathlib.Path, ssp_href: str) -> pathlib.Path:
    model = generators.generate_sample_model(assessment_plan.AssessmentPlan)
    model.import_ssp.href = ssp_href
    path.parent.mkdir(parents=True, exist_ok=True)
    model.oscal_write(path)
    return path


def _write_assessment_results(path: pathlib.Path, assessment_plan_href: str) -> pathlib.Path:
    model = generators.generate_sample_model(assessment_results.AssessmentResults)
    model.import_ap.href = assessment_plan_href
    path.parent.mkdir(parents=True, exist_ok=True)
    model.oscal_write(path)
    return path


def _write_poam(path: pathlib.Path, ssp_href: str | None = None) -> pathlib.Path:
    model = generators.generate_sample_model(poam.PlanOfActionAndMilestones)
    model.import_ssp = common.ImportSsp(href=ssp_href) if ssp_href else None
    path.parent.mkdir(parents=True, exist_ok=True)
    model.oscal_write(path)
    return path


def _write_mapping_collection(
    path: pathlib.Path,
    source_href: str,
    target_href: str,
    source_type: str = const.MODEL_TYPE_CATALOG,
    target_type: str = const.MODEL_TYPE_PROFILE,
) -> pathlib.Path:
    data = _read_json(test_utils.JSON_TEST_DATA_PATH / 'simple_mapping.json')
    mapping = data['mapping-collection']['mappings'][0]
    mapping['source-resource'] = {'type': source_type, 'href': source_href}
    mapping['target-resource'] = {'type': target_type, 'href': target_href}
    return _write_json(path, data)


def _artifact_names(manifest_path: pathlib.Path) -> List[str]:
    return [artifact.name for artifact in load_signing_manifest(manifest_path).artifacts]


def _mock_remote_documents(
    monkeypatch: MonkeyPatch, tmp_path: pathlib.Path, documents: Dict[str, str], expected_block_private_ips: bool = True
) -> List[str]:
    remote_root = tmp_path / 'remote-source'
    remote_root.mkdir()
    remote_paths: Dict[str, pathlib.Path] = {}
    for index, (uri, content) in enumerate(documents.items()):
        remote_path = remote_root / f'{index}.json'
        remote_path.write_bytes(content.encode(const.FILE_ENCODING))
        remote_paths[uri] = remote_path

    requested_uris: List[str] = []

    class _FakeFetcher:
        def __init__(self, cached_path: pathlib.Path) -> None:
            self.cached_path = cached_path

        def get_cached_path(self, force_update: bool = False) -> pathlib.Path:
            assert not force_update
            return self.cached_path

    def _get_fetcher(
        trestle_root: pathlib.Path, uri: str, max_size_bytes: int | None = None, block_private_ips: bool | None = None
    ) -> _FakeFetcher:
        assert (trestle_root / const.TRESTLE_CONFIG_DIR).is_dir()
        assert max_size_bytes is not None
        assert 0 < max_size_bytes <= discovery.MAX_REMOTE_ARTIFACT_SIZE_BYTES
        assert block_private_ips is expected_block_private_ips
        requested_uris.append(uri)
        return _FakeFetcher(remote_paths[uri])

    monkeypatch.setattr(FetcherFactory, 'get_fetcher', staticmethod(_get_fetcher))
    return requested_uris


def test_discover_signing_manifest_follows_nested_profiles_and_deduplicates_diamond(tmp_path: pathlib.Path) -> None:
    """Discovery should be deterministic, root-first, and deduplicate shared dependencies."""
    package_root = tmp_path / 'package'
    catalog = _write_catalog(package_root / 'catalogs/nist/catalog.json')
    first_nested = _write_profile(package_root / 'profiles/first/profile.json', ['../../catalogs/nist/catalog.json'])
    second_nested = _write_profile(package_root / 'profiles/second/profile.json', ['../../catalogs/nist/catalog.json'])
    root_profile = _write_profile(
        package_root / 'profiles/root/profile.json', ['../first/profile.json', '../second/profile.json']
    )
    ssp = _write_ssp(package_root / 'system-security-plans/acme/ssp.json', '../../profiles/root/profile.json')
    output = package_root / 'package.json'

    manifest = discover_signing_manifest(ssp, output, [])
    write_signing_manifest(manifest)

    assert [artifact.name for artifact in manifest.artifacts] == [
        'system-security-plans/acme/ssp.json',
        'profiles/root/profile.json',
        'profiles/first/profile.json',
        'catalogs/nist/catalog.json',
        'profiles/second/profile.json',
    ]
    assert manifest.primary_artifact == 'system-security-plans/acme/ssp.json'
    assert manifest.artifacts[3].path == catalog.resolve()
    assert manifest.artifacts[2].path == first_nested.resolve()
    assert manifest.artifacts[4].path == second_nested.resolve()
    assert manifest.artifacts[1].path == root_profile.resolve()
    assert _artifact_names(output) == [artifact.name for artifact in manifest.artifacts]


def test_discover_signing_manifest_preserves_duplicate_basenames(tmp_path: pathlib.Path) -> None:
    """Artifact names should use relative paths rather than colliding basenames."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalogs/a/catalog.json')
    _write_catalog(package_root / 'catalogs/b/catalog.json')
    _write_profile(package_root / 'profiles/profile.json', ['../catalogs/a/catalog.json', '../catalogs/b/catalog.json'])
    ssp = _write_ssp(package_root / 'ssp.json', 'profiles/profile.json')

    manifest = discover_signing_manifest(ssp, package_root / 'package.json', [])

    assert [artifact.name for artifact in manifest.artifacts] == [
        'ssp.json',
        'profiles/profile.json',
        'catalogs/a/catalog.json',
        'catalogs/b/catalog.json',
    ]


def test_discover_signing_manifest_rejects_cycles(tmp_path: pathlib.Path) -> None:
    """Profile import cycles should fail with the full local dependency chain."""
    package_root = tmp_path / 'package'
    _write_profile(package_root / 'profiles/a.json', ['b.json'])
    _write_profile(package_root / 'profiles/b.json', ['a.json'])
    ssp = _write_ssp(package_root / 'ssp.json', 'profiles/a.json')

    with pytest.raises(TrestleError, match=r'Circular OSCAL dependency detected: profiles/a.json.*profiles/b.json'):
        discover_signing_manifest(ssp, package_root / 'package.json', [])


def test_discover_signing_manifest_limits_dependency_depth(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Discovery should reject dependency graphs deeper than its configured limit."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalog.json')
    _write_profile(package_root / 'nested.json', ['catalog.json'])
    profile = _write_profile(package_root / 'profile.json', ['nested.json'])
    monkeypatch.setattr(discovery, 'MAX_DISCOVERY_DEPTH', 2)

    with pytest.raises(TrestleError, match='exceeds maximum depth of 2'):
        discover_signing_manifest(profile, package_root / 'package.json', [])


def test_discover_signing_manifest_limits_artifact_count(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Discovery should reject graphs containing too many distinct artifacts."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'first.json')
    _write_catalog(package_root / 'second.json')
    profile = _write_profile(package_root / 'profile.json', ['first.json', 'second.json'])
    monkeypatch.setattr(discovery, 'MAX_DISCOVERED_ARTIFACTS', 2)

    with pytest.raises(TrestleError, match='exceeds maximum of 2 artifacts'):
        discover_signing_manifest(profile, package_root / 'package.json', [])


def test_discover_signing_manifest_resolves_back_matter_json_link(tmp_path: pathlib.Path) -> None:
    """A local profile #uuid import should resolve through exactly one JSON rlink."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalogs/catalog.json')
    resource_uuid = '657e15f4-bee9-45fb-a43d-44d7f7f2abfa'
    _write_profile(
        package_root / 'profiles/profile.json',
        [f'#{resource_uuid}'],
        {
            'resources': [
                {
                    'uuid': resource_uuid,
                    'rlinks': [{'href': '../catalogs/catalog.xml'}, {'href': '../catalogs/catalog.json'}],
                }
            ]
        },
    )
    ssp = _write_ssp(package_root / 'ssp.json', 'profiles/profile.json')

    manifest = discover_signing_manifest(ssp, package_root / 'package.json', [])

    assert [artifact.name for artifact in manifest.artifacts] == [
        'ssp.json',
        'profiles/profile.json',
        'catalogs/catalog.json',
    ]


@pytest.mark.parametrize('json_links', [[], ['../catalogs/one.json', '../catalogs/two.json']])
def test_discover_signing_manifest_rejects_unusable_back_matter_links(
    tmp_path: pathlib.Path, json_links: List[str]
) -> None:
    """Back-matter imports should identify one resource containing one usable JSON link."""
    package_root = tmp_path / 'package'
    resource_uuid = '657e15f4-bee9-45fb-a43d-44d7f7f2abfa'
    resource: Dict[str, Any] = {'uuid': resource_uuid}
    if json_links:
        resource['rlinks'] = [{'href': href} for href in json_links]
    _write_profile(package_root / 'profile.json', [f'#{resource_uuid}'], {'resources': [resource]})
    ssp = _write_ssp(package_root / 'ssp.json', 'profile.json')

    with pytest.raises(TrestleError, match='must provide one JSON rlink'):
        discover_signing_manifest(ssp, package_root / 'package.json', [])


def test_discover_signing_manifest_rejects_unknown_back_matter_resource(tmp_path: pathlib.Path) -> None:
    """A #uuid import must identify exactly one back-matter resource."""
    package_root = tmp_path / 'package'
    _write_profile(package_root / 'profile.json', ['#657e15f4-bee9-45fb-a43d-44d7f7f2abfa'])
    ssp = _write_ssp(package_root / 'ssp.json', 'profile.json')

    with pytest.raises(TrestleError, match='does not identify one back-matter resource'):
        discover_signing_manifest(ssp, package_root / 'package.json', [])


def test_discover_signing_manifest_follows_explicit_component_definition_includes(tmp_path: pathlib.Path) -> None:
    """Explicit component definitions should be included and recursively discovered."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalog.json')
    _write_profile(package_root / 'profile.json', ['catalog.json'])
    ssp = _write_ssp(package_root / 'ssp.json', 'profile.json')
    nested = _write_component_definition(package_root / 'component-definitions/nested.json')
    root = _write_component_definition(package_root / 'component-definitions/root.json', ['nested.json'])

    manifest = discover_signing_manifest(ssp, package_root / 'package.json', [root])

    assert [artifact.name for artifact in manifest.artifacts] == [
        'ssp.json',
        'profile.json',
        'catalog.json',
        'component-definitions/root.json',
        'component-definitions/nested.json',
    ]
    assert manifest.artifacts[-1].path == nested.resolve()


def test_discover_signing_manifest_follows_component_definition_control_sources(tmp_path: pathlib.Path) -> None:
    """Component and capability control sources should include their profiles and catalogs."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalogs/catalog.json')
    _write_profile(package_root / 'profiles/profile.json', ['../catalogs/catalog.json'])
    component_definition = _write_component_definition(
        package_root / 'component-definitions/component-definition.json',
        component_source='../profiles/profile.json',
        capability_source='../catalogs/catalog.json',
    )

    manifest = discover_signing_manifest(component_definition, package_root / 'package.json', [])

    assert [artifact.name for artifact in manifest.artifacts] == [
        'component-definitions/component-definition.json',
        'profiles/profile.json',
        'catalogs/catalog.json',
    ]


def test_discover_signing_manifest_supports_trestle_uris(tmp_path: pathlib.Path) -> None:
    """Trestle URIs should resolve from the containing Trestle workspace root."""
    package_root = tmp_path / 'workspace'
    (package_root / const.TRESTLE_CONFIG_DIR).mkdir(parents=True)
    _write_catalog(package_root / 'catalogs/nist/catalog.json')
    _write_profile(package_root / 'profiles/profile.json', ['trestle://catalogs/nist/catalog.json'])
    ssp = _write_ssp(package_root / 'ssp.json', 'trestle://profiles/profile.json')

    manifest = discover_signing_manifest(ssp, package_root / 'package.json', [])

    assert [artifact.name for artifact in manifest.artifacts] == [
        'ssp.json',
        'profiles/profile.json',
        'catalogs/nist/catalog.json',
    ]


@pytest.mark.parametrize('scheme, in_workspace', [('https', False), ('sftp', True)])
def test_discover_signing_manifest_fetches_remote_dependencies_recursively(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch, scheme: str, in_workspace: bool
) -> None:
    """Remote dependencies should be safely fetched and vendored inside the package."""
    package_root = tmp_path / 'package'
    if in_workspace:
        (package_root / const.TRESTLE_CONFIG_DIR).mkdir(parents=True)
    profile_uri = f'{scheme}://example.com/oscal/profiles/profile.json'
    catalog_uri = f'{scheme}://example.com/oscal/catalogs/catalog.json'
    profile_data = _read_json(test_utils.JSON_TEST_DATA_PATH / 'simple_test_profile.json')
    profile_data['profile']['imports'] = [{'href': '../catalogs/catalog.json', 'include-all': {}}]
    profile_data['profile'].pop('back_matter', None)
    requested_uris = _mock_remote_documents(
        monkeypatch,
        tmp_path,
        {
            profile_uri: json.dumps(profile_data),
            catalog_uri: (test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json').read_text(
                encoding=const.FILE_ENCODING
            ),
        },
    )
    ssp = _write_ssp(package_root / 'ssp.json', profile_uri)
    output = package_root / 'package.json'

    manifest = discover_signing_manifest(ssp, output, [])
    write_signing_manifest(manifest)

    assert requested_uris == [profile_uri, catalog_uri]
    assert manifest.primary_artifact == 'ssp.json'
    assert [artifact.name for artifact in manifest.artifacts][0] == 'ssp.json'
    assert all(artifact.name.startswith('remote/') for artifact in manifest.artifacts[1:])
    assert all(artifact.path.is_file() for artifact in manifest.artifacts)
    assert _artifact_names(output) == [artifact.name for artifact in manifest.artifacts]


def test_discover_signing_manifest_reuses_matching_remote_artifact(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Repeated discovery should reuse unchanged downloaded package content."""
    package_root = tmp_path / 'package'
    remote_uri = 'https://example.com/catalog.json'
    catalog = (test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json').read_text(encoding=const.FILE_ENCODING)
    requested_uris = _mock_remote_documents(monkeypatch, tmp_path, {remote_uri: catalog})
    profile = _write_profile(package_root / 'profile.json', [remote_uri])

    first = discover_signing_manifest(profile, package_root / 'first-package.json', [])
    second = discover_signing_manifest(profile, package_root / 'second-package.json', [])

    assert first.artifacts[1].path == second.artifacts[1].path
    assert requested_uris == [remote_uri, remote_uri]


def test_discover_signing_manifest_fetches_duplicate_remote_uri_once(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """A repeated remote URI in one graph should be fetched only once."""
    package_root = tmp_path / 'package'
    remote_uri = 'https://example.com/catalog.json'
    catalog = (test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json').read_text(encoding=const.FILE_ENCODING)
    requested_uris = _mock_remote_documents(monkeypatch, tmp_path, {remote_uri: catalog})
    profile = _write_profile(package_root / 'profile.json', [remote_uri, remote_uri])

    manifest = discover_signing_manifest(profile, package_root / 'package.json', [])

    assert requested_uris == [remote_uri]
    assert len(manifest.artifacts) == 2


def test_discover_signing_manifest_allows_explicit_private_uri_opt_in(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Explicit opt-in should disable private-range blocking for discovery fetchers."""
    package_root = tmp_path / 'package'
    remote_uri = 'https://internal.example/catalog.json'
    catalog = (test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json').read_text(encoding=const.FILE_ENCODING)
    requested_uris = _mock_remote_documents(
        monkeypatch, tmp_path, {remote_uri: catalog}, expected_block_private_ips=False
    )
    profile = _write_profile(package_root / 'profile.json', [remote_uri])

    discover_signing_manifest(profile, package_root / 'package.json', [], allow_private_uris=True)

    assert requested_uris == [remote_uri]


def test_discover_signing_manifest_blocks_private_uri_by_default(tmp_path: pathlib.Path) -> None:
    """Automatic discovery should reject private-network dependencies before fetching them."""
    package_root = tmp_path / 'package'
    profile = _write_profile(package_root / 'profile.json', ['https://10.0.0.1/catalog.json'])

    with pytest.raises(TrestleError, match='10.0.0.0/8'):
        discover_signing_manifest(profile, package_root / 'package.json', [])


def test_discover_signing_manifest_limits_remote_artifacts_before_fetch(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """An exhausted artifact budget should prevent another remote request."""
    package_root = tmp_path / 'package'
    remote_uri = 'https://example.com/catalog.json'
    catalog = (test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json').read_text(encoding=const.FILE_ENCODING)
    requested_uris = _mock_remote_documents(monkeypatch, tmp_path, {remote_uri: catalog})
    profile = _write_profile(package_root / 'profile.json', [remote_uri])
    monkeypatch.setattr(discovery, 'MAX_DISCOVERED_ARTIFACTS', 1)

    with pytest.raises(TrestleError, match='exceeds maximum of 1 artifacts'):
        discover_signing_manifest(profile, package_root / 'package.json', [])

    assert not requested_uris


def test_discover_signing_manifest_limits_total_remote_size(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """Discovery should stop before a fetch that would exceed the total remote byte budget."""
    package_root = tmp_path / 'package'
    first_uri = 'https://example.com/first.json'
    second_uri = 'https://example.com/second.json'
    catalog = (test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json').read_text(encoding=const.FILE_ENCODING)
    requested_uris = _mock_remote_documents(monkeypatch, tmp_path, {first_uri: catalog, second_uri: catalog})
    profile = _write_profile(package_root / 'profile.json', [first_uri, second_uri])
    monkeypatch.setattr(discovery, 'MAX_TOTAL_REMOTE_SIZE_BYTES', len(catalog.encode(const.FILE_ENCODING)))

    with pytest.raises(TrestleError, match='exceed maximum total size'):
        discover_signing_manifest(profile, package_root / 'package.json', [])

    assert requested_uris == [first_uri]


def test_discover_signing_manifest_rejects_fetcher_size_limit_violation(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """Discovery should verify the fetched size even when a fetcher fails to enforce its limit."""
    package_root = tmp_path / 'package'
    remote_uri = 'https://example.com/catalog.json'
    catalog = (test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json').read_text(encoding=const.FILE_ENCODING)
    _mock_remote_documents(monkeypatch, tmp_path, {remote_uri: catalog})
    profile = _write_profile(package_root / 'profile.json', [remote_uri])
    monkeypatch.setattr(discovery, 'MAX_TOTAL_REMOTE_SIZE_BYTES', 1)

    with pytest.raises(TrestleError, match='exceeds maximum size of 1 byte'):
        discover_signing_manifest(profile, package_root / 'package.json', [])


def test_discover_signing_manifest_rejects_unreadable_remote_object(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """A fetched cache entry must be a readable UTF-8 file."""
    package_root = tmp_path / 'package'
    remote_uri = 'https://example.com/catalog.json'
    cached_directory = tmp_path / 'cached-directory'
    cached_directory.mkdir()
    profile = _write_profile(package_root / 'profile.json', [remote_uri])

    class _DirectoryFetcher:
        def get_cached_path(self, force_update: bool = False) -> pathlib.Path:
            return cached_directory

    monkeypatch.setattr(
        FetcherFactory,
        'get_fetcher',
        staticmethod(lambda trestle_root, uri, max_size_bytes=None, block_private_ips=None: _DirectoryFetcher()),
    )

    with pytest.raises(TrestleError, match='Unable to read fetched OSCAL dependency'):
        discover_signing_manifest(profile, package_root / 'package.json', [])


@pytest.mark.parametrize('remote_kind', ['file', 'symlink'])
def test_discover_signing_manifest_rejects_unsafe_remote_directory(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch, remote_kind: str
) -> None:
    """Downloaded artifacts must use a real package-local directory."""
    if remote_kind == 'symlink' and file_utils.is_windows():
        pytest.skip('Creating symlinks requires additional privileges on Windows.')
    package_root = tmp_path / 'package'
    remote_uri = 'https://example.com/catalog.json'
    catalog = (test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json').read_text(encoding=const.FILE_ENCODING)
    _mock_remote_documents(monkeypatch, tmp_path, {remote_uri: catalog})
    profile = _write_profile(package_root / 'profile.json', [remote_uri])
    remote_root = package_root / 'remote'
    if remote_kind == 'file':
        remote_root.write_text('not a directory', encoding=const.FILE_ENCODING)
        expected_error = 'is not a directory'
    else:
        remote_root.symlink_to(tmp_path / 'outside', target_is_directory=True)
        expected_error = 'must not be a symlink'

    with pytest.raises(TrestleError, match=expected_error):
        discover_signing_manifest(profile, package_root / 'package.json', [])


def test_remote_artifact_directory_stays_inside_package(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """A directory changed during validation must not redirect downloads outside the package."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalog.json')
    discovery = SigningManifestDiscovery(package_root / 'package.json')
    remote_root = package_root / 'remote'
    outside = tmp_path / 'outside'
    original_resolve = pathlib.Path.resolve

    def _redirect_remote_root(path: pathlib.Path, *args: Any, **kwargs: Any) -> pathlib.Path:
        if path == remote_root:
            return outside
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, 'resolve', _redirect_remote_root)

    with pytest.raises(TrestleError, match='must stay within the package directory'):
        discovery._remote_artifact_path('https://example.com/catalog.json')


@pytest.mark.skipif(file_utils.is_windows(), reason='Creating symlinks requires additional privileges on Windows.')
def test_write_remote_artifact_rejects_symlink(tmp_path: pathlib.Path) -> None:
    """A downloaded artifact must not replace a final symlink."""
    destination = tmp_path / 'artifact.json'
    destination.symlink_to(tmp_path / 'target.json')

    with pytest.raises(TrestleError, match='must not be a symlink'):
        SigningManifestDiscovery._write_remote_artifact(destination, b'{}', 'https://example.com/artifact.json')


@pytest.mark.parametrize('race_kind', ['same', 'different', 'symlink', 'oserror'])
def test_write_remote_artifact_handles_creation_races(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch, race_kind: str
) -> None:
    """Exclusive creation should not overwrite a path created concurrently."""
    if race_kind == 'symlink' and file_utils.is_windows():
        pytest.skip('Creating symlinks requires additional privileges on Windows.')
    destination = tmp_path / 'artifact.json'
    original_open = pathlib.Path.open

    def _race_open(path: pathlib.Path, *args: Any, **kwargs: Any) -> Any:
        if path != destination or not args or args[0] != 'xb':
            return original_open(path, *args, **kwargs)
        if race_kind == 'oserror':
            raise PermissionError
        if race_kind == 'symlink':
            destination.symlink_to(tmp_path / 'target.json')
        else:
            content = b'{}' if race_kind == 'same' else b'{"changed":true}'
            with original_open(destination, 'wb') as write_file:
                write_file.write(content)
        raise FileExistsError

    monkeypatch.setattr(pathlib.Path, 'open', _race_open)
    if race_kind == 'same':
        SigningManifestDiscovery._write_remote_artifact(destination, b'{}', 'https://example.com/artifact.json')
    else:
        expected_error = {
            'different': 'already exists with different content',
            'symlink': 'must not be a symlink',
            'oserror': 'Unable to write fetched OSCAL dependency',
        }[race_kind]
        with pytest.raises(TrestleError, match=expected_error):
            SigningManifestDiscovery._write_remote_artifact(destination, b'{}', 'https://example.com/artifact.json')


@pytest.mark.parametrize(
    'href, expected_error',
    [
        ('http://example.com/catalog.json', 'Remote or absolute'),
        ('file:///tmp/catalog.json', 'Remote or absolute'),
        ('/tmp/catalog.json', 'Remote or absolute'),
        ('catalog.json?version=1', 'query parameters or fragments'),
        ('catalog.json#fragment', 'query parameters or fragments'),
        ('https://example.com/catalog.json?version=1', 'query parameters or fragments'),
        ('https://example.com/catalog.yaml', 'must be JSON files'),
        ('missing.json', 'does not exist or is not a file'),
        ('catalog.yaml', 'must be JSON files'),
        ('../../outside.json', 'must stay within the package directory'),
    ],
)
def test_discover_signing_manifest_rejects_unsupported_dependency_references(
    tmp_path: pathlib.Path, href: str, expected_error: str
) -> None:
    """Only local JSON dependencies inside the package boundary should be followed."""
    package_root = tmp_path / 'package'
    _write_profile(package_root / 'profiles/profile.json', [href])
    ssp = _write_ssp(package_root / 'ssp.json', 'profiles/profile.json')

    with pytest.raises(TrestleError, match=expected_error):
        discover_signing_manifest(ssp, package_root / 'package.json', [])


@pytest.mark.parametrize(
    'content, expected_error',
    [('{', 'Input is not valid JSON'), ('{"catalog":{"uuid":"first","uuid":"second"}}', 'Duplicate JSON object key')],
)
def test_discover_signing_manifest_rejects_invalid_remote_json(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch, content: str, expected_error: str
) -> None:
    """Fetched dependencies must pass the same strict JSON checks as local files."""
    package_root = tmp_path / 'package'
    remote_uri = 'https://example.com/catalog.json'
    _mock_remote_documents(monkeypatch, tmp_path, {remote_uri: content})
    profile = _write_profile(package_root / 'profile.json', [remote_uri])

    with pytest.raises(TrestleError, match=expected_error):
        discover_signing_manifest(profile, package_root / 'package.json', [])

    assert not (package_root / 'remote').exists()


def test_discover_signing_manifest_does_not_replace_remote_artifact(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """A changed remote resource should not replace package content from an earlier run."""
    package_root = tmp_path / 'package'
    remote_uri = 'https://example.com/catalog.json'
    catalog_data = _read_json(test_utils.JSON_TEST_DATA_PATH / 'minimal_catalog.json')
    requested_uris = _mock_remote_documents(monkeypatch, tmp_path, {remote_uri: json.dumps(catalog_data)})
    profile = _write_profile(package_root / 'profile.json', [remote_uri])
    first_manifest = discover_signing_manifest(profile, package_root / 'first-package.json', [])
    remote_path = first_manifest.artifacts[1].path

    catalog_data['catalog']['metadata']['title'] = 'Changed catalog'
    remote_source = tmp_path / 'remote-source/0.json'
    remote_source.write_text(json.dumps(catalog_data), encoding=const.FILE_ENCODING)

    with pytest.raises(TrestleError, match='already exists with different content'):
        discover_signing_manifest(profile, package_root / 'second-package.json', [])

    assert len(requested_uris) == 2
    assert _read_json(remote_path)['catalog']['metadata']['title'] != 'Changed catalog'


def test_discover_signing_manifest_rejects_empty_dependency_href(tmp_path: pathlib.Path) -> None:
    """An OSCAL dependency href should be a non-empty string."""
    package_root = tmp_path / 'package'
    _write_profile(package_root / 'profile.json', [''])
    ssp = _write_ssp(package_root / 'ssp.json', 'profile.json')

    with pytest.raises(TrestleError, match='has an empty href'):
        discover_signing_manifest(ssp, package_root / 'package.json', [])


def test_discover_signing_manifest_rejects_trestle_uri_outside_workspace(tmp_path: pathlib.Path) -> None:
    """Trestle URIs require a discoverable Trestle workspace root."""
    package_root = tmp_path / 'package'
    ssp = _write_ssp(package_root / 'ssp.json', 'trestle://profiles/profile.json')

    with pytest.raises(TrestleError, match='outside a trestle workspace'):
        discover_signing_manifest(ssp, package_root / 'package.json', [])


@pytest.mark.parametrize(
    'href, expected_error',
    [
        ('trestle://profiles/profile.json?version=1', 'query parameters or fragments'),
        ('trestle://', 'empty trestle URI'),
    ],
)
def test_discover_signing_manifest_rejects_unsupported_trestle_uris(
    tmp_path: pathlib.Path, href: str, expected_error: str
) -> None:
    """Trestle dependency URIs should contain one unqualified local path."""
    package_root = tmp_path / 'workspace'
    (package_root / const.TRESTLE_CONFIG_DIR).mkdir(parents=True)
    ssp = _write_ssp(package_root / 'ssp.json', href)

    with pytest.raises(TrestleError, match=expected_error):
        discover_signing_manifest(ssp, package_root / 'package.json', [])


@pytest.mark.parametrize(
    'content, suffix, expected_error',
    [
        ('{', '.json', 'Input is not valid JSON'),
        ('{"system-security-plan":{"uuid":"a","uuid":"b"}}', '.json', 'Duplicate JSON object key'),
        ('[]', '.json', 'not a top-level OSCAL JSON object'),
        ('{"unknown":{}}', '.json', 'Unsupported OSCAL model type'),
        ('{"system-security-plan":{}}', '.json', 'Unable to load OSCAL model'),
        ('{}', '.yaml', 'must be JSON files'),
    ],
)
def test_discover_signing_manifest_rejects_invalid_primary_files(
    tmp_path: pathlib.Path, content: str, suffix: str, expected_error: str
) -> None:
    """Discovery should strictly load a valid local OSCAL JSON primary artifact."""
    package_root = tmp_path / 'package'
    primary = package_root / f'ssp{suffix}'
    primary.parent.mkdir(parents=True)
    primary.write_text(content, encoding=const.FILE_ENCODING)

    with pytest.raises(TrestleError, match=expected_error):
        discover_signing_manifest(primary, package_root / 'package.json', [])


def test_discover_signing_manifest_supports_all_primary_model_types(tmp_path: pathlib.Path) -> None:
    """Every top-level OSCAL model should work as a primary artifact."""
    package_root = tmp_path / 'package'
    catalog = _write_catalog(package_root / 'catalog.json')
    profile = _write_profile(package_root / 'profile.json', ['catalog.json'])
    ssp = _write_ssp(package_root / 'ssp.json', 'profile.json')
    assessment_plan_path = _write_assessment_plan(package_root / 'assessment-plan.json', 'ssp.json')
    assessment_results_path = _write_assessment_results(
        package_root / 'assessment-results.json', 'assessment-plan.json'
    )
    poam_path = _write_poam(package_root / 'poam.json', 'ssp.json')
    _write_component_definition(package_root / 'component-definitions/nested.json')
    component = _write_component_definition(package_root / 'component-definitions/root.json', ['nested.json'])
    mapping = _write_mapping_collection(package_root / 'mapping.json', 'catalog.json', 'profile.json')

    expected_artifacts = {
        catalog: ['catalog.json'],
        profile: ['profile.json', 'catalog.json'],
        ssp: ['ssp.json', 'profile.json', 'catalog.json'],
        assessment_plan_path: ['assessment-plan.json', 'ssp.json', 'profile.json', 'catalog.json'],
        assessment_results_path: [
            'assessment-results.json',
            'assessment-plan.json',
            'ssp.json',
            'profile.json',
            'catalog.json',
        ],
        poam_path: ['poam.json', 'ssp.json', 'profile.json', 'catalog.json'],
        component: ['component-definitions/root.json', 'component-definitions/nested.json'],
        mapping: ['mapping.json', 'catalog.json', 'profile.json'],
    }
    for primary, artifact_names in expected_artifacts.items():
        manifest = discover_signing_manifest(primary, package_root / f'{primary.stem}-package.json', [])
        assert manifest.primary_artifact == primary.relative_to(package_root).as_posix()
        assert [artifact.name for artifact in manifest.artifacts] == artifact_names


def test_discover_signing_manifest_supports_poam_without_ssp(tmp_path: pathlib.Path) -> None:
    """A POA&M without the optional SSP import should be a terminal package artifact."""
    package_root = tmp_path / 'package'
    poam_path = _write_poam(package_root / 'poam.json')

    manifest = discover_signing_manifest(poam_path, package_root / 'package.json', [])

    assert [artifact.name for artifact in manifest.artifacts] == ['poam.json']


def test_discover_signing_manifest_supports_single_mapping_object(tmp_path: pathlib.Path) -> None:
    """A mapping collection may contain one mapping object instead of a list."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalog.json')
    data = _read_json(test_utils.JSON_TEST_DATA_PATH / 'simple_mapping.json')
    mapping = data['mapping-collection']['mappings'][0]
    mapping['source-resource'] = {'type': 'catalog', 'href': 'catalog.json'}
    mapping['target-resource'] = {'type': 'catalog', 'href': 'catalog.json'}
    data['mapping-collection']['mappings'] = mapping
    mapping_path = _write_json(package_root / 'mapping.json', data)

    manifest = discover_signing_manifest(mapping_path, package_root / 'package.json', [])

    assert [artifact.name for artifact in manifest.artifacts] == ['mapping.json', 'catalog.json']


def test_discover_signing_manifest_rejects_unsupported_mapping_resource_type(tmp_path: pathlib.Path) -> None:
    """Mapping resources should declare catalog or profile dependencies."""
    package_root = tmp_path / 'package'
    _write_ssp(package_root / 'ssp.json', 'profile.json')
    mapping = _write_mapping_collection(
        package_root / 'mapping.json', 'ssp.json', 'profile.json', source_type=const.MODEL_TYPE_SSP
    )

    with pytest.raises(TrestleError, match='Unsupported mapping source resource type'):
        discover_signing_manifest(mapping, package_root / 'package.json', [])


def test_discover_signing_manifest_requires_supported_include(tmp_path: pathlib.Path) -> None:
    """Every explicit include must be a supported OSCAL model."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalog.json')
    _write_profile(package_root / 'profile.json', ['catalog.json'])
    ssp = _write_ssp(package_root / 'ssp.json', 'profile.json')
    unsupported = _write_json(package_root / 'unknown.json', {'unknown': {}})
    with pytest.raises(TrestleError, match='Unsupported OSCAL model type'):
        discover_signing_manifest(ssp, package_root / 'package.json', [unsupported])


def test_discover_signing_manifest_rejects_invalid_dependency_model_type(tmp_path: pathlib.Path) -> None:
    """A supported model must still be valid for its dependency relationship."""
    package_root = tmp_path / 'package'
    _write_component_definition(package_root / 'component-definition.json')
    profile = _write_profile(package_root / 'profile.json', ['component-definition.json'])

    with pytest.raises(TrestleError, match='Profile import has OSCAL model type component-definition'):
        discover_signing_manifest(profile, package_root / 'package.json', [])


@pytest.mark.parametrize('output_kind', ['file', 'directory'])
def test_write_signing_manifest_rejects_existing_output(tmp_path: pathlib.Path, output_kind: str) -> None:
    """Generated manifests should never overwrite an existing file or directory."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalog.json')
    _write_profile(package_root / 'profile.json', ['catalog.json'])
    ssp = _write_ssp(package_root / 'ssp.json', 'profile.json')
    output = package_root / 'package.json'
    manifest = discover_signing_manifest(ssp, output, [])
    if output_kind == 'file':
        output.write_text('existing', encoding=const.FILE_ENCODING)
    else:
        output.mkdir()

    with pytest.raises(TrestleError, match='already exists|is a directory'):
        write_signing_manifest(manifest)


@pytest.mark.parametrize('overwrite', [False, True])
@pytest.mark.skipif(file_utils.is_windows(), reason='Creating symlinks requires additional privileges on Windows.')
def test_write_signing_manifest_rejects_final_symlink(tmp_path: pathlib.Path, overwrite: bool) -> None:
    """The manifest writer should reject an existing final symlink without following it."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalog.json')
    _write_profile(package_root / 'profile.json', ['catalog.json'])
    ssp = _write_ssp(package_root / 'ssp.json', 'profile.json')
    target = package_root / 'target.json'
    output = package_root / 'package.json'
    output.symlink_to(target)
    manifest = discover_signing_manifest(ssp, output, [])

    with pytest.raises(TrestleError, match='must not be a symlink'):
        write_signing_manifest(manifest, overwrite)


def test_write_signing_manifest_rejects_non_json_output(tmp_path: pathlib.Path) -> None:
    """Generated package manifests should use the JSON manifest format."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalog.json')
    _write_profile(package_root / 'profile.json', ['catalog.json'])
    ssp = _write_ssp(package_root / 'ssp.json', 'profile.json')
    manifest = discover_signing_manifest(ssp, package_root / 'package.yml', [])

    with pytest.raises(TrestleError, match='output must be a JSON file'):
        write_signing_manifest(manifest)


def test_write_signing_manifest_handles_exclusive_creation_race(
    tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
) -> None:
    """A file created after validation should still prevent manifest overwrite."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalog.json')
    _write_profile(package_root / 'profile.json', ['catalog.json'])
    ssp = _write_ssp(package_root / 'ssp.json', 'profile.json')
    output = package_root / 'package.json'
    manifest = discover_signing_manifest(ssp, output, [])
    original_open = pathlib.Path.open

    def _race_open(path: pathlib.Path, *args: Any, **kwargs: Any) -> Any:
        if path == output and args and args[0] == 'x':
            raise FileExistsError
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, 'open', _race_open)
    with pytest.raises(TrestleError, match='output path already exists'):
        write_signing_manifest(manifest)


def test_write_signing_manifest_cleans_up_failed_overwrite(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> None:
    """An atomic overwrite failure should not leave its temporary file behind."""
    package_root = tmp_path / 'package'
    _write_catalog(package_root / 'catalog.json')
    output = package_root / 'package.json'
    manifest = discover_signing_manifest(package_root / 'catalog.json', output, [])
    output.write_text('existing', encoding=const.FILE_ENCODING)
    existing_paths = set(package_root.iterdir())

    def _fail_replace(path: pathlib.Path, target: pathlib.Path) -> pathlib.Path:
        raise OSError('replace failed')

    monkeypatch.setattr(pathlib.Path, 'replace', _fail_replace)
    with pytest.raises(OSError, match='replace failed'):
        write_signing_manifest(manifest, overwrite=True)

    assert set(package_root.iterdir()) == existing_paths
