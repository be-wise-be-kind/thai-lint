# How to: Add a Custom Hook

**Purpose**: Guide to creating and configuring custom pre-commit hooks for project-specific validation

**Scope**: Custom validation rules, business logic checks, organization standards enforcement

**Overview**: This guide explains how to create custom pre-commit hooks tailored to your project's needs.
    Covers understanding hook structure, writing custom validation scripts, integrating with Docker containers,
    configuring file filters, error handling patterns, and testing custom hooks. Includes examples for common
    use cases like checking for TODO comments, validating file naming conventions, enforcing documentation
    standards, and project-specific security checks. Applicable to any project using pre-commit framework.

**Dependencies**: Pre-commit framework installed, .pre-commit-config.yaml configured, Docker containers (optional)

**Exports**: Custom hook configuration, validation scripts, tested custom hooks

**Related**: how-to-install-pre-commit.md, how-to-debug-failing-hooks.md, PRE_COMMIT_STANDARDS.md

**Implementation**: Step-by-step hook creation with examples and testing procedures

---

## When to Add Custom Hooks

Add custom hooks for:

✅ **Project-specific validation**:
- File naming conventions
- Directory structure rules
- Project-specific code patterns

✅ **Business logic constraints**:
- Required documentation
- License headers
- API versioning rules

✅ **Organization standards**:
- Security policies
- Compliance requirements
- Team conventions

❌ **Don't add custom hooks for**:
- Standard linting (use ruff, eslint)
- Code formatting (use prettier, black)
- Type checking (use mypy, tsc)
- One-off checks (use CI/CD instead)

---

## Hook Structure

### Basic Hook Configuration

```yaml
- id: custom-hook-name
  name: Human-Readable Name
  entry: bash -c 'your-command-here'
  language: system
  files: <file-pattern>
  pass_filenames: false
  stages: [pre-commit]
```

### Hook Fields Explained

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `id` | Yes | Unique identifier | `custom-check-todos` |
| `name` | Yes | Display name | `Check for TODO comments` |
| `entry` | Yes | Command to execute | `bash -c 'script.sh'` |
| `language` | Yes | Language/runtime | `system`, `python`, `node` |
| `files` | No | File filter regex | `\.(py|js)$` |
| `pass_filenames` | No | Pass files to command | `false` (usually) |
| `stages` | No | When to run | `[pre-commit]`, `[pre-push]` |
| `always_run` | No | Ignore file filters | `true` or `false` |

---

## Example 1: Check for TODO Comments

### Goal
Warn when committing files with unresolved TODO comments.

### Implementation

Add to `.pre-commit-config.yaml`:

```yaml
- id: custom-check-todos
  name: Check for unresolved TODOs
  entry: bash -c 'if git diff --cached | grep -i "# TODO:.*FIXME"; then echo "⚠️  Warning: Unresolved critical TODOs found"; exit 1; fi'
  language: system
  pass_filenames: false
  stages: [pre-commit]
```

### Explanation
- Uses `git diff --cached` to check only staged changes
- Searches for `TODO:` followed by `FIXME` (critical TODOs)
- Prints warning message
- Exits with code 1 to fail the commit

### Testing

```bash
# Create file with critical TODO
echo "# TODO: FIXME - Critical issue" > test.py
git add test.py

# Try to commit (should fail)
git commit -m "Test TODO check"

# Expected output:
# ⚠️  Warning: Unresolved critical TODOs found
```

---

## Example 2: Enforce File Naming Convention

### Goal
Ensure Python files use snake_case naming.

### Implementation

Create validation script `tools/check_filenames.sh`:

```bash
#!/bin/bash
# Check Python files for snake_case naming

files=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.py$")

for file in $files; do
  filename=$(basename "$file" .py)

  # Check if filename is snake_case (lowercase with underscores)
  if ! echo "$filename" | grep -qE "^[a-z_][a-z0-9_]*$"; then
    echo "❌ File '$file' does not follow snake_case naming convention"
    exit 1
  fi
done

echo "✅ All Python files follow snake_case naming"
```

Make executable:
```bash
chmod +x tools/check_filenames.sh
```

Add to `.pre-commit-config.yaml`:

