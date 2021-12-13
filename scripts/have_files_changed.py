# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
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
"""Check whether repo is clear of fixes - to be used in combination with scripts in the CI pipeline."""
import logging
import pathlib
import sys
import traceback
from typing import List

from git import Repo

from ilcli import Command

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


class FilesChanged(Command):
    """Check whether files have changed in a repository."""

    def _init_arguments(self):
        self.add_argument('exclude', help='Extensions to exclude.', nargs='*')
        self.add_argument('-v', '--verbose', action='store_true')
        self.add_argument('-C', help='Repository root', type=pathlib.Path, default=pathlib.Path.cwd())
        self.add_argument('-u', '--untracked', help='Error on untracked files.', action='store_true')

    def _run(self, args):
        if args.verbose:
            logger.setLevel(logging.INFO)
        try:
            pretty_exclude = args.exclude if len(args.exclude) > 0 else ''
            if FilesChanged.has_changed(args.C, args.exclude):
                logger.info(f'Files excluding types: {pretty_exclude} have changed.')
                return 1
            if args.untracked:
                if FilesChanged.untracked(args.C):
                    logger.info('Untracked files in the repo.')
                    return 1
            logger.info(f'No files have changed (excluding the following extensions: {pretty_exclude}.')
            return 0
        except Exception as e:
            logger.error(f'Unexpected error {e}')
            logger.debug(traceback.format_exc())
            return 2

    @staticmethod
    def untracked(repo_root: pathlib.Path) -> bool:
        """Determine if there are untracked files in the repo, respecting .gitignore."""
        repo = Repo(repo_root)
        if len(repo.untracked_files) > 0:
            for untracked in repo.untracked_files:
                logger.info(f'Untracked: {untracked}')
            return True
        return False

    @staticmethod
    def has_changed(repo_root: pathlib.Path, excludes: List[str]) -> bool:
        """Determine if files have changed."""
        # Ensure no periods are passed.
        excludes = list(map(lambda x: x.lstrip('.'), excludes))
        repo = Repo(repo_root)
        if repo.bare:
            raise Exception('Cannot operate on a bare git repository.')
        if not repo.is_dirty():
            logger.info('Repository is completely clean.')
            return False
        head_commit = repo.head.commit
        # None is a reference to current working tree.
        for diff in head_commit.diff(None):
            path = pathlib.Path(diff.a_path)
            if not path.suffix.lstrip('.') in excludes:
                logger.info(f'The following path has changed {path}.')
                return True
        return False


if __name__ == '__main__':
    sys.exit(FilesChanged().run())
