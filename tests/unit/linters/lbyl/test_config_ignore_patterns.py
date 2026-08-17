"""
Purpose: Regression tests for LBYL linter's config-level ignore patterns

Scope: File-level ignore patterns from LBYLConfig.ignore

Overview: Guards against LBYLConfig.ignore being parsed but never enforced.
    docs/lbyl-linter.md documents `ignore:` as a working config option, and
    LBYLConfig.from_dict() does read it, but LBYLRule (built on PythonOnlyLintRule)
    never consulted it before running analysis, so it was silently dead. Verifies a
    file matching an ignore glob is skipped entirely, while a non-matching file with
    the same violation is still reported.

Dependencies: pytest, src.linters.lbyl.linter, src.linters.lbyl.config

Exports: TestLBYLIgnorePatterns

Interfaces: Tests LBYLRule.check() with an LBYLConfig.ignore override

Implementation: Uses the shared mock_context fixture from conftest.py
"""

from src.linters.lbyl.config import LBYLConfig
from src.linters.lbyl.linter import LBYLRule

DICT_KEY_LBYL_CODE = """
def process_config(config: dict) -> str:
    if "api_key" in config:
        return config["api_key"]
    return ""
"""


class TestLBYLIgnorePatterns:
    """Test configuration-based ignore patterns for the LBYL linter."""

    def test_ignores_glob_pattern_from_config(self, mock_context) -> None:
        """A file matching config.ignore must report zero violations."""
        context = mock_context(DICT_KEY_LBYL_CODE, "legacy/config_check.py")
        rule = LBYLRule(config=LBYLConfig(ignore=["legacy/**"]))

        violations = rule.check(context)

        assert violations == [], "File under legacy/** should be ignored"

    def test_processes_file_not_in_ignore_list(self, mock_context) -> None:
        """A file not matching config.ignore must still be checked."""
        context = mock_context(DICT_KEY_LBYL_CODE, "src/config_check.py")
        rule = LBYLRule(config=LBYLConfig(ignore=["legacy/**"]))

        violations = rule.check(context)

        assert len(violations) > 0, "File outside legacy/** should still be flagged"
