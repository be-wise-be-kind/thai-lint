"""
Purpose: Shared utility functions for creating IgnoreDirective objects

Scope: Common directive creation and path normalization for ignore detectors

Overview: Provides shared utility functions used across Python, TypeScript, and test skip
    detectors. Centralizes logic for normalizing file paths, extracting rule IDs from
    regex matches, extracting inline justifications, and creating IgnoreDirective objects
    to avoid code duplication.

Dependencies: re for match handling, pathlib for file paths, types module for dataclasses

Exports: normalize_path, extract_rule_ids, create_directive, create_directive_no_rules,
    extract_inline_justification

Interfaces: Pure utility functions with no state

Implementation: Simple helper functions for directive creation

Suppressions:
    too-many-arguments: create_directive needs all params for proper IgnoreDirective construction
    too-many-positional-arguments: Factory function mirrors IgnoreDirective fields
"""

import re
from pathlib import Path

from src.linters.lazy_ignores.types import IgnoreDirective, IgnoreType

# Pattern for inline justification: space-dash-space followed by text
INLINE_JUSTIFICATION_PATTERN = re.compile(r"\s+-\s+(.+)$")


def normalize_path(file_path: Path | str | None) -> Path:
    """Normalize file path to Path object.

    Args:
        file_path: Path object, string path, or None

    Returns:
        Path object, defaults to Path("unknown") if None
    """
    if file_path is None:
        return Path("unknown")
    if isinstance(file_path, str):
        return Path(file_path)
    return file_path


def extract_inline_justification(raw_text: str) -> str | None:
    """Extract inline justification from raw directive text.

    Looks for the pattern " - " (space-dash-space) followed by justification text.
    This allows inline justifications like:
        # noqa: PLR0912 - state machine inherently complex
        # type: ignore[arg-type] - library has typing bug

    Args:
        raw_text: The raw comment text containing the ignore directive

    Returns:
        The justification text if found, None otherwise.
        Returns None for empty/whitespace-only justifications.
    """
    match = INLINE_JUSTIFICATION_PATTERN.search(raw_text)
    if not match:
        return None

    justification = match.group(1).strip()
    return justification if justification else None


def _get_captured_group(match: re.Match[str]) -> str | None:
    """Get the first captured group from a regex match if it exists.

    Args:
        match: Regex match object

    Returns:
        Captured group text or None if no capture groups
    """
    if match.lastindex is None or match.lastindex < 1:
        return None
    return match.group(1)


def extract_rule_ids(match: re.Match[str]) -> list[str]:
    """Extract rule IDs from regex match group 1.

    Args:
        match: Regex match object with optional group 1 containing rule IDs

    Returns:
        List of rule ID strings, empty if no specific rules
    """
    group = _get_captured_group(match)
    if not group:
        return []

    ids = [rule_id.strip() for rule_id in group.split(",")]
    return [rule_id for rule_id in ids if rule_id]


def create_directive(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    match: re.Match[str],
    ignore_type: IgnoreType,
    line_num: int,
    file_path: Path,
    rule_ids: tuple[str, ...] | None = None,
    full_line: str | None = None,
) -> IgnoreDirective:
    """Create an IgnoreDirective from a regex match.

    Args:
        match: Regex match object
        ignore_type: Type of ignore pattern
        line_num: 1-indexed line number
        file_path: Path to source file
        rule_ids: Optional tuple of rule IDs; if None, extracts from match group 1
        full_line: Optional full line text for extracting inline justification

    Returns:
        IgnoreDirective for this match
    """
    if rule_ids is None:
        rule_ids = tuple(extract_rule_ids(match))

    # Use full line from match position to capture inline justification
    if full_line is not None:
        raw_text = full_line[match.start() :].strip()
    else:
        raw_text = match.group(0).strip()

    inline_justification = extract_inline_justification(raw_text)

    return IgnoreDirective(
        ignore_type=ignore_type,
        rule_ids=rule_ids,
        line=line_num,
        column=match.start() + 1,
        raw_text=raw_text,
        file_path=file_path,
        inline_justification=inline_justification,
    )


def create_directive_no_rules(
    match: re.Match[str],
    ignore_type: IgnoreType,
    line_num: int,
    file_path: Path,
) -> IgnoreDirective:
    """Create an IgnoreDirective without rule IDs (for patterns like test skips).

    Args:
        match: Regex match object
        ignore_type: Type of ignore pattern
        line_num: 1-indexed line number
        file_path: Path to source file

    Returns:
        IgnoreDirective with empty rule_ids tuple
    """
    return create_directive(match, ignore_type, line_num, file_path, rule_ids=())
