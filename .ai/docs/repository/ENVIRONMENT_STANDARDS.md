# Environment Variable Standards

**Purpose**: Standards and requirements for environment variable management in ai-projen projects

**Scope**: Mandatory and recommended practices for environment variables, direnv usage, and secret management

**Overview**: Defines the standards that all ai-projen projects must follow for environment variable management.
    Establishes requirements for file structure, naming conventions, security practices, and direnv configuration.
    Based on 12-Factor App methodology, OWASP security guidelines, and production-tested patterns. Ensures
    consistency across projects and prevents common security vulnerabilities.

**Dependencies**: Git repository, direnv, .env files

**Exports**: Standards compliance requirements, validation criteria, security guidelines

**Related**: environment-variables-best-practices.md, Security Standards Plugin, Pre-commit Hooks Plugin

**Implementation**: Validation-based enforcement with automated checks and manual review

---

## Core Principles

### 1. Separation of Config from Code

**Principle**: Configuration belongs in the environment, not in code.

**Rationale**: From the [12-Factor App](https://12factor.net/config):
> "An app's config is everything that is likely to vary between deploys (staging, production, developer environments, etc). This includes database handles to backing services, credentials to external services, and per-deploy values."

**Implementation**:
- ✅ All configuration in environment variables
- ✅ Code reads from `os.getenv()` or `process.env`
- ❌ No hardcoded values in source code
- ❌ No config files committed with secrets

### 2. Security by Default

**Principle**: Environment variables containing secrets never enter version control.

**Rationale**: Committed secrets are the #1 cause of credential leaks and security breaches.

**Implementation**:
- ✅ .env file in .gitignore
- ✅ Secrets scanned before commit (pre-commit hooks)
- ✅ .env.example contains only placeholders
- ❌ Never commit .env, .env.local, or variants

### 3. Consistency Across Environments

**Principle**: Same variable names across all environments (dev/staging/prod).

**Rationale**: Reduces errors when promoting code between environments.

**Implementation**:
- ✅ DATABASE_URL in dev, staging, and prod
- ✅ Only values differ, not names
- ❌ Don't use DEV_DATABASE_URL and PROD_DATABASE_URL

---

## Required Standards

All ai-projen projects **MUST** implement the following:

### File Structure

**Required Files:**

1. **`.envrc`** (Committed)
   - Contains: `dotenv` command (minimum)
   - Purpose: Tells direnv to load .env
   - Status: Committed to version control

2. **`.env.example`** (Committed)
   - Contains: All variable names with placeholder values
   - Purpose: Template for team members
   - Status: Committed to version control

3. **`.env`** (NOT Committed)
   - Contains: Actual secret values
   - Purpose: Runtime configuration
   - Status: **NEVER** committed to version control

**File Relationships:**
```
.envrc (committed)
  ↓ loads
.env (gitignored)
  ↓ template is
.env.example (committed)
```

### Gitignore Patterns

**Required in .gitignore:**
```gitignore
# Environment files
.env
.env.local
.env.*.local
*.env
.envrc.local
```

**Validation:**
```bash
# Must pass
git check-ignore .env
# Output: .env

# Must fail (not ignored)
git check-ignore .env.example
# Output: (empty)
```

### direnv Configuration

**Minimum .envrc:**
```bash
# Required
dotenv
```

**Allowed Extensions:**
```bash
dotenv
PATH_add bin
dotenv_if_exists .env.local
```

**Forbidden:**
- Secrets directly in .envrc
- Hardcoded values in .envrc
- Source commands to files outside project

### Installation Requirement

**direnv Must Be Installed:**
- Version: 2.28.0 or higher
- Shell hook configured
- Directory allowed (`direnv allow`)

**Validation:**
```bash
# Must pass
command -v direnv
direnv version  # >= 2.28.0
direnv status | grep "Found RC allowed true"
```

---

## Naming Conventions

### Variable Names

**Format:** `SCREAMING_SNAKE_CASE`

**Rules:**
- ✅ All uppercase
- ✅ Underscores between words
- ✅ Letters and numbers only
- ❌ No hyphens
- ❌ No special characters
- ❌ No lowercase

**Examples:**
```bash
# ✅ Correct
API_KEY
DATABASE_URL
JWT_SECRET
AWS_ACCESS_KEY_ID
NOTION_API_KEY

# ❌ Wrong
apiKey              # camelCase
api-key             # hyphens
API.KEY             # dots
api_key             # lowercase
```

### Service Prefixes

**Pattern:** `SERVICE_VARIABLE_NAME`

**Purpose:** Clear ownership and grouping

**Examples:**
```bash
# AWS variables
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
AWS_S3_BUCKET

# Notion variables
NOTION_API_KEY
NOTION_DATABASE_ID
NOTION_WORKSPACE_ID

# Slack variables
SLACK_WEBHOOK_URL
SLACK_BOT_TOKEN
SLACK_CHANNEL
```

### Boolean Variables

**Format:** `ENABLE_FEATURE` or `FEATURE_ENABLED`

**Values:** `true` or `false` (lowercase)

**Examples:**
```bash
ENABLE_DEBUG=true
ENABLE_FEATURE_X=false
DEBUG_MODE_ENABLED=true
VERBOSE_LOGGING_ENABLED=false
```

### URL Variables

**Format:** Full URL with protocol

**Examples:**
```bash
# ✅ Correct - Full URL
DATABASE_URL=postgresql://user:pass@host:5432/db
API_URL=https://api.example.com
REDIS_URL=redis://localhost:6379/0

# ❌ Wrong - Missing protocol
DATABASE_URL=localhost:5432/db
API_URL=api.example.com
```

---

## Security Standards

### Secret Strength

**Minimum Requirements:**

| Type | Minimum Length | Format |
|------|----------------|--------|
| API Keys | 32 characters | Provider-specific |
| JWT Secrets | 32 characters | Random base64 |
| Database Passwords | 16 characters | Alphanumeric + symbols |
| Session Secrets | 32 characters | Random base64 |

**Generation:**
```bash
# JWT Secret (32+ characters)
openssl rand -base64 32

# API Key (hex format)
openssl rand -hex 32

# Password (alphanumeric + symbols)
openssl rand -base64 24 | tr -d "=+/"
```

### Secret Rotation

**Requirements:**
- Secrets **MUST** be rotated if:
  - Accidentally committed to version control
  - Exposed in logs or error messages
  - Team member with access leaves
  - Suspected compromise
  - Every 90 days (recommended)

**Process:**
1. Generate new secret
2. Update production environment
3. Update .env files for all team members
4. Revoke old secret
5. Verify application still works

### Prohibited Practices

**NEVER:**
- ❌ Commit .env file
- ❌ Hardcode secrets in code
- ❌ Share secrets via email/Slack
- ❌ Store secrets in cloud storage (Dropbox, Google Drive)
- ❌ Use same secrets for dev and prod
- ❌ Put real secrets in .env.example
- ❌ Log environment variables
- ❌ Echo secrets in scripts

### Required Scanning

**Pre-commit:**
- Secrets detection (gitleaks, detect-secrets)
- .env file not staged for commit
- .env.example has no real secrets

**Regular:**
- Weekly credential scans
- Monthly security reviews
- Quarterly secret rotation

---

## .env.example Standards

### Structure

**Required Sections:**
```bash
# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# =============================================================================
# AUTHENTICATION & SECURITY
# =============================================================================

# =============================================================================
# EXTERNAL API SERVICES
# =============================================================================
```

### Documentation

**Each Variable Must Have:**

1. **Comment Explaining Purpose**
```bash
# OpenAI API Key for GPT-4 access
OPENAI_API_KEY=sk-your_api_key_here
```

2. **Where to Get It** (for external services)
```bash
# Notion API Key
# Get from: https://www.notion.so/my-integrations
NOTION_API_KEY=secret_your_key_here
```

3. **Format or Example**
```bash
# Database URL
# Format: postgresql://username:password@host:port/database
DATABASE_URL=postgresql://user:pass@localhost:5432/myapp_dev
```

4. **Default Value** (if applicable)
```bash
# Application Port
# Default: 3000
PORT=3000
```

### Placeholder Values

**Format:** `your_value_here` or `placeholder_value`

**Examples:**
```bash
# ✅ Good placeholders
API_KEY=your_api_key_here
DATABASE_PASSWORD=your_secure_password
JWT_SECRET=your_jwt_secret_min_32_chars

# ✅ Also acceptable (shows format)
API_KEY=sk-1234567890abcdef...
DATABASE_URL=postgresql://user:pass@host:5432/dbname
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE

# ❌ Bad - real values
API_KEY=sk-realkeythatworks  # Real!
DATABASE_PASSWORD=admin123  # Weak!
```

---

## Validation Requirements

### Automated Checks

**Pre-commit Hooks:**
```yaml
# Required checks
- .env file not being committed
- .env.example exists
- .env.example has no real secrets
- All secrets pass strength requirements
- No hardcoded values in code
```

**CI/CD Checks:**
```yaml
# Required in CI pipeline
- Environment variables set correctly
- No secrets in code (gitleaks scan)
- .env.example is up to date
```

### Manual Review Checklist

**Before Merging PR:**
- [ ] New variables added to .env.example
- [ ] Placeholder values used (not real secrets)
- [ ] Variables documented with comments
- [ ] .gitignore excludes .env
- [ ] No hardcoded values in code changes
- [ ] Security scan passes (gitleaks)

### Validation Script

**Run before commit:**
```bash
bash plugins/repository/environment-setup/scripts/validate-env-setup.sh
```

**Must pass all checks:**
- ✅ direnv installed
- ✅ Shell hook configured
- ✅ .envrc exists
- ✅ .env.example exists
- ✅ .gitignore excludes .env
- ✅ .env not in git
- ✅ Directory allowed by direnv
- ✅ No gitleaks violations

---

## Recommended Practices

While not strictly required, these practices are **strongly recommended**:

### Local Overrides

**Use .env.local for personal settings:**
```bash
# .envrc
dotenv
dotenv_if_exists .env.local  # Personal overrides

# .gitignore
.env.local
```

**Example .env.local:**
```bash
# Personal development preferences
LOG_LEVEL=debug
DATABASE_URL=postgresql://localhost:5433/myapp_dev  # Different port
```

### Environment-Specific Files

**For multiple environments:**
```bash
# .envrc
dotenv
dotenv_if_exists .env.${NODE_ENV}

# Files (all gitignored except examples)
.env.development
.env.staging
.env.production
.env.development.example  # Committed
.env.production.example   # Committed
```

### Validation in Code

**Fail fast on missing variables:**

**Python:**
```python
import os

def get_required_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Missing required environment variable: {key}")
    return value

DATABASE_URL = get_required_env('DATABASE_URL')
API_KEY = get_required_env('API_KEY')
```

**TypeScript:**
```typescript
function getRequiredEnv(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value;
}

const DATABASE_URL = getRequiredEnv('DATABASE_URL');
const API_KEY = getRequiredEnv('API_KEY');
```

### Type Conversion

**Convert to correct types:**

**Python:**
```python
PORT = int(os.getenv('PORT', '3000'))
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS', '100'))
```

**TypeScript:**
```typescript
const PORT = parseInt(process.env.PORT || '3000', 10);
const DEBUG = process.env.DEBUG === 'true';
const MAX_CONNECTIONS = parseInt(process.env.MAX_CONNECTIONS || '100', 10);
```

---

## Integration Standards

### With Pre-commit Hooks Plugin

**Required Hooks:**
```yaml
- id: check-env-not-committed
  name: Prevent .env from being committed
- id: check-env-example-exists
  name: Ensure .env.example exists
- id: gitleaks
  name: Scan for secrets
```

### With Security Plugin

**Required Integration:**
- Gitleaks scanning enabled
- Violation reports generated
- Pre-commit prevention active

### With Language Plugins

**Python:**
```python
# Use os.getenv() for all environment access
import os
API_KEY = os.getenv('API_KEY')
```

**TypeScript:**
```typescript
// Use process.env for all environment access
const API_KEY = process.env.API_KEY;
```

---

## Compliance Verification

### Self-Assessment Checklist

Use this checklist to verify standards compliance:

#### File Structure
- [ ] .envrc exists and contains `dotenv`
- [ ] .env.example exists with all variables
- [ ] .env exists but is gitignored
- [ ] .gitignore excludes .env patterns

#### direnv Configuration
- [ ] direnv installed (>= 2.28.0)
- [ ] Shell hook configured
- [ ] Directory allowed (`direnv allow` run)
- [ ] Environment loads on cd

#### Naming Conventions
- [ ] All variables use SCREAMING_SNAKE_CASE
- [ ] Service-specific variables prefixed
- [ ] No hyphens or special characters
- [ ] Boolean variables follow pattern

#### Security
- [ ] Secrets meet minimum length requirements
- [ ] .env never committed to git
- [ ] .env.example has only placeholders
- [ ] Gitleaks scan passes
- [ ] Pre-commit hooks configured

#### Documentation
- [ ] Each variable documented in .env.example
- [ ] Comments explain purpose
- [ ] External services include "Get from" URLs
- [ ] Format examples provided

#### Validation
- [ ] Validation script passes
- [ ] CI/CD checks configured
- [ ] Manual review checklist used

### Audit Process

**Quarterly Review:**
1. Run validation script
2. Review .env.example completeness
3. Check secret rotation dates
4. Verify team member access
5. Update documentation

---

## Non-Compliance Remediation

### If Standards Not Met

**Priority 1 (Critical - Fix Immediately):**
- .env file committed to git
- Real secrets in .env.example
- Secrets hardcoded in code
- No .gitignore exclusions

**Priority 2 (High - Fix This Week):**
- direnv not installed
- .env.example missing variables
- Weak secrets (< minimum length)
- No gitleaks scanning

**Priority 3 (Medium - Fix This Sprint):**
- Naming conventions not followed
- Documentation incomplete
- Validation script not passing
- Pre-commit hooks not configured

### Remediation Steps

**For Committed Secrets:**
1. Remove from git immediately
2. Rotate all exposed secrets
3. Clean git history (if necessary)
4. Notify team and update .env files

**For Missing Standards:**
1. Install Environment Setup Plugin
2. Run automated setup
3. Verify validation passes
4. Document any exceptions

---

## Exceptions and Waivers

### When Standards Can Be Relaxed

**Acceptable Exceptions:**
- Legacy systems during migration
- Third-party code with different patterns
- Temporary development environments

**Process for Exception:**
1. Document reason in README.md
2. Create remediation plan
3. Get security team approval
4. Set expiration date

**Example Exception:**
```markdown
## Environment Variable Exception

**Status**: Temporary
**Reason**: Legacy authentication system uses hardcoded config
**Remediation Plan**: Migrate to environment variables by Q2 2025
**Approved By**: Security Team
**Expires**: 2025-06-30
```

---

## Resources

### Standards References
- [12-Factor App - Config](https://12factor.net/config)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)

### Tools
- direnv: https://direnv.net/
- gitleaks: https://github.com/zricethezav/gitleaks
- Environment Setup Plugin: plugins/repository/environment-setup/

### Support
- Validation Script: scripts/validate-env-setup.sh
- Best Practices Guide: docs/environment-variables-best-practices.md
- Plugin README: README.md

---

## Summary

**Key Standards:**

1. ✅ Three-file structure (.env, .env.example, .envrc)
2. ✅ direnv installed and configured
3. ✅ .env always gitignored
4. ✅ SCREAMING_SNAKE_CASE naming
5. ✅ Service-prefixed variables
6. ✅ Strong secrets (32+ characters)
7. ✅ Placeholder values in .env.example
8. ✅ Comprehensive documentation
9. ✅ Automated validation
10. ✅ Security scanning enabled

**Validation:** Run `bash plugins/repository/environment-setup/scripts/validate-env-setup.sh` to verify compliance.

**Remember:** These standards protect your application and your team. Follow them consistently.
