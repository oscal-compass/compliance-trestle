# Github actions setup

Github actions contains variables which have opaque values to a user.
The variables are documented here such that trestle can be setup on a fork etc.

## Secrets

- `ADMIN_PAT`: Github PAT with sufficient write access to merge content into `develop` and commit to `gh-pages` and `main`

- `SONAR_TOKEN`: Token to sonarcloud with rights to the appropriate project.

## Repository level variables

- `PYTHON_MIN`: Minimum test version of python e.g. `3.9`
- `PYTHON_MAX`: Maxmimum test version of python e.g. `3.11`

## Authorization with pypi

Pypi authorization must be setup following the procedure in the following documents

- https://docs.pypi.org/trusted-publishers/adding-a-publisher/
