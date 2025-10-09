# How to Write Tests

**Purpose**: Comprehensive guide for writing, organizing, and running tests
**Scope**: Testing practices, pytest usage, fixtures, and quality standards

## Overview

This project uses pytest for testing with strict quality requirements. All tests must be isolated, reproducible, and follow consistent patterns. Tests are organized into unit and integration tests with shared fixtures for common setup patterns.

## Test Organization

### Directory Structure

```
tests/
├── conftest.py              # Shared pytest fixtures
├── unit/                    # Unit tests (fast, isolated)
│   ├── core/               # Core functionality tests
│   ├── linters/            # Linter-specific tests
│   │   ├── file_placement/
│   │   ├── nesting/
│   │   └── srp/
│   ├── orchestrator/       # Orchestrator tests
│   └── utils/              # Utility function tests
└── integration/            # Integration tests (slower, broader scope)
    ├── test_e2e_cli.py     # CLI workflow tests
    ├── test_e2e_library.py # Library API tests
    └── test_artifacts_generation.py
```

### Test Types

**Unit Tests** (`tests/unit/`)
- Test single functions/classes in isolation
- Fast execution (< 1s per test)
- Mock external dependencies
- Focus on edge cases and error handling

**Integration Tests** (`tests/integration/`)
- Test complete workflows end-to-end
- Test interactions between components
- Use real filesystem and subprocess calls where appropriate
- Validate CLI commands, library APIs, Docker integration

## Running Tests

### Basic Commands

```bash
# Run all tests
just test

# Run tests with coverage
just test-coverage

# Run specific test file
pytest tests/unit/utils/test_project_root.py

# Run specific test class
pytest tests/unit/utils/test_project_root.py::TestGetProjectRoot

# Run specific test method
pytest tests/unit/utils/test_project_root.py::TestGetProjectRoot::test_finds_root_with_git_marker

# Run with verbose output
pytest -v

# Run with print statements visible
pytest -s

# Stop on first failure
pytest -x

# Run tests matching pattern
pytest -k "project_root"
```

### Coverage Requirements

- Minimum 80% code coverage
- New code should have 100% coverage
- Check coverage report: `just test-coverage`

## Writing Tests

### Test File Naming

- Test files: `test_*.py` or `*_test.py`
- Mirror source structure: `src/utils/project_root.py` → `tests/unit/utils/test_project_root.py`

### Test Class Organization

```python
"""Unit tests for project root detection utilities.

Purpose: Test is_project_root() and get_project_root() functions
Scope: Comprehensive testing of project root detection logic
"""

from pathlib import Path
import pytest
from src.utils.project_root import get_project_root, is_project_root


class TestIsProjectRoot:
    """Test is_project_root() function."""

    def test_returns_true_for_directory_with_git(self, tmp_path):
        """Should return True when .git directory exists."""
        (tmp_path / ".git").mkdir()
        assert is_project_root(tmp_path) is True

    def test_returns_false_for_directory_without_markers(self, tmp_path):
        """Should return False when no project markers exist."""
        assert is_project_root(tmp_path) is False


class TestGetProjectRoot:
    """Test get_project_root() function."""

    def test_finds_root_with_git_marker(self, tmp_path):
        """Should find project root when .git directory exists."""
        (tmp_path / ".git").mkdir()
        subdir = tmp_path / "src" / "nested"
        subdir.mkdir(parents=True)

        result = get_project_root(subdir)
        assert result == tmp_path
```

### Test Naming Conventions

- Test methods: `test_<what_it_tests>`
- Be descriptive: `test_returns_error_when_file_missing` (good) vs `test_error` (bad)
- Use docstrings: Start with "Should..." to describe expected behavior

### Assertions

```python
# Basic assertions
assert result == expected
assert result is True
assert result is not None

# Collection assertions
assert len(violations) == 3
assert item in collection
assert set(result) == {"a", "b", "c"}

# Exception assertions
with pytest.raises(ValueError, match="Invalid config"):
    function_that_raises()

# Approximate comparisons
assert result == pytest.approx(3.14159, rel=0.001)
```

