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
"""Discover OSCAL dependencies and write package signing manifests."""

from __future__ import annotations

import hashlib
import json
import pathlib
import tempfile
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import unquote, urljoin, urlparse

from trestle.common import const, file_utils
from trestle.common.err import TrestleError
from trestle.core import parser
from trestle.core.canonicalization import canonicalize_json_text, load_canonical_json_file
from trestle.core.remote.cache import FetcherFactory
from trestle.core.signing_manifest import ManifestArtifact, SigningManifest, load_signing_manifest

OSCAL_JSON_MEDIA_TYPE = 'application/oscal+json'
SUPPORTED_DISCOVERY_TYPES = set(const.MODEL_TYPE_LIST)
MAX_DISCOVERED_ARTIFACTS = 1000
MAX_DISCOVERY_DEPTH = 64
MAX_REMOTE_ARTIFACT_SIZE_BYTES = 50 * 1024 * 1024
MAX_TOTAL_REMOTE_SIZE_BYTES = 500 * 1024 * 1024


class SigningManifestDiscovery:
    """Discover an OSCAL dependency graph for a package manifest."""

    def __init__(self, output_path: pathlib.Path, allow_private_uris: bool = False) -> None:
        """Initialize discovery using the output directory as the package boundary."""
        self.output_path = output_path.absolute()
        self.package_root = self.output_path.parent.resolve()
        self.trestle_root = file_utils.extract_trestle_project_root(self.package_root)
        self._artifacts: List[ManifestArtifact] = []
        self._models: Dict[pathlib.Path, Tuple[str, Any]] = {}
        self._visited: Set[pathlib.Path] = set()
        self._visiting: List[pathlib.Path] = []
        self._source_uris: Dict[pathlib.Path, str] = {}
        self._remote_artifacts: Dict[str, pathlib.Path] = {}
        self._remote_size_bytes = 0
        self._block_private_ips = not allow_private_uris

    def discover(self, primary_path: pathlib.Path, include_paths: Iterable[pathlib.Path]) -> SigningManifest:
        """Discover primary model dependencies and additional explicitly included models."""
        primary_path = self._validated_artifact_path(primary_path)
        self._visit(primary_path, SUPPORTED_DISCOVERY_TYPES, 'Primary artifact')

        for include_path in include_paths:
            self._visit(self._validated_artifact_path(include_path), SUPPORTED_DISCOVERY_TYPES, 'Included artifact')

        primary_name = self._artifact_name(primary_path)
        return SigningManifest(self.output_path, primary_name, self._artifacts)

    def _visit(self, path: pathlib.Path, expected_types: Set[str], reference_context: str) -> Tuple[str, Any]:
        """Visit one OSCAL model, recursively following supported dependency references."""
        path = self._validated_artifact_path(path)
        if path in self._visiting:
            cycle_start = self._visiting.index(path)
            cycle = self._visiting[cycle_start:] + [path]
            cycle_text = ' -> '.join(self._artifact_name(item) for item in cycle)
            raise TrestleError(f'Circular OSCAL dependency detected: {cycle_text}')
        if path in self._visited:
            model_type, model = self._models[path]
            self._validate_expected_type(model_type, expected_types, reference_context, path)
            return model_type, model
        if len(self._visiting) >= MAX_DISCOVERY_DEPTH:
            raise TrestleError(f'OSCAL dependency graph exceeds maximum depth of {MAX_DISCOVERY_DEPTH}.')
        if len(self._artifacts) >= MAX_DISCOVERED_ARTIFACTS:
            raise TrestleError(f'OSCAL dependency graph exceeds maximum of {MAX_DISCOVERED_ARTIFACTS} artifacts.')

        model_type, model = self._load_oscal_model(path)
        self._models[path] = (model_type, model)
        self._validate_expected_type(model_type, expected_types, reference_context, path)
        self._artifacts.append(self._manifest_artifact(path))
        self._visiting.append(path)
        try:
            for href, dependency_types, dependency_context in self._dependency_references(model_type, model):
                dependency_path = self._resolve_reference(path, model, href)
                self._visit(dependency_path, dependency_types, dependency_context)
        finally:
            self._visiting.pop()
        self._visited.add(path)
        return model_type, model

    def _resolve_reference(self, source_path: pathlib.Path, source_model: Any, href: Optional[str]) -> pathlib.Path:
        """Resolve an OSCAL dependency href relative to its source document."""
        if not isinstance(href, str) or not href.strip():
            raise TrestleError(f'OSCAL dependency in {self._artifact_name(source_path)} has an empty href.')
        href = href.strip()
        if href.startswith('#'):
            href = self._resolve_back_matter_reference(source_path, source_model, href[1:])

        parsed_href = urlparse(href)
        if parsed_href.query or parsed_href.fragment:
            raise TrestleError(
                f'OSCAL dependency references with query parameters or fragments are unsupported: {href}'
            )

        if href.startswith(const.TRESTLE_HREF_HEADING):
            if self.trestle_root is None:
                raise TrestleError(f'Unable to resolve trestle URI outside a trestle workspace: {href}')
            relative_path = unquote(href[len(const.TRESTLE_HREF_HEADING) :])
            if not relative_path:
                raise TrestleError(f'OSCAL dependency contains an empty trestle URI: {href}')
            dependency_path = self.trestle_root / relative_path
        else:
            if parsed_href.scheme in ('https', 'sftp'):
                return self._fetch_remote_artifact(href)
            if parsed_href.scheme or parsed_href.netloc:
                raise TrestleError(f'Remote or absolute OSCAL dependencies are not supported: {href}')
            source_uri = self._source_uris.get(source_path)
            if source_uri:
                return self._fetch_remote_artifact(urljoin(source_uri, href))
            relative_path_text = unquote(parsed_href.path)
            relative_path = pathlib.Path(relative_path_text)
            if (
                not relative_path_text
                or pathlib.PurePosixPath(relative_path_text).is_absolute()
                or relative_path.is_absolute()
            ):
                raise TrestleError(f'Remote or absolute OSCAL dependencies are not supported: {href}')
            dependency_path = source_path.parent / relative_path

        return self._validated_artifact_path(dependency_path)

    def _fetch_remote_artifact(self, uri: str) -> pathlib.Path:
        """Fetch, validate, and vendor one remote OSCAL JSON dependency."""
        existing_path = self._remote_artifacts.get(uri)
        if existing_path is not None:
            return existing_path
        if len(self._artifacts) >= MAX_DISCOVERED_ARTIFACTS:
            raise TrestleError(f'OSCAL dependency graph exceeds maximum of {MAX_DISCOVERED_ARTIFACTS} artifacts.')
        remaining_remote_bytes = MAX_TOTAL_REMOTE_SIZE_BYTES - self._remote_size_bytes
        if remaining_remote_bytes <= 0:
            raise TrestleError(
                f'Remote OSCAL dependencies exceed maximum total size of {MAX_TOTAL_REMOTE_SIZE_BYTES} bytes.'
            )

        parsed_uri = urlparse(uri)
        if pathlib.PurePosixPath(parsed_uri.path).suffix.lower() != '.json':
            raise TrestleError(f'Remote OSCAL dependencies must be JSON files: {uri}')

        if self.trestle_root:
            canonical_bytes, fetched_size = self._fetch_remote_json(
                self.trestle_root, uri, remaining_remote_bytes, self._block_private_ips
            )
        else:
            with tempfile.TemporaryDirectory(prefix='trestle-manifest-') as temporary_directory:
                temporary_root = pathlib.Path(temporary_directory)
                (temporary_root / const.TRESTLE_CONFIG_DIR).mkdir()
                canonical_bytes, fetched_size = self._fetch_remote_json(
                    temporary_root, uri, remaining_remote_bytes, self._block_private_ips
                )

        destination = self._remote_artifact_path(uri)
        self._write_remote_artifact(destination, canonical_bytes, uri)
        destination = self._validated_artifact_path(destination)
        self._source_uris[destination] = uri
        self._remote_artifacts[uri] = destination
        self._remote_size_bytes += fetched_size
        return destination

    @staticmethod
    def _fetch_remote_json(
        trestle_root: pathlib.Path, uri: str, remaining_remote_bytes: int, block_private_ips: bool
    ) -> Tuple[bytes, int]:
        """Fetch a remote object through Trestle and return strict canonical JSON."""
        maximum_size = min(MAX_REMOTE_ARTIFACT_SIZE_BYTES, remaining_remote_bytes)
        fetcher = FetcherFactory.get_fetcher(trestle_root, uri, maximum_size, block_private_ips)
        cached_path = fetcher.get_cached_path()
        try:
            json_text = cached_path.read_text(encoding=const.FILE_ENCODING)
        except (OSError, UnicodeError) as error:
            raise TrestleError(f'Unable to read fetched OSCAL dependency: {uri}') from error
        fetched_size = cached_path.stat().st_size
        if fetched_size > maximum_size:
            raise TrestleError(f'Remote object exceeds maximum size of {maximum_size} bytes: {uri}')
        _, canonical_bytes = canonicalize_json_text(json_text)
        return canonical_bytes, fetched_size

    def _remote_artifact_path(self, uri: str) -> pathlib.Path:
        """Return a deterministic package-local path for a remote URI."""
        remote_root = self.package_root / 'remote'
        if remote_root.is_symlink():
            raise TrestleError(f'Remote artifact directory must not be a symlink: {remote_root}')
        if remote_root.exists() and not remote_root.is_dir():
            raise TrestleError(f'Remote artifact path is not a directory: {remote_root}')
        remote_root.mkdir(exist_ok=True)
        remote_root = remote_root.resolve()
        try:
            remote_root.relative_to(self.package_root)
        except ValueError:
            raise TrestleError(f'Remote artifact directory must stay within the package directory: {remote_root}')
        uri_digest = hashlib.sha256(uri.encode(const.FILE_ENCODING)).hexdigest()
        return remote_root / f'{uri_digest}.json'

    @staticmethod
    def _write_remote_artifact(destination: pathlib.Path, canonical_bytes: bytes, uri: str) -> None:
        """Write fetched canonical JSON without replacing package content."""
        if destination.is_symlink():
            raise TrestleError(f'Remote artifact output must not be a symlink: {destination}')
        if destination.exists():
            _, existing_bytes = load_canonical_json_file(destination)
            if existing_bytes != canonical_bytes:
                raise TrestleError(f'Remote artifact output already exists with different content: {destination}')
            return
        try:
            with destination.open('xb') as write_file:
                write_file.write(canonical_bytes)
        except FileExistsError:
            if destination.is_symlink():
                raise TrestleError(f'Remote artifact output must not be a symlink: {destination}')
            _, existing_bytes = load_canonical_json_file(destination)
            if existing_bytes != canonical_bytes:
                raise TrestleError(f'Remote artifact output already exists with different content: {destination}')
        except OSError as error:
            raise TrestleError(f'Unable to write fetched OSCAL dependency {uri}: {destination}') from error

    def _resolve_back_matter_reference(self, source_path: pathlib.Path, source_model: Any, uuid: str) -> str:
        """Resolve a dependency reference through a back-matter resource UUID."""
        back_matter = getattr(source_model, 'back_matter', None)
        resources = back_matter.resources if back_matter and back_matter.resources else []
        matching_resources = [resource for resource in resources if resource.uuid == uuid]
        if len(matching_resources) != 1:
            raise TrestleError(
                f'OSCAL dependency #{uuid} in {self._artifact_name(source_path)} does not identify one back-matter resource.'
            )

        resource = matching_resources[0]
        json_links = [
            rlink.href
            for rlink in resource.rlinks or []
            if pathlib.PurePosixPath(urlparse(rlink.href).path).suffix.lower() == '.json'
        ]
        if len(json_links) != 1:
            raise TrestleError(
                f'OSCAL dependency #{uuid} in {self._artifact_name(source_path)} must provide one JSON rlink.'
            )
        return json_links[0]

    def _validated_artifact_path(self, path: pathlib.Path) -> pathlib.Path:
        """Validate a package artifact path and return its canonical local path."""
        path = path.resolve()
        try:
            path.relative_to(self.package_root)
        except ValueError:
            raise TrestleError(f'Discovered OSCAL artifact must stay within the package directory: {path}')
        if path.suffix.lower() != '.json':
            raise TrestleError(f'Discovered OSCAL artifacts must be JSON files: {path}')
        if not path.exists() or not path.is_file():
            raise TrestleError(f'Discovered OSCAL artifact does not exist or is not a file: {path}')
        return path

    def _load_oscal_model(self, path: pathlib.Path) -> Tuple[str, Any]:
        """Strictly load a supported top-level OSCAL JSON model."""
        model_data, _ = load_canonical_json_file(path)
        if not isinstance(model_data, dict):
            raise TrestleError(f'Discovered artifact is not a top-level OSCAL JSON object: {path}')
        model_type = parser.root_key(model_data)
        if model_type not in SUPPORTED_DISCOVERY_TYPES:
            raise TrestleError(f'Unsupported OSCAL model type for package discovery: {model_type}')
        model_name = parser.to_full_model_name(model_type)
        try:
            model = parser.parse_dict(model_data[model_type], model_name)
        except Exception as error:
            raise TrestleError(f'Unable to load OSCAL model for package discovery: {path}') from error
        return model_type, model

    def _manifest_artifact(self, path: pathlib.Path) -> ManifestArtifact:
        name = self._artifact_name(path)
        return ManifestArtifact(name, name, OSCAL_JSON_MEDIA_TYPE, path)

    def _artifact_name(self, path: pathlib.Path) -> str:
        return path.relative_to(self.package_root).as_posix()

    @staticmethod
    def _validate_expected_type(
        model_type: str, expected_types: Set[str], reference_context: str, path: pathlib.Path
    ) -> None:
        if model_type not in expected_types:
            expected = ', '.join(sorted(expected_types))
            raise TrestleError(
                f'{reference_context} has OSCAL model type {model_type}, expected one of {expected}: {path}'
            )

    @staticmethod
    def _dependency_references(model_type: str, model: Any) -> List[Tuple[Optional[str], Set[str], str]]:
        """Return semantic dependency hrefs for a supported OSCAL model."""
        if model_type == const.MODEL_TYPE_A_PLAN:
            return [(model.import_ssp.href, {const.MODEL_TYPE_SSP}, 'Assessment-plan import-ssp')]
        if model_type == const.MODEL_TYPE_A_RESULT:
            return [(model.import_ap.href, {const.MODEL_TYPE_A_PLAN}, 'Assessment-results import-ap')]
        if model_type == const.MODEL_TYPE_SSP:
            return [
                (model.import_profile.href, {const.MODEL_TYPE_CATALOG, const.MODEL_TYPE_PROFILE}, 'SSP import-profile')
            ]
        if model_type == const.MODEL_TYPE_PROFILE:
            return [
                (import_.href, {const.MODEL_TYPE_CATALOG, const.MODEL_TYPE_PROFILE}, 'Profile import')
                for import_ in model.imports
            ]
        if model_type == const.MODEL_TYPE_COMPDEF:
            references = [
                (import_.href, {const.MODEL_TYPE_COMPDEF}, 'Component-definition import')
                for import_ in model.import_component_definitions or []
            ]
            for container in (model.components or []) + (model.capabilities or []):
                references.extend(
                    (
                        implementation.source,
                        {const.MODEL_TYPE_CATALOG, const.MODEL_TYPE_PROFILE},
                        'Component-definition control-implementation source',
                    )
                    for implementation in container.control_implementations or []
                )
            return references
        if model_type == const.MODEL_TYPE_MAPPING:
            references = []
            mappings = model.mappings if isinstance(model.mappings, list) else [model.mappings]
            for mapping in mappings:
                for resource_name, resource in (
                    ('source', mapping.source_resource),
                    ('target', mapping.target_resource),
                ):
                    resource_type_value = getattr(resource.type, 'root', resource.type)
                    resource_type = str(getattr(resource_type_value, 'value', resource_type_value))
                    if resource_type not in {const.MODEL_TYPE_CATALOG, const.MODEL_TYPE_PROFILE}:
                        raise TrestleError(f'Unsupported mapping {resource_name} resource type: {resource_type}')
                    references.append((resource.href, {resource_type}, f'Mapping {resource_name} resource'))
            return references
        if model_type == const.MODEL_TYPE_POAM and model.import_ssp:
            return [(model.import_ssp.href, {const.MODEL_TYPE_SSP}, 'POA&M import-ssp')]
        return []


