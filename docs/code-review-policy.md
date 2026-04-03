# Code Review Policy

This document outlines the mandatory quality assurance checks and standards for all contributions to Compliance Trestle, as required by OSPS-GV-03.02.

## Review Requirements
All Pull Requests must satisfy the following criteria before they are eligible for merging. Technical setup and legal requirements (such as DCO sign-off and license headers) are maintained in the OSCAL Compass Community CONTRIBUTING guide.

### 1. Quality Assurance
* **Code Style:** Contributions must adhere to project-specific formatting (PEP 8 via yapf/flake8).
* **Documentation:** Changes must include updated documentation following Google-style docstrings.
* **Testing:** PRs must meet the project-configured code coverage threshold. Reviewers must verify that new tests cover logic edge cases and that all CI checks pass.

### 2. Review Standards
* **Logic Verification:** Reviewers must verify that the change is functionally sound and does not introduce security vulnerabilities or logic regressions.
* **Maintainability:** Code should be reviewed for complexity; reviewers are encouraged to suggest simplifications to ensure the project remains accessible to beginners.
* **Issue Alignment:** Every PR must be linked to a tracked issue to maintain the project's audit trail for compliance.

### 3. Submission Workflow
* **Commit History:** In alignment with the [Merge details for committers](https://github.com/oscal-compass/community/blob/main/CONTRIBUTING.md#merge-details-for-committers) section of the community guide, all merges into the `develop` branch MUST be conducted via a **squash-merge**.
* **Audit Trail:** Reviewers are responsible for verifying that the final squash message provides a clear description of the functional changes to ensure a clean, searchable history for auditing.

## Security Oversight
In accordance with OSPS-GV-03.02, this policy ensures that every code change undergoes a rigorous review to maintain the security posture of the Compliance Trestle ecosystem.

