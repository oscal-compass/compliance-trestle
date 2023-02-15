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
import os
import pathlib
from typing import Iterator, List, Optional, Union

import trestle.common.const as const
import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.common.err import TrestleError
from trestle.core.control_interface import ParameterRep
from trestle.core.pipeline import Pipeline
from trestle.core.remote import cache
from trestle.core.resolver.merge import Merge
from trestle.core.resolver.modify import Modify
from trestle.core.resolver.prune import Prune
from trestle.oscal.common import Resource

logger = logging.getLogger(__name__)


class Import(Pipeline.Filter):
    """Import filter class."""

    def __init__(
        self,
        trestle_root: pathlib.Path,
        import_: prof.Import,
        uuid_chain: List[str],
        change_prose=False,
        block_adds: bool = False,
        block_params: bool = False,
        params_format: str = None,
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES,
        resources: Optional[List[Resource]] = None,
        show_value_warnings: bool = False,
        value_assigned_prefix: Optional[str] = None,
        value_not_assigned_prefix: Optional[str] = None,
        parent_url_root: Optional[str] = None
    ) -> None:
        """Initialize and store trestle root for cache access."""
        self._trestle_root = trestle_root
        self._import = import_
        self._uuid_chain = uuid_chain
        self._block_adds = block_adds
        self._block_params = block_params
        self._change_prose = change_prose
        self._params_format = params_format
        self._param_rep = param_rep
        self._resources = resources
        self.show_value_warnings = show_value_warnings
        self.value_assigned_prefix = value_assigned_prefix
        self.value_not_assigned_prefix = value_not_assigned_prefix
        self._parent_url_root = parent_url_root

        if not self._import.href or not self._import.href.strip():
            raise TrestleError('Attempt to import via an empty href.')

        if self._import.href[0] == '#':
            # Specification section on internal reference resolution:
            # https://pages.nist.gov/OSCAL/concepts/processing/profile-resolution/#d2e300-head
            # if href is a local reference, replace it with the actual uri in the resources
            try:
                resource = [r for r in self._resources if r.uuid == self._import.href[1:]][0]
                self._import.href = [
                    rlink.href
                    for rlink in resource.rlinks
                    if rlink.href.endswith('.json') or rlink.href.endswith('.yaml') or rlink.href.endswith('.yml')
                ][0]

            except Exception as e:
                logger.debug(f'Profile resolution failed for resource with uuid: {self._import.href}')
                raise TrestleError(
                    f'Back matter resource resolution needed for profile import failed with error: {str(e)}'
                )

        uri_type = cache.FetcherFactory.get_uri_type(self._import.href)
        # if this looks like a relative path to remote source, append parent path
        if uri_type == cache.FetcherFactory.UriType.LOCAL_FILE and self._parent_url_root:
            self._import.href = self._parent_url_root + '/' + self._import.href
        # if href is now a remote path, capture its parent path for possible use with child imports that are relative
        if cache.FetcherFactory.uri_type_is_not_local(uri_type):
            self._parent_url_root = os.path.dirname(self._import.href)
            logger.debug('parent url root path %s', self._parent_url_root)
        logger.debug('import href is %s', self._import.href)

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
            # profile uuid's must be unique or they may trigger circular reference warning
            if profile.uuid in self._uuid_chain:
                raise TrestleError(f'Profile {profile.metadata.title} is referenced in circular manner.')
            self._uuid_chain.append(profile.uuid)
            resources = profile.back_matter.resources if profile.back_matter and profile.back_matter.resources else None

            pipelines: List[Pipeline] = []
            logger.debug(
                f'import pipelines for sub_imports of profile {self._import.href} with title {model.metadata.title}'
            )
            for sub_import in profile.imports:
                import_filter = Import(
                    self._trestle_root,
                    sub_import,
                    self._uuid_chain,
                    resources=resources,
                    parent_url_root=self._parent_url_root
                )
                prune_filter = Prune(sub_import, profile)
                pipeline = Pipeline([import_filter, prune_filter])
                pipelines.append(pipeline)
                logger.debug(f'sub_import add pipeline for sub href {sub_import.href} of main href {self._import.href}')
            merge_filter = Merge(profile)
            modify_filter = Modify(
                profile,
                self._change_prose,
                self._block_adds,
                self._block_params,
                self._params_format,
                self._param_rep,
                self.show_value_warnings,
                self.value_assigned_prefix,
                self.value_not_assigned_prefix
            )
            final_pipeline = Pipeline([merge_filter, modify_filter])
            yield next(final_pipeline.process(pipelines))
