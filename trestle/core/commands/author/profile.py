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
"""Author commands to generate profile as markdown and assemble to json after edit."""

import argparse
import logging
import pathlib
import shutil
import traceback
from typing import Dict, List

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.common.const as const
import trestle.common.log as log
import trestle.oscal.common as com
import trestle.oscal.profile as prof
from trestle.common import file_utils
from trestle.common.err import TrestleError, TrestleNotFoundError
from trestle.common.list_utils import as_list
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.control_io import ControlIOReader, ParameterRep
from trestle.core.profile_resolver import ProfileResolver

logger = logging.getLogger(__name__)


class ProfileGenerate(AuthorCommonCommand):
    """Generate profile in markdown form from a profile in the trestle workspace."""

    name = 'profile-generate'

    def _init_arguments(self) -> None:
        name_help_str = 'Name of the source profile model in the trestle workspace'
        self.add_argument('-n', '--name', help=name_help_str, required=True, type=str)
        self.add_argument('-o', '--output', help=const.HELP_MARKDOWN_NAME, required=True, type=str)
        self.add_argument('-y', '--yaml-header', help=const.HELP_YAML_PATH, required=False, type=str)
        self.add_argument('-sp', '--set-parameters', action='store_true', help=const.HELP_SET_PARAMS, required=False)
        self.add_argument(
            '-ohv',
            '--overwrite-header-values',
            help=const.HELP_OVERWRITE_HEADER_VALUES,
            required=False,
            action='store_true',
            default=False
        )

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = args.trestle_root
            if not file_utils.is_directory_name_allowed(args.output):
                logger.warning(f'{args.output} is not an allowed directory name')
                return CmdReturnCodes.COMMAND_ERROR.value

            yaml_header: dict = {}
            if 'yaml_header' in args and args.yaml_header is not None:
                try:
                    logging.debug(f'Loading yaml header file {args.yaml_header}')
                    yaml = YAML()
                    yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'))
                except YAMLError as e:
                    logging.warning(f'YAML error loading yaml header for ssp generation: {e}')
                    return CmdReturnCodes.COMMAND_ERROR.value

            profile_path = trestle_root / f'profiles/{args.name}/profile.json'

            markdown_path = trestle_root / args.output

            return self.generate_markdown(
                trestle_root,
                profile_path,
                markdown_path,
                yaml_header,
                args.overwrite_header_values,
                args.set_parameters
            )
        except Exception as e:
            logger.error(f'Generation of the profile markdown failed with error: {e}')
            logger.debug(traceback.format_exc())
            return CmdReturnCodes.COMMAND_ERROR.value

    def generate_markdown(
        self,
        trestle_root: pathlib.Path,
        profile_path: pathlib.Path,
        markdown_path: pathlib.Path,
        yaml_header: dict,
        overwrite_header_values: bool,
        set_parameters: bool
    ) -> int:
        """Generate markdown for the controls in the profile.

        Args:
            trestle_root: Root directory of the trestle workspace
            profile_path: Path of the profile json file
            markdown_path: Path to the directory into which the markdown will be written
            yaml_header: Dict to merge into the yaml header of the control markdown
            overwrite_header_values: Overwrite values in the markdown header but allow new items to be added
            set_parameters: Generate list of control parameters in yaml headers, with values if set by this profile

        Returns:
            0 on success, 1 on error
        """
        try:
            _, _, profile = ModelUtils.load_distributed(profile_path, trestle_root)
            catalog = ProfileResolver().get_resolved_profile_catalog(
                trestle_root, profile_path, True, None, ParameterRep.LEAVE_MOUSTACHE
            )
            catalog_interface = CatalogInterface(catalog)
            catalog_interface.write_catalog_as_markdown(
                md_path=markdown_path,
                yaml_header=yaml_header,
                sections=None,
                prompt_responses=False,
                additional_content=True,
                profile=profile,
                overwrite_header_values=overwrite_header_values,
                set_parameters=set_parameters
            )
        except TrestleNotFoundError as e:
            logger.warning(f'Profile {profile_path} not found, error {e}')
            return CmdReturnCodes.COMMAND_ERROR.value
        except TrestleError as e:
            logger.warning(f'Error generating the catalog as markdown: {e}')
            return CmdReturnCodes.COMMAND_ERROR.value
        return CmdReturnCodes.SUCCESS.value


