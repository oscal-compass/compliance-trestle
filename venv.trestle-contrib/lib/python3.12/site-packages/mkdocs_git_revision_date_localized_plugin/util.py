"""Utility class for mkdocs plugin."""

import logging
import os
import time
from pathlib import Path

from git import (
    Git,
    GitCommandError,
    GitCommandNotFound,
    InvalidGitRepositoryError,
    NoSuchPathError,
    Repo,
)

from mkdocs_git_revision_date_localized_plugin.ci import raise_ci_warnings
from mkdocs_git_revision_date_localized_plugin.dates import get_date_formats

logger = logging.getLogger("mkdocs.plugins")


class Util:
    """Utility class.

    This helps find git and calculate relevant dates.
    """

    def __init__(self, config: dict, mkdocs_dir: str):
        """Initialize utility class."""
        self.config = config
        self.repo_cache = {}

        ignore_commits_file = self.config.get("ignored_commits_file")
        if ignore_commits_file:
            ignore_commits_filepath = Path(mkdocs_dir) / ignore_commits_file
            self.ignored_commits = self.parse_git_ignore_revs(ignore_commits_filepath)
        else:
            self.ignored_commits: list[str] = []

    def _get_repo(self, path: str) -> Git:
        if not os.path.isdir(path):
            path = os.path.dirname(path)

        if path not in self.repo_cache:
            self.repo_cache[path] = Repo(path, search_parent_directories=True).git
            # Checks if user is running builds on CI
            # and raise appropriate warnings
            raise_ci_warnings(self.repo_cache[path])

        return self.repo_cache[path]

    def get_git_commit_timestamp(self, path: str, is_first_commit: bool = False) -> tuple[str, int]:
        """
        Get a list of commit dates in unix timestamp, starts with the most recent commit.

        Args:
            is_first_commit (bool): if true, get the timestamp of the first commit,
                                    else, get that of the most recent commit.
            path (str): Location of a markdown file that is part of a Git repository.
            is_first_commit (bool): retrieve commit timestamp when file was created.

        Returns:
            tuple[str, int]: commit hash and commit date in unix timestamp.
        """
        commit_timestamp = ""
        commit_hash = ""
        n_ignored_commits = 0

        # Determine the logging level
        # Only log warnings when plugin is set to strict.
        # That way, users turn those into errors using mkdocs build --strict
        if self.config.get("strict"):
            log = logger.warning
        else:
            log = logger.info

        # perform git log operation
        try:
            # Retrieve author date in UNIX format (%at)
            # https://git-scm.com/docs/git-log#Documentation/git-log.txt-ematem
            # https://git-scm.com/docs/git-log#Documentation/git-log.txt---diff-filterACDMRTUXB82308203
            realpath = os.path.realpath(path)
            git = self._get_repo(realpath)

            follow_option = self.config.get("enable_git_follow")

            # Ignored commits are only considered for the most recent update, not for creation
            if is_first_commit:
                # diff_filter="A" will select the commit that created the file
                commit_timestamp = git.log(
                    realpath, date="unix", format="%at", diff_filter="Ar", no_show_signature=True, follow=follow_option
                )
                # A file can be created multiple times, through a file renamed.
                # Commits are ordered with most recent commit first
                # Get the oldest commit only
                if commit_timestamp != "":
                    commit_timestamp = commit_timestamp.split()[-1]
            else:
                # Retrieve the history for the file in the format <hash> <timestamp>
                # The maximum number of commits we will ever need to examine is 1 more than the number of ignored commits.
                lines = git.log(
                    realpath,
                    date="unix",
                    format="%H %at",
                    diff_filter="r",
                    n=len(self.ignored_commits) + 1,
                    no_show_signature=True,
                    follow=follow_option,
                    ignore_all_space=True,
                    ignore_blank_lines=True,
                ).split("\n")

                # process the commits for the file in reverse-chronological order. Ignore any commit that is on the
                # ignored list. If the line is empty, we've reached the end and need to use the fallback behavior.
                for line in lines:
                    if not line:
                        commit_timestamp = ""
                        break
                    commit_hash, commit_timestamp = line.split(" ")
                    if not any(commit_hash.startswith(x) for x in self.ignored_commits):
                        break
                    else:
                        n_ignored_commits += 1

        except (InvalidGitRepositoryError, NoSuchPathError) as err:
            if self.config.get("fallback_to_build_date"):
                log(
                    "[git-revision-date-localized-plugin] Unable to find a git directory and/or git is not installed."
                    " Option 'fallback_to_build_date' set to 'true': Falling back to build date"
                )
                commit_timestamp = time.time()
            else:
                log(
                    "[git-revision-date-localized-plugin] Unable to find a git directory and/or git is not installed."
                    " To ignore this error, set option 'fallback_to_build_date: true'"
                )
                raise err
        except GitCommandError as err:
            if self.config.get("fallback_to_build_date"):
                log(
                    f"[git-revision-date-localized-plugin] Unable to read git logs of '{path}'. Is git log readable?"
                    " Option 'fallback_to_build_date' set to 'true': Falling back to build date"
                )
                commit_timestamp = time.time()
            else:
                logger.error(
                    f"[git-revision-date-localized-plugin] Unable to read git logs of '{path}'. "
                    " To ignore this error, set option 'fallback_to_build_date: true'"
                )
                raise err
        except GitCommandNotFound as err:
            if "detected dubious ownership" in str(err):
                raise err
            if self.config.get("fallback_to_build_date"):
                log(
                    "[git-revision-date-localized-plugin] Unable to perform command: 'git log'. Is git installed?"
                    " Option 'fallback_to_build_date' set to 'true': Falling back to build date"
                )
                commit_timestamp = time.time()
            else:
                log(
                    "[git-revision-date-localized-plugin] Unable to perform command 'git log'. Is git installed?"
                    " To ignore this error, set option 'fallback_to_build_date: true'"
                )
                raise err
        except Exception as err:
            if self.config.get("fallback_to_build_date"):
                log(
                    f"[git-revision-date-localized-plugin] An unexpected error occurred: {str(err)}"
                    " Option 'fallback_to_build_date' set to 'true': Falling back to build date"
                )
                commit_timestamp = time.time()
            else:
                logger.error(
                    f"[git-revision-date-localized-plugin] An unexpected error occurred: {str(err)}"
                    " To ignore this error, set option 'fallback_to_build_date: true'"
                )
                raise err

        # create timestamp
        if commit_timestamp == "":
            commit_timestamp = time.time()
            msg = f"[git-revision-date-localized-plugin] '{path}' has no git logs, using current timestamp"
            if n_ignored_commits:
                msg += f" (ignored {n_ignored_commits} commits)"
            log(msg)

        return commit_hash, int(commit_timestamp)

    def get_date_formats_for_timestamp(
        self,
        commit_timestamp: int,
        locale: str,
        add_spans: bool = True,
    ) -> dict[str, str]:
        """
        Determine localized date variants for a given timestamp.

        Args:
            commit_timestamp (int): most recent commit date in unix timestamp.
            locale (str, optional): Locale code of language to use. Defaults to 'en'.
            add_spans: Wraps output in <span> elements with unique classes for easy CSS formatting

        Returns:
            dict: Localized date variants.
        """
        date_formats = get_date_formats(
            unix_timestamp=commit_timestamp,
            time_zone=self.config.get("timezone") or "UTC",
            locale=locale,
            custom_format=self.config.get("custom_format") or "%d. %B %Y",
        )
        if add_spans:
            date_formats = self.add_spans(date_formats)

        return date_formats

    @staticmethod
    def add_spans(date_formats: dict[str, str]) -> dict[str, str]:
        """
        Wraps the date string in <span> elements with CSS identifiers.
        """
        datetime_string = date_formats["datetime-timezone"]
        for date_type, date_string in date_formats.items():
            date_formats[date_type] = (
                f'<span class="git-revision-date-localized-plugin git-revision-date-localized-plugin-{date_type}" title="{datetime_string}">{date_string}</span>'
            )
        return date_formats

    @staticmethod
    def parse_git_ignore_revs(filename: str | Path) -> list[str]:
        """
        Parses a file that is the same format as git's blame.ignoreRevsFile and return the list of commit hashes.

        Whitespace, blanklines and comments starting with # are all ignored.
        """
        result = []

        try:
            with open(filename, encoding="utf-8") as f:
                for line in f:
                    line = line.split("#", 1)[0].strip()
                    if not line:
                        continue
                    result.append(line)
        except FileNotFoundError:
            logger.error(f"File not found: {filename}")
        except Exception as e:
            logger.error(f"An error occurred while reading the file {filename}: {e}")

        return result

    def get_tag_name_for_commit(self, commit_hash: str) -> str:
        """
        Get the tag name for a specific commit.

        Args:
            commit_hash (str): The commit hash to find tags for

        Returns:
            str: Tag name if found, otherwise empty string
        """
        if not commit_hash:
            return ""

        try:
            for path, git in self.repo_cache.items():
                try:
                    # Check if there's a tag pointing to this commit
                    tags = git.tag("--points-at", commit_hash, format="%(refname:short)")
                    if tags:
                        # Return first tag if multiple tags exist for the commit
                        return tags.split("\n")[0]
                except GitCommandError:
                    # Continue checking other repositories in cache
                    continue

            return ""  # No tag found for this commit
        except Exception as e:
            logger.debug(f"Error getting tag for commit {commit_hash}: {str(e)}")
            return ""
