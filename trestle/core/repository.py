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
"""Trestle Repository APIs."""

import argparse
import logging
import os
import pathlib
import shutil
from typing import List, Type

import trestle.core.commands.assemble as assemblecmd
import trestle.core.commands.merge as mergecmd
import trestle.core.commands.split as splitcmd
import trestle.core.commands.validate as validatecmd
import trestle.core.const as const
from trestle.core import parser
from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.core.models.actions import CreatePathAction, RemovePathAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.file_content_type import FileContentType
from trestle.core.models.plans import Plan
from trestle.core.remote import cache
from trestle.core.utils import classname_to_alias
from trestle.utils import fs
from trestle.utils.load_distributed import load_distributed

logger = logging.getLogger(__name__)


class ManagedOSCAL:
    """Object representing OSCAL models in repository for programmatic manipulation."""

    def __init__(self, root_dir: pathlib.Path, model_type: Type[OscalBaseModel], name: str) -> None:
        """Initialize repository OSCAL model object."""
        if not fs.is_valid_project_root(root_dir):
            raise TrestleError(f'Provided root directory {str(root_dir)} is not a valid Trestle root directory.')
        self.root_dir = root_dir
        self.model_type = model_type
        self.model_name = name

        # set model alais and dir
        self.model_alias = classname_to_alias(self.model_type.__name__, 'json')
        if parser.to_full_model_name(self.model_alias) is None:
            raise TrestleError(f'Given model {self.model_alias} is not a top level model.')

        plural_path = fs.model_type_to_model_dir(self.model_alias)
        self.model_dir = self.root_dir / plural_path / self.model_name

        if not self.model_dir.exists() or not self.model_dir.is_dir():
            raise TrestleError(f'Model dir {self.model_name} does not exist.')

        file_content_type = FileContentType.path_to_content_type(self.model_dir / self.model_alias)
        if file_content_type == FileContentType.UNKNOWN:
            raise TrestleError(f'Model file for model {self.model_name} does not exist.')
        self.file_content_type = file_content_type

        filepath = pathlib.Path(
            self.model_dir,
            self.model_alias + FileContentType.path_to_file_extension(self.model_dir / self.model_alias)
        )

        self.filepath = filepath

    def read(self) -> OscalBaseModel:
        """Read OSCAL model from repository."""
        logger.debug(f'Reading model {self.model_name}.')
        _, _, model = load_distributed(self.filepath, self.root_dir)
        return model

    def write(self, model: OscalBaseModel) -> bool:
        """Write OSCAL model to repository."""
        logger.debug(f'Writing model {self.model_name}.')
        model_alias = classname_to_alias(model.__class__.__name__, 'json')
        if parser.to_full_model_name(model_alias) is None:
            raise TrestleError(f'Given model {model_alias} is not a top level model.')

        # split directory if the model was split
        split_dir = pathlib.Path(self.model_dir, self.model_alias)

        # Prepare actions; delete split model dir if any, recreate model file, and write to filepath
        top_element = Element(model)
        remove_action = RemovePathAction(split_dir)
        create_action = CreatePathAction(self.filepath, True)
        write_action = WriteFileAction(self.filepath, top_element, self.file_content_type)

        # create a plan to create the directory and imported file.
        import_plan = Plan()
        import_plan.add_action(remove_action)
        import_plan.add_action(create_action)
        import_plan.add_action(write_action)

        import_plan.execute()

        logger.debug(f'Model {self.model_name} written to repository')
        return True

    def split(self, model_file: pathlib.Path, elements: List[str]) -> bool:
        """Split the given OSCAL model file in repository.

        Model file path should be relative to the main model directory, e.g., model dir is $TRESTLE_ROOT/catalogs/NIST
        then model file path can be 'catalog/metadata.json' if metadata is to be split.

        Elements should be specified relative to model file, e.g., 'metadata.props.*'
        """
        logger.debug(f'Splitting model {self.model_name}, file {model_file}.')
        # input model_file should be relative to the model dir
        model_file_path = self.model_dir / model_file
        model_file_path = model_file_path.resolve()
        file_parent = model_file_path.parent
        filename = model_file_path.name

        elems = ''
        first = True
        for elem in elements:
            if first:
                elems = elem
                first = False
            else:
                elems = elems + ',' + elem

        success = False
        try:
            ret = splitcmd.SplitCmd().perform_split(file_parent, filename, elems, self.root_dir)
            if ret == 0:
                success = True
        except Exception as e:
            raise TrestleError(f'Error in splitting model: {e}')

        logger.debug(f'Model {self.model_name}, file {model_file} splitted successfully.')
        return success

    def merge(self, elements: List[str], parent_model_dir: pathlib.Path = None) -> bool:
        """Merge OSCAL elements in repository.

        The parent_model_dir specifies the parent model direcotry in which to merge relative to main model dir.
        For example, if we have to merge 'metadata.*' into 'metadata' then parent_model_dir should be the 'catalog'
        dir that contains the 'metadata.json' file or the 'metadata' directory
        """
        logger.debug(f'Merging model {self.model_name}, parent dir {parent_model_dir}.')
        if parent_model_dir is None:
            effective_cwd = self.model_dir
        else:
            effective_cwd = self.model_dir / parent_model_dir

        success = True
        try:
            for elem in elements:
                plan = mergecmd.MergeCmd.merge(effective_cwd, ElementPath(elem), self.root_dir)
                plan.execute()

        except Exception as e:
            raise TrestleError(f'Error in merging model: {e}')

        logger.debug(f'Model {self.model_name} merged successfully.')
        return success

    def validate(self) -> bool:
        """Validate OSCAL model in repository."""
        logger.debug(f'Validating model {self.model_name}.')
        repo = Repository(self.root_dir)
        success = repo.validate_model(self.model_type, self.model_name)
        return success


