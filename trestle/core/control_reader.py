# Copyright (c) 2022 IBM Corp. All rights reserved.
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
"""Handle reading of writing controls from markdown."""
import logging
import pathlib
from typing import Any, Dict, List, Optional, Tuple

import trestle.core.generic_oscal as generic
import trestle.oscal.catalog as cat
from trestle.common import const
from trestle.common.common_types import TypeWithProps
from trestle.common.err import TrestleError
from trestle.common.list_utils import as_list, deep_get, delete_list_from_list, none_if_empty
from trestle.common.model_utils import ModelUtils
from trestle.core import generators as gens
from trestle.core.control_context import ContextPurpose, ControlContext
from trestle.core.control_interface import CompDict, ComponentImpInfo, ControlInterface
from trestle.core.markdown.control_markdown_node import ControlMarkdownNode
from trestle.core.markdown.markdown_api import MarkdownAPI
from trestle.oscal import common
from trestle.oscal import component as comp
from trestle.oscal import profile as prof
from trestle.oscal import ssp as ossp

logger = logging.getLogger(__name__)


class ControlReader:
    """Class to read controls from markdown."""

    @staticmethod
    def _clean_prose(prose: List[str]) -> List[str]:
        # remove empty and horizontal rule lines at start and end of list of prose lines
        forward_index = 0
        for line in prose:
            if line.strip() and not line.startswith('____'):
                break
            forward_index += 1
        new_prose = prose[forward_index:]
        reverse_index = 0
        for line in reversed(new_prose):
            if line.strip() and not line.startswith('____'):
                break
            reverse_index += 1
        clean_prose = new_prose[:len(new_prose) - reverse_index]
        clean_prose = clean_prose if clean_prose else ['']
        # if there is no useful prose this will return [''] and allow generation of a statement with empty prose
        return clean_prose

    @staticmethod
    def _comp_name_in_dict(comp_name: str, comp_dict: CompDict) -> str:
        """If the name is already in the dict in a similar form, stick to that form."""
        simple_name = ControlReader.simplify_name(comp_name)
        for name in comp_dict.keys():
            if simple_name == ControlReader.simplify_name(name):
                return name
        return comp_name

    @staticmethod
    def _add_node_to_dict(
        comp_name: Optional[str],
        label: str,
        comp_dict: CompDict,
        node: ControlMarkdownNode,
        control_id: str,
        comp_list: List[str],
        context: ControlContext
    ) -> None:
        """
        Extract the label, prose, possible component name - along with implementation status.

        In component mode there is only one component and its name is not in markdown.
        In ssp mode there are many components in each md file.
        """
        component_mode = context.purpose == ContextPurpose.COMPONENT
        # for ssp, ### marks component name but for component it is ##
        # if it is a header, make sure it has correct format
        if node.key and node.key[0] == '#' and ControlInterface.bad_header(node.key):
            raise TrestleError(f'Improper header format for control {control_id}: {node.key}')
        if not component_mode:
            # look for component name heading if present
            prefix = '### '
            if node.key.startswith(prefix):
                if len(node.key.split()) <= 1:
                    raise TrestleError(
                        f'Header line in control {control_id} markdown starts with {prefix} but has no content.'
                    )
                comp_name = node.key.split(' ', 1)[1].strip()
                simp_comp_name = ControlReader.simplify_name(comp_name)
                if simp_comp_name in comp_list:
                    raise TrestleError(
                        f'Control {control_id} has a section with two component headings for {comp_name}.  '
                        'Please combine the sections so there is only one heading for each component in a '
                        'statement.'
                    )
                comp_list.append(simp_comp_name)
                comp_name = ControlReader._comp_name_in_dict(comp_name, comp_dict)

        # prose may be empty in md and we want to capture that so put it in the comp_dict
        prose = '\n'.join(ControlReader._clean_prose(node.content.text))
        # add the prose to the comp_dict, creating new entry as needed
        if comp_name in comp_dict:
            if label in comp_dict[comp_name]:
                comp_dict[comp_name][label].prose = prose
            else:
                # create new entry with prose
                comp_dict[comp_name][label] = ComponentImpInfo(prose=prose, rules=[], props=[])
        elif comp_name:
            comp_dict[comp_name] = {label: ComponentImpInfo(prose=prose, rules=[], props=[])}

        # build list of subnodes that get handled specially so they aren't processed here
        subnode_kill: List[int] = []
        status_str = None
        remarks_str = None
        rules_list: List[str] = []
        for ii, subnode in enumerate(node.subnodes):
            if subnode.key.find(const.IMPLEMENTATION_STATUS_REMARKS_HEADER) >= 0:
                remarks_str = subnode.key.split(maxsplit=4)[-1]
                subnode_kill.append(ii)
            elif subnode.key.find(const.IMPLEMENTATION_STATUS_HEADER) >= 0:
                status_str = subnode.key.split(maxsplit=3)[-1]
                subnode_kill.append(ii)
            elif subnode.key.find('Rules:') >= 0:
                rules_list = [text[2:] for text in subnode.content.text if text.startswith('- ')]
                subnode_kill.append(ii)
        if status_str:
            new_status = common.ImplementationStatus(state=status_str, remarks=remarks_str)
            if comp_name not in comp_dict:
                comp_dict[comp_name] = {}
            if label not in comp_dict[comp_name]:
                comp_dict[comp_name][label] = ComponentImpInfo(prose='', rules=[], props=[])
            comp_dict[comp_name][label].status = new_status
        if rules_list:
            comp_dict[comp_name][label].rules = rules_list
        delete_list_from_list(node.subnodes, subnode_kill)
        for subnode in as_list(node.subnodes):
            ControlReader._add_node_to_dict(comp_name, label, comp_dict, subnode, control_id, comp_list, context)

    @staticmethod
    def _insert_header_content(
        imp_req: generic.GenericImplementedRequirement, header: Dict[str, Any], control_id: str
    ) -> None:
        """Insert yaml header content into the imp_req and its by_comps as props."""
        dict_ = header.get(const.TRESTLE_PROPS_TAG, {})
        roles = as_list(dict_.get(const.RESPONSIBLE_ROLES, []))
        props = []
        responsible_roles = []
        for role in roles:
            if isinstance(role, str):
                # role_id must conform to NCNAME regex
                role = role.strip().replace(' ', '_')
                if role:
                    responsible_roles.append(common.ResponsibleRole(role_id=role))
            else:
                logger.warning(f'Role in header for control {control_id} not recognized: {role}')
        if props:
            imp_req.props = as_list(imp_req.props)
            imp_req.props.extend(props)
        if responsible_roles:
            imp_req.responsible_roles = as_list(imp_req.responsible_roles)
            imp_req.responsible_roles.extend(responsible_roles)
            imp_req.responsible_roles = none_if_empty(imp_req.responsible_roles)
            # enforce single list of resp. roles for control and each by_comp
            for by_comp in as_list(imp_req.by_components):
                by_comp.responsible_roles = imp_req.responsible_roles

    @staticmethod
    def simplify_name(name: str) -> str:
        """Simplify the name to ignore variations in case, space, hyphen, underscore, slash."""
        return name.lower().replace(' ', '').replace('-', '').replace('_', '').replace('/', '')

    @staticmethod
    def _get_label_from_implementation_header(imp_header: str):
        # assumed to be of form: Implementation for part a.
        split_header = imp_header.split(' ', 4)
        if len(split_header) != 5:
            raise TrestleError(f'Implementation header cannot be parsed for statement part: {imp_header}')
        return split_header[4].strip()

    @staticmethod
    def read_control_info_from_md(control_file: pathlib.Path,
                                  context: ControlContext) -> Tuple[Dict[str, List[str]], CompDict]:
        """
        Find all labels and associated implementation prose in the markdown for this control.

        Args:
            control_file: path to the control markdown file
            context: context of the control usage

        Returns:
            The yaml header as dict in second part of tuple.
            Adds to the passed in comp_dict.
        """
        yaml_header = {}
        comp_dict = {}

        if not control_file.exists():
            return yaml_header, comp_dict
        # if the file exists, load the contents but do not use prose from comp_dict
        # for non ssp or component mode just use empty string for comp
        comp_name = ''
        try:
            control_id = control_file.stem
            if context.purpose == ContextPurpose.COMPONENT:
                comp_name = context.comp_name if context.comp_name else const.SSP_MAIN_COMP_NAME

            md_api = MarkdownAPI()
            yaml_header, control_md = md_api.processor.process_markdown(control_file)

            # first get the header strings, including statement labels, for statement imp reqs
            imp_string = '## Implementation '
            headers = control_md.get_all_headers_for_level(2)
            # get e.g. ## Implementation a.  ## Implementation b. etc
            imp_header_list = [header for header in headers if header.startswith(imp_string)]

            # now get the (one) header for the main solution
            main_headers = list(control_md.get_all_headers_for_key(const.SSP_MD_IMPLEMENTATION_QUESTION, False))
            # should be only one header, so warn if others found
            if main_headers:
                if len(main_headers) > 1:
                    logger.warning(
                        f'Control {control_id} has {len(main_headers)} main header responses.  Will use first one only.'
                    )
                main_header = main_headers[0]
                node = control_md.get_all_nodes_for_keys([main_header], False)[0]
                # this node is top level so it will have empty label
                # it may have subnodes of Rules, Implementation Status, Implementaton Remarks
                ControlReader._add_node_to_dict(comp_name, '', comp_dict, node, control_id, [], context)
            for imp_header in imp_header_list:
                label = ControlReader._get_label_from_implementation_header(imp_header)
                node = control_md.get_node_for_key(imp_header)
                ControlReader._add_node_to_dict(comp_name, label, comp_dict, node, control_id, [], context)

        except TrestleError as e:
            raise TrestleError(f'Error occurred reading {control_file}: {e}')
        return yaml_header, comp_dict

    @staticmethod
    def _handle_empty_prose(prose: str, id_: str) -> str:
        """Regard prompt text or id_ as no prose and return blank string."""
        if prose.startswith(const.SSP_ADD_IMPLEMENTATION_PREFIX) or prose == id_:
            return ''
        return prose

    @staticmethod
    def read_implemented_requirement(control_file: pathlib.Path,
                                     context: ControlContext) -> Tuple[str, comp.ImplementedRequirement]:
        """
        Get the implementated requirement associated with given control and link to existing components or new ones.

        Args:
            control_file: path of the control markdown file
            context: context of the control usage

        Returns:
            Tuple: The control sort-id and the one implemented requirement for this control.

        Notes:
            Each statement may have several responses, with each response in a by_component for a specific component.
            statement_map keeps track of statements that may have several by_component responses.
            This is only used during component assemble and only for updating one component.
        """
        control_id = control_file.stem
        md_header, md_comp_dict = ControlReader.read_control_info_from_md(control_file, context)
        comp_name = context.component.title

        statement_map: Dict[str, comp.Statement] = {}
        # create a new implemented requirement linked to the control id to hold the statements
        imp_req = gens.generate_sample_model(comp.ImplementedRequirement)
        imp_req.control_id = control_id

        imp_req.statements = []
        comp_dict = md_comp_dict[comp_name]
        for label, comp_info in comp_dict.items():
            # only assemble responses with associated rules
            if not comp_info.rules:
                continue
            # if no label it applies to the imp_req itself rather than a statement
            if not label:
                imp_req.description = ControlReader._handle_empty_prose(comp_info.prose, control_id)
                ControlInterface.insert_status_in_props(imp_req, comp_info.status)
                continue
            statement_id = ControlInterface.create_statement_id(control_id)
            if label in ['', const.STATEMENT]:
                statement_part_id = statement_id
            else:
                clean_label = label.strip('.')
                statement_part_id = ControlInterface.strip_to_make_ncname(f'{statement_id}.{clean_label}')
            if statement_part_id in statement_map:
                statement = statement_map[statement_part_id]
            else:
                statement = gens.generate_sample_model(comp.Statement)
                statement.statement_id = statement_part_id
                statement_map[statement_part_id] = statement
            statement.description = comp_info.prose
            statement.props = none_if_empty(ControlInterface.clean_props(comp_info.props))
            ControlInterface.insert_status_in_props(statement, comp_info.status)

        imp_req.statements = list(statement_map.values())
        imp_req.set_parameters = []

        for _, param_dict_list in md_header.get(const.COMP_DEF_RULES_PARAM_VALS_TAG, {}).items():
            for param_dict in param_dict_list:
                values = param_dict.get(const.VALUES, [])
                comp_values = param_dict.get(const.COMPONENT_VALUES, [])
                values = comp_values if comp_values else values
                set_param = ossp.SetParameter(param_id=param_dict['name'], values=values)
                imp_req.set_parameters.append(set_param)
        imp_req.statements = none_if_empty(list(statement_map.values()))
        imp_req.set_parameters = none_if_empty(imp_req.set_parameters)

        ControlReader._insert_header_content(imp_req, md_header, control_id)
        sort_id = md_header.get(const.SORT_ID, control_id)
        return sort_id, imp_req

    @staticmethod
    def _get_props_list(control_id: str, label_map: Dict[str, str],
                        yaml_header: Dict[str, Any]) -> Tuple[List[common.Property], Dict[str, List[common.Property]]]:
        """Get the list of props in the yaml header of this control as separate lists with and without by_id."""
        prop_list = yaml_header.get(const.TRESTLE_ADD_PROPS_TAG, [])
        props = []
        props_by_id = {}
        for prop_d in prop_list:
            by_id = prop_d.get('smt-part', None)
            if by_id and control_id in label_map:
                by_id = label_map[control_id].get(by_id, by_id)
            prop = common.Property(name=prop_d['name'], value=prop_d['value'], ns=prop_d.get('ns', None))
            if by_id:
                if by_id not in props_by_id:
                    props_by_id[by_id] = []
                props_by_id[by_id].append(prop)
            else:
                props.append(prop)
        return props, props_by_id

    @staticmethod
    def read_editable_content(
        control_path: pathlib.Path,
        required_sections_list: List[str],
        part_label_to_id_map: Dict[str, Dict[str, str]],
        cli_section_dict: Dict[str, str],
        write_mode: bool
    ) -> Tuple[str, List[prof.Alter], Dict[str, Any]]:
        """Get parts for the markdown control corresponding to Editable Content - along with the set-parameter dict."""
        control_id = control_path.stem

        md_api = MarkdownAPI()
        yaml_header, control_tree = md_api.processor.process_control_markdown(control_path, cli_section_dict, part_label_to_id_map)  # noqa: E501
        # extract the sort_id if present in header
        sort_id = yaml_header.get(const.SORT_ID, control_id)

        editable_node = None
        for header in list(control_tree.get_all_headers_for_level(1)):
            if header.startswith('# Editable'):
                editable_node = control_tree.get_node_for_key(header)
                break
        if not editable_node:
            return sort_id, [], {}

        editable_parts = control_tree.get_editable_parts_and_subparts()
        by_id_parts = control_tree.get_by_id_parts()
        found_sections = [p.name for p in editable_parts]

        # Validate that all required sections have a prose
        for editable_part in editable_parts:
            if not write_mode and editable_part.name in required_sections_list and editable_part.prose.startswith(
                    const.PROFILE_ADD_REQUIRED_SECTION_FOR_CONTROL_TEXT):
                raise TrestleError(f'Control {control_id} is missing prose for required section {editable_part.title}')

        # Validate that all required sections are present
        missing_sections = set(required_sections_list) - set(found_sections)
        if missing_sections:
            raise TrestleError(f'Control {control_id} is missing required sections {missing_sections}')
        param_dict: Dict[str, Any] = {}
        # get set_params from the header and add to parm_dict
        header_params = yaml_header.get(const.SET_PARAMS_TAG, {})
        if header_params:
            param_dict.update(header_params)

        props, props_by_id = ControlReader._get_props_list(control_id, part_label_to_id_map, yaml_header)

        # When adding props without by_id it can either be starting or ending and we default to ending
        # This is the default behavior as described for implicit binding in
        # https://pages.nist.gov/OSCAL/concepts/processing/profile-resolution/
        # When adding props to a part using by_id, it is the same situation because it cannot be before or after since
        # props are not in the same list as parts

        adds: List[prof.Add] = []

        # add the parts and props at control level
        if editable_parts or props:
            adds.append(
                prof.Add(
                    parts=none_if_empty(editable_parts), props=none_if_empty(props), position=prof.Position.ending
                )
            )

        # add the parts and props at the part level, by-id
        by_ids = set(by_id_parts.keys()).union(props_by_id.keys())
        for by_id in sorted(by_ids):
            parts = by_id_parts.get(by_id, None)
            props = props_by_id.get(by_id, None)
            adds.append(prof.Add(parts=parts, props=props, position=prof.Position.ending, by_id=by_id))

        new_alters = []
        if adds:
            new_alters = [prof.Alter(control_id=control_id, adds=adds)]
        return sort_id, new_alters, param_dict

    @staticmethod
    def _update_display_prop_namespace(item: TypeWithProps):
        """Set namespace for special property display_name."""
        for prop in as_list(item.props):
            if prop.name == const.DISPLAY_NAME:
                prop.ns = const.TRESTLE_GENERIC_NS

    @staticmethod
    def read_control(control_path: pathlib.Path, set_parameters_flag: bool) -> Tuple[cat.Control, str]:
        """Read the control and group title from the markdown file."""
        control = gens.generate_sample_model(cat.Control)
        md_api = MarkdownAPI()
        yaml_header, control_tree = md_api.processor.process_control_markdown(control_path)
        control_titles = list(control_tree.get_all_headers_for_level(1))
        if len(control_titles) == 0:
            raise TrestleError(f'Control markdown: {control_path} contains no control title.')
        if len(control_titles) > 1:
            raise TrestleError(f'Control markdown: {control_path} contains multiple control titles {control_titles}.')

        control.id = control_tree.subnodes[0].content.control_id
        group_title = control_tree.subnodes[0].content.control_group
        control.title = control_tree.subnodes[0].content.control_title

        control_statement = control_tree.get_control_statement()
        statement_part = control_statement.content.part

        control.parts = [statement_part] if statement_part else None
        control_objective = control_tree.get_control_objective()
        if control_objective is not None:
            objective_part = control_objective.content.part
            if objective_part:
                if control.parts:
                    control.parts.append(objective_part)
                else:
                    control.parts = [objective_part]

        control_guidance = control_tree.get_control_guidance()
        if control_guidance is not None:
            guidance_part = control_guidance.content.part
            if guidance_part:
                if control.parts:
                    control.parts.append(guidance_part)
                else:
                    control.parts = [guidance_part]

        all_other_parts = []
        for section_node in control_tree.get_other_control_parts():
            parts = section_node.content.part
            all_other_parts.extend([parts])
        if all_other_parts:
            if control.parts:
                control.parts.extend(all_other_parts)
            else:
                control.parts = all_other_parts

        if set_parameters_flag:
            params: Dict[str, str] = yaml_header.get(const.SET_PARAMS_TAG, [])
            if params:
                control.params = []
                for id_, param_dict in params.items():
                    param_dict['id'] = id_
                    param = ModelUtils.dict_to_parameter(param_dict)
                    # if display_name is in list of properties, set its namespace
                    ControlReader._update_display_prop_namespace(param)
                    control.params.append(param)
        sort_id = deep_get(yaml_header, [const.TRESTLE_GLOBAL_TAG, const.SORT_ID], None)
        if sort_id:
            control.props = control.props if control.props else []
            control.props.append(common.Property(name=const.SORT_ID, value=sort_id))
        return control, group_title
