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
from typing import Any, Dict, List, Optional

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.common.const as const
import trestle.common.log as log
import trestle.oscal.common as com
import trestle.oscal.profile as prof
from trestle.common import file_utils
from trestle.common.err import TrestleError, TrestleNotFoundError, handle_generic_command_exception
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.control_io import ParameterRep
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver

logger = logging.getLogger(__name__)


def sections_to_dict(sections: Optional[str]) -> Dict[str, str]:
    """
    Convert sections string to dict mapping short to long names.

    Args:
        sections: String containing comma-sep pars of short_name:long_name for sections

    Returns:
        Dict mapping short names to long names

    Notes:
        If the long name is not provided (single string and no :) the long name is same as short name.
        This is needed to map the internal part name for a guidance section to its long name in the formatted markdown.
    """
    sections_dict: Dict[str, str] = {}
    if sections:
        section_pairs = sections.strip("'").split(',')
        # section pair is a single string possibly containing : and is either short_name:long_name or just short_name
        for section_pair in section_pairs:
            if ':' in section_pair:
                section_tuple = section_pair.split(':')
                sections_dict[section_tuple[0].strip()] = section_tuple[1].strip()
            else:
                sections_dict[section_pair] = section_pair
    return sections_dict


class ProfileGenerate(AuthorCommonCommand):
    """Generate profile in markdown form from a profile in the trestle workspace."""

    name = 'profile-generate'

    def _init_arguments(self) -> None:
        name_help_str = 'Name of the source profile model in the trestle workspace'
        self.add_argument('-n', '--name', help=name_help_str, required=True, type=str)
        self.add_argument('-o', '--output', help=const.HELP_MARKDOWN_NAME, required=True, type=str)
        self.add_argument('-y', '--yaml-header', help=const.HELP_YAML_PATH, required=False, type=str)
        self.add_argument(
            '-ohv',
            '--overwrite-header-values',
            help=const.HELP_OVERWRITE_HEADER_VALUES,
            required=False,
            action='store_true',
            default=False
        )
        self.add_argument('-s', '--sections', help=const.HELP_SECTIONS, required=False, type=str)
        self.add_argument('-rs', '--required-sections', help=const.HELP_REQUIRED_SECTIONS, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root: pathlib.Path = args.trestle_root
            if not file_utils.is_directory_name_allowed(args.output):
                raise TrestleError(f'{args.output} is not an allowed directory name')

            yaml_header: dict = {}
            if args.yaml_header:
                try:
                    logging.debug(f'Loading yaml header file {args.yaml_header}')
                    yaml = YAML()
                    yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'))
                except YAMLError as e:
                    raise TrestleError(f'YAML error loading yaml header for ssp generation: {e}')

            # combine command line sections with any in the yaml header, with priority to command line
            sections_dict: Optional[Dict[str, str]] = None
            if args.sections:
                sections_dict = sections_to_dict(args.sections)

            profile_path = trestle_root / f'profiles/{args.name}/profile.json'

            markdown_path = trestle_root / args.output

            return self.generate_markdown(
                trestle_root,
                profile_path,
                markdown_path,
                yaml_header,
                args.overwrite_header_values,
                sections_dict,
                args.required_sections
            )
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Generation of the profile markdown failed')

    def generate_markdown(
        self,
        trestle_root: pathlib.Path,
        profile_path: pathlib.Path,
        markdown_path: pathlib.Path,
        yaml_header: dict,
        overwrite_header_values: bool,
        sections_dict: Optional[Dict[str, str]],
        required_sections: Optional[str]
    ) -> int:
        """Generate markdown for the controls in the profile.

        Args:
            trestle_root: Root directory of the trestle workspace
            profile_path: Path of the profile json file
            markdown_path: Path to the directory into which the markdown will be written
            yaml_header: Dict to merge into the yaml header of the control markdown
            overwrite_header_values: Overwrite values in the markdown header but allow new items to be added
            sections_dict: Optional dict mapping section short names to long
            required_sections: Optional comma-sep list of sections that get prompted for prose if not in the profile

        Returns:
            0 on success, 1 on error
        """
        try:
            if sections_dict and 'statement' in sections_dict:
                logger.warning('statement is not allowed as a section name.')
                return CmdReturnCodes.COMMAND_ERROR.value
            _, _, profile = ModelUtils.load_distributed(profile_path, trestle_root)
            catalog = ProfileResolver().get_resolved_profile_catalog(
                trestle_root, profile_path, True, True, None, ParameterRep.LEAVE_MOUSTACHE
            )
            catalog_interface = CatalogInterface(catalog)
            catalog_interface.write_catalog_as_markdown(
                md_path=markdown_path,
                yaml_header=yaml_header,
                sections_dict=sections_dict,
                prompt_responses=False,
                additional_content=True,
                profile=profile,
                overwrite_header_values=overwrite_header_values,
                set_parameters=True,
                required_sections=required_sections,
                allowed_sections=None
            )
        except TrestleNotFoundError as e:
            raise TrestleError(f'Profile {profile_path} not found, error {e}')
        except TrestleError as e:
            raise TrestleError(f'Error generating the catalog as markdown: {e}')
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
        self.add_argument('-r', '--regenerate', action='store_true', help=const.HELP_REGENERATE)
        self.add_argument('-vn', '--version', help=const.HELP_VERSION, required=False, type=str)
        self.add_argument('-rs', '--required-sections', help=const.HELP_REQUIRED_SECTIONS, required=False, type=str)
        self.add_argument('-as', '--allowed-sections', help=const.HELP_ALLOWED_SECTIONS, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root = pathlib.Path(args.trestle_root)
            return self.assemble_profile(
                trestle_root=trestle_root,
                parent_prof_name=args.name,
                md_name=args.markdown,
                assem_prof_name=args.output,
                set_parameters=args.set_parameters,
                regenerate=args.regenerate,
                version=args.version,
                required_sections=args.required_sections,
                allowed_sections=args.allowed_sections
            )
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Assembly of markdown to profile failed')

    @staticmethod
    def _replace_alter_adds(profile: prof.Profile, alters: List[prof.Alter]) -> bool:
        """Replace the alter adds in the orig_profile with the new ones and return True if changed."""
        changed = False
        if not profile.modify:
            profile.modify = prof.Modify(alters=alters)
            if alters:
                changed = True
        elif not profile.modify.alters:
            profile.modify.alters = alters
            if alters:
                changed = True
        else:
            alter_dict = {}
            # if an alter has adds - remove them up front and build dict of alters by control id
            for alter in profile.modify.alters:
                alter.adds = None
                alter_dict[alter.control_id] = alter
            # now go through new alters and add them to each control in dict by control id
            for new_alter in alters:
                alter = alter_dict.get(new_alter.control_id, None)
                if alter:
                    # even though we removed adds at start, we may have added one already
                    if alter.adds:
                        alter.adds.extend(new_alter.adds)
                    else:
                        alter.adds = new_alter.adds
                    # update the dict with the new alter with its added adds
                    alter_dict[new_alter.control_id] = alter
            # get the new list of alters from the dict and update profile
            new_alters = list(alter_dict.values())
            if profile.modify.alters != new_alters:
                changed = True
            profile.modify.alters = new_alters
        return changed

    @staticmethod
    def _replace_modify_set_params(
        profile: prof.Profile, param_dict: Dict[str, Any], param_map: Dict[str, str]
    ) -> bool:
        """
        Replace the set_params in the profile with list and values from markdown.

        Notes:
            Returns whether or not change was made.
        """
        changed = False
        if param_dict:
            if not profile.modify:
                profile.modify = prof.Modify()
            new_set_params: List[prof.SetParameter] = []
            for key, sub_param_dict in param_dict.items():
                if sub_param_dict:
                    sub_param_dict['id'] = key
                    param = ModelUtils.dict_to_parameter(sub_param_dict)
                    new_set_params.append(
                        prof.SetParameter(param_id=key, label=param.label, values=param.values, select=param.select)
                    )
            if profile.modify.set_parameters != new_set_params:
                changed = True
            # sort the params first by control sorting then by param_id
            profile.modify.set_parameters = sorted(
                new_set_params, key=lambda param: (param_map[param.param_id], param.param_id)
            )
        return changed

    @staticmethod
    def assemble_profile(
        trestle_root: pathlib.Path,
        parent_prof_name: str,
        md_name: str,
        assem_prof_name: str,
        set_parameters: bool,
        regenerate: bool,
        version: Optional[str],
        required_sections: Optional[str],
        allowed_sections: Optional[List[str]]
    ) -> int:
        """
        Assemble the markdown directory into a json profile model file.

        Args:
            trestle_root: The trestle root directory
            parent_prof_name: Optional name of profile used to generate the markdown (default is assem_prof_name)
            md_name: The name of the directory containing the markdown control files for the profile
            assem_prof_name: The name of the assembled profile.  It can be the same as the parent to overwrite
            set_parameters: Use the parameters in the yaml header to specify values for setparameters in the profile
            regenerate: Whether to regenerate the uuid's in the profile
            version: Optional version for the assembled profile
            required_sections: Optional List of required sections in assembled profile, as comma-separated short names
            allowed_sections: Optional list of section short names that are allowed, as comma-separated short names

        Returns:
            0 on success, 1 otherwise

        Notes:
            There must already be a profile model and it will either be updated or a new json profile created.
            The generated markdown has the current values for parameters of controls being imported, as set by
            the original catalog and any intermediate profiles.  It also shows the current SetParameters being applied
            by this profile.  That list of SetParameters can be edited by changing the assigned values and adding or
            removing SetParameters from that list.  During assembly that list will be used to create the SetParameters
            in the assembled profile if the --set-parameters option is specified.
        """
        md_dir = trestle_root / md_name
        if not md_dir.exists():
            raise TrestleError(f'Markdown directory {md_name} does not exist.')

        if not parent_prof_name:
            parent_prof_name = assem_prof_name

        parent_prof, parent_prof_path = ModelUtils.load_top_level_model(trestle_root, parent_prof_name, prof.Profile)
        new_content_type = FileContentType.path_to_content_type(parent_prof_path)

        required_sections_list = required_sections.split(',') if required_sections else []

        # load the editable sections of the markdown and create Adds for them
        # then overwrite the Adds in the existing profile with the new ones
        # keep track if any changes were made
        md_dir = trestle_root / md_name
        found_alters, param_dict, param_map = CatalogInterface.read_additional_content(md_dir, required_sections_list)
        if allowed_sections:
            for alter in found_alters:
                for add in alter.adds:
                    for part in add.parts:
                        if part.name not in allowed_sections:
                            raise TrestleError(f'Profile has alter with name {part.name} not in allowed sections.')
        ProfileAssemble._replace_alter_adds(parent_prof, found_alters)
        if set_parameters:
            ProfileAssemble._replace_modify_set_params(parent_prof, param_dict, param_map)

        if version:
            parent_prof.metadata.version = com.Version(__root__=version)

        assem_prof_path = ModelUtils.path_for_top_level_model(
            trestle_root, assem_prof_name, prof.Profile, new_content_type
        )

        if assem_prof_path.exists():
            _, _, existing_prof = ModelUtils.load_distributed(assem_prof_path, trestle_root)
            if ModelUtils.models_are_equivalent(existing_prof, parent_prof):
                logger.info('Assembled profile is no different from existing version, so no update.')
                return CmdReturnCodes.SUCCESS.value

        if regenerate:
            parent_prof, _, _ = ModelUtils.regenerate_uuids(parent_prof)
        ModelUtils.update_last_modified(parent_prof)

        if assem_prof_path.parent.exists():
            logger.info('Creating profile from markdown and destination profile exists, so updating.')
            shutil.rmtree(str(assem_prof_path.parent))

        assem_prof_path.parent.mkdir(parents=True, exist_ok=True)
        parent_prof.oscal_write(assem_prof_path)
        return CmdReturnCodes.SUCCESS.value
