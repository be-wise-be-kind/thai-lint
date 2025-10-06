# Secrets Management

**Purpose**: Comprehensive guide for preventing, detecting, and managing secrets in version control systems

**Scope**: All development projects requiring secure handling of API keys, passwords, tokens, certificates, and other sensitive credentials

**Overview**: Establishes comprehensive strategies and best practices for secrets management throughout the software development lifecycle. Covers prevention techniques including pre-commit hooks and scanning tools, detection mechanisms for identifying leaked secrets, remediation procedures for handling exposed credentials, and secure storage alternatives. Includes detailed implementation guides for automated secrets scanning, environment variable management, and integration with secret management services. Provides specific patterns for different credential types and environments.

**Dependencies**: Git pre-commit hooks, secrets scanning tools (gitleaks, detect-secrets, git-secrets), environment management tools

**Exports**: Secrets management patterns, scanning configurations, remediation procedures, secure storage strategies

**Related**: how-to-prevent-secrets-in-git.md, .env.example.template, .gitignore.security.template, SECURITY_STANDARDS.md

**Implementation**: Multi-layered defense approach combining prevention, detection, and secure alternatives with automated tooling

---

## Overview

Secrets management is one of the most critical aspects of application security. Hardcoded credentials, API keys, and other secrets in source code represent a significant security risk that can lead to data breaches, unauthorized access, and compliance violations. This document provides comprehensive guidance on preventing secrets from entering your codebase, detecting them when they do, and implementing secure alternatives.

## The Problem with Hardcoded Secrets

### Common Secret Types

**API Keys and Tokens**
- Third-party service API keys (AWS, Stripe, SendGrid, etc.)
- Authentication tokens and bearer tokens
- OAuth client secrets
- Webhook signing secrets
- Service-to-service authentication tokens

**Database Credentials**
- Database connection strings with embedded passwords
- Database usernames and passwords
- Redis passwords and connection URLs
- MongoDB connection strings with credentials

**Encryption Keys and Certificates**
- Private keys for SSL/TLS certificates
- Encryption keys for data at rest
- JWT signing keys
- SSH private keys
- PGP/GPG private keys

**Cloud Provider Credentials**
- AWS access keys and secret access keys
- Azure storage account keys
- Google Cloud service account keys
- Digital Ocean API tokens

**Application Secrets**
- Session secrets and signing keys
- Password reset tokens
- Application-specific secret keys
- Internal API tokens

### Risks and Impact

**Security Breaches**
- Unauthorized access to production systems
- Data exfiltration and exposure
- Lateral movement within infrastructure
- Privilege escalation attacks

**Compliance Violations**
- GDPR data protection requirements
- PCI-DSS for payment card data
- HIPAA for healthcare information
- SOC 2 compliance failures

**Financial Impact**
- Direct financial losses from breaches
- Regulatory fines and penalties
- Incident response and remediation costs
- Reputation damage and customer churn

**Operational Impact**
- Emergency credential rotation
- Service disruptions during remediation
- Developer productivity loss
- Security audit overhead

## Prevention Strategies

### Pre-Commit Hooks

Pre-commit hooks provide the first line of defense by scanning code before it enters version control.

**Installation and Setup**
```bash
# Install pre-commit framework
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package-lock.json

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key
EOF

# Install the hooks
pre-commit install
```

**Benefits of Pre-Commit Hooks**
- Immediate feedback during development
- Prevents secrets from entering version control
- Zero-cost prevention at the source
- Educates developers about security patterns
- Integrates seamlessly into developer workflow

### .gitignore Security Patterns

Prevent sensitive files from being tracked by Git in the first place.

**Essential Patterns**
```gitignore
# Environment files
.env
.env.local
.env.*.local
.env.production
.env.development
.env.test

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

# Configuration with secrets
config/secrets.yml
config/database.yml
config/production.yml
secrets.yaml
application-secrets.properties

# Cloud provider credentials
.aws/credentials
.azure/credentials
.gcloud/credentials
gcp-key.json

# IDE and editor files with secrets
.vscode/settings.json
.idea/workspace.xml

# Backup and temporary files
*.bak
*.backup
*~
.DS_Store
Thumbs.db

# Log files that might contain secrets
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Database files
*.sqlite
*.sqlite3
*.db

# Certificate files
*.crt
*.cer
*.der

# Docker secrets
docker-compose.override.yml
.docker/secrets/
```

