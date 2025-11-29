"""
Purpose: Unit tests validating docstrings are excluded from DRY duplication detection

Scope: Testing docstring filtering to prevent false positive duplication violations

Overview: Comprehensive test suite ensuring identical docstrings appearing in multiple
    functions or classes are not incorrectly flagged as duplicate code violations.
    Docstrings are documentation rather than logic and should be filtered from DRY analysis.
    Tests class docstrings, function docstrings, and module docstrings across multiple files
    to ensure consistent filtering behavior.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: test_class_docstrings_not_flagged, test_function_docstrings_not_flagged,
    test_module_docstrings_not_flagged test functions

Interfaces: Test functions accepting tmp_path fixture for file system operations

Implementation: Creates temporary Python files with identical docstrings in multiple locations,
    runs DRY linter, validates no violations reported for docstring content
"""

from src import Linter


def test_class_docstrings_not_flagged(tmp_path):
    """Test that identical class docstrings are NOT flagged as duplicate."""
    file1 = tmp_path / "models1.py"
    file1.write_text("""
class DataModel:
    '''
    A data model class for storing information.
    Provides validation and serialization.
    Supports multiple data formats.
    '''

    def process(self):
        return transform_data()
""")

    file2 = tmp_path / "models2.py"
    file2.write_text("""
class ConfigModel:
    '''
    A data model class for storing information.
    Provides validation and serialization.
    Supports multiple data formats.
    '''

    def load(self):
        return load_config()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Docstrings should NOT be flagged as duplicate
    assert len(violations) == 0, "Class docstrings should not be flagged as duplicate"


def test_duplicate_code_after_docstrings_is_still_flagged(tmp_path):
    """Test that actual duplicate code (not docstrings) IS still flagged."""
    file1 = tmp_path / "processor1.py"
    file1.write_text("""
def process_one():
    '''Different docstring for function one.'''
    x = validate(data)
    y = transform(x)
    z = save(y)
    return z
""")

    file2 = tmp_path / "processor2.py"
    file2.write_text("""
def process_two():
    '''Different docstring for function two.'''
    x = validate(data)
    y = transform(x)
    z = save(y)
    return z
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # The actual code (not docstrings) SHOULD be flagged
    assert len(violations) > 0, "Duplicate code after docstrings should still be flagged"