class ProfileAssemble(AuthorCommonCommand):
    """Assemble markdown files of controls into a Profile json file."""

    name = 'profile-assemble'

    def _init_arguments(self) -> None:
        name_help_str = (
            'Optional name of the profile model in the trestle workspace that is being modified.  '
            'If not provided the output name is used.'
        )
        self.add_argument('-n', '--name', help=name_help_str, required=False, type=str)
        file_help_str = 'Name of the source markdown file directory'
        self.add_argument('-m', '--markdown', help=file_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json Profile (ok to overwrite original)'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        self.add_argument('-sp', '--set-parameters', action='store_true', help=const.HELP_SET_PARAMS, required=False)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = pathlib.Path(args.trestle_root)
            # the original profile model name defaults to being the same as the new one
            prof_name = args.output if not args.name else args.name
            return self.assemble_profile(
                trestle_root=trestle_root,
                orig_profile_name=prof_name,
                md_name=args.markdown,
                new_profile_name=args.output,
                set_parameters=args.set_parameters
            )
        except Exception as e:
            logger.error(f'Assembly of markdown to profile failed with error: {e}')
            logger.debug(traceback.format_exc())
            return CmdReturnCodes.COMMAND_ERROR.value

    @staticmethod
    def _replace_alter_adds(profile: prof.Profile, alters: List[prof.Alter]) -> None:
        """Replace the alter adds in the orig_profile with the new ones."""
        if not profile.modify:
            profile.modify = prof.Modify(alters=alters)
        elif not profile.modify.alters:
            profile.modify.alters = alters
        else:
            alter_dict = {}
            # if an alter has adds - remove them up front and build dict of alters by control id
            for alter in profile.modify.alters:
                alter.adds = None
                alter_dict[alter.control_id] = alter
            # now go through new alters and add them to each control in dict by control id
            for new_alter in alters:
                alter = alter_dict.get(new_alter.control_id, None)
                if alter is None:
                    alter_dict[new_alter.control_id] = alter
                else:
                    # even though we removed adds at start, we may have added one already
                    if alter.adds:
                        alter.adds.extend(new_alter.adds)
                    else:
                        alter.adds = new_alter.adds
                    # update the dict with the new alter with its added adds
                    alter_dict[new_alter.control_id] = alter
            # get the new list of alters from the dict and update profile
            new_alters = list(alter_dict.values())
            profile.modify.alters = new_alters

    @staticmethod
    def _replace_modify_set_params(profile: prof.Profile, param_str_dict: Dict[str, str]) -> None:
        """Update the set_params in the profile with new values from markdown."""
        if param_str_dict:
            if not profile.modify:
                profile.modify = prof.Modify()
            profile.modify.set_parameters = as_list(profile.modify.set_parameters)
            # create mapping of original param_id to value for profile
            # then update it with new or additional mappings in param_str_dict
            profile_param_str_dict = {}
            for set_param in profile.modify.set_parameters:
                param = CatalogInterface.setparam_to_param(set_param.param_id, set_param)
                param_str = ControlIOReader.param_to_str(param, ParameterRep.VALUE_OR_LABEL_OR_CHOICES)
                profile_param_str_dict[set_param.param_id] = param_str
            profile_param_str_dict.update(param_str_dict)
            new_set_params = []
            for key, value in profile_param_str_dict.items():
                if value:
                    new_set_params.append(prof.SetParameter(param_id=key, values=[com.ParameterValue(__root__=value)]))
            profile.modify.set_parameters = new_set_params

    @staticmethod
    def assemble_profile(
        trestle_root: pathlib.Path, orig_profile_name: str, md_name: str, new_profile_name: str, set_parameters: bool
    ) -> int:
        """
        Assemble the markdown directory into a json profile model file.

        Args:
            trestle_root: The trestle root directory
            orig_profile_name: Optional name of original profile used to generate the markdown (default is md_name)
            md_name: The name of the directory containing the markdown control files for the profile
            new_profile_name: The name of the new json profile.  It can be the same as original to overwrite
            set_parameters: Use the parameters in the yaml header to specify values for parameters in the profile

        Returns:
            0 on success, 1 otherwise

        Notes:
            There must already be a json profile model and it will either be updated or a new json profile created.
        """
        md_dir = trestle_root / md_name
        profile_path = trestle_root / f'profiles/{orig_profile_name}/profile.json'
        _, _, orig_profile = ModelUtils.load_distributed(profile_path, trestle_root, prof.Profile)
        # load the editable sections of the markdown and create Adds for them
        # then overwrite the Adds in the existing profile with the new ones
        found_alters, param_str_dict = CatalogInterface.read_additional_content(md_dir)
        ProfileAssemble._replace_alter_adds(orig_profile, found_alters)
        if set_parameters:
            ProfileAssemble._replace_modify_set_params(orig_profile, param_str_dict)

        new_prof_dir = trestle_root / f'profiles/{new_profile_name}'

        if new_prof_dir.exists():
            logger.info('Creating profile from markdown and destination profile directory exists, so updating.')
            try:
                shutil.rmtree(str(new_prof_dir))
            except OSError as e:
                raise TrestleError(f'OSError deleting existing catalog directory with rmtree {new_prof_dir}: {e}')
        try:
            new_prof_dir.mkdir()
            orig_profile.oscal_write(new_prof_dir / 'profile.json')
        except OSError as e:
            raise TrestleError(f'OSError writing profile from markdown to {new_prof_dir}: {e}')
        return CmdReturnCodes.SUCCESS.value
