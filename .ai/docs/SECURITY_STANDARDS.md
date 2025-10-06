# Security Standards

**Purpose**: Comprehensive security standards and requirements for all development projects covering secrets management, dependency security, and code security

**Scope**: All software development projects within the organization requiring security controls and compliance

**Overview**: Establishes mandatory security standards and best practices across the software development lifecycle. Covers three critical security domains: secrets management to prevent credential exposure, dependency scanning to detect vulnerable libraries, and code scanning to identify security flaws in custom code. Defines specific requirements, implementation guidelines, compliance criteria, and enforcement mechanisms. Provides security baselines applicable to all projects while allowing for additional project-specific requirements. Includes audit procedures, exception processes, and continuous improvement frameworks.

**Dependencies**: GitHub Advanced Security, pre-commit hooks, scanning tools (gitleaks, Dependabot, CodeQL, Semgrep)

**Exports**: Mandatory security requirements, implementation standards, compliance criteria, audit procedures

**Related**: secrets-management.md, dependency-scanning.md, code-scanning.md, all how-to guides, all templates

**Implementation**: Enforceable security standards with automated validation and regular compliance audits

---

## Overview

This document defines the mandatory security standards for all development projects. These standards establish minimum security requirements that must be met before code can be deployed to production. Compliance with these standards is not optional and will be enforced through automated checks, code reviews, and security audits.

## Core Security Principles

### Defense in Depth
- Implement multiple layers of security controls
- Assume each layer may fail and compensate with additional controls
- Never rely on a single security mechanism

### Shift Left Security
- Integrate security early in development lifecycle
- Detect and fix vulnerabilities during development, not production
- Automate security checks in development workflow

### Least Privilege
- Grant minimum necessary permissions
- Regularly review and revoke unnecessary access
- Use time-limited credentials where possible

### Fail Secure
- Systems must fail in a secure state
- Error messages must not expose sensitive information
- Maintain security even during failures

### Security by Default
- Secure configurations must be the default
- Developers must explicitly opt-in to less secure options
- Document all security-relevant configuration decisions

## Domain 1: Secrets Management

### Mandatory Requirements

**MUST: No Secrets in Version Control**
- API keys, passwords, tokens, and certificates must never be committed
- Pre-commit hooks must be configured to prevent secret commits
- All developers must have secrets scanning enabled locally

**MUST: Environment Variables for Secrets**
- All secrets must be loaded from environment variables
- .env files must be gitignored
- .env.example templates must be provided for all required variables

**MUST: Security-Focused .gitignore**
- Repository must include comprehensive security patterns
- Must ignore credential files, environment files, and key files
- Must be reviewed and updated quarterly

**MUST: Secrets Scanning in CI/CD**
- All commits must be scanned for secrets
- Pull requests containing secrets must be blocked
- Failed secret scans must prevent deployment

### Implementation Standards

