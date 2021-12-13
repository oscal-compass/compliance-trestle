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
review to indicate acceptance. A change requires LGTMs from one of the maintainers.

For a list of the maintainers, see the [MAINTAINERS.md](https://ibm.github.io/compliance-trestle/maintainers/) page.

### Trestle merging and release workflow

`trestle` is operating on a simple, yet opinionated, method for continuous integration. It's designed to give developers a coherent understanding of the objectives of other past developers.
The criteria for this are below. Trestle effectively uses a gitflow workflow with one modification: PR's merge into develop are squash merged as one commit.

In trestle's CI environment this results in the following rules:

1. All Commit's *MUST* be signed off with `git commit --signoff` irrespective of the author's affiliation. This ensures all code can be attributed.
   1. This is enforced by DCO bot and can be overrided by maintainers presuming at least one commit is signed-off.
1. All commits *SHOULD* use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0-beta.2/)
   1. This is as github, when only one commit is in a PR, will use the native git commit message as the merge commit title.
      1. When only a single commit is provided the commit MUST be an conventional commit and will be checked the `Lint PR` aciton.
1. All PR's title's MUST be formed as an [convention commit](https://www.conventionalcommits.org/en/v1.0.0-beta.2/)
   1. This is checked by the `Lint PR` action
1. All PR's to `develop` and hotfix PR's to `main` must close at least one issue by [linking the PR to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword).
1. Trestle will release on demand the default approach for a hot fix should be to merge into `develop`, followed by releasing to `main`, unless this will release functionality that is not ready.
1. Each feature/fix/chore (PR into develop) be represented by a single commit into develop / main with a coherent title (in the PR).
   1. The trestle preference for doing this is to use squash merge functionality when merging a PR into develop.
1. Developers *MUST* pass the required CI checks for each PR.
1. Developers are encouraged to use GitHub's automated merge process where possible to keep the number of active PR's low.

### Merge details for committers:

1. All merges into develop MUST be conducted by a squash-merge
1. All merges from develop into main MUST be done by a merge commit (e.g. preserving the history of commits into the develop branch).
1. Hotfixes into main, not via develop, MUST be done via a squash merge.
1. Merge's into any branch excluding main and develop are at the developers choice.
1. Use of autocommit is encouraged to ensure commit messages and squash vs merge commit are completed properly.

### Working from a fork

1. In order not to break Github Actions security model SonarCloud will not run on a fork.
1. Given this a maintainer MAY determine that sonar needs to be run and ask you to first merge your branch to a
   staging branch, after reviewing for security risks in the CI pipeline.
1. From this staging branch sonar would be run and then the code merged.

## Typing, docstrings and documentation

`trestle` has a goal of using [PEP 484](https://www.python.org/dev/peps/pep-0484/) type annotations where possible / practical.
The devops process does not _strictly_ enforce typing, however, the expectation is that type coverage is added for new
commits with a focus on quality over quantity (e.g. don't add `Any` everywhere just to meet coverage requirements).
Python typing of functions is an active work in progress.

`mkbuild` is used to generate the [trestle documenation site](https://ibm.github.io/compliance-trestle). The `mkbuild`
website includes an API reference section generated from the code. Docstrings within the code are expected to follow
[google style docstrings](https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html).

## Legal

Each source file must include a license header for the Apache
Software License 2.0. Using the SPDX format is the simplest approach.
e.g.

```text
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
```

We have tried to make it as easy as possible to make contributions. This
applies to how we handle the legal aspects of contribution. We use the
same approach - the [Developer's Certificate of Origin 1.1 (DCO)](https://ibm.github.io/compliance-trestle/contributing/DCO.md) - that the Linux® Kernel [community](https://elinux.org/Developer_Certificate_Of_Origin)
uses to manage code contributions.

We simply ask that when submitting a patch for review, the developer
must include a sign-off statement in the commit message.

Here is an example Signed-off-by line, which indicates that the
submitter accepts the DCO:

```text
Signed-off-by: John Doe <john.doe@example.com>
```

You can include this automatically when you commit a change to your
local git repository using the following command:

```bash
git commit --signoff
```

Note that DCO signoff is enforced by [DCO bot](https://github.com/probot/dco). Missing DCO's will be required to be rebased
with a signed off commit before being accepted.

## Setup - Developing `trestle`

### Does `trestle` run correctly on my platform

- (Optional) setup a venv for python
- Run `make develop`
  - This will install all python dependencies
  - It will also checkout the submodules required for testing.
- Run `make test`
  - This *should* run on all platforms

### Setting up `vscode` for python.

- Use the following commands to setup python:

```bash
python3 -m venv venv
. ./venv/bin/activate
# for zsh put .[dev] in quotes as below
pip install -q -e ".[dev]" --upgrade --upgrade-strategy eager
```

- Install vscode plugin `Python extension for Visual Studio Code`

- Enable `yapf` for code formatting

- Enable `flake8` for code linting

### Testing python in `vscode`

Tests should be in the test subdirectory. Each file should be named test\_\*.py and each test function should be named \*\_test().

Note that with Python3 there should be no need for __init__.py in directories.

Test discovery should be automatic when you select a .py file for editing. After tests are discovered a flask icon will appear on the left and you can select it to see a panel listing of your tests.  In addition your test functions will be annotated with Run/Debug so they can be launched directly from the editor.  When everything is set up properly you should be able to step through your test code - which is important.

Sometimes the discovery fails - and you may need to resort to uninstalling the python extension and reinstalling it - perhaps also shutting down code and restarting.  This is a lightweight operation and seems to be safe and usually fixes any problems.

Test disovery will fail or stop if any of the tests have errors in them - so be sure to monitor the Problems panel at the bottom for problems in the code.

Note that there are many panels available in Output - so be sure to check `Python Test Log` for errors and output from the tests.

pytest fixtures are available to allow provision of common functionality.  See conftest.py and tmp_dir for an example.

#### NIST reference data for testing.

Trestle relies on reference data from two NIST repositories for testing:

- https://github.com/usnistgov/OSCAL
- https://github.com/usnistgov/oscal-content

Both of these repositories are submodules in the trestle project. In order to develop / test trestle the submodules must be checked out with `git submodule update --init` or `make submodules`.

### Code style and formating

`trestle` uses [yapf](https://github.com/google/yapf) for code formatting and [flake8](https://flake8.pycqa.org/en/latest/) for code styling.  It also uses [pre-commit](https://pre-commit.com/) hooks that are integrated into the development process and the CI. When you run `make develop` you are ensuring that the pre-commit hooks are installed and updated to their latest versions for this repository. This ensures that all delivered code has been properly formatted
and passes the linter rules.  See the [pre-commit configuration file](<>)./.pre-commit-config.yaml) for details on
`yapf` and `flake8` configurations.

Since `yapf` and `flake8` are installed as part of the `pre-commit` hooks, running `yapf` and `flake8`
manually must be done through `pre-commit`.  See examples below:

```bash
make code-format
make code-lint
```

...will run `yapf` and `flake8` on the entire repo and is equivalent to:

```bash
pre-commit run yapf --all-files
pre-commit run flake8 --all-files
```

...and when looking to limit execution to a subset of files do similar to:

```bash
pre-commit run yapf --files trestle/*
pre-commit run flake8 --files trestle/*
```

Note that in both of these cases autogenerated files under `trestle/oscal` are excluded. Note that for IDE support `setup.cfg` maintains a cache of `flake8` configuration.
