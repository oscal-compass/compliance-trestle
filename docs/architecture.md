---
title: Architecture
description: High-level architecture of compliance-trestle — major components, their relationships, and key design properties.
---

# Architecture

This page describes the high-level architecture of compliance-trestle: its major components, the relationships among them, and the key properties of those relationships.

## Overview

Trestle is a Python application and library built around three concerns:

1. **OSCAL document management** — create, split, merge, validate, and assemble OSCAL artifacts stored in a structured workspace on disk.
1. **Format transformation** — convert third-party compliance data (XCCDF, Tanium, CIS XLSX, CSV, …) into OSCAL.
1. **Compliance content authoring** — generate and govern human-editable Markdown and DrawIO representations of OSCAL objects, and re-assemble them back into OSCAL.

All three concerns are exposed both as a **CLI** (`trestle <command>`) and as a **Python API** (via `trestle.core.repository` and the OSCAL object model in `trestle.oscal`).

______________________________________________________________________

## Component Map

```
┌──────────────────────────────────────────────────────────────────┐
│  Plugin packages  (any installed trestle_* package)             │
│  trestle/core/plugins.py scans sys.path at import time          │
└──────┬──────────────────────────────────────────────────────────┘
       │ injects CommandBase subclasses into Trestle.subcommands
       │ (cli.py class body, runs once at module import)
┌──────▼───────────────────────────────────────────────────────────┐
│                         Entry Points                            │
│   trestle CLI  (trestle/cli.py)                                 │
│   Python API   (trestle/core/repository.py)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │ dispatches to
┌────────────────────────▼────────────────────────────────────────┐
│                     Command Layer                               │
│   trestle/core/commands/                                        │
│   ┌──────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│   │ author/      │  │ split /  │  │ validate │  │ sign /   │  │
│   │ (catalog,    │  │ merge /  │  │ assemble │  │ verify   │  │
│   │  profile,    │  │ import   │  │ create   │  │ manifest │  │
│   │  ssp,        │  │ href     │  │ remove   │  └──────────┘  │
│   │  component)  │  │ replicate│  │ describe │                 │
│   └──────┬───────┘  └────┬─────┘  └────┬─────┘                │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  task  (trestle/core/commands/task.py)                  │  │
│   │  scans trestle/tasks/ for TaskBase subclasses at        │  │
│   │  runtime; invokes execute() → TransformerBase.transform()│  │
│   │  trestle/tasks/   trestle/transforms/                   │  │
│   └──────────────────────────┬──────────────────────────────┘  │
└──────────────────────────────│──────────────────────────────────┘
           │               │             │  all use          │
┌──────────▼───────────────▼─────────────▼────────────────────▼──┐
│                      Core Services                              │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │ Catalog API      │  │ Profile Resolver │  │  Validator    │  │
│  │ trestle/core/    │  │ trestle/core/    │  │  Framework    │  │
│  │ catalog/         │  │ profile_resolver │  │  trestle/core/│  │
│  │                  │  │ + resolver/      │  │  validator*   │  │
│  └────────┬─────────┘  └────────┬─────────┘  └───────┬───────┘  │
│  ┌────────┴─────────────────────┴──────────────┐      │         │
│  │          Markdown / DrawIO Authoring         │      │         │
│  │   trestle/core/control_{reader,writer}       │      │         │
│  │   trestle/core/markdown/   trestle/core/jinja│      │         │
│  │   trestle/core/draw_io.py                    │      │         │
│  └──────────────────────────────────────────────┘      │         │
│  ┌─────────────────────────────────────────────────────┴───────┐ │
│  │                  Signing & Canonicalization                  │ │
│  │   trestle/core/signing.py   trestle/core/canonicalization.py│ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │ reads/writes
┌──────────────────────────────▼──────────────────────────────────┐
│                      OSCAL Object Model                         │
│   trestle/oscal/   (auto-generated Pydantic v2 classes)         │
│   catalog · profile · ssp · component · assessment_plan         │
│   assessment_results · poam · common                            │
│   Base: trestle/core/base_model.py  (OscalBaseModel)            │
└──────────────────────────────┬──────────────────────────────────┘
                               │ serialises to/from
┌──────────────────────────────▼──────────────────────────────────┐
│              Workspace & Remote I/O                             │
│   trestle/common/  (file_utils, model_utils, load_validate)     │
│   trestle/core/remote/cache.py  (HTTP · HTTPS · SFTP · local)  │
└──────────────────────────────────────────────────────────────────┘
```

______________________________________________________________________

## Components

### Entry Points

