"""
Purpose: TypeScript/JavaScript source code tokenization and duplicate block analysis

Scope: TypeScript and JavaScript file analysis for duplicate detection

Overview: Analyzes TypeScript and JavaScript source files to extract code blocks for duplicate
    detection. Inherits from BaseTokenAnalyzer for common token-based hashing and rolling hash
    window logic. Adds TypeScript-specific filtering to exclude JSDoc comments, single statements
    (decorators, function calls, object literals, class fields), and interface/type definitions.
    Uses tree-sitter for AST-based filtering to achieve same sophistication as Python analyzer.

Dependencies: BaseTokenAnalyzer, CodeBlock, DRYConfig, pathlib.Path, tree-sitter

Exports: TypeScriptDuplicateAnalyzer class

Interfaces: TypeScriptDuplicateAnalyzer.analyze(file_path: Path, content: str, config: DRYConfig)
    -> list[CodeBlock]

Implementation: Inherits analyze() workflow from BaseTokenAnalyzer, adds JSDoc comment extraction,
    single statement detection using tree-sitter AST patterns, and interface filtering logic

Suppressions:
    - type:ignore[assignment,misc]: Tree-sitter Node type alias (optional dependency fallback)
    - invalid-name: Node type alias follows tree-sitter naming convention
    - srp.violation: Complex tree-sitter AST analysis algorithm. See SRP Exception below.

SRP Exception: TypeScriptDuplicateAnalyzer has 20 methods and 324 lines (exceeds max 8 methods/200 lines)
    Justification: Complex tree-sitter AST analysis algorithm for duplicate code detection with sophisticated
    false positive filtering. Mirrors Python analyzer structure. Methods form tightly coupled algorithm
    pipeline: JSDoc extraction, tokenization with line tracking, single-statement pattern detection across
    10+ AST node types (decorators, call_expression, object, class_body, member_expression, as_expression,
    jsx elements, array_pattern), and context-aware filtering. Similar to parser or compiler pass architecture
    where algorithmic cohesion is critical. Splitting would fragment the algorithm logic and make maintenance
    harder by separating interdependent tree-sitter AST analysis steps. All methods contribute to single
    responsibility: accurately detecting duplicate TypeScript/JavaScript code while minimizing false positives.
"""

from collections.abc import Iterable
from pathlib import Path

from src.analyzers.typescript_base import TREE_SITTER_AVAILABLE

from . import token_hasher
from .base_token_analyzer import BaseTokenAnalyzer
from .block_filter import BlockFilterRegistry, create_default_registry
from .cache import CodeBlock
from .config import DRYConfig
from .typescript_statement_detector import is_single_statement, should_include_block

if TREE_SITTER_AVAILABLE:
    from tree_sitter import Node
else:
    Node = None  # type: ignore[assignment,misc]  # pylint: disable=invalid-name


