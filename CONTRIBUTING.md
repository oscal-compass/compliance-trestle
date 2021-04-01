## Contributing In General

Our project welcomes external contributions. If you have an itch, please feel
free to scratch it.

To contribute code or documentation, please submit a [pull request](https://github.com/IBM/compliance-trestle/pulls).

A good way to familiarize yourself with the codebase and contribution process is
to look for and tackle low-hanging fruit in the [issue tracker](https://github.com/IBM/compliance-trestle/issues).
Before embarking on a more ambitious contribution, please quickly [get in touch](https://ibm.github.io/compliance-trestle/maintainers/) with us.

**Note: We appreciate your effort, and want to avoid a situation where a contribution
requires extensive rework (by you or by us), sits in backlog for a long time, or
cannot be accepted at all!**

We have also adopted [Contributor Covenant Code of Conduct](https://ibm.github.io/compliance-trestle/contributing/mkdocs_contributing/).

### Proposing new features

If you would like to implement a new feature, please [raise an issue](https://github.com/IBM/compliance-trestle/issues)
labelled `enhancement` before sending a pull request so the feature can be discussed. This is to avoid
you wasting your valuable time working on a feature that the project developers
are not interested in accepting into the code base.

### Fixing bugs

If you would like to fix a bug, please [raise an issue](https://github.com/IBM/compliance-trestle/issues) labelled `bug` before sending a
pull request so it can be tracked.

### Merge approval

The project maintainers use LGTM (Looks Good To Me) in comments on the code
review to indicate acceptance. A change requires LGTMs from one of the
maintainers of each component affected.

For a list of the maintainers, see the [MAINTAINERS.md](https://ibm.github.io/compliance-trestle/maintainers/) page.

### Merging and release workflow.

`trestle` today is maintaining two protected workflow branches. The a trunk development branch `develop` which is the target
for all enhancements and non critical features. `main` is used to track releases and allow for hotfixes.

Each merge into `develop` will be squashed into a single commit. This can either be performed on merge or via developers
rebasing their commits into a single commit. As `trestle` has adopted [python semantic release](https://python-semantic-release.readthedocs.org)
the rebase / squash merge commit MUST follow the [angular commit style](https://github.com/angular/angular.js/blob/main/DEVELOPERS.md#-git-commit-guidelines).

Merges from `develop` to `main` for release capture all of these commits for the changelog. The current objective is to
release once per sprint (2 weeks)

Hotfixes *may* be merged directly into main when critical bugs are found. Each hotfix *must* be squashed when merging
into main and MUST only be a commit of type `fix:` in angular style.

## Typing, docstrings and documentation

`trestle` has a goal of using [PEP 484](https://www.python.org/dev/peps/pep-0484/) type annotations where possible / practical.
The devops process does not _strictly_ enforce typing, however, the expectation is that type coverage is added for new
commits with a focus on quality over quantity (e.g. don't add `Any` everywhere just to meet coverage requirements).

`mkbuild` is used to generate the [trestle documenation site](https://ibm.github.io/compliance-trestle). The `mkbuild`
website includes an API reference section generated from the code. Docstrings within the code are expected to follow
[google style docstrings](https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html).

## Legal

Each source file must include a license header for the Apache
Software License 2.0. Using the SPDX format is the simplest approach.
e.g.

```
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
```

We have tried to make it as easy as possible to make contributions. This
applies to how we handle the legal aspects of contribution. We use the
same approach - the [Developer's Certificate of Origin 1.1 (DCO)](https://ibm.github.io/compliance-trestle/contributing/DCO.md) - that the Linux® Kernel [community](https://elinux.org/Developer_Certificate_Of_Origin)
uses to manage code contributions.

We simply ask that when submitting a patch for review, the developer
must include a sign-off statement in the commit message.

Here is an example Signed-off-by line, which indicates that the
submitter accepts the DCO:

```
Signed-off-by: John Doe <john.doe@example.com>
```

You can include this automatically when you commit a change to your
local git repository using the following command:

```
git commit --signoff
```

Note that DCO signoff is enforced by [DCO bot](https://github.com/probot/dco). Missing DCO's will be required to be rebased
with a signed off commit before being accepted.

## Setup - Developing `trestle`

### Setting up `vscode` for python.

- Use the following commands to setup python:

```shell
python3 -m venv venv
. ./venv/bin/activate
# for zsh put .[dev] in quotes as below
pip install -q -e ".[dev]" --upgrade --upgrade-strategy eager
```

- Install vscode plugin `Python extension for Visual Studio Code`

- Enable `yapf` for code formatting

- Enable `flake8` for code linting

### Testing python in `vscode`

Tests should be in the test subdirectory.  Each file should be named test\_\*.py and each test function should be named \*\_test().

Note that with Python3 there should be no need for __init__.py in directories.

Test discovery should be automatic when you select a .py file for editing. After tests are discovered a flask icon will appear on the left and you can select it to see a panel listing of your tests.  In addition your test functions will be annotated with Run/Debug so they can be launched directly from the editor.  When everything is set up properly you should be able to step through your test code - which is important.

Sometimes the discovery fails - and you may need to resort to uninstalling the python extension and reinstalling it - perhaps also shutting down code and restarting.  This is a lightweight operation and seems to be safe and usually fixes any problems.

Test disovery will fail or stop if any of the tests have errors in them - so be sure to monitor the Problems panel at the bottom for problems in the code.

Note that there are many panels available in Output - so be sure to check `Python Test Log` for errors and output from the tests.

pytest fixtures are available to allow provision of common functionality.  See conftest.py and tmp_dir for an example.

### Code style and formating

`trestle` uses [yapf](https://github.com/google/yapf) for code formatting and [flake8](https://flake8.pycqa.org/en/latest/) for code styling.  It also uses [pre-commit](https://pre-commit.com/) hooks that are integrated into the development process and the CI. When you run `make develop` you are ensuring that the pre-commit hooks are installed and updated to their latest versions for this repository. This ensures that all delivered code has been properly formatted
and passes the linter rules.  See the [pre-commit configuration file](<>)./.pre-commit-config.yaml) for details on
`yapf` and `flake8` configurations.

Since `yapf` and `flake8` are installed as part of the `pre-commit` hooks, running `yapf` and `flake8`
manually must be done through `pre-commit`.  See examples below:

```shell
make code-format
make code-lint
```

...will run `yapf` and `flake8` on the entire repo and is equivalent to:

```shell
pre-commit run yapf --all-files
pre-commit run flake8 --all-files
```

...and when looking to limit execution to a subset of files do similar to:

```shell
pre-commit run yapf --files trestle/*
pre-commit run flake8 --files trestle/*
```

Note that in both of these cases autogenerated files under `trestle/oscal` are excluded. Note that for IDE support `setup.cfg` maintains a cache of `flake8` configuration.