**Best Practices**
- Include .gitignore in repository root
- Create language-specific .gitignore files
- Review and update patterns regularly
- Use global .gitignore for IDE-specific files
- Document why patterns exist

### Environment Variable Management

Environment variables provide a secure alternative to hardcoded secrets.

**The .env.example Pattern**
```bash
# .env.example - Safe to commit
# Copy to .env and fill in actual values

# Application
APP_NAME=my-application
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost:3000
APP_SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Database
DATABASE_TYPE=postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=app_db
DATABASE_USER=<your-database-username>
DATABASE_PASSWORD=<your-secure-password>

# Redis Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=<your-redis-password>
REDIS_DB=0

# AWS Services
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-aws-access-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
AWS_S3_BUCKET=<your-bucket-name>

# Email Service
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<your-sendgrid-api-key>

# Third-party APIs
STRIPE_PUBLISHABLE_KEY=<pk_test_...>
STRIPE_SECRET_KEY=<sk_test_...>
STRIPE_WEBHOOK_SECRET=<whsec_...>

# JWT Authentication
JWT_SECRET=<generate-with-openssl-rand-hex-64>
JWT_EXPIRATION=3600

# Monitoring
SENTRY_DSN=<your-sentry-dsn>
```

**Environment Variable Best Practices**
- Never commit actual .env files
- Provide comprehensive .env.example
- Use descriptive placeholder values
- Document required vs. optional variables
- Include example formats and validation rules
- Group related variables together
- Use consistent naming conventions (SCREAMING_SNAKE_CASE)

### Code Review Guidelines

Human review remains essential for catching secrets that automated tools might miss.

**Reviewer Checklist**
- [ ] No hardcoded passwords, API keys, or tokens
- [ ] No database credentials in code or config
- [ ] Environment variables used for all sensitive data
- [ ] No secrets in comments or documentation
- [ ] No secrets in test files or fixtures
- [ ] No secrets in error messages or logs
- [ ] Configuration files use placeholders
- [ ] New secrets added to .env.example

**Patterns to Flag**
```python
# BAD - Hardcoded secrets
API_KEY = "sk_live_abc123xyz789"
DATABASE_URL = "postgresql://user:password@host/db"
SECRET_KEY = "super-secret-key-12345"

# GOOD - Environment variables
API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
```

```javascript
// BAD - Hardcoded secrets
const apiKey = 'sk_live_abc123xyz789';
const dbPassword = 'MySecretPassword123!';

// GOOD - Environment variables
const apiKey = process.env.API_KEY;
const dbPassword = process.env.DB_PASSWORD;
```

## Detection Tools and Techniques

### Gitleaks

Gitleaks is a fast, configurable secrets scanner for Git repositories.

**Installation**
```bash
# macOS
brew install gitleaks

# Linux
wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz
tar -xzf gitleaks_8.18.0_linux_x64.tar.gz
sudo mv gitleaks /usr/local/bin/

# Verify installation
gitleaks version
```

**Basic Usage**
```bash
# Scan current repository
gitleaks detect --source . --verbose

# Scan specific directory
gitleaks detect --source ./src --verbose

# Scan with custom config
gitleaks detect --config .gitleaks.toml --verbose

# Generate baseline to ignore existing findings
gitleaks detect --baseline-path .gitleaks-baseline.json --report-path gitleaks-report.json
```

