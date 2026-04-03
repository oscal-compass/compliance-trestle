# Code Review Policy

This document outlines the mandatory quality assurance checks and standards for all contributions to Compliance Trestle, as required by OSPS-GV-03.02.

## Review Requirements

All Pull Requests must satisfy the following criteria before they are eligible for merging. Technical setup and legal requirements (such as DCO sign-off and license headers) are maintained in the [OSCAL Compass Community CONTRIBUTING guide](https://github.com/oscal-compass/community/blob/main/CONTRIBUTING.md).

### 1. Quality Assurance

* **Code style:** Contributions must adhere to project-specific formatting (PEP 8 via yapf/flake8).
* **Documentation:** Changes must include updated documentation following Google-style docstrings.
* **Testing:** PRs must meet the project-configured code coverage threshold of **96%**. Reviewers must verify that new tests cover logic edge cases.
* **CI gates:** All automated checks must pass, including the **SonarCloud** scan for code quality and security vulnerabilities. SonarCloud is a mandatory gate — no PR may be merged while SonarCloud checks are failing.

### 2. Review Standards

* **Reviewer count:** In accordance with the project's governance, every PR requires at least **two (2) LGTMs** (Looks Good To Me) before merging. At least one of these reviewers must be a designated **Code Owner**.
* **Logic verification:** Reviewers must verify that the change is functionally sound and does not introduce security vulnerabilities or logic regressions.
* **Maintainability:** Code should be reviewed for complexity; reviewers are encouraged to suggest simplifications to promote long-term maintainability and readability.
* **Issue alignment:** Every PR must be linked to a tracked issue to maintain the project's audit trail for compliance.

### 3. Submission Workflow

* **Commit history:** In alignment with the community guide, all merges into the `develop` branch MUST be conducted via a **squash-merge**.
* **Audit trail:** Reviewers are responsible for verifying that the final squash message provides a clear description of the functional changes to ensure a clean, searchable history for auditing.

## Security Oversight

In accordance with OSPS-GV-03.02, this policy ensures that every code change undergoes a rigorous review to maintain the security posture of the Compliance Trestle ecosystem.
