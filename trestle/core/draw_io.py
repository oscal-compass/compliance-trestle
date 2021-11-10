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
"""Functionality for reading information from a drawio file."""
import base64
import logging
import pathlib
import zlib
from typing import Any, Dict, List
from urllib.parse import unquote
from xml.etree.ElementTree import Element  # noqa: S405 - For typing purposes only

import defusedxml.ElementTree

import trestle.core.const as const
from trestle.core.err import TrestleError
from trestle.core.markdown.markdown_validator import MarkdownValidator

logger = logging.getLogger(__name__)


class DrawIO():
    """Access and process drawio data / metadata."""

    def __init__(self, file_path: pathlib.Path) -> None:
        """
        Load drawio object into memory.

        args:
            file_path: Path to the drawio object.
        """
        self.file_path: pathlib.Path = file_path
        self._load()
        self.banned_keys = ['id', 'label']

    def _load(self) -> None:
        """Load the file."""
        if not self.file_path.exists() or self.file_path.is_dir():
            logger.error(f'Candidate drawio file {str(self.file_path)} does not exist or is a directory')
            raise TrestleError(f'Candidate drawio file {str(self.file_path)} does not exist or is a directory')
        try:
            self.raw_xml = defusedxml.ElementTree.parse(self.file_path, forbid_dtd=True)
        except Exception as e:
            logger.error(f'Exception loading Element tree from file: {e}')
            raise TrestleError(f'Exception loading Element tree from file: {e}')
        self.mx_file = self.raw_xml.getroot()
        if not self.mx_file.tag == 'mxfile':
            logger.error('DrawIO file is not a draw io file (mxfile)')
            raise TrestleError('DrawIO file is not a draw io file (mxfile)')
        self.diagrams = []
        for diagram in list(self.mx_file):
            # Determine if compressed or not
            # Assumption 1 mxGraphModel
            n_children = len(list(diagram))
            if n_children == 0:
                # Compressed object
                self.diagrams.append(self._uncompress(diagram.text))
            elif n_children == 1:
                self.diagrams.append(list(diagram)[0])
            else:
                raise TrestleError('Unhandled behaviour in drawio read.')

    def _uncompress(self, compressed_text: str) -> Element:
        """
        Given a compressed object from a drawio file return an xml element for the mxGraphModel.

        Args:
            compressed_text: A compressed mxGraphModel from inside an mxfile

        Returns:
            An element containing the mxGraphModel
        """
        # Assume b64 encode
        decoded = base64.b64decode(compressed_text)
        clean_text = unquote(zlib.decompress(decoded, -15).decode(const.FILE_ENCODING))
        element = defusedxml.ElementTree.fromstring(clean_text, forbid_dtd=True)
        if not element.tag == 'mxGraphModel':
            raise TrestleError('Unknown data structure within a compressed drawio file.')
        return element

    def get_metadata(self) -> List[Dict[str, str]]:
        """Get metadata from each tab if it exists or provide an empty dict."""
        # Note that id and label are special for drawio.
        md_list: List[Dict[str, str]] = []
        for diagram in self.diagrams:
            md_dict: Dict[str, str] = {}
            # Drawio creates data within a root and then an object element type
            children = list(diagram)
            root_obj = children[0]
            md_objects = root_obj.findall('object')
            # Should always be true - to test presumptions.
            if len(md_objects) == 0:
                md_list.append(md_dict)
                continue
            items = md_objects[0].items()
            for item in items:
                key = item[0]
                val = item[1]
                if key in self.banned_keys:
                    continue
                md_dict[key] = val
            md_list.append(md_dict)
        return md_list

    @classmethod
    def restructure_metadata(cls, input_dict: Dict[str, str]) -> Dict[str, Any]:
        """Restructure metadata into a hierarchial dict assuming a period separator."""
        # get the list of duplicate keys
        # Get a count of keys
        result = {}
        key_map = {}
        for keys in input_dict.keys():
            stub = keys.split('.')[0]
            tmp = key_map.get(stub, [])
            tmp.append(keys)
            key_map[stub] = tmp

        for key, values in key_map.items():
            holding = {}
            if len(values) == 1 and key == values[0]:
                result[key] = input_dict[key]
            else:
                for value in values:
                    holding[value.split('.', 1)[-1]] = input_dict[value]
                result[key] = cls.restructure_metadata(holding)
        return result

    def write_drawio_with_metadata(
        self, path: pathlib.Path, metadata: Dict, diagram_metadata_idx: int, target_path: pathlib.Path = None
    ) -> None:
        """
        Write modified metadata to drawio file.

        Writes given metadata to 'object' element attributes inside of the selected drawio diagram element.
        Currently supports writing only uncompressed elements.

        Args:
            path: path to write modified drawio file to
            metadata: dictionary of modified metadata to insert to drawio
            diagram_metadata_idx: index of diagram which metadata was modified
            target_path: if not provided the changes will be written to path
        """
        flattened_dict = self._flatten_dictionary(metadata)
        if diagram_metadata_idx >= len(list(self.diagrams)):
            raise TrestleError(f'Drawio file {path} does not contain a diagram for index {diagram_metadata_idx}')

        diagram = list(self.diagrams)[diagram_metadata_idx]
        children = list(diagram)
        root_obj = children[0]
        md_objects = root_obj.findall('object')
        if len(md_objects) == 0:
            raise TrestleError(f'Unable to write metadata, diagram in drawio file {path} does not have objects.')

        for key in md_objects[0].attrib.copy():
            if key not in flattened_dict.keys() and key not in self.banned_keys:
                # outdated key delete
                del md_objects[0].attrib[key]
                continue
            if key in self.banned_keys:
                continue
            md_objects[0].attrib[key] = flattened_dict[key]
        for key in flattened_dict.keys():
            if key in self.banned_keys:
                continue
            md_objects[0].attrib[key] = flattened_dict[key]
        parent_diagram = self.mx_file.findall('diagram')[diagram_metadata_idx]
        if len(parent_diagram.findall('mxGraphModel')) == 0:
            parent_diagram.insert(0, diagram)

        if target_path:
            self.raw_xml.write(target_path)
        else:
            self.raw_xml.write(path)

    def _flatten_dictionary(self, metadata: Dict, parent_key='', separator='.') -> Dict[str, str]:
        """Flatten hierarchial dict back to xml attributes."""
        items = []
        for key, value in metadata.items():
            new_key = parent_key + separator + key if parent_key else key
            if isinstance(value, Dict):
                items.extend(self._flatten_dictionary(value, new_key, separator).items())
            else:
                items.append((new_key, value))
        return dict(items)


