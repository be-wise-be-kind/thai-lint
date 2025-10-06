# Environment Variables Best Practices

**Purpose**: Comprehensive guide to secure environment variable management with direnv and .env files

**Scope**: Installation, configuration, usage patterns, security practices, and troubleshooting for environment variables

**Overview**: Complete reference for managing environment variables in software projects using direnv for automatic
    loading, .env files for secret storage, and .env.example for team coordination. Covers the why behind environment
    variables, installation procedures for all major operating systems, security best practices, common patterns,
    and troubleshooting guidance. Based on the 12-Factor App methodology and production-tested patterns.

**Dependencies**: Git repository, direnv, bash/zsh/fish shell

**Exports**: Knowledge of environment variable best practices, direnv usage, secure secret management

**Related**: ENVIRONMENT_STANDARDS.md, .envrc, .env.example, Security Standards Plugin

**Implementation**: Template-based setup with automatic loading and git integration

---

## Why Environment Variables Matter

### The Problem We're Solving

When building applications, you need different configuration for different environments:

1. **API Keys** - OpenAI, AWS, Notion, Stripe keys differ between dev/staging/prod
2. **Database Credentials** - Local postgres vs production RDS
3. **Service URLs** - localhost:3000 vs https://api.production.com
4. **Feature Flags** - Enable debug mode in dev, disable in prod
5. **Secrets** - JWT signing keys, encryption keys, webhook secrets

**Without proper environment variable management:**
- ❌ Secrets get hardcoded in source files
- ❌ Credentials accidentally committed to git
- ❌ Different developers have different configurations
- ❌ Production secrets exposed in development
- ❌ Manual `export` commands required every terminal session
- ❌ Team members don't know what variables are needed

### The Solution

**Environment Variables + direnv + .env files**

This combination provides:
- ✅ Automatic environment loading when you `cd` into project
- ✅ Secrets stored securely in gitignored .env file
- ✅ Team coordination via committed .env.example template
- ✅ Separation of config from code (12-Factor App principle)
- ✅ Easy switching between environments
- ✅ One source of truth for configuration

---

## Core Concepts

### The Three Files

#### 1. `.env` (Gitignored - Contains Secrets)

Your actual secrets. **NEVER commit this file.**

```bash
# .env
API_KEY=sk-1234567890abcdef
DATABASE_URL=postgresql://admin:secure_password@prod-db:5432/app
JWT_SECRET=super_secret_signing_key_min_32_chars
```

#### 2. `.env.example` (Committed - Template)

Template showing what variables are needed. **Safe to commit.**

```bash
# .env.example
API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET=your_jwt_secret_here_min_32_characters
```

#### 3. `.envrc` (Committed - direnv Config)

Tells direnv to load .env. **Safe to commit.**

```bash
# .envrc
dotenv
```

### How It Works

```
1. You cd into project directory
   ↓
2. direnv detects .envrc file
   ↓
3. .envrc says "load .env file"
   ↓
4. Environment variables from .env are loaded
   ↓
5. Your application reads from environment
   ↓
6. When you cd out, variables are unloaded
```

---

## Installation

### Prerequisites

- Git repository initialized
- Command line access
- Package manager (brew, apt, dnf, etc.)

### Quick Install (Automated)

The Environment Setup Plugin automates everything:

```bash
# Via AI agent
"Please configure environment variable handling for this project"

# Agent will:
# 1. Detect your OS
# 2. Install direnv
# 3. Configure shell hook
# 4. Create .envrc, .env.example
# 5. Update .gitignore
# 6. Scan for violations
# 7. Validate setup
```

### Manual Installation

#### Step 1: Install direnv

**macOS (Homebrew)**
```bash
brew install direnv
```

**Ubuntu/Debian**
```bash
sudo apt update
sudo apt install -y direnv
```

**Fedora/RHEL/CentOS**
```bash
sudo dnf install -y direnv
```

**Arch Linux**
```bash
sudo pacman -S direnv
```

**Windows (WSL)**
```bash
# Inside WSL
sudo apt install -y direnv
```

**Windows (Scoop)**
```powershell
scoop install direnv
```

