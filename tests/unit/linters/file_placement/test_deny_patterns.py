"""
Purpose: Test suite for deny pattern matching in file placement linter

Scope: Pattern matching validation for deny rules including precedence over allow patterns and custom error messages

Overview: Validates the deny pattern matching system that prevents specific files from being placed
    in certain locations regardless of allow patterns. Tests verify simple deny regex matching,
    precedence rules (deny always overrides allow), multiple deny patterns (file rejected if matches
    ANY deny), custom error messages from deny patterns, detection of temporary files, debug files
    in production, absolute path usage in code, and platform-specific path separator handling.
    Ensures deny patterns provide strong enforcement with clear, customizable violation messages.

Dependencies: pytest for testing framework, pathlib for Path objects

Exports: TestDenyPatternMatching test class with 8 tests

Interfaces: Tests FilePlacementLinter.lint_path(Path) with deny pattern configurations

Implementation: 8 tests covering simple deny, precedence over allow, multiple patterns, custom messages,
    temp file detection, debug file detection, absolute paths, and cross-platform paths
"""

from pathlib import Path


class TestDenyPatternMatching:
    """Test files matching deny patterns."""

    def test_multiple_deny_patterns(self):
        """File can match any of multiple deny patterns."""
        config = {
            "file-placement": {
                "directories": {
                    "src/": {
                        "deny": [
                            {"pattern": r".*test.*"},
                            {"pattern": r".*debug.*"},
                            {"pattern": r".*tmp.*"},
                        ]
                    }
                }
            }
        }
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        assert len(linter.lint_path(Path("src/test.py"))) > 0
        assert len(linter.lint_path(Path("src/debug.py"))) > 0
        assert len(linter.lint_path(Path("src/tmp.py"))) > 0

    def test_temporary_file_patterns(self):
        """Detect temporary files (.tmp, .log, .bak)."""
        config = {
            "file-placement": {
                "global_deny": [{"pattern": r".*\.(tmp|log|bak)$", "reason": "No temporary files"}]
            }
        }
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        assert len(linter.lint_path(Path("file.tmp"))) > 0
        assert len(linter.lint_path(Path("debug.log"))) > 0
        assert len(linter.lint_path(Path("backup.bak"))) > 0