**Configuration (.gitleaks.toml)**
```toml
title = "Gitleaks Configuration"

[extend]
useDefault = true

[[rules]]
id = "generic-api-key"
description = "Generic API Key"
regex = '''(?i)(?:api|key|token|secret)['"]?\s*[:=]\s*['"]?[a-zA-Z0-9_\-]{32,}['"]?'''
tags = ["api", "key"]

[[rules]]
id = "aws-access-key"
description = "AWS Access Key"
regex = '''AKIA[0-9A-Z]{16}'''
tags = ["aws", "credentials"]

[[rules]]
id = "private-key"
description = "Private Key"
regex = '''-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----'''
tags = ["private-key"]

[[rules]]
id = "database-connection-string"
description = "Database Connection String"
regex = '''(?i)(postgresql|mysql|mongodb):\/\/[^\s]+:[^\s]+@[^\s]+'''
tags = ["database", "credentials"]

[allowlist]
description = "Global allowlist"
paths = [
  '''\.env\.example$''',
  '''\.env\.template$''',
  '''README\.md$''',
  '''\.gitleaks\.toml$''',
]
regexes = [
  '''placeholder''',
  '''example\.com''',
  '''your-.*-here''',
  '''<.*>''',
]
```

**CI/CD Integration**
```yaml
# GitHub Actions
name: Gitleaks Scan
on: [push, pull_request]
jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Detect-Secrets

Yelp's detect-secrets provides advanced secret detection with low false-positive rates.

**Installation and Setup**
```bash
# Install detect-secrets
pip install detect-secrets

# Generate baseline file
detect-secrets scan --baseline .secrets.baseline

# Update baseline
detect-secrets scan --baseline .secrets.baseline --update

# Audit baseline (review findings)
detect-secrets audit .secrets.baseline
```

**Configuration**
```bash
# .secrets.baseline includes configuration
# Customize plugins
detect-secrets scan \
  --baseline .secrets.baseline \
  --disable-plugin KeywordDetector \
  --disable-plugin Base64HighEntropyString
```

**Pre-commit Integration**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: 'package-lock.json|yarn.lock|poetry.lock'
```

### Git-Secrets

AWS's git-secrets prevents committing secrets to Git repositories.

**Installation**
```bash
# macOS
brew install git-secrets

# Linux
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets
sudo make install
```

**Setup**
```bash
# Initialize in repository
git secrets --install

# Register AWS patterns
git secrets --register-aws

# Add custom patterns
git secrets --add 'password\s*=\s*.+'
git secrets --add 'api[_-]?key\s*=\s*.+'

# Scan repository
git secrets --scan
git secrets --scan-history
```

### TruffleHog

TruffleHog searches for secrets in Git history with high-entropy detection.

**Installation and Usage**
```bash
# Install
pip install truffleHog

# Scan repository
trufflehog git https://github.com/your-org/your-repo

# Scan local repository
trufflehog filesystem /path/to/repo

# Scan with custom regex
trufflehog git file://. --regex --rules ./custom-rules.json
```

## Remediation Procedures

### When Secrets Are Detected

**Immediate Actions (Within 1 hour)**

1. **Revoke the Exposed Credential**
   - Immediately disable the compromised credential
   - Generate new replacement credentials
   - Update production systems with new credentials

2. **Assess the Exposure**
   - Determine if the secret was pushed to remote repository
   - Check if the repository is public or private
   - Identify who had access to the repository
   - Review access logs for suspicious activity

3. **Notify Stakeholders**
   - Inform security team
   - Alert affected service owners
   - Document the incident

**Short-term Actions (Within 24 hours)**

4. **Remove Secret from Git History**
```bash
# Using BFG Repo-Cleaner (recommended)
java -jar bfg.jar --replace-text passwords.txt repo.git
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Using git-filter-repo
git filter-repo --path-glob '*.env' --invert-paths
git filter-repo --replace-text expressions.txt

# Force push (DANGEROUS - coordinate with team)
git push origin --force --all
git push origin --force --tags
```

5. **Rotate Additional Credentials**
   - Rotate credentials that might be compromised
   - Update all deployment pipelines
   - Verify new credentials in production

6. **Audit Related Systems**
   - Review logs for unauthorized access
   - Check for data exfiltration
   - Monitor for unusual activity

**Long-term Actions (Within 1 week)**

