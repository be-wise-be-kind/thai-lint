# Dependency Scanning

**Purpose**: Comprehensive guide for automated vulnerability detection and management in project dependencies

**Scope**: All projects using third-party libraries, packages, and dependencies across languages and package managers

**Overview**: Establishes comprehensive strategies for identifying, tracking, and remediating security vulnerabilities in project dependencies. Covers automated scanning tools for multiple ecosystems (npm, pip, Maven, etc.), continuous monitoring approaches, vulnerability assessment workflows, and remediation strategies. Includes detailed implementation guides for integrating dependency scanning into development workflows, CI/CD pipelines, and production monitoring. Provides specific configurations for different package managers, vulnerability databases, and alert management systems.

**Dependencies**: Package managers (npm, pip, Maven, Gradle), GitHub Dependabot, security scanning tools (Snyk, Safety, npm audit)

**Exports**: Dependency scanning configurations, vulnerability assessment workflows, remediation procedures, monitoring strategies

**Related**: how-to-setup-dependency-scanning.md, github-workflow-security.yml.template, SECURITY_STANDARDS.md

**Implementation**: Multi-layered approach combining automated scanning, continuous monitoring, and proactive vulnerability management

---

## Overview

Dependencies are a critical attack vector in modern software development. The average application includes hundreds or thousands of third-party libraries, each potentially containing security vulnerabilities. Dependency scanning automates the detection of known vulnerabilities in your project's dependencies, enabling teams to identify and remediate security issues before they reach production.

## Understanding Dependency Vulnerabilities

### Types of Vulnerabilities

**Known CVEs (Common Vulnerabilities and Exposures)**
- Publicly disclosed security vulnerabilities
- Tracked in National Vulnerability Database (NVD)
- Assigned severity scores (CVSS)
- Often have patches or workarounds available

**Supply Chain Attacks**
- Malicious code injected into legitimate packages
- Typosquatting attacks on popular packages
- Compromised maintainer accounts
- Dependency confusion attacks

**Outdated Dependencies**
- No longer maintained packages
- Unsupported versions with known issues
- Missing security patches
- Compatibility and stability risks

**Transitive Dependencies**
- Vulnerabilities in dependencies of dependencies
- Often invisible in direct dependency lists
- Can be numerous and complex to track
- Require deep dependency tree analysis

### Risk Factors

**Severity Levels**
- **Critical**: Immediate exploitation possible, severe impact
- **High**: Easily exploitable with significant impact
- **Medium**: Exploitable under certain conditions
- **Low**: Difficult to exploit or limited impact

**Exploit Availability**
- Public exploit code available
- Active exploitation in the wild
- Proof-of-concept demonstrations
- No known exploits yet

**Attack Complexity**
- No special privileges required
- No user interaction needed
- Network-accessible vulnerabilities
- Local-only exploitation

**Impact Assessment**
- Confidentiality impact (data exposure)
- Integrity impact (data modification)
- Availability impact (denial of service)
- Scope (can vulnerability escape sandbox)

## Scanning Tools and Platforms

### GitHub Dependabot

GitHub's built-in dependency scanning and automated update tool.

**Features**
- Automatic vulnerability scanning
- Security alerts for vulnerable dependencies
- Automated pull requests for updates
- Support for multiple ecosystems
- Integration with GitHub Security tab

**Setup and Configuration**

Enable Dependabot in repository settings or via configuration file:

```yaml
# .github/dependabot.yml
version: 2
updates:
  # JavaScript dependencies
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    assignees:
      - "tech-lead"
    labels:
      - "dependencies"
      - "security"
    commit-message:
      prefix: "chore"
      include: "scope"

  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    allow:
      - dependency-type: "all"
    ignore:
      # Ignore major version updates for specific packages
      - dependency-name: "django"
        update-types: ["version-update:semver-major"]

  # Docker dependencies
  - package-ecosystem: "docker"
    directory: "/.docker/dockerfiles"
    schedule:
      interval: "weekly"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

**Advanced Configuration Options**

```yaml
# Customize version constraints
- package-ecosystem: "npm"
  directory: "/"
  schedule:
    interval: "daily"
  versioning-strategy: increase
  # Options: auto, increase, increase-if-necessary, lockfile-only, widen

  # Target specific branch
  target-branch: "development"

  # Group updates
  groups:
    production-dependencies:
      dependency-type: "production"
    development-dependencies:
      dependency-type: "development"

  # Vendor dependencies
  vendor: true

  # Custom registry configuration
  registries:
    - npm-registry

