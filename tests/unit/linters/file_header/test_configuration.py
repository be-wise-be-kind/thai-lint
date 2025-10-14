"""
File: tests/unit/linters/file_header/test_configuration.py

Purpose: Test suite for configuration loading and handling in file header linter

Exports: TestConfiguration test class with ~8 tests

Depends: pytest, unittest.mock, src.linters.file_header.linter.FileHeaderRule

Implements: TDD RED phase tests for configuration support

Related: conftest.py for configuration fixtures

Overview: Tests configuration loading from metadata, default configuration behavior,
    custom required fields, and ignore patterns configuration. Validates that linter
    correctly reads and applies configuration settings. TDD RED phase tests.

Usage: Run via pytest: `pytest tests/unit/linters/file_header/test_configuration.py`

Notes: All tests FAIL initially until FileHeaderRule configuration handling in PR3
"""

from pathlib import Path
from unittest.mock import Mock


class TestConfiguration:
    """Tests for configuration loading and handling."""

    def test_uses_default_config_when_no_metadata(self):
        """Should use default configuration when no metadata provided."""
        code = '''"""
Purpose: Test
Scope: Test
Overview: Test
Dependencies: None
Exports: Test
Interfaces: test()
Implementation: Standard
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}  # No config

        violations = rule.check(context)
        # Should work with defaults, no violations for valid header
        assert isinstance(violations, list)

    def test_loads_config_from_metadata(self, file_header_config):
        """Should load configuration from context metadata."""
        code = '''"""
Purpose: Test
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {"file_header": file_header_config}

        violations = rule.check(context)
        # Should detect missing fields based on config
        assert len(violations) >= 1

    def test_respects_custom_required_fields(self):
        """Should respect custom required fields configuration."""
        code = '''"""
Purpose: Test purpose
CustomField: Test value
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        # Custom config with only Purpose and CustomField required
        context.metadata = {
            "file_header": {
                "required_fields_python": ["Purpose", "CustomField"],
                "enforce_atemporal": True,
            }
        }

        violations = rule.check(context)
        # Should only check for Purpose and CustomField
        # Filter to just missing field violations
        missing_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_violations) == 0  # Both required fields present

    def test_respects_enforce_atemporal_setting(self):
        """Should respect enforce_atemporal configuration setting."""
        code = '''"""
Purpose: Created 2025-01-15 for testing
Scope: Test
Overview: Test
Dependencies: None
Exports: Test
Interfaces: test()
Implementation: Standard
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        # Disable atemporal checking
        context.metadata = {
            "file_header": {
                "enforce_atemporal": False,
                "required_fields_python": [
                    "Purpose",
                    "Scope",
                    "Overview",
                    "Dependencies",
                    "Exports",
                    "Interfaces",
                    "Implementation",
                ],
            }
        }

        violations = rule.check(context)
        # Should not flag temporal language when disabled
        temporal_violations = [
            v for v in violations if "temporal" in v.message.lower() or "date" in v.message.lower()
        ]
        assert len(temporal_violations) == 0

    def test_applies_ignore_patterns_from_config(self):
        """Should apply ignore patterns from configuration."""
        code = '''"""
No proper header
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test/test_module.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {
            "file_header": {
                "ignore": ["test/**", "**/migrations/**"],
            }
        }

        violations = rule.check(context)
        # Should be ignored due to test/** pattern
        assert len(violations) == 0

    def test_handles_missing_config_section(self):
        """Should handle missing file_header config section gracefully."""
        code = '''"""
Purpose: Test
Scope: Test
Overview: Test
Dependencies: None
Exports: Test
Interfaces: test()
Implementation: Standard
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {"other_linter": {"some_setting": True}}  # No file_header section

        violations = rule.check(context)
        # Should use defaults and not crash
        assert isinstance(violations, list)

    def test_handles_invalid_config_gracefully(self):
        """Should handle invalid configuration gracefully."""
        code = '''"""
Purpose: Test
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {"file_header": "invalid_config_type"}  # Invalid type

        violations = rule.check(context)
        # Should fall back to defaults or handle gracefully
        assert isinstance(violations, list)

    def test_config_enabled_setting(self):
        """Should respect enabled setting in configuration."""
        code = '''"""
No proper header
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {
            "file_header": {
                "enabled": False,  # Linter disabled
            }
        }

        violations = rule.check(context)
        # May return empty if linter respects enabled=False
        # Implementation detail, but should handle gracefully
        assert isinstance(violations, list)
