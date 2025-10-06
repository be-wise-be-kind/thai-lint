# Environment Setup - How-To Guides

**Purpose**: Quick reference guide for environment variable management tasks

**Scope**: Common environment variable operations and troubleshooting

**Overview**: Index of how-to guides for environment variable management with direnv and .env files.
    Covers installation, configuration, troubleshooting, and best practices. Quick reference for
    developers setting up new projects or debugging environment variable issues.

---

## Available Guides

This plugin provides automated installation through AGENT_INSTRUCTIONS.md. For manual operations and troubleshooting, refer to the comprehensive documentation.

### Core Documentation

| Document | Description | Time | Difficulty |
|----------|-------------|------|------------|
| environment-variables-best-practices.md | Comprehensive best practices guide | 15 min | Beginner |
| ENVIRONMENT_STANDARDS.md | Standards and requirements | 10 min | Beginner |

### Quick Reference

#### Installation
- Automated via plugin: Follow `AGENT_INSTRUCTIONS.md`
- Manual installation: See environment-variables-best-practices.md

#### Common Tasks

**Setup New Project**
```bash
# Automatic (via plugin)
# Agent will detect and install everything

# Manual
cp .env.example .env
# Edit .env with real values
direnv allow
```

**Add New Variable**
```bash
# 1. Add to .env (not committed)
echo "NEW_VAR=secret_value" >> .env

# 2. Add to .env.example (committed)
echo "NEW_VAR=placeholder_value" >> .env.example
echo "# NEW_VAR: Description of what this variable does" >> .env.example

# 3. direnv will auto-reload
```

**Test Environment Loading**
```bash
# Exit and re-enter directory
cd .. && cd -

# Should see: direnv: loading .envrc
# Check variable loaded
echo $YOUR_VARIABLE
```

**Fix "direnv: error .envrc is blocked"**
```bash
direnv allow
```

**Scan for Committed Secrets**
```bash
# If security plugin installed
gitleaks detect --source . --no-git

# Review findings
cat gitleaks-report.json
```

#### Troubleshooting

**Variables Not Loading**
1. Check direnv installed: `which direnv`
2. Check hook configured: `grep "direnv hook" ~/.bashrc`
3. Check directory allowed: `direnv status`
4. Check .envrc syntax: `cat .envrc`

**direnv Not Found**
```bash
# macOS
brew install direnv

# Ubuntu/Debian
sudo apt install direnv

# Add hook to shell
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc
```

**Wrong Values Loaded**
1. Check .env file format (no spaces around =)
2. Check for duplicate variables
3. Test manually: `direnv exec . env | grep YOUR_VAR`

---

## Best Practices Quick Reference

### ✅ DO
- Commit .env.example with placeholders
- Keep .env in .gitignore
- Use SCREAMING_SNAKE_CASE
- Add comments in .env.example
- Run `direnv allow` after editing .envrc
- Update .env.example when adding variables

### ❌ DON'T
- Never commit .env
- Don't hardcode secrets in code
- Don't use spaces around = in .env
- Don't share .env via Slack/email
- Don't mix prod and dev credentials

---

## Additional Resources

- [direnv official docs](https://direnv.net/)
- [12-Factor App - Config](https://12factor.net/config)
- Plugin documentation: `README.md`
- Validation script: `scripts/validate-env-setup.sh`

---

## Getting Help

1. Run validation: `bash plugins/repository/environment-setup/scripts/validate-env-setup.sh`
2. Check comprehensive guide: `.ai/docs/repository/environment-variables-best-practices.md`
3. Review standards: `.ai/docs/repository/ENVIRONMENT_STANDARDS.md`
4. Check direnv status: `direnv status`
5. Test manual loading: `direnv exec . env`