### Parametrized Tests

Test multiple scenarios with same logic:

```python
@pytest.mark.parametrize("input,expected", [
    ("test.py", True),
    ("test.js", False),
    ("test.PY", True),  # Case insensitive
])
def test_is_python_file(input, expected):
    """Should detect Python files by extension."""
    assert is_python_file(input) == expected


@pytest.mark.parametrize("marker", [".git", "pyproject.toml"])
def test_detects_project_markers(tmp_path, marker):
    """Should detect various project root markers."""
    if marker.startswith("."):
        (tmp_path / marker).mkdir()
    else:
        (tmp_path / marker).touch()

    assert is_project_root(tmp_path) is True
```

## Using Pytest Fixtures

Fixtures provide reusable test setup and teardown. This project provides shared fixtures in `tests/conftest.py`.

### Available Fixtures

#### 1. `tmp_path` (Built-in Pytest Fixture)

Provides a clean temporary directory for each test.

```python
def test_creates_file(tmp_path):
    """Test file creation in temporary directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    assert test_file.exists()
    assert test_file.read_text() == "content"
    # Cleanup is automatic after test
```

#### 2. `mock_project_root` (Custom Fixture)

Creates a temporary directory with `.git` marker (looks like a real project).

**What it provides:**
- Clean temporary directory (isolated per test)
- `.git` directory marker (makes it detectable as project root)
- Automatic cleanup after test

**When to use:**
- Testing project root detection
- Testing file operations in a project context
- Testing CLI commands that need a project structure
- Any test that needs a basic project directory

**Example:**
```python
def test_find_project_root(mock_project_root):
    """Test that we can find the project root."""
    from src.utils.project_root import get_project_root

    # Create nested subdirectory
    subdir = mock_project_root / "src" / "deeply" / "nested"
    subdir.mkdir(parents=True)

    # Should find the root from any subdirectory
    found_root = get_project_root(start_path=subdir)
    assert found_root == mock_project_root
```

#### 3. `mock_project_with_config` (Custom Fixture)

Creates a complete test project with configuration file.

**What it provides:**
- Everything from `mock_project_root`
- `.artifacts/generated-config.yaml` with deny-all-python config
- Returns tuple: `(project_root: Path, config_content: str)`

**When to use:**
- Testing linting behavior
- Testing configuration loading
- Testing file placement rules
- Any test that needs a configured project

**Example:**
```python
def test_linting_finds_violations(mock_project_with_config):
    """Test that linting detects Python files when denied."""
    project_root, config_content = mock_project_with_config

    # Create a Python file (should violate deny-all rule)
    test_file = project_root / "test.py"
    test_file.write_text("print('hello')")

    # Run linter
    from src.linters.file_placement.linter import FilePlacementLinter
    linter = FilePlacementLinter(project_root)
    violations = linter.lint([test_file])

    # Should find violation
    assert len(violations) > 0
    assert "No Python files" in violations[0].message
```

### Migration: Replacing Manual Setup

**Before (Manual Setup):**
```python
def test_something(tmp_path):
    """Old way - creates directories manually."""
    # Manually create .git
    (tmp_path / ".git").mkdir()

    # Manually create .artifacts
    artifacts_dir = tmp_path / ".artifacts"
    artifacts_dir.mkdir()

    # Manually write config
    config = artifacts_dir / "generated-config.yaml"
    config.write_text("file-placement:\n  global_deny:\n    - pattern: '.*\\.py$'")

    # Now run test...
```

**After (Using Fixtures):**
```python
def test_something(mock_project_with_config):
    """New way - uses shared fixture."""
    project_root, config_content = mock_project_with_config

    # .git and .artifacts/generated-config.yaml already exist!
    # Just create test files and run tests
```

### Custom Fixture for Custom Config

When you need non-default configuration:

```python
def test_with_custom_config(mock_project_root):
    """Test with custom configuration."""
    # Use mock_project_root when you need custom config
    artifacts_dir = mock_project_root / ".artifacts"
    artifacts_dir.mkdir()

    # Write your custom config
    config = artifacts_dir / "generated-config.yaml"
    config.write_text("""
file-placement:
  allowed:
    - pattern: '.*\\.ts$'
      locations: ['src/']
""")

    # Run test with custom config
    # ...
```

## Common Testing Patterns

### Testing CLI Commands

Use Click's `CliRunner` for CLI testing:

```python
from click.testing import CliRunner
from src.cli import cli


def test_cli_help_shows_usage():
    """Test that --help flag shows usage information."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "Options:" in result.output


def test_cli_lint_command(mock_project_with_config):
    """Test lint command execution."""
    project_root, _ = mock_project_with_config

    # Create test file
    test_file = project_root / "test.py"
    test_file.write_text("print('test')")

    # Run CLI in isolated context
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=project_root):
        result = runner.invoke(cli, ["lint", str(test_file)])

        assert result.exit_code == 1  # Violations found
        assert "test.py" in result.output
```

### Testing File Operations

```python
def test_file_creation(mock_project_root):
    """Test creating files in project."""
    # Create nested structure
    src_dir = mock_project_root / "src" / "utils"
    src_dir.mkdir(parents=True)

    # Create file
    test_file = src_dir / "helpers.py"
    test_file.write_text("def helper(): pass")

    # Verify
    assert test_file.exists()
    assert test_file.read_text() == "def helper(): pass"
```

### Testing Configuration Loading

```python
def test_loads_yaml_config(mock_project_root):
    """Test loading YAML configuration."""
    config_dir = mock_project_root / ".artifacts"
    config_dir.mkdir()

    config_file = config_dir / "generated-config.yaml"
    config_file.write_text("""
nesting:
  max_depth: 3
  exclude_patterns:
    - "test_*.py"
""")

    from src.linter_config.config_loader import load_config
    config = load_config(mock_project_root)

    assert config["nesting"]["max_depth"] == 3
    assert "test_*.py" in config["nesting"]["exclude_patterns"]
```

### Testing Error Handling

```python
def test_raises_error_on_missing_config(mock_project_root):
    """Test error handling when config is missing."""
    from src.linter_config.config_loader import load_config

    with pytest.raises(FileNotFoundError, match="Config file not found"):
        load_config(mock_project_root)


def test_handles_invalid_yaml(mock_project_root):
    """Test handling of invalid YAML syntax."""
    config_dir = mock_project_root / ".artifacts"
    config_dir.mkdir()

    config_file = config_dir / "generated-config.yaml"
    config_file.write_text("invalid: yaml: syntax:")

    from src.linter_config.config_loader import load_config

    with pytest.raises(ValueError, match="Invalid YAML"):
        load_config(mock_project_root)
```

### Testing with Multiple Files

```python
def test_multiple_files(mock_project_with_config):
    """Test linting across multiple files."""
    project_root, _ = mock_project_with_config

    # Create multiple test files
    files = []
    for i in range(3):
        f = project_root / f"test{i}.py"
        f.write_text(f"print({i})")
        files.append(f)

    # Lint all files
    from src.linters.file_placement.linter import FilePlacementLinter
    linter = FilePlacementLinter(project_root)
    violations = linter.lint(files)

    # Should find violation for each file
    assert len(violations) == 3
```

## Best Practices

### Test Isolation

- Each test should be independent
- Don't rely on test execution order
- Use fixtures for setup, avoid class-level setUp/tearDown
- Clean up resources (fixtures handle this automatically)

### Descriptive Names

```python
# Good
def test_returns_empty_list_when_no_files_match_pattern():
    """Should return empty list when no files match the pattern."""
    # ...

# Bad
def test_empty():
    """Test empty case."""
    # ...
```

### Arrange-Act-Assert Pattern

```python
def test_calculates_total_price(mock_project_root):
    """Should calculate total price including tax."""
    # Arrange - Set up test data
    items = [
        {"price": 10.00, "quantity": 2},
        {"price": 5.00, "quantity": 3},
    ]
    tax_rate = 0.08

    # Act - Execute the code under test
    result = calculate_total(items, tax_rate)

    # Assert - Verify the result
    expected = (10.00 * 2 + 5.00 * 3) * 1.08
    assert result == pytest.approx(expected, rel=0.01)
```

