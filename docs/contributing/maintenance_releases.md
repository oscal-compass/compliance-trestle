---
title: Maintenance releases
description: How to create security and patch releases for older major versions
---

# Maintenance releases

Trestle supports releasing security and bug fixes for older major versions through **maintenance branches**. This allows patching e.g. v3.x while active development continues on v4.x.

## Overview

- Maintenance branches are named `v<major>` (e.g., `v3`, `v4`)
- Patch-safe commit types are allowed (`fix:`, `perf:`, `chore:`, `ci:`, `docs:`, `build:`, `refactor:`, `style:`, `test:`, `revert:`) — `feat:` and breaking changes (`!`) are blocked by CI
- Releases are automated via the same semantic-release pipeline as `main`
- Documentation is automatically updated when a maintenance release is tagged

## Developer workflow for security fixes

1. **Branch from the maintenance branch**, not from `develop`:

   ```bash
   git checkout v3
   git pull origin v3
   git checkout -b fix/cve-2026-xxxx
   ```

1. **Make the fix and commit** using conventional commits:

   ```bash
   git commit --signoff -m "fix: address CVE-2026-XXXX in authentication module"
   ```

1. **Open a PR targeting the maintenance branch** (e.g., `v3`, not `develop`)

1. **CI runs automatically**:

   - Full test suite via `python-test.yml`
   - PR title validation -- `feat:` titles are rejected on maintenance branches
   - Standard code quality checks

1. **After merge** (squash merge required), the deploy pipeline:

   - Validates the branch name and version consistency
   - Runs semantic-release to bump the patch version (e.g., `3.12.0` -> `3.12.1`)
   - Publishes to PyPI, signs with sigstore, creates a GitHub Release
   - Updates versioned documentation

## Security fix propagation

When a security fix is applied to a maintenance branch, it **must** also be applied to all other affected release trains:

1. After merging the fix to the maintenance branch, cherry-pick to `develop`:

   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b fix/cve-2026-xxxx-develop
   git cherry-pick <commit-sha-from-maintenance-branch>
   ```

1. Open a PR targeting `develop` with the cherry-picked fix

1. Track progress in the original security issue with a cross-train checklist:

   ```markdown
   - [x] v3 (v3.12.1)
   - [ ] v4 (pending PR #NNN)
   ```

1. A security fix is **not considered complete** until all affected trains are patched

## Creating a new maintenance branch

When a new major version is released (e.g., v5.0.0), create a maintenance branch for the previous major version:

1. **Create the branch** from `main` at the last release tag before the breaking change:

   ```bash
   git checkout v4.x.y  # last v4 tag
   git checkout -b v4
   git push origin v4
   ```

1. **The CI pipeline automatically supports the new branch** -- the `v[0-9]*` glob patterns in workflow triggers match any `v<number>` branch without code changes.

1. **Configure branch protection** (see [GitHub actions setup](github_actions_setup.md)):

   - Require pull requests with at least one CODEOWNER review
   - Require status checks to pass
   - Require squash merges only
   - Restrict push access to maintainers
   - Disallow force pushes and deletions

1. **Update the GitHub `release` environment** if it uses an explicit branch list (add the new branch)

1. **Consider enabling Dependabot** for security updates on the new maintenance branch

## CI/CD behavior on maintenance branches

| Pipeline                | Behavior                                                                                                                                              |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `python-test.yml`       | Runs on PRs targeting maintenance branches (same as `develop`)                                                                                        |
| `python-push.yml`       | Triggers on push to maintenance branches; validates branch name, build command, version consistency, and commit types before running semantic-release |
| `conventional-pr.yml`   | Validates PR titles; blocks `feat:` commits on maintenance branches                                                                                   |
| `docs-update.yml`       | Automatically triggered by version tags (e.g., `v3.12.1`)                                                                                             |
| `merge-main-to-develop` | Does **not** run -- maintenance releases are isolated                                                                                                 |

## Restrictions on maintenance branches

- **No feature releases**: `feat:` commits are blocked at the PR level and verified server-side before release. Minor version bumps cannot happen on maintenance branches.
- **No direct pushes**: Branch protection requires all changes go through reviewed PRs.
- **Version consistency**: The major version in `trestle/__init__.py` must match the branch name (e.g., branch `v3` must have version `3.x.x`).
- **Build command integrity**: The `build_command` in `pyproject.toml` is validated against an allowlist before each release.
