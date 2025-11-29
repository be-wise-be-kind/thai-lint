# SARIF Output Format

**Purpose**: Guide for using SARIF (Static Analysis Results Interchange Format) v2.1.0 output with thailint

**Scope**: SARIF output configuration, CI/CD integration, tool compatibility, and best practices

**Overview**: Comprehensive documentation for thailint's SARIF v2.1.0 output format. Covers command-line
    usage, SARIF document structure, integration with GitHub Code Scanning, Azure DevOps, and VS Code
    SARIF Viewer. Includes practical examples for CI/CD pipelines, Python API usage, and troubleshooting
    guidance. Helps users leverage SARIF for enterprise static analysis workflows and security tooling.

**Dependencies**: thailint CLI, SARIF v2.1.0 specification, optional tools (jq, VS Code SARIF Viewer)

**Exports**: Usage documentation, integration examples, CI/CD templates, troubleshooting guide

**Related**: cli-reference.md, configuration.md, deployment-modes.md

**Implementation**: User guide with practical examples, CI/CD templates, and tool integration patterns

---

## Overview

thailint supports SARIF (Static Analysis Results Interchange Format) v2.1.0 as an output format for all linting commands. SARIF is the OASIS standard for static analysis tool output, enabling seamless integration with modern development platforms.

### What is SARIF?

SARIF (Static Analysis Results Interchange Format) is an industry-standard JSON format for representing static analysis results. Version 2.1.0 is the latest specification maintained by OASIS.

**Key Benefits:**
- **Universal Format**: One format works across all major platforms
- **Rich Metadata**: Includes rule definitions, severity levels, and precise locations
- **Tool Interoperability**: Aggregate results from multiple analysis tools
- **IDE Integration**: Click-to-navigate support in VS Code and other editors

### Platform Support

thailint's SARIF output works with:

