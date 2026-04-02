# OSCAL Document Signing Tutorial

This tutorial explains how to cryptographically sign and verify OSCAL JSON
documents using the `trestle sign` and `trestle verify` commands.

______________________________________________________________________

## Why sign OSCAL documents?

OSCAL documents (catalogs, profiles, SSPs, assessment results, etc.) describe
sensitive compliance posture.  Without signatures, there is no way to prove
that a document:

- has not been **tampered with** since it was produced, or
- was authored by a **trusted party** (a specific CI pipeline, an assessment
  tool, or a named reviewer).

Signing closes this gap by attaching a cryptographic proof to each artifact
before it is published, exported, or stored.  This aligns with:

- NIST SP 800-53 / 800-92 provenance expectations
- Executive Order 14028 software supply-chain guidance (SSDF)
- SLSA provenance level requirements

______________________________________________________________________

## Key concepts

| Concept              | Description                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------------ |
| Canonicalization     | Stable, reproducible byte representation of a JSON document (RFC 8785 / JCS).                                |
| Detached signature   | The signature lives in a separate `.sig` file—the OSCAL document itself is never modified.                   |
| Signature envelope   | A JSON file containing the document digest, the algorithm, the base64url signature, and provenance metadata. |
| Supported algorithms | `ecdsa-p256-sha256` (recommended) and `rsa-pss-sha256`.                                                      |

______________________________________________________________________

## Prerequisites

Install trestle with its default dependencies (the `cryptography` library is
already included):

```bash
pip install compliance-trestle
```

______________________________________________________________________

## Step 1 — Generate a test key pair

For experiments and CI pipelines you can generate an ECDSA P-256 key pair
directly from Python:

```python
from trestle.core.oscal_sign import generate_keypair, ALG_ECDSA_P256_SHA256

private_pem, public_pem = generate_keypair(ALG_ECDSA_P256_SHA256)

with open("private.pem", "wb") as f:
    f.write(private_pem)

with open("public.pem", "wb") as f:
    f.write(public_pem)
```

> **Production note:** In production environments, private keys should be
> stored in a dedicated key-management system (HSM, KMS, HashiCorp Vault, etc.)
> and never written to disk as plain-text PEM files.

You can also generate keys with OpenSSL:

```bash
# ECDSA P-256
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out private.pem
openssl pkey -in private.pem -pubout -out public.pem

# RSA-PSS (2048-bit)
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out rsa_private.pem
openssl pkey -in rsa_private.pem -pubout -out rsa_public.pem
```

______________________________________________________________________

## Step 2 — Sign an OSCAL document

```bash
trestle sign -f assessment-results.json -k private.pem
```

This produces `assessment-results.json.sig` in the same directory.  The
original OSCAL file is **not modified**.

```
SUCCESS: Signature written to assessment-results.json.sig
```

### Options

| Flag              | Description                                                   |
| ----------------- | ------------------------------------------------------------- |
| `-f` / `--file`   | Path to the OSCAL JSON file to sign (**required**).           |
| `-k` / `--key`    | Path to the PEM private key (**required**).                   |
| `-o` / `--output` | Custom output path for the `.sig` file.                       |
| `--signer`        | Optional human-readable signer identity embedded in metadata. |

```bash
# Custom output path and signer identity
trestle sign -f ssp.json -k private.pem -o ssp.json.sig --signer "ci-pipeline@org.example"
```

______________________________________________________________________

## Step 3 — Inspect the signature envelope

The `.sig` file is plain JSON and can be inspected directly:

```json
{
  "payload_digest": "sha256:3a1f...",
  "signature_algorithm": "ecdsa-p256-sha256",
  "signature": "MEUCIQD...",
  "metadata": {
    "tool": "compliance-trestle",
    "tool_version": "3.12.0",
    "oscal_model": "assessment-results",
    "signed_file": "assessment-results.json",
    "signed_at": "2026-03-08T12:00:00Z",
    "signer": "ci-pipeline@org.example"
  }
}
```

______________________________________________________________________

## Step 4 — Verify a signed document

```bash
trestle verify -f assessment-results.json -k public.pem
```

On success:

```
SUCCESS: Signature verification PASSED.
  Tool        : compliance-trestle 3.12.0
  OSCAL model : assessment-results
  Signed at   : 2026-03-08T12:00:00Z
  Signer      : ci-pipeline@org.example
```

On failure (tampered document):

```
FAILED: Signature verification did not pass: Digest mismatch — the OSCAL
document has been modified since it was signed.
  Recorded digest : sha256:3a1f...
  Current digest  : sha256:9q8z...
```

### Options

