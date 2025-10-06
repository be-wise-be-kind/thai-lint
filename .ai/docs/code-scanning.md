# Code Scanning

**Purpose**: Comprehensive guide for implementing static analysis and automated security code review in development workflows

**Scope**: All code repositories requiring automated security analysis, vulnerability detection, and code quality enforcement

**Overview**: Establishes comprehensive strategies for implementing static application security testing (SAST) and automated code review across development workflows. Covers static analysis tools for multiple languages, security linters, code quality scanners, and integration with CI/CD pipelines. Includes detailed configurations for GitHub Advanced Security CodeQL, Semgrep, language-specific security linters, and custom rule development. Provides specific patterns for different vulnerability types, security standards enforcement, and remediation workflows.

**Dependencies**: GitHub Advanced Security, CodeQL, Semgrep, language-specific linters (Bandit, ESLint, etc.)

**Exports**: Code scanning configurations, security rules, vulnerability detection patterns, remediation workflows

**Related**: how-to-configure-code-scanning.md, github-workflow-security.yml.template, SECURITY_STANDARDS.md

**Implementation**: Multi-layered security analysis combining automated scanning, custom rules, and continuous monitoring

---

## Overview

Code scanning automates the detection of security vulnerabilities, coding errors, and quality issues in source code before they reach production. Unlike dependency scanning which focuses on third-party libraries, code scanning analyzes your own code for security flaws, common vulnerabilities, and adherence to security best practices. This proactive approach catches issues during development when they're easiest and cheapest to fix.

## Understanding Code Scanning

### Types of Analysis

**Static Application Security Testing (SAST)**
- Analyzes source code without executing it
- Identifies security vulnerabilities and code quality issues
- Detects patterns indicative of security flaws
- Provides fix recommendations and remediation guidance

**Semantic Analysis**
- Understands code structure and data flow
- Tracks tainted data through the application
- Identifies complex vulnerability patterns
- Detects logic flaws and business logic vulnerabilities

**Pattern Matching**
- Uses regular expressions and AST patterns
- Identifies specific code patterns
- Fast and efficient for known patterns
- Easily customizable with custom rules

**Data Flow Analysis**
- Tracks data flow through the application
- Identifies sources and sinks of sensitive data
- Detects injection vulnerabilities
- Traces user input to dangerous operations

### Common Vulnerability Categories

**Injection Flaws**
- SQL injection (SQLi)
- Command injection
- LDAP injection
- XML injection
- Expression language injection

**Cross-Site Scripting (XSS)**
- Reflected XSS
- Stored XSS
- DOM-based XSS
- Content injection

**Authentication and Authorization**
- Broken authentication
- Session management flaws
- Insecure direct object references
- Missing function-level access control

**Sensitive Data Exposure**
- Hardcoded credentials
- Unencrypted sensitive data
- Insecure cryptographic storage
- Information disclosure

**Security Misconfiguration**
- Debug mode enabled in production
- Default credentials
- Unnecessary features enabled
- Insecure default configurations

**Insecure Deserialization**
- Unsafe object deserialization
- Remote code execution via deserialization
- Data tampering

**Using Components with Known Vulnerabilities**
- Outdated libraries (covered in dependency scanning)
- Vulnerable code patterns

**Insufficient Logging and Monitoring**
- Missing security event logging
- Inadequate error handling
- Sensitive data in logs

## GitHub Advanced Security and CodeQL

### Overview

GitHub Advanced Security provides enterprise-grade security features including CodeQL, the industry-leading semantic code analysis engine.

**Key Features**
- Deep semantic analysis of code
- Support for 10+ languages
- Pre-built security queries
- Custom query development
- Integration with GitHub Security tab
- SARIF format output
- Automated remediation suggestions

### Setup and Configuration

**Enable GitHub Advanced Security**

For organization-owned repositories:
```bash
# Enable via GitHub CLI
gh api repos/{owner}/{repo}/vulnerability-alerts --method PUT

# Enable code scanning
gh api repos/{owner}/{repo}/code-scanning/default-setup --method PUT
```

**CodeQL Workflow Configuration**

