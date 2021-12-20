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
	python -m pip install -e .[dev] --upgrade --upgrade-strategy eager --

pre-commit: 
	pre-commit install

pre-commit-update:
	pre-commit autoupdate

install:
	python -m pip install  --upgrade pip setuptools
	python -m pip install . --upgrade --upgrade-strategy eager

code-format: pre-commit-update
	pre-commit run yapf --all-files

code-lint: pre-commit-update
	pre-commit run flake8 --all-files

code-typing:
	mypy --pretty trestle

test::
	python -m pytest --exitfirst -n auto

test-cov::
	python -m pytest --cov=trestle  --exitfirst -n auto -vv --cov-report=xml --cov-fail-under=96

test-all-random::
	python -m pytest --cov=trestle --cov-report=xml --random-order

test-verbose:
	python -m pytest  -vv -n auto

test-speed-measure:
	python -m pytest -n auto --durations=30 


test-bdist:: clean
	. tests/manual_tests/test_binary.sh


release::
	git config --global user.name "semantic-release (via Github actions)"
	git config --global user.email "semantic-release@github-actions"
	semantic-release publish

gen-oscal::
	python ./scripts/gen_oscal.py

docs-automation::
	python ./scripts/website_automation.py

docs-validate:: docs-automation
	mkdocs build -c -s
	rm -rf site

docs-serve: docs-automation
	mkdocs serve	

mdformat: pre-commit-update
	pre-commit run mdformat --all-files

simplified-catalog:
	python ./scripts/simplify_retain_ac.py ./nist-content/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json ./tests/data/json/simplified_nist_catalog.json

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