registries:
  npm-registry:
    type: npm-registry
    url: https://npm.pkg.github.com
    token: ${{ secrets.NPM_TOKEN }}
```

**Managing Dependabot Alerts**

```bash
# View security alerts
gh api repos/{owner}/{repo}/dependabot/alerts

# Dismiss an alert
gh api repos/{owner}/{repo}/dependabot/alerts/{alert_number} \
  --method PATCH \
  --field state=dismissed \
  --field dismissed_reason=inaccurate

# Dismiss reasons: fix_started, inaccurate, no_bandwidth, not_used, tolerable_risk
```

### Snyk

Comprehensive security platform for finding and fixing vulnerabilities.

**Installation**

```bash
# Install Snyk CLI
npm install -g snyk

# Authenticate
snyk auth

# Or use API token
snyk config set api=YOUR_API_TOKEN
```

**Basic Usage**

```bash
# Test for vulnerabilities
snyk test

# Test and show detailed vulnerability information
snyk test --json

# Test all projects in directory
snyk test --all-projects

# Monitor project (continuous monitoring)
snyk monitor

# Test with specific severity threshold
snyk test --severity-threshold=high

# Test Docker images
snyk container test node:16-alpine

# Test Kubernetes configurations
snyk iac test ./k8s-manifests/
```

**Configuration (.snyk)**

```yaml
# .snyk
version: v1.22.0

# Ignore specific vulnerabilities
ignore:
  'SNYK-JS-LODASH-590103':
    - '*':
        reason: 'No fix available, investigating alternative packages'
        expires: '2024-12-31'
        created: '2024-01-15'

  'SNYK-PYTHON-DJANGO-2971148':
    - 'django@3.2.0 > django-admin@3.2.0':
        reason: 'False positive - not exploitable in our use case'
        expires: '2024-06-30'

# Language-specific settings
language-settings:
  python:
    skip-unresolved: true

# Patches
patch:
  'npm:lodash:20180130':
    - lodash:
        patched: '2024-01-15T12:00:00.000Z'

