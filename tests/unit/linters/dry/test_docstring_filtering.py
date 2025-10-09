"""
Purpose: Test that docstrings are NOT flagged as duplicate code

Scope: Verify DRY linter filters out docstrings from duplication detection

Overview: Tests that identical docstrings appearing in multiple functions/classes
    are not incorrectly flagged as duplicate code. Docstrings are documentation,
    not logic, and should be filtered from DRY analysis.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: Test functions for docstring filtering

Implementation: Creates files with identical docstrings in multiple locations
    and verifies they are NOT flagged as violations.
"""

from src import Linter


def test_function_docstrings_not_flagged(tmp_path):
    """Test that identical function docstrings are NOT flagged as duplicate."""
    file1 = tmp_path / "utils1.py"
    file1.write_text("""
def helper_one():
    '''
    This is a helper function that does something useful.
    It has multiple lines in the docstring.
    '''
    return process_data()
""")

    file2 = tmp_path / "utils2.py"
    file2.write_text("""
def helper_two():
    '''
    This is a helper function that does something useful.
    It has multiple lines in the docstring.
    '''
    return process_other_data()
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
    assert len(violations) == 0, "Docstrings should not be flagged as duplicate"


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


def test_module_docstrings_not_flagged(tmp_path):
    """Test that identical module docstrings are NOT flagged as duplicate."""
    file1 = tmp_path / "service1.py"
    file1.write_text("""'''
Service module for handling business logic.
Provides core functionality for the application.
Includes error handling and logging.
'''

def execute():
    return run_service()
""")

    file2 = tmp_path / "service2.py"
    file2.write_text("""'''
Service module for handling business logic.
Provides core functionality for the application.
Includes error handling and logging.
'''

def start():
    return start_service()
""")

    config = tmp_path / ".thailint.yaml"
    config.write_text("""dry:
  enabled: true
  min_duplicate_lines: 3
  cache_enabled: false
""")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Module docstrings should NOT be flagged as duplicate
    assert len(violations) == 0, "Module docstrings should not be flagged as duplicate"


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
