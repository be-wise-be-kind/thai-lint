"""
Purpose: Test suite for violation output formatting in file placement linter

Scope: Validation of consistent violation structure, messages, and serialization formats

Overview: Validates the violation output formatting system that ensures consistent, actionable
    error reporting across all file placement checks. Tests verify violation structure consistency
    (rule_id, file_path, message, severity fields), relative file paths from project root,
    error messages that include violated pattern details, helpful suggestions for correct file
    placement, and machine-readable JSON serialization. Ensures violations provide clear,
    actionable feedback to users and can be consumed by automated tools.

Dependencies: pytest for testing framework, pathlib for Path objects, json for serialization testing

Exports: TestOutputFormatting test class with 5 tests

Interfaces: Tests Violation structure and to_dict() serialization method

Implementation: 5 tests covering violation structure, relative paths, pattern inclusion in messages,
    placement suggestions, and JSON serialization
"""


class TestOutputFormatting:
    """Test consistent violation message format."""