# Exclude directories
exclude:
  - test/**
  - node_modules/**
  - .venv/**
```

**GitHub Actions Integration**

```yaml
# .github/workflows/snyk-security.yml
name: Snyk Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2am

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high --fail-on=all

      - name: Upload Snyk results to GitHub Code Scanning
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: snyk.sarif
```

**Policy Configuration**

```yaml
# .snyk policy for organization
rules:
  # Fail builds on high severity
  - severity: high
    action: fail

  # Warn on medium severity
  - severity: medium
    action: warn

  # Ignore low severity
  - severity: low
    action: ignore

  # License policy
  - license:
      - GPL-3.0
      - AGPL-3.0
    action: fail
    reason: "Incompatible with commercial use"
```

### npm audit

Built-in npm security auditing tool.

**Basic Commands**

```bash
# Run security audit
npm audit

# Get detailed JSON output
npm audit --json

# Show only production dependencies
npm audit --production

# Audit with specific registry
npm audit --registry=https://registry.npmjs.org

# Generate detailed report
npm audit --parseable
```

**Automated Fixes**

```bash
# Automatically fix vulnerabilities
npm audit fix

# Fix only production dependencies
npm audit fix --only=prod

# Force fix (may introduce breaking changes)
npm audit fix --force

# Dry run to see what would be fixed
npm audit fix --dry-run
```

**CI/CD Integration**

```bash
# Fail CI build on vulnerabilities
npm audit --audit-level=high

# Audit levels: info, low, moderate, high, critical
npm audit --audit-level=moderate

# Combine with other npm commands
npm ci && npm audit --audit-level=high
```

**Package-lock.json Audit**

```bash
# Audit lockfile only (faster)
npm audit --package-lock-only

# Update package-lock.json with audit fixes
npm audit fix --package-lock-only
```

### Python Safety

Safety checks Python dependencies for known vulnerabilities.

**Installation**

```bash
pip install safety
```

**Basic Usage**

```bash
# Check installed packages
safety check

# Check requirements file
safety check -r requirements.txt

# Generate JSON report
safety check --json

# Check with specific database
safety check --db /path/to/safety-db.json

# Full report with remediation suggestions
safety check --full-report

# Set exit code based on severity
safety check --exit-code
```

**CI/CD Integration**

```yaml
# .github/workflows/python-security.yml
name: Python Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install safety
          pip install -r requirements.txt

      - name: Run Safety check
        run: safety check --continue-on-error --save-json safety-report.json

      - name: Upload Safety report
        uses: actions/upload-artifact@v3
        with:
          name: safety-report
          path: safety-report.json
```

**Configuration (.safety-policy.yml)**

```yaml
# .safety-policy.yml
security:
  # Ignore specific vulnerabilities
  ignore-vulnerabilities:
    # CVE-2019-8341 in Jinja2
    39621:
      reason: "Not exploitable in our configuration"
      expires: "2024-12-31"

  # Continue on vulnerability found
  continue-on-vulnerability-error: false

  # Alert on unpinned requirements
  alert-on-unpinned-requirements: true
```

### Trivy

Comprehensive vulnerability scanner for containers and dependencies.

**Installation**

```bash
# macOS
brew install aquasecurity/trivy/trivy

# Linux
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy
```

**Usage**

```bash
# Scan Docker image
trivy image python:3.11-slim

# Scan filesystem
trivy fs /path/to/project

# Scan with specific severity
trivy image --severity HIGH,CRITICAL nginx:latest

# Generate report
trivy image --format json --output report.json python:3.11

# Scan with custom policy
trivy image --policy ./policy.rego myimage:latest

# Scan Kubernetes manifests
trivy config ./k8s/
```

**CI/CD Integration**

```yaml
# .github/workflows/trivy-scan.yml
name: Trivy Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

## Language-Specific Scanning

### JavaScript/TypeScript (npm/yarn/pnpm)

**npm audit**

```bash
# Standard audit
npm audit

# Fix automatically
npm audit fix

# Audit with severity threshold
npm audit --audit-level=moderate

# Generate detailed report
npm audit --json > audit-report.json
```

**yarn audit**

```bash
# Run audit
yarn audit

# Audit with JSON output
yarn audit --json

# Audit groups
yarn audit --groups dependencies devDependencies
```

**pnpm audit**

```bash
# Run audit
pnpm audit

# Audit with specific severity
pnpm audit --audit-level=high

# Fix vulnerabilities
pnpm audit --fix
```

**Package.json Scripts**

```json
{
  "scripts": {
    "audit:check": "npm audit --audit-level=high",
    "audit:fix": "npm audit fix",
    "audit:report": "npm audit --json > security-audit.json",
    "precommit": "npm audit --audit-level=moderate"
  }
}
```

### Python (pip/poetry/pipenv)

**pip-audit**

```bash
# Install pip-audit
pip install pip-audit

# Audit installed packages
pip-audit

# Audit requirements file
pip-audit -r requirements.txt

# Generate JSON report
pip-audit --format json --output audit.json

# Audit with custom vulnerability database
pip-audit --vulnerability-service osv
```

**Poetry**

```bash
# Check for security updates
poetry show --outdated

# Update with security fixes
poetry update

# Export and audit with Safety
poetry export -f requirements.txt | safety check --stdin
```

**Pipenv**

```bash
# Check for vulnerabilities
pipenv check

# Update vulnerable packages
pipenv update --outdated

# Detailed vulnerability report
pipenv check --verbose
```

**Requirements Scanning Script**

```python
# scan_requirements.py
import subprocess
import json
import sys

def scan_dependencies():
    """Scan dependencies for vulnerabilities."""
    try:
        # Run safety check
        result = subprocess.run(
            ['safety', 'check', '--json'],
            capture_output=True,
            text=True
        )

        vulnerabilities = json.loads(result.stdout)

        if vulnerabilities:
            print(f"Found {len(vulnerabilities)} vulnerabilities:")
            for vuln in vulnerabilities:
                print(f"  - {vuln['package']}: {vuln['vulnerability']}")
            sys.exit(1)
        else:
            print("No vulnerabilities found!")
            sys.exit(0)

    except Exception as e:
        print(f"Error scanning dependencies: {e}")
        sys.exit(1)

if __name__ == "__main__":
    scan_dependencies()
```

### Java (Maven/Gradle)

**OWASP Dependency-Check (Maven)**

```xml
<!-- pom.xml -->
<build>
  <plugins>
    <plugin>
      <groupId>org.owasp</groupId>
      <artifactId>dependency-check-maven</artifactId>
      <version>8.4.0</version>
      <configuration>
        <failBuildOnCVSS>7</failBuildOnCVSS>
        <format>ALL</format>
      </configuration>
      <executions>
        <execution>
          <goals>
            <goal>check</goal>
          </goals>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

```bash
# Run dependency check
mvn dependency-check:check

# Update vulnerability database
mvn dependency-check:update-only

# Generate report
mvn dependency-check:aggregate
```

**OWASP Dependency-Check (Gradle)**

```gradle
// build.gradle
plugins {
    id 'org.owasp.dependencycheck' version '8.4.0'
}

dependencyCheck {
    failBuildOnCVSS = 7
    suppressionFile = 'config/dependency-check-suppressions.xml'
    formats = ['HTML', 'JSON']
    outputDirectory = 'build/reports/dependency-check'
}
```

```bash
# Run dependency check
./gradlew dependencyCheckAnalyze

# Update NVD database
./gradlew dependencyCheckUpdate
```

**Snyk for Java**

```bash
# Test Maven project
snyk test --file=pom.xml

# Test Gradle project
snyk test --file=build.gradle

# Monitor project
snyk monitor --file=pom.xml
```

### Ruby (Bundler)

**bundler-audit**

```bash
# Install bundler-audit
gem install bundler-audit

# Update vulnerability database
bundle audit update

# Check for vulnerabilities
bundle audit check

# Check and update database
bundle audit check --update
```

**Gemfile Configuration**

```ruby
# Gemfile
source 'https://rubygems.org'

gem 'rails', '~> 7.0.0'
gem 'bundler-audit', group: :development

group :development, :test do
  gem 'brakeman'  # Security scanner for Rails
end
```

### Go

**govulncheck**

```bash
# Install govulncheck
go install golang.org/x/vuln/cmd/govulncheck@latest

# Scan for vulnerabilities
govulncheck ./...

# Scan with JSON output
govulncheck -json ./...

# Scan specific package
govulncheck -pkg github.com/your/package
```

**nancy (Sonatype)**

```bash
# Install nancy
go get -u github.com/sonatype-nexus-community/nancy

# Scan dependencies
go list -json -m all | nancy sleuth

# Exclude dev dependencies
go list -json -m all | nancy sleuth --exclude-vulnerability-file .nancy-ignore
```

### .NET

**dotnet list package**

```bash
# List vulnerable packages
dotnet list package --vulnerable

# List vulnerable packages with details
dotnet list package --vulnerable --include-transitive

# List deprecated packages
dotnet list package --deprecated
```

**NuGet Audit**

```xml
<!-- Directory.Build.props -->
<Project>
  <PropertyGroup>
    <NuGetAudit>true</NuGetAudit>
    <NuGetAuditMode>all</NuGetAuditMode>
    <NuGetAuditLevel>moderate</NuGetAuditLevel>
  </PropertyGroup>
</Project>
```

## Continuous Monitoring

### Scheduled Scans

**GitHub Actions Scheduled Workflow**

```yaml
# .github/workflows/scheduled-security-scan.yml
name: Scheduled Security Scan

on:
  schedule:
    # Daily at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        scanner: [npm-audit, snyk, trivy]

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        if: matrix.scanner == 'npm-audit'
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Run npm audit
        if: matrix.scanner == 'npm-audit'
        run: |
          npm ci
          npm audit --audit-level=moderate

      - name: Run Snyk scan
        if: matrix.scanner == 'snyk'
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      - name: Run Trivy scan
        if: matrix.scanner == 'trivy'
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'

      - name: Notify on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Security scan failed for ${{ matrix.scanner }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Alert Management

**Slack Notifications**

```yaml
# .github/workflows/security-alerts.yml
name: Security Alerts

on:
  push:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run security scan
        id: scan
        run: |
          npm audit --json > audit-results.json || true

      - name: Parse results
        id: parse
        run: |
          CRITICAL=$(jq '.metadata.vulnerabilities.critical' audit-results.json)
          HIGH=$(jq '.metadata.vulnerabilities.high' audit-results.json)
          echo "critical=$CRITICAL" >> $GITHUB_OUTPUT
          echo "high=$HIGH" >> $GITHUB_OUTPUT

      - name: Send Slack notification
        if: steps.parse.outputs.critical > 0 || steps.parse.outputs.high > 0
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              text: "Security Alert",
              attachments: [{
                color: 'danger',
                text: `Found ${{ steps.parse.outputs.critical }} critical and ${{ steps.parse.outputs.high }} high severity vulnerabilities`
              }]
            }
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

**Email Notifications**

```yaml
- name: Send email notification
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: Security Scan Failed - ${{ github.repository }}
    to: security-team@company.com
    from: github-actions@company.com
    body: |
      Security scan failed in repository ${{ github.repository }}

      Commit: ${{ github.sha }}
      Author: ${{ github.actor }}

      Please review the workflow run:
      ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
```

## Vulnerability Assessment and Prioritization

### Severity Assessment

**CVSS Scoring**

```python
# vulnerability_assessment.py
from dataclasses import dataclass
from enum import Enum
from typing import List

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class Vulnerability:
    id: str
    package: str
    version: str
    severity: Severity
    cvss_score: float
    cwe: List[str]
    exploit_available: bool
    patch_available: bool
    transitive: bool

    @property
    def priority(self) -> int:
        """Calculate priority score for remediation."""
        score = 0

        # Base severity score
        severity_scores = {
            Severity.CRITICAL: 100,
            Severity.HIGH: 75,
            Severity.MEDIUM: 50,
            Severity.LOW: 25,
            Severity.INFO: 10,
        }
        score += severity_scores[self.severity]

        # Exploit availability increases priority
        if self.exploit_available:
            score += 50

        # Patch availability makes it easier to fix
        if self.patch_available:
            score += 25

        # Direct dependencies are higher priority
        if not self.transitive:
            score += 20

        return score

def prioritize_vulnerabilities(vulns: List[Vulnerability]) -> List[Vulnerability]:
    """Sort vulnerabilities by priority."""
    return sorted(vulns, key=lambda v: v.priority, reverse=True)
```

### Risk Matrix

```
Impact vs. Exploitability Matrix:

                 Low Impact  Medium Impact  High Impact
Easy Exploit     MEDIUM      HIGH          CRITICAL
Medium Exploit   LOW         MEDIUM        HIGH
Hard Exploit     INFO        LOW           MEDIUM
```

**Prioritization Factors**
1. Severity (CVSS score)
2. Exploitability (public exploits available)
3. Attack vector (network vs. local)
4. Privileges required
5. User interaction required
6. Patch availability
7. Dependency type (direct vs. transitive)
8. Production vs. development dependency

## Remediation Strategies

### Update Strategies

**Immediate Updates (Critical/High)**

```bash
# For critical vulnerabilities, update immediately
npm update package-name

# Or use specific version
npm install package-name@latest

# Python
pip install --upgrade package-name

# Or specific version
pip install package-name==x.y.z
```

**Scheduled Updates (Medium/Low)**

```yaml
# Schedule regular dependency updates
# .github/workflows/dependency-updates.yml
name: Weekly Dependency Updates

on:
  schedule:
    - cron: '0 9 * * 1'  # Monday at 9 AM
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Update dependencies
        run: |
          npm update
          npm audit fix

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'chore: update dependencies'
          title: 'Weekly dependency updates'
          body: 'Automated dependency updates'
          branch: dependency-updates
          labels: dependencies
```

### Workarounds and Mitigations

**Version Pinning**

```json
// package.json
{
  "dependencies": {
    // Exact version (no updates)
    "vulnerable-package": "1.2.3",

    // Allow patch updates only
    "semi-safe-package": "~1.2.3",

    // Allow minor updates
    "safer-package": "^1.2.3"
  },
  "resolutions": {
    // Force specific version for transitive dependencies
    "transitive-vuln-package": "2.0.0"
  }
}
```

**npm overrides**

```json
{
  "overrides": {
    "vulnerable-package": "2.0.0",
    "parent-package": {
      "vulnerable-dependency": "1.5.0"
    }
  }
}
```

**yarn resolutions**

```json
{
  "resolutions": {
    "vulnerable-package": "2.0.0",
    "**/vulnerable-transitive-dep": "1.5.0"
  }
}
```

**Suppression Files**

```yaml
# .snyk
ignore:
  'SNYK-JS-MINIMIST-559764':
    - '*':
        reason: 'No fix available, not exploitable in our context'
        expires: '2024-12-31'
        created: '2024-01-15'