### Helpful Error Messages

```python
# Good - Shows what was expected vs actual
assert len(violations) == 3, (
    f"Expected 3 violations but got {len(violations)}: {violations}"
)

# Bad - Just fails without context
assert len(violations) == 3
```

### Test One Thing

```python
# Good - Tests one specific behavior
def test_ignores_comments_in_python_files():
    """Should not count comment lines in Python files."""
    # ...

def test_counts_blank_lines_in_python_files():
    """Should count blank lines in Python files."""
    # ...

# Bad - Tests multiple things
def test_python_file_parsing():
    """Test Python file parsing."""
    # Tests comments AND blank lines AND imports AND...
```

## Quality Gates

### All Tests Must Pass

```bash
# Tests must exit with code 0
just test
if [ $? -ne 0 ]; then
    echo "FAILED - fix all tests before committing"
    exit 1
fi
```

### Tests Must Be Linted

Test code follows the same quality standards as production code:
- Pylint score: 10.00/10
- Complexity: A-grade (Xenon)
- Type hints: Required (MyPy)

```bash
# Lint tests
just lint-full
```

### Coverage Requirements

- Minimum 80% coverage overall
- New code should have 100% coverage
- Use `# pragma: no cover` sparingly with justification

```bash
# Check coverage
just test-coverage

# View HTML coverage report
open htmlcov/index.html
```

## When NOT to Use Fixtures

Use `tmp_path` directly when you need:
- No `.git` directory (testing non-git projects)
- No config file (testing config generation)
- Completely custom setup that doesn't fit fixtures

```python
def test_non_git_project(tmp_path):
    """Test behavior in non-git project."""
    # Deliberately no .git directory
    result = get_project_root(tmp_path)
    assert result == tmp_path  # Should return start path
```

## Debugging Tests

### Print Debugging

```bash
# Run with print statements visible
pytest -s tests/unit/utils/test_project_root.py
```

### Verbose Output

```bash
# Show individual test results
pytest -v

# Show even more detail
pytest -vv
```

### Stop on First Failure

```bash
# Stop immediately when a test fails
pytest -x
```

### Run Specific Test

```bash
# Run one test to debug
pytest tests/unit/utils/test_project_root.py::TestGetProjectRoot::test_finds_root_with_git_marker -v
```

### Use Python Debugger

```python
def test_something(mock_project_root):
    """Test something complex."""
    # Add breakpoint
    import pdb; pdb.set_trace()

    # Code execution will pause here
    result = some_function()
    assert result == expected
```

## Common Pitfalls

### Shared Mutable State

```python
# Bad - Shared list between tests
class TestBad:
    results = []  # DON'T DO THIS

    def test_one(self):
        self.results.append(1)
        assert len(self.results) == 1  # Fails if test_two runs first

# Good - Isolated state
class TestGood:
    def test_one(self):
        results = []  # Fresh list for each test
        results.append(1)
        assert len(results) == 1
```

### Path Assumptions

```python
# Bad - Assumes specific path
def test_bad():
    config = Path("/tmp/config.yaml")  # Fails on Windows, conflicts with other tests

# Good - Use fixtures
def test_good(mock_project_root):
    config = mock_project_root / ".artifacts" / "config.yaml"
```

### External Dependencies

```python
# Bad - Depends on network
def test_bad():
    result = requests.get("https://api.example.com")  # Flaky, slow

# Good - Mock external calls
def test_good(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse({"data": "test"})

    monkeypatch.setattr(requests, "get", mock_get)
    result = requests.get("https://api.example.com")
```

## See Also

- `tests/conftest.py` - Fixture definitions
- `AGENTS.md` - Project development guidelines
- `Makefile` - Test commands
- [Pytest documentation](https://docs.pytest.org/)
- [Pytest fixtures guide](https://docs.pytest.org/en/stable/fixture.html)
