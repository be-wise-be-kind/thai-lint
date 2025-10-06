# How to Setup Dependency Scanning

**Purpose**: Step-by-step guide for implementing automated vulnerability detection in project dependencies using GitHub Dependabot and scanning tools

**Scope**: GitHub repositories using npm, pip, Maven, Gradle, or other supported package managers

**Overview**: Provides hands-on instructions for configuring comprehensive dependency scanning across JavaScript, Python, Java, and other ecosystems. Covers GitHub Dependabot setup, npm audit integration, Python Safety configuration, and automated alerting. Includes vulnerability assessment workflows, automated update strategies, and team notification procedures. Ensures continuous monitoring of third-party dependencies for known vulnerabilities.

**Dependencies**: GitHub repository, package manager (npm, pip, Maven, etc.), GitHub Actions (optional)

**Exports**: Working dependency scanning setup, automated alerts, vulnerability tracking, update workflows

**Related**: dependency-scanning.md, github-workflow-security.yml.template, SECURITY_STANDARDS.md

**Implementation**: Automated scanning with alerts, scheduled updates, and vulnerability management workflows

---

## Overview

This guide walks you through setting up automated dependency vulnerability scanning for your project. You'll configure tools that continuously monitor your dependencies for known security vulnerabilities and automatically create pull requests to update vulnerable packages.

**Time Required**: 25-35 minutes
**Difficulty**: Intermediate
**Prerequisites**:
- GitHub repository with admin or security access
- Project using a supported package manager
- Basic understanding of dependencies
- GitHub Actions enabled (for advanced features)

## What You'll Accomplish

By the end of this guide, you'll have:
- GitHub Dependabot configured and running
- Automated vulnerability alerts
- Automated security update pull requests
- Package manager-specific scanning (npm audit or Safety)
- Scheduled dependency update workflows
- Vulnerability tracking and management process

## Step 1: Enable GitHub Dependabot

GitHub Dependabot provides free automated dependency scanning for all public repositories and private repositories with GitHub Advanced Security.

### Enable Dependabot Alerts

1. **Navigate to Repository Settings**
   - Go to your repository on GitHub
   - Click **Settings** tab
   - Click **Code security and analysis** in the left sidebar

2. **Enable Dependabot Alerts**
   - Find "Dependabot alerts" section
   - Click **Enable** button
   - Dependabot will immediately scan your dependencies

3. **Enable Dependabot Security Updates**
   - Find "Dependabot security updates" section
   - Click **Enable** button
   - Dependabot will create PRs to fix vulnerabilities

4. **Verify Configuration**
   - Navigate to **Security** tab
   - Click **Dependabot alerts**
   - You should see scanning in progress or completed

### Using GitHub CLI (Alternative Method)

```bash
# Enable Dependabot alerts
gh api repos/{owner}/{repo}/vulnerability-alerts \
  --method PUT

# Verify enabled
gh api repos/{owner}/{repo}/vulnerability-alerts
```

## Step 2: Configure Dependabot Updates

Create a configuration file to customize Dependabot behavior:

```bash
# Create GitHub workflows directory
mkdir -p .github

# Create Dependabot configuration
cat > .github/dependabot.yml << 'EOF'
version: 2
updates:
  # JavaScript/TypeScript dependencies
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "America/New_York"
    open-pull-requests-limit: 10
    reviewers:
      - "your-team/security"
    assignees:
      - "security-lead"
    labels:
      - "dependencies"
      - "security"
    commit-message:
      prefix: "chore"
      prefix-development: "chore"
      include: "scope"
    # Version update strategies
    versioning-strategy: auto
    # Rebase strategy
    rebase-strategy: auto

  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "python"
    allow:
      - dependency-type: "all"
    # Ignore major version updates for specific packages
    ignore:
      - dependency-name: "django"
        update-types: ["version-update:semver-major"]

  # Docker dependencies
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "docker"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"

EOF
```

### Commit and Push Configuration

```bash
# Add and commit
git add .github/dependabot.yml
git commit -m "chore: configure Dependabot dependency scanning"
git push origin main
```

Dependabot will start scanning within minutes.

## Step 3: Configure npm audit (For JavaScript/TypeScript Projects)

If you're using npm, set up automated npm audit scanning:

### Add npm Scripts

