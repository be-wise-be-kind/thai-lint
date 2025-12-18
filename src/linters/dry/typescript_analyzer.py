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

from collections.abc import Generator, Iterable
from pathlib import Path

from src.analyzers.typescript_base import TREE_SITTER_AVAILABLE

from .base_token_analyzer import BaseTokenAnalyzer
from .block_filter import BlockFilterRegistry, create_default_registry
from .cache import CodeBlock
from .config import DRYConfig

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
            if self._should_include_block(content, start_line, end_line)
            and not self._is_single_statement_in_source(content, start_line, end_line)
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
        normalized = self._hasher._normalize_line(line)  # pylint: disable=protected-access
        if not normalized:
            return in_multiline_import, None

        new_state, should_skip = self._hasher._should_skip_import_line(  # pylint: disable=protected-access
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

    def _should_include_block(self, content: str, start_line: int, end_line: int) -> bool:
        """Filter out blocks that overlap with interface/type definitions.

        Args:
            content: File content
            start_line: Block start line
            end_line: Block end line

        Returns:
            False if block overlaps interface definition, True otherwise
        """
        interface_ranges = self._find_interface_ranges(content)
        return not self._overlaps_interface(start_line, end_line, interface_ranges)

    def _is_single_statement_in_source(self, content: str, start_line: int, end_line: int) -> bool:
        """Check if a line range in the original source is a single logical statement.

        Uses tree-sitter AST analysis to detect patterns like:
        - Decorators (@Component(...))
        - Function call arguments
        - Object literal properties
        - Class field definitions
        - Type assertions
        - Chained method calls (single expression)

        Args:
            content: TypeScript source code
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)

        Returns:
            True if this range represents a single logical statement/expression
        """
        if not TREE_SITTER_AVAILABLE:
            return False

        from src.analyzers.typescript_base import TypeScriptBaseAnalyzer

        analyzer = TypeScriptBaseAnalyzer()
        root = analyzer.parse_typescript(content)
        if not root:
            return False

        return self._check_overlapping_nodes(root, start_line, end_line)

    def _check_overlapping_nodes(self, root: Node, start_line: int, end_line: int) -> bool:
        """Check if any AST node overlaps and matches single-statement pattern.

        Args:
            root: Root tree-sitter node
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)

        Returns:
            True if any node matches single-statement pattern
        """
        # Convert to 0-indexed for tree-sitter
        ts_start = start_line - 1
        ts_end = end_line - 1

        for node in self._walk_nodes(root):
            if self._node_overlaps_and_matches(node, ts_start, ts_end):
                return True
        return False

    def _walk_nodes(self, node: Node) -> Generator[Node, None, None]:
        """Generator to walk all nodes in tree.

        Args:
            node: Starting node

        Yields:
            All nodes in tree
        """
        yield node
        for child in node.children:
            yield from self._walk_nodes(child)

    def _node_overlaps_and_matches(self, node: Node, ts_start: int, ts_end: int) -> bool:
        """Check if node overlaps with range and matches single-statement pattern.

        Args:
            node: Tree-sitter node
            ts_start: Starting line (0-indexed)
            ts_end: Ending line (0-indexed)

        Returns:
            True if node overlaps and matches pattern
        """
        node_start = node.start_point[0]
        node_end = node.end_point[0]

        # Check if ranges overlap
        overlaps = not (node_end < ts_start or node_start > ts_end)
        if not overlaps:
            return False

        return self._is_single_statement_pattern(node, ts_start, ts_end)

    def _matches_simple_container_pattern(self, node: Node, contains: bool) -> bool:
        """Check if node is a simple container pattern (decorator, object, etc.).

        Args:
            node: AST node to check
            contains: Whether node contains the range

        Returns:
            True if node matches simple container pattern
        """
        simple_types = (
            "decorator",
            "object",
            "member_expression",
            "as_expression",
            "array_pattern",
        )
        return node.type in simple_types and contains

    def _matches_call_expression_pattern(
        self, node: Node, ts_start: int, ts_end: int, contains: bool
    ) -> bool:
        """Check if node is a call expression pattern.

        Args:
            node: AST node to check
            ts_start: Starting line (0-indexed)
            ts_end: Ending line (0-indexed)
            contains: Whether node contains the range

        Returns:
            True if node matches call expression pattern
        """
        if node.type != "call_expression":
            return False

        # Check if this is a multi-line call containing the range
        node_start = node.start_point[0]
        node_end = node.end_point[0]
        is_multiline = node_start < node_end
        if is_multiline and node_start <= ts_start <= node_end:
            return True

        return contains

    def _matches_declaration_pattern(self, node: Node, contains: bool) -> bool:
        """Check if node is a lexical declaration pattern.

        Args:
            node: AST node to check
            contains: Whether node contains the range

        Returns:
            True if node matches declaration pattern (excluding function bodies)
        """
        if node.type != "lexical_declaration" or not contains:
            return False

        # Only filter if simple value assignment, NOT a function body
        if self._contains_function_body(node):
            return False

        return True

    def _matches_jsx_pattern(self, node: Node, contains: bool) -> bool:
        """Check if node is a JSX element pattern.

        Args:
            node: AST node to check
            contains: Whether node contains the range

        Returns:
            True if node matches JSX pattern
        """
        jsx_types = ("jsx_opening_element", "jsx_self_closing_element")
        return node.type in jsx_types and contains

    def _matches_class_body_pattern(self, node: Node, ts_start: int, ts_end: int) -> bool:
        """Check if node is a class body field definition pattern.

        Args:
            node: AST node to check
            ts_start: Starting line (0-indexed)
            ts_end: Ending line (0-indexed)

        Returns:
            True if node is class body with field definitions
        """
        if node.type != "class_body":
            return False

        return self._is_in_class_field_area(node, ts_start, ts_end)

    def _is_single_statement_pattern(self, node: Node, ts_start: int, ts_end: int) -> bool:
        """Check if an AST node represents a single-statement pattern to filter.

        Delegates to specialized pattern matchers for different AST node categories.

        Args:
            node: AST node that overlaps with the line range
            ts_start: Starting line number (0-indexed)
            ts_end: Ending line number (0-indexed)

        Returns:
            True if this node represents a single logical statement pattern
        """
        node_start = node.start_point[0]
        node_end = node.end_point[0]
        contains = (node_start <= ts_start) and (node_end >= ts_end)

        # Check pattern categories using specialized helpers - use list for any()
        matchers = [
            self._matches_simple_container_pattern(node, contains),
            self._matches_call_expression_pattern(node, ts_start, ts_end, contains),
            self._matches_declaration_pattern(node, contains),
            self._matches_jsx_pattern(node, contains),
            self._matches_class_body_pattern(node, ts_start, ts_end),
        ]
        return any(matchers)

    def _contains_function_body(self, node: Node) -> bool:
        """Check if node contains an arrow function or function expression.

        Args:
            node: Node to check

        Returns:
            True if node contains a function with a body
        """
        for child in node.children:
            if child.type in ("arrow_function", "function", "function_expression"):
                return True
            if self._contains_function_body(child):
                return True
        return False

    def _find_first_method_line(self, class_body: Node) -> int | None:
        """Find line number of first method in class body.

        Args:
            class_body: Class body node

        Returns:
            Line number of first method or None if no methods
        """
        for child in class_body.children:
            if child.type in ("method_definition", "function_declaration"):
                return child.start_point[0]
        return None

    def _is_in_class_field_area(self, class_body: Node, ts_start: int, ts_end: int) -> bool:
        """Check if range is in class field definition area (before methods).

        Args:
            class_body: Class body node
            ts_start: Starting line (0-indexed)
            ts_end: Ending line (0-indexed)

        Returns:
            True if range is in field area
        """
        first_method_line = self._find_first_method_line(class_body)
        class_start = class_body.start_point[0]
        class_end = class_body.end_point[0]

        # No methods: check if range is in class body
        if first_method_line is None:
            return class_start <= ts_start and class_end >= ts_end

        # Has methods: check if range is before first method
        return class_start <= ts_start and ts_end < first_method_line

    def _find_interface_ranges(self, content: str) -> list[tuple[int, int]]:
        """Find line ranges of interface/type definitions.

        Args:
            content: File content

        Returns:
            List of (start_line, end_line) tuples for interface blocks
        """
        ranges: list[tuple[int, int]] = []
        lines = content.split("\n")
        state = {"in_interface": False, "start_line": 0, "brace_count": 0}

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            self._process_line_for_interface(stripped, i, state, ranges)

        return ranges

    def _process_line_for_interface(
        self, stripped: str, line_num: int, state: dict, ranges: list[tuple[int, int]]
    ) -> None:
        """Process single line for interface detection.

        Args:
            stripped: Stripped line content
            line_num: Line number
            state: Tracking state (in_interface, start_line, brace_count)
            ranges: Accumulated interface ranges
        """
        if self._is_interface_start(stripped):
            self._handle_interface_start(stripped, line_num, state, ranges)
            return

        if state["in_interface"]:
            self._handle_interface_continuation(stripped, line_num, state, ranges)

    def _is_interface_start(self, stripped: str) -> bool:
        """Check if line starts interface/type definition."""
        return stripped.startswith(("interface ", "type ")) and "{" in stripped

    def _handle_interface_start(
        self, stripped: str, line_num: int, state: dict, ranges: list[tuple[int, int]]
    ) -> None:
        """Handle start of interface definition."""
        state["in_interface"] = True
        state["start_line"] = line_num
        state["brace_count"] = stripped.count("{") - stripped.count("}")

        if state["brace_count"] == 0:  # Single-line interface
            ranges.append((line_num, line_num))
            state["in_interface"] = False

    def _handle_interface_continuation(
        self, stripped: str, line_num: int, state: dict, ranges: list[tuple[int, int]]
    ) -> None:
        """Handle continuation of interface definition."""
        state["brace_count"] += stripped.count("{") - stripped.count("}")
        if state["brace_count"] == 0:
            ranges.append((state["start_line"], line_num))
            state["in_interface"] = False

    def _overlaps_interface(
        self, start: int, end: int, interface_ranges: list[tuple[int, int]]
    ) -> bool:
        """Check if block overlaps with any interface range.

        Args:
            start: Block start line
            end: Block end line
            interface_ranges: List of interface definition ranges

        Returns:
            True if block overlaps with an interface
        """
        for if_start, if_end in interface_ranges:
            if start <= if_end and end >= if_start:
                return True
        return False
