"""
Purpose: Regression tests for lazy-ignores linter's config-level ignore patterns

Scope: File-level ignore patterns from .thailint.yaml lazy-ignores: config, via check()

Overview: Guards against LazyIgnoresRule.check() never loading its configuration from
    context at all. LazyIgnoresConfig.ignore_patterns is parsed by from_dict(), and
    docs/lazy-ignores-linter.md documents it as a working exclusion mechanism, but
    check() never called load_linter_config() - so nothing in a .thailint.yaml
    lazy-ignores: block, including ignore_patterns, ever reached the rule. Verifies a
    file matching an ignore glob is skipped entirely, while a non-matching file with an
    unjustified suppression is still reported. Uses check(context), not the lower-level
    check_content() other tests in this directory use, since check() is exactly the
    entry point that was skipping config loading.

Dependencies: pytest, src.linters.lazy_ignores, tests.unit.linters.lazy_ignores.conftest

Exports: TestLazyIgnoresIgnorePatterns

Interfaces: Tests LazyIgnoresRule.check() with ignore_patterns in config metadata

Implementation: Mock-based testing with configuration injection containing ignore patterns
"""

from .conftest import PYTHON_WITH_TYPE_IGNORE, create_mock_context


class TestLazyIgnoresIgnorePatterns:
    """Test configuration-based ignore patterns for the lazy-ignores linter."""

    def test_ignores_glob_pattern_from_config(self) -> None:
        """A file matching lazy-ignores.ignore_patterns must report zero violations."""
        from src.linters.lazy_ignores import LazyIgnoresRule

        context = create_mock_context(
            PYTHON_WITH_TYPE_IGNORE,
            filename="legacy/shim.py",
            metadata={"lazy-ignores": {"ignore_patterns": ["legacy/**"]}},
        )
        rule = LazyIgnoresRule()

        violations = rule.check(context)

        assert len(violations) == 0, "File under legacy/** should be ignored"

    def test_processes_file_not_in_ignore_list(self) -> None:
        """A file not matching lazy-ignores.ignore_patterns must still be checked."""
        from src.linters.lazy_ignores import LazyIgnoresRule

        context = create_mock_context(
            PYTHON_WITH_TYPE_IGNORE,
            filename="src/shim.py",
            metadata={"lazy-ignores": {"ignore_patterns": ["legacy/**"]}},
        )
        rule = LazyIgnoresRule()

        violations = rule.check(context)

        assert len(violations) > 0, "File outside legacy/** should still be flagged"
