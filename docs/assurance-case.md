---
title: Assurance Case
description: >-
  A documented body of evidence providing a convincing and valid argument that
  the security requirements of compliance-trestle are adequately justified.
---

# Assurance Case

This document is the assurance case for **compliance-trestle** (also published as `trestle` on PyPI).
It provides "a documented body of evidence that provides a convincing and valid argument that a
specified set of critical claims regarding a system's properties are adequately justified for a
given application in a given environment"
([Rhodes et al., NIST IR 7608](https://www.nist.gov/publications/software-assurance-using-structured-assurance-case-models)).

---

## 1. Scope and Application Environment

Compliance-trestle is a **Python library and CLI tool** used to create, validate, transform, and
govern OSCAL compliance artifacts in a developer's local workspace or inside a CI/CD pipeline.
It is a **command-line / library tool** — there is no persistent server process, no inbound network
listener, and no multi-user session state.

**What is in scope for this assurance case:**

- The `trestle` CLI and Python API (`trestle/cli.py`, `trestle/core/repository.py`)
- Remote content fetching (`trestle/core/remote/`)
- OSCAL parsing and serialisation (`trestle/oscal/`, `trestle/core/base_model.py`)
- Jinja2 template authoring (`trestle/core/commands/author/jinja.py`)
- Cryptographic signing and verification (`trestle/core/signing.py`)
- The trestle workspace on the local filesystem

**What is explicitly out of scope:**

- The CI/CD platform (GitHub Actions, Tekton, etc.) that runs trestle
- Trestle plugin packages authored by third parties (see trust boundary B3)
- The accuracy or completeness of OSCAL compliance content written by users

---

## 2. Threat Model

### 2.1 Actors and Assets

| Actor | Description |
|---|---|
| **Operator** | A developer or compliance engineer who runs trestle commands locally or in a pipeline. Trusted. |
| **Remote OSCAL source** | A server (GitHub, private GitLab, SFTP host) that provides catalog or profile imports. Partially trusted — may be compromised or substituted. |
| **Plugin author** | An author of a `trestle_*` Python package installed into the same environment. Trusted by assumption; must be vested before installation (documented boundary). |
| **Template author** | An author of Jinja2 templates that trestle renders. Partially trusted — templates execute in a sandbox. |
| **Malicious file / URL** | A crafted OSCAL document, URL, or local file path supplied as trestle input. Untrusted. |

**Protected assets:**

- Workspace files containing OSCAL compliance artifacts
- The host filesystem (cloud credentials, SSH keys, `/etc/passwd`, etc.)
- The Python runtime process
- The integrity of signed OSCAL artifacts
- Cloud metadata endpoints and internal network services reachable from the host

### 2.2 Threat Scenarios

| ID | Threat | STRIDE category | Affected component |
|---|---|---|---|
| T1 | Malicious `import href` URL triggers SSRF to cloud metadata endpoint | Elevation of privilege | `trestle/core/remote/cache.py` |
| T2 | Crafted relative path (`../../etc/passwd`) in an OSCAL URL or local path escapes workspace | Tampering / info disclosure | `trestle/core/remote/security.py`, file utilities |
| T3 | Server-side template injection via malicious Jinja2 template | Elevation of privilege | `trestle/core/commands/author/jinja.py` |
| T4 | Tampered or substituted remote OSCAL artifact accepted without verification | Tampering / repudiation | `trestle/core/signing.py` |
| T5 | Malformed OSCAL document causes uncontrolled parsing / DoS | Denial of service | `trestle/oscal/`, `trestle/core/base_model.py` |
| T6 | Dependency with known CVE introduces exploitable weakness | Any | `pyproject.toml`, Dependabot/Snyk |
| T7 | Supply chain attack against the trestle release package itself | Tampering | PyPI publishing workflow |
| T8 | Third-party plugin loaded from `sys.path` executes arbitrary code | Elevation of privilege | `trestle/core/plugins.py` |
| T9 | Sensitive system files accessed via XML external entity or path injection in input data | Info disclosure | `defusedxml`, file utilities |

---

## 3. Trust Boundaries

Trust boundaries are the points where data or execution crosses between different levels of trust.

```
┌─────────────────────────────────────────────────────────────────────┐
│  HOST ENVIRONMENT  (operator's machine / CI runner)                 │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  TRESTLE PROCESS                                             │   │
│  │                                                              │   │
│  │  ┌──────────┐   B1   ┌────────────────────────────────────┐ │   │
│  │  │ Operator │ ──────▶│ CLI / Python API entry point       │ │   │
│  │  │ (trusted)│        │ trestle/cli.py                     │ │   │
│  │  └──────────┘        └────────────────────────────────────┘ │   │
│  │                                    │                         │   │
│  │                         B2         ▼                         │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │ Workspace (local filesystem)                         │   │   │
│  │  │  OSCAL JSON/YAML files, Markdown, DrawIO             │   │   │
│  │  │  Pydantic parse/validate on every read               │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  │                                                              │   │
│  │  B3 ─── Plugin boundary ────────────────────────────────    │   │
│  │  │  trestle_* packages loaded from sys.path               │   │   │
│  │  │  Assumed trusted; no sandbox                           │   │   │
│  │  ─────────────────────────────────────────────────────    │   │
│  │                                                              │   │
│  │  B4 ─── Template boundary ──────────────────────────────    │   │
│  │  │  Jinja2 SandboxedEnvironment                           │   │   │
│  │  ─────────────────────────────────────────────────────    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│                    B5 — Remote network boundary                     │
│       ┌──────────────────────────────────────────────────────┐      │
│       │  Remote OSCAL sources (HTTPS / SFTP)                 │      │
│       │  security.py validates URL before connection         │      │
│       └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

| Boundary | Description | Control mechanism |
|---|---|---|
| **B1** Operator → CLI | Operator supplies commands, file paths, and URLs | Argument validation; Pydantic schema enforcement on all read inputs |
| **B2** Process → Workspace | Trestle reads/writes files within the workspace directory | Path canonicalization and workspace-root enforcement in `trestle/common/file_utils.py` and `trestle/core/remote/security.py` |
| **B3** Process → Plugin | Installed `trestle_*` packages are loaded at import time | No sandbox; users MUST vet plugins before installation (documented in [Architecture](architecture.md) and [Plugin Extension Point](architecture.md#plugin-extension-point-trestlecorepluginspy)) |
| **B4** Process → Template | Jinja2 templates supplied by users or pipeline | `SandboxedEnvironment` blocks `__class__`, `__globals__`, `__subclasses__` and other dangerous attributes |
| **B5** Process → Internet | OSCAL `import href` or `trestle fetch` contacts remote server | SSRF protection in `trestle/core/remote/security.py`; HTTPS/SFTP only; blocked IP lists; optional domain allowlist |

---

## 4. Argument: Secure Design Principles Have Been Applied

The following table maps accepted secure design principles
([Saltzer & Schroeder, 1975](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html)
and their modern expansions) to concrete trestle design decisions.

| Principle | How trestle applies it | Evidence |
|---|---|---|
| **Economy of mechanism** (keep the design simple) | Trestle is a stateless CLI/library with no server process, no session management, and no privileged daemon. Each command is an isolated Python invocation. | [`trestle/cli.py`](https://github.com/oscal-compass/compliance-trestle/blob/develop/trestle/cli.py) |
| **Fail-safe defaults** | Loopback and link-local IPs are always blocked for remote fetches. Private RFC 1918 ranges are allowed by default only for legitimate intranet use, and a single env-var (`TRESTLE_BLOCK_PRIVATE_IPS=true`) tightens this to deny-all. Unknown OSCAL fields are rejected at parse time by strict Pydantic models. | [`trestle/core/remote/security.py`](https://github.com/oscal-compass/compliance-trestle/blob/develop/trestle/core/remote/security.py) |
| **Complete mediation** (check every access) | Every read of an OSCAL document from disk or network passes through the Pydantic model layer (schema validated), and every remote URL is validated against the security policy before a socket is opened. | [`trestle/core/remote/cache.py`](https://github.com/oscal-compass/compliance-trestle/blob/develop/trestle/core/remote/cache.py), `trestle/common/load_validate.py` |
| **Open design** | Source code is publicly available under Apache 2.0. Security controls are documented and transparent. | [GitHub repository](https://github.com/oscal-compass/compliance-trestle) |
| **Separation of privilege** | No single function grants full access to the workspace. Remote fetch, signing, and authoring are independent subsystems. CI/CD merges require two LGTMs from distinct reviewers. | [`docs/code-review-policy.md`](code-review-policy.md) |
| **Least privilege** | Trestle runs as the invoking user, never elevates privileges, and does not write outside the workspace directory by default. Plugin code runs in the same process but without any special OS privilege grants. | Design constraint; no `setuid`/`sudo` calls |
| **Least common mechanism** (minimize shared state) | Trestle has no shared mutable global state across commands. Each CLI invocation is a fresh process. | Architecture: stateless design |
| **Psychological acceptability** (usable security) | Security knobs have safe defaults. Private IP blocking is off-by-default (to support common private GitLab installs) with a one-line env-var to harden. A domain allowlist is available when stricter control is needed. | [`SECURITY.md`](https://github.com/oscal-compass/compliance-trestle/blob/develop/SECURITY.md) |
| **Defense in depth** | SSRF uses a two-tier blocking model (always-blocked + optionally-blocked). Path traversal uses URL-level `..` detection *and* path-canonicalization *and* workspace-root enforcement — three independent checks. | [`trestle/core/remote/security.py`](https://github.com/oscal-compass/compliance-trestle/blob/develop/trestle/core/remote/security.py) |
| **Reluctance to trust** | Remote content is cached and treated as untrusted data until schema-validated. Jinja templates execute in a `SandboxedEnvironment`. Plugins are explicitly marked as trusted-by-assumption, not trusted-by-enforcement. | Architecture documentation; `trestle/core/commands/author/jinja.py` |

---

## 5. Argument: Common Implementation Security Weaknesses Have Been Countered

The following tables map the [OWASP Top 10 (2021)](https://owasp.org/Top10/) and the
[CWE/SANS Top 25 (2024)](https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html)
to trestle mitigations.

### 5.1 OWASP Top 10 (2021)

| OWASP ID | Name | Applicability to trestle | Mitigation |
|---|---|---|---|
| **A01** | Broken Access Control | Low — no multi-user server; OS handles access control | Trestle defers to OS file permissions; workspace boundary checks in `file_utils.py` prevent escape to parent directories |
| **A02** | Cryptographic Failures | Medium — data at rest not encrypted; in-transit uses TLS | HTTPS enforced for all remote fetches (HTTP rejected); SFTP only alternative. Signing uses DSSE + RFC 8785 canonicalization + `cryptography` library (no custom crypto). Sensitive files not stored by trestle itself. |
| **A03** | Injection | High — OSCAL documents may contain crafted paths/URLs | Path traversal: multi-layer detection in `security.py`. XML injection: `defusedxml` used for all XML parsing (disables XXE). SQL injection: N/A — no database. Command injection: trestle does not shell-out user-supplied data. |
| **A04** | Insecure Design | Addressed | Secure design principles applied (§4 above); threat model documented (§2). |
| **A05** | Security Misconfiguration | Low — no server, no default credentials | No services listen by default; security defaults are safe; documented env-var overrides. |
| **A06** | Vulnerable and Outdated Components | Medium | Dependabot and Snyk (`/.snyk`) perform automated dependency scanning; SonarCloud gates all PRs; pinned or constrained versions in `pyproject.toml`; Python ≥ 3.11 required. |
| **A07** | Identification and Authentication Failures | Low — no user authentication in the tool itself | Remote fetching relies on host credentials (SSH keys, tokens) provided by the operator, not stored by trestle. |
| **A08** | Software and Data Integrity Failures | High — remote OSCAL imports | HTTPS + optional domain allowlist ensure transport integrity. `sign`/`verify` commands give consumers a mechanism to assert and check artifact integrity end-to-end. SLSA provenance attestations are published for releases. |
| **A09** | Security Logging and Monitoring Failures | Low — trestle is a CLI tool | Standard Python `logging` module; private IP accesses trigger explicit warnings; no PII logged. |
| **A10** | Server-Side Request Forgery (SSRF) | **High** — core attack surface | Fully mitigated: two-tier IP blocking (always-blocked tier: loopback, link-local, cloud metadata; configurable tier: RFC 1918); HTTPS/SFTP only; port restriction (443/22); `..` in URL path blocked; domain allowlist available. Covered by dedicated security advisory [GHSA-w76h-q7c6-jpjp](https://github.com/oscal-compass/compliance-trestle/security/advisories/GHSA-w76h-q7c6-jpjp). 100% test coverage on all SSRF controls. |

### 5.2 CWE/SANS Top 25 (2024) — applicable subset

| CWE | Name | Trestle mitigation |
|---|---|---|
| [CWE-79](https://cwe.mitre.org/data/definitions/79.html) | Improper Neutralisation of Input During Web Page Generation (XSS) | N/A — trestle generates Markdown/JSON/YAML files, not HTML served to browsers |
| [CWE-89](https://cwe.mitre.org/data/definitions/89.html) | SQL Injection | N/A — no database backend |
| [CWE-22](https://cwe.mitre.org/data/definitions/22.html) | Path Traversal | Multi-layer: `..` blocked in URL paths; cache and workspace path validation using `pathlib.Path.resolve()`; sensitive-file block-list in `security.py` |
| [CWE-78](https://cwe.mitre.org/data/definitions/78.html) | OS Command Injection | Trestle does not construct shell commands from user input. `subprocess` calls are not present in the security-sensitive path. |
| [CWE-20](https://cwe.mitre.org/data/definitions/20.html) | Improper Input Validation | All OSCAL inputs validated against strict Pydantic v2 models. URL inputs validated by `security.py` before socket open. |
| [CWE-125](https://cwe.mitre.org/data/definitions/125.html) | Out-of-bounds Read | Python's memory-safe runtime mitigates buffer overflows; `defusedxml` prevents billion-laughs and similar XML DoS attacks |
| [CWE-416](https://cwe.mitre.org/data/definitions/416.html) | Use After Free | Python GC; not applicable to CPython runtime |
| [CWE-862](https://cwe.mitre.org/data/definitions/862.html) | Missing Authorization | No server, no authorization decisions; trestle delegates to OS file permissions |
| [CWE-918](https://cwe.mitre.org/data/definitions/918.html) | Server-Side Request Forgery (SSRF) | Fully mitigated — see A10 above and [SECURITY.md](https://github.com/oscal-compass/compliance-trestle/blob/develop/SECURITY.md) |
| [CWE-94](https://cwe.mitre.org/data/definitions/94.html) | Code Injection | Jinja2 `SandboxedEnvironment` blocks access to Python internals from templates; no `eval`/`exec` on user-supplied content |
| [CWE-502](https://cwe.mitre.org/data/definitions/502.html) | Deserialization of Untrusted Data | OSCAL JSON/YAML is parsed by Pydantic (no `pickle`); `defusedxml` for XML; no untrusted serialisation formats accepted |
| [CWE-611](https://cwe.mitre.org/data/definitions/611.html) | XML External Entity (XXE) | All XML parsing uses `defusedxml`, which disables external entity expansion by default |
| [CWE-200](https://cwe.mitre.org/data/definitions/200.html) | Exposure of Sensitive Information | Sensitive system paths (SSH keys, cloud credentials, `/etc/passwd`, etc.) are in the block-list in `security.py`; no credentials stored or logged by trestle |
| [CWE-276](https://cwe.mitre.org/data/definitions/276.html) | Incorrect Default Permissions | Trestle does not set file permissions; relies on OS umask; no world-writable files created |
| [CWE-306](https://cwe.mitre.org/data/definitions/306.html) | Missing Authentication for Critical Function | No authentication required because trestle is a local CLI, not a network service; operator identity established by OS |
| [CWE-77](https://cwe.mitre.org/data/definitions/77.html) | Command Injection | User-supplied data is never passed to shell or `subprocess` in the fetch/parse path |

---

## 6. Supporting Evidence

| Category | Evidence |
|---|---|
| **Automated testing** | ≥ 96 % code coverage enforced as a CI gate; SSRF and path traversal tests achieve 100 % branch coverage on `trestle/core/remote/security.py` |
| **Static analysis** | SonarCloud SAST scans every PR; blocking gate — no merge with open findings above threshold |
| **Dependency scanning** | Snyk (`/.snyk`) and GitHub Dependabot monitor all runtime and dev dependencies for known CVEs |
| **Peer review** | Every PR requires two LGTMs, at least one from a Code Owner, per [`docs/code-review-policy.md`](code-review-policy.md) |
| **OpenSSF Best Practices** | Project carries a passing OpenSSF Best Practices badge ([badge](https://www.bestpractices.dev/projects/9408)) |
| **OpenSSF Scorecard** | Scorecard badge tracks branch protection, token permissions, binary artifacts, and other supply-chain hygiene ([scorecard](https://scorecard.dev/viewer/?uri=github.com/oscal-compass/compliance-trestle)) |
| **SLSA provenance** | Release distributions include SLSA build provenance attestations published via PyPI trusted publishing |
| **Vulnerability disclosure** | Security advisories published via GitHub Security Advisories; historical fix for [GHSA-w76h-q7c6-jpjp](https://github.com/oscal-compass/compliance-trestle/security/advisories/GHSA-w76h-q7c6-jpjp) demonstrates a functioning disclosure and remediation process |
| **Architecture documentation** | [`docs/architecture.md`](architecture.md) documents component structure and Security Requirements & Guarantees section |
| **Security documentation** | [`SECURITY.md`](https://github.com/oscal-compass/compliance-trestle/blob/develop/SECURITY.md) documents SSRF protection tiers, path traversal controls, and scheme/port restrictions |

---

## 7. Residual Risks and Accepted Limitations

The following risks are **accepted** rather than mitigated, with rationale:

| Residual risk | Rationale for acceptance |
|---|---|
| **Third-party plugins run unsandboxed** (B3) | Python does not provide a practical in-process code sandbox. The documented mitigation is operator vetting. This is the same trust model applied to any installed Python package. |
| **Workspace files are not encrypted at rest** | Trestle is a developer tool; encryption at rest is a host OS / filesystem responsibility. Users operating in high-sensitivity environments should use full-disk encryption or encrypted filesystems. |
| **No semantic validation of compliance content** | Trestle validates OSCAL *schema* correctness, not the *adequacy* of the compliance policies written in the documents. This is out of scope for a structural tooling library. |
| **Private RFC 1918 addresses allowed by default** | Many legitimate users host private GitLab instances or internal OSCAL repositories on RFC 1918 addresses. Blocking these by default would break common workflows. The `TRESTLE_BLOCK_PRIVATE_IPS=true` opt-in is documented and recommended for production CI environments. |

---

## 8. References

- [NIST IR 7608 — Software Assurance Using Structured Assurance Case Models](https://www.nist.gov/publications/software-assurance-using-structured-assurance-case-models)
- [Saltzer & Schroeder, 1975 — The Protection of Information in Computer Systems](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html)
- [OWASP Top 10 (2021)](https://owasp.org/Top10/)
- [CWE/SANS Top 25 (2024)](https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [GHSA-w76h-q7c6-jpjp — SSRF vulnerability advisory](https://github.com/oscal-compass/compliance-trestle/security/advisories/GHSA-w76h-q7c6-jpjp)
- [SECURITY.md](https://github.com/oscal-compass/compliance-trestle/blob/develop/SECURITY.md) — trestle security features and best practices
- [Architecture](architecture.md) — component map, data flows, security guarantees
- [Code Review Policy](code-review-policy.md)
- [OpenSSF Best Practices badge](https://www.bestpractices.dev/projects/9408)
- [OpenSSF Scorecard](https://scorecard.dev/viewer/?uri=github.com/oscal-compass/compliance-trestle)
- [BadgeApp assurance case (reference example)](https://github.com/coreinfrastructure/best-practices-badge/blob/main/docs/assurance-case.md)
