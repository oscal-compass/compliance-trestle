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
"""Define the TransformerFactory and corresponding ResultsTransformer class it creates."""

from abc import ABC, abstractmethod
from typing import Dict, Type

from trestle.core.base_model import OscalBaseModel
from trestle.core.err import TrestleError
from trestle.transforms.results import Results


class TransformerBase(ABC):
    """Abstract base interface for all transformers."""

    @abstractmethod
    def transform(self, blob: str) -> OscalBaseModel:
        """Transform the blob into a general OscalBaseModel."""


class ResultsTransformer(TransformerBase):
    """Abstract interface for transformers that specifically return Results."""

    @abstractmethod
    def transform(self, blob: str) -> Results:
        """Transform the blob into Results."""


class TransformerFactory:
    """Perform registration and creation of transformers."""

    def __init__(self) -> None:
        """Initialize the transformers dictionary as empty."""
        self._transformers: Dict[str, Type[TransformerBase]] = {}

    def register_transformer(self, name: str, transformer: Type[TransformerBase]) -> None:
        """
        Register the transformer.

        This registers transformers in the factory so they may be created by name.

        Args:
            name (str): The name of the transformer.
            transformer (TransformerBase): The transformer class to be registered.

        Returns:
            None
        """
        self._transformers[name] = transformer

    def get(self, name: str) -> TransformerBase:
        """
        Create an instance of the desired transformer based its name.

        Args:
            name (str): The name of the transformer.

        Returns:
            An instance of the desired transformer.

        Raises:
            TrestleError: if the name does not exist in the registry.
        """
        t = self._transformers.get(name)
        if t is not None:
            return t()
        raise TrestleError(f'Error getting non-registered transform {name}')
