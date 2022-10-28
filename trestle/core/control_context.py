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
"""Provide a context for control operations."""
from __future__ import annotations

import copy
import pathlib
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from trestle.common.list_utils import as_dict
from trestle.oscal import component as comp
from trestle.oscal import profile as prof


class ContextPurpose(Enum):
    """Specify the modality of the control markdown."""

    CATALOG = 0
    COMPONENT = 1
    PROFILE = 2
    SSP = 3


@dataclass
class ControlContext:
    """Class encapsulating control markdown usage."""

    purpose: ContextPurpose
    to_markdown: bool
    trestle_root: pathlib.Path
    md_root: pathlib.Path
    prompt_responses: bool
    additional_content: bool
    overwrite_header_values: bool
    set_parameters_flag: bool
    yaml_header: Optional[Dict[Any, Any]] = None
    sections_dict: Optional[Dict[str, str]] = None
    profile: Optional[prof.Profile] = None
    required_sections: Optional[str] = None
    allowed_sections: Optional[str] = None
    comp_def: Optional[comp.ComponentDefinition] = None
    comp_name: Optional[str] = None
    inherited_props: Optional[Dict[str, Any]] = None
    rules_dict: Optional[Dict[str, Dict[str, str]]] = None
    rules_params_dict: Optional[Dict[str, Dict[str, Any]]] = None
    rules_param_vals: Optional[List[Dict[str, str]]] = None
    control_implementation: Optional[comp.ControlImplementation] = None

    @classmethod
    def generate(
        cls,
        purpose: ContextPurpose,
        to_markdown: bool,
        trestle_root: pathlib.Path,
        md_root: pathlib.Path,
        prompt_responses=False,
        additional_content=False,
        overwrite_header_values=False,
        set_parameters_flag=False,
        yaml_header: Optional[Dict[Any, Any]] = None,
        sections_dict: Optional[Dict[str, str]] = None,
        profile: Optional[prof.Profile] = None,
        required_sections: Optional[str] = None,
        allowed_sections: Optional[str] = None,
        comp_def: Optional[comp.ComponentDefinition] = None,
        comp_name: Optional[str] = None,
        inherited_props: Optional[Dict[str, Any]] = None,
        rules_dict: Optional[Dict[str, Dict[str, str]]] = None,
        rules_params_dict: Optional[Dict[str, Dict[str, Any]]] = None,
        rules_param_vals: Optional[List[Dict[str, str]]] = None,
        control_implementation: Optional[comp.ControlImplementation] = None
    ) -> ControlContext:
        """Generate control context of the needed type."""
        context = cls(
            purpose,
            to_markdown,
            trestle_root,
            md_root,
            prompt_responses,
            additional_content,
            overwrite_header_values,
            set_parameters_flag,
            yaml_header=yaml_header,
            sections_dict=sections_dict,
            profile=profile,
            required_sections=required_sections,
            allowed_sections=allowed_sections,
            comp_def=comp_def,
            comp_name=comp_name,
            inherited_props=inherited_props,
            rules_dict=rules_dict,
            rules_params_dict=rules_params_dict,
            rules_param_vals=rules_param_vals,
            control_implementation=control_implementation
        )
        context.yaml_header = as_dict(yaml_header)
        context.sections_dict = as_dict(sections_dict)
        # catalog generate always sets params
        if to_markdown:
            context.set_parameters = True
        return context

    @classmethod
    def clone(cls, context: ControlContext) -> ControlContext:
        """Create a deep clone of the context without duplicating large objects."""
        new_context = cls(
            context.purpose,
            context.to_markdown,
            context.trestle_root,
            context.md_root,
            context.prompt_responses,
            context.additional_content,
            context.overwrite_header_values,
            context.set_parameters_flag,
            yaml_header=copy.deepcopy(context.yaml_header),
            sections_dict=copy.deepcopy(context.sections_dict),
            profile=context.profile,
            required_sections=context.required_sections,
            allowed_sections=context.allowed_sections,
            comp_def=context.comp_def,
            comp_name=context.comp_name,
            inherited_props=copy.deepcopy(context.inherited_props),
            rules_dict=copy.deepcopy(context.rules_dict),
            rules_params_dict=copy.deepcopy(context.rules_params_dict),
            rules_param_vals=context.rules_param_vals,
            control_implementation=copy.deepcopy(context.control_implementation)
        )
        return new_context
