"""
Purpose: Ignore directive marker detection for thailint comments

Scope: Detection of thailint and design-lint ignore markers in source code

Overview: Provides functions for detecting various ignore directive markers in code
    comments. Supports file-level ignores, line-level ignores, block ignores, and
    next-line ignores. Works with both Python (#) and JavaScript (//) comment styles.
    All checks are case-insensitive.

Dependencies: None (pure string operations)

Exports: Marker detection functions for various ignore directive types

Interfaces: has_*_marker(line) -> bool for each marker type

Implementation: String-based pattern detection with case-insensitive matching
"""


def has_ignore_directive_marker(line: str) -> bool:
    """Check if line contains a file-level ignore directive marker.

    Args:
        line: Line of code to check

    Returns:
        True if line has ignore-file marker
    """
    line_lower = line.lower()
    return "# thailint: ignore-file" in line_lower or "# design-lint: ignore-file" in line_lower


def has_line_ignore_marker(code: str) -> bool:
    """Check if code line has an inline ignore marker.

    Args:
        code: Line of code to check

    Returns:
        True if line has inline ignore marker
    """
    code_lower = code.lower()
    return (
        "# thailint: ignore" in code_lower
        or "# design-lint: ignore" in code_lower
        or "// thailint: ignore" in code_lower
        or "// design-lint: ignore" in code_lower
    )


def has_ignore_next_line_marker(line: str) -> bool:
    """Check if line has ignore-next-line marker.

    Args:
        line: Line of code to check

    Returns:
        True if line has ignore-next-line marker
    """
    return "# thailint: ignore-next-line" in line or "# design-lint: ignore-next-line" in line


def has_ignore_start_marker(line: str) -> bool:
    """Check if line has ignore-start comment marker.

    Only matches actual comment lines (starting with # or //), not strings
    containing the marker text.

    Args:
        line: Line of code to check

    Returns:
        True if line is a proper ignore-start comment
    """
    stripped = line.strip().lower()
    if not (stripped.startswith("#") or stripped.startswith("//")):
        return False
    return "ignore-start" in stripped and ("thailint:" in stripped or "design-lint:" in stripped)


def has_ignore_end_marker(line: str) -> bool:
    """Check if line has ignore-end comment marker.

    Only matches actual comment lines (starting with # or //), not strings
    containing the marker text.

    Args:
        line: Line of code to check

    Returns:
        True if line is a proper ignore-end comment
    """
    stripped = line.strip().lower()
    if not (stripped.startswith("#") or stripped.startswith("//")):
        return False
    return "ignore-end" in stripped and ("thailint:" in stripped or "design-lint:" in stripped)


def check_general_ignore(line: str) -> bool:
    """Check if line has general ignore directive (no specific rules).

    Args:
        line: Line containing ignore directive

    Returns:
        True if no specific rules are specified (not bracket syntax)
    """
    return "ignore-file[" not in line