class DrawIOMetadataValidator():
    """Validator to check whether drawio metadata meets validation expectations."""

    def __init__(self, template_path: pathlib.Path, must_be_first_tab: bool = True) -> None:
        """
        Initialize drawio validator.

        Args:
            template_path: Path to a templated drawio file where metadata will be looked up on the first tab only.
            must_be_first_tab: Whether to search the candidate file for a metadata across multiple tabs.
        """
        self.template_path = template_path
        self.must_be_first_tab = must_be_first_tab
        # Load metadat from template
        template_drawio = DrawIO(self.template_path)
        # Zero index as must be first tab
        self.template_metadata = template_drawio.get_metadata()[0]
        self.template_version = MarkdownValidator.extract_template_version(self.template_metadata)
        if self.template_version not in str(self.template_path):
            raise TrestleError(
                f'Version of the template {self.template_version} does not match the path {self.template_path}.'
                + f'Move the template to the folder {self.template_version}'
            )
        if 'Version' in self.template_metadata.keys() and self.template_metadata['Version'] != self.template_version:
            raise TrestleError(f'Version does not match template-version in template: {self.template_path}.')

    def validate(self, candidate: pathlib.Path) -> bool:
        """
        Run drawio validation against a candidate file.

        Args:
            candidate: The path to a candidate markdown file to be validated.

        Returns:
            Whether or not the validation passes.

        Raises:
            err.TrestleError: If a file IO / formatting error occurs.
        """
        logging.info(f'Validating drawio file {candidate} against template file {self.template_path}')
        candidate_drawio = DrawIO(candidate)
        drawio_metadata = candidate_drawio.get_metadata()

        if self.must_be_first_tab:
            return MarkdownValidator.compare_keys(self.template_metadata, drawio_metadata[0])
        for md_tab in drawio_metadata:
            status = MarkdownValidator.compare_keys(self.template_metadata, md_tab)
            if status:
                return status
        return False
