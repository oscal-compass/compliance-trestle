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

submodules: 
	git submodule update --init

develop: submodules
	uv sync --all-extras --dev --all-packages

pre-commit: 
	pre-commit install

pre-commit-update:
	pre-commit autoupdate


install:
	uv pip install --upgrade pip setuptools
	uv pip install . --upgrade

code-format:
	pre-commit run yapf --all-files

code-lint:
	pre-commit run flake8 --all-files

code-typing:
	mypy --pretty trestle

test-all::
	uv run pytest -n auto

test::
	uv run pytest --exitfirst -n auto

test-cov::
	uv run pytest --cov=trestle  --exitfirst -n auto -vv --cov-report=xml --cov-fail-under=96

test-all-random::
	uv run pytest --cov=trestle --cov-report=xml --random-order

test-verbose:
	uv run pytest  -vv -n auto

test-speed-measure:
	uv run pytest -n auto --durations=30

test-fast:
	uv run pytest -n auto --exitfirst -k "not fetcher and not from_nist and not from_url"

test-bdist:: clean
	. trestle-cli/tests/manual_tests/test_binary.sh


release::
	git config --global user.name "semantic-release (via Github actions)"
	git config --global user.email "semantic-release@github-actions"
	semantic-release publish

gen-oscal::
	python ./scripts/gen_oscal.py

docs-osx-deps:
	brew install cairo freetype libffi libjpeg libpng zlib

docs-ubuntu-deps:
	sudo apt-get -y install libcairo2-dev libfreetype6-dev libffi-dev libjpeg-dev libpng-dev libz-dev

docs-automation::
	python ./scripts/website_automation.py


# docs validate remains using mkdocs as mike does not have a build validation tool for serving
docs-validate:: docs-automation
	mkdocs build -c -s
	rm -rf site

docs-serve: docs-automation
	git fetch origin gh-pages
	mike serve	

mdformat:
	pre-commit run mdformat --all-files

simplified-catalog:
	python ./scripts/simplify_retain_ac.py ./nist-content/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json ./trestle-cli/tests/data/json/simplified_nist_catalog.json

# POSIX ONLY
clean::
	rm -rf build
	rm -rf dist
	rm -rf .pytest_cache
	rm -rf tmp_bin_test
	rm -rf cov_html
	rm -rf coverage.xml
	rm -rf .coverage*
	rm -rf .mypy_cache
	find . | grep -E "__pycache__|\.pyc|\.pyo" | xargs rm -rf

pylint:
	pylint trestle

pylint-test:
	pylint tests --rcfile=.pylintrc_tests

check-for-changes:
	python scripts/have_files_changed.py -u