```bash
# Update package.json
cat > package.json.tmp << 'EOF'
{
  "scripts": {
    "audit": "npm audit --audit-level=moderate",
    "audit:fix": "npm audit fix",
    "audit:production": "npm audit --production",
    "audit:report": "npm audit --json > security-audit.json"
  }
}
EOF

# Merge with existing package.json (manually or using jq)
```

### Create npm Audit Workflow

```yaml
# .github/workflows/npm-audit.yml
name: npm Security Audit

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    # Run daily at 2 AM
    - cron: '0 2 * * *'

jobs:
  npm-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run npm audit
        run: npm audit --audit-level=high
        continue-on-error: false

      - name: Generate audit report
        if: always()
        run: npm audit --json > npm-audit-report.json

      - name: Upload audit report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: npm-audit-report
          path: npm-audit-report.json
          retention-days: 30
```

## Step 4: Configure Safety (For Python Projects)

Set up Python dependency scanning with Safety:

### Install Safety

```bash
# Add to requirements-dev.txt or pyproject.toml
echo "safety>=2.3.0" >> requirements-dev.txt

# Or with Poetry
poetry add --group dev safety
```

### Create Safety Configuration

```yaml
# .safety-policy.yml
security:
  ignore-vulnerabilities:
    # Example: Ignore specific CVE with expiration
    # 39621:
    #   reason: "Not exploitable in our configuration"
    #   expires: "2024-12-31"

  continue-on-vulnerability-error: false
  alert-on-unpinned-requirements: true
```

### Create Safety Workflow

```yaml
# .github/workflows/python-safety.yml
name: Python Safety Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'

jobs:
  safety-scan:
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
        run: |
          safety check --json --output safety-report.json
          safety check --continue-on-error

      - name: Upload Safety report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: safety-report
          path: safety-report.json
          retention-days: 30
```

## Step 5: Setup Automated Notifications

Configure notifications for vulnerability alerts:

### Slack Notifications

```yaml
# .github/workflows/security-notifications.yml
name: Security Notifications

on:
  schedule:
    - cron: '0 9 * * 1'  # Weekly on Monday at 9 AM

jobs:
  notify-vulnerabilities:
    runs-on: ubuntu-latest
    steps:
      - name: Get Dependabot alerts
        id: alerts
        run: |
          ALERT_COUNT=$(gh api repos/${{ github.repository }}/dependabot/alerts \
            --jq 'length')
          echo "count=$ALERT_COUNT" >> $GITHUB_OUTPUT
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Send Slack notification
        if: steps.alerts.outputs.count > 0
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              text: "Security Alert",
              attachments: [{
                color: 'danger',
                text: `Repository ${{ github.repository }} has ${{ steps.alerts.outputs.count }} open security vulnerabilities`,
                fields: [{
                  title: 'Action Required',
                  value: 'Review and remediate vulnerabilities in GitHub Security tab'
                }]
              }]
            }
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Email Notifications

Enable email notifications in GitHub:
1. Go to **Settings** > **Notifications**
2. Under **Watching**, check "Email" for "Security alerts"
3. Ensure repository security notifications are enabled

## Step 6: Create Vulnerability Management Process

### Document Response Process

Create VULNERABILITY_RESPONSE.md:

```markdown
# Vulnerability Response Process

## Severity Levels and Response Times

| Severity | Response Time | Resolution Time |
|----------|--------------|-----------------|
| Critical | 24 hours | 48 hours |
| High | 72 hours | 1 week |
| Medium | 1 week | 1 month |
| Low | 1 month | 3 months |

## Process

### 1. Alert Received
- Dependabot creates alert in Security tab
- Team notified via Slack/Email
- Security lead reviews within response SLA

### 2. Triage
- Review vulnerability details
- Assess exploitability in our context
- Determine if affected code is used
- Prioritize based on severity and exposure

### 3. Remediation
- Accept Dependabot PR if available
- Manually update if no automated fix
- Apply workarounds if no patch available
- Document suppression if accepted risk

### 4. Verification
- Test updated dependencies
- Run full test suite
- Deploy to staging
- Monitor for issues

### 5. Documentation
- Document resolution in alert
- Update changelog
- Notify team of updates

## Suppression Policy