**Generic Linux (curl)**
```bash
curl -sfL https://direnv.net/install.sh | bash
```

#### Step 2: Configure Shell Hook

**Bash**
```bash
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc
```

**Zsh**
```bash
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc
```

**Fish**
```bash
echo 'direnv hook fish | source' >> ~/.config/fish/config.fish
```

**Verify Installation**
```bash
direnv version
# Should output: 2.32.0 or higher
```

#### Step 3: Create Project Files

**Create .envrc**
```bash
echo "dotenv" > .envrc
```

**Create .env.example**
```bash
cat > .env.example << 'EOF'
# Application
APP_NAME=my-project
PORT=3000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# API Keys
API_KEY=your_api_key_here
EOF
```

**Create .env from .env.example**
```bash
cp .env.example .env
# Edit .env with real values
nano .env
```

**Update .gitignore**
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.*.local" >> .gitignore
```

**Allow direnv**
```bash
direnv allow
```

---

## Usage Patterns

### Basic Usage

**Load Environment on cd**
```bash
$ cd my-project
direnv: loading .envrc
direnv: export +API_KEY +DATABASE_URL +PORT
```

**Variables Are Available**
```bash
$ echo $API_KEY
sk-1234567890abcdef

$ echo $DATABASE_URL
postgresql://user:pass@localhost:5432/mydb
```

**Variables Unload on cd Out**
```bash
$ cd ..
direnv: unloading

$ echo $API_KEY
# (empty - variable unloaded)
```

### In Application Code

**Python**
```python
import os

# Read from environment
api_key = os.getenv('API_KEY')
database_url = os.getenv('DATABASE_URL')
port = int(os.getenv('PORT', 3000))  # default value

# Or use python-dotenv for non-direnv environments
from dotenv import load_dotenv
load_dotenv()
```

**Node.js / TypeScript**
```javascript
// Read from environment
const apiKey = process.env.API_KEY;
const databaseUrl = process.env.DATABASE_URL;
const port = parseInt(process.env.PORT || '3000');

// Or use dotenv package
require('dotenv').config();
```

**Go**
```go
import "os"

func main() {
    apiKey := os.Getenv("API_KEY")
    databaseURL := os.Getenv("DATABASE_URL")
}
```

### Adding New Variables

**Step 1: Add to .env (not committed)**
```bash
echo "NEW_SERVICE_TOKEN=secret123" >> .env
```

**Step 2: Add to .env.example (committed)**
```bash
echo "NEW_SERVICE_TOKEN=your_token_here" >> .env.example
```

**Step 3: direnv Auto-Reloads**
```bash
# direnv watches .env and reloads automatically
direnv: loading .envrc
direnv: export +NEW_SERVICE_TOKEN ~PATH
```

### Multiple Environments

**Development .env**
```bash
# .env (for local development)
DATABASE_URL=postgresql://localhost:5432/myapp_dev
API_URL=http://localhost:8000
DEBUG=true
```

**Production .env**
```bash
# .env (on production server)
DATABASE_URL=postgresql://prod-db.amazonaws.com:5432/myapp_prod
API_URL=https://api.myapp.com
DEBUG=false
```

**Environment-Specific Files**
```bash
# .envrc (advanced usage)
dotenv
dotenv_if_exists .env.local           # Personal overrides
dotenv_if_exists .env.development     # Dev-specific
dotenv_if_exists .env.production      # Prod-specific
```

### Local Overrides

**Use .env.local for Personal Settings**
```bash
# .env.local (not committed, in .gitignore)
DATABASE_URL=postgresql://localhost:5433/myapp_dev  # Use different port
LOG_LEVEL=debug                                      # Personal preference
```

**Load in .envrc**
```bash
# .envrc
dotenv
dotenv_if_exists .env.local  # Loads if exists, silent if not
```

---

## Security Best Practices

### Rule #1: Never Commit .env

**Always in .gitignore**
```bash
# .gitignore
.env
.env.local
.env.*.local
```

**Verify .env is Ignored**
```bash
git check-ignore .env
# Should output: .env

