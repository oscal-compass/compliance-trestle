# Copyright (c) 2022 IBM Corp. All rights reserved.
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
"""Create resolved catalog from profile."""

import logging
import pathlib
from typing import Iterator, List, Union

import trestle.core.const as const
import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.core.err import TrestleError
from trestle.core.pipeline import Pipeline
from trestle.core.remote import cache
from trestle.core.resolver.merge import Merge
from trestle.core.resolver.modify import Modify
from trestle.core.resolver.prune import Prune

logger = logging.getLogger(__name__)


class Import(Pipeline.Filter):
    """Import filter class."""

    def __init__(
        self,
        trestle_root: pathlib.Path,
        import_: prof.Import,
        change_prose=False,
        block_adds: bool = False,
        params_format: str = None
    ) -> None:
        """Initialize and store trestle root for cache access."""
        self._trestle_root = trestle_root
        self._import = import_
        self._block_adds = block_adds
        self._change_prose = change_prose
        self._params_format = params_format

    def process(self, _=None) -> Iterator[cat.Catalog]:
        """Load href for catalog or profile and yield each import as catalog imported by its distinct pipeline."""
        logger.debug(f'import entering process with href {self._import.href}')
        fetcher = cache.FetcherFactory.get_fetcher(self._trestle_root, self._import.href)

        model: Union[cat.Catalog, prof.Profile]
        model, model_type = fetcher.get_oscal()

        if model_type == const.MODEL_TYPE_CATALOG:
            logger.debug(f'DIRECT YIELD in import of catalog {model.metadata.title}')
            yield model
        else:
            if model_type != const.MODEL_TYPE_PROFILE:
                raise TrestleError(f'Improper model type {model_type} as profile import.')
            profile: prof.Profile = model

            pipelines: List[Pipeline] = []
            logger.debug(
                f'import pipelines for sub_imports of profile {self._import.href} with title {model.metadata.title}'
            )
            for sub_import in profile.imports:
                import_filter = Import(self._trestle_root, sub_import)
                prune_filter = Prune(sub_import, profile)
                pipeline = Pipeline([import_filter, prune_filter])
                pipelines.append(pipeline)
                logger.debug(f'sub_import add pipeline for sub href {sub_import.href} of main href {self._import.href}')
            merge_filter = Merge(profile)
            modify_filter = Modify(profile, self._change_prose, self._block_adds, self._params_format)
            final_pipeline = Pipeline([merge_filter, modify_filter])
            yield next(final_pipeline.process(pipelines))