Vulnerabilities may be suppressed only if:
1. Not exploitable in our configuration
2. No patch available and workaround applied
3. Accepted risk with management approval
4. Suppression expires within 90 days
5. Documented in .snyk or equivalent
```

## Step 7: Configure Dependabot Auto-merge (Optional)

For low-risk updates, enable auto-merge:

```yaml
# .github/workflows/dependabot-auto-merge.yml
name: Dependabot Auto-merge

on:
  pull_request:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    if: github.actor == 'dependabot[bot]'
    steps:
      - name: Dependabot metadata
        id: metadata
        uses: dependabot/fetch-metadata@v1
        with:
          github-token: "${{ secrets.GITHUB_TOKEN }}"

      - name: Enable auto-merge for patch updates
        if: steps.metadata.outputs.update-type == 'version-update:semver-patch'
        run: gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Enable auto-merge for security patches
        if: steps.metadata.outputs.update-type == 'version-update:semver-patch' && steps.metadata.outputs.severity == 'high'
        run: gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Step 8: Test the Setup

### Test 1: Verify Dependabot is Running

```bash
# Check for Dependabot PRs
gh pr list --author "dependabot[bot]"

# View Dependabot alerts
gh api repos/{owner}/{repo}/dependabot/alerts
```

### Test 2: Trigger Manual Scan

For npm:
```bash
npm audit
```

For Python:
```bash
safety check
```

### Test 3: Create Test Vulnerability

Add an old, vulnerable package temporarily:

```bash
# For npm (example)
npm install lodash@4.17.11

# Check for alerts
npm audit

# Remove test package
npm uninstall lodash
```

## Step 9: Monitor and Maintain

### Weekly Tasks
- [ ] Review new Dependabot alerts
- [ ] Merge approved dependency update PRs
- [ ] Check for stale security issues

### Monthly Tasks
- [ ] Review suppressed vulnerabilities
- [ ] Update vulnerability response documentation
- [ ] Review auto-merge rules
- [ ] Audit dependency update patterns

### Quarterly Tasks
- [ ] Review dependency scanning tools
- [ ] Update Dependabot configuration
- [ ] Conduct team security training
- [ ] Audit all suppressed/ignored vulnerabilities

## Troubleshooting

### Issue: Dependabot Not Creating PRs

**Solution**:
1. Verify Dependabot is enabled in repository settings
2. Check .github/dependabot.yml syntax
3. Ensure package-ecosystem matches your project
4. Check open-pull-requests-limit

### Issue: Too Many Dependabot PRs

**Solution**:
```yaml
# Reduce in .github/dependabot.yml
open-pull-requests-limit: 5

# Group updates
groups:
  production-dependencies:
    dependency-type: "production"
```

### Issue: False Positive Vulnerabilities

**Solution**:
```yaml
# In .github/dependabot.yml
ignore:
  - dependency-name: "package-name"
    versions: ["1.2.3"]
```

### Issue: Workflow Failing

**Solution**:
```bash
# Check workflow logs
gh run list --workflow=npm-audit.yml

# View specific run
gh run view <run-id> --log
```

## Verification Checklist

- [ ] Dependabot alerts enabled
- [ ] Dependabot security updates enabled
- [ ] .github/dependabot.yml configured
- [ ] Package manager scanning configured (npm audit or Safety)
- [ ] GitHub Actions workflows created
- [ ] Notifications configured (Slack/Email)
- [ ] Vulnerability response process documented
- [ ] Team trained on process
- [ ] Auto-merge configured (if desired)
- [ ] Monitoring schedule established

## Next Steps

1. **Configure Code Scanning**: Follow [how-to-configure-code-scanning.md](./how-to-configure-code-scanning.md)
2. **Review Security Standards**: See [SECURITY_STANDARDS.md](../standards/SECURITY_STANDARDS.md)
3. **Setup Advanced Scanning**: Consider Snyk or other commercial tools
4. **Regular Reviews**: Schedule monthly vulnerability review meetings

## Additional Resources

- GitHub Dependabot Documentation: https://docs.github.com/en/code-security/dependabot
- npm audit: https://docs.npmjs.com/cli/v8/commands/npm-audit
- Safety: https://pyup.io/safety/
- Snyk: https://snyk.io/
- OWASP Dependency-Check: https://owasp.org/www-project-dependency-check/
