# -*- mode:makefile; coding:utf-8 -*-

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

# ============================================================================
# Setup
# ============================================================================

submodules:
	git submodule update --init

develop: submodules
	pip install hatch
	pip install -e .[dev]

pre-commit:
	pre-commit install

pre-commit-update:
	pre-commit autoupdate

# ============================================================================
# Code Quality (via hatch)
# ============================================================================

code-format:
	hatch fmt --formatter

code-lint:
	hatch fmt --linter --check

code-lint-fix:
	hatch fmt --linter

code-typing:
	hatch run -- mypy --pretty trestle

code-check: code-format code-lint code-typing

mdformat:
	pre-commit run mdformat --all-files

# ============================================================================
# Testing (via hatch test)
# ============================================================================

test:
	hatch test

test-all:
	hatch test --all

test-cov:
	hatch test --cover

test-cov-xml: test-cov
	coverage xml

test-bdist:: clean
	bash tests/manual_tests/test_binary.sh

# ============================================================================
# Build & Release
# ============================================================================

build:
	hatch build

release::
	git config --global user.name "semantic-release (via Github actions)"
	git config --global user.email "semantic-release@github-actions"
	semantic-release publish

# ============================================================================
# Documentation
# ============================================================================

docs-osx-deps:
	brew install cairo freetype libffi libjpeg libpng zlib

docs-ubuntu-deps:
	sudo apt-get update
	sudo apt-get -y install libcairo2-dev libfreetype6-dev libffi-dev libjpeg-dev libpng-dev libz-dev

docs-build:
	hatch run docs:build

docs-serve:
	hatch run docs:serve

docs-validate:
	hatch run docs:validate

# ============================================================================
# Utilities
# ============================================================================

gen-oscal::
	hatch run python ./scripts/gen_oscal.py

simplified-catalog:
	hatch run python ./scripts/simplify_retain_ac.py ./nist-content/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json ./tests/data/json/simplified_nist_catalog.json

check-for-changes:
	hatch run docs:automation
	git diff --exit-code

clean::
	rm -rf build dist .pytest_cache tmp_bin_test cov_html coverage.xml .coverage* .mypy_cache .ruff_cache site
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
