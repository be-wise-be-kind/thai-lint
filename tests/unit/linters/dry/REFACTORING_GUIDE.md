# DRY Test Refactoring Guide

## Purpose
Guide for completing the fixture-based refactoring of DRY linter tests.

## Progress

### ✅ Completed
- **conftest.py**: 10 powerful fixtures created
- **test_python_duplicates.py**: 15/15 tests refactored (100%)
- **test_cross_file_detection.py**: 2/11 tests refactored (18%)

### 🔄 In Progress
- **test_typescript_duplicates.py**: 0/15 tests (0%)
- **test_cross_file_detection.py**: 9/11 tests remaining (82%)
- **test_within_file_detection.py**: 0/10 tests (0%)
- **test_cache_operations.py**: 0/11 tests (0%)
- **test_config_loading.py**: 0/11 tests (0%)
- **test_violation_messages.py**: 0/8 tests (0%)
- **test_ignore_directives.py**: 0/9 tests (0%)
- **test_cli_interface.py**: 0/4 tests (0%)
- **test_library_api.py**: 0/4 tests (0%)
- **test_edge_cases.py**: 0/8 tests (0%)

**Total**: 17/106 tests refactored (16%)

---

## Available Fixtures

### File Creation Fixtures

#### `create_python_file(name, content)`
Create Python files with given content.

**Example**:
```python
def test_example(tmp_path, create_python_file, create_config):
    create_python_file("module1", "def foo(): pass")
    config = create_config()
    # ... rest of test
```

#### `create_typescript_file(name, content, extension=".ts")`
Create TypeScript/JavaScript files.

**Example**:
```python
def test_ts_example(tmp_path, create_typescript_file):
    create_typescript_file("module1", "function foo() {}", ".ts")
```

#### `create_duplicate_files(duplicate_code, count=2, prefix="file", extension=".py")`
Create multiple files with the same duplicate code - **MOST USEFUL**!

**Example**:
```python
def test_5_files(tmp_path, create_duplicate_files, create_config):
    code = """    for item in items:
        item.save()"""
    create_duplicate_files(code, count=5, prefix="module")
    config = create_config()
    # ... test expects 5 violations
```

#### `create_config(enabled=True, min_duplicate_lines=3, cache_enabled=False, **kwargs)`
Create `.thailint.yaml` configuration.

**Example**:
```python
# Default config
config = create_config()

# Custom config
config = create_config(min_duplicate_lines=5, cache_enabled=True)

# With additional options
config = create_config(ignore_patterns=["tests/", "*.test.py"])
```

#### `create_subdirectory(dir_path)`
Create nested directories.

**Example**:
```python
def test_nested(tmp_path, create_subdirectory, create_python_file):
    src_dir = create_subdirectory("src/utils")
    # Now can create files in src/utils/
```

#### `create_unique_files(count=10, prefix="unique")`
Create multiple files with unique content (no duplicates).

**Example**:
```python
def test_no_duplicates(tmp_path, create_unique_files, create_config):
    create_unique_files(count=10)
    config = create_config()
    # ... test expects 0 violations
```

### Code Snippet Fixtures

#### `duplicate_code_3_lines`
Standard 3-line Python duplicate.

#### `duplicate_code_5_lines`
Standard 5-line Python duplicate.

#### `duplicate_code_10_lines`
Standard 10-line Python duplicate.

#### `duplicate_code_ts_3_lines`
Standard 3-line TypeScript duplicate.

#### `duplicate_code_ts_5_lines`
Standard 5-line TypeScript duplicate.

---

## Refactoring Patterns

### Pattern 1: Simple 2-File Duplicate

**Before** (19 lines):
```python
def test_duplicate(tmp_path):
    file1 = tmp_path / "file1.py"
    file1.write_text("""
def foo():
    x = 1
    y = 2
    z = 3
""")
    file2 = tmp_path / "file2.py"
    file2.write_text("""
def bar():
    x = 1
    y = 2
    z = 3
""")
    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")
    # ... rest
```

**After** (7 lines - 63% reduction):
```python
def test_duplicate(tmp_path, create_duplicate_files, create_config, duplicate_code_3_lines):
    create_duplicate_files(duplicate_code_3_lines, count=2)
    config = create_config()
    # ... rest
```

### Pattern 2: N-File Duplicate with Loop