| Flag            | Description                                           |
| --------------- | ----------------------------------------------------- |
| `-f` / `--file` | Path to the OSCAL JSON file to verify (**required**). |
| `-k` / `--key`  | Path to the PEM public key (**required**).            |
| `-s` / `--sig`  | Path to the `.sig` file.  Defaults to `<file>.sig`.   |

```bash
# Explicit signature file
trestle verify -f assessment-results.json -k public.pem -s assessment-results.json.sig
```

______________________________________________________________________

## Step 5 — Using signing in a CI pipeline

A typical CI job that generates and signs an OSCAL artifact:

```yaml
# GitHub Actions example
  - name: Generate OSCAL assessment results
    run: trestle task my-assessment-task

  - name: Sign assessment results
    run: |
      trestle sign \
        -f assessment-results/my-assessment/assessment-results.json \
        -k ${{ secrets.SIGNING_PRIVATE_KEY_PATH }} \
        --signer "github-actions@${{ github.repository }}"

  - name: Upload artifacts (OSCAL + signature)
    uses: actions/upload-artifact@v4
    with:
      name: assessment-artifacts
      path: |
        assessment-results/my-assessment/assessment-results.json
        assessment-results/my-assessment/assessment-results.json.sig
```

A downstream consumer can then verify:

```bash
trestle verify \
  -f assessment-results.json \
  -k ci_public.pem
```

______________________________________________________________________

## Canonicalization details

Before signing, trestle canonicalizes the JSON document to ensure that
*logically identical* documents always produce the *same hash*, regardless of
key insertion order or whitespace differences.

The canonicalization algorithm (following RFC 8785 / JCS principles):

1. Parse the JSON document into a Python dict.
1. Recursively **sort all object keys** lexicographically.
1. Serialize with **no insignificant whitespace** (`separators=(',', ':')`).
1. Encode the result as **UTF-8**.

Example:

```python
from trestle.core.oscal_sign import canonicalize_json

# These two dicts are logically identical.
a = {"z": 1, "a": 2}
b = {"a": 2, "z": 1}

assert canonicalize_json(a) == canonicalize_json(b)  # True
# Both produce: b'{"a":2,"z":1}'
```

______________________________________________________________________

## Python API

You can also use the signing utilities directly from Python:

```python
import pathlib
from trestle.core.oscal_sign import sign_oscal_file, verify_oscal_file

# Sign
sig_path = sign_oscal_file(
    oscal_path=pathlib.Path("catalog.json"),
    key_path=pathlib.Path("private.pem"),
    signer="my-tool-v1.0",
)
print(f"Signature written to: {sig_path}")

# Verify
metadata = verify_oscal_file(
    oscal_path=pathlib.Path("catalog.json"),
    key_path=pathlib.Path("public.pem"),
)
print(f"Signed at: {metadata['signed_at']}")
```

`verify_oscal_file` raises `trestle.common.err.TrestleError` on any failure,
making it easy to integrate into validation pipelines:

```python
from trestle.common.err import TrestleError

try:
    verify_oscal_file(oscal_path, public_key_path)
    print("Artifact is authentic and untampered.")
except TrestleError as e:
    print(f"Verification failed: {e}")
    raise SystemExit(1)
```

______________________________________________________________________

## Security considerations

- **Key protection:** Keep private keys out of source control.  Use secrets
  management (Vault, KMS, GitHub Secrets) for CI pipelines.
- **Key rotation:** When you rotate a signing key, re-sign existing artifacts
  or maintain a record of previously-trusted public keys for historical
  verification.
- **Signature expiry:** Consider adding organizational policy to re-sign
  artifacts that are older than a defined window (e.g. 90 days).
- **Algorithm choice:** ECDSA P-256 (`ecdsa-p256-sha256`) is the recommended
  algorithm—compact signatures, strong security, widely supported.

______________________________________________________________________

## Frequently asked questions

**Q: Does signing change the OSCAL document?**\
A: No.  The signature is always stored in a separate `.sig` file.  The OSCAL
document itself is never modified.

**Q: Can I sign XML or YAML OSCAL documents?**\
A: JSON is the only format supported in this release.  XML canonicalization
(C14N) and YAML-to-JSON normalization are planned for a future release.

**Q: What happens if I pretty-print the JSON after signing?**\
A: Changing whitespace changes the raw bytes.  Trestle canonicalizes before
hashing, so only logical content changes—not whitespace—will break
verification.

**Q: Can I embed signature data inside the OSCAL document?**\
A: Not currently.  Detached signatures are the preferred model because they
keep OSCAL documents schema-valid and format-agnostic.
