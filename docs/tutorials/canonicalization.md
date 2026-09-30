---
title: Canonicalizing JSON documents
description: Canonicalizing JSON documents with RFC 8785
---

# Canonicalizing JSON documents

Trestle can canonicalize JSON documents using RFC 8785.

Canonical JSON is useful when the same logical JSON document needs to produce the same bytes every time. This is important for reproducible digests and later signing workflows.

The canonicalization flow is:

```text
JSON document -> strict JSON parsing -> RFC 8785 canonical JSON bytes
```

The command reads the raw JSON document directly. It does not load the document through the OSCAL object models, so it does not change the artifact before canonicalization.

This workflow can handle arbitrary valid JSON documents with a `.json` extension. The input does not need to be an OSCAL model.

## Canonicalize to a file

Use `trestle canonicalize` with an input JSON file and an output path:

```bash
trestle canonicalize \
  -f catalog.json \
  -o catalog.canonical.json
```

The original JSON file is not modified. The output file contains the RFC 8785 canonical JSON bytes. The recommended output extension is `.canonical.json`.

## Canonicalize to stdout

If `--output` is omitted, trestle writes the canonical JSON bytes to stdout:

```bash
trestle canonicalize -f catalog.json
```

This can be useful for shell pipelines that compute or compare digests.

## JSON requirements

The command is JSON-only.

Trestle rejects ambiguous or unsupported JSON inputs before canonicalization, including:

- non-`.json` input paths
- duplicate object keys
- non-finite JSON constants such as `NaN` and `Infinity`
