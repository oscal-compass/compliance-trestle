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
"""Trestle Repository APIs."""

import argparse
import logging
import os
import pathlib
import shutil
from typing import List, Type

import trestle.core.commands.assemble as assemblecmd
import trestle.core.commands.validate as validatecmd
import trestle.core.const as const
from trestle.core import parser
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, WriteFileAction
from trestle.core.models.elements import Element
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.core.utils import classname_to_alias
from trestle.utils import fs

logger = logging.getLogger(__name__)


class ManagedOSCAL:
    """Object representing OSCAL models in repository for programmatic manipulation."""

    def __init__(self, root_dir: pathlib.Path, model_type: Type[OscalBaseModel], name: str) -> None:
        """Initialize repository OSCAL model object."""
        self.root_dir = root_dir
        self.model_type = model_type
        self.model_name = name

    def read(self) -> OscalBaseModel:
        """Read OSCAL model from repository."""
        model_alias = classname_to_alias(self.model_type.__name__, 'json')
        plural_path = fs.model_type_to_model_dir(model_alias)
        desired_model_dir = self.root_dir / plural_path / self.model_name

        if not desired_model_dir.exists() or not desired_model_dir.is_dir():
            raise TrestleError(f'Model {self.model_name} does not exist.')

        model = parser.parse_file(filepath, None)
        return model

    def write(self, model: OscalBaseModel, preserve_split: bool) -> bool:
        """Write OSCAL model to repository."""
        pass

    def split(self, elements: List[str]) -> bool:
        """Split OSCAL model in repository."""
        pass

    def merge(self, elements: List[str]) -> bool:
        """Merge OSCAL model in repository."""
        pass

    def add(self, element: str) -> bool:
        """Add elements to OSCAL model in repository."""
        pass

    def remove(self, element: str) -> bool:
        """Remove elements from OSCAL model in repository."""
        pass

    def validate(self, mode: str) -> bool:
        """Validate OSCAL model in repository."""
        pass


