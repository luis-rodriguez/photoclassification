# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please email security concerns to:

- **Email**: luis-rodriguez@users.noreply.github.com
- **Subject**: [SECURITY] Photo Date Classifier - Brief Description

### What to Include

Please include the following in your report:

1. **Description**: Clear description of the vulnerability
2. **Impact**: Potential impact and attack scenarios
3. **Steps to Reproduce**: Detailed steps to reproduce the issue
4. **Proof of Concept**: Code or commands demonstrating the vulnerability (if applicable)
5. **Suggested Fix**: Proposed solution (optional but appreciated)
6. **Your Contact**: How we can reach you for follow-up

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-14 days
  - Medium: 14-30 days
  - Low: 30-90 days

## Security Measures

### In the Codebase

- **Input Validation**: All user inputs are validated and sanitized
- **Path Sanitization**: File paths are sanitized to prevent traversal attacks
- **No Shell Injection**: We avoid shell execution; use Python libraries directly
- **Secure Hashing**: SHA-256 for content hashing
- **Type Safety**: Full type hints with mypy strict mode
- **Dependency Pinning**: Dependencies have upper bounds to prevent unexpected updates

### Security Tools

We use the following tools to maintain security:

1. **Bandit**: Static security analysis for Python code
   ```bash
   bandit -r src/
   ```

2. **pip-audit**: Scan dependencies for known vulnerabilities
   ```bash
   pip-audit
   ```

3. **CodeQL**: GitHub's semantic code analysis (via GitHub Actions)

4. **Dependabot**: Automated dependency updates and security alerts

### Pre-commit Security Checks

Security checks run automatically via pre-commit:

```yaml
- repo: https://github.com/PyCQA/bandit
  rev: 1.7.5
  hooks:
    - id: bandit
      args: ['-r', 'src/']
```

## Known Security Considerations

### File System Access

- The tool requires read access to source directory
- The tool requires write access to destination directory
- Follows system file permissions
- Does not escalate privileges

### Path Traversal Prevention

- All paths are sanitized using `sanitize_path_component()`
- Paths are resolved to absolute paths
- `..` and path separators in filenames are removed/replaced

### Dependency Security

- Production dependencies are pinned with compatible ranges
- Regular updates via Dependabot
- Security advisories monitored

### Data Privacy

- No data is sent to external services
- All operations are local
- No telemetry or analytics

## Best Practices for Users

### Before Running

1. **Backup Your Data**: Always backup photos before organizing
2. **Test with Dry Run**: Use `--dry-run` to preview changes
3. **Start Small**: Test on a small subset first
4. **Check Permissions**: Ensure proper file permissions

### Safe Usage

```bash
# 1. Backup
cp -r /path/to/photos /path/to/photos.backup

# 2. Dry run
photo-date-classifier classify \
  --source /path/to/photos \
  --dest /path/to/organized \
  --dry-run

# 3. Review output

# 4. Run for real
photo-date-classifier classify \
  --source /path/to/photos \
  --dest /path/to/organized
```

### Permissions

- Run with minimal necessary permissions
- Avoid running as root/administrator
- Use dedicated user accounts for batch operations

## Security Updates

Security updates will be released as:

1. **Patch Release**: For backward-compatible security fixes
2. **GitHub Security Advisory**: For public disclosure
3. **CHANGELOG.md**: Documented in changelog with `[SECURITY]` tag

## Disclosure Policy

We follow **responsible disclosure**:

1. Issue reported privately
2. Issue confirmed and validated
3. Fix developed and tested
4. Fix released to users
5. Public disclosure (coordinated with reporter)

## Hall of Fame

We recognize security researchers who responsibly disclose vulnerabilities:

<!-- Security researchers will be listed here -->

*No security issues reported yet.*

## Questions?

For security questions (not vulnerabilities), please:

- Open a GitHub Discussion
- Tag with "security" label

Thank you for helping keep Photo Date Classifier secure!
