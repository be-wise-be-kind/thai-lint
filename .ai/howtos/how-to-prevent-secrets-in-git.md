# How to Prevent Secrets in Git

**Purpose**: Step-by-step guide for implementing pre-commit hooks and secrets scanning to prevent credentials from entering version control

**Scope**: Git repositories requiring automated secrets prevention for all commit operations

**Overview**: Provides hands-on instructions for setting up comprehensive secrets prevention using pre-commit hooks and automated scanning tools. Covers installation of gitleaks or detect-secrets, configuration of .gitignore patterns, creation of .env.example templates, and verification testing. Includes troubleshooting steps, team rollout strategies, and integration with existing workflows. Ensures secrets never enter version control through automated prevention at commit time.

**Dependencies**: Git, Python or Node.js, pre-commit framework, gitleaks or detect-secrets

**Exports**: Working secrets prevention setup, pre-commit configuration, security patterns, team processes

**Related**: secrets-management.md, .gitignore.security.template, .env.example.template

**Implementation**: Multi-layered prevention using pre-commit hooks, pattern matching, and developer education

---

## Overview

This guide walks you through setting up automated secrets detection that prevents API keys, passwords, tokens, and other sensitive information from being committed to your Git repository. You'll install pre-commit hooks that scan every commit for secrets before allowing it to proceed.

**Time Required**: 30-45 minutes
**Difficulty**: Intermediate
**Prerequisites**:
- Git repository (local or cloned)
- Python 3.7+ or Node.js 14+
- Command line access
- Administrative access to repository

## What You'll Accomplish

By the end of this guide, you'll have:
- Pre-commit hooks installed and configured
- Secrets scanning tool (gitleaks or detect-secrets) running automatically
- Comprehensive .gitignore patterns for security
- .env.example template for team guidance
- Tested and verified secrets prevention
- Team rollout documentation

## Step 1: Choose Your Secrets Scanner

### Option A: Gitleaks (Recommended for Most Projects)

**Pros**:
- Fast scanning (Go-based)
- Comprehensive default rules
- Active development
- Low false positives

**Best for**: General purpose, multi-language projects

### Option B: detect-secrets (Recommended for Python Projects)

**Pros**:
- Advanced entropy detection
- Baseline management
- Lower false positives with tuning
- Strong Python integration

**Best for**: Python-heavy projects, teams wanting fine-grained control

**For this guide, we'll use gitleaks**. detect-secrets setup is similar with different installation commands.

## Step 2: Install Pre-commit Framework

The pre-commit framework manages Git hooks and runs checks before commits.

### Installation

**macOS/Linux:**
```bash
# Using pip
pip install pre-commit

# Or using Homebrew (macOS)
brew install pre-commit

# Verify installation
pre-commit --version
```

**Windows:**
```powershell
# Using pip
pip install pre-commit

# Verify installation
pre-commit --version
```

### Initialize in Your Repository

```bash
# Navigate to your repository
cd /path/to/your/repo

# Verify you're in a Git repository
git status

# Install pre-commit hooks
pre-commit install
```

You should see:
```
pre-commit installed at .git/hooks/pre-commit
```

## Step 3: Configure Gitleaks

Create a pre-commit configuration file:

```bash
# Create .pre-commit-config.yaml
touch .pre-commit-config.yaml
```

Add the following configuration:

```yaml
# .pre-commit-config.yaml
repos:
  # Gitleaks for secrets detection
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  # Additional helpful pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      # Prevent committing large files
      - id: check-added-large-files
        args: ['--maxkb=500']

      # Detect private keys
      - id: detect-private-key

      # Check for merge conflicts
      - id: check-merge-conflict

      # Check YAML syntax
      - id: check-yaml
        exclude: ^\.github/workflows/

      # Check JSON syntax
      - id: check-json

      # Trim trailing whitespace
      - id: trailing-whitespace

      # Fix end of files
      - id: end-of-file-fixer
```

### Install the Hooks

```bash
# Install all configured hooks
pre-commit install

# Run against all files to test (optional)
pre-commit run --all-files
```

## Step 4: Configure Gitleaks Rules (Optional)

Create a custom gitleaks configuration to reduce false positives:

```bash
# Create .gitleaks.toml
touch .gitleaks.toml
```

Add configuration:

