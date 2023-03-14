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
from typing import Iterator, List, Optional

import trestle.oscal.catalog as cat
import trestle.oscal.profile as prof
from trestle.common.common_types import OBT
from trestle.common.const import RESOLUTION_SOURCE, TRESTLE_INHERITED_PROPS_TRACKER
from trestle.common.err import TrestleNotFoundError
from trestle.common.list_utils import as_list, get_item_from_list, none_if_empty
from trestle.core.catalog.catalog_interface import CatalogInterface
from trestle.core.control_interface import ParameterRep
from trestle.core.pipeline import Pipeline
from trestle.oscal import OSCAL_VERSION, common

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
        param_rep: ParameterRep = ParameterRep.VALUE_OR_LABEL_OR_CHOICES,
        show_value_warnings: bool = False,
        value_assigned_prefix: Optional[str] = None,
        value_not_assigned_prefix: Optional[str] = None
    ) -> None:
        """Initialize the filter."""
        self._profile = profile
        self._catalog_interface: Optional[CatalogInterface] = None
        self._block_adds = block_adds
        self._block_params = block_params
        self._change_prose = change_prose
        self._params_format = params_format
        self._param_rep = param_rep
        self.show_value_warnings = show_value_warnings
        self._value_assigned_prefix = value_assigned_prefix
        self._value_not_assigned_prefix = value_not_assigned_prefix
        logger.debug(f'modify initialize filter with profile {profile.metadata.title}')

    @staticmethod
    def _add_adds_to_part(part: common.Part, add: prof.Add, added_parts=False) -> None:
        for attr in ['params', 'props', 'parts', 'links']:
            # don't add parts if already added earlier
            if added_parts and attr == 'parts':
                continue
            add_list = getattr(add, attr, None)
            if add_list:
                Modify._add_attr_to_part(part, add_list[:], attr, add.position)

    @staticmethod
    def _add_to_list(parts_list: List[common.Part], add: prof.Add) -> bool:
        """Add the contents of the add according to its by_id and position.

        Return True on success or False if id needed and not found.

        This is only called when by_id is not None.
        The add will be inserted if the id is found, or return False if not.
        This allows a separate recursive routine to search sub-lists for the id.
        Position before/after will put the item adjacent to the target in the same list as target
        Position starting/ending will put the item within the target itself
        """
        # Test here for matched by_id attribute.
        added_parts = False
        for index in range(len(parts_list)):
            # find the matching part
            if parts_list[index].id == add.by_id:
                if add.position == prof.Position.after:
                    for offset, new_item in enumerate(as_list(add.parts)):
                        parts_list.insert(index + 1 + offset, new_item)
                    added_parts = True
                elif add.position == prof.Position.before:
                    for offset, new_item in enumerate(as_list(add.parts)):
                        parts_list.insert(index + offset, new_item)
                    added_parts = True
                # if starting or ending or None, the adds go directly into this part according to type
                Modify._add_adds_to_part(parts_list[index], add, added_parts)
                return True
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
    def _add_attr_to_part(part: common.Part, items: List[OBT], attr: str, position: Optional[prof.Position]) -> None:
        attr_list = as_list(getattr(part, attr, None))
        # position may be None and if so will go at end
        if position in [prof.Position.starting, prof.Position.before]:
            items.extend(attr_list)
            attr_list = items
        else:
            attr_list.extend(items)
        setattr(part, attr, attr_list)

    @staticmethod
    def _add_attr_to_control(
        control: cat.Control, items: List[OBT], attr: str, position: Optional[prof.Position]
    ) -> None:
        attr_list = as_list(getattr(control, attr, None))
        # if position is None it will add to end
        if position in [prof.Position.starting, prof.Position.before]:
            items.extend(attr_list)
            attr_list = items
        else:
            attr_list.extend(items)
        setattr(control, attr, attr_list)

    @staticmethod
    def _add_to_trestle_props(control: cat.Control, add: prof.Add) -> None:
        """Add props to special trestle part that keeps track of inherited props."""
        if add.props:
            trestle_part = get_item_from_list(control.parts, TRESTLE_INHERITED_PROPS_TRACKER, lambda p: p.name)
            if trestle_part is None:
                trestle_part = common.Part(
                    id=TRESTLE_INHERITED_PROPS_TRACKER, name=TRESTLE_INHERITED_PROPS_TRACKER, props=[], parts=[]
                )
                control.parts = as_list(control.parts)
                control.parts.append(trestle_part)
                trestle_part = control.parts[-1]
            if add.by_id is None or add.by_id == control.id:
                trestle_part.props.extend(add.props)
            else:
                by_id_part = get_item_from_list(trestle_part.parts, add.by_id, lambda p: p.title)
                if by_id_part is None:
                    trestle_part.parts.append(
                        common.Part(name=TRESTLE_INHERITED_PROPS_TRACKER + '_' + add.by_id, title=add.by_id, props=[])
                    )
                    by_id_part = trestle_part.parts[-1]
                by_id_part.props.extend(add.props)

    @staticmethod
    def _add_to_control(control: cat.Control, add: prof.Add) -> None:
        """First step in applying Add to control."""
        control.parts = as_list(control.parts)
        if add.by_id is None or add.by_id == control.id:
            # add contents will be added to the control directly and with no recursion
            for attr in ['params', 'props', 'parts', 'links']:
                add_list = getattr(add, attr, None)
                if add_list:
                    Modify._add_attr_to_control(control, add_list[:], attr, add.position)
        else:
            # this is only called if by_id is not None
            if not Modify._add_to_parts(control.parts, add):
                logger.warning(f'Could not find id for add in control {control.id}: {add.by_id}')
        Modify._add_to_trestle_props(control, add)
        control.parts = none_if_empty(control.parts)

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

        # an add with no by-id applies to the control
        # if position is starting it should appear immediately after title
        # if position is ending it should appear at end
        # if not specified it defaults to ending
        # if no by-id then before is treated as starting and after is treated as ending
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
            self._catalog_interface._change_prose_with_param_values(
                self._params_format,
                self._param_rep,
                self.show_value_warnings,
                self._value_assigned_prefix,
                self._value_not_assigned_prefix
            )

        catalog = self._catalog_interface.get_catalog()

        # update the original profile metadata with new contents
        # roles and responsible-parties will be pulled in with new uuid's
        # the title simply becomes the title of the current profile - and will get overwritten
        # by any other profiles downstream so that only the final profile title is used
        new_metadata = self._profile.metadata
        new_metadata.title = self._profile.metadata.title
        new_metadata.oscal_version = OSCAL_VERSION

        links: List[common.Link] = []
        for import_ in self._profile.imports:
            links.append(common.Link(**{'href': import_.href, 'rel': RESOLUTION_SOURCE}))
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
