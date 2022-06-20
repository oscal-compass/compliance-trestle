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
"""Update uuids in model to be sure all are different."""
import pathlib
import sys

from trestle.common.model_utils import ModelUtils
from trestle.core.remote.cache import FetcherFactory


def update_uuids(model_path: str) -> None:
    """Update all the uuids in a model."""
    # cwd must be in trestle project
    fetcher = FetcherFactory.get_fetcher(pathlib.Path.cwd(), model_path)
    model, _ = fetcher.get_oscal(True)
    new_model, _, _ = ModelUtils.regenerate_uuids(model)
    new_model.oscal_write(pathlib.Path(model_path))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        sys.exit(update_uuids(sys.argv[1]))
