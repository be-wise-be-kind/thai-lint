"""
File: tests/unit/linters/file_header/test_configuration.py
Purpose: Test suite for configuration loading and handling in file header linter
Exports: TestDefaultConfiguration, TestCustomConfiguration, TestInvalidConfiguration
Depends: pytest, conftest.create_mock_context, src.linters.file_header.linter.FileHeaderRule
Related: test_ignore_directives.py, test_mandatory_fields.py

Overview:
    Tests for configuration loading and validation in file header linter including
    default configuration, custom configuration from .thailint.yaml, required fields
    configuration, ignore patterns, and invalid configuration handling. All tests
    initially fail (TDD RED phase) since FileHeaderRule does not exist yet.

Usage:
    pytest tests/unit/linters/file_header/test_configuration.py -v
"""

from tests.unit.linters.file_header.conftest import create_mock_context


class TestDefaultConfiguration:
    """Test default configuration when no custom config provided."""

    def test_uses_default_required_fields_for_python(self):
        """Should use default required fields for Python files."""
        code = '"""Purpose: Test"""'
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should detect missing default required fields
        # Default: Purpose, Scope, Overview, Dependencies, Exports, Interfaces, Implementation
        assert len(violations) >= 6
        violation_messages = " ".join([v.message for v in violations])
        assert "Scope" in violation_messages
        assert "Overview" in violation_messages

    def test_default_atemporal_enforcement_enabled(self):
        """Should enforce atemporal language by default."""
        code = '''"""
Purpose: Created 2025-01-15
Scope: Test
Overview: Test module
Dependencies: None
Exports: None
Interfaces: None
Implementation: Test
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should detect temporal language (date) by default
        assert len(violations) >= 1
        assert any("temporal" in v.message.lower() or "2025" in v.message for v in violations)

    def test_default_ignore_patterns_exclude_tests(self):
        """Should exclude test files by default."""
        code = '"""Purpose: Test"""'
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        # Note: Default config should ignore test_*.py files
        context = create_mock_context(code, "test_module.py")
        _ = rule.check(context)

        # Depending on default config, test files may be ignored
        # This tests that default ignore patterns are respected
        # If test files are ignored by default, violations should be 0
        # This behavior will be determined by FileHeaderConfig defaults


class TestCustomConfiguration:
    """Test custom configuration loading."""

    def test_loads_custom_required_fields(self):
        """Should load custom required fields from configuration."""
        code = '''"""
Purpose: Custom config test
CustomField: Custom value
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(
            code,
            "test.py",
            metadata={"file_header": {"required_fields": {"python": ["Purpose", "CustomField"]}}},
        )
        violations = rule.check(context)

        # Should only require Purpose and CustomField, not default fields
        # Should have no violations if both are present
        missing_violations = [v for v in violations if "missing" in v.message.lower()]
        assert len(missing_violations) == 0

    def test_loads_custom_ignore_patterns(self):
        """Should load custom ignore patterns from configuration."""
        code = '"""Purpose: Test"""'
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(
            code,
            "generated/auto_gen.py",
            metadata={"file_header": {"ignore": ["generated/**", "vendor/**"]}},
        )
        violations = rule.check(context)

        # Should ignore files matching custom patterns
        assert len(violations) == 0

    def test_can_disable_atemporal_enforcement(self):
        """Should allow disabling atemporal language enforcement."""
        code = '''"""
Purpose: Created 2025-01-15
Scope: Test
Overview: Test module
Dependencies: None
Exports: None
Interfaces: None
Implementation: Test
"""
'''
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(
            code, "test.py", metadata={"file_header": {"enforce_atemporal": False}}
        )
        violations = rule.check(context)

        # Should not detect temporal language when disabled
        temporal_violations = [v for v in violations if "temporal" in v.message.lower()]
        assert len(temporal_violations) == 0


class TestInvalidConfiguration:
    """Test handling of invalid configuration."""

    def test_handles_missing_configuration_gracefully(self):
        """Should handle missing configuration gracefully with defaults."""
        code = '"""Purpose: Test"""'
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        # No metadata provided - should use defaults
        context = create_mock_context(code, "test.py")
        violations = rule.check(context)

        # Should not crash, should use default configuration
        assert isinstance(violations, list)

    def test_handles_empty_configuration_gracefully(self):
        """Should handle empty configuration gracefully."""
        code = '"""Purpose: Test"""'
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(
            code,
            "test.py",
            metadata={"file_header": {}},  # Empty config
        )
        violations = rule.check(context)

        # Should not crash, should use defaults
        assert isinstance(violations, list)

    def test_handles_invalid_metadata_type(self):
        """Should handle invalid metadata type gracefully."""
        code = '"""Purpose: Test"""'
        from src.linters.file_header.linter import FileHeaderRule

        rule = FileHeaderRule()
        context = create_mock_context(
            code,
            "test.py",
            metadata="invalid",  # Invalid type
        )
        violations = rule.check(context)

        # Should not crash, should use defaults
        assert isinstance(violations, list)
