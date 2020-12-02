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
"""Action wrapper of a command."""
from enum import Enum

from trestle.core.err import TrestleError


class FileContentType(Enum):
    """File Content type for read/write."""

    # JSON formatted content
    JSON = 1

    # YAML formatted content
    YAML = 2

    @classmethod
    def to_file_extension(cls, content_type: 'FileContentType') -> str:
        """Get file extension for the type."""
        if content_type == FileContentType.YAML:
            return '.yaml'
        elif content_type == FileContentType.JSON:
            return '.json'

        raise TrestleError(f'Invalid file content type {content_type}')

    @classmethod
    def to_content_type(cls, file_extension: str) -> 'FileContentType':
        """Get content type form file extension."""
        if file_extension == '.json':
            return FileContentType.JSON
        elif file_extension == '.yaml' or file_extension == '.yml':
            return FileContentType.YAML

        raise TrestleError(f'Unsupported file extension {file_extension}')
