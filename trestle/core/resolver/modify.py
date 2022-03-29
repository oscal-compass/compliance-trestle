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
"""Create resolved catalog from profile."""

import logging
import re
from typing import Dict, Iterator, List, Optional

import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.common.common_types import OBT
from trestle.common.err import TrestleError, TrestleNotFoundError
from trestle.common.list_utils import as_list
from trestle.core.catalog_interface import CatalogInterface
from trestle.core.control_io import ControlIOReader, ParameterRep
from trestle.core.pipeline import Pipeline
from trestle.oscal import common

logger = logging.getLogger(__name__)


class Modify(Pipeline.Filter):
    """Modify the controls based on the profile."""

    def __init__(
        self,
        profile: prof.Profile,
        change_prose: bool = False,
        block_adds: bool = False,
        block_params: bool = False,
        params_format: str = None,
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) -> None:
        """Initialize the filter."""
        self._profile = profile
        self._catalog_interface: Optional[CatalogInterface] = None
        self._block_adds = block_adds
        self._block_params = block_params
        self._change_prose = change_prose
        self._params_format = params_format
        self._param_rep = param_rep
        logger.debug(f'modify initialize filter with profile {profile.metadata.title}')

    @staticmethod
    def _replace_ids_with_text(prose: str, param_rep: ParameterRep, param_dict: Dict[str, common.Parameter]) -> str:
        """Find all instances of param_ids in prose and replace each with corresponding parameter representation.

        Need to check all values in dict for a match
        Reject matches where the string has an adjacent alphanumeric char: param_1 and param_10 or aparam_1
        """
        for param in param_dict.values():
            if param.id not in prose:
                continue
            # create the replacement text for the param_id
            param_str = ControlIOReader.param_to_str(param, param_rep)
            # non-capturing groups are odd in re.sub so capture all 3 groups and replace the middle one
            pattern = r'(^|[^a-zA-Z0-9_])' + param.id + r'($|[^a-zA-Z0-9_])'
            prose = re.sub(pattern, r'\1' + param_str + r'\2', prose)
        return prose

    @staticmethod
    def _replace_params(
        text: str,
        param_dict: Dict[str, common.Parameter],
        params_format: Optional[str] = None,
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) -> str:
        """
        Replace params found in moustaches with values from the param_dict.

        A single line of prose may contain multiple moustaches.
        """
        # first check if there are any moustache patterns in the text
        if param_rep == ParameterRep.LEAVE_MOUSTACHE:
            return text
        staches: List[str] = re.findall(r'{{.*?}}', text)
        if not staches:
            return text
        # now have list of all staches including braces, e.g. ['{{foo}}', '{{bar}}']
        # clean the staches so they just have the param ids
        param_ids = []
        for stache in staches:
            # remove braces so these are just param_ids but may have extra chars
            stache_contents = stache[2:(-2)]
            param_id = stache_contents.replace('insert: param,', '').strip()
            param_ids.append(param_id)

        # now replace original stache text with param values
        for i, _ in enumerate(staches):
            # A moustache may refer to a param_id not listed in the control's params
            if param_ids[i] not in param_dict:
                logger.warning(f'Control prose references param {param_ids[i]} not set in the control: {staches}')
            elif param_dict[param_ids[i]] is not None:
                param = param_dict[param_ids[i]]
                param_str = ControlIOReader.param_to_str(param, param_rep, False, False, params_format)
                text = text.replace(staches[i], param_str, 1).strip()
            else:
                logger.warning(f'Control prose references param {param_ids[i]} with no specified value.')
        return text

    @staticmethod
    def _replace_part_prose(
        control: cat.Control,
        part: common.Part,
        param_dict: Dict[str, common.Parameter],
        params_format: Optional[str] = None,
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) -> None:
        """Replace the part prose according to set_param."""
        if part.prose is not None:
            fixed_prose = Modify._replace_params(part.prose, param_dict, params_format, param_rep)
            # change the prose in the control itself
            part.prose = fixed_prose
        for prt in as_list(part.parts):
            Modify._replace_part_prose(control, prt, param_dict, params_format, param_rep)
        for sub_control in as_list(control.controls):
            for prt in as_list(sub_control.parts):
                Modify._replace_part_prose(sub_control, prt, param_dict, params_format, param_rep)

    @staticmethod
    def _replace_control_prose(
        control: cat.Control,
        param_dict: Dict[str, common.Parameter],
        params_format: Optional[str] = None,
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) -> None:
        """Replace the control prose according to set_param."""
        for part in as_list(control.parts):
            if part.prose is not None:
                fixed_prose = Modify._replace_params(part.prose, param_dict, params_format, param_rep)
                # change the prose in the control itself
                part.prose = fixed_prose
            for prt in as_list(part.parts):
                Modify._replace_part_prose(control, prt, param_dict, params_format, param_rep)
        for param in as_list(control.params):
            Modify._replace_param_choices(param, param_dict)

    @staticmethod
    def _add_contents_as_list(add: prof.Add) -> List[OBT]:
        add_list = []
        add_list.extend(as_list(add.props))
        add_list.extend(as_list(add.parts))
        add_list.extend(as_list(add.links))
        return add_list

    @staticmethod
    def _add_adds_to_part(part: common.Part, add: prof.Add) -> None:
        for attr in ['params', 'props', 'parts', 'links']:
            add_list = getattr(add, attr, None)
            if add_list:
                Modify._add_attr_to_part(part, add_list, attr, add.position)

    @staticmethod
    def _add_to_list(input_list: List[OBT], add: prof.Add) -> bool:
        """Add the contents of the add according to its by_id and position.

        Return True on success or False if id needed and not found.

        This is only called when by_id is not None.
        The add will be inserted if the id is found, or return False if not.
        This allows a separate recursive routine to search sub-lists for the id.
        """
        add_list = Modify._add_contents_as_list(add)
        # Test here for matched by_id attribute.
        try:
            for index in range(len(input_list)):
                if input_list[index].id == add.by_id:
                    if add.position == prof.Position.after:
                        for offset, new_item in enumerate(add_list):
                            input_list.insert(index + 1 + offset, new_item)
                        return True
                    elif add.position == prof.Position.before:
                        for offset, new_item in enumerate(add_list):
                            input_list.insert(index + offset, new_item)
                        return True
                    # if starting or ending, the adds go directly into this part according to type
                    Modify._add_adds_to_part(input_list[index], add)
                    return True
        except AttributeError:
            raise TrestleError(
                'Cannot use "after" or "before" modifications for a list where elements'
                + ' do not contain the referenced by_id attribute.'
            )
        return False

    @staticmethod
    def _add_to_parts(parts: List[common.Part], add: prof.Add) -> bool:
        """
        Add the add to the parts.

        This is only called if add.by_id is not None.
        """
        if Modify._add_to_list(parts, add):
            return True
        for part in parts:
            if part.parts is not None and Modify._add_to_parts(part.parts, add):
                return True
        return False

    @staticmethod
    def _add_attr_to_part(part: common.Part, items: List[OBT], attr: str, position: prof.Position) -> None:
        attr_list = as_list(getattr(part, attr, None))
        if position in [prof.Position.starting, prof.Position.before]:
            items.extend(attr_list)
            attr_list = items
        else:
            attr_list.extend(items)
        setattr(part, attr, attr_list)

    @staticmethod
    def _add_attr_to_control(control: cat.Control, items: List[OBT], attr: str, position: prof.Position) -> None:
        attr_list = as_list(getattr(control, attr, None))
        if position in [prof.Position.starting, prof.Position.before]:
            items.extend(attr_list)
            attr_list = items
        else:
            attr_list.extend(items)
        setattr(control, attr, attr_list)

    @staticmethod
    def _add_to_control(control: cat.Control, add: prof.Add) -> None:
        """First step in applying Add to control."""
        control.parts = as_list(control.parts)
        if add.by_id is None or add.by_id == control.id:
            # add contents will be added to the control directly and with no recursion
            for attr in ['params', 'props', 'parts', 'links']:
                add_list = getattr(add, attr, None)
                if add_list:
                    Modify._add_attr_to_control(control, add_list, attr, add.position)
            return
        else:
            # this is only called if by_id is not None
            if not Modify._add_to_parts(control.parts, add):
                logger.warning(f'Could not find id for add in control {control.id}: {add.by_id}')

    @staticmethod
    def _set_overwrite_items(param: common.Parameter, set_param: prof.SetParameter) -> None:
        # these overwrite
        if set_param.class_:
            param.class_ = set_param.class_
        if set_param.depends_on:
            param.depends_on = set_param.depends_on
        if set_param.label:
            param.label = set_param.label
        if set_param.usage:
            param.usage = set_param.usage
        if set_param.values:
            param.values = set_param.values
        if set_param.select:
            param.select = set_param.select

    @staticmethod
    def _set_appended_items(param: common.Parameter, set_param: prof.SetParameter) -> None:
        # these append
        if set_param.constraints:
            if not param.constraints:
                param.constraints = []
            param.constraints.extend(set_param.constraints)
        if set_param.guidelines:
            if not param.guidelines:
                param.guidelines = []
            param.guidelines.extend(set_param.guidelines)

    @staticmethod
    def _set_replaced_or_appended_items(param: common.Parameter, set_param: prof.SetParameter) -> None:
        # these replace or append
        if set_param.props:
            new_props = as_list(param.props)
            names = [prop.name for prop in new_props]
            for prop in set_param.props:
                if prop.name in names:
                    new_props[names.index(prop.name)] = prop
                else:
                    new_props.append(prop)
            param.props = new_props
        if set_param.links:
            new_links = as_list(param.links)
            hrefs = [link.href for link in new_links]
            for link in set_param.links:
                if link.href in hrefs:
                    new_links[hrefs.index(link.href)] = link
                else:
                    new_links.append(link)
            param.links = new_links

    def _set_parameter_in_control_or_loose(self, set_param: prof.SetParameter) -> None:
        """
        Find the control with the param_id in it and set the parameter contents.

        It modifies controls in the control_dict not the catalog.
        Parameters are either bound to a control or are 'loose' and bound to the catalog itself.
        """
        # find the target param in control or the catalog's loose ones, i.e. catalog.params
        control = self._catalog_interface.get_control_by_param_id(set_param.param_id)
        loose_param = False
        if control:
            control.params = as_list(control.params)
            param_ids = [param.id for param in control.params]
            if set_param.param_id not in param_ids:
                raise TrestleNotFoundError(f'Param id {set_param.param_id} not found in control {control.id}')
            index = param_ids.index(set_param.param_id)
            param = control.params[index]
        else:
            param = self._catalog_interface.loose_param_dict.get(set_param.param_id, None)
            if param:
                loose_param = True
            else:
                logger.warning(f'SetParameter for param_id {set_param.param_id} not found in catalog')
                return

        # rules here follow https://pages.nist.gov/OSCAL/concepts/processing/profile-resolution/
        # see 'Modify Phase' and Setting Parameters

        Modify._set_overwrite_items(param, set_param)
        Modify._set_appended_items(param, set_param)
        Modify._set_replaced_or_appended_items(param, set_param)

        if loose_param:
            self._catalog_interface.loose_param_dict[set_param.param_id] = param
        else:
            control.params[index] = param
            self._catalog_interface.replace_control(control)

    def _change_prose_with_param_values(self):
        """Go through all controls and change prose based on param values."""
        param_dict: Dict[str, common.Parameter] = {}
        # build the full mapping of params to values from the catalog interface
        for control in self._catalog_interface.get_all_controls_from_dict():
            param_dict.update(ControlIOReader.get_control_param_dict(control, False))
        param_dict.update(self._catalog_interface.loose_param_dict)
        # insert param values into prose of all controls
        for control in self._catalog_interface.get_all_controls_from_dict():
            self._replace_control_prose(control, param_dict, self._params_format, self._param_rep)

    @staticmethod
    def _replace_param_choices(param: common.Parameter, param_dict: Dict[str, common.Parameter]) -> None:
        """Set values for all choices param that refer to params with values."""
        if param.select:
            new_choices: List[str] = []
            for choice in as_list(param.select.choice):
                new_choice = Modify._replace_params(choice, param_dict)
                new_choices.append(new_choice)
            param.select.choice = new_choices

    def _modify_controls(self, catalog: cat.Catalog) -> cat.Catalog:
        """Modify the controls based on the profile."""
        logger.debug(f'modify specify catalog {catalog.metadata.title} for profile {self._profile.metadata.title}')
        self._catalog_interface = CatalogInterface(catalog)
        alters: Optional[List[prof.Alter]] = None
        # find the modify and alters
        if self._profile.modify:
            # change all parameter values
            if self._profile.modify.set_parameters and not self._block_params:
                set_param_list = self._profile.modify.set_parameters
                for set_param in set_param_list:
                    self._set_parameter_in_control_or_loose(set_param)
            alters = self._profile.modify.alters

        if alters is not None:
            title = self._profile.metadata.title
            for alter in alters:
                if alter.control_id is None:
                    logger.warning(f'Alter must have control id specified in profile {title}.')
                    continue
                id_ = alter.control_id
                if alter.removes is not None:
                    logger.warning(f'Alter not supported for removes in profile {title} control {id_}')
                    continue
                # we want a warning about adds even if adds are blocked, as in profile generate
                if alter.adds is None:
                    logger.warning(f'Alter has no adds in profile {title} control {id_}')
                    continue
                if not self._block_adds:
                    for add in alter.adds:
                        if add.position is None and add.parts is not None:
                            msg = f'Alter/Add position is not specified in profile {title} control {id_}'
                            msg += ' when adding part, so defaulting to ending.'
                            logger.warning(msg)
                            add.position = prof.Position.ending
                        control = self._catalog_interface.get_control(id_)
                        if control is None:
                            logger.warning(
                                f'Alter/Add refers to control {id_} but it is not found in the import '
                                + f'for profile {self._profile.metadata.title}'
                            )
                        else:
                            self._add_to_control(control, add)
                            self._catalog_interface.replace_control(control)

        if self._change_prose:
            # go through all controls and fix the prose based on param values
            self._change_prose_with_param_values()

        catalog = self._catalog_interface.get_catalog()

        # update the original profile metadata with new contents
        # roles and responsible-parties will be pulled in with new uuid's
        new_metadata = self._profile.metadata
        new_metadata.title = f'{catalog.metadata.title}: Resolved by profile {self._profile.metadata.title}'
        links: List[common.Link] = []
        for import_ in self._profile.imports:
            links.append(common.Link(**{'href': import_.href, 'rel': 'resolution-source'}))
        new_metadata.links = links

        # move catalog controls from dummy group '' into the catalog
        for group in as_list(catalog.groups):
            if not group.id:
                catalog.controls = group.controls
                catalog.groups.remove(group)
                break

        catalog.metadata = new_metadata

        return catalog

    def process(self, catalog_iter: Iterator[cat.Catalog]) -> Iterator[cat.Catalog]:
        """Make the modifications to the controls based on the profile."""
        catalog = next(catalog_iter)
        logger.debug(
            f'modify process with catalog {catalog.metadata.title} using profile {self._profile.metadata.title}'
        )
        yield self._modify_controls(catalog)