```yaml
# .github/workflows/codeql-analysis.yml
name: "CodeQL Analysis"

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    # Daily at 2 AM
    - cron: '0 2 * * *'

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: ['javascript', 'python', 'typescript']
        # CodeQL supports: cpp, csharp, go, java, javascript, python, ruby, typescript

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: ${{ matrix.language }}
          # Query suite options: default, security-extended, security-and-quality
          queries: security-extended
          # Custom config file
          config-file: ./.github/codeql/codeql-config.yml

      - name: Autobuild
        uses: github/codeql-action/autobuild@v2
        # Or use custom build commands:
        # - run: |
        #     npm ci
        #     npm run build

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
        with:
          category: "/language:${{ matrix.language }}"
          upload: true
```

**CodeQL Configuration File**

```yaml
# .github/codeql/codeql-config.yml
name: "CodeQL Configuration"

# Disable default queries and use only specified queries
disable-default-queries: false

# Additional queries to run
queries:
  - name: security-extended
    uses: security-extended
  - name: security-and-quality
    uses: security-and-quality

# Custom query packs
packs:
  - codeql/javascript-queries
  - codeql/python-queries

# Path filters
paths-ignore:
  - '**/test/**'
  - '**/tests/**'
  - '**/__tests__/**'
  - '**/node_modules/**'
  - '**/vendor/**'
  - '**/*.test.js'
  - '**/*.spec.ts'

paths:
  - 'src/**'
  - 'lib/**'
  - 'app/**'

# Query filters
query-filters:
  - exclude:
      id: js/angular/disabling-sce
      reason: "False positive in our Angular configuration"
```

### Custom CodeQL Queries

**Writing Custom Queries**

```ql
/**
 * @name Hardcoded JWT secret
 * @description Detects hardcoded JWT secrets in code
 * @kind problem
 * @problem.severity error
 * @security-severity 8.0
 * @precision high
 * @id js/hardcoded-jwt-secret
 * @tags security
 *       external/cwe/cwe-798
 */

import javascript

from StringLiteral secret, CallExpr call
where
  call.getCalleeName() = "sign" and
  call.getArgument(1) = secret and
  secret.getValue().length() > 10 and
  not secret.getValue().matches("%process.env%") and
  not secret.getValue().matches("%config.%")
select secret, "Hardcoded JWT secret detected. Use environment variables instead."
```

**Python SQL Injection Detection**

```ql
/**
 * @name SQL injection vulnerability
 * @description Detects potential SQL injection vulnerabilities
 * @kind path-problem
 * @problem.severity error
 * @security-severity 9.0
 * @precision high
 * @id py/sql-injection
 * @tags security
 *       external/cwe/cwe-089
 */

import python
import semmle.python.security.dataflow.SqlInjectionQuery

from SqlInjectionConfiguration config, DataFlow::PathNode source, DataFlow::PathNode sink
where config.hasFlowPath(source, sink)
select sink.getNode(), source, sink,
  "SQL injection vulnerability: user input $@ flows to SQL query.",
  source.getNode(), "here"
```

**Custom Query Pack**

```yaml
# codeql-custom-queries/qlpack.yml
name: custom/security-queries
version: 1.0.0
dependencies:
  codeql/javascript-all: "*"
  codeql/python-all: "*"
suites:
  - name: custom-security
    description: Custom security queries for our codebase
```

### CodeQL Analysis Results

**Viewing Results**

Results appear in:
- GitHub Security tab
- Pull request annotations
- SARIF file output
- API access for automation

**Managing False Positives**

```yaml
# .github/codeql/false-positives.yml
# Dismiss specific alerts
dismissals:
  - alert-id: 12345
    reason: "False positive - input is validated elsewhere"
    expires: 2024-12-31

  - alert-id: 67890
    reason: "Accepted risk - legacy code scheduled for refactor"
    expires: 2024-06-30
```

## Semgrep

### Overview

Semgrep is a fast, open-source static analysis tool with simple pattern-based rules.

**Key Features**
- Fast pattern-based scanning
- Support for 30+ languages
- Simple rule syntax
- Large open-source rule registry
- Custom rule development
- CI/CD integration
- SARIF output

