# Dependency Management Policy

This document sets the baseline requirements Compliance Trestle uses to choose, add, update, monitor and remove
third-party dependencies, as required by [OSPS-DO-06.01](https://baseline.openssf.org/versions/2025-02-25#osps-do-0601).

## Scope

This policy covers every third-party component that trestle depends on:

- Runtime dependencies declared in `[project].dependencies` of [`pyproject.toml`](pyproject.toml). They are installed
  for every trestle user.
- Optional dependency groups (extras) declared in `[project.optional-dependencies]` of `pyproject.toml`, such as
  `fuzz`, `typing`, `docs` and `dev`.
- Dependencies of the hatch environments used for testing and development (`[tool.hatch.envs.*]` in
  `pyproject.toml`).
- GitHub Actions and container images used by the workflows in [`.github/workflows`](.github/workflows) and the
  composite actions in [`.github/actions`](.github/actions).

The [license](#license-requirements) and [vulnerability](#monitoring-for-vulnerabilities) requirements also apply to
transitive dependencies, that is, the dependencies of trestle's dependencies.

## Choosing a dependency

Before adding a new dependency, check that the functionality is not already available in the Python standard library
or in a dependency that trestle already uses. Every new dependency adds to the install footprint and the attack surface
for all users, so prefer a small amount of code in trestle over a dependency that would only be used lightly.

A new dependency must meet all of the following:

1. **License:** It meets the [license requirements](#license-requirements) below.
1. **Maintenance:** It is actively maintained, for example with recent releases and issues that maintainers respond to.
   Deprecated or archived projects must not be added.
1. **Adoption:** It shows substantial use outside trestle, for example a widely used package on PyPI, or a project
   created at least 12 months ago with at least 10 stars or 10 forks.
1. **Security:** It has no known unresolved vulnerabilities in the version being added. Check the package in public
   advisory databases such as the [OSV database](https://osv.dev/) or the
   [GitHub Advisory Database](https://github.com/advisories), and review how past vulnerabilities were handled.
1. **Compatibility:** It supports every Python version that trestle supports (see `requires-python` and the classifiers
   in `pyproject.toml`) and the operating systems trestle runs on (Linux, macOS and Windows), unless it is limited to
   one platform with an environment marker.
1. **Placement:** It is declared in the narrowest place that works. Packages needed only for an optional feature,
   testing, typing, documentation or development go in the matching extra or hatch environment, not in the runtime
   dependencies.

The pull request that adds the dependency must say why it is needed and what alternatives were considered. Dependency
changes are reviewed under the [code review policy](docs/code-review-policy.md), like every other change.

## License requirements

Trestle is an Apache-2.0 licensed [CNCF](https://www.cncf.io/) project and follows the
[CNCF allowed third-party license policy](https://github.com/cncf/foundation/blob/main/policies-guidance/allowed-third-party-license-policy.md):

- Dependencies licensed under Apache-2.0 are allowed.
- Dependencies that are fully licensable under one of the licenses in the CNCF
  [Approved Licenses for Allowlist](https://github.com/cncf/foundation/blob/main/policies-guidance/allowed-third-party-license-policy.md#approved-licenses-for-allowlist)
  (for example MIT, BSD-2-Clause, BSD-3-Clause, ISC or PSF-2.0) are allowed if they also meet the other criteria of the
  CNCF Allowlist License Policy. Trestle meets the storage criterion by not vendoring dependencies: they are installed
  from PyPI.
- Any other license (for example MPL-2.0 or LGPL-2.1) needs a license exception approved by the CNCF Governing Board
  **before** the dependency is merged. A maintainer requests the exception through the
  [CNCF exception process](https://github.com/cncf/foundation/blob/main/policies-guidance/allowed-third-party-license-policy.md#process-for-applying-for-an-exception).
- Approved exceptions are recorded in the [`.snyk`](.snyk) policy file with a link to the approved request, so that the
  license check in CI accepts them.
- Dependencies with no license, or with a license that does not allow redistribution, are not allowed.

## Declaring dependencies

- Runtime dependencies, extras and hatch environment dependencies in `pyproject.toml` are pinned to an exact version
  with `==`. This makes builds reproducible and means that every version change goes through a reviewed pull request.
- Platform-specific dependencies use [environment markers](https://peps.python.org/pep-0508/#environment-markers), for
  example `pywin32 == 312; platform_system == 'Windows'`.
- GitHub Actions are pinned to a full commit SHA, with the release tag in a trailing comment, for example
  `actions/checkout@<sha> # v7.0.1`. Container images used by workflows are pinned to a digest.

## Updating dependencies

- [Dependabot](.github/dependabot.yml) checks the `pip` and `github-actions` ecosystems every week and opens a pull
  request for each new version. Its commits use the `fix(deps)` and `fix(deps-dev)` prefixes, so updates show up in the
  release notes.
- Dependency update pull requests run the same pipeline as every other pull request: tests on the oldest and newest
  supported Python versions on Linux, macOS and Windows, linting, type checking and the documentation build. They are
  merged only when the pipeline passes.
- If an update needs code changes, for example a new major version with breaking changes, the changes are made in the
  same pull request as the update, with tests.
- Dependencies that become deprecated or unmaintained are replaced, and dependencies that are no longer used are
  removed.

## Monitoring for vulnerabilities

- **Dependabot** proposes updates to the pinned dependencies every week, which brings in security fixes from new
  releases.
- **Snyk** runs in the pull request pipeline for pull requests opened from branches of this repository, other than
  Dependabot's (see [`.github/actions/snyk-test`](.github/actions/snyk-test)). It resolves the full dependency tree from
  `pyproject.toml` and checks it for known vulnerabilities and license issues.
- **OpenSSF Scorecard** and **CodeQL** run on the repository and report supply chain and code security findings.

When a dependency has a known vulnerability:

1. Upgrade to a version that fixes it as soon as one is available.
1. If no fix is available, maintainers assess whether the vulnerability can be exploited through trestle. If the risk is
   accepted, the finding may be ignored in [`.snyk`](.snyk) with a written reason and an `expires` date, so that it is
   reviewed again. The ignore is removed once a fixed version is adopted.
1. If the vulnerability can be exploited through trestle, it is handled as a security issue in trestle itself.

To report a vulnerability in trestle, follow the [security policy](SECURITY.md).
