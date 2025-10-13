"""
Purpose: Test suite for magic numbers linter ignore patterns configuration

Scope: File-level ignore patterns from configuration

Overview: Tests that verify ignore patterns from configuration are properly applied to skip
    files that match glob patterns. Validates that files listed in the ignore section of
    magic-numbers configuration are completely skipped during linting. Tests both specific
    file paths and glob patterns like "test/**" and "**/test_*.py". Ensures configuration-
    based file filtering works correctly before any AST analysis occurs.

Dependencies: pytest for testing framework, pathlib for Path handling, unittest.mock for
    context mocking, src.linters.magic_numbers.linter for MagicNumberRule

Exports: TestIgnorePatterns (4 tests) - specific file, glob patterns, multiple patterns

Interfaces: Tests MagicNumberRule configuration handling through check() method

Implementation: Mock-based testing with configuration injection containing ignore patterns,
    validates that matching files produce zero violations
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.linters.magic_numbers.linter import MagicNumberRule


class TestIgnorePatterns:
    """Test configuration-based ignore patterns."""

    @pytest.mark.parametrize("config_key", ["magic_numbers", "magic-numbers"])
    def test_ignores_specific_file_from_config(self, config_key):
        """Should ignore file that matches specific path in config ignore list.

        Tests both underscore and hyphenated config key formats for backward compatibility.
        """
        code = """
def get_data():
    # File has 110 magic numbers but should be completely ignored
    value1 = 42
    value2 = 999
    value3 = 1234
    value4 = 5678
    return value1 + value2 + value3 + value4
"""
        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("backend/app/famous_tracks.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {
            config_key: {
                "enabled": True,
                "allowed_numbers": [-1, 0, 1, 2],
                "ignore": [
                    "backend/app/famous_tracks.py",  # Should ignore this exact file
                ],
            }
        }

        violations = rule.check(context)

        # Both formats should work after key normalization
        assert len(violations) == 0, (
            f"Should ignore file 'backend/app/famous_tracks.py' per config (key={config_key}), "
            f"but got {len(violations)} violations"
        )

    @pytest.mark.parametrize("config_key", ["magic_numbers", "magic-numbers"])
    def test_ignores_glob_pattern_from_config(self, config_key):
        """Should ignore files matching glob patterns from config.

        Tests both underscore and hyphenated config key formats for backward compatibility.
        """
        code = """
def test_something():
    # Test file should be ignored via glob pattern
    assert calculate(42) == 84
    assert process(999) == 1998
"""
        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("tests/unit/test_calculator.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {
            config_key: {
                "enabled": True,
                "allowed_numbers": [-1, 0, 1, 2],
                "ignore": [
                    "test/**",  # Should match files in test/ directory
                    "**/test_*.py",  # Should match test_*.py anywhere
                ],
            }
        }

        violations = rule.check(context)

        # Both formats should work after key normalization
        assert len(violations) == 0, (
            f"Should ignore test files via glob pattern '**/test_*.py' (key={config_key}), "
            f"but got {len(violations)} violations"
        )

    @pytest.mark.parametrize("config_key", ["magic_numbers", "magic-numbers"])
    def test_ignores_directory_pattern_from_config(self, config_key):
        """Should ignore entire directories from config.

        Tests both underscore and hyphenated config key formats for backward compatibility.
        """
        code = """
def generate_track():
    # File in algorithms/ directory should be ignored
    coordinates = [(100, 200), (300, 400), (500, 600)]
    return coordinates
"""
        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("backend/app/racing/algorithms/generator.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {
            config_key: {
                "enabled": True,
                "allowed_numbers": [-1, 0, 1, 2],
                "ignore": [
                    "backend/app/racing/algorithms/**",  # Should ignore entire directory
                ],
            }
        }

        violations = rule.check(context)

        # Both formats should work after key normalization
        assert len(violations) == 0, (
            f"Should ignore files in 'backend/app/racing/algorithms/**' (key={config_key}), "
            f"but got {len(violations)} violations"
        )

    @pytest.mark.parametrize("config_key", ["magic_numbers", "magic-numbers"])
    def test_processes_file_not_in_ignore_list(self, config_key):
        """Should process files that don't match any ignore patterns.

        Tests both underscore and hyphenated config key formats for backward compatibility.
        This test verifies normal processing still works when files don't match ignore patterns.
        """
        code = """
def calculate():
    return 42 + 999  # These should be flagged
"""
        rule = MagicNumberRule()
        context = Mock()
        context.file_path = Path("src/calculator.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {
            config_key: {
                "enabled": True,
                "allowed_numbers": [-1, 0, 1, 2],
                "ignore": [
                    "backend/app/famous_tracks.py",  # Doesn't match our file
                    "test/**",  # Doesn't match our file
                ],
            }
        }

        violations = rule.check(context)

        # This file is NOT in ignore list, should detect violations normally
        assert len(violations) == 2, (
            f"Should detect violations in non-ignored file (key={config_key}), expected 2, got {len(violations)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
