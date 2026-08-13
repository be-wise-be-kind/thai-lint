"""
Purpose: Tokenization and rolling hash generation for code deduplication

Scope: Code normalization, comment stripping, and hash window generation

Overview: Implements token-based hashing algorithm (Rabin-Karp) for detecting code duplicates.
    Normalizes source code by stripping comments and whitespace, then generates rolling hash
    windows over consecutive lines. Each window represents a potential duplicate code block.
    Uses a stable content hash (blake2b) rather than Python's built-in hash(), whose per-process
    random seed (PYTHONHASHSEED) would otherwise make the same block hash differently in every
    new process - fine for a single run, but fatal for any cache read back across process
    invocations. Supports both Python and JavaScript/TypeScript comment styles.

Dependencies: hashlib (stdlib)

Exports: tokenize, rolling_hash, stable_hash, normalize_line, should_skip_import_line functions

Interfaces: tokenize(code: str) -> list[str],
    rolling_hash(lines: list[str], window_size: int) -> list[tuple],
    stable_hash(snippet: str) -> int,
    normalize_line(line: str) -> str,
    should_skip_import_line(line: str, in_multiline_import: bool) -> tuple

Implementation: Token-based normalization with rolling window algorithm, language-agnostic approach
"""

import hashlib

# Pre-compiled import token set for O(1) membership test
_IMPORT_TOKENS: frozenset[str] = frozenset(("{", "}", "} from"))
_IMPORT_PREFIXES: tuple[str, ...] = ("import ", "from ", "export ")

# Digest size for stable_hash: 8 bytes -> fits a signed 64-bit int, matching the range
# hash() previously produced.
_STABLE_HASH_DIGEST_SIZE = 8


def stable_hash(snippet: str) -> int:
    """Compute a hash for a code snippet that is stable across process boundaries.

    Python's built-in hash() salts str hashing with a per-process random seed
    (PYTHONHASHSEED) by default, so the same string gets a different hash in every new
    process. blake2b has no such salt, so the same snippet always hashes identically
    regardless of which process, machine, or run computed it - required for any
    duplicate index that persists across separate CLI invocations.

    Args:
        snippet: Code snippet to hash

    Returns:
        Deterministic signed integer hash of the snippet
    """
    digest = hashlib.blake2b(snippet.encode("utf-8"), digest_size=_STABLE_HASH_DIGEST_SIZE).digest()
    return int.from_bytes(digest, byteorder="big", signed=True)


def tokenize(code: str) -> list[str]:
    """Tokenize code by stripping comments and normalizing whitespace.

    Args:
        code: Source code string

    Returns:
        List of normalized code lines (non-empty, comments removed, imports filtered)
    """
    lines = []
    in_multiline_import = False

    for line in code.split("\n"):
        line = normalize_line(line)
        if not line:
            continue

        # Update multi-line import state and check if line should be skipped
        in_multiline_import, should_skip = should_skip_import_line(line, in_multiline_import)
        if should_skip:
            continue

        lines.append(line)

    return lines


def normalize_line(line: str) -> str:
    """Normalize a line by removing comments and excess whitespace.

    Args:
        line: Raw source code line

    Returns:
        Normalized line (empty string if line has no content)
    """
    line = _strip_comments(line)
    return " ".join(line.split())


def should_skip_import_line(line: str, in_multiline_import: bool) -> tuple[bool, bool]:
    """Determine if an import line should be skipped.

    Args:
        line: Normalized code line
        in_multiline_import: Whether we're currently inside a multi-line import

    Returns:
        Tuple of (new_in_multiline_import_state, should_skip_line)
    """
    if _is_multiline_import_start(line):
        return True, True

    if in_multiline_import:
        return _handle_multiline_import_continuation(line)

    if _is_import_statement(line):
        return False, True

    return False, False


def _is_multiline_import_start(line: str) -> bool:
    """Check if line starts a multi-line import statement.

    Args:
        line: Normalized code line

    Returns:
        True if line starts a multi-line import (has opening paren but no closing)
    """
    return _is_import_statement(line) and "(" in line and ")" not in line


def _handle_multiline_import_continuation(line: str) -> tuple[bool, bool]:
    """Handle a line that's part of a multi-line import.

    Args:
        line: Normalized code line inside a multi-line import

    Returns:
        Tuple of (still_in_import, should_skip)
    """
    closes_import = ")" in line
    return not closes_import, True


def _strip_comments(line: str) -> str:
    """Remove comments from line (Python # and // style).

    Args:
        line: Source code line

    Returns:
        Line with comments removed
    """
    # Python comments
    if "#" in line:
        line = line[: line.index("#")]

    # JavaScript/TypeScript comments
    if "//" in line:
        line = line[: line.index("//")]

    return line


def _is_import_statement(line: str) -> bool:
    """Check if line is an import statement.

    Args:
        line: Normalized code line

    Returns:
        True if line is an import statement
    """
    return line.startswith(_IMPORT_PREFIXES) or line in _IMPORT_TOKENS


def rolling_hash(lines: list[str], window_size: int) -> list[tuple[int, int, int, str]]:
    """Create rolling hash windows over code lines.

    Args:
        lines: List of normalized code lines
        window_size: Number of lines per window (min_duplicate_lines)

    Returns:
        List of tuples: (hash_value, start_line, end_line, code_snippet)
    """
    if len(lines) < window_size:
        return []

    hashes = []
    for i in range(len(lines) - window_size + 1):
        window = lines[i : i + window_size]
        snippet = "\n".join(window)
        hash_val = stable_hash(snippet)

        # Line numbers are 1-indexed
        start_line = i + 1
        end_line = i + window_size

        hashes.append((hash_val, start_line, end_line, snippet))

    return hashes
