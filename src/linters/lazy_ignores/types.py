"""
Purpose: Type definitions for lazy-ignores linter

Scope: Data structures for ignore directives and suppression entries

Overview: Defines core types for the lazy-ignores linter including IgnoreType enum for
    categorizing different suppression patterns, IgnoreDirective dataclass for representing
    detected ignores in code, and SuppressionEntry dataclass for representing declared
    suppressions in file headers. Supports Python (noqa, type:ignore, pylint, nosec),
    TypeScript (@ts-ignore, eslint-disable), thai-lint (thailint:ignore), and test skip
    patterns (pytest.mark.skip, it.skip, describe.skip).

Dependencies: dataclasses, enum, pathlib

Exports: IgnoreType, IgnoreDirective, SuppressionEntry

Interfaces: Frozen dataclasses for immutable ignore representation

Implementation: Enum-based categorization with frozen dataclasses for thread safety
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class IgnoreType(Enum):
    """Type of linting ignore directive."""

    NOQA = "noqa"
    TYPE_IGNORE = "type:ignore"
    PYLINT_DISABLE = "pylint:disable"
    NOSEC = "nosec"
    TS_IGNORE = "ts-ignore"
    TS_NOCHECK = "ts-nocheck"
    TS_EXPECT_ERROR = "ts-expect-error"
    ESLINT_DISABLE = "eslint-disable"
    THAILINT_IGNORE = "thailint:ignore"
    THAILINT_IGNORE_FILE = "thailint:ignore-file"
    THAILINT_IGNORE_NEXT = "thailint:ignore-next-line"
    THAILINT_IGNORE_BLOCK = "thailint:ignore-start"
    # Test skip patterns
    PYTEST_SKIP = "pytest:skip"
    PYTEST_SKIPIF = "pytest:skipif"
    JEST_SKIP = "jest:skip"
    MOCHA_SKIP = "mocha:skip"


@dataclass(frozen=True)
class IgnoreDirective:
    """Represents a linting ignore found in code."""

    ignore_type: IgnoreType
    rule_ids: tuple[str, ...]  # Can have multiple: noqa: PLR0912, PLR0915
    line: int
    column: int
    raw_text: str  # Original comment text
    file_path: Path


@dataclass(frozen=True)
class SuppressionEntry:
    """Represents a suppression declared in file header."""

    rule_id: str  # Normalized rule ID
    justification: str
    raw_text: str  # Original header line
