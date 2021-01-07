# -*- mode:python; coding:utf-8 -*-

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
"""
Cleanup - a basic scropt to cleanup trestle project from various silliness that may occur.

WARNING: This will delete files unprompted so make sure you know what you are doing.
"""

import logging
import pathlib

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def cleanup():
    """Cleanup trestle repo."""
    # sanity check
    assert pathlib.Path('trestle').exists()
    assert pathlib.Path('tests').exists()

    # Remove goop from oscal directory
    oscal_dir = pathlib.Path('trestle/oscal')

    for child in oscal_dir.iterdir():
        split = str(child).split('.')
        if len(split) > 2:
            if split[1] in ['py_flat', 'pyb4fix']:
                logger.info(str(child) + ' REMOVED')
                child.unlink()


if __name__ == '__main__':
    logger.info('Cleaning up trestle repo.')
    cleanup()
    logger.info('Done')
