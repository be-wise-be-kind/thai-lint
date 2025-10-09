# How to Configure Code Scanning

**Purpose**: Step-by-step guide for implementing GitHub CodeQL and Semgrep static analysis security scanning in development workflows

**Scope**: GitHub repositories requiring automated security code review and vulnerability detection in custom code

**Overview**: Provides hands-on instructions for configuring comprehensive code scanning using GitHub CodeQL and Semgrep across multiple programming languages. Covers GitHub Advanced Security setup, CodeQL workflow configuration, custom query development, Semgrep rule creation, and integration with pull request workflows. Includes language-specific scanner setup (Bandit, ESLint), custom rule development, and security gate enforcement. Ensures automated detection of security vulnerabilities in custom code before production.

**Dependencies**: GitHub Advanced Security, GitHub Actions, CodeQL, Semgrep, language-specific linters

**Exports**: Working code scanning setup, security workflows, custom rules, vulnerability detection

**Related**: code-scanning.md, github-workflow-security.yml.template, SECURITY_STANDARDS.md

**Implementation**: Multi-tool scanning approach with automated PR checks and security gates

---

## Overview

This guide walks you through setting up automated security code scanning that analyzes your source code for vulnerabilities, security flaws, and code quality issues. You'll configure GitHub CodeQL for deep semantic analysis and Semgrep for fast pattern-based scanning.

**Time Required**: 45-60 minutes
**Difficulty**: Advanced
**Prerequisites**:
- GitHub repository with admin access
- GitHub Advanced Security enabled (for CodeQL on private repos)
- GitHub Actions enabled
- Source code in supported language (JavaScript, Python, Java, Go, etc.)
- Understanding of CI/CD concepts

## What You'll Accomplish

By the end of this guide, you'll have:
- GitHub CodeQL scanning configured and running
- Semgrep security scanning integrated
- Language-specific security linters (Bandit, ESLint, etc.)
- Custom security rules for your codebase
- Pull request security gates
- Security findings in GitHub Security tab
- Automated remediation suggestions

## Step 1: Enable GitHub Advanced Security

### For GitHub Enterprise Cloud or GitHub Enterprise Server

1. **Organization Level** (Admin)
   - Go to organization **Settings**
   - Click **Code security and analysis**
   - Enable **GitHub Advanced Security**

2. **Repository Level**
   - Go to repository **Settings**
   - Click **Code security and analysis**
   - Enable **GitHub Advanced Security**
   - Enable **CodeQL analysis**

### Verify Access

```bash
# Check if CodeQL is available
gh api repos/{owner}/{repo}/code-scanning/alerts

# Should return [] or existing alerts, not 404
```

## Step 2: Setup CodeQL Analysis

### Quick Setup (Recommended)

GitHub provides default CodeQL setup:

1. **Navigate to Security Tab**
   - Go to repository on GitHub
   - Click **Security** tab
   - Click **Set up code scanning**
   - Click **Set up this workflow** for CodeQL Analysis

2. **Review and Commit**
   - GitHub generates .github/workflows/codeql-analysis.yml
   - Review the configuration
   - Commit to your repository

### Manual Setup (More Control)

Create the workflow file manually:

```bash
# Create workflows directory
mkdir -p .github/workflows

# Create CodeQL workflow
cat > .github/workflows/codeql-analysis.yml << 'EOF'
name: "CodeQL Security Scan"

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    # Weekly scan on Monday at 2 AM
    - cron: '0 2 * * 1'

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
        language: ['javascript', 'python']
        # Supported: cpp, csharp, go, java, javascript, python, ruby, typescript

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v2
        with:
          languages: ${{ matrix.language }}
          # Query suites: default, security-extended, security-and-quality
          queries: security-extended

      # Autobuild attempts to build any compiled languages
      - name: Autobuild
        uses: github/codeql-action/autobuild@v2

      # Alternative: Manual build commands
      # - run: |
      #     just bootstrap
      #     just release

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
        with:
          category: "/language:${{ matrix.language }}"
EOF
```

### Create CodeQL Configuration (Optional but Recommended)

