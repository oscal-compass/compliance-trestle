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
"""Create ssp from catalog and profile."""

import logging
import pathlib
from typing import Any, Iterable, List, Union

import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.core.err import TrestleError
from trestle.core.pipeline import Pipeline
from trestle.core.remote import cache

logger = logging.getLogger(__name__)


class CatalogResolver():
    """Class to resolve a catalog given a profile."""

    class Merge(Pipeline.Filter):
        """Merge the catalogs according to rules in the profile."""

        # this pulls from import and iterates
        def __init__(self, profile):
            """Initialize the class with the profile."""
            self._profile = profile

        def _merge_controls(self, merged: Union[None, cat.Catalog], catalog: cat.Catalog) -> cat.Catalog:
            """Merge the controls with the current catalog based on the profile."""
            if merged is None:
                return catalog
            if catalog.controls is not None:
                for control in catalog.controls:
                    merged.controls.append(control)
            return catalog

        def process(self, catalogs: Iterable[List[cat.Control]]) -> cat.Catalog:
            """Merge the existing controls with the new ones based on the profile."""
            merged: cat.Catalog
            merged = None
            for catalog in catalogs:
                merged = self._merge_controls(merged, catalog)
            return merged

    class Modify(Pipeline.Filter):
        """Modify the controls based on the profile."""

        def __init__(self, profile: prof.Profile) -> None:
            """Initialize the filter."""
            self._profile = profile

        def _modify_controls(self, catalog: cat.Catalog) -> cat.Catalog:
            """Modify the controls based on the profile."""
            return catalog

        def process(self, catalog: cat.Catalog) -> cat.Catalog:
            """Make the modifications to the controls based on the profile."""
            return self._modify_controls(catalog)

    class Import(Pipeline.Filter):
        """Profile filter class."""

        def __init__(self, trestle_root: pathlib.Path) -> None:
            """Initialie and store trestle root for cache access."""
            self._trestle_root = trestle_root

        def process(self, uri: str, initializing=False) -> Any:
            """Load uri catalog or profile and yield a sequence of catalogs imported through separate pipelines."""
            fetcher = cache.FetcherFactory.get_fetcher(self._trestle_root, uri)

            model, model_type = fetcher.get_oscal()

            if model_type == 'catalog':
                # it's a catalog so just yield it
                yield model
            else:
                if model_type != 'profile':
                    raise TrestleError(f'Improper model type {model_type} as profile import.')
                profile: prof.Profile
                profile = model

                # it is a profile, so yield each import into the pipeline
                merge_filter = CatalogResolver.Merge(profile)
                modify_filter = CatalogResolver.Modify(profile)
                import_filter = CatalogResolver.Import(self._trestle_root)
                pipeline = Pipeline([import_filter, merge_filter, modify_filter])
                # To start we load the profile and then re-launch to do the work
                if initializing:
                    yield pipeline.process(uri)
                else:
                    for link in profile.imports:
                        yield pipeline.process(link.href)

    @staticmethod
    def get_resolved_profile_catalog(trestle_root: pathlib.Path, profile_path: pathlib.Path) -> cat.Catalog:
        """Create the resolved profile catalog given a profile path."""
        import_filter = CatalogResolver.Import(trestle_root)
        # the first time we just import the profile and launch pipelines from there
        result = next(import_filter.process(str(profile_path), True))
        return result