```toml
# .gitleaks.toml
title = "Gitleaks Configuration"

[extend]
# Use default rules as a base
useDefault = true

[[rules]]
id = "generic-api-key"
description = "Generic API Key"
regex = '''(?i)(?:api|key|token|secret)['"\s]*[:=]\s*['"]?[a-zA-Z0-9_\-]{32,}['"]?'''
tags = ["api", "key", "secret"]

[[rules]]
id = "aws-access-key"
description = "AWS Access Key ID"
regex = '''AKIA[0-9A-Z]{16}'''
tags = ["aws", "credentials"]

[[rules]]
id = "github-token"
description = "GitHub Personal Access Token"
regex = '''ghp_[0-9a-zA-Z]{36}'''
tags = ["github", "token"]

[[rules]]
id = "slack-token"
description = "Slack Token"
regex = '''xox[baprs]-[0-9a-zA-Z-]{10,72}'''
tags = ["slack", "token"]

[[rules]]
id = "private-key"
description = "Private Key"
regex = '''-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----'''
tags = ["private-key"]

[[rules]]
id = "database-connection-string"
description = "Database Connection String with Password"
regex = '''(?i)(postgresql|mysql|mongodb|mssql):\/\/[^\s]+:[^\s]+@[^\s]+'''
tags = ["database", "credentials"]

[allowlist]
description = "Allowlist for false positives"

# Allowlist specific file paths
paths = [
  '''^\.env\.example$''',
  '''^\.env\.template$''',
  '''README\.md$''',
  '''\.gitleaks\.toml$''',
  '''^docs/''',
]

# Allowlist specific regex patterns
regexes = [
  '''placeholder''',
  '''example\.com''',
  '''your-.*-here''',
  '''<.*>''',
  '''TODO''',
  '''FIXME''',
  '''XXX''',
]

# Allowlist specific commits (use for historical commits if needed)
commits = []
```

Update .pre-commit-config.yaml to use custom config:

```yaml
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.18.0
  hooks:
    - id: gitleaks
      args: ['--config=.gitleaks.toml']
```

## Step 5: Create Security .gitignore Patterns

Create or update your .gitignore with security patterns:

```bash
# Backup existing .gitignore if it exists
cp .gitignore .gitignore.backup 2>/dev/null || true

# Add security patterns
cat >> .gitignore << 'EOF'

# ========================================
# Security - Sensitive Files
# ========================================

# Environment files with secrets
.env
.env.local
.env.*.local
.env.production
.env.development
.env.test
*.env

# Credential files
*.pem
*.key
*.p12
*.pfx
*.keystore
*.jks
credentials.json
client_secret*.json
service-account*.json
*-credentials.json

# Configuration with secrets
config/secrets.yml
config/database.yml
config/production.yml
secrets.yaml
secrets.json
application-secrets.properties

# Cloud provider credentials
.aws/credentials
.azure/credentials
.gcloud/credentials
gcp-key.json
aws-credentials.json

# Certificate files
*.crt
*.cer
*.der

# Database files
*.sqlite
*.sqlite3
*.db

# SSH keys
id_rsa
id_dsa
id_ecdsa
id_ed25519

# Log files (may contain secrets)
*.log
logs/
*.log.*
npm-debug.log*
yarn-debug.log*
yarn-error.log*

EOF
```

## Step 6: Create .env.example Template

Create a template that shows required environment variables without exposing secrets:

```bash
# Create .env.example
cat > .env.example << 'EOF'
# ========================================
# Application Configuration
# ========================================

# Application Settings
APP_NAME=my-application
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost:3000

# IMPORTANT: Copy this file to .env and fill in actual values
# .env is gitignored and will not be committed

# ========================================
# Security
# ========================================

# Application secret key
# Generate with: openssl rand -hex 32
APP_SECRET_KEY=<generate-with-openssl-rand-hex-32>

# JWT Secret
# Generate with: openssl rand -hex 64
JWT_SECRET=<generate-with-openssl-rand-hex-64>
JWT_EXPIRATION=3600

# ========================================
# Database
# ========================================

DATABASE_TYPE=postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=app_db
DATABASE_USER=<your-database-username>
DATABASE_PASSWORD=<your-secure-password>

# Alternative: Full connection URL
# DATABASE_URL=postgresql://user:password@localhost:5432/app_db

# ========================================
# Redis Cache
# ========================================

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=<your-redis-password>
REDIS_DB=0

# ========================================
# AWS Services
# ========================================

AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
AWS_S3_BUCKET=<your-bucket-name>

# ========================================
# Email Service (SendGrid example)
# ========================================

SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<your-sendgrid-api-key>
EMAIL_FROM=noreply@example.com

# ========================================
# Third-party APIs
# ========================================

# Stripe
STRIPE_PUBLISHABLE_KEY=<pk_test_...>
STRIPE_SECRET_KEY=<sk_test_...>
STRIPE_WEBHOOK_SECRET=<whsec_...>

# Google OAuth
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-client-secret>

# ========================================
# Monitoring
# ========================================

SENTRY_DSN=<your-sentry-dsn>
LOG_LEVEL=info

EOF
```

## Step 7: Test the Setup

### Test 1: Try to Commit a Secret

Create a test file with a fake secret:

```bash
# Create test file
cat > test-secret.txt << 'EOF'
API_KEY=sk_test_abc123xyz789_this_is_a_fake_key_for_testing
EOF

# Try to commit
git add test-secret.txt
git commit -m "Test: attempting to commit secret"
```

**Expected Result**: Pre-commit hook should **block** the commit and show:
```
gitleaks....................................................Failed
- hook id: gitleaks
- exit code: 1

Finding:     API_KEY=sk_test_abc123xyz789_this_is_a_fake_key_for_testing
Secret:      sk_test_abc123xyz789_this_is_a_fake_key_for_testing
File:        test-secret.txt
...
```