```bash
# Create CodeQL config directory
mkdir -p .github/codeql

# Create config file
cat > .github/codeql/codeql-config.yml << 'EOF'
name: "CodeQL Configuration"

# Don't disable default queries
disable-default-queries: false

# Use extended security queries
queries:
  - uses: security-and-quality

# Path filters
paths-ignore:
  - '**/test/**'
  - '**/tests/**'
  - '**/__tests__/**'
  - '**/node_modules/**'
  - '**/vendor/**'
  - '**/*.test.js'
  - '**/*.spec.ts'
  - '**/*.test.py'

paths:
  - 'src/**'
  - 'lib/**'
  - 'app/**'
  - 'backend/**'
  - 'frontend/**'

# Query filters for suppressing specific queries
query-filters:
  - exclude:
      id: js/angular/disabling-sce
  - exclude:
      id: py/quantum-readiness/cbom/all-cryptographic-algorithms

EOF
```

Update workflow to use config:

```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v2
  with:
    languages: ${{ matrix.language }}
    config-file: ./.github/codeql/codeql-config.yml
```

## Step 3: Setup Semgrep Scanning

Semgrep provides fast, customizable security scanning.

### Create Semgrep Workflow

```bash
cat > .github/workflows/semgrep.yml << 'EOF'
name: Semgrep Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  semgrep:
    name: Scan
    runs-on: ubuntu-latest
    container:
      image: returntocorp/semgrep

    steps:
      - uses: actions/checkout@v3

      - name: Run Semgrep
        run: |
          semgrep scan \
            --config=auto \
            --sarif \
            --output=semgrep.sarif \
            --error \
            --verbose

      - name: Upload SARIF file
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: semgrep.sarif
EOF
```

### Create Semgrep Custom Rules

```bash
# Create Semgrep config
cat > .semgrep.yml << 'EOF'
rules:
  # Detect hardcoded secrets
  - id: hardcoded-secret
    pattern-either:
      - pattern: |
          $KEY = "sk_live_..."
      - pattern: |
          $TOKEN = "ghp_..."
      - pattern: |
          password = "..."
    message: "Hardcoded secret detected. Use environment variables."
    severity: ERROR
    languages: [python, javascript, typescript]
    metadata:
      category: security
      cwe: "CWE-798"
      confidence: HIGH

  # SQL injection detection
  - id: sql-injection-risk
    patterns:
      - pattern-inside: |
          def $FUNC(...):
            ...
      - pattern-either:
          - pattern: execute(f"... {$VAR} ...")
          - pattern: execute("... " + $VAR + " ...")
    message: "Potential SQL injection. Use parameterized queries."
    severity: ERROR
    languages: [python]
    metadata:
      category: security
      cwe: "CWE-089"

  # Command injection
  - id: command-injection
    patterns:
      - pattern-either:
          - pattern: subprocess.call($CMD, shell=True)
          - pattern: os.system($CMD)
      - pattern-inside: |
          $CMD = f"... {$INPUT} ..."
    message: "Potential command injection. Avoid shell=True with user input."
    severity: ERROR
    languages: [python]
    fix: |
      Use subprocess.run(['cmd', 'arg1', arg2], shell=False) instead

  # XSS in React
  - id: react-dangerously-set-html
    pattern: <$EL dangerouslySetInnerHTML={{__html: $HTML}} />
    message: "Potential XSS via dangerouslySetInnerHTML. Sanitize input."
    severity: ERROR
    languages: [typescript, javascript]
    metadata:
      category: security
      cwe: "CWE-79"

  # Weak cryptography
  - id: weak-crypto-md5
    patterns:
      - pattern-either:
          - pattern: hashlib.md5(...)
          - pattern: crypto.createHash('md5')
          - pattern: crypto.createHash("md5")
    message: "MD5 is cryptographically broken. Use SHA-256 or better."
    severity: WARNING
    languages: [python, javascript]
    fix: |
      Use hashlib.sha256() or crypto.createHash('sha256')

  # Insecure random
  - id: insecure-random-for-security
    patterns:
      - pattern-either:
          - pattern: random.random()
          - pattern: Math.random()
      - pattern-inside: |
          $TOKEN = ...
    message: "Using insecure random for security-sensitive data."
    severity: ERROR
    languages: [python, javascript]
    fix: |
      Python: Use secrets module
      JavaScript: Use crypto.randomBytes()

EOF
```

## Step 4: Setup Language-Specific Linters

### For Python: Bandit

