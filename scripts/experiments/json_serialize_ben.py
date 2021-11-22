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
"""Simple script to test json serialization."""
import logging
import pathlib
import timeit

from trestle.oscal.catalog import Catalog

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def run(path: pathlib.Path, count: int) -> None:
    """Run the benchmark."""
    my_catalog = Catalog.oscal_read(path)
    tick = timeit.default_timer()
    for ii in range(count):
        if ii % 2 == 0:
            stuff = my_catalog.oscal_serialize_json(pretty=True)
        else:
            stuff = my_catalog.oscal_serialize_json()
    tock = timeit.default_timer()
    # This line is needed. Without if stuff is not used strange behaviour can occur.
    logger.debug(stuff)
    logger.info('-----------------------------')
    logger.info(f'Time to complete {count} iterations:  {tock - tick}')


if __name__ == '__main__':
    path = pathlib.Path('nist-content/nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json')
    count = 50
    run(path, count)