**Success!** The secret was blocked.

```bash
# Clean up test file
rm test-secret.txt
git reset
```

### Test 2: Verify .env.example is Allowed

```bash
# .env.example should be allowed
git add .env.example
git commit -m "Add environment variable template"
```

**Expected Result**: Commit should **succeed** because .env.example contains placeholders, not real secrets.

### Test 3: Verify .gitignore Works

```bash
# Create actual .env file (will be ignored)
cat > .env << 'EOF'
DATABASE_PASSWORD=RealPasswordHere123!
API_KEY=sk_live_real_key_12345
EOF

# Check git status
git status
```

**Expected Result**: .env should **not appear** in untracked files (it's gitignored).

```bash
# Clean up
rm .env
```

## Step 8: Handle Existing Secrets (If Any)

If pre-commit finds secrets in your repository:

### Option 1: Remove from Latest Commit

```bash
# Edit the file and remove the secret
vim file-with-secret.txt

# Amend the commit
git add file-with-secret.txt
git commit --amend
```

### Option 2: Remove from Git History

**WARNING**: This rewrites history. Coordinate with your team.

```bash
# Install BFG Repo-Cleaner
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar

# Create passwords file
cat > passwords.txt << 'EOF'
sk_live_abc123xyz789
MySecretPassword123
EOF

# Clean the repository
java -jar bfg-1.14.0.jar --replace-text passwords.txt .git

# Force garbage collection
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (WARNING: destructive)
git push origin --force --all
```

**IMPORTANT**: After cleaning history:
1. Revoke the exposed credentials immediately
2. Generate new credentials
3. All team members must re-clone the repository

## Step 9: Team Rollout

### Create Documentation

Create SECRETS_PREVENTION.md in your repository:

```markdown
# Secrets Prevention Setup

## For New Team Members

1. Install pre-commit:
   ```bash
   pip install pre-commit
   ```

2. Install the hooks:
   ```bash
   pre-commit install
   ```

3. Copy environment template:
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

4. Verify setup:
   ```bash
   pre-commit run --all-files
   ```

## What This Prevents

- API keys and tokens
- Database passwords
- Private keys and certificates
- AWS credentials
- Any hardcoded secrets

## If You Need to Commit Something Flagged

1. Verify it's not actually a secret
2. Add to .gitleaks.toml allowlist if legitimate
3. Never use --no-verify to bypass checks

## Getting Help

Contact the security team if you have questions.
```

### Notify Team

Send team notification:

```
Subject: New Security Requirement: Secrets Prevention

Team,

We've implemented automated secrets scanning to prevent credentials
from being committed to our repository.

ACTION REQUIRED:
1. Pull the latest changes
2. Run: pip install pre-commit
3. Run: pre-commit install

What this means:
- Commits with secrets will be automatically blocked
- Use .env files (not committed) for local credentials
- Follow the .env.example template for required variables

Documentation: See SECRETS_PREVENTION.md in the repository

Questions? Contact the security team.
```

## Step 10: CI/CD Integration (Optional)

Add secrets scanning to your CI/CD pipeline as a safety net:

```yaml
# .github/workflows/secrets-scan.yml
name: Secrets Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Troubleshooting

### Issue: Pre-commit Not Running

**Solution**:
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Verify hooks are installed
ls -la .git/hooks/pre-commit
```

### Issue: Too Many False Positives

**Solution**: Update .gitleaks.toml allowlist:
```toml
[allowlist]
regexes = [
  '''your-false-positive-pattern''',
]
```

### Issue: Hook is Slow

**Solution**: Gitleaks only scans changed files by default. If slow:
```yaml
# In .pre-commit-config.yaml
- id: gitleaks
  args: ['--verbose']  # See what's being scanned
```

### Issue: Need to Bypass for Legitimate Reason

**Last Resort Only**:
```bash
# Use --no-verify flag (use sparingly)
git commit --no-verify -m "message"
```

## Verification Checklist

- [ ] Pre-commit framework installed
- [ ] .pre-commit-config.yaml created and configured
- [ ] Gitleaks scanning on every commit
- [ ] .gitignore includes security patterns
- [ ] .env.example template created
- [ ] .env file gitignored (not committed)
- [ ] Tested blocking actual secrets
- [ ] Tested allowing .env.example
- [ ] Team documentation created
- [ ] Team notified and trained
- [ ] CI/CD integration configured (optional)

## Next Steps

1. **Setup Dependency Scanning**: Follow [how-to-setup-dependency-scanning.md](./how-to-setup-dependency-scanning.md)
2. **Configure Code Scanning**: Follow [how-to-configure-code-scanning.md](./how-to-configure-code-scanning.md)
3. **Review Full Documentation**: See [secrets-management.md](../docs/secrets-management.md)

## Additional Resources

- Gitleaks Documentation: https://github.com/gitleaks/gitleaks
- Pre-commit Documentation: https://pre-commit.com/
- detect-secrets Alternative: https://github.com/Yelp/detect-secrets
- OWASP Secrets Management: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