# If not ignored:
git rm --cached .env  # Remove from git tracking
git add .gitignore
git commit -m "Ensure .env is gitignored"
```

### Rule #2: Use Strong Secrets

**Generate Secure Secrets**
```bash
# JWT Secret (32+ characters)
openssl rand -base64 32

# API Key (hex format)
openssl rand -hex 32

# UUID
uuidgen
```

**Example .env with Strong Secrets**
```bash
JWT_SECRET=$(openssl rand -base64 32)
API_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)
```

### Rule #3: Separate Environments

**Never Mix Production and Development**

```bash
# ❌ BAD - Mixed environments
DATABASE_URL=postgresql://prod-db.amazonaws.com:5432/app  # Production!
DEBUG=true                                                 # Development!

# ✅ GOOD - Consistent environment
# Development .env
DATABASE_URL=postgresql://localhost:5432/myapp_dev
DEBUG=true
LOG_LEVEL=debug

# Production .env (on prod server)
DATABASE_URL=postgresql://prod-db.amazonaws.com:5432/app
DEBUG=false
LOG_LEVEL=error
```

### Rule #4: Rotate Compromised Secrets

**If .env Was Accidentally Committed:**

1. **Remove from Git**
```bash
git rm --cached .env
git commit -m "Remove accidentally committed .env"
```

2. **Rotate ALL Secrets Immediately**
```bash
# Generate new API keys at service providers
# Update database passwords
# Regenerate JWT secrets
# Update all affected .env files
```

3. **Clean Git History** (Dangerous!)
```bash
# Use git-filter-repo or BFG Repo-Cleaner
# Coordinate with team first!
git filter-repo --path .env --invert-paths
```

4. **Notify Team**
```bash
# Alert all team members
# Ensure everyone updates their .env files
# Update production secrets
```

### Rule #5: Use Placeholder Values in .env.example

**❌ BAD - Real Secrets in .env.example**
```bash
# .env.example
API_KEY=sk-1234567890abcdef  # Real key!
DATABASE_PASSWORD=my_real_password  # Real password!
```

**✅ GOOD - Placeholders Only**
```bash
# .env.example
API_KEY=sk-your_openai_api_key_here
DATABASE_PASSWORD=your_secure_database_password
JWT_SECRET=your_jwt_secret_min_32_characters

# Even better - with descriptions
# OpenAI API Key (get from: https://platform.openai.com/api-keys)
API_KEY=sk-your_openai_api_key_here

# Database Password (alphanumeric, min 12 characters)
DATABASE_PASSWORD=your_secure_database_password
```

### Rule #6: Scan for Committed Secrets

**Use Gitleaks (via Security Plugin)**
```bash
# Scan repository
gitleaks detect --source . --no-git

# If violations found:
cat gitleaks-report.json
```

**Automated Scanning with Pre-commit Hooks**
```yaml
# .pre-commit-config.yaml
- repo: https://github.com/zricethezav/gitleaks
  rev: v8.16.1
  hooks:
    - id: gitleaks
```

---

## Common Patterns

### Service-Specific Variables

**Prefix by Service**
```bash
# ✅ GOOD - Clear ownership
NOTION_API_KEY=secret_123
NOTION_DATABASE_ID=abc-def-123
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
SLACK_CHANNEL=#general
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJalr...
AWS_REGION=us-east-1
```

**❌ BAD - Ambiguous**
```bash
API_KEY=secret_123  # Which API?
TOKEN=abc123  # Which service?
URL=https://...  # What URL?
```

### Feature Flags

**Environment-Based Feature Flags**
```bash
# Development .env
ENABLE_DEBUG_TOOLBAR=true
ENABLE_BETA_FEATURES=true
ENABLE_VERBOSE_LOGGING=true

# Production .env
ENABLE_DEBUG_TOOLBAR=false
ENABLE_BETA_FEATURES=false
ENABLE_VERBOSE_LOGGING=false
```

### Database Connections

**Full URL Format**
```bash
# PostgreSQL
DATABASE_URL=postgresql://username:password@host:port/database

# MySQL
DATABASE_URL=mysql://username:password@host:port/database

# MongoDB
MONGODB_URL=mongodb://username:password@host:port/database

