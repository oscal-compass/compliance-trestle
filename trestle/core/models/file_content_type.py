# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Action wrapper of a command."""
from enum import Enum
from pathlib import Path

from trestle.core.err import TrestleError


class FileContentType(Enum):
    """File Content type for read/write."""

    # JSON formatted content
    JSON = 1

    # YAML formatted content
    YAML = 2

    # No extension and possibly a DIR
    DIRLIKE = 3

    # Type could not be determined
    UNKNOWN = 4

    @classmethod
    def to_file_extension(cls, content_type: 'FileContentType') -> str:
        """Get file extension for the type, including the dot."""
        if content_type == FileContentType.YAML:
            return '.yaml'
        if content_type == FileContentType.JSON:
            return '.json'
        raise TrestleError(f'Invalid file content type {content_type}')

    @classmethod
    def to_content_type(cls, file_extension: str) -> 'FileContentType':
        """Get content type form file extension, including the dot."""
        if file_extension == '.json':
            return FileContentType.JSON
        if file_extension == '.yaml' or file_extension == '.yml':
            return FileContentType.YAML
        if not file_extension:
            return FileContentType.DIRLIKE

        raise TrestleError(f'Unsupported file extension {file_extension}')

    @classmethod
    def path_to_content_type(cls, file_path: Path) -> 'FileContentType':
        """Get content type from file path looking for extension."""
        if file_path.with_suffix('.json').exists():
            return FileContentType.JSON
        if file_path.with_suffix('.yaml').exists():
            return FileContentType.YAML
        if file_path.with_suffix('.yml').exists():
            return FileContentType.YAML
        return FileContentType.UNKNOWN

    @classmethod
    def dir_to_content_type(cls, dir_path: Path) -> 'FileContentType':
        """Get content type by looking for json or yaml files in dir."""
        files = dir_path.glob('*')
        for file in files:
            if file.is_file():
                suffix = file.suffix
                if suffix == '.json':
                    return FileContentType.JSON
                if suffix in ['.yaml', '.yml']:
                    return FileContentType.YAML
        return FileContentType.UNKNOWN

    @classmethod
    def path_to_file_extension(cls, file_path: Path) -> str:
        """Get extension from file path looking for extension."""
        if file_path.with_suffix('.json').exists():
            return '.json'
        if file_path.with_suffix('.yaml').exists():
            return '.yaml'
        if file_path.with_suffix('.yml').exists():
            return '.yml'
        return ''

    @classmethod
    def is_readable_file(cls, content_type: 'FileContentType') -> bool:
        """Is the file a type that can be read directly."""
        return content_type == FileContentType.JSON or content_type == FileContentType.YAML