### Installation and Setup

```bash
# Install Semgrep
pip install semgrep

# Or via Homebrew (macOS)
brew install semgrep

# Verify installation
semgrep --version
```

**Basic Usage**

```bash
# Scan with default rules
semgrep --config=auto .

# Scan with specific ruleset
semgrep --config=p/security-audit .

# Scan with OWASP Top 10 rules
semgrep --config=p/owasp-top-ten .

# Scan Python code with Python-specific rules
semgrep --config=p/python .

# Generate JSON output
semgrep --config=auto --json --output=semgrep-results.json .

# Scan with severity threshold
semgrep --config=auto --severity=ERROR .
```

### Configuration

**Semgrep Configuration File**

```yaml
# .semgrep.yml
rules:
  # Detect hardcoded secrets
  - id: hardcoded-api-key
    pattern: |
      api_key = "..."
    message: "Hardcoded API key detected. Use environment variables."
    severity: ERROR
    languages: [python, javascript, typescript]
    metadata:
      category: security
      cwe: "CWE-798: Use of Hard-coded Credentials"
      owasp: "A02:2021 - Cryptographic Failures"

  # SQL injection detection
  - id: sql-injection-risk
    patterns:
      - pattern: execute($QUERY)
      - pattern-inside: |
          $QUERY = f"... {$USER_INPUT} ..."
      - pattern-not: execute($SAFE_QUERY)
    message: "Potential SQL injection vulnerability"
    severity: ERROR
    languages: [python]
    metadata:
      category: security
      cwe: "CWE-089: SQL Injection"

  # Detect eval usage
  - id: dangerous-eval
    pattern: eval($ARG)
    message: "Use of eval() is dangerous and should be avoided"
    severity: WARNING
    languages: [python, javascript]

  # Weak cryptography
  - id: weak-crypto-md5
    patterns:
      - pattern-either:
          - pattern: hashlib.md5(...)
          - pattern: crypto.createHash('md5')
    message: "MD5 is cryptographically broken. Use SHA-256 or better."
    severity: WARNING
    languages: [python, javascript]
    fix: |
      Use hashlib.sha256() or crypto.createHash('sha256') instead

  # XSS prevention
  - id: react-dangerously-set-html
    pattern: |
      <$EL dangerouslySetInnerHTML={{__html: $VAR}} />
    message: "Potential XSS vulnerability via dangerouslySetInnerHTML"
    severity: ERROR
    languages: [typescript, javascript]
    metadata:
      category: security
      cwe: "CWE-79: Cross-site Scripting"

  # Command injection
  - id: command-injection
    patterns:
      - pattern-either:
          - pattern: subprocess.call($CMD, shell=True)
          - pattern: os.system($CMD)
      - pattern-inside: |
          $CMD = f"... {$INPUT} ..."
    message: "Potential command injection vulnerability"
    severity: ERROR
    languages: [python]
    fix: |
      Use subprocess with shell=False and pass command as list
```

**Advanced Rule Patterns**

```yaml
rules:
  # Detect authentication bypass
  - id: auth-bypass
    patterns:
      - pattern-inside: |
          def $FUNC(...):
            ...
      - pattern: |
          if $USER.is_authenticated:
            ...
          else:
            return $RESPONSE
      - pattern-not-inside: |
          if $USER.is_authenticated:
            ...
          else:
            raise $EXCEPTION
    message: "Potential authentication bypass - ensure proper error handling"
    severity: WARNING

  # Detect insecure randomness
  - id: insecure-random
    patterns:
      - pattern-either:
          - pattern: random.random()
          - pattern: Math.random()
      - pattern-inside: |
          $TOKEN = ...
    message: "Using insecure random for security-sensitive operations"
    severity: ERROR
    fix: |
      Use secrets module in Python or crypto.randomBytes in Node.js

  # Detect missing CSRF protection
  - id: missing-csrf-protection
    patterns:
      - pattern: |
          @app.route($ROUTE, methods=["POST"])
          def $FUNC(...):
            ...
      - pattern-not-inside: |
          @csrf_protect
          ...
    message: "POST endpoint missing CSRF protection"
    severity: WARNING
    languages: [python]
```