7. **Post-Incident Review**
   - Document root cause analysis
   - Identify process improvements
   - Update prevention measures
   - Conduct team training

8. **Implement Additional Controls**
   - Add missed patterns to scanning tools
   - Enhance pre-commit hooks
   - Improve code review guidelines
   - Update documentation

### BFG Repo-Cleaner

BFG is the fastest way to clean secrets from Git history.

**Installation**
```bash
# Download BFG
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar
mv bfg-1.14.0.jar bfg.jar
```

**Usage**
```bash
# Create a passwords.txt file
cat > passwords.txt << EOF
sk_live_abc123xyz789
MySecretPassword123
regex:api[_-]?key\s*=\s*.+
EOF

# Clone a mirror of the repository
git clone --mirror https://github.com/your-org/your-repo.git

# Clean the repository
java -jar bfg.jar --replace-text passwords.txt your-repo.git

# Navigate and cleanup
cd your-repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (coordinate with team first)
git push --force
```

**Important Warnings**
- BFG rewrites Git history permanently
- All team members must re-clone the repository
- Coordinate timing with team to avoid conflicts
- Back up repository before cleaning
- Existing clones will be incompatible

## Secure Storage Alternatives

### Environment Variables

Environment variables are the simplest secure alternative for most applications.

**Best Practices**
```bash
# Development: Use .env files (never commit)
# Production: Use platform-specific mechanisms

# Docker
docker run -e DATABASE_URL="postgresql://..." my-app

# Docker Compose
services:
  app:
    environment:
      - DATABASE_URL=${DATABASE_URL}
    env_file:
      - .env

# Kubernetes
kubectl create secret generic app-secrets \
  --from-literal=database-url=postgresql://...

# Systemd
[Service]
Environment="DATABASE_URL=postgresql://..."
```

**Validation and Type Safety**
```python
# Python with pydantic
from pydantic import BaseSettings, SecretStr, PostgresDsn

class Settings(BaseSettings):
    database_url: PostgresDsn
    api_key: SecretStr
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

```typescript
// TypeScript with envalid
import { cleanEnv, str, url, bool } from 'envalid';

const env = cleanEnv(process.env, {
  DATABASE_URL: url(),
  API_KEY: str(),
  DEBUG: bool({ default: false }),
});

export default env;
```

### Secret Management Services

For production systems, use dedicated secret management services.

**AWS Secrets Manager**
```python
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='us-east-1'
    )

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except ClientError as e:
        raise e

# Usage
database_password = get_secret('production/db/password')
```

**HashiCorp Vault**
```python
import hvac

client = hvac.Client(url='https://vault.example.com:8200')
client.auth.approle.login(
    role_id=os.getenv('VAULT_ROLE_ID'),
    secret_id=os.getenv('VAULT_SECRET_ID'),
)

secret = client.secrets.kv.v2.read_secret_version(
    path='database/production',
)
database_password = secret['data']['data']['password']
```

**Azure Key Vault**
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://my-vault.vault.azure.net/",
    credential=credential
)

secret = client.get_secret("database-password")
database_password = secret.value
```

**Google Cloud Secret Manager**
```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
name = "projects/my-project/secrets/database-password/versions/latest"

response = client.access_secret_version(request={"name": name})
database_password = response.payload.data.decode('UTF-8')
```

### Encrypted Configuration Files

For teams that need configuration files, use encrypted storage.

**git-crypt**
```bash
# Install git-crypt
brew install git-crypt  # macOS
apt-get install git-crypt  # Linux

# Initialize in repository
git-crypt init

# Add team members
git-crypt add-gpg-user user@example.com

# Mark files for encryption in .gitattributes
cat > .gitattributes << EOF
secrets/*.yml filter=git-crypt diff=git-crypt
.env.production filter=git-crypt diff=git-crypt
EOF

# Files are automatically encrypted on commit
git add secrets/production.yml
git commit -m "Add encrypted production secrets"

# Other team members unlock with their GPG key
git-crypt unlock
```

