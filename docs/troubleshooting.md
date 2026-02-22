# Troubleshooting Guide

Common issues and solutions for thailint.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [Ignore Pattern Issues](#ignore-pattern-issues)
- [Magic Numbers Issues](#magic-numbers-issues)
- [Performance Issues](#performance-issues)
- [CLI Issues](#cli-issues)
- [Docker Issues](#docker-issues)
- [CI/CD Issues](#cicd-issues)

## Installation Issues

### pip install fails with "package not found"

**Problem:** `pip install thailint` fails with "could not find a version that satisfies the requirement"

**Solutions:**

1. **PyPI package not yet published** - Install from source:
   ```bash
   git clone https://github.com/be-wise-be-kind/thai-lint.git
   cd thai-lint
   pip install -e ".[dev]"
   ```

2. **Use Poetry** (recommended for development):
   ```bash
   git clone https://github.com/be-wise-be-kind/thai-lint.git
   cd thai-lint
   poetry install
   ```

### Python version mismatch

**Problem:** Installation fails with "requires Python 3.11 or higher"

**Solution:** Check and upgrade Python version:

```bash
# Check current version
python --version

# Install Python 3.11+
# macOS (Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11

# Windows: Download from python.org
```

### tree-sitter build errors

**Problem:** Installation fails during tree-sitter compilation

**Solution:** Install system dependencies:

```bash
# macOS
brew install gcc

# Ubuntu/Debian
sudo apt install build-essential

# Windows
# Install Visual Studio Build Tools from microsoft.com
```

## Configuration Issues

### Config file not found

**Problem:** thailint says "Config file not found" but `.thailint.yaml` exists

**Solutions:**

1. **Check filename** - Must be exactly `.thailint.yaml`, `.thailint.json`, or `pyproject.toml` with `[tool.thailint]`:
   ```bash
   # Wrong
   thailint.yaml
   .thailint.yml

   # Correct
   .thailint.yaml
   .thailint.json
   pyproject.toml  # with [tool.thailint] section
   ```

2. **Check file location** - Must be in current directory or parent:
   ```bash
   # Verify file exists
   ls -la .thailint.yaml

   # Use explicit path
   thailint magic-numbers --config .thailint.yaml src/
   ```

3. **Check file permissions**:
   ```bash
   chmod 644 .thailint.yaml
   ```

### Invalid YAML/TOML syntax

**Problem:** "YAML parse error" or "Invalid TOML" when loading config

**Solution:** Validate syntax:

```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('.thailint.yaml'))"

# Validate TOML (Python 3.11+)
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# Common issues:
# - Inconsistent indentation (use 2 spaces, not tabs)
# - Missing quotes around special characters
# - Incorrect nesting
```

**Example of common YAML mistakes:**

```yaml
# Wrong - inconsistent indentation
magic-numbers:
  allowed_numbers:
    - 1
     - 2  # Extra space

# Correct
magic-numbers:
  allowed_numbers:
    - 1
    - 2
```

### Config values not taking effect

**Problem:** Changed config values but violations still appear

**This is the most common issue!** Usually caused by config file not being loaded from correct location.

**Quick diagnostic test:**

```bash
# Test 1: Check project root detection
cd /path/to/your/project
python -c "
from pathlib import Path
from src.utils.project_root import get_project_root  # If using source install

# Or use this standalone test:
test_path = Path('src/myfile.py')  # Replace with your file
search_start = test_path.parent if test_path.is_file() else test_path
print(f'Starting search from: {search_start}')

# Walk up looking for markers
current = search_start
while current != current.parent:
    for marker in ['.git', '.thailint.yaml', 'pyproject.toml']:
        if (current / marker).exists():
            print(f'Found {marker} at: {current}')
            break
    current = current.parent
"

# Test 2: Verify config is readable
python -c "import yaml; print(yaml.safe_load(open('.thailint.yaml')))"

# Test 3: Test with explicit config path
thailint magic-numbers --config .thailint.yaml src/
```

**Solutions:**

1. **Project root detection issue** (MOST COMMON):

   **Symptom**: Config works when you specify `--config` but not without it.

   **Cause**: thailint can't find your project root automatically.

   **Debug steps:**
   ```bash
   # Check where thailint thinks your project root is
   cd your-project-dir
   python -c "
   from pathlib import Path
   test_file = Path('src/myfile.py')  # Your problematic file

   # Check for project markers
   for marker in ['.git', '.thailint.yaml', 'pyproject.toml']:
       marker_path = Path.cwd() / marker
       print(f'{marker}: exists={marker_path.exists()} at {marker_path}')
   "

   # Test if config is found from different directories
   cd /path/to/project && thailint magic-numbers src/file.py  # From root
   cd /path/to/project/src && thailint magic-numbers file.py  # From subdirectory
   ```

   **Fix**: Ensure you have at least ONE of these in your project root:
   - `.git/` directory (most reliable)
   - `.thailint.yaml` file
   - `pyproject.toml` file

   ```bash
   # Create .git directory if missing
   git init

   # OR ensure .thailint.yaml is in the right place
   mv config/.thailint.yaml ./.thailint.yaml

   # Verify location
   ls -la .thailint.yaml
   pwd
   ```

2. **Running from wrong directory**:

   ```bash
   # Wrong - running from parent of project
   cd /home/user/Projects
   thailint magic-numbers my-project/src/  # Config won't be found!

   # Correct - run from project root
   cd /home/user/Projects/my-project
   thailint magic-numbers src/  # Config will be found

   # OR use explicit config
   thailint magic-numbers --config /path/to/.thailint.yaml src/
   ```

3. **Check config is being loaded**:
   ```bash
   # Run with verbose output
   thailint magic-numbers --format json src/ 2>&1 | head -20
   ```

4. **Check linter is enabled**:
   ```yaml
   magic-numbers:
     enabled: true  # Make sure this is true
     allowed_numbers: [0, 1, 2]
   ```

5. **Config key format issues** (0.4.0 compatibility):

   ```yaml
   # Both formats are supported in 0.4.1+
   magic_numbers:     # Underscore (preferred)
     enabled: true

   magic-numbers:     # Hyphen (also works)
     enabled: true
   ```

6. **Restart CLI** - Some cached configs may persist:
   ```bash
   # Clear Python cache
   find . -type d -name "__pycache__" -exec rm -r {} +
   ```

**Advanced debugging:**

If config still not loading, test the config loading chain:

```bash
# Step 1: Can Python read the YAML?
python -c "
import yaml
from pathlib import Path
config = yaml.safe_load(Path('.thailint.yaml').read_text())
print('Config keys:', list(config.keys()))
print('Magic numbers config:', config.get('magic_numbers') or config.get('magic-numbers'))
"

# Step 2: Where does thailint think project root is?
python -c "
from pathlib import Path
import sys
sys.path.insert(0, '/path/to/thai-lint')  # If using source install

from src.utils.project_root import get_project_root
root = get_project_root(Path('src'))  # Adjust path
print(f'Project root: {root}')
print(f'Config file: {root / \".thailint.yaml\"}')
print(f'Config exists: {(root / \".thailint.yaml\").exists()}')
"

# Step 3: Test with minimal config
cat > /tmp/.thailint.yaml << EOF
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2, 60]
EOF

# Test file with violations
echo "x = 99" > /tmp/test.py

# Run with explicit config
cd /tmp && thailint magic-numbers --config .thailint.yaml test.py

# Should show: "Magic number 99 should be a named constant"
# Should NOT show: violations for 0, 1, 2, or 60
```

### Language-specific config not working

**Problem:** Language-specific settings (python, typescript) are ignored

**Solution:** Ensure correct config structure:

```yaml
# Wrong - language as top-level key
python:
  magic-numbers:
    allowed_numbers: [0, 1]

# Correct - language nested under linter
magic-numbers:
  python:
    allowed_numbers: [0, 1]
  typescript:
    allowed_numbers: [0, 1, 2]
```

## Ignore Pattern Issues

### Patterns not matching expected files

**Problem:** Files still being linted despite ignore patterns

**Version Check:**
- **If using 0.4.0**: Ignore patterns for magic-numbers are not implemented (known bug)
- **Solution**: Upgrade to 0.4.1 or later:
  ```bash
  pip install --upgrade thai-lint
  ```

**Common Pattern Mistakes:**

1. **Wrong pattern format**:
   ```yaml
   # Wrong - missing recursive wildcard
   ignore:
     - "test_*.py"  # Only matches test_*.py in root

   # Correct - matches in any directory
   ignore:
     - "**/test_*.py"
   ```

2. **Pattern doesn't match actual path**:
   ```bash
   # Check what path thailint sees
   thailint magic-numbers --format json src/ | grep file_path

   # If path is "src/backend/app/famous_tracks.py"
   # Pattern must match that full path:
   ignore:
     - "src/backend/app/famous_tracks.py"  # Exact
     - "**/famous_tracks.py"                # Recursive
     - "backend/**"                         # Directory
   ```

3. **Case sensitivity**:
   ```yaml
   # Wrong - case doesn't match
   ignore:
     - "**/Test_*.py"  # Won't match test_foo.py

   # Correct
   ignore:
     - "**/test_*.py"
   ```

### Debugging ignore patterns

**Step-by-step debugging:**

1. **Test pattern matching in Python**:
   ```python
   from pathlib import Path

   file_path = Path("src/backend/app/famous_tracks.py")
   pattern = "**/famous_tracks.py"

   print(f"Pattern: {pattern}")
   print(f"File: {file_path}")
   print(f"Match: {file_path.match(pattern)}")
   ```

2. **Check actual file paths**:
   ```bash
   # See all files being checked
   thailint magic-numbers --format json src/ 2>&1 | grep -E "(file_path|Checking)"
   ```

3. **Test with simple pattern first**:
   ```yaml
   # Start simple
   ignore:
     - "famous_tracks"  # Substring match

   # Then refine
   ignore:
     - "**/famous_tracks.py"
   ```

### Per-linter ignore patterns

**Problem:** Want different ignore patterns for different linters

**Solution:** Use per-linter ignore lists:

```yaml
magic-numbers:
  ignore:
    - "backend/config/constants.py"  # Only for magic-numbers
    - "**/test_*.py"

dry:
  ignore:
    - "tests/**"  # Only for DRY linter
    - "**/models.py"
```

## Magic Numbers Issues

### Decimal numbers flagged despite being in allowed_numbers

**Problem:** `60.0` is flagged even though `60` is in `allowed_numbers`

**Version Check:**
- **If using 0.4.0 with CLI**: Known issue with CLI config loading
- **Status**: Linter logic handles this correctly (60 == 60.0 in Python sets), but CLI may have loading issues

**Workarounds:**

1. **Add both forms to config**:
   ```yaml
   magic-numbers:
     allowed_numbers: [60, 60.0]  # Include both
   ```

2. **Use inline ignore**:
   ```python
   timeout = 60.0  # thailint: ignore[magic-numbers]
   ```

3. **Upgrade** to latest version and test:
   ```bash
   pip install --upgrade thai-lint
   thailint --version
   ```

### Too many false positives

**Problem:** Getting violations for reasonable numbers

**Solutions:**

1. **Use lenient preset**:
   ```bash
   thailint init-config --preset lenient
   ```

2. **Add project-specific numbers**:
   ```yaml
   magic-numbers:
     allowed_numbers:
       - -1
       - 0
       - 1
       - 2
       - 10
       - 60    # Your project uses minutes frequently
       - 100
       - 1000
       - 1024  # Your project uses binary units
       - 3600  # Your project uses hours frequently
   ```

3. **Increase max_small_integer**:
   ```yaml
   magic-numbers:
     max_small_integer: 20  # Allow larger range() values
   ```

4. **Use file-level ignores** for specific files:
   ```yaml
   magic-numbers:
     ignore:
       - "backend/config/constants.py"
       - "backend/app/famous_tracks.py"
   ```

### Numbers in constants still flagged

**Problem:** Numbers in `CONSTANT_NAME = 100` are flagged

**Check:**
1. Constant name must be ALL_UPPERCASE:
   ```python
   # Allowed (uppercase constant)
   MAX_RETRIES = 3
   TIMEOUT_SECONDS = 60

   # Flagged (not uppercase)
   max_retries = 3
   timeoutSeconds = 60
   ```

2. Must be direct assignment:
   ```python
   # Allowed
   MAX_SIZE = 100

   # May be flagged (expression, not simple assignment)
   MAX_SIZE = 100 * 1024
   ```

### Test files still showing violations

**Problem:** Test files being flagged despite test detection

**Solution:** Use explicit ignore patterns:

```yaml
magic-numbers:
  ignore:
    - "**/test_*.py"
    - "**/*_test.py"
    - "**/*.test.ts"
    - "**/*.spec.js"
    - "tests/**"  # Entire test directory
```

## Performance Issues

### Linting takes too long

**Problem:** thailint is slow on large codebase

**Solutions:**

1. **Use ignore patterns** to skip large directories:
   ```yaml
   dry:
     ignore:
       - "node_modules/**"
       - "venv/**"
       - ".venv/**"
       - "dist/**"
       - "build/**"
   ```

2. **Lint specific directories** instead of entire project:
   ```bash
   # Instead of
   thailint magic-numbers .

   # Run on specific dirs
   thailint magic-numbers src/ backend/
   ```

3. **For DRY linter**, use memory storage (default):
   ```yaml
   dry:
     storage_mode: "memory"  # Faster than tempfile
   ```

4. **Run linters in parallel** in CI/CD:
   ```bash
   # Instead of sequential
   thailint magic-numbers src/ && thailint nesting src/

   # Run in parallel
   thailint magic-numbers src/ &
   thailint nesting src/ &
   wait
   ```

### Out of memory errors

**Problem:** Python process runs out of memory

**Solutions:**

1. **For DRY linter**, switch to tempfile storage:
   ```yaml
   dry:
     storage_mode: "tempfile"  # Uses disk instead of RAM
   ```

2. **Lint in chunks**:
   ```bash
   thailint dry src/module1/
   thailint dry src/module2/
   thailint dry src/module3/
   ```

3. **Increase system memory** or use Docker with memory limits:
   ```bash
   docker run --memory 4g -v $(pwd):/data washad/thailint:latest dry /data/src
   ```

## CLI Issues

### "command not found: thailint"

**Problem:** Shell can't find thailint command

**Solutions:**

1. **Check installation**:
   ```bash
   pip list | grep thai-lint
   ```

2. **Ensure pip bin directory is in PATH**:
   ```bash
   # Check where thailint is installed
   which thailint

   # Add to PATH (bash)
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc

   # Add to PATH (zsh)
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Use Python module syntax**:
   ```bash
   python -m src.cli magic-numbers src/
   ```

4. **Use Poetry** if installed with Poetry:
   ```bash
   poetry run thailint magic-numbers src/
   ```

### Exit codes not working correctly

**Problem:** thailint returns wrong exit codes

**Expected behavior:**
- `0` - No violations (success)
- `1` - Violations found
- `2` - Error (config not found, syntax error, etc.)

**Check:**
```bash
thailint magic-numbers src/
echo "Exit code: $?"
```

**If wrong:**
1. Update to latest version
2. Check for shell aliases overriding exit codes
3. Report issue on GitHub

### JSON output malformed

**Problem:** `--format json` output is not valid JSON

**Solutions:**

1. **Redirect stderr** to separate stream:
   ```bash
   thailint magic-numbers --format json src/ 2>/dev/null | jq .
   ```

2. **Check for debug output** mixing with JSON:
   ```bash
   # Filter only JSON lines
   thailint magic-numbers --format json src/ | grep -E '^\{|\[' | jq .
   ```

## Docker Issues

### Docker image not found

**Problem:** `docker pull washad/thailint:latest` fails

**Solution:** Check Docker Hub availability:

```bash
# Verify image exists
docker search washad/thailint

# Try specific version
docker pull washad/thailint:0.4.1

# Or build locally
cd thai-lint
docker build -t thailint:local .
docker run thailint:local --help
```

### Volume mount issues

**Problem:** Docker can't access files

**Solutions:**

1. **Use absolute paths**:
   ```bash
   # Wrong - relative path
   docker run -v ./src:/data thailint:latest magic-numbers /data

   # Correct - absolute path
   docker run -v $(pwd)/src:/data washad/thailint:latest magic-numbers /data
   ```

2. **Check permissions**:
   ```bash
   # Fix permissions
   chmod -R 755 src/

   # Run with user ID
   docker run --user $(id -u):$(id -g) -v $(pwd):/data washad/thailint:latest magic-numbers /data
   ```

3. **Verify mount**:
   ```bash
   # Check files are visible in container
   docker run -v $(pwd):/data washad/thailint:latest ls -la /data
   ```

### Config file not found in Docker

**Problem:** Docker container can't find `.thailint.yaml`

**Solution:** Mount config directory:

```bash
# Mount entire project directory
docker run -v $(pwd):/data washad/thailint:latest magic-numbers --config /data/.thailint.yaml /data/src

# Or mount config separately
docker run \
  -v $(pwd)/.thailint.yaml:/config/.thailint.yaml \
  -v $(pwd)/src:/src \
  washad/thailint:latest magic-numbers --config /config/.thailint.yaml /src
```

### Docker sibling directory structure not working

**Problem:** Docker setup with sibling directories doesn't find config or properly resolve ignore patterns

**Symptoms:**
- Config file exists but violations use default settings
- Ignore patterns don't match files
- Error: "Config file not found" even though it's mounted

**Common scenario:**
```
/workspace/
├── root/           # Contains .thailint.yaml and .git
├── backend/        # Code to lint
└── tools/
```

**Root cause:** thailint auto-detects project root by walking UP from the file being linted. When you lint `/workspace/backend/`, it never finds `/workspace/root/.thailint.yaml` because it's in a sibling directory.

**Solution 1: Use `--project-root` (recommended)**

```bash
# Explicit project root - most reliable
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest \
  --project-root /workspace/root \
  magic-numbers /workspace/backend/
```

**Solution 2: Use config path inference (automatic)**

When you specify `--config`, thailint automatically infers the project root from the config's directory:

```bash
# Config path inference - no --project-root needed
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest \
  --config /workspace/root/.thailint.yaml \
  magic-numbers /workspace/backend/
```

**Solution 3: Restructure to nested directories**

If possible, restructure so config is a parent of code:

```
/workspace/root/
├── .thailint.yaml
├── .git/
├── backend/        # Nested under root
└── tools/
```

Then auto-detection works:
```bash
docker run --rm -v $(pwd):/workspace/root \
  washad/thailint:latest \
  magic-numbers /workspace/root/backend/
```

**Priority order:**
1. `--project-root` (highest - explicit specification)
2. Inferred from `--config` path directory (automatic)
3. Auto-detection from file location (may fail with siblings)

**Debugging sibling directory issues:**

```bash
# Test 1: Check if config is accessible
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest \
  ls -la /workspace/root/.thailint.yaml

# Test 2: Try with explicit paths
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest \
  --project-root /workspace/root \
  --config /workspace/root/.thailint.yaml \
  magic-numbers /workspace/backend/

# Test 3: Check ignore pattern resolution
# Add debug output to config temporarily:
cat > .thailint.yaml << EOF
magic_numbers:
  enabled: true
  allowed_numbers: [0, 1, 2]
  ignore:
    - "**/test_*.py"
    - "../backend/famous_tracks.py"  # Relative to config location
EOF

# Run with verbose output
docker run --rm -v $(pwd):/workspace \
  washad/thailint:latest \
  --verbose \
  --project-root /workspace/root \
  magic-numbers /workspace/backend/ 2>&1 | head -50
```

**See also:**
- README.md section "Docker with Sibling Directories"
- CLI Reference: `--project-root` option
- Configuration Guide: ignore pattern resolution

## CI/CD Issues

### Pre-commit hook fails

**Problem:** pre-commit runs but doesn't catch violations

**Solutions:**

1. **Verify hook is installed**:
   ```bash
   pre-commit run --all-files
   ```

2. **Check `.pre-commit-config.yaml`**:
   ```yaml
   repos:
     - repo: local
       hooks:
         - id: thailint-magic-numbers
           name: Check for magic numbers
           entry: thailint magic-numbers
           language: system
           types: [python]
           pass_filenames: false
           args: ["src/"]
   ```

3. **Test manually**:
   ```bash
   thailint magic-numbers src/
   echo $?  # Should be 1 if violations exist
   ```

### GitHub Actions failing

**Problem:** CI fails with "command not found: thailint"

**Solution:** Ensure proper installation in workflow:

```yaml
name: Lint
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install thailint  # Or install from source

      - name: Verify installation
        run: |
          which thailint
          thailint --version

      - name: Run linters
        run: |
          thailint magic-numbers src/
          thailint nesting src/
```

### CI cache issues

**Problem:** CI uses cached old version

**Solution:** Force cache clear:

```yaml
# GitHub Actions
- name: Install dependencies
  run: |
    pip cache purge
    pip install --no-cache-dir thai-lint

# GitLab CI
before_script:
  - pip cache purge
  - pip install --no-cache-dir thai-lint
```

## Getting More Help

If your issue isn't covered here:

1. **Check existing issues**: https://github.com/be-wise-be-kind/thai-lint/issues
2. **Search documentation**: Browse the [docs/](.) folder
3. **Report a bug**: Create a new issue with:
   - thailint version (`thailint --version`)
   - Python version (`python --version`)
   - Config file (if applicable)
   - Command you ran
   - Expected vs actual behavior
   - Error messages

## Known Issues by Version

### 0.4.0

- **Magic-numbers ignore patterns not working** - Fixed in 0.4.1
- **Workaround**: Use inline ignore comments or upgrade

### 0.3.x

- **TypeScript support limited** - Improved in 0.4.0+
- **Workaround**: Upgrade to 0.4.0+

### Earlier versions

- Check release notes: https://github.com/be-wise-be-kind/thai-lint/releases

## Reporting Issues

When reporting issues, include:

```bash
# Version info
thailint --version
python --version

# Config file
cat .thailint.yaml

# Command and output
thailint magic-numbers src/ 2>&1

# File structure
tree -L 3 src/
```

This helps maintainers diagnose problems quickly.
