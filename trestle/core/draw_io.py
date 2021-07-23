# -*- mode:python; coding:utf-8 -*-

# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Functionality for reading information from a drawio file."""
import base64
import logging
import pathlib
import zlib
from typing import Dict, List
from urllib.parse import unquote
from xml.etree.ElementTree import Element  # noqa: S405 - For typing purposes only

import defusedxml.ElementTree

import trestle.core.err as err
import trestle.core.markdown_validator as markdown_validator

logger = logging.getLogger(__name__)


class DrawIO(object):
    """Access and process drawio data / metadata."""

    def __init__(self, file_path: pathlib.Path) -> None:
        """
        Load drawio object into memory.

        args:
            file_path: Path to the drawio object.
        """
        self.file_path: pathlib.Path = file_path
        self._load()

    def _load(self) -> None:
        """Load the file."""
        if not self.file_path.exists() or self.file_path.is_dir():
            logger.error(f'Candidate drawio file {str(self.file_path)} does not exist or is a directory')
            raise err.TrestleError(f'Candidate drawio file {str(self.file_path)} does not exist or is a directory')
        try:
            raw_xml = defusedxml.ElementTree.parse(self.file_path, forbid_dtd=True)
        except Exception as e:
            logger.error(f'Exception loading Element tree from file: {e}')
            raise err.TrestleError(f'Exception loading Element tree from file: {e}')
        mx_file = raw_xml.getroot()
        if not mx_file.tag == 'mxfile':
            logger.error('DrawIO file is not a draw io file (mxfile)')
            raise err.TrestleError('DrawIO file is not a draw io file (mxfile)')
        self.diagrams = []
        for diagram in list(mx_file):
            # Determine if compressed or not
            # Assumption 1 mxGraphModel
            n_children = len(list(diagram))
            if n_children == 0:
                # Compressed object
                self.diagrams.append(self._uncompress(diagram.text))
            elif n_children == 1:
                self.diagrams.append(list(diagram)[0])
            else:
                raise err.TrestleError('Unhandled behaviour in drawio read.')

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
        clean_text = unquote(zlib.decompress(decoded, -15).decode('utf8'))
        element = defusedxml.ElementTree.fromstring(clean_text, forbid_dtd=True)
        if not element.tag == 'mxGraphModel':
            raise err.TrestleError('Unknown data structure within a compressed drawio file.')
        return element

    def get_metadata(self) -> List[Dict[str, str]]:
        """Get metadata from each tab if it exists or provide an empty dict."""
        # Note that id and label are special for drawio.
        banned_keys = ['id', 'label']
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
                if key in banned_keys:
                    continue
                md_dict[key] = val
            md_list.append(md_dict)
        return md_list


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
            return markdown_validator.MarkdownValidator.compare_keys(self.template_metadata, drawio_metadata[0])
        else:
            for md_tab in drawio_metadata:
                status = markdown_validator.MarkdownValidator.compare_keys(self.template_metadata, md_tab)
                if status:
                    return status
        return False
