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

from trestle.common.err import TrestleError


class FileContentType(Enum):
    """File Content type for read/write."""

    # JSON formatted content
    JSON = 1

    # YAML formatted content
    YAML = 2

    # RFC 8785 canonical JSON formatted content. This is an explicit content type;
    # extension inference still treats canonical JSON files as JSON.
    CANONICAL_JSON = 3

    # No extension and possibly a DIR
    DIRLIKE = 4

    # Type could not be determined
    UNKNOWN = 5

    @classmethod
    def to_file_extension(cls, content_type: 'FileContentType') -> str:
        """Get file extension for the type, including the dot."""
        if content_type == FileContentType.YAML:
            return '.yaml'
        if content_type in [FileContentType.JSON, FileContentType.CANONICAL_JSON]:
            return '.json'
        raise TrestleError(f'Invalid file content type {content_type}')

    @classmethod
    def to_content_type(cls, file_extension: str) -> 'FileContentType':
        """Get content type form file extension, including the dot."""
        if file_extension == '.canonical.json':
            return FileContentType.CANONICAL_JSON
        if file_extension == '.json':
            return FileContentType.JSON
        if file_extension == '.yaml' or file_extension == '.yml':
            return FileContentType.YAML
        if not file_extension:
            return FileContentType.DIRLIKE

        raise TrestleError(f'Unsupported file extension {file_extension}')

    @classmethod
    def path_suffix_to_content_type(cls, file_path: Path) -> 'FileContentType':
        """Get content type from an explicit file path's suffixes without checking existence."""
        if cls._has_canonical_json_suffix(file_path):
            return FileContentType.CANONICAL_JSON
        return FileContentType.to_content_type(file_path.suffix)

    @classmethod
    def _has_canonical_json_suffix(cls, file_path: Path) -> bool:
        """Return True if the path ends with the canonical JSON double extension."""
        return ''.join(file_path.suffixes[-2:]) == '.canonical.json'

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
        return content_type in [FileContentType.JSON, FileContentType.YAML, FileContentType.CANONICAL_JSON]
