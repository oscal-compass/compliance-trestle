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
"""
Trestle MD command.

Umbrella command for all markdown related transformations
"""
import argparse
import logging
import pathlib
import shutil
from typing import Any, Dict, List, Optional, Tuple

import frontmatter

import mistune

import trestle.core.const as const
from trestle.core import err
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.utils import fs
from trestle.utils import log

logger = logging.getLogger(__name__)


def partition_ast(content: List[Dict[str, Any]], ref_level=0) -> Tuple[List[Dict[str, Any]], int]:
    """
    Partition AST, recursive function to create a hierarchial tree out of a stream of markdown elements.

    Markdown elements are typically treated as a flat stream of tokens - which is sufficient for most needs.
    For this project and understanding of heading hierarchy.


    Args:
        List of AST parsing elements as from mistune
    Returns:
        List containing a tree of elements.

    """
    new_content = []
    ii = 0
    while ii < len(content):
        if content[ii]['type'] == 'heading':
            if content[ii]['level'] <= ref_level:
                break
            if ii + 1 == len(content):
                new_content.append(content[ii])
                ii = ii + 1
                break
            else:
                sub_content, jj = partition_ast(content[ii + 1:], content[ii]['level'])
                fixed_header = content[ii]
                fixed_header['children'].extend(sub_content)
                new_content.append(fixed_header)
                ii = ii + jj + 1
        else:
            new_content.append(content[ii])
            ii = ii + 1
    return new_content, ii


def compare_tree(template: Dict[str, Any], content: Dict[str, Any]) -> bool:
    """
    Compare whether a content parse tree is a superset of the template tree.

    The fundamental assumption here is anchored on the nesting of markdown headings.

    Assumptions:
    - Users of a template cannot create headers at the same level as a template only below that level.
    - Template levels cannot be changed.
    - Headers are the only element measured in the template.
    """
    # TODO: Add logging statements to this context.
    if not (template['type'] == 'heading'):
        # It's okay as we should not be here:
        return True
    template_heading_level = template['level']
    template_header_name = template['children'][0]['text'].strip()
    content_heading_level = content['level']
    content_header_name = content['children'][0]['text'].strip()
    if not template_heading_level == content_heading_level:
        return False
    # ESCAPE title if required
    if not (template_header_name[0] == const.HEADER_L_ESCAPE and template_header_name[-1] == const.HEADER_R_ESCAPE):
        if not template_header_name == content_header_name:
            return False
    template_sub_headers = []
    content_sub_headers = []
    for ii in range(len(template['children'])):
        if template['children'][ii]['type'] == 'heading':
            template_sub_headers.append(template['children'][ii])
    # IF there is no template headers we are good
    if len(template_sub_headers) == 0:
        return True

    for ii in range(len(content['children'])):
        if content['children'][ii]['type'] == 'heading':
            content_sub_headers.append(content['children'][ii])
    if not len(template_sub_headers) == len(content_sub_headers):
        return False
    for ii in range(len(template_sub_headers)):
        status = compare_tree(template_sub_headers[ii], content_sub_headers[ii])
        if not status:
            return False
    return True


def allowed_task_name(name: str, trestle_root: pathlib.Path) -> bool:
    """Determine whether a task / directory name is prohibited from use."""
    # Task must not use an OSCAL directory
    # Task must not self-interfere with a project
    pathed_name = pathlib.Path(name)

    root_path = pathed_name.parts[0]
    if root_path in const.MODEL_TYPE_TO_MODEL_DIR.values():
        logger.error('Task name is the same as an OSCAL schema name.')
        return False
    elif root_path == '.trestle':
        logger.error('Task name must not use the `.trestle` name.')
        return False
    elif pathed_name.suffix != '':
        # Does it look like a file
        logger.error('tasks name must not look like a file path (e.g. contain a suffix')
        return False
    return True


