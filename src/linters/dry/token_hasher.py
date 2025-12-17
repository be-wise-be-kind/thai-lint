"""
Purpose: Tokenization and rolling hash generation for code deduplication

Scope: Code normalization, comment stripping, and hash window generation

Overview: Implements token-based hashing algorithm (Rabin-Karp) for detecting code duplicates.
    Normalizes source code by stripping comments and whitespace, then generates rolling hash
    windows over consecutive lines. Each window represents a potential duplicate code block.
    Uses Python's built-in hash function for simplicity and performance. Supports both Python
    and JavaScript/TypeScript comment styles.

Dependencies: Python built-in hash function

Exports: TokenHasher class

Interfaces: TokenHasher.tokenize(code: str) -> list[str],
    TokenHasher.rolling_hash(lines: list[str], window_size: int) -> list[tuple]

Implementation: Token-based normalization with rolling window algorithm, language-agnostic approach
"""


class TokenHasher:  # thailint: ignore[srp] - Methods support single responsibility of code tokenization
    """Tokenize code and create rolling hashes for duplicate detection."""

    def __init__(self) -> None:
        """Initialize the token hasher."""
        pass  # Stateless hasher for code tokenization

    def tokenize(self, code: str) -> list[str]:
        """Tokenize code by stripping comments and normalizing whitespace.

        Args:
            code: Source code string

        Returns:
            List of normalized code lines (non-empty, comments removed, imports filtered)
        """
        lines = []
        in_multiline_import = False

        for line in code.split("\n"):
            line = self._normalize_line(line)
            if not line:
                continue

            # Update multi-line import state and check if line should be skipped
            in_multiline_import, should_skip = self._should_skip_import_line(
                line, in_multiline_import
            )
            if should_skip:
                continue

            lines.append(line)

        return lines

    def _normalize_line(self, line: str) -> str:
        """Normalize a line by removing comments and excess whitespace.

        Args:
            line: Raw source code line

        Returns:
            Normalized line (empty string if line has no content)
        """
        line = self._strip_comments(line)
        return " ".join(line.split())

    def _should_skip_import_line(self, line: str, in_multiline_import: bool) -> tuple[bool, bool]:
        """Determine if an import line should be skipped.

        Args:
            line: Normalized code line
            in_multiline_import: Whether we're currently inside a multi-line import

        Returns:
            Tuple of (new_in_multiline_import_state, should_skip_line)
        """
        if self._is_multiline_import_start(line):
            return True, True

        if in_multiline_import:
            return self._handle_multiline_import_continuation(line)

        if self._is_import_statement(line):
            return False, True

        return False, False

    def _is_multiline_import_start(self, line: str) -> bool:
        """Check if line starts a multi-line import statement.

        Args:
            line: Normalized code line

        Returns:
            True if line starts a multi-line import (has opening paren but no closing)
        """
        return self._is_import_statement(line) and "(" in line and ")" not in line

    def _handle_multiline_import_continuation(self, line: str) -> tuple[bool, bool]:
        """Handle a line that's part of a multi-line import.

        Args:
            line: Normalized code line inside a multi-line import

        Returns:
            Tuple of (still_in_import, should_skip)
        """
        closes_import = ")" in line
        return not closes_import, True

    def _strip_comments(self, line: str) -> str:
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

    def _is_import_statement(self, line: str) -> bool:
        """Check if line is an import statement.

        Args:
            line: Normalized code line

        Returns:
            True if line is an import statement
        """
        # Check all import/export patterns
        import_prefixes = ("import ", "from ", "export ")
        import_tokens = ("{", "}", "} from")

        return line.startswith(import_prefixes) or line in import_tokens

    def rolling_hash(self, lines: list[str], window_size: int) -> list[tuple[int, int, int, str]]:
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
            hash_val = hash(snippet)

            # Line numbers are 1-indexed
            start_line = i + 1
            end_line = i + window_size

            hashes.append((hash_val, start_line, end_line, snippet))

        return hashes
