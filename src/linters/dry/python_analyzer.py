"""
Purpose: Python source code tokenization and duplicate block analysis

Scope: Python-specific code analysis for duplicate detection

Overview: Analyzes Python source files to extract code blocks for duplicate detection. Inherits
    from BaseTokenAnalyzer to reuse common token-based hashing and rolling hash window logic.
    Filters out docstrings at the tokenization level to prevent false positive duplication
    detection on documentation strings.

Dependencies: BaseTokenAnalyzer, CodeBlock, DRYConfig, pathlib.Path, ast, TokenHasher

Exports: PythonDuplicateAnalyzer class

Interfaces: PythonDuplicateAnalyzer.analyze(file_path: Path, content: str, config: DRYConfig)
    -> list[CodeBlock]

Implementation: Uses custom tokenizer that filters docstrings before hashing
"""

import ast
from pathlib import Path

from .base_token_analyzer import BaseTokenAnalyzer
from .cache import CodeBlock
from .config import DRYConfig


class PythonDuplicateAnalyzer(BaseTokenAnalyzer):
    """Analyzes Python code for duplicate blocks, excluding docstrings."""

    def analyze(self, file_path: Path, content: str, config: DRYConfig) -> list[CodeBlock]:
        """Analyze Python file for duplicate code blocks, excluding docstrings.

        Args:
            file_path: Path to source file
            content: File content
            config: DRY configuration

        Returns:
            List of CodeBlock instances with hash values
        """
        # Get docstring line ranges
        docstring_ranges = self._get_docstring_ranges_from_content(content)

        # Tokenize with line number tracking
        lines_with_numbers = self._tokenize_with_line_numbers(content, docstring_ranges)

        # Generate rolling hash windows
        windows = self._rolling_hash_with_tracking(lines_with_numbers, config.min_duplicate_lines)

        blocks = []
        for hash_val, start_line, end_line, snippet in windows:
            # Skip blocks that are single logical statements
            # Check the original source code, not the normalized snippet
            if self._is_single_statement_in_source(content, start_line, end_line):
                continue

            block = CodeBlock(
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                snippet=snippet,
                hash_value=hash_val,
            )
            blocks.append(block)

        return blocks

    def _get_docstring_ranges_from_content(self, content: str) -> set[int]:
        """Extract line numbers that are part of docstrings.

        Args:
            content: Python source code

        Returns:
            Set of line numbers (1-indexed) that are part of docstrings
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return set()

        docstring_lines: set[int] = set()
        for node in ast.walk(tree):
            self._extract_docstring_lines(node, docstring_lines)

        return docstring_lines

    def _extract_docstring_lines(self, node: ast.AST, docstring_lines: set[int]) -> None:
        """Extract docstring line numbers from a node."""
        docstring = self._get_docstring_safe(node)
        if not docstring:
            return

        if not hasattr(node, "body") or not node.body:
            return

        first_stmt = node.body[0]
        if self._is_docstring_node(first_stmt):
            self._add_line_range(first_stmt, docstring_lines)

    @staticmethod
    def _get_docstring_safe(node: ast.AST) -> str | None:
        """Safely get docstring from node, returning None on error."""
        try:
            return ast.get_docstring(node, clean=False)  # type: ignore[arg-type]
        except TypeError:
            return None

    @staticmethod
    def _is_docstring_node(node: ast.stmt) -> bool:
        """Check if a statement node is a docstring."""
        return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)

    @staticmethod
    def _add_line_range(node: ast.stmt, line_set: set[int]) -> None:
        """Add all line numbers from node's line range to the set."""
        if node.lineno and node.end_lineno:
            for line_num in range(node.lineno, node.end_lineno + 1):
                line_set.add(line_num)

    def _tokenize_with_line_numbers(
        self, content: str, docstring_lines: set[int]
    ) -> list[tuple[int, str]]:
        """Tokenize code while tracking original line numbers and skipping docstrings.

        Args:
            content: Source code
            docstring_lines: Set of line numbers that are docstrings

        Returns:
            List of (original_line_number, normalized_code) tuples
        """
        lines_with_numbers = []

        for line_num, line in enumerate(content.split("\n"), start=1):
            # Skip docstring lines
            if line_num in docstring_lines:
                continue

            # Use hasher's existing tokenization logic
            line = self._hasher._strip_comments(line)
            line = " ".join(line.split())

            if not line:
                continue

            if self._hasher._is_import_statement(line):
                continue

            lines_with_numbers.append((line_num, line))

        return lines_with_numbers

    def _rolling_hash_with_tracking(
        self, lines_with_numbers: list[tuple[int, str]], window_size: int
    ) -> list[tuple[int, int, int, str]]:
        """Create rolling hash windows while preserving original line numbers.

        Args:
            lines_with_numbers: List of (line_number, code) tuples
            window_size: Number of lines per window

        Returns:
            List of (hash_value, start_line, end_line, snippet) tuples
        """
        if len(lines_with_numbers) < window_size:
            return []

        hashes = []
        for i in range(len(lines_with_numbers) - window_size + 1):
            window = lines_with_numbers[i : i + window_size]

            # Extract just the code for hashing
            code_lines = [code for _, code in window]
            snippet = "\n".join(code_lines)
            hash_val = hash(snippet)

            # Get original line numbers
            start_line = window[0][0]
            end_line = window[-1][0]

            hashes.append((hash_val, start_line, end_line, snippet))

        return hashes

    def _is_single_statement_in_source(self, content: str, start_line: int, end_line: int) -> bool:
        """Check if a line range in the original source is a single logical statement.

        A decorator by itself is not a complete statement - it needs the function it decorates.
        We need to look ahead to include the decorated function/class to parse correctly.

        Args:
            content: Original source code
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)

        Returns:
            True if the line range contains a single statement (shouldn't be flagged)
        """
        # Extract the original source lines
        lines = content.split("\n")
        source_lines = lines[start_line - 1 : end_line]
        source_snippet = "\n".join(source_lines)

        # First, try to parse the exact range
        try:
            tree = ast.parse(source_snippet)
            # If it parses and has exactly 1 statement, filter it
            return len(tree.body) == 1
        except SyntaxError:
            pass

        # If it doesn't parse, it might be a decorator without the function
        # Try to extend the range to include the next few lines (likely the function)
        extended_lines = lines[start_line - 1 : min(end_line + 10, len(lines))]
        extended_snippet = "\n".join(extended_lines)

        try:
            tree = ast.parse(extended_snippet)
            # If the extended version parses and has exactly 1 statement,
            # then our original range is part of a single statement (decorator + function)
            return len(tree.body) == 1
        except SyntaxError:
            # Can't parse even with extension - let it through for detection
            return False