class Repository:
    """Repository object for performing operations on Trestle repository."""

    def __init__(self, root_dir: pathlib.Path) -> None:
        """Initialize trestle epository object."""
        if not fs.is_valid_project_root(root_dir):
            raise TrestleError(f'Provided root directory {str(root_dir)} is not a valid Trestle root directory.')
        self.root_dir = root_dir

    def import_model(self, model: OscalBaseModel, name: str, content_type='json') -> ManagedOSCAL:
        """Import OSCAL object into trestle repository."""
        logger.debug(f'Importing model {name} of type {model.__class__}.')
        model_alias = classname_to_alias(model.__class__.__name__, 'json')

        # Work out output directory and file
        plural_path = fs.model_type_to_model_dir(model_alias)

        desired_model_dir = self.root_dir / plural_path
        desired_model_path = desired_model_dir / name / (model_alias + '.' + content_type)
        desired_model_path = desired_model_path.resolve()

        if desired_model_path.exists():
            raise TrestleError(f'OSCAL file to be created here: {desired_model_path} exists.')

        content_type = FileContentType.to_content_type(pathlib.Path(desired_model_path).suffix)

        # Prepare actions
        top_element = Element(model)
        create_action = CreatePathAction(desired_model_path, True)
        write_action = WriteFileAction(desired_model_path, top_element, content_type)

        # create a plan to create the directory and imported file.
        import_plan = Plan()
        import_plan.add_action(create_action)
        import_plan.add_action(write_action)

        import_plan.simulate()
        import_plan.execute()

        # Validate the imported file, rollback if unsuccessful
        success = False
        errmsg = ''
        try:
            success = self.validate_model(model.__class__, name, 'all')
            if not success:
                errmsg = f'Validation of model {name} did not pass'
        except Exception as err:
            errmsg = f'Import of model {name} failed. Validation failed with error: {err}'

        if not success:
            # rollback in case of validation error or failure
            logger.debug(f'Rolling back import of model {name} to {desired_model_path}')
            try:
                import_plan.rollback()
            except TrestleError as err:
                logger.error(f'Failed to rollback: {err}. Remove {desired_model_path} to resolve state.')
            else:
                logger.debug(f'Successful rollback of import to {desired_model_path}')

            # raise trestle error
            raise TrestleError(errmsg)

        # all well; model was imported and validated successfully
        return ManagedOSCAL(self.root_dir, model.__class__, name)

    def list_models(self, model_type: Type[OscalBaseModel]) -> List[str]:
        """List models of a given type in trestle repository."""
        model_alias = classname_to_alias(model_type.__name__, 'json')
        models = fs.get_models_of_type(model_alias, self.root_dir)

        return models

    def get_model(self, model_type: Type[OscalBaseModel], name: str) -> ManagedOSCAL:
        """Get a specific OSCAL model from repository."""
        model_alias = classname_to_alias(model_type.__name__, 'json')
        plural_path = fs.model_type_to_model_dir(model_alias)
        desired_model_dir = self.root_dir / plural_path / name

        if not desired_model_dir.exists() or not desired_model_dir.is_dir():
            raise TrestleError(f'Model {name} does not exist.')

        return ManagedOSCAL(self.root_dir, model_type, name)

    def delete_model(self, model_type: Type[OscalBaseModel], name: str) -> bool:
        """Delete an OSCAL model from repository."""
        model_alias = classname_to_alias(model_type.__name__, 'json')
        plural_path = fs.model_type_to_model_dir(model_alias)
        desired_model_dir = self.root_dir / plural_path / name

        if not desired_model_dir.exists() or not desired_model_dir.is_dir():
            raise TrestleError(f'Model {name} does not exist.')
        shutil.rmtree(desired_model_dir)

        # remove model from dist directory if it exists
        dist_model_dir = self.root_dir / const.TRESTLE_DIST_DIR / plural_path
        file_content_type = FileContentType.path_to_content_type(dist_model_dir / name)
        if file_content_type != FileContentType.UNKNOWN:
            file_path = pathlib.Path(
                dist_model_dir, name + FileContentType.path_to_file_extension(dist_model_dir / name)
            )
            os.remove(file_path)

        return True

    def assemble_model(self, model_type: Type[OscalBaseModel], name: str, extension='json') -> bool:
        """Assemble an OSCAL model in repository and publish it to 'dist' directory."""
        success = False

        model_alias = classname_to_alias(model_type.__name__, 'json')
        if logger.getEffectiveLevel() <= logging.DEBUG:
            verbose = True
        else:
            verbose = False
        args = argparse.Namespace(
            type=model_alias, name=name, extension=extension, trestle_root=self.root_dir, verbose=verbose
        )

        try:
            ret = assemblecmd.AssembleCmd().assemble_model(model_alias, model_type, args)
            if ret == 0:
                success = True
        except Exception as e:
            raise TrestleError(f'Error in assembling model: {e}')

        return success

    def validate_model(self, model_type: Type[OscalBaseModel], name: str, mode: str) -> bool:
        """Validate an OSCAL model in repository."""
        success = False

        model_alias = classname_to_alias(model_type.__name__, 'json')
        if logger.getEffectiveLevel() <= logging.DEBUG:
            verbose = True
        else:
            verbose = False
        args = argparse.Namespace(type=model_alias, name=name, mode=mode, trestle_root=self.root_dir, verbose=verbose)

        try:
            ret = validatecmd.ValidateCmd()._run(args)
            if ret == 0:
                success = True
        except Exception as e:
            raise TrestleError(f'Error in validating model: {e}')

        return success


if __name__ == '__main__':
    repo_path = pathlib.Path('/Users/admin/trestle-test1')
    repo = Repository(repo_path)
    filepath = pathlib.Path('/Users/admin/Downloads/NIST_SP-800-53_rev4_catalog.json')
    model = parser.parse_file(filepath, None)
    try:
        repo.import_model(model, 'NIST')
        # comment success = repo.validate_model(oscal.catalog.Catalog, 'NIST', 'all')
        # comment success = repo.assemble_model(oscal.catalog.Catalog, 'NIST')
        # comment models = repo.list_models(oscal.catalog.Catalog)
        # comment print(models)
        # comment model = repo.get_model(oscal.catalog.Catalog, 'NIST')
        # comment print(model.root_dir, model.model_type, model.model_name)
        # comment success = repo.delete_model(oscal.catalog.Catalog, 'NIST')
        # comment print(success)
    except TrestleError as e:
        logger.error(e)
