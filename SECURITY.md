# Security Policy

## Reporting Security Vulnerabilities

For information about how to report security vulnerabilities, please see the [OSCAL Compass Community Security Policy](https://github.com/oscal-compass/community/blob/main/SECURITY.md).

## Security Features

### SSRF (Server-Side Request Forgery) Protection

Compliance-trestle implements comprehensive SSRF protection when fetching remote OSCAL content via HTTPS or SFTP. This protection uses a **two-tier defense system** to prevent malicious actors from exploiting the fetching mechanism to access internal resources or cloud metadata endpoints.

#### Tier 1: Always Blocked (Zero Tolerance)

The following address ranges and endpoints are **always blocked** regardless of configuration, as they have zero legitimate use for OSCAL content fetching:

- **Loopback addresses**: `127.0.0.0/8` (IPv4), `::1/128` (IPv6)
- **Link-local addresses**: `169.254.0.0/16` (IPv4), `fe80::/10` (IPv6)
- **Cloud metadata endpoints**:
  - `169.254.169.254` (AWS, Azure, GCP)
  - `metadata.google.internal` (GCP)
  - `metadata.azure.com` (Azure alternative)
  - `100.100.100.200` (Alibaba Cloud)

These ranges are blocked to prevent:

- Access to localhost services
- Exploitation of cloud metadata endpoints to steal credentials
- Access to link-local services

#### Tier 2: Optionally Blocked (Configurable)

RFC 1918 private IP ranges are **allowed by default** to support legitimate use cases such as private GitLab instances or internal OSCAL repositories:

- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`
- `fc00::/7` (IPv6 unique local)

**To block private IP ranges**, set the environment variable:

```bash
export TRESTLE_BLOCK_PRIVATE_IPS=true
```

When private IPs are allowed (default), trestle logs a warning when accessing them to maintain visibility.

#### Maximum Remote Object Size

Objects fetched over `https://` or `sftp://` are streamed to disk and rejected once they exceed a size limit, so a
malicious endpoint cannot exhaust memory or disk. The default limit is 1 GiB. It is a safety ceiling, not a measured
limit. To set a different limit, for example a lower one on a memory-constrained CI runner, set the environment
variable to a positive number of bytes:

```bash
export TRESTLE_MAX_REMOTE_FETCH_BYTES=104857600  # 100 MiB
```

An invalid value causes the fetch to fail rather than fall back to the default. Note that parsing an OSCAL document
needs several times its size in memory.

#### Domain Allowlist (Optional)

For additional security, you can restrict fetching to specific domains by configuring an allowed domains list. When configured, only URLs from the specified domains will be permitted.

### Local File Access

A document must never decide what trestle reads from the user's disk. A local file outside the trestle workspace may be
read only if the user (or calling program) named that file directly.

**Allowed**

1. Files inside the trestle workspace, however referenced (`trestle://…`, or a relative or absolute path that resolves
   inside it).
1. A file named directly by the user, wherever it is, for example `trestle import -f /any/path/catalog.json`, or the
   profile and leveraged SSP arguments of `trestle author ssp-generate`.
1. A file path passed by a calling program to the Python API, for example `Repository.load_and_import_model()`.
1. `https://` and `sftp://` references from any source. They are not local files and are covered by the URL protections
   above.

**Not allowed**

1. A reference found inside a document (for example a profile `imports[].href`, or the leveraged SSP href in an SSP
   inheritance markdown file) that resolves to a local file outside the workspace, whether given as an absolute path, a
   `..` relative path, or a `file:///` URI.
1. A reference that reaches outside the workspace through a symbolic link. The resolved path is checked.

To use a file that lives outside the workspace, run `trestle import` to bring it in, then refer to it as `trestle://…`.

These rules protect the confidentiality of local files. They do not verify that a permitted file is authentic or
untampered with; use signatures for that.

### Path Traversal Protection

Trestle implements multiple layers of path traversal protection:

1. **URL Path Validation**: Blocks `..` sequences in URL paths to prevent directory traversal
1. **Cache Path Validation**: Ensures cached files remain within the designated cache directory
1. **Workspace Boundary Enforcement**: Local files referenced from within documents must resolve inside the trestle workspace (see Local File Access above)
1. **Sensitive File Protection**: Blocks access to sensitive system files even when the user names a path outside the workspace:
   - `/etc/passwd`, `/etc/shadow`, `/etc/group`, `/etc/sudoers`
   - SSH keys (`.ssh/`)
   - Cloud credentials (`.aws/`, `.docker/`, `.kube/`)
   - System logs (`/var/log/`)
   - Database files (`/var/lib/mysql/`)
   - Windows system files (`C:\Windows\System32\`, credentials)
   - Process information (`/proc/self/environ`)

### Scheme Restrictions

Only HTTPS and SFTP schemes are allowed for remote URLs. HTTP, FTP, and other protocols are rejected to ensure encrypted transport.

### Port Restrictions

By default, only standard ports are allowed:

- HTTPS: port 443
- SFTP: port 22

Non-standard ports are blocked unless explicitly configured.

## Security Best Practices

When using compliance-trestle to fetch remote OSCAL content:

1. **Use HTTPS URLs** from trusted sources
1. **Enable private IP blocking** (`TRESTLE_BLOCK_PRIVATE_IPS=true`) in production environments unless you specifically need to access private repositories
1. **Lower the remote object size limit** (`TRESTLE_MAX_REMOTE_FETCH_BYTES`) on memory-constrained hosts such as CI runners, since the 1 GiB default is only a safety ceiling and parsing needs several times a document's size in memory
1. **Configure domain allowlists** when fetching from a known set of trusted domains
1. **Monitor logs** for warnings about private IP access
1. **Keep trestle updated** to receive the latest security fixes
1. **Review fetched content** before using it in production compliance workflows

## Security Testing

The SSRF and path traversal protections are comprehensively tested with 100% code coverage. Tests include:

- Blocking of all Tier 1 addresses and endpoints
- Configurable blocking of Tier 2 private ranges
- Path traversal attack vectors
- Sensitive file access attempts
- Real-world attack scenarios from security advisories

## Version History

- **v4.x**: Introduced two-tier SSRF protection system (GHSA-w76h-q7c6-jpjp fix)
- **v3.x and earlier**: Limited SSRF protection (vulnerable)

## References

- [GHSA-w76h-q7c6-jpjp](https://github.com/oscal-compass/compliance-trestle/security/advisories/GHSA-w76h-q7c6-jpjp) - SSRF vulnerability advisory
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [CWE-918: Server-Side Request Forgery (SSRF)](https://cwe.mitre.org/data/definitions/918.html)
