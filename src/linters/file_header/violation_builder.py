"""
Purpose: Builds violation messages for file header linter

Scope: Violation message creation for file header validation failures

Overview: Creates formatted violation messages for file header validation failures.
    Handles missing fields, atemporal language, and other header issues with clear,
    actionable messages. Provides consistent violation format across all validation types
    including rule_id, message, location, severity, and helpful suggestions. Supports
    multiple violation types with appropriate error messages and remediation guidance.

Dependencies: Violation and Severity types from core.types module

Exports: ViolationBuilder class

Interfaces: build_missing_field(field_name, file_path, line) -> Violation,
    build_atemporal_violation(pattern, description, file_path, line) -> Violation

Implementation: Builder pattern with message templates for different violation types
"""

from src.core.types import Severity, Violation


class ViolationBuilder:
    """Builds violation messages for file header issues."""

    def __init__(self, rule_id: str):
        """Initialize with rule ID.

        Args:
            rule_id: Rule identifier for violations
        """
        self.rule_id = rule_id

    def build_missing_field(self, field_name: str, file_path: str, line: int = 1) -> Violation:
        """Build violation for missing mandatory field.

        Args:
            field_name: Name of missing field
            file_path: Path to file
            line: Line number (default 1 for header)

        Returns:
            Violation object describing missing field
        """
        return Violation(
            rule_id=self.rule_id,
            message=f"Missing mandatory field: {field_name}",
            file_path=file_path,
            line=line,
            column=1,
            severity=Severity.ERROR,
            suggestion=f"Add '{field_name}:' field to file header",
        )

    def build_atemporal_violation(
        self, pattern: str, description: str, file_path: str, line: int
    ) -> Violation:
        """Build violation for temporal language.

        Args:
            pattern: Matched regex pattern
            description: Description of temporal language
            file_path: Path to file
            line: Line number of violation

        Returns:
            Violation object describing temporal language issue
        """
        return Violation(
            rule_id=self.rule_id,
            message=f"Temporal language detected: {description}",
            file_path=file_path,
            line=line,
            column=1,
            severity=Severity.ERROR,
            suggestion="Use present-tense factual descriptions without temporal references",
        )