**Pre-commit Hook Requirements**
```yaml
# Required in .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

**Environment Variable Standards**
- Use consistent naming: `SCREAMING_SNAKE_CASE`
- Group related variables with prefixes (`DB_`, `AWS_`, `API_`)
- Provide clear placeholders in .env.example
- Document all required variables

**Approved Secret Storage**
- Development: .env files (gitignored)
- Production: AWS Secrets Manager, Azure Key Vault, HashiCorp Vault, or equivalent
- Never: Hardcoded, environment variables in Dockerfile, configuration files in git

### Compliance Validation

**Automated Checks**
- [ ] Pre-commit hooks installed and functional
- [ ] .gitignore includes security patterns
- [ ] .env.example exists and is comprehensive
- [ ] No .env files committed to repository
- [ ] CI/CD includes secrets scanning
- [ ] All secret scans passing

**Manual Review**
- [ ] No hardcoded credentials in codebase
- [ ] Production secrets use approved storage
- [ ] Secret rotation procedures documented
- [ ] Access to secrets follows least privilege

### Exceptions and Remediation

**Allowed Exceptions**
- Example/demo credentials clearly marked as non-functional
- Test fixtures with explicitly fake data
- Public API keys (properly documented as such)

**Remediation Process for Exposed Secrets**
1. Revoke compromised credential immediately (within 1 hour)
2. Generate new credential
3. Update production systems
4. Remove from Git history using BFG or git-filter-repo
5. Conduct incident review
6. Document lessons learned

## Domain 2: Dependency Scanning

### Mandatory Requirements

**MUST: Automated Dependency Scanning**
- GitHub Dependabot must be enabled for all repositories
- Scans must run on every push and pull request
- Vulnerabilities must be tracked in GitHub Security tab

**MUST: Vulnerability Response SLAs**
| Severity | Response Time | Resolution Time |
|----------|--------------|-----------------|
| Critical | 24 hours | 48 hours |
| High | 72 hours | 1 week |
| Medium | 1 week | 1 month |
| Low | 1 month | 3 months |

**MUST: Automated Security Updates**
- Dependabot security updates must be enabled
- Security update PRs must be reviewed within SLA
- Blocking vulnerabilities must prevent deployment

**MUST: Dependency Auditing**
- npm audit, pip-audit, or equivalent must run in CI/CD
- Audit results must be tracked and reviewed
- New vulnerable dependencies must be blocked

### Implementation Standards

**Dependabot Configuration**
```yaml
# Required in .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"  # or pip, maven, etc.
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "security"
```

**Package Manager Scanning**
- JavaScript: `npm audit --audit-level=moderate` in CI
- Python: `safety check` or `pip-audit` in CI
- Java: OWASP Dependency-Check in build
- .NET: `dotnet list package --vulnerable` in CI

**Vulnerability Tracking**
- All vulnerabilities logged in GitHub Security tab
- Suppressed vulnerabilities documented with expiration
- Regular review of suppressed vulnerabilities (quarterly)

### Compliance Validation

**Automated Checks**
- [ ] Dependabot enabled and configured
- [ ] Security updates enabled
- [ ] Package manager auditing in CI/CD
- [ ] No critical or high vulnerabilities in main branch
- [ ] All security PRs addressed within SLA

**Manual Review**
- [ ] Vulnerability response documented
- [ ] Suppressions justified and time-limited
- [ ] Dependencies reviewed for licensing issues
- [ ] Unmaintained dependencies identified and replaced

### Exceptions and Remediation

**Allowed Suppressions**
- False positives (must document evidence)
- Not exploitable in specific context (must document)
- No fix available and workaround implemented
- Accepted risk with management approval

**Suppression Requirements**
- Must include detailed justification
- Must have expiration date (max 90 days)
- Must be reviewed by security team
- Must be documented in code

## Domain 3: Code Scanning

### Mandatory Requirements

**MUST: Static Application Security Testing (SAST)**
- CodeQL or equivalent must scan all code changes
- Security-extended query suite must be enabled
- Scans must run on all pull requests and pushes

**MUST: Language-Specific Security Linters**
- Python: Bandit
- JavaScript/TypeScript: ESLint with security plugins
- Java: SpotBugs with FindSecBugs
- Go: gosec
- Other languages: Approved equivalent

**MUST: Security Gate for Pull Requests**
- Code scanning must pass before merge
- Critical and high severity findings must block merge
- Security review required for security-related changes

**MUST: Custom Security Rules**
- Organization-specific security patterns must be codified
- Custom rules for common vulnerability patterns
- Regular review and update of rule sets

### Implementation Standards

**CodeQL Configuration**
```yaml
# Required in .github/workflows/codeql-analysis.yml
- uses: github/codeql-action/init@v2
  with:
    queries: security-extended
    config-file: ./.github/codeql/codeql-config.yml
```

**Semgrep Configuration**
```yaml
# Required for additional scanning
- uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/security-audit
      p/owasp-top-ten
