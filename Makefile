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

.DEFAULT_GOAL := help

# ============================================================================
# Help
# ============================================================================

.PHONY: help
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "For more details, see the project documentation."

# ============================================================================
# Setup
# ============================================================================

.PHONY: submodules develop pre-commit pre-commit-update

submodules: ## Initialize git submodules (nist-content, oscal)
	git submodule update --init

develop: submodules ## Set up development environment
	pip install hatch
	pip install -e .[dev]

pre-commit: ## Install pre-commit hooks
	pre-commit install

pre-commit-update: ## Update pre-commit hooks to latest versions
	pre-commit autoupdate

# ============================================================================
# Code Quality (via hatch)
# ============================================================================

.PHONY: code-format code-lint code-lint-fix code-typing code-check mdformat

code-format: ## Format code with ruff
	hatch fmt --formatter

code-lint: ## Check code style with ruff (no fixes)
	hatch fmt --linter --check

code-lint-fix: ## Fix code style issues with ruff
	hatch fmt --linter

code-typing: ## Run mypy type checking
	hatch run -- mypy --pretty trestle

code-check: code-format code-lint code-typing ## Run all code quality checks

mdformat: ## Format markdown files
	pre-commit run mdformat --all-files

# ============================================================================
# Testing (via hatch test)
# ============================================================================

.PHONY: test test-all test-cov test-cov-xml test-bdist

test: ## Run tests (stops on first failure)
	hatch test

test-all: ## Run all tests in parallel
	hatch test --all

test-cov: ## Run tests with coverage report
	hatch test --cover

test-cov-xml: test-cov ## Run tests with coverage and generate XML report
	coverage xml

test-bdist: clean ## Test binary distribution (wheel install)
	bash tests/manual_tests/test_binary.sh

# ============================================================================
# Build & Release
# ============================================================================

.PHONY: build release

build: ## Build source and wheel distributions
	hatch build

release: ## Create a release (CI only)
	git config --global user.name "semantic-release (via Github actions)"
	git config --global user.email "semantic-release@github-actions"
	semantic-release publish

# ============================================================================
# Documentation
# ============================================================================

.PHONY: docs-osx-deps docs-ubuntu-deps docs-build docs-serve docs-validate

docs-osx-deps: ## Install docs dependencies on macOS
	brew install cairo freetype libffi libjpeg libpng zlib

docs-ubuntu-deps: ## Install docs dependencies on Ubuntu
	sudo apt-get update
	sudo apt-get -y install libcairo2-dev libfreetype6-dev libffi-dev libjpeg-dev libpng-dev libz-dev

docs-build: ## Build documentation site
	hatch run docs:build

docs-serve: ## Serve documentation locally
	hatch run docs:serve

docs-validate: ## Validate documentation (build + link check)
	hatch run docs:validate

# ============================================================================
# Utilities
# ============================================================================

.PHONY: gen-oscal simplified-catalog check-for-changes clean clean-env

gen-oscal: ## Generate OSCAL Python models from JSON schemas
	hatch run python ./scripts/gen_oscal.py

simplified-catalog: ## Generate simplified NIST catalog for testing
	hatch run python ./scripts/simplify_retain_ac.py ./nist-content/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json ./tests/data/json/simplified_nist_catalog.json

check-for-changes: ## Check for uncommitted changes (CI)
	hatch run docs:automation
	git diff --exit-code

clean: ## Remove build artifacts and caches
	rm -rf build dist .pytest_cache tmp_bin_test cov_html coverage.xml .coverage* .mypy_cache .ruff_cache site
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

clean-env: ## Remove all hatch environments (forces dependency reinstall)
	hatch env prune