**SOPS (Secrets OPerationS)**
```bash
# Install SOPS
brew install sops

# Create encrypted file
sops --encrypt secrets.yaml > secrets.enc.yaml

# Edit encrypted file
sops secrets.enc.yaml

# Decrypt for use
sops --decrypt secrets.enc.yaml > secrets.yaml
```

**Example SOPS Configuration (.sops.yaml)**
```yaml
creation_rules:
  - path_regex: secrets/.*\.yaml$
    kms: 'arn:aws:kms:us-east-1:123456789:key/abc-def-123'
    pgp: 'FBC7B9E2A4F9289AC0C1D4843D16CEE4A27381B4'
```

## Language-Specific Patterns

### Python

**Configuration with python-decouple**
```python
from decouple import config, Csv

# Load from .env
DATABASE_URL = config('DATABASE_URL')
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# With validation
API_KEY = config('API_KEY', default='')
if not API_KEY:
    raise ValueError("API_KEY must be set")
```

**Django Settings**
```python
# settings.py
from pathlib import Path
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# NEVER commit this value
SECRET_KEY = config('DJANGO_SECRET_KEY')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

**FastAPI with pydantic**
```python
from pydantic import BaseSettings, PostgresDsn, validator
from typing import Optional

class Settings(BaseSettings):
    # Database
    postgres_server: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    database_uri: Optional[PostgresDsn] = None

    @validator("database_uri", pre=True)
    def assemble_db_connection(cls, v, values):
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("postgres_user"),
            password=values.get("postgres_password"),
            host=values.get("postgres_server"),
            path=f"/{values.get('postgres_db') or ''}",
        )

    # API Keys
    api_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### JavaScript/TypeScript

**Node.js with dotenv**
```javascript
// Load at application start
require('dotenv').config();

// Access variables
const dbConfig = {
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT || '5432'),
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
};

// Validate required variables
const requiredEnvVars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'API_KEY'];
for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    throw new Error(`Missing required environment variable: ${envVar}`);
  }
}
```

**TypeScript with Type Safety**
```typescript
// env.ts
import { cleanEnv, str, port, url, bool } from 'envalid';

export const env = cleanEnv(process.env, {
  NODE_ENV: str({ choices: ['development', 'test', 'production'] }),
  PORT: port({ default: 3000 }),
  DATABASE_URL: url(),
  API_KEY: str(),
  DEBUG: bool({ default: false }),
});

// Usage in application
import { env } from './env';

console.log(`Server running on port ${env.PORT}`);
```

**React with Create React App**
```javascript
// Must start with REACT_APP_
// .env
REACT_APP_API_URL=https://api.example.com
REACT_APP_GOOGLE_MAPS_KEY=your-key-here

// Usage
const apiUrl = process.env.REACT_APP_API_URL;
const mapsKey = process.env.REACT_APP_GOOGLE_MAPS_KEY;
```

**Next.js Environment Variables**
```javascript
// next.config.js
module.exports = {
  env: {
    // Public variables (exposed to browser)
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};

// Server-side only secrets (never exposed to browser)
// .env.local
DATABASE_URL=postgresql://...
API_SECRET_KEY=sk_live_...

// Usage
// Server-side
const db = process.env.DATABASE_URL;

// Client-side (must use NEXT_PUBLIC_ prefix)
const apiUrl = process.env.NEXT_PUBLIC_API_URL;
```

### Go

**Environment Variables with godotenv**
```go
package main

import (
    "log"
    "os"

    "github.com/joho/godotenv"
)

type Config struct {
    DatabaseURL string
    APIKey      string
    Port        string
}

func LoadConfig() (*Config, error) {
    // Load .env file
    if err := godotenv.Load(); err != nil {
        log.Println("No .env file found")
    }

    config := &Config{
        DatabaseURL: os.Getenv("DATABASE_URL"),
        APIKey:      os.Getenv("API_KEY"),
        Port:        getEnv("PORT", "8080"),
    }

    // Validate required variables
    if config.DatabaseURL == "" {
        return nil, fmt.Errorf("DATABASE_URL is required")
    }

    return config, nil
}

func getEnv(key, fallback string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return fallback
}
```

