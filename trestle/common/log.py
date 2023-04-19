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
"""Common logging utilities."""
import argparse
import logging
import sys
from types import TracebackType
from typing import Optional, Type

# Singleton logger instance
# All other CLI sub module will inherit settings of this logger as long as
# sub-module instantiates a logger with a prefix 'trestle' or __name__
_logger = logging.getLogger('trestle')


class SpecificLevelFilter(logging.Filter):
    """
    Filter for the same level as provided by setLevel for a log handler.

    Python by default logs all levels above to a given destination. This makes it easy to split levels where you might
    log all levels to file and only errors to std.err, however, does not allow logging a specific level elsewhere.
    """

    def __init__(self, level: int) -> None:
        """Initialize providing maximum level to be pushed through the filter."""
        self._level = level

    def filter(self, log_record: logging.LogRecord) -> bool:  # noqa: A003
        """Filter log messages."""
        return log_record.levelno == self._level


def set_global_logging_levels(level: int = logging.INFO) -> None:
    """Initialise logging.

    Should only be invoked by the CLI classes or similar.
    """
    # This line stops default root loggers setup for a python context from logging extra messages.
    # DO NOT USE THIS COMMAND directly from an SDK. Handle logs levels based on your own application
    _logger.propagate = False
    # Remove handlers
    _logger.handlers.clear()
    # set global level
    _logger.setLevel(level)
    # Create standard out
    console_out_handler = logging.StreamHandler(sys.stdout)
    console_out_handler.setLevel(logging.INFO)
    console_out_handler.addFilter(SpecificLevelFilter(logging.INFO))

    console_debug_handler = logging.StreamHandler(sys.stdout)
    console_debug_handler.setLevel(logging.DEBUG)
    console_debug_handler.addFilter(SpecificLevelFilter(logging.DEBUG))

    console_error_handler = logging.StreamHandler(sys.stderr)
    console_error_handler.setLevel(logging.WARNING)
    # create formatters
    error_formatter = logging.Formatter('%(name)s:%(lineno)d %(levelname)s: %(message)s')
    debug_formatter = logging.Formatter('%(name)s:%(lineno)d %(levelname)s: %(message)s')
    console_debug_handler.setFormatter(debug_formatter)
    console_error_handler.setFormatter(error_formatter)
    # add ch to logger
    _logger.addHandler(console_out_handler)
    _logger.addHandler(console_error_handler)
    _logger.addHandler(console_debug_handler)


def _exception_handler(
    exception_type: Type[BaseException], exception: BaseException, traceback: Optional[TracebackType]
) -> None:
    """Empty exception handler to prevent stack traceback in quiet mode."""
    logging.warning(exception)


def _get_trace_level() -> int:
    """Get special value used for trace - just below DEBUG."""
    return logging.DEBUG - 5


def set_log_level_from_args(args: argparse.Namespace) -> None:
    """Vanity function to automatically set log levels based on verbosity flags."""
    if args.verbose > 1:
        # these msgs only output by trace calls
        set_global_logging_levels(_get_trace_level())
    elif args.verbose == 1:
        set_global_logging_levels(logging.DEBUG)
    else:
        set_global_logging_levels(logging.INFO)
        sys.excepthook = _exception_handler


def get_current_verbosity_level(logger: logging.Logger) -> int:
    """Get the current verbosity level based on logging level."""
    level = logger.getEffectiveLevel()
    if level < logging.DEBUG:
        return 2
    elif level == logging.DEBUG:
        return 1
    return 0


class Trace():
    """Class allowing low priority trace message when verbose > 1 and log level below DEBUG."""

    def __init__(self, logger: logging.Logger) -> None:
        """Store the main logger with its module name."""
        self._logger = logger

    def log(self, msg: str) -> None:
        """Output the trace msg if log level is below DEBUG."""
        level = self._logger.getEffectiveLevel()
        if level < logging.DEBUG:
            self._logger.debug(msg)
