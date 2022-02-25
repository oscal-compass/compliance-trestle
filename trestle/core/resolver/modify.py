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
from trestle.common.err import TrestleError
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
        params_format: str = None,
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES
    ) -> None:
        """Initialize the filter."""
        self._profile = profile
        self._catalog_interface: Optional[CatalogInterface] = None
        self._block_adds = block_adds
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
                logger.warning(f'Control prose references param {param_ids[i]} not found in the control.')
            elif param_dict[param_ids[i]] is not None:
                param = param_dict[param_ids[i]]
                param_str = ControlIOReader.param_to_str(param, param_rep, False, False, params_format)
                text = text.replace(staches[i], param_str, 1)
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
        for sub_control in as_list(control.controls):
            prts: List[common.Part] = as_list(sub_control.parts)
            for prt in prts:
                Modify._replace_part_prose(sub_control, prt, param_dict, params_format, param_rep)

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

        If the add is not by_id then the insertion will happen immediately.
        But if the add is by_id it will insert if the id is found, or return False if not.
        This allows a separate recursive routine to search sub-lists for the id.

        Note: If a list can be none this method will fail
        """
        add_list = Modify._add_contents_as_list(add)
        # if by_id is not specified then OSCAL docs say to interpret before and after as starting or ending
        if not add.by_id:
            # if we are just adding to the list then the add contents should be of the same type
            if add.position in [prof.Position.before, prof.Position.starting]:
                for offset, item in enumerate(add_list):
                    input_list.insert(offset, item)
                return True
            else:
                input_list.extend(add_list)
                return True
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
                'Cannot use "after" or "before" modifictions for a list where elements'
                + ' do not contain the referenced by_id attribute.'
            )
        return False

    @staticmethod
    def _add_to_parts(parts: List[common.Part], add: prof.Add) -> bool:
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
        control.parts = as_list(control.parts)
        if add.by_id is None or add.by_id == control.id:
            # add contents will be added to the control directly
            for attr in ['params', 'props', 'parts', 'links']:
                add_list = getattr(add, attr, None)
                if add_list:
                    Modify._add_attr_to_control(control, add_list, attr, add.position)
            return
        else:
            if not Modify._add_to_parts(control.parts, add):
                logger.warning(f'Could not find id for add in control {control.id}: {add.by_id}')

    def _set_parameter_in_control(self, set_param: prof.SetParameter) -> None:
        """
        Find the control with the param_id in it and set the parameter value.

        This does not recurse because expectation is that only top level params will be set.
        """
        control = self._catalog_interface.get_control_by_param_id(set_param.param_id)
        if control is None:
            raise TrestleError(
                f'Set parameter object in profile does not have a corresponding param-id: "{set_param.param_id}"'
            )
        control.params = as_list(control.params)
        param_ids = [param.id for param in control.params]
        index = param_ids.index(set_param.param_id)
        param = control.params[index]
        # FIXME these may need to merge
        if set_param.values:
            param.values = set_param.values
        if set_param.constraints:
            param.constraints = set_param.constraints
        if set_param.guidelines:
            param.guidelines = set_param.guidelines
        if set_param.links:
            param.links = set_param.links
        if set_param.props:
            param.props = set_param.props
        if set_param.select:
            param.select = set_param.select
        if set_param.usage:
            param.usage = set_param.usage
        control.params[index] = param
        self._catalog_interface.replace_control(control)

    def _change_prose_with_param_values(self):
        """Go through all controls and change prose based on param values."""
        param_dict: Dict[str, common.Paramter] = {}
        # build the full mapping of params to values
        for control in self._catalog_interface.get_all_controls_from_dict():
            param_dict.update(ControlIOReader.get_control_param_dict(control, False))
        # insert param values into prose of all controls
        for control in self._catalog_interface.get_all_controls_from_dict():
            self._replace_control_prose(control, param_dict, self._params_format, self._param_rep)

    def _modify_controls(self, catalog: cat.Catalog) -> cat.Catalog:
        """Modify the controls based on the profile."""
        logger.debug(f'modify specify catalog {catalog.metadata.title} for profile {self._profile.metadata.title}')
        self._catalog_interface = CatalogInterface(catalog)
        alters: Optional[List[prof.Alter]] = None
        # find the modify and alters
        if self._profile.modify is not None:
            # change all parameter values
            if self._profile.modify.set_parameters is not None:
                param_list = self._profile.modify.set_parameters
                for param in param_list:
                    self._set_parameter_in_control(param)
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