| Platform | Integration Type | Documentation |
|----------|-----------------|---------------|
| **GitHub Code Scanning** | Native SARIF upload | [GitHub SARIF Docs](https://docs.github.com/en/code-security/code-scanning) |
| **Azure DevOps** | Pipeline security results | [Azure SARIF Docs](https://docs.microsoft.com/en-us/azure/devops/pipelines/artifacts/sarif) |
| **VS Code SARIF Viewer** | IDE results display | [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=MS-SarifVSCode.sarif-viewer) |
| **GitLab SAST** | Security dashboard | [GitLab SAST Docs](https://docs.gitlab.com/ee/user/application_security/sast/) |

---

## Quick Start

### Basic Usage

All thailint linting commands support `--format sarif`:

```bash
# Nesting depth analysis
thailint nesting --format sarif src/

# File placement validation
thailint file-placement --format sarif .

# SRP violations
thailint srp --format sarif src/

# DRY violations
thailint dry --format sarif src/

# Magic numbers detection
thailint magic-numbers --format sarif src/

# Print statements detection
thailint print-statements --format sarif src/
```

### Save to File

Redirect output to a file for CI/CD integration:

```bash
thailint nesting --format sarif src/ > results.sarif
thailint srp --format sarif src/ > srp-results.sarif
```

### Validate Output

Use `jq` to pretty-print and validate SARIF output:

```bash
# Pretty-print SARIF
thailint nesting --format sarif src/ | jq

# Extract just the results
thailint nesting --format sarif src/ | jq '.runs[0].results'

# Count violations
thailint nesting --format sarif src/ | jq '.runs[0].results | length'
```

---

## SARIF Document Structure

### Overview

thailint produces SARIF v2.1.0 documents with the following structure:

```json
{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "thai-lint",
          "version": "0.5.0",
          "informationUri": "https://github.com/be-wise-be-kind/thai-lint",
          "rules": [...]
        }
      },
      "results": [...]
    }
  ]
}
```

### Document Level

| Field | Description | Example |
|-------|-------------|---------|
| `version` | SARIF specification version | `"2.1.0"` |
| `$schema` | JSON schema URL for validation | Schema URL |
| `runs` | Array of analysis runs | One run per invocation |

### Tool Driver

The `tool.driver` object identifies thailint:

```json
{
  "name": "thai-lint",
  "version": "0.5.0",
  "informationUri": "https://github.com/be-wise-be-kind/thai-lint",
  "rules": [
    {
      "id": "nesting.excessive-depth",
      "shortDescription": {
        "text": "Nesting depth violation"
      }
    }
  ]
}
```

### Results

Each violation becomes a SARIF result:

```json
{
  "ruleId": "nesting.excessive-depth",
  "level": "error",
  "message": {
    "text": "Nesting depth 5 exceeds maximum 4"
  },
  "locations": [
    {
      "physicalLocation": {
        "artifactLocation": {
          "uri": "src/example.py"
        },
        "region": {
          "startLine": 42,
          "startColumn": 9
        }
      }
    }
  ]
}
```

### Rule Definitions

thailint includes rule metadata in the SARIF output:

| Rule ID Pattern | Description |
|----------------|-------------|
| `file-placement` | File placement violation |
| `nesting.*` | Nesting depth violations |
| `srp.*` | Single Responsibility Principle violations |
| `dry.*` | Don't Repeat Yourself violations |
| `magic-number.*` | Magic number violations |
| `print-statements.*` | Print statement violations |

---

## GitHub Code Scanning Integration

### GitHub Actions Workflow

Create `.github/workflows/thailint-sarif.yml`:

```yaml
name: thailint SARIF

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  security-events: write
  contents: read

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install thailint
        run: pip install thailint

      - name: Run thailint nesting analysis
        run: |
          thailint nesting --format sarif src/ > nesting.sarif || true

      - name: Run thailint SRP analysis
        run: |
          thailint srp --format sarif src/ > srp.sarif || true

      - name: Upload SARIF to GitHub
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: nesting.sarif
          category: thailint-nesting

      - name: Upload SRP SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: srp.sarif
          category: thailint-srp
```

### Viewing Results

After the workflow runs:

1. Go to your repository's **Security** tab
2. Click **Code scanning alerts**
3. View thailint results alongside other security findings
4. Click any alert to see the exact line in your code

### Multiple Linters

Run all thailint linters and merge results:

```yaml
- name: Run all thailint analyses
  run: |
    thailint nesting --format sarif src/ > nesting.sarif || true
    thailint srp --format sarif src/ > srp.sarif || true
    thailint magic-numbers --format sarif src/ > magic.sarif || true
    thailint dry --format sarif src/ > dry.sarif || true

- name: Upload all SARIF files
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: .
    category: thailint
```

---

## VS Code Integration

### Install SARIF Viewer

1. Open VS Code Extensions (Ctrl+Shift+X)
2. Search for "SARIF Viewer"
3. Install **Microsoft SARIF Viewer** extension

### Generate and View Results

```bash
# Generate SARIF file
thailint nesting --format sarif src/ > results.sarif

# Open in VS Code
code results.sarif
```

### Features

The SARIF Viewer provides:
- **Results Explorer**: Browse all violations in a tree view
- **Click-to-Navigate**: Click any result to jump to the source location
- **Filtering**: Filter by rule, severity, or file
- **Grouping**: Group results by rule, file, or severity

---

## Azure DevOps Integration

### Pipeline Configuration

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.11'

  - script: pip install thailint
    displayName: 'Install thailint'

  - script: |
      thailint nesting --format sarif src/ > $(Build.ArtifactStagingDirectory)/nesting.sarif
      thailint srp --format sarif src/ > $(Build.ArtifactStagingDirectory)/srp.sarif
    displayName: 'Run thailint analysis'
    continueOnError: true

  - task: PublishBuildArtifacts@1
    inputs:
      PathtoPublish: '$(Build.ArtifactStagingDirectory)'
      ArtifactName: 'sarif-results'
```

---

## Python API Usage

### Programmatic SARIF Generation

```python
"""Generate SARIF output programmatically."""
import json
from src.api import Linter
from src.formatters.sarif import SarifFormatter

# Initialize linter
linter = Linter(config_file='.thailint.yaml')

# Run analysis
violations = linter.lint('src/', rules=['nesting'])

# Format as SARIF
formatter = SarifFormatter()
sarif_document = formatter.format(violations)

# Output JSON
print(json.dumps(sarif_document, indent=2))
```

### Custom Tool Metadata

```python
"""Customize SARIF tool metadata."""
from src.formatters.sarif import SarifFormatter

formatter = SarifFormatter(
    tool_name="my-linter",
    tool_version="1.0.0",
    information_uri="https://example.com/my-linter"
)

sarif_document = formatter.format(violations)
```

### Combine Multiple Analyses

```python
"""Combine SARIF results from multiple linter runs."""
import json
from src.api import Linter
from src.formatters.sarif import SarifFormatter

linter = Linter()
formatter = SarifFormatter()

# Run multiple analyses
nesting_violations = linter.lint('src/', rules=['nesting'])
srp_violations = linter.lint('src/', rules=['srp'])
magic_violations = linter.lint('src/', rules=['magic-numbers'])

# Combine all violations
all_violations = nesting_violations + srp_violations + magic_violations

# Generate single SARIF document
sarif_document = formatter.format(all_violations)

# Save to file
with open('all-results.sarif', 'w') as f:
    json.dump(sarif_document, f, indent=2)
```

---

## CI/CD Best Practices

### Fail on Violations

Use exit codes to fail pipelines when violations are found:

```bash
# Strict mode: fail on any violation
thailint nesting --format sarif src/ > results.sarif
if [ $? -ne 0 ]; then
    echo "Violations found! See results.sarif"
    exit 1
fi
```

### Threshold-Based Failures

Check violation count before failing:

```bash
thailint nesting --format sarif src/ > results.sarif
COUNT=$(jq '.runs[0].results | length' results.sarif)
if [ "$COUNT" -gt 10 ]; then
    echo "Too many violations: $COUNT (max 10)"
    exit 1
fi
```

### Parallel Analysis

Run multiple linters in parallel for faster CI:

```yaml
jobs:
  lint-nesting:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install thailint
      - run: thailint nesting --format sarif src/ > nesting.sarif || true
      - uses: actions/upload-artifact@v4
        with:
          name: nesting-sarif
          path: nesting.sarif

  lint-srp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install thailint
      - run: thailint srp --format sarif src/ > srp.sarif || true
      - uses: actions/upload-artifact@v4
        with:
          name: srp-sarif
          path: srp.sarif

  upload-sarif:
    needs: [lint-nesting, lint-srp]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: .
```

---

## Output Examples

### Example: Nesting Violations

```bash
thailint nesting --format sarif src/
```

```json
{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "thai-lint",
          "version": "0.5.0",
          "informationUri": "https://github.com/be-wise-be-kind/thai-lint",
          "rules": [
            {
              "id": "nesting.excessive-depth",
              "shortDescription": {
                "text": "Nesting depth violation"
              }
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "nesting.excessive-depth",
          "level": "error",
          "message": {
            "text": "Nesting depth 5 exceeds maximum 4 in function 'process_data'"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "src/processor.py"
                },
                "region": {
                  "startLine": 42,
                  "startColumn": 17
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### Example: No Violations

When no violations are found, SARIF output has an empty results array:

```json
{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "thai-lint",
          "version": "0.5.0",
          "informationUri": "https://github.com/be-wise-be-kind/thai-lint",
          "rules": []
        }
      },
      "results": []
    }
  ]
}
```

---

## Troubleshooting

### Invalid JSON Output

**Problem**: SARIF output is malformed or not valid JSON.

**Solution**: Ensure no other output is mixed with SARIF:

```bash
# Wrong: verbose output mixed with SARIF
thailint --verbose nesting --format sarif src/

# Correct: verbose to stderr, SARIF to stdout
thailint nesting --format sarif src/ 2>/dev/null
```

### GitHub Upload Fails

**Problem**: `upload-sarif` action fails with schema validation errors.

**Solution**: Verify SARIF structure:

```bash
# Validate SARIF against schema
thailint nesting --format sarif src/ > results.sarif
jq . results.sarif  # Check valid JSON

# Verify required fields
jq '.version, .runs[0].tool.driver.name' results.sarif
```

### Missing Results in VS Code

**Problem**: VS Code SARIF Viewer shows no results.

**Solution**: Check file paths are relative:

```bash
# SARIF uses relative paths - run from project root
cd /path/to/project
thailint nesting --format sarif src/ > results.sarif
```

### Column Numbers Off by One

**Problem**: Clicking a result navigates to wrong column.

**Explanation**: thailint uses 0-indexed columns internally but converts to 1-indexed for SARIF compliance. This matches the SARIF specification where both line and column numbers are 1-indexed.

---

## Comparison with Other Formats

### Text vs JSON vs SARIF

| Feature | Text | JSON | SARIF |
|---------|------|------|-------|
| Human readable | ✅ Best | ⚠️ OK | ⚠️ OK |
| Machine parseable | ❌ No | ✅ Yes | ✅ Yes |
| GitHub Code Scanning | ❌ No | ❌ No | ✅ Yes |
| VS Code integration | ❌ No | ❌ No | ✅ Yes |
| Rule metadata | ❌ No | ⚠️ Limited | ✅ Full |
| Industry standard | ❌ No | ⚠️ Partial | ✅ Yes |

### When to Use Each Format

- **Text**: Local development, quick checks, terminal output
- **JSON**: Custom integrations, simple CI/CD scripts
- **SARIF**: GitHub Code Scanning, VS Code, enterprise security tooling

---

## Resources

### SARIF Specification

- [SARIF v2.1.0 Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [SARIF JSON Schema](https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json)

### Platform Documentation

- [GitHub Code Scanning SARIF Support](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning)
- [Azure DevOps SARIF Publishing](https://docs.microsoft.com/en-us/azure/devops/pipelines/artifacts/sarif)
- [VS Code SARIF Viewer Extension](https://marketplace.visualstudio.com/items?itemName=MS-SarifVSCode.sarif-viewer)

### thailint Documentation

- [CLI Reference](cli-reference.md)
- [Configuration Guide](configuration.md)
- [Deployment Modes](deployment-modes.md)