# Redis
REDIS_URL=redis://:password@host:port/database
```

**Component Format**
```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=secure_password
DB_NAME=myapp_dev
```

### Cloud Provider Credentials

**AWS**
```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
AWS_S3_BUCKET=my-app-uploads
```

**Google Cloud Platform**
```bash
GCP_PROJECT_ID=my-project-123456
GCP_SERVICE_ACCOUNT_KEY=/path/to/service-account-key.json
GCS_BUCKET=my-app-storage
```

---

## Troubleshooting

### Issue: direnv not loading environment

**Symptoms**
```bash
$ cd my-project
# No "direnv: loading .envrc" message
$ echo $API_KEY
# Empty
```

**Solutions**

1. **Check direnv installation**
```bash
which direnv
# Should output: /usr/local/bin/direnv or similar

direnv version
# Should output version number
```

2. **Check shell hook**
```bash
# Bash
grep "direnv hook" ~/.bashrc

# Zsh
grep "direnv hook" ~/.zshrc

# If not found, add it:
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc
```

3. **Check directory is allowed**
```bash
direnv status

# If "Found RC allowed false", allow it:
direnv allow
```

4. **Check .envrc exists and syntax**
```bash
cat .envrc
# Should contain at minimum: dotenv

# Test manually
direnv exec . env | grep YOUR_VAR
```

### Issue: Variables have wrong values

**Symptoms**
```bash
$ echo $DATABASE_URL
postgresql://wrong_host:5432/wrong_db
```

**Solutions**

1. **Check .env file format**
```bash
cat .env

# ✅ Correct format (no spaces around =)
API_KEY=value

# ❌ Wrong format (spaces cause issues)
API_KEY = value
API_KEY= value
API_KEY =value
```

2. **Check for duplicate variables**
```bash
# List all variables in .env
grep "^[A-Z]" .env | sort

# Check for duplicates
grep "^[A-Z]" .env | cut -d= -f1 | sort | uniq -d
```

3. **Check load order**
```bash
# If using multiple .env files
cat .envrc

# Last file loaded wins
dotenv
dotenv_if_exists .env.local  # Overrides .env
```

4. **Force reload**
```bash
direnv reload
```

### Issue: .env accidentally committed

**Immediate Actions**

1. **Remove from git tracking**
```bash
git rm --cached .env
git add .gitignore  # Ensure .env is in .gitignore
git commit -m "Remove .env from version control"
```

2. **Rotate ALL secrets immediately**
- Change API keys at provider
- Update database passwords
- Regenerate JWT secrets
- Update production credentials

3. **Alert team members**
```bash
# Notify via Slack/email that secrets were compromised
# Provide new .env file securely (1Password, LastPass, etc.)
```

4. **Consider history cleaning**
```bash
# WARNING: Coordinate with team first!
# Use git-filter-repo or BFG Repo-Cleaner
git filter-repo --path .env --invert-paths
```

### Issue: Permission denied errors

**Symptoms**
```bash
$ direnv allow
bash: /usr/local/bin/direnv: Permission denied
```

**Solutions**
```bash
# Fix permissions
chmod +x /usr/local/bin/direnv

# Or reinstall
brew reinstall direnv  # macOS
sudo apt install --reinstall direnv  # Ubuntu
```

### Issue: Variables not available in IDE

Some IDEs don't load direnv automatically.

**VSCode**
```json
// .vscode/settings.json
{
  "terminal.integrated.shellArgs.osx": ["-l"],
  "terminal.integrated.shellArgs.linux": ["-l"]
}
```

**PyCharm/IntelliJ**
1. Install direnv plugin
2. Or use EnvFile plugin to load .env directly

**Alternative: Use .env loading in code**
```python
# Python
from dotenv import load_dotenv
load_dotenv()

# Node.js
require('dotenv').config();
```

---

## Advanced Usage

### PATH Extensions

**Add project bin/ to PATH**
```bash
# .envrc
dotenv
PATH_add bin
```

**Usage**
```bash
$ ls bin/
my-script.sh

