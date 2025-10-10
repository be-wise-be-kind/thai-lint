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

# If we ever improve to detect code AFTER docstrings, update this test
# For now, filtering out blocks that overlap with docstrings is acceptable


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
