"""
Purpose: TypeScript-specific ignore directive checking for magic numbers linter

Scope: Ignore directive detection for TypeScript/JavaScript files

Overview: Provides ignore directive checking functionality specifically for TypeScript and JavaScript
    files in the magic numbers linter. Handles both thailint-style and noqa-style ignore comments
    using TypeScript comment syntax (// instead of #). Extracted from linter.py to reduce file
    size and improve modularity.

Dependencies: IgnoreDirectiveParser from src.linter_config.ignore, Violation type, violation_utils

Exports: TypeScriptIgnoreChecker class

Interfaces: TypeScriptIgnoreChecker.should_ignore(violation, context) -> bool

Implementation: Comment parsing with TypeScript-specific syntax handling, uses shared utilities
"""

from src.core.base import BaseLintContext
from src.core.types import Violation
from src.core.violation_utils import get_violation_line, has_typescript_noqa
from src.linter_config.ignore import get_ignore_parser


class TypeScriptIgnoreChecker:
    """Checks for TypeScript-style ignore directives in magic numbers linter."""

    def __init__(self) -> None:
        """Initialize with standard ignore parser."""
        self._ignore_parser = get_ignore_parser()

    def should_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check if TypeScript violation should be ignored.

        Args:
            violation: Violation to check
            context: Lint context

        Returns:
            True if should ignore
        """
        if self._ignore_parser.should_ignore_violation(violation, context.file_content or ""):
            return True

        return self._check_typescript_ignore(violation, context)

    def _check_typescript_ignore(self, violation: Violation, context: BaseLintContext) -> bool:
        """Check for TypeScript-style ignore directives.

        Args:
            violation: Violation to check
            context: Lint context

        Returns:
            True if line has ignore directive
        """
        line_text = get_violation_line(violation, context)
        if line_text is None:
            return False

        return self._has_typescript_ignore_directive(line_text)

    def _has_typescript_ignore_directive(self, line_text: str) -> bool:
        """Check if line has TypeScript-style ignore directive.

        Args:
            line_text: Line text to check

        Returns:
            True if has ignore directive
        """
        if "// thailint: ignore[magic-numbers]" in line_text:
            return True

        if "// thailint: ignore" in line_text:
            after_ignore = line_text.split("// thailint: ignore")[1].split("//")[0]
            if "[" not in after_ignore:
                return True

        return has_typescript_noqa(line_text)
