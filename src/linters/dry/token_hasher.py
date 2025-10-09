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


class TokenHasher:
    """Tokenize code and create rolling hashes for duplicate detection."""

    def tokenize(self, code: str) -> list[str]:
        """Tokenize code by stripping comments and normalizing whitespace.

        Args:
            code: Source code string

        Returns:
            List of normalized code lines (non-empty, comments removed, imports filtered)
        """
        lines = []

        for line in code.split("\n"):
            # Remove comments (language-specific logic can be added)
            line = self._strip_comments(line)

            # Normalize whitespace (collapse to single space)
            line = " ".join(line.split())

            # Skip empty lines
            if not line:
                continue

            # Skip import statements (common false positive)
            if self._is_import_statement(line):
                continue

            lines.append(line)

        return lines

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