class Repository:
    """Repository class for performing operations on Trestle repository.

    This class provides a set of APIs to perform operations on trestle repository programmatically
    rather than using the command line. It takes the trestle root directory as input while creating
    an instance of this object. Operations such as import and get model return a ManagedOSCAL object
    representing the specific model that can be used to perform operations on the specific models.

    """

    def __init__(self, root_dir: pathlib.Path) -> None:
        """Initialize trestle repository object."""
        if not fs.is_valid_project_root(root_dir):
            raise TrestleError(f'Provided root directory {str(root_dir)} is not a valid Trestle root directory.')
        self.root_dir = root_dir

    def import_model(self, model: OscalBaseModel, name: str, content_type='json') -> ManagedOSCAL:
        """Import OSCAL object into trestle repository."""
        logger.debug(f'Importing model {name} of type {model.__class__.__name__}.')
        model_alias = classname_to_alias(model.__class__.__name__, 'json')
        if parser.to_full_model_name(model_alias) is None:
            raise TrestleError(f'Given model {model_alias} is not a top level model.')

        # Work out output directory and file
        plural_path = fs.model_type_to_model_dir(model_alias)

        desired_model_dir = self.root_dir / plural_path
        desired_model_path = desired_model_dir / name / (model_alias + '.' + content_type)
        desired_model_path = desired_model_path.resolve()

        if desired_model_path.exists():
            logger.error(f'OSCAL file to be created here: {desired_model_path} exists.')
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
        import_plan.execute()

        # Validate the imported file, rollback if unsuccessful
        success = False
        errmsg = ''
        try:
            success = self.validate_model(model.__class__, name)
            if not success:
                errmsg = f'Validation of model {name} did not pass'
                logger.error(errmsg)
        except Exception as err:
            logger.error(errmsg)
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
        logger.debug(f'Model {name} of type {model.__class__.__name__} imported successfully.')
        return ManagedOSCAL(self.root_dir, model.__class__, name)

    def load_and_import_model(self, model_path: pathlib.Path, name: str, content_type='json') -> ManagedOSCAL:
        """Load the model at the specified path into trestle with the specified name."""
        fetcher = cache.FetcherFactory.get_fetcher(self.root_dir, str(model_path))
        model, _ = fetcher.get_oscal(True)

        return self.import_model(model, name, content_type)

    def list_models(self, model_type: Type[OscalBaseModel]) -> List[str]:
        """List models of a given type in trestle repository."""
        logger.debug(f'Listing models of type {model_type.__name__}.')
        model_alias = classname_to_alias(model_type.__name__, 'json')
        if parser.to_full_model_name(model_alias) is None:
            raise TrestleError(f'Given model {model_alias} is not a top level model.')
        models = fs.get_models_of_type(model_alias, self.root_dir)

        return models

    def get_model(self, model_type: Type[OscalBaseModel], name: str) -> ManagedOSCAL:
        """Get a specific OSCAL model from repository."""
        logger.debug(f'Getting model {name} of type {model_type.__name__}.')
        model_alias = classname_to_alias(model_type.__name__, 'json')
        if parser.to_full_model_name(model_alias) is None:
            raise TrestleError(f'Given model {model_alias} is not a top level model.')
        plural_path = fs.model_type_to_model_dir(model_alias)
        desired_model_dir = self.root_dir / plural_path / name

        if not desired_model_dir.exists() or not desired_model_dir.is_dir():
            logger.error(f'Model {name} does not exist.')
            raise TrestleError(f'Model {name} does not exist.')

        return ManagedOSCAL(self.root_dir, model_type, name)

    def delete_model(self, model_type: Type[OscalBaseModel], name: str) -> bool:
        """Delete an OSCAL model from repository."""
        logger.debug(f'Deleting model {name} of type {model_type.__name__}.')
        model_alias = classname_to_alias(model_type.__name__, 'json')
        if parser.to_full_model_name(model_alias) is None:
            raise TrestleError(f'Given model {model_alias} is not a top level model.')
        plural_path = fs.model_type_to_model_dir(model_alias)
        desired_model_dir = self.root_dir / plural_path / name

        if not desired_model_dir.exists() or not desired_model_dir.is_dir():
            logger.error(f'Model {name} does not exist.')
            raise TrestleError(f'Model {name} does not exist.')
        shutil.rmtree(desired_model_dir)

        # remove model from dist directory if it exists
        dist_model_dir = self.root_dir / const.TRESTLE_DIST_DIR / plural_path
        file_content_type = FileContentType.path_to_content_type(dist_model_dir / name)
        if file_content_type != FileContentType.UNKNOWN:
            file_path = pathlib.Path(
                dist_model_dir, name + FileContentType.path_to_file_extension(dist_model_dir / name)
            )
            logger.debug(f'Deleting model {name} from dist directory.')
            os.remove(file_path)

        logger.debug(f'Model {name} deleted successfully.')
        return True

    def assemble_model(self, model_type: Type[OscalBaseModel], name: str, extension='json') -> bool:
        """Assemble an OSCAL model in repository and publish it to 'dist' directory."""
        logger.debug(f'Assembling model {name} of type {model_type.__name__}.')
        success = False

        model_alias = classname_to_alias(model_type.__name__, 'json')
        if parser.to_full_model_name(model_alias) is None:
            raise TrestleError(f'Given model {model_alias} is not a top level model.')

        if logger.getEffectiveLevel() <= logging.DEBUG:
            verbose = True
        else:
            verbose = False
        args = argparse.Namespace(
            type=model_alias, name=name, extension=extension, trestle_root=self.root_dir, verbose=verbose
        )

        try:
            ret = assemblecmd.AssembleCmd().assemble_model(model_alias, args)
            if ret == 0:
                success = True
        except Exception as e:
            raise TrestleError(f'Error in assembling model: {e}')

        logger.debug(f'Model {name} assembled successfully.')
        return success

    def validate_model(self, model_type: Type[OscalBaseModel], name: str) -> bool:
        """Validate an OSCAL model in repository."""
        logger.debug(f'Validating model {name} of type {model_type.__name__}.')
        success = False

        model_alias = classname_to_alias(model_type.__name__, 'json')
        if parser.to_full_model_name(model_alias) is None:
            raise TrestleError(f'Given model {model_alias} is not a top level model.')

        if logger.getEffectiveLevel() <= logging.DEBUG:
            verbose = True
        else:
            verbose = False
        args = argparse.Namespace(type=model_alias, name=name, trestle_root=self.root_dir, verbose=verbose)

        try:
            ret = validatecmd.ValidateCmd()._run(args)
            if ret == 0:
                success = True
        except Exception as e:
            raise TrestleError(f'Error in validating model: {e}')

        logger.debug(f'Model {name} validated successfully.')
        return success
