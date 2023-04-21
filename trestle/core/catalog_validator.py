# -*- mode:python; coding:utf-8 -*-

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
"""Validate catalog by confirming no duplicate param ids."""
import logging
import pathlib
from typing import Optional

from trestle.common.common_types import TopLevelOscalModel
from trestle.common.list_utils import as_list
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.validator import Validator
from trestle.oscal.catalog import Catalog

logger = logging.getLogger(__name__)


class CatalogValidator(Validator):
    """Validator to confirm all param ids in catalog are unique."""

    def model_is_valid(
        self, model: TopLevelOscalModel, quiet: bool, trestle_root: Optional[pathlib.Path] = None
    ) -> bool:
        """
        Test if the model is valid.

        args:
            model: A top level OSCAL model.
            quiet: Don't report msgs unless invalid.

        returns:
            True (valid) if it is not a catalog, or it is a catalog and its links are 1:1 with resources.
        """
        if not isinstance(model, Catalog):
            return True
        catalog: Catalog = model
        cat_interface = CatalogInterface(catalog)
        param_ids = set()
        for control in cat_interface.get_all_controls_from_dict():
            for param in as_list(control.params):
                if param.id in param_ids:
                    logger.warning(f'Catalog has duplicated parameter id: {param.id} in control {control.id}')
                    return False
                param_ids.add(param.id)
        for param_id in cat_interface.loose_param_dict.keys():
            if param_id in param_ids:
                logger.warning(f'Catalog has duplicated parameter id: {param.id} in control {control.id}')
                return False
        return True
