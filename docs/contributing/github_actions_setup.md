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

- `RELEASE_TAG_SIGNING_KEY` and `RELEASE_TAG_SIGNING_KEY_PUB`: SSH key pair used to cryptographically sign release tags. See [Release tag signing](#release-tag-signing) below.

## Release tag signing

Every version tag created by the release pipeline is signed with an SSH key so that consumers can verify the tag's authenticity with `git tag -v <tag>`. The `python-semantic-release` action reads the key pair from the two secrets below and configures git to sign the tag automatically during `semantic-release version`.

### Secrets

| Secret | Content |
| --- | --- |
| `RELEASE_TAG_SIGNING_KEY` | PEM-encoded Ed25519 **private** key (no passphrase) |
| `RELEASE_TAG_SIGNING_KEY_PUB` | Corresponding **public** key in `authorized_keys` format |

### Generating the key pair

Run once, outside of CI, and store the outputs in the repository's **release** environment secrets:

```bash
ssh-keygen -t ed25519 -C "compliance-trestle release tag signing" -f release_tag_signing_key -N ""
# Private key → RELEASE_TAG_SIGNING_KEY  (contents of release_tag_signing_key)
# Public key  → RELEASE_TAG_SIGNING_KEY_PUB  (contents of release_tag_signing_key.pub)
rm release_tag_signing_key release_tag_signing_key.pub  # remove local copies after upload
```

Add both secrets to **Settings → Environments → release** (not as repository-level secrets) so they are only accessible to the deploy job.

### Adding the public key to the repository's allowed signers

GitHub uses the repository's `/.github/allowed_signers` file (or a `CODEOWNERS`-adjacent convention) to let `git tag -v` resolve the signer identity. Create or append to `.github/allowed_signers`:

```
semantic-release@users.noreply.github.com namespaces="git" <contents of release_tag_signing_key.pub>
```

Then configure git locally to use it for verification:

```bash
git config gpg.ssh.allowedSignersFile .github/allowed_signers
```

### Verifying a signed tag

```bash
# One-time setup: point git at the repository's allowed-signers file
git config gpg.ssh.allowedSignersFile .github/allowed_signers

git fetch --tags
git tag -v v5.1.0
# Expected output includes:
# Good "git" signature for semantic-release@users.noreply.github.com with ED25519 key ...
```

## Authorization with pypi

Pypi authorization must be setup following the procedure in the following documents

- https://docs.pypi.org/trusted-publishers/adding-a-publisher/

## Maintenance branch configuration

Trestle supports releasing patches from maintenance branches (e.g., `v3`, `v4`). When creating a new maintenance branch, the following GitHub configuration is required:

- **Branch protection**: Create a ruleset for `v[0-9]*` branches requiring PR reviews, status checks, squash merges, and restricted push access. See [Maintenance releases](maintenance_releases.md) for details.
- **Release environment**: Add the specific maintenance branch to the `release` environment's deployment branch rules. See [Adding a branch to the release environment](#adding-a-branch-to-the-release-environment) below.
- **PyPI trusted publisher**: Verify the trusted publisher configuration does not restrict publishing to `main` only.

### Adding a branch to the release environment

When cutting a new major version (e.g., v5.0.0), add the previous major version's maintenance branch (e.g., `v4`) to the `release` GitHub Environment. Each branch must be added **individually by exact name** (not using wildcards) to require deliberate opt-in for new maintenance branches.

#### Using the GitHub UI

1. Navigate to **Settings** → **Environments** → **release**
1. Under **Deployment branches and tags**, click **Add deployment branch or tag rule**
1. Select **Branch** as the rule type
1. Enter the exact branch name: `v4` (not `v*` or `v[0-9]*`)
1. Click **Add rule**

#### Using the GitHub CLI

```bash
gh api repos/oscal-compass/compliance-trestle/environments/release/deployment-branch-policies \
  --method POST -f name='v4' -f type='branch'
```

#### Verifying the configuration

List all deployment branches to confirm the new branch was added:

```bash
gh api repos/oscal-compass/compliance-trestle/environments/release/deployment-branch-policies \
  --jq '.branch_policies[] | {name, type}'
```

Expected output should include entries for `main` and all active maintenance branches (e.g., `v3`, `v4`).
