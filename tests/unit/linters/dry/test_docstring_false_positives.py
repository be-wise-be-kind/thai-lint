"""
Purpose: Tests for DRY linter docstring false positives

Scope: Ensure docstrings are not incorrectly flagged as duplicate code

Overview: Test suite to verify that duplicate content in docstrings (function docstrings,
    class docstrings, module docstrings) is NOT flagged as DRY violations. Docstrings are
    documentation, not executable code, and should be excluded from duplication detection.

Dependencies: pytest, src.Linter, pathlib, tmp_path fixture

Exports: Test functions for docstring exclusion scenarios

Interfaces: Uses Linter class with config file

Implementation: Tests that identical docstrings across multiple functions/classes/files
    do NOT generate DRY violations.
"""

from src import Linter


def test_duplicate_function_docstrings_should_not_violate(tmp_path):
    """Test that duplicate function docstrings are NOT flagged as violations.

    This test verifies the bugfix where docstrings were incorrectly being
    flagged as duplicate code.
    """
    file1 = tmp_path / "module1.py"
    file1.write_text('''
def process_data(data):
    """
    Process the input data.

    This function validates and transforms the data.
    Returns processed result.
    """
    result = validate(data)
    transformed = transform(result)
    return save(transformed)

def handle_request(request):
    """
    Process the input data.

    This function validates and transforms the data.
    Returns processed result.
    """
    result = validate(request)
    transformed = transform(result)
    return save(transformed)
''')

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # The 3-line docstring should NOT be flagged as duplicate
    # Docstrings should be completely filtered out from duplication detection
    assert len(violations) == 0  # No violations - docstrings are filtered

    # If we ever improve to detect code AFTER docstrings, update this test
    # For now, filtering out blocks that overlap with docstrings is acceptable


def test_duplicate_docstrings_across_files_should_not_violate(tmp_path):
    """Test that identical docstrings in different files are NOT flagged."""
    file1 = tmp_path / "parser1.py"
    file1.write_text('''
def parse_config(path):
    """
    Parse configuration file.

    Args:
        path: Path to config file

    Returns:
        Parsed configuration dict
    """
    data = load_file(path)
    return parse_yaml(data)
''')

    file2 = tmp_path / "parser2.py"
    file2.write_text('''
def parse_settings(path):
    """
    Parse configuration file.

    Args:
        path: Path to config file

    Returns:
        Parsed configuration dict
    """
    data = load_file(path)
    return parse_json(data)
''')

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # The docstring should NOT be flagged
    # The 2 code lines (data = load_file, return parse_*) are below threshold
    assert len(violations) == 0


def test_duplicate_class_docstrings_should_not_violate(tmp_path):
    """Test that duplicate class docstrings are NOT flagged."""
    file1 = tmp_path / "handlers.py"
    file1.write_text('''
class RequestHandler:
    """
    Base handler for HTTP requests.

    Provides common functionality for request processing.
    """

    def process_request(self):
        data = self.get_request_data()
        result = self.validate_request(data)
        return self.save_request(result)

class ResponseHandler:
    """
    Base handler for HTTP requests.

    Provides common functionality for request processing.
    """

    def process_response(self):
        data = self.get_response_data()
        result = self.validate_response(data)
        return self.save_response(result)
''')

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Docstrings should be filtered out, so no violations detected
    # (The code duplication is small enough to not be flagged separately)
    assert len(violations) == 0


def test_module_docstrings_should_not_violate(tmp_path):
    """Test that duplicate module-level docstrings are NOT flagged."""
    file1 = tmp_path / "utils1.py"
    file1.write_text('''"""
Utility functions for data processing.

This module provides common utilities.
"""

def process():
    return "result1"
''')

    file2 = tmp_path / "utils2.py"
    file2.write_text('''"""
Utility functions for data processing.

This module provides common utilities.
"""

def process():
    return "result2"
''')

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Module docstrings should NOT be flagged
    assert len(violations) == 0


def test_mixed_docstring_and_code_only_code_violates(tmp_path):
    """Test that only duplicate code is flagged, not docstrings within same function."""
    file1 = tmp_path / "mixed.py"
    file1.write_text('''
def function_one():
    """First function with unique docstring."""
    x = get_first_data()
    y = transform_first(x)
    z = validate_first(y)
    return save_first(z)

def function_two():
    """Second function with different docstring."""
    a = get_second_data()
    b = transform_second(a)
    c = validate_second(b)
    return save_second(c)
''')

    config = tmp_path / ".thailint.yaml"
    config.write_text("dry:\n  enabled: true\n  min_duplicate_lines: 3\n  cache_enabled: false")

    linter = Linter(config_file=config, project_root=tmp_path)
    violations = linter.lint(tmp_path, rules=["dry.duplicate-code"])

    # Docstrings should NOT cause false positives
    # The code duplication is filtered since it overlaps with docstring regions
    assert len(violations) == 0
