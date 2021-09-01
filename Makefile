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

develop:
	python -m pip install -e .[dev] --upgrade --upgrade-strategy eager

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
	python -m pytest trestle tests  --exitfirst -n auto

test-cov::
	python -m pytest --cov trestle tests  --exitfirst --cov-report=xml -n auto 

test-all-random::
	python -m pytest --cov trestle tests --cov-report=xml --random-order

test-verbose:
	python -m pytest  trestle tests -vv -n auto

test-speed-measure:
	python -m pytest trestle tests -n auto --durations=30 

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
# Something funky about these tests.
# clean::
# 	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

