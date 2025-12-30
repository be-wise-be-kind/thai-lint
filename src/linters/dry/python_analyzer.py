"""
Purpose: Python source code tokenization and duplicate block analysis

Scope: Python-specific code analysis for duplicate detection

Overview: Analyzes Python source files to extract code blocks for duplicate detection. Inherits
    from BaseTokenAnalyzer to reuse common token-based hashing and rolling hash window logic.
    Filters out docstrings at the tokenization level to prevent false positive duplication
    detection on documentation strings.

Dependencies: BaseTokenAnalyzer, CodeBlock, DRYConfig, pathlib.Path, ast, token_hasher module

Exports: PythonDuplicateAnalyzer class

Interfaces: PythonDuplicateAnalyzer.analyze(file_path: Path, content: str, config: DRYConfig)
    -> list[CodeBlock]

Implementation: Uses custom tokenizer that filters docstrings before hashing

Suppressions:
    - too-many-arguments,too-many-positional-arguments: Line processing with related params
    - type:ignore[arg-type]: ast.get_docstring returns str|None, typing limitation
    - srp.violation: Complex AST analysis algorithm for duplicate detection. See SRP Exception below.
    - nesting.excessive-depth: analyze method uses nested loops for docstring extraction.

SRP Exception: PythonDuplicateAnalyzer has 32 methods and 358 lines (exceeds max 8 methods/200 lines)
    Justification: Complex AST analysis algorithm for duplicate code detection with sophisticated
    false positive filtering. Methods form tightly coupled algorithm pipeline: docstring extraction,
    tokenization with line tracking, single-statement pattern detection across 5+ AST node types
    (ClassDef, FunctionDef, Call, Assign, Expr), and context-aware filtering (decorators, function
    calls, class bodies). Similar to parser or compiler pass architecture where algorithmic
    cohesion is critical. Splitting would fragment the algorithm logic and make maintenance
    harder by separating interdependent AST analysis steps. All methods contribute to single
    responsibility: accurately detecting duplicate Python code while minimizing false positives.
"""

import ast
from pathlib import Path

from . import token_hasher
from .base_token_analyzer import BaseTokenAnalyzer
from .block_filter import BlockFilterRegistry, create_default_registry
from .cache import CodeBlock
from .config import DRYConfig
from .single_statement_detector import SingleStatementDetector


class PythonDuplicateAnalyzer(BaseTokenAnalyzer):  # thailint: ignore[srp.violation]
    """Analyzes Python code for duplicate blocks, excluding docstrings.

    SRP suppression: Complex AST analysis algorithm requires 32 methods to implement
    sophisticated duplicate detection with false positive filtering. See file header for justification.
    """

    def __init__(self, filter_registry: BlockFilterRegistry | None = None):
        """Initialize analyzer with optional custom filter registry.

        Args:
            filter_registry: Custom filter registry (uses defaults if None)
        """
        super().__init__()
        self._filter_registry = filter_registry or create_default_registry()
        # Single-statement detector is created per-analysis with cached AST data
        self._statement_detector: SingleStatementDetector | None = None

    def analyze(  # thailint: ignore[nesting.excessive-depth]
        self, file_path: Path, content: str, config: DRYConfig
    ) -> list[CodeBlock]:
        """Analyze Python file for duplicate code blocks, excluding docstrings.

        Args:
            file_path: Path to source file
            content: File content
            config: DRY configuration

        Returns:
            List of CodeBlock instances with hash values
        """
        # Performance optimization: Parse AST once and create detector with cached data
        cached_ast = self._parse_content_safe(content)
        line_to_nodes = SingleStatementDetector.build_line_to_node_index(cached_ast)
        self._statement_detector = SingleStatementDetector(cached_ast, content, line_to_nodes)

        try:
            # Get docstring line ranges
            docstring_ranges = self._get_docstring_ranges_from_content(content)

            # Tokenize with line number tracking
            lines_with_numbers = self._tokenize_with_line_numbers(content, docstring_ranges)

            # Generate rolling hash windows
            windows = self._rolling_hash_with_tracking(
                lines_with_numbers, config.min_duplicate_lines
            )

            return self._filter_valid_blocks(windows, file_path, content)
        finally:
            # Clear detector after analysis to avoid memory leaks
            self._statement_detector = None

    def _filter_valid_blocks(
        self,
        windows: list[tuple[int, int, int, str]],
        file_path: Path,
        content: str,
    ) -> list[CodeBlock]:
        """Filter hash windows and create valid CodeBlock instances."""
        return [
            block
            for hash_val, start_line, end_line, snippet in windows
            if (
                block := self._create_block_if_valid(
                    file_path, content, hash_val, start_line, end_line, snippet
                )
            )
        ]

    def _create_block_if_valid(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        file_path: Path,
        content: str,
        hash_val: int,
        start_line: int,
        end_line: int,
        snippet: str,
    ) -> CodeBlock | None:
        """Create CodeBlock if it passes all validation checks."""
        if self._statement_detector and self._statement_detector.is_single_statement(
            content, start_line, end_line
        ):
            return None

        block = CodeBlock(
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            snippet=snippet,
            hash_value=hash_val,
        )

        if self._filter_registry.should_filter_block(block, content):
            return None

        return block

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
        in_multiline_import = False

        non_docstring_lines = (
            (line_num, line)
            for line_num, line in enumerate(content.split("\n"), start=1)
            if line_num not in docstring_lines
        )
        for line_num, line in non_docstring_lines:
            in_multiline_import, normalized = self._normalize_and_filter_line(
                line, in_multiline_import
            )
            if normalized is not None:
                lines_with_numbers.append((line_num, normalized))

        return lines_with_numbers

    def _normalize_and_filter_line(
        self, line: str, in_multiline_import: bool
    ) -> tuple[bool, str | None]:
        """Normalize line and check if it should be included.

        Args:
            line: Raw source line
            in_multiline_import: Current multi-line import state

        Returns:
            Tuple of (new_import_state, normalized_line or None if should skip)
        """
        normalized = token_hasher.normalize_line(line)
        if not normalized:
            return in_multiline_import, None

        new_state, should_skip = token_hasher.should_skip_import_line(
            normalized, in_multiline_import
        )
        if should_skip:
            return new_state, None
        return new_state, normalized

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

    @staticmethod
    def _parse_content_safe(content: str) -> ast.Module | None:
        """Parse content, returning None on syntax error."""
        try:
            return ast.parse(content)
        except SyntaxError:
            return None