**Before** (12 lines):
```python
def test_5_files(tmp_path):
    duplicate_code = "..."
    for i in range(1, 6):
        file = tmp_path / f"module{i}.py"
        file.write_text(f"def func{i}():\n{duplicate_code}\n")
    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:...")
    # ... rest
```

**After** (4 lines - 67% reduction):
```python
def test_5_files(tmp_path, create_duplicate_files, create_config):
    create_duplicate_files("...", count=5, prefix="module")
    config = create_config()
    # ... rest
```

### Pattern 3: Custom Code Per File

**Before** (15 lines):
```python
def test_custom(tmp_path):
    file1 = tmp_path / "utils_a.py"
    file1.write_text("""
def validate(x):
    if not x:
        return False
    return True
""")
    file2 = tmp_path / "utils_b.py"
    file2.write_text("""
def check(x):
    if not x:
        return False
    return True
""")
    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:...")
    # ... rest
```

**After** (8 lines - 47% reduction):
```python
def test_custom(tmp_path, create_python_file, create_config):
    code = """    if not x:
        return False
    return True"""
    create_python_file("utils_a", f"def validate(x):\n{code}\n")
    create_python_file("utils_b", f"def check(x):\n{code}\n")
    config = create_config()
    # ... rest
```

### Pattern 4: Unique Files (No Duplicates Expected)

**Before** (25+ lines):
```python
def test_unique(tmp_path):
    file1 = tmp_path / "unique1.py"
    file1.write_text("""
def process_users():
    users = fetch_users()
    return transform_users(users)
""")
    file2 = tmp_path / "unique2.py"
    file2.write_text("""
def process_products():
    products = fetch_products()
    return transform_products(products)
""")
    # ... more files
    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:...")
    # ... rest
```

**After** (4 lines - 84% reduction):
```python
def test_unique(tmp_path, create_unique_files, create_config):
    create_unique_files(count=10)
    config = create_config()
    # ... rest expects 0 violations
```

---

## Step-by-Step Refactoring Process

### For Each Test File:

1. **Add fixture imports to test function signature**
   ```python
   # Before
   def test_something(tmp_path):

   # After
   def test_something(tmp_path, create_python_file, create_config):
   ```

2. **Replace file creation patterns**
   - Look for `tmp_path / "filename.py"` followed by `write_text()`
   - Replace with `create_python_file("filename", content)`
   - Or use `create_duplicate_files()` if same code in multiple files

3. **Replace config creation**
   - Look for `.thailint.yaml` creation with `write_text()`
   - Replace with `config = create_config(...)`

4. **Use code snippet fixtures where possible**
   - If test uses 3/5/10 line duplicates, use fixtures
   - Otherwise, define inline (still cleaner than before)

5. **Test the refactored version**
   ```bash
   pytest tests/unit/linters/dry/test_filename.py -v
   ```

---

## Example: Complete File Refactoring

See `test_python_duplicates.py` for a fully refactored example with all 15 tests using fixtures.

**Key improvements**:
- **Average 50-70% line reduction** per test
- **Much more readable** - intent is clear
- **Easier to maintain** - change fixture once, affects all tests
- **Consistent** - all tests use same patterns

---

## Quick Reference Commands

```bash
# Test single file
pytest tests/unit/linters/dry/test_python_duplicates.py -v

# Test specific test
pytest tests/unit/linters/dry/test_python_duplicates.py::test_exact_3_line_duplicate -v

# Test all DRY tests (will fail until implementation)
pytest tests/unit/linters/dry/ -v

# Check test count
pytest tests/unit/linters/dry/ --collect-only | grep "test session starts" -A 2
```

---

## Notes

- Tests are **expected to fail** until DRY linter is implemented (PR2)
- Fixtures use `cache_enabled: false` by default for test isolation
- The `create_config()` fixture is flexible - pass any YAML options as kwargs
- TypeScript tests should use `create_typescript_file()` and `duplicate_code_ts_*` fixtures

---

## Completion Checklist

When refactoring a test file:
- [ ] All tests use fixtures instead of manual file creation
- [ ] All tests use `create_config()` instead of manual YAML
- [ ] Tests still have same assertions and logic
- [ ] Tests still fail with same error (ModuleNotFoundError or assertion on violations)
- [ ] File is committed with descriptive commit message