```

### Alternative Packages

**Finding Alternatives**

```bash
# Search for alternatives
npm search alternative-package

# Check package popularity
npm info package-name

# Review package on npmjs.com
# - Download statistics
# - Last publish date
# - Number of maintainers
# - GitHub stars
# - Open issues
```

**Migration Strategy**

1. Identify alternative packages
2. Review compatibility and features
3. Test in development environment
4. Update code to use new package
5. Run comprehensive tests
6. Deploy to staging
7. Monitor for issues
8. Deploy to production

## Compliance and Reporting

### Vulnerability Reports

**Automated Report Generation**

```python
# generate_security_report.py
import json
import subprocess
from datetime import datetime
from typing import Dict, List

def run_npm_audit() -> Dict:
    """Run npm audit and return results."""
    result = subprocess.run(
        ['npm', 'audit', '--json'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def run_safety_check() -> List[Dict]:
    """Run Safety check and return results."""
    result = subprocess.run(
        ['safety', 'check', '--json'],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout) if result.stdout else []

def generate_report() -> str:
    """Generate comprehensive security report."""
    npm_results = run_npm_audit()
    safety_results = run_safety_check()

    report = f"""
# Security Scan Report
Generated: {datetime.now().isoformat()}

## JavaScript Dependencies (npm audit)
- Total vulnerabilities: {npm_results.get('metadata', {}).get('vulnerabilities', {}).get('total', 0)}
- Critical: {npm_results.get('metadata', {}).get('vulnerabilities', {}).get('critical', 0)}
- High: {npm_results.get('metadata', {}).get('vulnerabilities', {}).get('high', 0)}
- Medium: {npm_results.get('metadata', {}).get('vulnerabilities', {}).get('moderate', 0)}
- Low: {npm_results.get('metadata', {}).get('vulnerabilities', {}).get('low', 0)}

## Python Dependencies (Safety)
- Total vulnerabilities: {len(safety_results)}

## Detailed Findings
"""

    # Add detailed findings
    for vuln_id, vuln in npm_results.get('vulnerabilities', {}).items():
        report += f"\n### {vuln.get('name')} - {vuln.get('severity').upper()}\n"
        report += f"- Version: {vuln.get('range')}\n"
        report += f"- CVE: {', '.join(vuln.get('cves', []))}\n"
        report += f"- Fix: {vuln.get('fixAvailable', 'No fix available')}\n"

    return report

if __name__ == "__main__":
    report = generate_report()
    with open('security-report.md', 'w') as f:
        f.write(report)
    print("Security report generated: security-report.md")
```

### Compliance Tracking

**SLA Compliance**

```yaml
# Define remediation SLAs
slas:
  critical:
    response_time: 24h
    resolution_time: 48h
  high:
    response_time: 72h
    resolution_time: 1week
  medium:
    response_time: 1week
    resolution_time: 1month
  low:
    response_time: 1month
    resolution_time: 3months
```

**Tracking Dashboard**

```javascript
// vulnerability-dashboard.js
const metrics = {
  totalVulnerabilities: 0,
  bySeverity: {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
  },
  byStatus: {
    open: 0,
    inProgress: 0,
    resolved: 0,
    dismissed: 0,
  },
  mttr: 0,  // Mean Time To Remediate
  slaCompliance: 95,  // Percentage
};
```

## Best Practices Summary

**Prevention**
- Enable automated dependency scanning in CI/CD
- Configure Dependabot or equivalent for all repositories
- Run scans on every pull request
- Monitor multiple vulnerability databases
- Keep scanning tools updated

**Detection**
- Use multiple scanning tools for comprehensive coverage
- Scan both direct and transitive dependencies
- Include development and production dependencies
- Scan container images and infrastructure code
- Monitor continuously, not just at build time

**Remediation**
- Prioritize based on severity and exploitability
- Update dependencies regularly (weekly for non-critical)
- Test updates thoroughly before production deployment
- Document suppression decisions with expiration dates
- Track remediation metrics and SLA compliance

**Governance**
- Establish clear remediation SLAs
- Assign ownership for vulnerability management
- Conduct regular security reviews
- Maintain audit trails for compliance
- Train developers on secure dependency management

## Resources

**Tools**
- GitHub Dependabot: https://docs.github.com/en/code-security/dependabot
- Snyk: https://snyk.io/
- npm audit: https://docs.npmjs.com/cli/v8/commands/npm-audit
- Safety: https://pyup.io/safety/
- OWASP Dependency-Check: https://owasp.org/www-project-dependency-check/
- Trivy: https://aquasecurity.github.io/trivy/

**Vulnerability Databases**
- National Vulnerability Database (NVD): https://nvd.nist.gov/
- GitHub Advisory Database: https://github.com/advisories
- Snyk Vulnerability DB: https://snyk.io/vuln/
- OSV (Open Source Vulnerabilities): https://osv.dev/

**Standards and Guidelines**
- OWASP Dependency Management Cheat Sheet
- NIST Software Supply Chain Security Guidance
- CIS Software Supply Chain Security Guide