### GitHub Actions Integration

```yaml
# .github/workflows/semgrep.yml
name: Semgrep Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  semgrep:
    runs-on: ubuntu-latest
    container:
      image: returntocorp/semgrep

    steps:
      - uses: actions/checkout@v3

      - name: Run Semgrep
        run: |
          semgrep scan \
            --config=auto \
            --config=.semgrep.yml \
            --sarif \
            --output=semgrep.sarif

      - name: Upload SARIF file
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: semgrep.sarif

      - name: Semgrep App
        if: github.event_name == 'pull_request'
        run: |
          semgrep ci
        env:
          SEMGREP_APP_TOKEN: ${{ secrets.SEMGREP_APP_TOKEN }}
```

## Language-Specific Security Linters

### Python - Bandit

Bandit finds common security issues in Python code.

**Installation and Usage**

```bash
# Install Bandit
pip install bandit

# Basic scan
bandit -r .

# Generate report
bandit -r . -f json -o bandit-report.json

# Scan with specific tests
bandit -r . -t B201,B301,B302,B303

# Exclude paths
bandit -r . -x ./tests,./venv

# Set severity level
bandit -r . -ll  # Only medium and high severity
```

**Configuration (.bandit)**

```yaml
# .bandit
exclude_dirs:
  - /test
  - /tests
  - /.venv
  - /venv
  - /node_modules

tests:
  - B201  # Flask debug mode
  - B301  # Pickle usage
  - B302  # Marshal usage
  - B303  # MD5 usage
  - B304  # Insecure cipher
  - B305  # Insecure cipher mode
  - B306  # mktemp usage
  - B307  # eval usage
  - B308  # Mark safe usage
  - B309  # HTTPSConnection
  - B310  # URL open
  - B311  # Random usage
  - B312  # Telnet usage
  - B313  # XML parsing
  - B314  # XML element tree
  - B315  # XML expat reader
  - B316  # XML expat builder
  - B317  # XML sax
  - B318  # XML minidom
  - B319  # XML pulldom
  - B320  # XML etree
  - B321  # FTP usage
  - B322  # Input usage
  - B323  # Unverified SSL context
  - B324  # Hashlib

skips:
  - B101  # Assert usage - OK in tests

# Scan with baseline
baseline:
  - ./bandit-baseline.json
```

**CI Integration**

```yaml
# .github/workflows/bandit.yml
name: Bandit Security Scan

on: [push, pull_request]

jobs:
  bandit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Bandit
        run: pip install bandit[toml]

      - name: Run Bandit
        run: |
          bandit -r . -f json -o bandit-report.json
          bandit -r . -f txt

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: bandit-report.json
```

### JavaScript/TypeScript - ESLint with Security Plugins

**Installation**

```bash
npm install --save-dev \
  eslint \
  eslint-plugin-security \
  eslint-plugin-no-secrets \
  @typescript-eslint/parser \
  @typescript-eslint/eslint-plugin
```

**ESLint Configuration**

```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:security/recommended',
  ],
  plugins: ['security', 'no-secrets'],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
  rules: {
    // Security rules
    'security/detect-object-injection': 'error',
    'security/detect-non-literal-regexp': 'warn',
    'security/detect-unsafe-regex': 'error',
    'security/detect-buffer-noassert': 'error',
    'security/detect-child-process': 'error',
    'security/detect-disable-mustache-escape': 'error',
    'security/detect-eval-with-expression': 'error',
    'security/detect-no-csrf-before-method-override': 'error',
    'security/detect-non-literal-fs-filename': 'warn',
    'security/detect-non-literal-require': 'warn',
    'security/detect-possible-timing-attacks': 'error',
    'security/detect-pseudoRandomBytes': 'error',

    // No secrets rules
    'no-secrets/no-secrets': ['error', { tolerance: 4.5 }],

    // General security best practices
    'no-eval': 'error',
    'no-implied-eval': 'error',
    'no-new-func': 'error',
    'no-script-url': 'error',
  },
  overrides: [
    {
      // TypeScript-specific rules
      files: ['**/*.ts', '**/*.tsx'],
      parser: '@typescript-eslint/parser',
      plugins: ['@typescript-eslint'],
      extends: [
        'plugin:@typescript-eslint/recommended',
        'plugin:@typescript-eslint/recommended-requiring-type-checking',
      ],
      parserOptions: {
        project: './tsconfig.json',
      },
      rules: {
        '@typescript-eslint/no-unsafe-assignment': 'error',
        '@typescript-eslint/no-unsafe-member-access': 'error',
        '@typescript-eslint/no-unsafe-call': 'error',
        '@typescript-eslint/no-unsafe-return': 'error',
      },
    },
  ],
};
```

