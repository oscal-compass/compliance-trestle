# -*- coding:utf-8 -*-
# Copyright (c) 2026 The OSCAL Compass Authors. All rights reserved.
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
"""Atheris fuzz harness: OSCAL Catalog JSON loading.

Feeds arbitrary bytes into the OSCAL Catalog pydantic model parser.
Expected rejections (ValidationError, ValueError, TrestleError) are swallowed;
any other exception is a real finding.

atheris is Linux-only.  On macOS/Windows the module is not installed and this
file becomes a no-op so that linting and imports still succeed on all platforms.

Run locally (Linux only):
    pip install atheris
    python fuzz/fuzz_oscal_load.py -max_total_time=60 fuzz/corpus/oscal_load
"""

import sys

try:
    import atheris
except ImportError:
    atheris = None  # type: ignore[assignment]

from pydantic import ValidationError

from trestle.common.err import TrestleError
from trestle.oscal.catalog import Catalog


def TestOneInput(data: bytes) -> None:  # noqa: N802
    """Feed arbitrary bytes to the OSCAL Catalog JSON parser."""
    fdp = atheris.FuzzedDataProvider(data)
    text = fdp.ConsumeUnicodeNoSurrogates(len(data))
    try:
        Catalog.model_validate_json(text)
    except (ValidationError, ValueError, TrestleError):
        pass


def main() -> None:
    """Entry point for atheris."""
    if atheris is None:
        raise SystemExit('atheris is only available on Linux')
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == '__main__':
    main()