| Component  | Location                                                                                                                    | Role                                                                                                                                                                                                        |
| ---------- | --------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CLI        | [`trestle/cli.py`](https://github.com/oscal-compass/compliance-trestle/blob/develop/trestle/cli.py)                         | `trestle` console script entry point. Instantiates the `Trestle` root command, which registers all sub-commands and dispatches argument parsing via the [ilcli](https://github.com/cloudant/ilcli) library. |
| Python API | [`trestle/core/repository.py`](https://github.com/oscal-compass/compliance-trestle/blob/develop/trestle/core/repository.py) | `ManagedOSCAL`, `Repository`, and `AgileAuthoring` (authoring-specific extension of `Repository`) provide programmatic access to the same operations as the CLI for use by downstream tools and scripts.    |

### Command Layer (`trestle/core/commands/`)

Each sub-command is a class extending `CommandBase` (or `CommandPlusDocs` for commands needing a trestle workspace root). Commands are grouped into:

| Group                     | Commands                                                                                                                                | Purpose                                                                                                                |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Workspace management**  | `init`, `create`, `import`, `split`, `merge`, `replicate`, `remove`, `href`                                                             | Create and maintain a trestle workspace; manipulate OSCAL document trees on disk.                                      |
| **Validation & assembly** | `validate`, `assemble`, `partial-object-validate`, `describe`, `canonicalize`                                                           | Validate OSCAL schemas and cross-references; assemble split files back into single documents.                          |
| **Authoring**             | `author catalog`, `author profile`, `author ssp`, `author component`, `author jinja`, `author docs`, `author folders`, `author headers` | Generate Markdown/DrawIO representations of OSCAL objects, govern their structure, and re-assemble them back to OSCAL. |
| **Task execution**        | `task`                                                                                                                                  | Invoke a named `TaskBase` implementation (from `trestle/tasks/`) to transform third-party data into OSCAL.             |
| **Signing**               | `sign`, `sign-manifest`, `verify`, `verify-manifest`                                                                                    | Produce and verify detached DSSE/in-toto provenance signatures over OSCAL artifacts and manifest files.                |

### Core Services

**Catalog API** (`trestle/core/catalog/`)
: `CatalogInterface`, `CatalogReader`, `CatalogWriter`, and `CatalogMerger` form the primary read/write/merge layer for OSCAL catalogs. The `author` commands delegate all catalog-level operations here.

**Profile Resolver** (`trestle/core/profile_resolver.py`, `trestle/core/resolver/`)
: Resolves a profile against its source catalog(s) — applying imports, parameter modifications, and additions/removals — to produce a resolved catalog. Built as composable `Pipeline` / `Filter` stages: for each imported source a `[Import, Prune]` pipeline is built, and a final `[Merge, Modify]` pipeline is applied across all results.

**Validator Framework** (`trestle/core/validator.py`, `trestle/core/validator_factory.py`)
: `Validator` is an abstract base class. Concrete validators (`CatalogValidator`, `DuplicatesValidator`, `LinksValidator`, `RefsValidator`, `RuleParametersValidator`) are registered with `ValidatorFactory` at module load time and selected by key when the `validate` command runs.

**Markdown & Jinja Authoring** (`trestle/core/control_{reader,writer}.py`, `trestle/core/markdown/`, `trestle/core/jinja/`)
: Converts OSCAL control structures to structured Markdown (with YAML headers) and back. The Jinja subsystem provides template-driven generation of arbitrary compliance documents from OSCAL data. `DrawIO` support (`trestle/core/draw_io.py`) handles diagram metadata.

**Signing & Canonicalization** (`trestle/core/signing.py`, `trestle/core/canonicalization.py`)
: Canonicalizes JSON artifacts using RFC 8785 before signing. Produces and verifies DSSE envelopes with in-toto predicates using `securesystemslib`.

### OSCAL Object Model (`trestle/oscal/`)

Auto-generated Pydantic v2 classes (via `scripts/gen_oscal.py` from NIST JSON schemas) representing every OSCAL layer: `catalog`, `profile`, `component`, `ssp`, `assessment_plan`, `assessment_results`, `poam`, `mapping`, and `common`. All classes extend `OscalBaseModel` ([`trestle/core/base_model.py`](https://github.com/oscal-compass/compliance-trestle/blob/develop/trestle/core/base_model.py)), which adds JSON/YAML serialization, field aliasing, and trestle-workspace-aware I/O.

### Workspace & Remote I/O (`trestle/common/`, `trestle/core/remote/`)

`trestle/common/` provides shared utilities: constants, error types, file and model utilities, and load/validate helpers used throughout the codebase.

`trestle/core/remote/cache.py` provides a `FetcherBase` hierarchy (`LocalFetcher`, `HTTPSFetcher`, `SFTPFetcher`) that resolves URI references in OSCAL documents — including remote catalog imports — to local cached copies. Security validation (`trestle/core/remote/security.py`) blocks private IP ranges and enforces HTTPS.

### Transform & Task Pipeline (`trestle/transforms/`, `trestle/tasks/`)

These two packages handle **inbound** conversion of non-OSCAL data and sit within the Command Layer — `TaskCmd` (`trestle/core/commands/task.py`) is what wires them in:

- `TransformerBase` / `TransformerFactory` (`trestle/transforms/`) — abstract interface for converting a raw blob into an `OscalBaseModel`. Used by a subset of tasks that process binary/XML formats (XCCDF, OSCO, Tanium). Most tasks (CSV, XLSX, CIS) write OSCAL directly without going through `TransformerBase`.
- `TaskBase` (`trestle/tasks/`) — abstract interface for a named, configurable task. Each task class encapsulates a full source-to-OSCAL pipeline (e.g. `CsvToOscalComponentDefinition`, `CisXlsxToOscalCatalog`). `TaskCmd` discovers all `TaskBase` subclasses, instantiates the requested one, calls `simulate()` then `execute()`, and the task writes its output through the OSCAL Object Model and workspace I/O layers like every other command.

### Plugin Extension Point (`trestle/core/plugins.py`)

When `trestle/cli.py` is first imported, its `Trestle` class body calls `discovered_plugins('commands')`. At that point `plugins.py` scans all installed packages on `sys.path` for names beginning with `trestle_`, imports each one's `commands/` sub-modules, and yields every `CommandBase` subclass found. Those classes are appended directly to `Trestle.subcommands` — making them indistinguishable from built-in commands at dispatch time.

Note that this mechanism injects **commands only**. Plugin tasks are not currently auto-discovered by `TaskCmd._build_task_index()`, which scans only the built-in `trestle/tasks/` package.

______________________________________________________________________

## Key Design Properties

**Workspace-centric storage** — a trestle workspace is a directory tree with a `.trestle/` marker. OSCAL documents may be stored as single files or split into sub-directories following the document's object hierarchy. All commands operate relative to this root.

**Schema-enforced I/O** — every read and write of an OSCAL document passes through the Pydantic model layer, guaranteeing schema validity at the boundary between disk and memory.

**Composable pipelines** — the `Pipeline` / `Filter` pattern (`trestle/core/pipeline.py`) is used wherever a multi-stage transformation is needed (profile resolution, OSCAL assembly). Stages are independently testable and reusable.

**Separation of concerns between CLI and API** — commands delegate business logic to core service classes (`CatalogInterface`, `ProfileResolver`, etc.) rather than implementing it inline. `repository.py` exposes the same services to Python callers without going through the CLI argument layer.

**Extensibility via plugins** — the `trestle_*` package convention means the core project does not need to depend on or bundle every possible third-party integration.

______________________________________________________________________

## Security Requirements & Guarantees

This section documents what users can and cannot expect regarding security from the software produced by the project (its security requirements and boundaries).

### What Users CAN Expect (Security Guarantees & Capabilities)

- **Input Validation & Schema Enforcement:**
  - All OSCAL models are parsed, validated, and serialized using strict Pydantic models derived from official NIST OSCAL schemas.
  - Malformed documents, invalid types, or unexpected data structures are rejected at parse time.
- **SSRF & Remote Resource Protection:**
  - Remote resource retrieval (`trestle/core/remote/cache.py` and `trestle/core/remote/security.py`) enforces HTTPS/SFTP and includes Server-Side Request Forgery (SSRF) protections.
  - Cloud metadata service endpoints (e.g., `169.254.169.254`, `metadata.google.internal`) and loopback addresses are blocked unconditionally during remote fetches.
  - Optional blocking of RFC 1918 private IP address ranges can be configured via the `TRESTLE_BLOCK_PRIVATE_IPS` environment variable.
- **Template Sandbox Execution:**
  - Jinja2 authoring templates (`trestle/core/commands/author/jinja.py`) execute within a `SandboxedEnvironment` to restrict access to dangerous Python attributes (`__class__`, `__globals__`, `__subclasses__`) and mitigate server-side template injection (SSTI) risks.
- **Cryptographic Provenance & Integrity:**
  - Built-in signing and verification commands (`sign`, `verify`, `sign-manifest`, `verify-manifest`) use RFC 8785 JSON canonicalization and standard in-toto / DSSE signatures via `securesystemslib` and standard cryptography libraries to establish tamper-evident document provenance.
- **Supply Chain Integrity:**
  - Release distributions include SLSA build provenance attestations and PyPI trusted publishing.

### What Users CANNOT Expect (Security Boundaries & User Responsibilities)

- **Execution Isolation for Third-Party Plugins:**
  - Trestle discovers and loads installed `trestle_*` command plugins from `sys.path`. Trestle does not sandbox or isolate third-party Python plugin code; users are responsible for ensuring installed plugins are trusted.
- **Protection Against Malicious Local Files / Filesystem Attacks:**
  - Trestle runs with the permissions of the invoking user and assumes the host environment and local workspace directory are secure.
- **Automatic Data Encryption at Rest:**
  - Trestle does not encrypt stored OSCAL models or workspace files at rest; encryption must be provided by the underlying operating system or filesystem.
- **Verification of Semantic Content Accuracy:**
  - While Trestle validates schema structure and cross-reference integrity, it cannot verify the accuracy, adequacy, or legal validity of the compliance content, policies, or controls written within documents.
- **Network-Level Access Controls:**
  - Outside of URL validation during remote fetches, Trestle does not manage network transport security or proxy configurations, relying instead on host environment settings.