**Package.json Scripts**

```json
{
  "scripts": {
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
    "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx --fix",
    "lint:security": "eslint . --ext .js,.jsx,.ts,.tsx --plugin security"
  }
}
```

### Go - gosec

**Installation and Usage**

```bash
# Install gosec
go install github.com/securego/gosec/v2/cmd/gosec@latest

# Scan current directory
gosec ./...

# Generate report
gosec -fmt=json -out=gosec-report.json ./...

# Scan with specific rules
gosec -include=G401,G402,G403 ./...

# Exclude specific checks
gosec -exclude=G104 ./...

# Set severity threshold
gosec -severity=medium ./...
```

**Configuration (gosec.json)**

```json
{
  "tests": true,
  "exclude": ["G104"],
  "include": [
    "G101",
    "G102",
    "G103",
    "G104",
    "G106",
    "G107",
    "G201",
    "G202",
    "G203",
    "G204",
    "G301",
    "G302",
    "G303",
    "G304",
    "G305",
    "G306",
    "G307",
    "G401",
    "G402",
    "G403",
    "G404",
    "G501",
    "G502",
    "G503",
    "G504",
    "G505",
    "G601"
  ],
  "exclude-dir": "vendor",
  "severity": "medium"
}
```

### Java - SpotBugs with Find Security Bugs

**Maven Configuration**

```xml
<!-- pom.xml -->
<build>
  <plugins>
    <plugin>
      <groupId>com.github.spotbugs</groupId>
      <artifactId>spotbugs-maven-plugin</artifactId>
      <version>4.7.3.5</version>
      <configuration>
        <effort>Max</effort>
        <threshold>Low</threshold>
        <plugins>
          <plugin>
            <groupId>com.h3xstream.findsecbugs</groupId>
            <artifactId>findsecbugs-plugin</artifactId>
            <version>1.12.0</version>
          </plugin>
        </plugins>
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

**Gradle Configuration**

```gradle
plugins {
    id 'com.github.spotbugs' version '5.0.14'
}

spotbugs {
    effort = 'max'
    reportLevel = 'low'
    toolVersion = '4.7.3'
}

dependencies {
    spotbugsPlugins 'com.h3xstream.findsecbugs:findsecbugs-plugin:1.12.0'
}
```

### Ruby - Brakeman

**Installation and Usage**

```bash
# Install Brakeman
gem install brakeman

# Scan Rails application
brakeman

# Generate report
brakeman -o brakeman-report.html

# JSON output
brakeman -f json -o brakeman-report.json

# Set confidence threshold
brakeman -w 2  # Only high and medium confidence

# Interactive mode
brakeman -I
```

## Comprehensive Security Workflow

### Multi-Tool Scanning Pipeline

```yaml
# .github/workflows/comprehensive-security.yml
name: Comprehensive Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 3 * * *'

