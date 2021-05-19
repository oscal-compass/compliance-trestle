# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Functionality for reading information from a drawio file."""
import logging
import pathlib

import defusedxml.ElementTree

import trestle.core.err as err

logger = logging.getLogger(__name__)


class DrawIO(object):
    """Access and process drawio data / metadata."""

    def __init__(self, file_path: pathlib.Path) -> None:
        """
        Load drawio object into memory.

        args:
            file_path: Path to the drawio object.
        """
        self.file_path: pathlib.Path = file_path
        self._load()

    def _load(self) -> bool:
        """Load the file."""
        if not self.file_path.exists() or self.file_path.is_dir():
            logger.error(f'Candidate drawio file {str(self.file_path)} does not exist or is a directory')
            raise err.TrestleError(f'Candidate drawio file {str(self.file_path)} does not exist or is a directory')
        _ = defusedxml.ElementTree(self.file_path)
        return True