## Monitoring and Compliance

### Continuous Monitoring

**GitHub Secret Scanning**
- Automatically scans for known secret patterns
- Alerts repository administrators
- Works for public and private repositories (with Advanced Security)
- Integrates with secret scanning partners

**GitGuardian**
- Real-time secret detection
- Historical repository scanning
- Incident management dashboard
- Team collaboration features

**Setup GitHub Secret Scanning**
```yaml
# .github/workflows/secret-scan.yml
name: Secret Scanning
on: [push, pull_request]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Run GitGuardian scan
        uses: GitGuardian/ggshield-action@v1
        env:
          GITHUB_PUSH_BEFORE_SHA: ${{ github.event.before }}
          GITHUB_PUSH_BASE_SHA: ${{ github.event.base }}
          GITHUB_DEFAULT_BRANCH: ${{ github.event.repository.default_branch }}
          GITGUARDIAN_API_KEY: ${{ secrets.GITGUARDIAN_API_KEY }}
```

### Compliance Requirements

**Audit Trails**
- Track all secret access and modifications
- Log authentication attempts
- Monitor unusual access patterns
- Maintain compliance documentation

**Regular Rotation**
```python
# Automated secret rotation
import boto3
from datetime import datetime, timedelta

def rotate_secret_if_needed(secret_name, max_age_days=90):
    client = boto3.client('secretsmanager')

    response = client.describe_secret(SecretId=secret_name)
    last_changed = response['LastChangedDate']

    age = datetime.now(last_changed.tzinfo) - last_changed

    if age > timedelta(days=max_age_days):
        # Trigger rotation
        client.rotate_secret(
            SecretId=secret_name,
            RotationLambdaARN='arn:aws:lambda:...'
        )
        return True

    return False
```

**Compliance Reporting**
- Generate regular security reports
- Document secret management procedures
- Track remediation of findings
- Maintain incident response logs

## Best Practices Summary

**Prevention**
- Use pre-commit hooks for immediate feedback
- Maintain comprehensive .gitignore patterns
- Provide .env.example templates
- Train developers on secret management
- Conduct regular code reviews

**Detection**
- Run multiple scanning tools (gitleaks, detect-secrets)
- Scan on every commit and pull request
- Monitor repository history
- Enable platform secret scanning features
- Review findings promptly

**Storage**
- Use environment variables for local development
- Use secret management services for production
- Encrypt configuration files if needed
- Implement least-privilege access
- Rotate secrets regularly

**Response**
- Have an incident response plan
- Revoke compromised credentials immediately
- Clean Git history when necessary
- Conduct post-incident reviews
- Update prevention measures

## Resources and Tools

**Scanning Tools**
- gitleaks: https://github.com/gitleaks/gitleaks
- detect-secrets: https://github.com/Yelp/detect-secrets
- git-secrets: https://github.com/awslabs/git-secrets
- TruffleHog: https://github.com/trufflesecurity/trufflehog
- GitGuardian: https://www.gitguardian.com/

**Secret Management**
- AWS Secrets Manager: https://aws.amazon.com/secrets-manager/
- HashiCorp Vault: https://www.vaultproject.io/
- Azure Key Vault: https://azure.microsoft.com/en-us/services/key-vault/
- Google Secret Manager: https://cloud.google.com/secret-manager
- Doppler: https://www.doppler.com/

**Git History Cleaning**
- BFG Repo-Cleaner: https://rtyley.github.io/bfg-repo-cleaner/
- git-filter-repo: https://github.com/newren/git-filter-repo

**Encryption**
- git-crypt: https://github.com/AGWA/git-crypt
- SOPS: https://github.com/mozilla/sops
- Sealed Secrets (Kubernetes): https://github.com/bitnami-labs/sealed-secrets

**Documentation**
- OWASP Secrets Management Cheat Sheet
- CIS Benchmarks for secret management
- NIST guidelines on cryptographic key management
