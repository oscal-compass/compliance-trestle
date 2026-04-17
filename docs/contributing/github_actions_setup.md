---
title: Setting up GitHub actions
description: Setting up github actions for a fork of compliance trestle for development
---

# Github actions setup

Github actions contains variables which have opaque values to a user.
The variables are documented here such that trestle can be setup on a fork for independent development.
This is not required to open a pull request against the compliance-trestle project.
Project maintainers, after an initial review, will allow github actions workflows to run.

## Secrets

- `APP_ID` and `PRIVATE_KEY`: GitHub App information with sufficient write access to merge content into `develop` and commit to `gh-pages`, `main`, and maintenance branches (`v3`, `v4`, etc.)

- `SONAR_TOKEN`: Token to sonarcloud with rights to the appropriate project.

## Authorization with pypi

Pypi authorization must be setup following the procedure in the following documents

- https://docs.pypi.org/trusted-publishers/adding-a-publisher/

## Maintenance branch configuration

Trestle supports releasing patches from maintenance branches (e.g., `v3`, `v4`). When creating a new maintenance branch, the following GitHub configuration is required:

- **Branch protection**: Create a ruleset for `v[0-9]*` branches requiring PR reviews, status checks, squash merges, and restricted push access. See [Maintenance releases](maintenance_releases.md) for details.
- **Release environment**: The `release` environment's deployment branch rules must include maintenance branches (add `v*` pattern or list branches explicitly).
- **PyPI trusted publisher**: Verify the trusted publisher configuration does not restrict publishing to `main` only.