```bash
# Create Bandit workflow
cat > .github/workflows/bandit.yml << 'EOF'
name: Bandit Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

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

      - name: Run Bandit scan
        run: |
          bandit -r . -f json -o bandit-report.json || true
          bandit -r . -ll  # Exit with error on medium+ severity

      - name: Upload Bandit report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: bandit-report.json
EOF

# Create Bandit config
cat > .bandit << 'EOF'
[bandit]
exclude_dirs = ['/test', '/tests', '/.venv', '/venv']

tests = [
  'B201', 'B301', 'B302', 'B303', 'B304', 'B305', 'B306',
  'B307', 'B308', 'B309', 'B310', 'B311', 'B312', 'B313',
  'B314', 'B315', 'B316', 'B317', 'B318', 'B319', 'B320',
  'B321', 'B322', 'B323', 'B324', 'B501', 'B502', 'B503',
  'B504', 'B505', 'B506', 'B507', 'B601', 'B602', 'B603',
  'B604', 'B605', 'B606', 'B607', 'B608', 'B609', 'B610',
  'B611', 'B701', 'B702', 'B703'
]

skips = ['B101']  # Assert usage OK in tests
EOF
```

### For JavaScript/TypeScript: ESLint Security

```bash
# Install ESLint security plugins
npm install --save-dev \
  eslint \
  eslint-plugin-security \
  eslint-plugin-no-secrets

# Create/update .eslintrc.js
cat > .eslintrc.js << 'EOF'
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:security/recommended',
  ],
  plugins: ['security', 'no-secrets'],
  rules: {
    'security/detect-object-injection': 'error',
    'security/detect-non-literal-regexp': 'warn',
    'security/detect-unsafe-regex': 'error',
    'security/detect-buffer-noassert': 'error',
    'security/detect-child-process': 'error',
    'security/detect-eval-with-expression': 'error',
    'security/detect-no-csrf-before-method-override': 'error',
    'security/detect-possible-timing-attacks': 'error',
    'security/detect-pseudoRandomBytes': 'error',
    'no-secrets/no-secrets': ['error', { tolerance: 4.5 }],
    'no-eval': 'error',
    'no-implied-eval': 'error',
    'no-new-func': 'error',
  },
};
EOF

# Create ESLint workflow
cat > .github/workflows/eslint-security.yml << 'EOF'
name: ESLint Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  eslint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint security scan
        run: npx eslint . --ext .js,.jsx,.ts,.tsx
EOF
```

## Step 5: Create Comprehensive Security Workflow

Combine all tools into a single security workflow:

```yaml
# .github/workflows/security-comprehensive.yml
name: Comprehensive Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 3 * * *'  # Daily at 3 AM

jobs:
  security-scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        scanner: [codeql, semgrep, bandit, eslint]

    steps:
      - uses: actions/checkout@v3

      # CodeQL
      - name: Initialize CodeQL
        if: matrix.scanner == 'codeql'
        uses: github/codeql-action/init@v2
        with:
          languages: javascript, python
          queries: security-extended

      - name: Autobuild (CodeQL)
        if: matrix.scanner == 'codeql'
        uses: github/codeql-action/autobuild@v2

      - name: Perform CodeQL Analysis
        if: matrix.scanner == 'codeql'
        uses: github/codeql-action/analyze@v2

      # Semgrep
      - name: Run Semgrep
        if: matrix.scanner == 'semgrep'
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/owasp-top-ten
            .semgrep.yml

      # Bandit
      - name: Setup Python
        if: matrix.scanner == 'bandit'
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run Bandit
        if: matrix.scanner == 'bandit'
        run: |
          pip install bandit
          bandit -r . -ll

      # ESLint
      - name: Setup Node.js
        if: matrix.scanner == 'eslint'
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Run ESLint Security
        if: matrix.scanner == 'eslint'
        run: |
          npm ci
          npx eslint . --ext .js,.jsx,.ts,.tsx
```

## Step 6: Setup Pull Request Security Gate

Enforce security checks on pull requests:

```yaml
# .github/workflows/pr-security-gate.yml
name: PR Security Gate

on:
  pull_request:
    branches: [main, develop]

jobs:
  security-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run security checks
        id: security
        run: |
          # Run quick security scans
          npx eslint . --ext .js,.ts --plugin security || echo "eslint_failed=true" >> $GITHUB_OUTPUT
          pip install bandit && bandit -r . -ll || echo "bandit_failed=true" >> $GITHUB_OUTPUT

      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const output = `#### Security Scan Results

            ${{ steps.security.outputs.eslint_failed == 'true' && '❌ ESLint security check failed' || '✅ ESLint passed' }}
            ${{ steps.security.outputs.bandit_failed == 'true' && '❌ Bandit security check failed' || '✅ Bandit passed' }}

            Please review security findings before merging.`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            });

      - name: Fail on security issues
        if: steps.security.outputs.eslint_failed == 'true' || steps.security.outputs.bandit_failed == 'true'
        run: exit 1
```

