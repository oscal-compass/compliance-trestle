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
import copy
import logging
import pathlib
import shutil
from typing import Any, Dict, List, Optional, Set

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

import trestle.common.const as const
import trestle.common.log as log
import trestle.core.generators as gens
import trestle.oscal.profile as prof
import trestle.oscal.ssp as ssp
from trestle.common import file_utils
from trestle.common.err import TrestleError, TrestleNotFoundError, handle_generic_command_exception
from trestle.common.list_utils import as_filtered_list, as_list, comma_sep_to_list, comma_colon_sep_to_dict, deep_set, none_if_empty  # noqa E501
from trestle.common.load_validate import load_validate_model_name
from trestle.common.model_utils import ModelUtils
from trestle.core.catalog.catalog_api import CatalogAPI
from trestle.core.commands.author.common import AuthorCommonCommand
from trestle.core.commands.common.cmd_utils import clear_folder
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.core.control_interface import ParameterRep
from trestle.core.models.file_content_type import FileContentType
from trestle.core.profile_resolver import ProfileResolver
from trestle.oscal import OSCAL_VERSION

logger = logging.getLogger(__name__)


class ProfileGenerate(AuthorCommonCommand):
    """Generate profile in markdown form from a profile in the trestle workspace."""

    name = 'profile-generate'

    def _init_arguments(self) -> None:
        name_help_str = 'Name of the source profile model in the trestle workspace'
        self.add_argument('-n', '--name', help=name_help_str, required=True, type=str)
        self.add_argument('-o', '--output', help=const.HELP_MARKDOWN_NAME, required=True, type=str)
        self.add_argument('-y', '--yaml-header', help=const.HELP_YAML_PATH, required=False, type=str)
        self.add_argument(
            '-fo', '--force-overwrite', help=const.HELP_FO_OUTPUT, required=False, action='store_true', default=False
        )
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

            yaml_header: Dict[str, Any] = {}
            if args.yaml_header:
                try:
                    logging.debug(f'Loading yaml header file {args.yaml_header}')
                    yaml = YAML()
                    yaml_header = yaml.load(pathlib.Path(args.yaml_header).open('r'))
                except YAMLError as e:
                    raise TrestleError(f'YAML error loading yaml header for ssp generation: {e}')

            if args.force_overwrite:
                try:
                    logger.info(f'Overwriting the content in {args.output}.')
                    clear_folder(pathlib.Path(args.output))
                except TrestleError as e:  # pragma: no cover
                    raise TrestleError(f'Unable to overwrite contents of {args.output}: {e}')

            # combine command line sections with any in the yaml header, with priority to command line
            sections_dict = comma_colon_sep_to_dict(args.sections)

            profile_path = trestle_root / f'profiles/{args.name}/profile.json'

            markdown_path = trestle_root / args.output

            return self.generate_markdown(
                trestle_root,
                profile_path,
                markdown_path,
                yaml_header,
                args.overwrite_header_values,
                sections_dict,
                comma_sep_to_list(args.required_sections)
            )
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Generation of the profile markdown failed')

    def generate_markdown(
        self,
        trestle_root: pathlib.Path,
        profile_path: pathlib.Path,
        markdown_path: pathlib.Path,
        yaml_header: Dict[str, Any],
        overwrite_header_values: bool,
        sections_dict: Optional[Dict[str, str]],
        required_sections: Optional[List[str]]
    ) -> int:
        """Generate markdown for the controls in the profile.

        Args:
            trestle_root: Root directory of the trestle workspace
            profile_path: Path of the profile json file
            markdown_path: Path to the directory into which the markdown will be written
            yaml_header: Dict to merge into the yaml header of the control markdown
            overwrite_header_values: Overwrite values in the markdown header but allow new items to be added
            sections_dict: Optional dict mapping section short names to long
            required_sections: Optional list of sections that get prompted for prose if not in the profile

        Returns:
            0 on success, 1 on error
        """
        try:
            if sections_dict and const.STATEMENT in sections_dict:
                logger.warning('statement is not allowed as a section name.')
                return CmdReturnCodes.COMMAND_ERROR.value
            _, _, profile = ModelUtils.load_distributed(profile_path, trestle_root)
            catalog, inherited_props = ProfileResolver().get_resolved_profile_catalog_and_inherited_props(
                trestle_root, profile_path, True, True, None, ParameterRep.LEAVE_MOUSTACHE
            )

            deep_set(yaml_header, [const.TRESTLE_GLOBAL_TAG, const.PROFILE, const.TITLE], profile.metadata.title)

            context = ControlContext.generate(ContextPurpose.PROFILE, True, trestle_root, markdown_path)
            context.cli_yaml_header = yaml_header
            context.sections_dict = sections_dict
            context.profile = profile
            context.overwrite_header_values = overwrite_header_values
            context.set_parameters_flag = True
            context.required_sections = required_sections
            context.inherited_props = inherited_props
            catalog_api = CatalogAPI(catalog=catalog, context=context)
            catalog_api.write_catalog_as_markdown()

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
        self.add_argument('-s', '--sections', help=const.HELP_SECTIONS, required=False, type=str)
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
                set_parameters_flag=args.set_parameters,
                regenerate=args.regenerate,
                version=args.version,
                sections_dict=comma_colon_sep_to_dict(args.sections),
                required_sections=comma_sep_to_list(args.required_sections),
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
                if not alter:
                    # the control did not have alters, so add
                    alter = prof.Alter(control_id=new_alter.control_id)

                # even though we removed adds at start, we may have added one already
                if alter.adds:
                    alter.adds.extend(new_alter.adds)
                else:
                    alter.adds = new_alter.adds
                # update the dict with the new alter with its added adds
                alter_dict[new_alter.control_id] = alter
            # get the new list of alters from the dict and update profile
            new_alters = list(alter_dict.values())
            # special case, if all adds were deleted remove such alters completely
            new_alters = list(filter(lambda alt: alt.adds or alt.removes, new_alters))
            if profile.modify.alters != new_alters:
                changed = True
            profile.modify.alters = none_if_empty(new_alters)
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
                        prof.SetParameter(
                            param_id=key,
                            label=param.label,
                            values=param.values,
                            select=param.select,
                            props=param.props
                        )
                    )
            if profile.modify.set_parameters != new_set_params:
                changed = True
            # sort the params first by control sorting then by param_id
            profile.modify.set_parameters = sorted(
                new_set_params, key=lambda param: (param_map[param.param_id], param.param_id)
            )
        if profile.modify:
            profile.modify.set_parameters = none_if_empty(profile.modify.set_parameters)
        return changed

    @staticmethod
    def assemble_profile(
        trestle_root: pathlib.Path,
        parent_prof_name: str,
        md_name: str,
        assem_prof_name: str,
        set_parameters_flag: bool,
        regenerate: bool,
        version: Optional[str],
        sections_dict: Dict[str, str],
        required_sections: List[str],
        allowed_sections: Optional[List[str]]
    ) -> int:
        """
        Assemble the markdown directory into a json profile model file.

        Args:
            trestle_root: The trestle root directory
            parent_prof_name: Optional name of profile used to generate the markdown (default is assem_prof_name)
            md_name: The name of the directory containing the markdown control files for the profile
            assem_prof_name: The name of the assembled profile.  It can be the same as the parent to overwrite
            set_parameters_flag: Use the params and props in yaml header to add or alter setparameters in the profile
            regenerate: Whether to regenerate the uuid's in the profile
            version: Optional version for the assembled profile
            sections_dict: Optional map of short name to long name for sections
            required_sections: List of required sections in assembled profile, as comma-separated short names
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

        parent_prof_path = ModelUtils.get_model_path_for_name_and_class(trestle_root, parent_prof_name, prof.Profile)
        if parent_prof_path is None:
            raise TrestleError(f'Profile {parent_prof_name} does not exist.  An existing profile must be provided.')

        parent_prof, parent_prof_path = load_validate_model_name(trestle_root, parent_prof_name, prof.Profile)
        new_content_type = FileContentType.path_to_content_type(parent_prof_path)

        catalog = ProfileResolver.get_resolved_profile_catalog(
            trestle_root, parent_prof_path, param_rep=ParameterRep.LEAVE_MOUSTACHE
        )

        context = ControlContext.generate(
            ContextPurpose.PROFILE, to_markdown=False, trestle_root=trestle_root, md_root=md_dir
        )
        context.sections_dict = sections_dict
        context.required_sections = required_sections

        # load the editable sections of the markdown and create Adds for them
        # then overwrite the Adds in the existing profile with the new ones
        # keep track if any changes were made
        catalog_api = CatalogAPI(catalog=catalog, context=context)
        found_alters, param_dict, param_map = catalog_api.read_additional_content_from_md(label_as_key=True)

        if allowed_sections is not None:
            for bad_part in [
                    part for alter in found_alters for add in as_list(alter.adds)
                    for part in as_filtered_list(add.parts, lambda a: a.name not in allowed_sections)  # type: ignore
            ]:
                raise TrestleError(f'Profile has alter with name {bad_part.name} not in allowed sections.')

        ProfileAssemble._replace_alter_adds(parent_prof, found_alters)
        if set_parameters_flag:
            ProfileAssemble._replace_modify_set_params(parent_prof, param_dict, param_map)

        if version:
            parent_prof.metadata.version = version

        parent_prof.metadata.oscal_version = OSCAL_VERSION

        assem_prof_path = ModelUtils.get_model_path_for_name_and_class(
            trestle_root, assem_prof_name, prof.Profile, new_content_type
        )

        if assem_prof_path.exists():
            _, _, existing_prof = ModelUtils.load_distributed(assem_prof_path, trestle_root)
            if ModelUtils.models_are_equivalent(existing_prof, parent_prof):  # type: ignore
                logger.info('Assembled profile is no different from existing version, so no update.')
                return CmdReturnCodes.SUCCESS.value

        if regenerate:
            parent_prof, _, _ = ModelUtils.regenerate_uuids(parent_prof)
        ModelUtils.update_last_modified(parent_prof)  # type: ignore

        if assem_prof_path.parent.exists():
            logger.info('Creating profile from markdown and destination profile exists, so updating.')
            shutil.rmtree(str(assem_prof_path.parent))

        assem_prof_path.parent.mkdir(parents=True, exist_ok=True)
        parent_prof.oscal_write(assem_prof_path)  # type: ignore
        return CmdReturnCodes.SUCCESS.value


class ProfileResolve(AuthorCommonCommand):
    """Resolve profile to resolved profile catalog."""

    name = 'profile-resolve'

    def _init_arguments(self) -> None:
        name_help_str = 'Name of the source profile model in the trestle workspace'
        self.add_argument('-n', '--name', help=name_help_str, required=True, type=str)
        self.add_argument('-o', '--output', help='Name of the output resolved profile catalog', required=True, type=str)
        self.add_argument(
            '-sv',
            '--show-values',
            help='Show values for parameters in prose',
            required=False,
            action='store_true',
            default=False
        )
        self.add_argument(
            '-sl',
            '--show-labels',
            help='Show labels for parameters in prose instead of values',
            required=False,
            action='store_true',
            default=False
        )
        self.add_argument(
            '-bf',
            '--bracket-format',
            help='With -sv, allows brackets around value, e.g. [.] or ((.)), with the dot representing the value.',
            required=False,
            type=str,
            default=''
        )
        self.add_argument(
            '-vap',
            '--value-assigned-prefix',
            help='With -sv, places a prefix in front of the parameter string if a value has been assigned.',
            required=False,
            type=str,
            default=''
        )
        self.add_argument(
            '-vnap',
            '--value-not-assigned-prefix',
            help='With -sv, places a prefix in front of the parameter string if a value has *not* been assigned.',
            required=False,
            type=str,
            default=''
        )
        self.add_argument(
            '-lp',
            '--label-prefix',
            help='With -sl, places a prefix in front of the parameter label.',
            required=False,
            type=str,
            default=''
        )

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root: pathlib.Path = args.trestle_root
            profile_path = trestle_root / f'profiles/{args.name}/profile.json'
            catalog_name = args.output
            show_values = args.show_values
            param_format = args.bracket_format
            value_assigned_prefix = args.value_assigned_prefix
            value_not_assigned_prefix = args.value_not_assigned_prefix
            label_prefix = args.label_prefix
            show_labels = args.show_labels

            return self.resolve_profile(
                trestle_root,
                profile_path,
                catalog_name,
                show_values,
                param_format,
                value_assigned_prefix,
                value_not_assigned_prefix,
                show_labels,
                label_prefix
            )

        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Generation of the resolved profile catalog failed')

    def resolve_profile(
        self,
        trestle_root: pathlib.Path,
        profile_path: pathlib.Path,
        catalog_name: str,
        show_values: bool,
        bracket_format: str,
        value_assigned_prefix: Optional[str],
        value_not_assigned_prefix: Optional[str],
        show_labels: bool,
        label_prefix: Optional[str]
    ) -> int:
        """Create resolved profile catalog from given profile.

        Args:
            trestle_root: Root directory of the trestle workspace
            profile_path: Path of the profile json file
            catalog_name: Name of the resolved profile catalog
            show_values: If true, show values of parameters in prose rather than original {{}} form
            bracket_format: String representing brackets around value, e.g. [.] or ((.))
            value_assigned_prefix: Prefix placed in front of param string if a value was assigned
            value_not_assigned_prefix: Prefix placed in front of param string if a value was *not* assigned
            show_labels: Show labels for parameters and not values
            label_prefix: Prefix placed in front of param label

        Returns:
            0 on success and raises exception on error
        """
        if not profile_path.exists():
            raise TrestleNotFoundError(f'Cannot resolve profile catalog: profile {profile_path} does not exist.')

        param_rep = ParameterRep.LEAVE_MOUSTACHE
        if show_values:
            param_rep = ParameterRep.ASSIGNMENT_FORM
            if label_prefix or show_labels:
                raise TrestleError('Use of show-values is not compatible with show-labels or label-prefix')
        elif value_assigned_prefix or value_not_assigned_prefix:
            raise TrestleError('Use of value-assigned-prefix or value-not-assigned-prefix requires show-values')
        if show_labels:
            param_rep = ParameterRep.LABEL_FORM
            # overload value_not_assigned_prefix to use the label_prefix value
            value_not_assigned_prefix = label_prefix
        elif label_prefix:
            raise TrestleError('Use of label-prefix requires show-labels')

        bracket_format = none_if_empty(bracket_format)
        catalog = ProfileResolver().get_resolved_profile_catalog(
            trestle_root,
            profile_path,
            False,
            False,
            bracket_format,
            param_rep,
            False,
            value_assigned_prefix,
            value_not_assigned_prefix
        )
        ModelUtils.save_top_level_model(catalog, trestle_root, catalog_name, FileContentType.JSON)

        return CmdReturnCodes.SUCCESS.value


class ProfileInherit(AuthorCommonCommand):
    """Generate and populate profile in JSON from a parent profile and leveraged ssp in the trestle workspace."""

    name = 'profile-inherit'

    def _init_arguments(self) -> None:
        ssp_help_str = 'Name of the leveraged ssp model in the trestle workspace'
        self.add_argument('-s', '--ssp', help=ssp_help_str, required=True, type=str)
        profile_help_str = 'Name of the parent profile model in the trestle workspace'
        self.add_argument('-p', '--profile', help=profile_help_str, required=True, type=str)
        output_help_str = 'Name of the output generated json Profile'
        self.add_argument('-o', '--output', help=output_help_str, required=True, type=str)
        self.add_argument('-vn', '--version', help=const.HELP_VERSION, required=False, type=str)

    def _run(self, args: argparse.Namespace) -> int:
        try:
            log.set_log_level_from_args(args)
            trestle_root: pathlib.Path = args.trestle_root

            if args.profile:
                if args.profile == args.output:
                    logger.warning(f'Output profile {args.output} cannot equal parent')
                    return CmdReturnCodes.INCORRECT_ARGS.value

            return self.initialize_profile(
                trestle_root=trestle_root,
                parent_prof_name=args.profile,
                output_prof_name=args.output,
                leveraged_ssp_name=args.ssp,
                version=args.version
            )
        except Exception as e:  # pragma: no cover
            return handle_generic_command_exception(e, logger, 'Profile generation failed')

    @staticmethod
    def _is_inherited(all_comps: List[ssp.ByComponent]) -> bool:
        # Fail fast by checking for any non-compliant components.
        # Must contain provided export statements, no responsibility
        # statements, and be implemented.
        for comp in all_comps:
            if comp.export is None:
                return False

            if comp.export.responsibilities is not None:
                return False

            if comp.export.provided is None:
                return False

            if comp.implementation_status.state != const.STATUS_IMPLEMENTED:
                return False

        return True

    @staticmethod
    def update_profile_import(
        orig_prof_import: prof.Import, leveraged_ssp: ssp.SystemSecurityPlan, catalog_api: CatalogAPI
    ) -> None:
        """Add controls to different sections of a profile import based on catalog and leveraged SSP.

        Args:
            orig_prof_import: The original profile import that will have the control selection updated.
            leveraged_ssp: SSP input for control filtering
            catalog_api: Catalog API with access to controls that need to be filtered

        Returns:
            None
        """
        exclude_with_ids: Set[str] = set()
        components_by_id: Dict[str, List[ssp.ByComponent]] = {}

        # Create dictionary containing all by-components by control for faster searching
        for implemented_requirement in leveraged_ssp.control_implementation.implemented_requirements:
            by_components: List[ssp.ByComponent] = []

            if implemented_requirement.by_components:
                by_components.extend(implemented_requirement.by_components)
            if implemented_requirement.statements:
                for stm in implemented_requirement.statements:
                    if stm.by_components:
                        by_components.extend(stm.by_components)
            components_by_id[implemented_requirement.control_id] = none_if_empty(by_components)

        # Looping by controls in the catalog because the ids in the profile should
        # be a subset of the catalog and not the ssp controls.
        catalog_control_ids: Set[str] = set(catalog_api._catalog_interface.get_control_ids())
        for control_id in catalog_control_ids:

            if control_id not in components_by_id:
                continue

            by_comps: Optional[List[ssp.ByComponent]] = components_by_id[control_id]
            if by_comps is not None and ProfileInherit._is_inherited(by_comps):
                exclude_with_ids.add(control_id)

        include_with_ids: Set[str] = catalog_control_ids - exclude_with_ids

        orig_prof_import.include_controls = [prof.SelectControlById(with_ids=sorted(include_with_ids))]
        orig_prof_import.exclude_controls = [prof.SelectControlById(with_ids=sorted(exclude_with_ids))]

    def initialize_profile(
        self,
        trestle_root: pathlib.Path,
        parent_prof_name: str,
        output_prof_name: str,
        leveraged_ssp_name: str,
        version: Optional[str],
    ) -> int:
        """Initialize profile with controls from a parent profile, filtering by inherited controls.

        Args:
            trestle_root: Root directory of the trestle workspace
            parent_prof_name: Name of the parent profile in the trestle workspace
            output_prof_name: Name of the output profile json file
            leveraged_ssp_name: Name of the ssp in the trestle workspace for control filtering
            version: Optional profile version

        Returns:
            0 on success, 1 on error

        Notes:
            The profile model will either be updated or a new json profile created. This will overwrite
            any import information on an exiting profile, but will preserve control modifications and parameters.
            Allowing profile updates ensure that SSP export updates can be incorporated into an existing profile. All
            controls from the original profile will exists and will be grouped by included and excluded controls based
            on inheritance information.
        """
        try:
            result_profile: prof.Profile
            existing_profile: Optional[prof.Profile] = None

            existing_profile_path = ModelUtils.get_model_path_for_name_and_class(
                trestle_root, output_prof_name, prof.Profile
            )

            # If a profile exists at the output path, use that as a starting point for a new profile.
            # else create a new sample profile.
            if existing_profile_path is not None:
                existing_profile, _ = load_validate_model_name(trestle_root,
                                                               output_prof_name,
                                                               prof.Profile,
                                                               FileContentType.JSON)
                result_profile = copy.deepcopy(existing_profile)
            else:
                result_profile = gens.generate_sample_model(prof.Profile)

            parent_prof_path = ModelUtils.get_model_path_for_name_and_class(
                trestle_root, parent_prof_name, prof.Profile
            )
            if parent_prof_path is None:
                raise TrestleNotFoundError(
                    f'Profile {parent_prof_name} does not exist.  An existing profile must be provided.'
                )

            local_path = f'profiles/{parent_prof_name}/profile.json'
            profile_import: prof.Import = gens.generate_sample_model(prof.Import)
            profile_import.href = const.TRESTLE_HREF_HEADING + local_path

            leveraged_ssp: ssp.SystemSecurityPlan
            try:
                leveraged_ssp, _ = load_validate_model_name(
                    trestle_root,
                    leveraged_ssp_name,
                    ssp.SystemSecurityPlan,
                    FileContentType.JSON
                )
            except TrestleNotFoundError as e:
                raise TrestleError(f'SSP {leveraged_ssp_name} not found: {e}')

            prof_resolver = ProfileResolver()
            catalog = prof_resolver.get_resolved_profile_catalog(
                trestle_root, parent_prof_path, show_value_warnings=True
            )
            catalog_api = CatalogAPI(catalog=catalog)

            # Sort controls based on what controls in the SSP have exported provided information with no
            # customer responsibility
            ProfileInherit.update_profile_import(profile_import, leveraged_ssp, catalog_api)

            result_profile.imports[0] = profile_import

            if version:
                result_profile.metadata.version = version

            if ModelUtils.models_are_equivalent(existing_profile, result_profile):
                logger.info('Profile is no different from existing version, so no update.')
                return CmdReturnCodes.SUCCESS.value

            ModelUtils.update_last_modified(result_profile)
            ModelUtils.save_top_level_model(result_profile, trestle_root, output_prof_name, FileContentType.JSON)

        except TrestleError as e:
            raise TrestleError(f'Error initializing profile {output_prof_name}: {e}')
        return CmdReturnCodes.SUCCESS.value