```yaml
- id: custom-check-filenames
  name: Check Python file naming (snake_case)
  entry: bash -c 'bash tools/check_filenames.sh'
  language: system
  files: \.(py)$
  pass_filenames: false
  stages: [pre-commit]
```

### Testing

```bash
# Create file with invalid name
echo "print('test')" > BadFileName.py
git add BadFileName.py

# Try to commit (should fail)
git commit -m "Test filename check"

# Expected output:
# ❌ File 'BadFileName.py' does not follow snake_case naming convention

# Fix the filename
mv BadFileName.py bad_file_name.py
git add bad_file_name.py
git commit -m "Test filename check"

# Should succeed
```

---

## Example 3: Require Documentation Headers

### Goal
Ensure all Python modules have proper documentation headers.

### Implementation

Create validation script `tools/check_headers.py`:

```python
#!/usr/bin/env python3
"""Check for required documentation headers in Python files."""

import sys
import re

def check_file(filepath):
    """Check if file has required Purpose header."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Check for docstring with Purpose field
    if not re.search(r'"""[\s\S]*Purpose:[\s\S]*"""', content):
        return False
    return True

def main():
    """Check all Python files for headers."""
    import subprocess

    # Get changed Python files
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True
    )

    files = [f for f in result.stdout.split('\n') if f.endswith('.py')]

    if not files:
        return 0

    failed = []
    for filepath in files:
        if not check_file(filepath):
            failed.append(filepath)

    if failed:
        print("❌ Files missing required documentation headers:")
        for f in failed:
            print(f"  - {f}")
        print("\nRequired: Docstring with 'Purpose:' field")
        return 1

    print("✅ All Python files have required headers")
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

Make executable:
```bash
chmod +x tools/check_headers.py
```

Add to `.pre-commit-config.yaml`:

```yaml
- id: custom-check-headers
  name: Check for documentation headers
  entry: bash -c 'python tools/check_headers.py'
  language: system
  files: \.(py)$
  pass_filenames: false
  stages: [pre-commit]
```

### Testing

```bash
# Create file without header
echo "def hello(): pass" > test_module.py
git add test_module.py

# Try to commit (should fail)
git commit -m "Test header check"

# Expected output:
# ❌ Files missing required documentation headers:
#   - test_module.py

# Fix by adding header
cat > test_module.py << 'EOF'
"""
Purpose: Test module for demonstration

This module demonstrates header checking.
"""

def hello():
    pass
EOF

git add test_module.py
git commit -m "Test header check"

# Should succeed
```

---

## Example 4: Docker-Integrated Custom Hook

### Goal
Run custom validation in Docker container for consistency.

### Implementation

Create validation script `tools/custom_validator.py`:

```python
#!/usr/bin/env python3
"""Custom project-specific validation."""

import sys
import subprocess

def validate_files():
    """Run custom validation on changed files."""
    # Get changed files
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True
    )

    files = [f for f in result.stdout.split('\n') if f.endswith('.py')]

    if not files:
        print("✅ No Python files to validate")
        return 0

    # Your custom validation logic here
    print(f"✅ Validated {len(files)} Python files")
    return 0

if __name__ == '__main__':
    sys.exit(validate_files())
```

Add to `.pre-commit-config.yaml`:

```yaml
- id: custom-docker-validator
  name: Custom validation in Docker
  entry: bash -c 'files=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.py$" || true); if [ -n "$files" ]; then docker exec <container-name> python /workspace/tools/custom_validator.py; fi'
  language: system
  files: \.(py)$
  pass_filenames: false
  stages: [pre-commit]
```

### Benefits of Docker Integration
- Consistent validation environment
- Same tools in dev and CI/CD
- No local dependency conflicts
- Isolated execution

---

## Example 5: Check for Hardcoded Secrets

### Goal
Prevent committing hardcoded secrets (API keys, passwords).

### Implementation

Create validation script `tools/check_secrets.sh`:

```bash
#!/bin/bash
# Check for potential hardcoded secrets

files=$(git diff --cached --name-only --diff-filter=ACM)