```

**Security Query Requirements**
- Must detect OWASP Top 10 vulnerabilities
- Must identify hardcoded secrets
- Must detect common injection flaws
- Must identify insecure cryptography

### Compliance Validation

**Automated Checks**
- [ ] CodeQL enabled and configured
- [ ] Security-extended queries enabled
- [ ] Language-specific linters configured
- [ ] All security scans passing
- [ ] No critical or high findings unresolved
- [ ] Branch protection requires security checks

**Manual Review**
- [ ] Custom security rules implemented
- [ ] False positives properly suppressed
- [ ] Security findings tracked to resolution
- [ ] Code reviews include security considerations

### Vulnerability Categories Covered

**OWASP Top 10 (2021)**
1. Broken Access Control
2. Cryptographic Failures
3. Injection
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable and Outdated Components
7. Identification and Authentication Failures
8. Software and Data Integrity Failures
9. Security Logging and Monitoring Failures
10. Server-Side Request Forgery (SSRF)

**Additional Security Patterns**
- Hardcoded secrets
- Weak cryptography (MD5, SHA1)
- Insecure random number generation
- Command injection
- Path traversal
- XML external entities (XXE)
- Deserialization vulnerabilities
- Race conditions
- Buffer overflows (compiled languages)

### Exceptions and Remediation

**Allowed Suppressions**
- False positives (must verify thoroughly)
- Risk accepted with compensating controls
- Framework-specific patterns verified as safe
- Test code with appropriate documentation

**Suppression Requirements**
```python
# Example: Properly documented suppression
# nosec B608 - SQL injection false positive
# This query uses parameterized statements via SQLAlchemy ORM
# Reviewed by: @security-team on 2024-01-15
# Expires: 2024-06-30
query = session.query(User).filter(User.id == user_id)
```

## Cross-Cutting Requirements

### Security Documentation

**MUST: Security Documentation**
- README must include security section
- Security contact information must be provided
- Vulnerability disclosure policy must be documented
- Security architecture must be documented for complex systems

**MUST: Security Training**
- All developers must complete security training annually
- New team members must complete training within 30 days
- Training must cover all three security domains

### Security Reviews

**MUST: Regular Security Audits**
- Quarterly review of all security controls
- Annual penetration testing for production systems
- Monthly review of security metrics

**MUST: Incident Response**
- Security incident response plan must exist
- Plan must be tested annually
- Incidents must be documented and reviewed

### Monitoring and Metrics

**Required Metrics**
- Number of secrets detected (should be 0)
- Mean time to remediate vulnerabilities by severity
- Percentage of dependencies with known vulnerabilities
- Number of security findings by severity
- SLA compliance rate

**Required Dashboards**
- Security posture dashboard
- Vulnerability trends
- Compliance status
- Incident tracking

## Compliance Enforcement

### Automated Enforcement

**Pre-commit Hooks**
- Block commits with secrets
- Enforce code formatting
- Run basic security checks

**CI/CD Pipeline**
- Block builds with critical vulnerabilities
- Fail on security scan failures
- Prevent deployment of non-compliant code

**Branch Protection**
- Require security checks to pass
- Require security team review for sensitive changes
- Prevent force pushes to protected branches

### Manual Enforcement

**Code Review Requirements**
- Security considerations in all reviews
- Security team review for authentication/authorization changes
- Architecture review for security-critical components

**Audit Process**
- Quarterly compliance audits
- Random sampling of repositories
- Remediation tracking for findings

### Non-Compliance Consequences

**Warning (First Instance)**
- Notification to developer and team lead
- Required remediation within 48 hours
- Additional training required

**Escalation (Repeated)**
- Notification to engineering management
- Immediate remediation required
- Performance review documentation

**Critical Non-Compliance**
- Production deployment blocked
- Immediate security team involvement
- Executive notification for critical systems

## Exception Process

### Requesting Exceptions

**Exception Request Requirements**
1. Written justification
2. Risk assessment
3. Compensating controls
4. Expiration date
5. Security team approval

**Approval Authority**
- Low risk: Team lead
- Medium risk: Security team
- High risk: Security team + Engineering director
- Critical systems: CISO approval required

**Documentation**
```yaml
# security-exception.yml
exception:
  id: SEC-2024-001
  requested_by: developer@company.com
  requested_date: 2024-01-15
  standard: "Dependency Scanning - High Severity SLA"
  justification: "No patch available, workaround implemented"
  compensating_controls:
    - "Input validation added"
    - "Additional monitoring enabled"
  risk_level: medium
  approved_by: security-team@company.com
  approved_date: 2024-01-16
  expires: 2024-04-15
  review_notes: "Acceptable with mitigations"
```

## Continuous Improvement

### Standards Review

**Quarterly Reviews**
- Review security metrics
- Update standards based on new threats
- Incorporate lessons learned from incidents
- Update tooling and automation

**Annual Reviews**
- Comprehensive standards review
- Alignment with industry best practices
- Update for new technologies and frameworks
- Regulatory compliance review

### Tool Updates

**Monthly Updates**
- Update scanning tools to latest versions
- Review and incorporate new security rules
- Update vulnerability databases
- Test new security features

**Quarterly Evaluations**
- Evaluate new security tools
- Assess tool effectiveness
- Review false positive rates
- Consider tool replacements if warranted

## Resources and Support

### Security Team Contacts
- Security team email: security-team@company.com
- Urgent security issues: security-urgent@company.com
- Security Slack channel: #security

### Training Resources
- Internal security training portal
- OWASP resources
- Language-specific security guides
- Monthly security office hours

### Tools and Documentation
- secrets-management.md - Comprehensive secrets guide
- dependency-scanning.md - Dependency security details
- code-scanning.md - Code scanning overview
- How-to guides in howtos/ directory
- Templates in templates/ directory

## Revision History

This document is reviewed and updated quarterly. Major changes require security team approval.

**Document Version**: 1.0
**Effective Date**: 2024-01-01
**Next Review**: 2024-04-01