class MarkdownValidator:
    """Markdown validator to meet conformance expectations."""

    def __init__(
        self,
        template_path: pathlib.Path,
        yaml_header_validate: bool,
        strict_heading_validate: Optional[str] = None
    ) -> None:
        """
        Initialize markdown validator.

        Args:
            template_path: path to markdown template.
            header_validate: whether to validate a yaml header or not.
        """
        self._yaml_header_validate = yaml_header_validate
        self.template_path = template_path
        if not self.template_path.is_file():
            logger.error(f'Provided template {self.template_path.absolute()} is not a file')
            raise err.TrestleError(f'Unable to find markdown template {self.template_path.absolute()}')
        template_header, template_parse = self._load_markdown_parsetree(self.template_path)
        self._template_header = template_header
        self._template_parse = template_parse
        self._strict_heading_validate = strict_heading_validate

    def _load_markdown_parsetree(self, path: pathlib.Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Load markdown file including yaml frontmatter.

        Args:
            path: File system path of the markdown.

        Returns:
            Yaml header which has been parsed, if it exists.

        """
        content = path.open('r').read()
        fm = frontmatter.loads(content)
        header_dict = fm.metadata
        md_no_header = fm.content
        mistune_ast_parser = mistune.create_markdown(renderer=mistune.AstRenderer())
        mistune_parse = mistune_ast_parser(md_no_header)
        return header_dict, mistune_parse

    def wrap_content(self, original: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Wrap an array of list into a pseudo-top level element to make it easier to handle.

        Warning: Not designed for rendering as it will produce extra text
        args:
            original: List of AST parse elements, likely normalized into a tree
        Returns:
            One pseudo element to make it easier to parse with a consistent name.
        """
        structure = {'type': 'heading', 'level': 0, 'children': [{'type': 'text', 'text': 'wrapping header'}]}
        structure['children'].extend(original)
        return structure

    def validate(self, candidate: pathlib.Path) -> bool:
        """Run the validation against a candidate file."""
        header_content, mistune_parse_content = self._load_markdown_parsetree(candidate)
        if self._yaml_header_validate:
            header_status = self.compare_keys(self._template_header, header_content)
            if not header_status:
                logger.warning(f'YAML header mismatch between template {self.template_path} and instance {candidate}')
                return False
        template_tree, _ = partition_ast(self._template_parse)
        w_template_tree = self.wrap_content(template_tree)
        candidate_tree, _ = partition_ast(mistune_parse_content)
        w_candidate_tree = self.wrap_content(candidate_tree)

        if self._strict_heading_validate is not None:
            status = self._template_heading_validate(w_template_tree, w_candidate_tree, self._strict_heading_validate)
            if not status:
                logger.error(f'Heading {self._strict_heading_validate} did not meet templating requirements.')
                return False
        return compare_tree(w_template_tree, w_candidate_tree)

    def compare_keys(self, template, dict_) -> bool:
        """Check whether two, formerly yaml objects, can have a template, user of template, formalization."""
        for key in template.keys():
            if key in dict_.keys():
                if type(template[key]) == dict:
                    status = self.compare_keys(template[key], dict_[key])
                    if not status:
                        return status
            else:
                return False
        return True

    def search_for_heading(self, candidate_tree: Dict[str, Any], heading: str) -> Dict[str, Any]:
        """Recursively search for a heading within a document and return the children."""
        answer = {}
        for candidate in candidate_tree['children']:
            if candidate['type'] == 'heading':
                if candidate['children'][0]['text'].strip() == heading.strip():
                    answer = candidate
                    break
                else:
                    answer = self.search_for_heading(candidate, heading)
        return answer

    def clean_content(self, parse_tree: Dict[str, Any]) -> List[str]:
        """
        Clean a set of content for measurement of header cleanliness.

        Args:
            parse_tree: AST parse normalized into a hierarchial tree.
        Returns:
            List of strings for each line of paragraph content.
        Raises:
            TrestleError when unhandled object types are present.
        Assumptions:
            - Multiple paragraphs
            - no sub-headings
            - tables unhandled

        """
        items = parse_tree['children']
        clean_text_lines: List[str] = []

        for index in range(len(items)):
            # first item is the header title text which we will ignore.
            if index == 0:
                continue
            item = items[index]
            if item['type'] == 'block_html':
                # ignore all block HTML
                continue
            elif item['type'] == 'paragraph':
                line_content = ''
                for child in item['children']:
                    if child['type'] == 'linebreak':
                        clean_text_lines.append(line_content)
                        line_content = ''
                    elif 'html' in child['type']:
                        # ignore HTML comment presuming a commment
                        continue
                    elif 'strong' in child['type']:
                        line_content = line_content + child['children'][0]['text']
                    elif 'text' in child['type']:
                        line_content = line_content + child['text']
                    else:
                        msg = f'Unexpected element type {item["type"]} when flattening a governed header.'
                        logger.error(msg)
                        raise err.TrestleError(msg)
                # handle EoParagraph condition
                clean_text_lines.append(line_content)
            else:
                msg = f'Unexpected element type {item["type"]} when flattening a governed header.'
                logger.error(msg)
                raise err.TrestleError(msg)
        return clean_text_lines

    def _template_heading_validate(self, wrapped_template, wrapped_candidate, title_tag) -> bool:
        """
        Validate a markdown document containing a structured header based on a title tag.

        This is an experimental capability which is relatively constrained.

        Assumptions:
            Header is determined the name of a heading block.
            Within the header no table exists (e.g. plain paragraphs)
            Header is valid if the header, excluding inline html comments, is characters 0-M of N in the content.
            Comparison removes formatting.
            All inline HTML is presumed to be comments (for now).
            Header is at the top level (e.g. heading level 1).
        """
        # Find the correct header
        template_heading = self.search_for_heading(wrapped_template, title_tag)
        if template_heading == {}:
            logger.error('Governed header tag provided but not found in the template - failing validation')
            return False
        candidate_heading = self.search_for_heading(wrapped_template, title_tag)
        if candidate_heading == {}:
            logger.error('Governed header tag provided but not found in the content - failing validation')
            return False
        template_lines = self.clean_content(template_heading)
        content_lines = self.clean_content(candidate_heading)
        if not len(template_lines) == len(content_lines):
            logger.error(
                'Governed heading has inconsistent number of content lines between the template and measured file.'
            )
            return False
        # Strict parsing
        for index in range(len(template_lines)):
            if not content_lines[index][0:len(template_lines[index])] == template_lines[index]:
                logger.warning('Mismatch in governed heading')
                logger.warning(f'Between template {template_lines[index]} and instance {content_lines[index]}')
                return False
        # Okay
        return True


class CIDD(CommandPlusDocs):
    """
    Control Information Description Document management.

    Control descriptions are a critical reviewable component of the compliance lifecycle - and are typically managed by
    *ISO teams. This command supports a set of actions for writing control descriptions as markdown and assembling into
    an SSP-like construct.

    Insert notes w.r.t. spreadsheet templates format (control family, control-id, information , current description?)
    """

    name = 'cidd'

    def _init_arguments(self) -> None:
        self.add_argument('--pave', action='store_true', help='Create tree of control templates')
        self.add_argument('--cidd', default=None, help='Create Control Implementation Description Document')
        self.add_argument('--parse', action='store_true', help='Parse templates')
        # Add as appropriate
        # catalog(s) should be addressed by name assuming the 800-53 content is in the trestle directory tree.
        # May need to simplify the model for spreadsheets.

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        try:
            logger.info(f'Are we paving? {args.pave}')

            logger.debug('Done')
            return 0
        except Exception as e:
            logger.error(f'Something failed in CIDD {e}')
            return 1


class GovernedDocs(CommandPlusDocs):
    """Markdown governed documents - enforcing consistent markdown across a set of files."""

    name = 'governed-docs'

    template_name = 'template.md'

    def _init_arguments(self) -> None:
        help_str = """
        The name of the the task to be governed.

        The template file is at .trestle/md/[task-name]/template.md
        Note that by default this will automatically enforce the task.
        """
        self.add_argument('-tn', '--task-name', help=help_str, required=True, type=str)
        heading_help = """
        Governed heading: Heading where for each line the content is a superset of the template's content."""
        self.add_argument('-gn', '--governed-heading', help=heading_help, default=None, type=str)
        self.add_argument('mode', choices=['validate', 'template-validate', 'setup', 'create-sample'])

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        trestle_root = fs.get_trestle_project_root(pathlib.Path.cwd())
        if not trestle_root:
            logger.error(f'Current working directory {pathlib.Path.cwd()} is not with a trestle project.')
            return 1
        if not allowed_task_name(args.task_name, trestle_root):
            logger.error(
                f'Task name {args.task_name} is invalid as it interferes with OSCAL and trestle reserved names.'
            )
            return 1
        status: int = None
        if args.mode == 'create-sample':
            status = self.create_sample(args.task_name, trestle_root)

        elif args.mode == 'template-validate':
            status = self.template_validate(args.task_name, trestle_root, args.governed_heading)
        elif args.mode == 'setup':
            status = self.setup_template_governed_docs(args.task_name, trestle_root)
        else:
            # mode is validate
            status = self.validate(args.task_name, trestle_root, args.governed_heading)

        return status

    def setup_template_governed_docs(self, task_name: str, trestle_root: pathlib.Path) -> int:
        """Create structure to allow markdown template enforcement."""
        task_path = trestle_root / task_name
        task_path.mkdir(exist_ok=True, parents=True)

        template_dir = trestle_root / const.TRESTLE_CONFIG_DIR / 'md' / task_name
        template_dir.mkdir(exist_ok=True, parents=True)
        logger.debug(template_dir)
        if not self._validate_template_dir(template_dir):
            logger.error('Aborting setup')
            return 1
        template_file = template_dir / self.template_name
        if template_file.is_file():
            return 0
        fh = template_file.open('w')
        fh.write("""# Template header\nThis file is a pro-forma template.\n""")
        logger.warning(f'Template file setup for task {task_name} at {template_file}')
        logger.warning(f'Task directory is {task_path} ')
        return 0

    def create_sample(self, task_name: str, trestle_root: pathlib.Path) -> int:
        """Presuming the template exists, copy into a sample markdown file with an index."""
        template_dir = trestle_root / const.TRESTLE_CONFIG_DIR / 'md' / task_name
        template_file = template_dir / self.template_name

        if not self._validate_template_dir(template_dir):
            logger.error('Aborting setup')
            return 1
        if not template_file.is_file():
            logger.error('No template file ... exiting.')
            return 1

        index = 0
        while True:
            candidate_task = trestle_root / task_name / f'{task_name}_{index:03d}.md'
            if candidate_task.is_file():
                index = index + 1
            else:
                shutil.copy(str(template_file), str(candidate_task))
                break
        return 0

    def template_validate(self, task_name: str, trestle_root: pathlib.Path, heading: str) -> int:
        """Validate that the template is acceptable markdown."""
        template_dir = trestle_root / const.TRESTLE_CONFIG_DIR / 'md' / task_name
        template_file = template_dir / self.template_name
        if not self._validate_template_dir(template_dir):
            logger.error('Aborting setup')
            return 1
        if not template_file.is_file():
            logger.error(f'Required template file: {template_file} does not exist. Exiting.')
            return 1
        try:
            _ = MarkdownValidator(template_file, False, heading)
        except Exception as ex:
            logger.error(f'Template for task {task_name} failed to validate due to {ex}')
            return 1
        return 0

    def _validate_template_dir(self, template_dir=pathlib.Path) -> bool:
        """Template directory should only have template file."""
        for child in template_dir.iterdir():
            # Only allowable template file in the directory is the template file.
            if child.name != self.template_name:
                logger.error(f'Unknown file: {child.name} in template directory {template_dir}')
                return False
        return True

    def validate(self, task_name: str, trestle_root: pathlib.Path, governed_heading: str) -> int:
        """Validate task."""
        task_path = trestle_root / task_name
        if not task_path.is_dir():
            logger.error(f'Task directory {task_path} does not exist. Exiting validate.')
        template_dir = trestle_root / const.TRESTLE_CONFIG_DIR / 'md' / task_name
        template_file = template_dir / self.template_name
        md_validator = MarkdownValidator(template_file, False, governed_heading)
        if not template_file.is_file():
            logger.error(f'Required template file: {template_file} does not exist. Exiting.')
            return 1
        for potential_md_file in task_path.iterdir():
            if not potential_md_file.suffix == '.md':
                logger.warning(f'Unexpected file {potential_md_file} in task {task_name}, exiting.')
            status = md_validator.validate(potential_md_file)
            if not status:
                logger.info(f'Markdown file {potential_md_file} fails to meet template for task {task_name}.')
                return 1
            else:
                logger.info(f'Markdown file {potential_md_file} is valid for task {task_name}.')
        return 0


class GovernedFolders(CommandPlusDocs):
    """Markdown governed folders - enforcing consistent files and templates across directories."""

    name = 'governed-folders'

    def _init_arguments(self) -> None:
        pass

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        logger.error('NOT YET IMPLEMENTED')
        return 1


class GovernedProjects(CommandPlusDocs):
    """Markdown governed projects - enforcing requirements at the project level."""

    def _init_arguments(self) -> None:
        pass

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        logger.error('NOT YET IMPLEMENTED')
        return 1


class MDCmd(CommandPlusDocs):
    """trestle md, a collection of commands for managing markdown objects related to compliance."""

    name = 'md'

    subcommands = [CIDD, GovernedDocs, GovernedFolders, GovernedProjects]

    def _init_arguments(self) -> None:
        pass