# Patterns to check for
patterns=(
  "password\s*=\s*['\"][^'\"]+['\"]"
  "api_key\s*=\s*['\"][^'\"]+['\"]"
  "secret\s*=\s*['\"][^'\"]+['\"]"
  "token\s*=\s*['\"][^'\"]+['\"]"
  "aws_access_key_id"
  "aws_secret_access_key"
)

found_secrets=false

for file in $files; do
  for pattern in "${patterns[@]}"; do
    if git diff --cached "$file" | grep -iE "$pattern" >/dev/null; then
      echo "❌ Potential hardcoded secret in $file"
      echo "   Pattern: $pattern"
      found_secrets=true
    fi
  done
done

if [ "$found_secrets" = true ]; then
  echo ""
  echo "⚠️  Secrets detected! Use environment variables instead."
  echo "   See .ai/docs/SECURITY_STANDARDS.md for guidance"
  exit 1
fi

echo "✅ No hardcoded secrets detected"
```

Make executable:
```bash
chmod +x tools/check_secrets.sh
```

Add to `.pre-commit-config.yaml`:

```yaml
- id: custom-check-secrets
  name: Check for hardcoded secrets
  entry: bash -c 'bash tools/check_secrets.sh'
  language: system
  pass_filenames: false
  stages: [pre-commit]
  always_run: true
```

### Testing

```bash
# Create file with hardcoded secret
echo "api_key = 'sk-1234567890abcdef'" > config.py
git add config.py

# Try to commit (should fail)
git commit -m "Test secrets check"

# Expected output:
# ❌ Potential hardcoded secret in config.py
#    Pattern: api_key\s*=\s*['\"][^'\"]+['\"]
```

---

## Hook Design Patterns

### Pattern 1: File-Specific Hook

Only run on specific file types:

```yaml
- id: custom-python-check
  name: Custom Python check
  entry: bash -c 'your-command'
  language: system
  files: \.(py)$  # Only .py files
  pass_filenames: false
  stages: [pre-commit]
```

### Pattern 2: Directory-Specific Hook

Only run on files in specific directories:

```yaml
- id: custom-app-check
  name: Custom app directory check
  entry: bash -c 'your-command'
  language: system
  files: ^app/  # Only files in app/ directory
  pass_filenames: false
  stages: [pre-commit]
```

### Pattern 3: Always-Run Hook

Run even if no matching files changed:

```yaml
- id: custom-always-check
  name: Always run this check
  entry: bash -c 'your-command'
  language: system
  pass_filenames: false
  stages: [pre-commit]
  always_run: true  # Ignore file filters
```

### Pattern 4: Pre-push Comprehensive Check

Run expensive checks only before push:

```yaml
- id: custom-comprehensive-check
  name: Comprehensive validation
  entry: bash -c 'your-expensive-command'
  language: system
  pass_filenames: false
  stages: [pre-push]  # Only on git push
  always_run: true
```

---

## Best Practices

### 1. Clear Error Messages

❌ Bad:
```bash
exit 1
```

✅ Good:
```bash
echo "❌ Custom check failed: File naming convention violated"
echo "   Expected: snake_case (e.g., my_file.py)"
echo "   Found: CamelCase (e.g., MyFile.py)"
exit 1
```

### 2. Exit Codes

- `exit 0`: Success (hook passes)
- `exit 1`: Failure (hook fails, blocks commit)
- Other codes: Also treated as failure

### 3. File Detection

Always check for changed files:

```bash
files=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.py$" || true)

if [ -z "$files" ]; then
  # No matching files, skip check
  exit 0
fi

# Run check on files
```

### 4. Performance

- Keep hooks fast (< 3 seconds)
- Only check changed files
- Use file filters (`files:` pattern)
- Cache results when possible

### 5. Idempotency

Hooks should be idempotent:
- Running twice should have same result
- Don't modify files (use auto-fix hook for that)
- Don't depend on external state

### 6. Documentation

Add comments to configuration:

```yaml
# Custom Hook: Check for TODO comments
# Purpose: Prevents committing critical TODOs
# Fails: If "TODO: FIXME" pattern found
# Docs: See .ai/howto/how-to-add-custom-hook.md
- id: custom-check-todos
  name: Check for critical TODOs
  entry: bash -c '...'
  language: system
  pass_filenames: false
  stages: [pre-commit]
