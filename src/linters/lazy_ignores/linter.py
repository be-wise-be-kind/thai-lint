"""
Purpose: Main LazyIgnoresRule class for detecting unjustified linting suppressions

Scope: Orchestration of ignore detection and header suppression validation

Overview: Provides LazyIgnoresRule that cross-references linting ignore directives found
    in code (noqa, type:ignore, pylint:disable, nosec) and test skip patterns with
    Suppressions entries declared in file headers. Detects two types of violations:
    unjustified ignores/skips (directive without header declaration) and orphaned
    suppressions (header declaration without matching ignore in code). Enforces the
    header-based suppression model requiring human approval for all linting bypasses.

Dependencies: PythonIgnoreDetector, TestSkipDetector, SuppressionsParser, IgnoreSuppressionMatcher

Exports: LazyIgnoresRule

Interfaces: check(context: BaseLintContext) -> list[Violation]

Implementation: Delegation to matcher for cross-reference logic, violation builder for messages
"""

from pathlib import Path

from src.core.base import BaseLintContext, BaseLintRule
from src.core.constants import Language
from src.core.types import Violation

from .header_parser import SuppressionsParser
from .matcher import IgnoreSuppressionMatcher
from .python_analyzer import PythonIgnoreDetector
from .skip_detector import TestSkipDetector
from .types import IgnoreDirective
from .violation_builder import build_orphaned_violation, build_unjustified_violation


class LazyIgnoresRule(BaseLintRule):
    """Detects unjustified linting suppressions and orphaned header entries."""

    def __init__(self, check_test_skips: bool = True) -> None:
        """Initialize the lazy ignores rule with detection components.

        Args:
            check_test_skips: Whether to check for unjustified test skips.
        """
        self._python_detector = PythonIgnoreDetector()
        self._test_skip_detector = TestSkipDetector()
        self._suppression_parser = SuppressionsParser()
        self._matcher = IgnoreSuppressionMatcher(self._suppression_parser)
        self._check_test_skips = check_test_skips

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "lazy-ignores"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Lazy Ignores"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return (
            "Detects linting suppressions (noqa, type:ignore, pylint:disable, nosec) "
            "and test skips without corresponding entries in the file header's "
            "Suppressions section."
        )

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for violations in the given context.

        Args:
            context: The lint context containing file information.

        Returns:
            List of violations for unjustified and orphaned suppressions.
        """
        if context.language != Language.PYTHON:
            return []

        if not context.file_content:
            return []

        file_path = str(context.file_path) if context.file_path else "unknown"
        return self.check_content(context.file_content, file_path)

    def check_content(self, code: str, file_path: str) -> list[Violation]:
        """Check code for unjustified ignores and orphaned suppressions.

        Args:
            code: Source code content to analyze.
            file_path: Path to the file being analyzed.

        Returns:
            List of violations for unjustified and orphaned suppressions.
        """
        # Extract and parse header suppressions
        header = self._suppression_parser.extract_header(code, "python")
        suppressions = self._suppression_parser.parse(header)

        # Find all ignore directives in code
        ignores = self._python_detector.find_ignores(code, Path(file_path))

        # Find test skip directives if enabled
        if self._check_test_skips:
            test_skips = self._test_skip_detector.find_skips(code, Path(file_path), "python")
            ignores = list(ignores) + list(test_skips)

        # Build set of normalized rule IDs used in code
        used_rule_ids = self._matcher.collect_used_rule_ids(ignores)

        # Find violations
        violations: list[Violation] = []
        violations.extend(self._find_unjustified(ignores, suppressions, file_path))
        violations.extend(self._find_orphaned(suppressions, used_rule_ids, file_path))

        return violations

    def _find_unjustified(
        self, ignores: list[IgnoreDirective], suppressions: dict[str, str], file_path: str
    ) -> list[Violation]:
        """Find ignore directives without matching header suppressions."""
        violations: list[Violation] = []

        for ignore in ignores:
            unjustified = self._matcher.find_unjustified_rule_ids(ignore, suppressions)
            if unjustified:
                violations.append(
                    build_unjustified_violation(
                        file_path=file_path,
                        line=ignore.line,
                        column=ignore.column,
                        rule_id=", ".join(unjustified),
                        raw_text=ignore.raw_text,
                    )
                )

        return violations

    def _find_orphaned(
        self, suppressions: dict[str, str], used_rule_ids: set[str], file_path: str
    ) -> list[Violation]:
        """Find header suppressions without matching code ignores."""
        violations: list[Violation] = []
        orphaned = self._matcher.find_orphaned_rule_ids(suppressions, used_rule_ids)

        for rule_id, justification in orphaned:
            violations.append(
                build_orphaned_violation(
                    file_path=file_path,
                    header_line=1,  # Header entries are at file start
                    rule_id=rule_id,
                    justification=justification,
                )
            )

        return violations