def discover_signing_manifest(
    primary_path: pathlib.Path,
    output_path: pathlib.Path,
    include_paths: Iterable[pathlib.Path],
    allow_private_uris: bool = False,
) -> SigningManifest:
    """Discover a signing manifest from a supported primary OSCAL model and explicit includes."""
    return SigningManifestDiscovery(output_path, allow_private_uris).discover(primary_path, include_paths)


def write_signing_manifest(manifest: SigningManifest, overwrite: bool = False) -> SigningManifest:
    """Write a generated signing manifest, optionally replacing an existing file."""
    output_path = manifest.path
    if output_path.suffix.lower() != '.json':
        raise TrestleError(f'Signing manifest output must be a JSON file: {output_path}')
    if output_path.is_symlink():
        raise TrestleError(f'Signing manifest output path must not be a symlink: {output_path}')
    if output_path.exists():
        if output_path.is_dir():
            raise TrestleError(f'Signing manifest output path is a directory: {output_path}')
        if not overwrite:
            raise TrestleError(f'Signing manifest output path already exists: {output_path}')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_data: Dict[str, Any] = {
        'primaryArtifact': manifest.primary_artifact,
        'artifacts': [artifact.to_predicate() for artifact in manifest.artifacts],
    }
    serialized_manifest = json.dumps(manifest_data, indent=2) + '\n'
    if overwrite:
        temporary_path: Optional[pathlib.Path] = None
        try:
            with tempfile.NamedTemporaryFile(
                'w', dir=output_path.parent, delete=False, encoding=const.FILE_ENCODING
            ) as temporary_file:
                temporary_path = pathlib.Path(temporary_file.name)
                temporary_file.write(serialized_manifest)
            temporary_path.replace(output_path)
        finally:
            if temporary_path and temporary_path.exists():
                temporary_path.unlink()
    else:
        try:
            with output_path.open('x', encoding=const.FILE_ENCODING) as write_file:
                write_file.write(serialized_manifest)
        except FileExistsError as error:
            raise TrestleError(f'Signing manifest output path already exists: {output_path}') from error

    return load_signing_manifest(output_path)