```

---

## Testing Custom Hooks

### Manual Testing

```bash
# 1. Add hook to .pre-commit-config.yaml

# 2. Run specific hook
pre-commit run custom-hook-name --all-files

# 3. Check output
# Expected: Hook runs and shows results

# 4. Test on specific files
pre-commit run custom-hook-name --files test.py

# 5. Test commit workflow
git add .
git commit -m "Test custom hook"
```

### Automated Testing

Create test script `test_hooks.sh`:

```bash
#!/bin/bash
# Test custom pre-commit hooks

# Test 1: Hook should pass on valid file
echo "# Valid file" > test_valid.py
git add test_valid.py
if pre-commit run custom-hook-name --files test_valid.py; then
  echo "✅ Test 1 passed"
else
  echo "❌ Test 1 failed"
fi

# Test 2: Hook should fail on invalid file
echo "# TODO: FIXME" > test_invalid.py
git add test_invalid.py
if ! pre-commit run custom-hook-name --files test_invalid.py; then
  echo "✅ Test 2 passed (correctly failed)"
else
  echo "❌ Test 2 failed (should have failed)"
fi

# Clean up
rm -f test_valid.py test_invalid.py
```

---

## Debugging Custom Hooks

### Enable Verbose Output

```bash
# Run with verbose flag
pre-commit run custom-hook-name --verbose --all-files

# Shows:
# - Hook command executed
# - Full output
# - Exit code
```

### Test Hook Command Manually

```bash
# Copy the entry command from .pre-commit-config.yaml
bash -c 'your-hook-command'

# Run directly to debug
```

### Check Hook Output

```bash
# Run hook and capture output
pre-commit run custom-hook-name --all-files 2>&1 | tee hook-output.log

# Review output
cat hook-output.log
```

---

## Common Mistakes

### Mistake 1: Not Checking for Files

❌ Bad:
```yaml
entry: bash -c 'python check.py'  # Runs even if no files
```

✅ Good:
```yaml
entry: bash -c 'files=$(git diff --cached --name-only | grep .py || true); if [ -n "$files" ]; then python check.py; fi'
```

### Mistake 2: Modifying Files

❌ Bad (don't modify in validation hook):
```bash
# This should be in auto-fix hook, not validation hook
ruff format --fix .
```

✅ Good (only validate):
```bash
ruff format --check .
```

### Mistake 3: Poor Error Messages

❌ Bad:
```bash
echo "Failed"
exit 1
```

✅ Good:
```bash
echo "❌ Custom validation failed"
echo "   Issue: File naming convention violated"
echo "   Fix: Rename files to snake_case"
echo "   See: .ai/docs/standards/naming-conventions.md"
exit 1
```

---

## Integration with CI/CD

Run same custom hooks in GitHub Actions:

```yaml
# .github/workflows/lint.yml
- name: Run pre-commit hooks
  run: |
    pip install pre-commit
    pre-commit run --all-files
```

Benefits:
- Consistent validation locally and in CI
- Catch issues before code review
- Enforce quality gates

---

## Summary

### Custom Hook Checklist

- [ ] Identified specific validation need
- [ ] Created validation script (if needed)
- [ ] Made script executable (`chmod +x`)
- [ ] Added hook to `.pre-commit-config.yaml`
- [ ] Used clear, descriptive hook name
- [ ] Added file filter if applicable
- [ ] Included clear error messages
- [ ] Tested hook manually (`pre-commit run <id>`)
- [ ] Tested in commit workflow
- [ ] Documented hook purpose (comments)
- [ ] Added to project documentation

### Key Takeaways

1. **Keep hooks simple**: One check per hook
2. **Fast execution**: < 3 seconds
3. **Clear errors**: Explain what failed and how to fix
4. **File filtering**: Only check relevant files
5. **Test thoroughly**: Test pass and fail cases
6. **Document**: Explain hook purpose and behavior

---

## Next Steps

- **Review standards**: Read `.ai/docs/PRE_COMMIT_STANDARDS.md`
- **Debug hooks**: See `.ai/howto/how-to-debug-failing-hooks.md`
- **Share hooks**: Commit custom hooks to version control
- **Team alignment**: Document custom hooks for team