$ my-script.sh  # Available without ./bin/
```

### Layout Commands

**Load language-specific tools**
```bash
# .envrc
dotenv
layout python3  # Activates virtualenv
```

**Use Node.js version**
```bash
# .envrc
dotenv
layout node  # Uses .nvmrc or .node-version
```

### Watch Files

**Reload when specific files change**
```bash
# .envrc
dotenv
watch_file package.json
watch_file requirements.txt
```

### Private Variables (not in .env)

**Computed or derived variables**
```bash
# .envrc
dotenv
export PROJECT_ROOT=$(pwd)
export TIMESTAMP=$(date +%Y%m%d)
```

---

## Team Workflows

### Onboarding New Developer

**Steps for new team member:**

1. Clone repository
```bash
git clone https://github.com/org/project.git
cd project
```

2. Copy .env.example to .env
```bash
cp .env.example .env
```

3. Get secrets from team lead
```bash
# Via 1Password, LastPass, or secure channel
# Update .env with real values
```

4. Allow direnv
```bash
direnv allow
```

5. Verify setup
```bash
env | grep API_KEY
# Should show the key
```

### Adding New Variable

**Process:**

1. Developer adds to their .env
```bash
echo "NEW_VAR=test_value" >> .env
```

2. Developer adds to .env.example
```bash
echo "NEW_VAR=your_value_here" >> .env.example
```

3. Developer commits .env.example
```bash
git add .env.example
git commit -m "Add NEW_VAR to environment"
git push
```

4. Team members pull and update their .env
```bash
git pull
echo "NEW_VAR=my_real_value" >> .env
# direnv auto-reloads
```

### Sharing Secrets Securely

**✅ GOOD Methods:**
- 1Password shared vaults
- LastPass shared folders
- AWS Secrets Manager
- HashiCorp Vault
- Encrypted messaging (Signal, etc.)

**❌ BAD Methods:**
- Email
- Slack messages
- Committing to git
- Plain text files in cloud storage
- Zoom chat

---

## Validation

### Check Setup

**Use validation script**
```bash
bash plugins/repository/environment-setup/scripts/validate-env-setup.sh
```

**Manual checks**
```bash
# 1. direnv installed
which direnv && echo "✓ direnv installed"

# 2. Shell hook configured
grep "direnv hook" ~/.bashrc && echo "✓ Shell hook configured"

# 3. .envrc exists
test -f .envrc && echo "✓ .envrc exists"

# 4. .env.example exists
test -f .env.example && echo "✓ .env.example exists"

# 5. .env excluded from git
grep "^\.env$" .gitignore && echo "✓ .env in .gitignore"

# 6. .env not committed
! git ls-files | grep -q "^\.env$" && echo "✓ .env not in git"

# 7. Directory allowed
direnv status | grep "Found RC allowed true" && echo "✓ Directory allowed"
```

---

## Resources

### Documentation
- [direnv official docs](https://direnv.net/)
- [12-Factor App - Config](https://12factor.net/config)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

### Tools
- [direnv](https://direnv.net/) - Automatic environment loading
- [gitleaks](https://github.com/zricethezav/gitleaks) - Credential scanning
- [dotenv](https://github.com/motdotla/dotenv) - .env loading (Node.js)
- [python-dotenv](https://github.com/theskumar/python-dotenv) - .env loading (Python)

### Plugin Resources
- Plugin README: `plugins/repository/environment-setup/README.md`
- Environment Standards: `ai-content/standards/ENVIRONMENT_STANDARDS.md`
- Validation Script: `scripts/validate-env-setup.sh`

---

## Summary

**Key Takeaways:**

1. ✅ Use .env for secrets (never commit)
2. ✅ Use .env.example for team coordination (commit)
3. ✅ Use direnv for automatic loading
4. ✅ Always add .env to .gitignore
5. ✅ Rotate secrets immediately if compromised
6. ✅ Use strong, unique secrets per environment
7. ✅ Scan for committed secrets regularly
8. ✅ Prefix variables by service (NOTION_API_KEY)
9. ✅ Document variables in .env.example
10. ✅ Share secrets securely (1Password, Vault)

**Remember:** Environment variables are the foundation of secure application configuration. This system makes it easy to get them right from the start.