class TypeScriptDuplicateAnalyzer(BaseTokenAnalyzer):  # thailint: ignore[srp.violation]
    """Analyzes TypeScript/JavaScript code for duplicate blocks.

    SRP suppression: Complex tree-sitter AST analysis algorithm requires 20 methods to implement
    sophisticated duplicate detection with false positive filtering. See file header for justification.
    """

    def __init__(self, filter_registry: BlockFilterRegistry | None = None):
        """Initialize analyzer with optional custom filter registry.

        Args:
            filter_registry: Custom filter registry (uses defaults if None)
        """
        super().__init__()
        self._filter_registry = filter_registry or create_default_registry()

    def analyze(self, file_path: Path, content: str, config: DRYConfig) -> list[CodeBlock]:
        """Analyze TypeScript/JavaScript file for duplicate code blocks.

        Filters out JSDoc comments, single statements, and interface definitions.

        Args:
            file_path: Path to source file
            content: File content
            config: DRY configuration

        Returns:
            List of CodeBlock instances with hash values
        """
        # Get JSDoc comment line ranges
        jsdoc_ranges = self._get_jsdoc_ranges_from_content(content)

        # Tokenize with line number tracking, skipping JSDoc lines
        lines_with_numbers = self._tokenize_with_line_numbers(content, jsdoc_ranges)

        # Generate rolling hash windows
        windows = self._rolling_hash_with_tracking(lines_with_numbers, config.min_duplicate_lines)

        # Filter out interface/type definitions and single statement patterns
        valid_windows = (
            (hash_val, start_line, end_line, snippet)
            for hash_val, start_line, end_line, snippet in windows
            if should_include_block(content, start_line, end_line)
            and not is_single_statement(content, start_line, end_line)
        )
        return self._build_blocks(valid_windows, file_path, content)

    def _build_blocks(
        self,
        windows: Iterable[tuple[int, int, int, str]],
        file_path: Path,
        content: str,
    ) -> list[CodeBlock]:
        """Build CodeBlock objects from valid windows, applying filters.

        Args:
            windows: Iterable of (hash_val, start_line, end_line, snippet) tuples
            file_path: Path to source file
            content: File content

        Returns:
            List of CodeBlock instances that pass all filters
        """
        blocks = []
        for hash_val, start_line, end_line, snippet in windows:
            block = CodeBlock(
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                snippet=snippet,
                hash_value=hash_val,
            )
            if not self._filter_registry.should_filter_block(block, content):
                blocks.append(block)
        return blocks

    def _get_jsdoc_ranges_from_content(self, content: str) -> set[int]:
        """Extract line numbers that are part of JSDoc comments.

        Args:
            content: TypeScript/JavaScript source code

        Returns:
            Set of line numbers (1-indexed) that are part of JSDoc comments
        """
        if not TREE_SITTER_AVAILABLE:
            return set()

        from src.analyzers.typescript_base import TypeScriptBaseAnalyzer

        analyzer = TypeScriptBaseAnalyzer()
        root = analyzer.parse_typescript(content)
        if not root:
            return set()

        jsdoc_lines: set[int] = set()
        self._collect_jsdoc_lines_recursive(root, jsdoc_lines)
        return jsdoc_lines

    def _is_jsdoc_comment(self, node: Node) -> bool:
        """Check if node is a JSDoc comment.

        Args:
            node: Tree-sitter node to check

        Returns:
            True if node is JSDoc comment (/** ... */)
        """
        if node.type != "comment":
            return False

        text = node.text.decode() if node.text else ""
        return text.startswith("/**")

    def _add_comment_lines_to_set(self, node: Node, jsdoc_lines: set[int]) -> None:
        """Add comment node's line range to set.

        Args:
            node: Comment node
            jsdoc_lines: Set to add line numbers to
        """
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        for line_num in range(start_line, end_line + 1):
            jsdoc_lines.add(line_num)

    def _collect_jsdoc_lines_recursive(self, node: Node, jsdoc_lines: set[int]) -> None:
        """Recursively collect JSDoc comment line ranges.

        Args:
            node: Tree-sitter node to examine
            jsdoc_lines: Set to accumulate line numbers
        """
        if self._is_jsdoc_comment(node):
            self._add_comment_lines_to_set(node, jsdoc_lines)

        for child in node.children:
            self._collect_jsdoc_lines_recursive(child, jsdoc_lines)

    def _tokenize_with_line_numbers(
        self, content: str, jsdoc_lines: set[int]
    ) -> list[tuple[int, str]]:
        """Tokenize code while tracking original line numbers and skipping JSDoc.

        Args:
            content: Source code
            jsdoc_lines: Set of line numbers that are JSDoc comments

        Returns:
            List of (original_line_number, normalized_code) tuples
        """
        lines_with_numbers = []
        in_multiline_import = False

        # Skip JSDoc comment lines
        non_jsdoc_lines = (
            (line_num, line)
            for line_num, line in enumerate(content.split("\n"), start=1)
            if line_num not in jsdoc_lines
        )
        for line_num, line in non_jsdoc_lines:
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
