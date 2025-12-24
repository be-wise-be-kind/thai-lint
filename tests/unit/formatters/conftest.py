"""
Purpose: Shared fixtures for SARIF formatter tests

Scope: Formatter test utilities and sample data

Overview: Provides reusable fixtures for testing SarifFormatter including formatter instance,
    sample violations, and factory functions for creating test data. Reduces boilerplate
    across all formatter tests.

Dependencies: pytest, src.core.types.Violation, src.core.types.Severity, src.formatters.sarif

Exports: formatter, sample_violation, empty_violations, multiple_violations, make_violation,
    format_single, mixed_methods_code fixtures

Interfaces: pytest fixtures for test setup and violation creation

Implementation: Factory fixtures for flexible test data creation, module-scoped formatter
"""

from typing import NamedTuple

import pytest

from src.core.types import Severity, Violation
from src.formatters.sarif import SarifFormatter


class ViolationTestCase(NamedTuple):
    """Test case for violation-based tests."""

    rule_id: str
    file_path: str
    line: int
    column: int
    message: str
    severity: Severity
    suggestion: str | None
    description: str


@pytest.fixture
def formatter() -> SarifFormatter:
    """Create a SarifFormatter instance."""
    return SarifFormatter()


@pytest.fixture
def sample_violation() -> Violation:
    """Create a sample violation for testing."""
    return Violation(
        rule_id="test.rule-id",
        file_path="src/example.py",
        line=42,
        column=10,
        message="Test violation message",
        severity=Severity.ERROR,
        suggestion="Test suggestion",
    )


@pytest.fixture
def empty_violations() -> list[Violation]:
    """Empty violations list."""
    return []


@pytest.fixture
def multiple_violations() -> list[Violation]:
    """Multiple violations for testing."""
    return [
        Violation(
            rule_id="file-placement.misplaced-file",
            file_path="src/test_utils.py",
            line=1,
            column=0,
            message="Test file in src/ directory",
            severity=Severity.ERROR,
            suggestion="Move to tests/ directory",
        ),
        Violation(
            rule_id="nesting.excessive-depth",
            file_path="src/complex.py",
            line=15,
            column=4,
            message="Nesting depth of 5 exceeds maximum 4",
            severity=Severity.ERROR,
            suggestion=None,
        ),
    ]


@pytest.fixture
def make_violation():
    """Factory fixture for creating custom violations."""

    def _create(
        rule_id: str = "test.rule",
        file_path: str = "test.py",
        line: int = 1,
        column: int = 0,
        message: str = "Test",
        severity: Severity = Severity.ERROR,
        suggestion: str | None = None,
    ) -> Violation:
        return Violation(
            rule_id=rule_id,
            file_path=file_path,
            line=line,
            column=column,
            message=message,
            severity=severity,
            suggestion=suggestion,
        )

    return _create


@pytest.fixture
def format_single(formatter, sample_violation):
    """Pre-formatted SARIF document with sample violation."""
    return formatter.format([sample_violation])