jobs:
  code-scanning:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        tool: [codeql, semgrep, bandit, eslint]

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        if: matrix.tool == 'eslint'
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Setup Python
        if: matrix.tool == 'bandit'
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run CodeQL
        if: matrix.tool == 'codeql'
        uses: github/codeql-action/init@v2
        with:
          languages: javascript, python
          queries: security-extended

      - name: CodeQL Autobuild
        if: matrix.tool == 'codeql'
        uses: github/codeql-action/autobuild@v2

      - name: CodeQL Analysis
        if: matrix.tool == 'codeql'
        uses: github/codeql-action/analyze@v2

      - name: Run Semgrep
        if: matrix.tool == 'semgrep'
        run: |
          pip install semgrep
          semgrep scan --config=auto --sarif --output=semgrep.sarif

      - name: Run Bandit
        if: matrix.tool == 'bandit'
        run: |
          pip install bandit
          bandit -r . -f json -o bandit-report.json || true

      - name: Run ESLint Security
        if: matrix.tool == 'eslint'
        run: |
          npm ci
          npm run lint:security

      - name: Upload SARIF results
        if: matrix.tool == 'codeql' || matrix.tool == 'semgrep'
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: ${{ matrix.tool }}.sarif
```

### Security Gate for Pull Requests

```yaml
# .github/workflows/security-gate.yml
name: Security Gate

on:
  pull_request:
    branches: [main]

jobs:
  security-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run security scans
        id: scan
        run: |
          # Run multiple security tools
          npm audit --audit-level=high
          semgrep --config=auto --error
          bandit -r . -ll

      - name: Check for blocking issues
        if: failure()
        run: |
          echo "::error::Security scan found blocking issues"
          exit 1

      - name: Comment on PR
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const output = `#### Security Scan Results

            ${{ steps.scan.outcome == 'success' && '✅ All security checks passed' || '❌ Security issues found' }}

            Please review the workflow logs for details.`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            });
```

## Custom Security Rules Development

### Semgrep Custom Rule Template

```yaml
rules:
  - id: custom-security-rule
    pattern: $PATTERN
    message: "Description of the security issue"
    severity: ERROR
    languages: [python, javascript]
    metadata:
      category: security
      cwe: "CWE-XXX: Description"
      owasp: "A0X:2021 - Category"
      confidence: HIGH
      likelihood: HIGH
      impact: HIGH
      subcategory:
        - vuln
      technology:
        - python
        - javascript
    fix: |
      Recommended fix or mitigation
```

### CodeQL Custom Query Template

```ql
/**
 * @name Custom security query
 * @description Detects specific security issue
 * @kind problem
 * @problem.severity error
 * @security-severity 8.0
 * @precision high
 * @id custom/security-issue
 * @tags security
 *       external/cwe/cwe-XXX
 */

import language

from SourceElement source, SinkElement sink
where
  vulnerabilityCondition(source, sink)
select sink, "Security issue message $@", source, "user input"
```

## Best Practices Summary

**Implementation**
- Enable multiple scanning tools for comprehensive coverage
- Run scans on every pull request and push
- Use security-extended or security-and-quality query suites
- Configure path filters to exclude test code
- Set appropriate severity thresholds for blocking builds

**Custom Rules**
- Develop organization-specific security rules
- Document rule rationale and fix guidance
- Test rules against known vulnerable code
- Maintain rule library in version control
- Review and update rules quarterly

**Integration**
- Integrate with GitHub Security tab
- Use SARIF format for standardized reporting
- Automate PR comments with scan results
- Block merges on critical findings
- Track remediation metrics

**Maintenance**
- Review false positives regularly
- Update scanning tools and databases
- Refine custom rules based on findings
- Train team on common vulnerability patterns
- Conduct periodic security reviews

## Resources

**Tools**
- GitHub Advanced Security: https://docs.github.com/en/code-security
- CodeQL: https://codeql.github.com/
- Semgrep: https://semgrep.dev/
- Bandit: https://bandit.readthedocs.io/
- ESLint Security: https://github.com/eslint-community/eslint-plugin-security
- gosec: https://github.com/securego/gosec
- Brakeman: https://brakemanscanner.org/

**Rule Libraries**
- Semgrep Registry: https://semgrep.dev/r
- CodeQL Queries: https://github.com/github/codeql
- OWASP Top 10: https://owasp.org/www-project-top-ten/

**Standards**
- CWE (Common Weakness Enumeration): https://cwe.mitre.org/
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- SANS Top 25: https://www.sans.org/top25-software-errors/
