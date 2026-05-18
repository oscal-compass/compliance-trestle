# Security Policy

<<<<<<< HEAD
## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 3.x.x   | :white_check_mark: |
| 2.x.x   | :white_check_mark: |
| \< 2.0  | :x:                |

## Reporting a Vulnerability

The compliance-trestle team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to the maintainers listed in [MAINTAINERS.md](MAINTAINERS.md).

Include the following information in your report:

- Type of vulnerability (e.g., SSRF, path traversal, injection, etc.)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 3 business days
- **Assessment**: We will assess the vulnerability and determine its severity and impact
- **Fix Development**: We will work on a fix and coordinate with you on disclosure timing
- **Disclosure**: Once a fix is available, we will:
  - Release a security advisory
  - Credit you for the discovery (unless you prefer to remain anonymous)
  - Release patched versions

### Security Update Process

1. Security vulnerability is reported privately
1. Maintainers confirm the vulnerability
1. Fix is developed and tested
1. Security advisory is drafted
1. Patched version is released
1. Security advisory is published
1. Users are notified through release notes and security channels

## Security Features

Compliance-trestle includes several security features to protect against common vulnerabilities:

### SSRF Protection (CWE-918)

- Blocks access to cloud metadata endpoints (AWS, GCP, Azure)
- Blocks access to private IP ranges and localhost
- Only allows HTTPS scheme for remote URLs
- Validates hostnames before making requests

### Path Traversal Protection (CWE-22)

- Validates all cache paths to prevent directory traversal
- Sanitizes URL paths before constructing file system paths
- Ensures all cached files remain within the `.trestle/cache` directory

### Arbitrary File Access Protection

- Restricts `file://` URIs to the trestle workspace by default
- Validates `trestle://` URIs to ensure they remain within workspace
- Prevents path traversal attempts in local file access

For detailed information, see [docs/security.md](docs/security.md).

## Security Testing

We maintain comprehensive security tests:

- Unit tests for security validators: `tests/trestle/core/remote/security_test.py`
- Integration tests for cache security: `tests/trestle/core/remote/cache_security_test.py`

Run security tests:

```bash
pytest tests/trestle/core/remote/security_test.py tests/trestle/core/remote/cache_security_test.py -v
```

## Security Best Practices for Users

1. **Keep Updated**: Always use the latest version of compliance-trestle
1. **Verify Sources**: Only import OSCAL models from trusted sources
1. **Use HTTPS**: Always use HTTPS URLs when importing from remote sources
1. **Review URLs**: Carefully review URLs before importing
1. **Workspace Isolation**: Keep your trestle workspace isolated from sensitive files

## Security Best Practices for Contributors

1. **Input Validation**: Always validate user-supplied input
1. **Use Security APIs**: Use provided security validators for URLs and paths
1. **Avoid Direct Access**: Use fetcher classes instead of direct file operations
1. **Security Review**: Security-sensitive code requires thorough review
1. **Test Security**: Add security tests for new features
1. **Follow OWASP**: Follow OWASP guidelines for secure coding

## Known Security Considerations

### Network Access

Compliance-trestle makes network requests when importing from remote URLs. Users should:

- Be aware of their network environment
- Use appropriate firewall rules
- Consider using a proxy for additional control

### File System Access

Compliance-trestle reads and writes files in the workspace. Users should:

- Ensure appropriate file system permissions
- Keep the workspace in a secure location
- Regularly backup important data

### Credentials

When using authenticated HTTPS or SFTP:

- Credentials must be provided via environment variables
- Never hardcode credentials in URLs
- Use secure credential management practices
- Rotate credentials regularly

## Security Audit History

| Date       | Version | Auditor  | Findings                          | Status |
| ---------- | ------- | -------- | --------------------------------- | ------ |
| 2026-03-31 | 3.x.x   | Internal | SSRF, Path Traversal, File Access | Fixed  |

## References

- [CWE-918: Server-Side Request Forgery (SSRF)](https://cwe.mitre.org/data/definitions/918.html)
- [CWE-22: Improper Limitation of a Pathname to a Restricted Directory](https://cwe.mitre.org/data/definitions/22.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)

## Contact

For security-related questions or concerns, please contact the maintainers listed in [MAINTAINERS.md](MAINTAINERS.md).

## Acknowledgments

We would like to thank the security researchers and community members who have helped improve the security of compliance-trestle through responsible disclosure.
=======
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

#### Domain Allowlist (Optional)

For additional security, you can restrict fetching to specific domains by configuring an allowed domains list. When configured, only URLs from the specified domains will be permitted.

### Path Traversal Protection

Trestle implements multiple layers of path traversal protection:

1. **URL Path Validation**: Blocks `..` sequences in URL paths to prevent directory traversal
2. **Cache Path Validation**: Ensures cached files remain within the designated cache directory
3. **Workspace Boundary Enforcement**: Validates that local file operations stay within the trestle workspace
4. **Sensitive File Protection**: Blocks access to sensitive system files even when outside-workspace access is allowed:
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
2. **Enable private IP blocking** (`TRESTLE_BLOCK_PRIVATE_IPS=true`) in production environments unless you specifically need to access private repositories
3. **Configure domain allowlists** when fetching from a known set of trusted domains
4. **Monitor logs** for warnings about private IP access
5. **Keep trestle updated** to receive the latest security fixes
6. **Review fetched content** before using it in production compliance workflows

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
>>>>>>> branch 'develop' of https://github.com/oscal-compass/compliance-trestle-ghsa-w76h-q7c6-jpjp.git