## Step 7: Configure Branch Protection

Require security checks to pass before merging:

### Via GitHub UI

1. Go to **Settings** > **Branches**
2. Add rule for `main` branch
3. Enable **Require status checks to pass**
4. Select security workflows:
   - CodeQL
   - Semgrep
   - Bandit
   - ESLint Security

### Via GitHub CLI

```bash
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["CodeQL","Semgrep","Bandit"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}'
```

## Step 8: Test the Setup

### Test 1: Verify Workflows Run

```bash
# Commit and push
git add .github/workflows/*.yml
git commit -m "feat: add security scanning workflows"
git push origin main

# Check workflow runs
gh run list
```

### Test 2: Create Intentional Vulnerability

```python
# test_vuln.py
import os

# This should be flagged by Bandit and CodeQL
password = "hardcoded_password_123"
os.system(f"echo {user_input}")  # Command injection
```

```bash
# Commit in a branch
git checkout -b test-security-scanning
git add test_vuln.py
git commit -m "test: security scanning detection"
git push origin test-security-scanning

# Create PR
gh pr create --title "Test Security Scanning" --body "Testing security detection"

# Check if security issues are detected
gh pr checks
```

**Expected**: Security workflows should fail and report vulnerabilities.

```bash
# Clean up
git checkout main
git branch -D test-security-scanning
gh pr close --delete-branch
```

## Step 9: Manage Security Findings

### Triage Process

1. **Review Alerts in Security Tab**
   ```bash
   gh api repos/{owner}/{repo}/code-scanning/alerts
   ```

2. **Assess Severity**
   - Critical: Immediate fix required
   - High: Fix within 1 week
   - Medium: Fix within 1 month
   - Low: Fix as time permits

3. **Remediate or Dismiss**
   ```bash
   # Dismiss false positive
   gh api repos/{owner}/{repo}/code-scanning/alerts/{alert_number} \
     --method PATCH \
     --field state=dismissed \
     --field dismissed_reason=false_positive
   ```

### Document Suppressions

```yaml
# .github/codeql/suppressions.yml
suppressions:
  - alert_id: 123
    reason: "False positive - input is validated before use"
    reviewer: "@security-team"
    expires: "2024-12-31"
```

## Troubleshooting

### Issue: CodeQL Fails to Build

**Solution**: Use manual build commands
```yaml
- name: Manual build
  run: |
    npm ci
    npm run build
```

### Issue: Too Many False Positives

**Solution**: Add to path filters in codeql-config.yml
```yaml
paths-ignore:
  - '**/examples/**'
  - '**/demo/**'
```

### Issue: Semgrep Rules Too Strict

**Solution**: Adjust severity in .semgrep.yml
```yaml
severity: WARNING  # Instead of ERROR
```

## Verification Checklist

- [ ] CodeQL workflow configured and running
- [ ] Semgrep scanning integrated
- [ ] Language-specific linters configured
- [ ] Custom security rules created
- [ ] PR security gate enforced
- [ ] Branch protection rules enabled
- [ ] Security findings visible in Security tab
- [ ] Team trained on triage process
- [ ] Suppression process documented
- [ ] Regular security reviews scheduled

## Next Steps

1. **Review All Documentation**: See [SECURITY_STANDARDS.md](../standards/SECURITY_STANDARDS.md)
2. **Develop Custom Rules**: Create organization-specific security rules
3. **Train Team**: Conduct security scanning training
4. **Monitor Metrics**: Track security finding resolution times
5. **Continuous Improvement**: Refine rules based on findings

## Additional Resources

- CodeQL Documentation: https://codeql.github.com/
- Semgrep Documentation: https://semgrep.dev/
- Bandit: https://bandit.readthedocs.io/
- ESLint Security: https://github.com/eslint-community/eslint-plugin-security
- GitHub Advanced Security: https://docs.github.com/en/code-security
