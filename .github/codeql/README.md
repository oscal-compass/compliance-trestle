# CodeQL Security Configuration for Compliance-Trestle

This directory contains the enhanced CodeQL security scanning configuration for the compliance-trestle project.

## Overview

The CodeQL configuration has been upgraded from basic scanning to comprehensive security analysis to proactively identify and prevent security vulnerabilities before they reach production.

## Files

### `codeql-config.yml`
Main configuration file that:
- Enables `security-and-quality` and `security-extended` query suites
- Configures path filtering to focus on source code
- Excludes test files and third-party content
- Enables trap caching for faster analysis
- Filters results to focus on high-severity security issues

### `python-security-queries.qls`
Custom query suite specifically tailored for trestle's security concerns:
- **Path Traversal (CWE-022)**: Critical for file operations
- **SSRF (CWE-918)**: Important for remote content fetching
- **Command Injection (CWE-078)**: Protects against OS command exploits
- **Deserialization (CWE-502)**: Guards against unsafe object deserialization
- **Cryptography Issues (CWE-327, CWE-338)**: Ensures strong crypto usage
- **Information Exposure (CWE-200)**: Prevents sensitive data leaks
- **Hard-coded Credentials (CWE-798)**: Detects embedded secrets
- **XML/XXE Attacks (CWE-611, CWE-776)**: Protects XML processing
- **Injection Attacks**: SQL, NoSQL, Code, Log injection detection

## Workflow Integration

The CodeQL workflow (`.github/workflows/codeql-analysis.yml`) now:
- ✅ Runs on **all PRs** to `develop` and `main` branches (not just develop)
- ✅ Runs on pushes to `develop` and `main` branches
- ✅ Runs weekly scheduled scans (Thursdays at 21:39 UTC)
- ✅ Supports manual triggering via `workflow_dispatch`
- ✅ Uploads SARIF results as artifacts for review
- ✅ Integrates with GitHub Security tab

## Security Coverage

The enhanced configuration provides comprehensive coverage for:

### High Priority (Always Scanned)
- Server-Side Request Forgery (SSRF)
- Path Traversal
- Command Injection
- Code Injection
- Deserialization vulnerabilities
- Cryptographic weaknesses
- Hard-coded credentials

### Medium Priority (Included)
- Information exposure
- Certificate validation issues
- XML external entity (XXE) attacks
- Log injection
- Cross-site scripting (XSS)
- SQL/NoSQL injection

### Excluded
- Low-precision audit queries (too noisy)
- Note-level findings (informational only)

## Benefits

1. **Early Detection**: Security issues caught in PRs before merge
2. **Comprehensive Coverage**: Multiple query suites for thorough analysis
3. **Focused Results**: Filtered to high-severity, actionable findings
4. **Compliance Ready**: Aligns with OSCAL security requirements
5. **Continuous Monitoring**: Weekly scans catch new vulnerabilities
6. **Artifact Retention**: 30-day SARIF file retention for audit trails

## Viewing Results

### In GitHub UI
1. Navigate to the **Security** tab
2. Click **Code scanning alerts**
3. Review findings by severity and category

### In Pull Requests
- CodeQL findings appear as PR checks
- Click "Details" to see specific issues
- Findings are annotated in the code diff

### As Artifacts
- Download SARIF files from workflow runs
- Use for offline analysis or compliance reporting
- Retained for 30 days

## Customization

### Adding New Queries
Edit `python-security-queries.qls` to include additional CWE categories:
```yaml
- include:
    tags contain:
      - external/cwe/cwe-XXX  # Add your CWE number
```

### Adjusting Severity Filters
Edit `codeql-config.yml` query filters:
```yaml
query-filters:
  - include:
      problem.severity:
        - error
        - warning
        # Add 'note' to include informational findings
```

### Excluding Paths
Add to `paths-ignore` in `codeql-config.yml`:
```yaml
paths-ignore:
  - '**/your-path/**'
```

## Troubleshooting

### Workflow Fails
- Check the Actions tab for detailed logs
- Verify CodeQL version compatibility
- Ensure config file syntax is valid

### Too Many False Positives
- Adjust precision filters in `python-security-queries.qls`
- Add specific exclusions for known safe patterns
- Use `# codeql[rule-id]` comments to suppress specific findings

### Missing Expected Findings
- Verify paths are not excluded
- Check that relevant query packs are enabled
- Ensure the code pattern matches query expectations

## Maintenance

- **Monthly**: Review new CodeQL query releases
- **Quarterly**: Audit excluded findings for false positives
- **After Security Incidents**: Add relevant CWE categories
- **Version Updates**: Test with new CodeQL action versions

## References

- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Python Query Reference](https://codeql.github.com/codeql-query-help/python/)
- [CWE Database](https://cwe.mitre.org/)
- [Trestle Security Policy](../../SECURITY.md)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## Support

For questions or issues with CodeQL configuration:
1. Check GitHub Actions logs
2. Review CodeQL documentation
3. Open an issue in the compliance-trestle repository
4. Contact the security team via SECURITY.md

---

**Last Updated**: 2026-05-29  
**Configuration Version**: 2.0 (Enhanced Security)