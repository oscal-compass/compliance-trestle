---
title: Testing GitHub Actions locally
description: How to test CI/CD workflow changes locally using act
---

# Testing GitHub Actions locally

When modifying GitHub Actions workflows, you can validate changes locally before pushing using [act](https://github.com/nektos/act). This avoids slow feedback loops from CI and reduces noise on the PR.

## Prerequisites

- **act**: Install via `brew install act` (macOS) or see [act installation](https://nektosact.com/installation/)
- **Container runtime**: Either [podman](https://podman.io/) or [Docker](https://www.docker.com/)

### Configuring act with podman

On macOS with podman, set the `DOCKER_HOST` environment variable so act can find the podman socket:

```bash
export DOCKER_HOST="unix://$(podman machine inspect --format '{{.ConnectionInfo.PodmanSocket.Path}}')"
```

Add this to your shell profile (`.zshrc`, `.bashrc`) to make it persistent.

Ensure the podman machine is running:

```bash
podman machine start
```

## Makefile targets

The following make targets are available for local workflow testing:

```bash
# Run actionlint workflow locally (validates workflow YAML syntax)
make act-lint

# Dry-run the full PR test pipeline (validates structure without executing)
make act-test-dry

# Dry-run the deploy pipeline (validates structure without executing)
make act-deploy-dry
```

All targets use `--container-architecture linux/amd64` automatically for Apple Silicon compatibility.

## Running act directly

For more control, run `act` directly:

```bash
# List all jobs across all workflows
act --list

# List jobs in a specific workflow
act --list -W .github/workflows/python-test.yml

# Dry-run a specific job
act -n -W .github/workflows/python-test.yml -j lint --container-architecture linux/amd64

# Actually run the actionlint workflow (requires container runtime)
act -W .github/workflows/actionlint.yml --container-architecture linux/amd64
```

## What can and cannot be tested locally

| What                                  | Testable locally?   | Notes                                                                                                             |
| ------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Workflow YAML syntax                  | Yes                 | `act --list` or `act -n` catches parse errors                                                                     |
| Job dependencies and ordering         | Yes                 | Dry-run validates the DAG                                                                                         |
| Step conditionals (`if:` expressions) | Partial             | Dry-run shows which steps would run, but context variables like `github.ref` need to be simulated via event files |
| Shell scripts in `run:` steps         | Yes (with full run) | Requires container runtime; secrets won't be available                                                            |
| Actions that require secrets          | No                  | GitHub App tokens, SonarCloud, Snyk, PyPI publishing cannot be tested locally                                     |
| Matrix strategies                     | Yes                 | Dry-run expands the matrix                                                                                        |
| Platform-specific jobs (Windows)      | No                  | Act only supports Linux containers                                                                                |

## Simulating different contexts

To test branch-specific logic (e.g., maintenance branch validation), create an event JSON file:

```bash
# Create an event file simulating a push to the v3 branch
cat > /tmp/act-event.json << 'EOF'
{
  "ref": "refs/heads/v3",
  "repository": {
    "full_name": "oscal-compass/compliance-trestle"
  }
}
EOF

# Dry-run the deploy pipeline with the simulated event
act push -n -W .github/workflows/python-push.yml \
  --container-architecture linux/amd64 \
  -e /tmp/act-event.json
```

## CI integration

PRs that modify files under `.github/` and have the `github_actions` label will automatically run `act` dry-runs in CI via the `act-test.yml` workflow. This validates that workflow changes parse correctly before merge.
