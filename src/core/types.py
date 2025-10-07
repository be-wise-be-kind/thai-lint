"""
Purpose: Core type definitions for the linter framework

Scope: Fundamental data types used across all linter components and rules

Overview: Defines the essential data structures that form the foundation of the linter
    framework, including violation reporting and severity classification. Provides the
    Violation dataclass for representing linting issues with complete location and context
    information, and the Severity enum implementing a binary error model (violations are
    either errors or not violations). These types are used throughout the framework by
    rules, orchestrators, and output formatters to maintain consistent violation reporting
    and severity handling across all linting operations.

Dependencies: dataclasses for Violation structure, enum for Severity classification

Exports: Severity enum (ERROR level), Violation dataclass with serialization support

Interfaces: Violation.to_dict() -> dict for JSON serialization, Severity.ERROR constant

Implementation: Binary severity model (errors only), dataclass-based violation structure
    with comprehensive field set (rule_id, file_path, line, column, message, severity, suggestion)
"""

from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Binary severity model - errors only.

    Following the design principle that linting violations are either
    errors that must be fixed or they're not violations at all.
    No warnings, info, or other severity levels.
    """

    ERROR = "error"


@dataclass
class Violation:
    """Represents a linting violation.

    A violation contains all the information needed to report a linting
    issue to the user, including location, message, and optional suggestion
    for how to fix it.
    """

    rule_id: str
    """Unique identifier of the rule that detected this violation."""

    file_path: str
    """Path to the file containing the violation."""

    line: int
    """Line number where the violation occurs (1-indexed)."""

    column: int
    """Column number where the violation occurs (0-indexed)."""

    message: str
    """Human-readable description of the violation."""

    severity: Severity = Severity.ERROR
    """Severity level of the violation (always ERROR in binary model)."""

    suggestion: str | None = None
    """Optional suggestion for how to fix the violation."""

    def to_dict(self) -> dict[str, str | int | None]:
        """Convert violation to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the violation with all fields.
        """
        return {
            "rule_id": self.rule_id,
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "severity": self.severity.value,
            "suggestion": self.suggestion,
        }
