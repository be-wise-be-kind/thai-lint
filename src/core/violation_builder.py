"""
Purpose: Base violation builder class for consistent violation creation across all linters

Scope: Core violation building functionality used by all linter violation builders

Overview: Provides base classes and data structures for violation creation across all linters.
    Defines ViolationInfo dataclass containing all required and optional violation fields,
    and BaseViolationBuilder class with common build() method. Eliminates duplicate violation
    construction patterns across file_placement, nesting, and srp linters. Ensures consistent
    violation creation with proper defaults for column and severity fields. Linter-specific
    builders extend this base class to inherit common construction logic while maintaining
    their domain-specific message generation and suggestion logic.

Dependencies: dataclasses, src.core.types (Violation, Severity)

Exports: ViolationInfo dataclass, build_violation function, build_violation_from_params function,
    BaseViolationBuilder class (compat)

Interfaces: ViolationInfo(rule_id, file_path, line, message, column, severity),
    build_violation(info: ViolationInfo) -> Violation

Implementation: Uses dataclass for type-safe violation info, functions provide build logic
    that constructs Violation objects with proper defaults
"""

from dataclasses import dataclass

from src.core.types import Severity, Violation


@dataclass
class ViolationInfo:
    """Information needed to build a violation.

    Attributes:
        rule_id: Identifier for the rule that was violated
        file_path: Path to the file containing the violation
        line: Line number where violation occurs (1-indexed)
        message: Description of the violation
        column: Column number where violation occurs (0-indexed, default=1)
        severity: Severity level of the violation (default=ERROR)
        suggestion: Optional suggestion for fixing the violation
    """

    rule_id: str
    file_path: str
    line: int
    message: str
    column: int = 1
    severity: Severity = Severity.ERROR
    suggestion: str | None = None


def build_violation(info: ViolationInfo) -> Violation:
    """Build a Violation from ViolationInfo.

    Args:
        info: ViolationInfo containing all violation details

    Returns:
        Violation object with all fields populated
    """
    return Violation(
        rule_id=info.rule_id,
        file_path=info.file_path,
        line=info.line,
        column=info.column,
        message=info.message,
        severity=info.severity,
        suggestion=info.suggestion,
    )


def build_violation_from_params(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    rule_id: str,
    file_path: str,
    line: int,
    message: str,
    column: int = 1,
    severity: Severity = Severity.ERROR,
    suggestion: str | None = None,
) -> Violation:
    """Build a Violation directly from parameters.

    Note: Pylint too-many-arguments disabled. This convenience function mirrors the
    ViolationInfo dataclass fields (7 parameters, 3 with defaults). The alternative
    would require every caller to create ViolationInfo objects manually, reducing
    readability.

    Args:
        rule_id: Identifier for the rule that was violated
        file_path: Path to the file containing the violation
        line: Line number where violation occurs (1-indexed)
        message: Description of the violation
        column: Column number where violation occurs (0-indexed, default=1)
        severity: Severity level of the violation (default=ERROR)
        suggestion: Optional suggestion for fixing the violation

    Returns:
        Violation object with all fields populated
    """
    info = ViolationInfo(
        rule_id=rule_id,
        file_path=file_path,
        line=line,
        message=message,
        column=column,
        severity=severity,
        suggestion=suggestion,
    )
    return build_violation(info)


# Legacy class wrapper for backward compatibility
class BaseViolationBuilder:
    """Base class for building violations with consistent structure.

    Provides common build() method for creating Violation objects from ViolationInfo.
    Linter-specific builders extend this class to add their domain-specific violation
    creation methods while inheriting the common construction logic.

    Note: This class is a thin wrapper around module-level functions
    for backward compatibility.
    """

    def __init__(self) -> None:
        """Initialize the builder."""
        pass  # No state needed

    def build(self, info: ViolationInfo) -> Violation:
        """Build a Violation from ViolationInfo.

        Args:
            info: ViolationInfo containing all violation details

        Returns:
            Violation object with all fields populated
        """
        return build_violation(info)

    def build_from_params(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        rule_id: str,
        file_path: str,
        line: int,
        message: str,
        column: int = 1,
        severity: Severity = Severity.ERROR,
        suggestion: str | None = None,
    ) -> Violation:
        """Build a Violation directly from parameters.

        Note: Pylint too-many-arguments disabled. This convenience method mirrors the
        ViolationInfo dataclass fields (7 parameters, 3 with defaults). The alternative
        would require every caller to create ViolationInfo objects manually, reducing
        readability. This is a standard builder pattern where all parameters are
        inherently related (Violation fields).

        This is a convenience method that combines ViolationInfo creation and build()
        to reduce duplication in violation builder methods.

        Args:
            rule_id: Identifier for the rule that was violated
            file_path: Path to the file containing the violation
            line: Line number where violation occurs (1-indexed)
            message: Description of the violation
            column: Column number where violation occurs (0-indexed, default=1)
            severity: Severity level of the violation (default=ERROR)
            suggestion: Optional suggestion for fixing the violation

        Returns:
            Violation object with all fields populated
        """
        return build_violation_from_params(
            rule_id=rule_id,
            file_path=file_path,
            line=line,
            message=message,
            column=column,
            severity=severity,
            suggestion=suggestion,
        )
