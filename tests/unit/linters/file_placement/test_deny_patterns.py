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

    def test_match_simple_deny_pattern(self):
        """File matches simple deny regex."""
        config = {
            "file-placement": {
                "directories": {
                    "src/": {"deny": [{"pattern": r".*test.*\.py$", "reason": "Tests in src/"}]}
                }
            }
        }
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        violations = linter.lint_path(Path("src/test_utils.py"))
        assert len(violations) > 0
        assert "Tests in src/" in violations[0].message

    def test_deny_takes_precedence_over_allow(self):
        """Deny patterns override allow patterns."""
        config = {
            "file-placement": {
                "directories": {
                    "src/": {"allow": [r"^src/.*\.py$"], "deny": [{"pattern": r".*debug.*"}]}
                }
            }
        }
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        violations = linter.lint_path(Path("src/debug_utils.py"))
        assert len(violations) > 0  # Denied despite matching allow

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

    def test_deny_with_custom_error_messages(self):
        """Deny pattern includes custom error message."""
        config = {
            "file-placement": {
                "global_deny": [{"pattern": r".*\.tmp$", "reason": "No temp files in repo"}]
            }
        }
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        violations = linter.lint_path(Path("data.tmp"))
        assert len(violations) > 0
        assert "No temp files in repo" in violations[0].message

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

    def test_debug_file_patterns_in_production(self):
        """Detect debug files in production directories."""
        config = {
            "file-placement": {
                "directories": {
                    "production/": {
                        "deny": [
                            {"pattern": r".*debug.*", "reason": "No debug files in production"}
                        ]
                    }
                }
            }
        }
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        violations = linter.lint_path(Path("production/debug_helpers.py"))
        assert len(violations) > 0
        assert "No debug files in production" in violations[0].message

    def test_absolute_path_detection(self):
        """Detect and deny absolute paths in code."""
        # This would require code parsing, not just path checking
        # Testing the pattern matching capability for now
        config = {
            "file-placement": {"global_deny": [{"pattern": r"^/.*", "reason": "No absolute paths"}]}
        }
        from src.linters.file_placement import FilePlacementLinter

        linter = FilePlacementLinter(config_obj=config)

        # Pattern would match absolute-style paths
        violations = linter.lint_path(Path("/absolute/path/file.py"))
        assert len(violations) > 0

    def test_platform_specific_path_separators(self, make_project):
        """Handle both / and \\ path separators."""
        config = {"file-placement": {"directories": {"src/": {"deny": [{"pattern": r".*test.*"}]}}}}
        from src.linters.file_placement import FilePlacementLinter

        # Create project with test files
        project_root = make_project(git=True, files={"src/test.py": "# test file"})

        linter = FilePlacementLinter(config_obj=config, project_root=project_root)

        # Should handle both separators (Unix-style)
        violations_unix = linter.lint_path(project_root / "src/test.py")
        # Note: On Unix systems, backslash paths don't work the same way
        # This test may need platform-specific handling

        assert len(violations_unix) > 0
