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
"""A Template Versioning."""
import logging
import re
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from pkg_resources import resource_filename, resource_listdir

from trestle.core.commands.author.consts import START_TEMPLATE_VERSION, TEMPLATE_VERSION_HEADER, TRESTLE_RESOURCES
from trestle.core.draw_io import DrawIO
from trestle.core.err import TrestleError
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.utils import fs

logger = logging.getLogger(__name__)


class TemplateVersioning:
    """
    Template versioning solution.

    1. Load template with a specified version.
        1. Template version can be specified via -tv flag
        2. If no version specified the latest version will be used by default.
        3. Otherwise use the templates from the specified version.
    2. Backward compatibility.
        1. Version 0.0.1 will be reserved for the template versions prior to this change.
        2. If the old template path is detected (i.e. without the template version).
            then the filesystem will be updated to the new path with the version.
        3. Upon first run, old template versions prior to this change will be placed to the folder 0.0.1.
        4. If templates have no headers then 0.0.1 version will be used.
    3. Versioning organization.
        1. Template and instance version is added both: in the file system (via path) and in the headers or metadata.
    4. Instance version validation.
        1. Markdown:
            1. When validating the instance the header will be used to validate the version.
        2. Drawio:
            1. When validating the instance the metadata will be used to validate the version.
    """

    @staticmethod
    def update_template_folder_structure(task_path: Path) -> None:
        """
        Automatically detect whether the path is an old style and update it.

        An old-style path is a path of the form:
         root_folder/.trestle/author/{template_name}/{template_objects}
        The new version path is a path of the form:
         root_folder/.trestle/author/{template_name}/{version}/{template_objects}
        By default all old-style templates will be updated to version 0.0.1
        """
        TemplateVersioning._check_if_exists_and_dir(task_path)

        try:
            all_files_wo_version = list(filter(lambda p: p.is_file(), fs.iterdir_without_hidden_files(task_path)))

            new_dir = Path(f'{task_path}/{START_TEMPLATE_VERSION}')
            new_dir.mkdir(parents=True, exist_ok=True)

            if len(all_files_wo_version) == 0:
                logger.debug('No templates outside of the version folders.')

            for f in all_files_wo_version:
                shutil.copy(f, new_dir)

            for p in all_files_wo_version:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()

        except OSError as e:
            logger.error(f'Error while updating template folder: {e}')
            raise TrestleError(f'Error while updating template folder: {e}')
        except Exception as e:
            logger.error(f'Unexpected error while updating template folder: {e}')
            raise TrestleError(f'Unexpected error while updating template folder: {e}')

    @staticmethod
    def validate_template_folder(template_dir: Path):
        """Validate template folder confirms to the versioned path style and has no other subdirectories."""
        TemplateVersioning._check_if_exists_and_dir(template_dir)

        version_regex = r'[0-9]+.[0-9]+.[0-9]+'
        pattern = re.compile(version_regex)
        subdirectories = list(
            filter(lambda p: p.is_dir() and pattern.search(p.parts[-1]) is None, template_dir.iterdir())
        )

        if len(subdirectories) > 0:
            raise TrestleError(f'Subdirectories are not allowed in template folders: {subdirectories}')

    @staticmethod
    def get_versioned_template_dir(task_path: Path, version: Optional[str] = None) -> Path:
        """
        Get a template folder of the specified version.

        If no version is given, the latest version of template will be returned
        """
        TemplateVersioning._check_if_exists_and_dir(task_path)
        latest_path = None
        if version is None:
            latest_path, _ = TemplateVersioning.get_latest_version_for_task(task_path)
        else:
            latest_path = Path(f'{task_path}/{version}/')

        if not latest_path.exists():
            raise TrestleError(f'The task: {task_path} with version: {version} does not exists.')

        return latest_path

    @staticmethod
    def get_latest_version_for_task(task_path: Path) -> Tuple[Path, str]:
        """Get latest version of the template for the given task."""
        TemplateVersioning._check_if_exists_and_dir(task_path)

        all_versions = TemplateVersioning.get_all_versions_for_task(task_path)
        max_version = START_TEMPLATE_VERSION

        if len(all_versions) == 0:
            logger.debug(f'No template versions were found for task: {task_path}, defaulting to 0.0.1')
            max_version = START_TEMPLATE_VERSION
        else:
            max_version = max(all_versions)

        latest_path = Path(f'{task_path}/{max_version}')

        return latest_path, max_version

    @staticmethod
    def get_all_versions_for_task(task_path: Path) -> List[str]:
        """Get all versions for the task."""
        version_regex = r'[0-9]+.[0-9]+.[0-9]+'
        pattern = re.compile(version_regex)
        all_versions = []
        max_version = START_TEMPLATE_VERSION
        for p in task_path.iterdir():
            if p.is_dir() and pattern.search(p.parts[-1]) is not None:
                match = pattern.search(p.parts[-1]).string
                all_versions.append(match)
                if match > max_version:
                    max_version = match

        return all_versions

    @staticmethod
    def write_versioned_template(
        resource_name: str, task_path: Path, target_file: Path, version: Optional[str] = None
    ) -> None:
        """
        Write a template with the header or metadata of a specified version.

        If no version was given the latest version for the task will be used.

        Args:
            resource_name:  Template resource name
            task_path: Task path
            target_file: File path where template will be written
            version: return a resource of a specific version

        Returns:
            A dotted path of a versioned template, list of all available versions
        """
        TemplateVersioning._check_if_exists_and_dir(task_path)
        try:
            templates_resource_path = TRESTLE_RESOURCES + '.templates'

            generic_template = Path(resource_filename(templates_resource_path, resource_name)).resolve()
            if version is None:
                _, version = TemplateVersioning.get_latest_version_for_task(task_path)

            # modify header/metadata in the template
            if generic_template.suffix == '.md':
                md_api = MarkdownAPI()
                header, md_body = md_api.processor.read_markdown_wo_processing(generic_template)
                header[TEMPLATE_VERSION_HEADER] = version
                md_api.write_markdown_with_header(target_file, header, md_body)
                logger.debug(f'Successfully written template markdown to {target_file}')
            elif generic_template.suffix == '.drawio':
                drawio = DrawIO(generic_template)
                metadata = drawio.get_metadata()[0]
                metadata[TEMPLATE_VERSION_HEADER] = version

                drawio.write_drawio_with_metadata(generic_template, metadata, 0, target_file)
                logger.debug(f'Successfully written template drawio to {target_file}')
            else:
                raise TrestleError(f'Unsupported template file extension {generic_template.suffix}')
        except OSError as e:
            logger.error(f'Error while updating template folder: {e}')
            raise TrestleError(f'Error while updating template folder: {e}')

    @staticmethod
    def is_valid_version(template_version: str) -> bool:
        """Check if the version format is correct."""
        if template_version is None:
            return True  # we can have empty version
        if template_version == '0.0.0':
            return False
        version_regex = r'^[0-9]+.[0-9]+.[0-9]+$'
        pattern = re.compile(version_regex)
        if pattern.search(template_version):
            return True
        else:
            return False

    @staticmethod
    def _build_dotted_path(dotted_path: str, all_paths: List[str]) -> None:
        """Traverse template resources and collect all versions."""
        are_all_files = True
        for r in resource_listdir(dotted_path, ''):
            p = Path(resource_filename(dotted_path, r))
            if p.is_dir() and '__pycache__' not in str(p):
                TemplateVersioning._build_dotted_path(dotted_path + '.' + r, all_paths)
                are_all_files = False

        if are_all_files:
            all_paths.append(dotted_path)

    @staticmethod
    def _check_if_exists_and_dir(task_path: Path) -> None:
        if not task_path.exists():
            raise TrestleError(f'Path: {task_path} does not exists.')

        if not task_path.is_dir():
            raise TrestleError(f'File {task_path} passed, however template directory is expected.')
