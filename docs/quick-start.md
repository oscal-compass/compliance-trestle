---
title: Quick Start
description: Get up and running with compliance-trestle in under five minutes — install, initialise a workspace, and import your first OSCAL catalog.
---

# Quick Start

Get up and running with `trestle` in a few minutes.  
By the end of this page you will have trestle installed, a workspace initialised, and a real NIST OSCAL catalog imported and validated.

## Prerequisites

- Python **3.11 – 3.14** installed ([download](https://www.python.org/downloads/))
- `pip` 19 or later

## 1 — Install trestle

Create an isolated virtual environment and install trestle from PyPI:

```bash
python -m venv venv.trestle
source venv.trestle/bin/activate          # Windows: venv.trestle\Scripts\activate
pip install compliance-trestle
```

Confirm the installation:

```bash
trestle version
```

Expected output (version numbers may differ):

```
Trestle version v5.0.0 based on OSCAL version 1.2.1
```

## 2 — Initialise a workspace

A *trestle workspace* is a directory that trestle manages for you. Every trestle command must be run from inside one.

```bash
mkdir my-trestle-workspace
cd my-trestle-workspace
trestle init
```

Expected output:

```
Initialized trestle project successfully in .../my-trestle-workspace
```

The workspace now contains the standard OSCAL directory layout (catalogs, profiles, component-definitions, …).

## 3 — Import an OSCAL catalog

Import the NIST SP 800-53 Rev 5 **Moderate Impact Baseline** catalog directly from the NIST OSCAL GitHub repository.
This is a self-contained, resolved catalog containing the 177 controls required for a Moderate-impact system — a good starting point for most compliance work.

```bash
trestle import \
  -f https://raw.githubusercontent.com/usnistgov/oscal-content/master/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_MODERATE-baseline-resolved-profile_catalog.json \
  -o nist-800-53-r5-moderate
```

Trestle fetches the file, validates it against the OSCAL schema, and stores it at:

```
my-trestle-workspace/catalogs/nist-800-53-r5-moderate/catalog.json
```

## 4 — Validate the catalog

Use `-f` to validate a specific file:

```bash
trestle validate -f catalogs/nist-800-53-r5-moderate/catalog.json
```

Or use `-t` to validate **all** catalogs in the workspace by type:

```bash
trestle validate -t catalog
```

Expected output:

```
VALID: Model .../catalogs/nist-800-53-r5-moderate/catalog.json passed the Validator ...
```

The catalog is ready to use.

## 5 — Explore the catalog structure

Get a high-level description of the imported catalog:

```bash
trestle describe -f catalogs/nist-800-53-r5-moderate/catalog.json
```

Expected output:

```
Model file .../catalog.json is of type catalog.Catalog and contains:
    uuid: ...
    metadata: common.Metadata
    params: None
    controls: None
    groups: list of 18 items of type catalog.Group2
    back_matter: common.BackMatter
```

## What's next?

| Goal | Resource |
|------|----------|
| Learn to split large OSCAL files into editable pieces | [Introduction to trestle workflows](tutorials/introduction_to_trestle.md) |
| Author SSPs, profiles, and component definitions | [Trestle authoring tutorials](tutorials/Trestle_authoring/ssp_profile_catalog_authoring.md) |
| Transform spreadsheets and other formats into OSCAL | [Transformer tasks](tutorials/Transformers_and_Tasks/OCP4_CIS_profile_to_oscal_catalog.md) |
| Full CLI reference | [CLI documentation](tutorials/cli.md) |
| Full installation guide | [Installation](installation.md) |

---

*Having trouble? Open an issue on [GitHub](https://github.com/oscal-compass/compliance-trestle/issues) or join the community — details in the [community README](https://github.com/oscal-compass/community/blob/main/README.md).*
