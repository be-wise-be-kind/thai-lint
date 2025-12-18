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
from collections.abc import Callable
from pathlib import Path
from typing import cast

from .base_token_analyzer import BaseTokenAnalyzer
from .block_filter import BlockFilterRegistry, create_default_registry
from .cache import CodeBlock
from .config import DRYConfig

# AST context checking constants
AST_LOOKBACK_LINES = 10
AST_LOOKFORWARD_LINES = 5

# Type alias for AST nodes that have line number attributes
# All stmt and expr nodes have lineno and end_lineno after parsing
ASTWithLineNumbers = ast.stmt | ast.expr


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
        # Performance optimization: Cache parsed AST to avoid re-parsing for each hash window
        self._cached_ast: ast.Module | None = None
        self._cached_content: str | None = None
        # Performance optimization: Line-to-node index for O(1) lookups instead of O(n) ast.walk()
        self._line_to_nodes: dict[int, list[ast.AST]] | None = None

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
        # Performance optimization: Parse AST once and cache for _is_single_statement_in_source() calls
        self._cached_ast = self._parse_content_safe(content)
        self._cached_content = content

        # Performance optimization: Build line-to-node index for O(1) lookups
        self._line_to_nodes = self._build_line_to_node_index(self._cached_ast)

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
            # Clear cache after analysis to avoid memory leaks
            self._cached_ast = None
            self._cached_content = None
            self._line_to_nodes = None

    def _filter_valid_blocks(
        self,
        windows: list[tuple[int, int, int, str]],
        file_path: Path,
        content: str,
    ) -> list[CodeBlock]:
        """Filter hash windows and create valid CodeBlock instances."""
        blocks = []
        for hash_val, start_line, end_line, snippet in windows:
            block = self._create_block_if_valid(
                file_path, content, hash_val, start_line, end_line, snippet
            )
            if block:
                blocks.append(block)
        return blocks

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
        if self._is_single_statement_in_source(content, start_line, end_line):
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

    def _is_single_statement_in_source(self, content: str, start_line: int, end_line: int) -> bool:
        """Check if a line range in the original source is a single logical statement.

        Performance optimization: Uses cached AST if available (set by analyze() method)
        to avoid re-parsing the entire file for each hash window check.
        """
        # Use cached AST if available and content matches
        tree: ast.Module | None
        if self._cached_ast is not None and content == self._cached_content:
            tree = self._cached_ast
        else:
            # Fallback: parse content (used by tests or standalone calls)
            tree = self._parse_content_safe(content)
            if tree is None:
                return False

        return self._check_overlapping_nodes(tree, start_line, end_line)

    @staticmethod
    def _parse_content_safe(content: str) -> ast.Module | None:
        """Parse content, returning None on syntax error."""
        try:
            return ast.parse(content)
        except SyntaxError:
            return None

    @staticmethod
    def _build_line_to_node_index(tree: ast.Module | None) -> dict[int, list[ast.AST]] | None:
        """Build an index mapping each line number to overlapping AST nodes.

        Performance optimization: This allows O(1) lookups instead of O(n) ast.walk() calls.
        For a file with 5,144 nodes and 673 hash windows, this reduces 3.46M node operations
        to just ~3,365 relevant node checks (99.9% reduction).

        Args:
            tree: Parsed AST tree (None if parsing failed)

        Returns:
            Dictionary mapping line numbers to list of AST nodes overlapping that line,
            or None if tree is None
        """
        if tree is None:
            return None

        line_to_nodes: dict[int, list[ast.AST]] = {}
        for node in ast.walk(tree):
            if PythonDuplicateAnalyzer._node_has_line_info(node):
                PythonDuplicateAnalyzer._add_node_to_index(node, line_to_nodes)

        return line_to_nodes

    @staticmethod
    def _node_has_line_info(node: ast.AST) -> bool:
        """Check if node has valid line number information."""
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            return False
        return node.lineno is not None and node.end_lineno is not None

    @staticmethod
    def _add_node_to_index(node: ast.AST, line_to_nodes: dict[int, list[ast.AST]]) -> None:
        """Add node to all lines it overlaps in the index."""
        for line_num in range(node.lineno, node.end_lineno + 1):  # type: ignore[attr-defined]
            if line_num not in line_to_nodes:
                line_to_nodes[line_num] = []
            line_to_nodes[line_num].append(node)

    def _check_overlapping_nodes(self, tree: ast.Module, start_line: int, end_line: int) -> bool:
        """Check if any AST node overlaps and matches single-statement pattern.

        Performance optimization: Use line-to-node index for O(1) lookups instead of O(n) ast.walk().
        """
        if self._line_to_nodes is not None:
            return self._check_nodes_via_index(start_line, end_line)
        return self._check_nodes_via_walk(tree, start_line, end_line)

    def _check_nodes_via_index(self, start_line: int, end_line: int) -> bool:
        """Check nodes using line-to-node index for O(1) lookups."""
        candidates = self._collect_candidate_nodes_from_index(start_line, end_line)
        return self._any_node_matches_pattern(candidates, start_line, end_line)

    def _collect_candidate_nodes_from_index(self, start_line: int, end_line: int) -> set[ast.AST]:
        """Collect unique nodes that overlap with the line range from index."""
        candidate_nodes: set[ast.AST] = set()
        for line_num in range(start_line, end_line + 1):
            if self._line_to_nodes and line_num in self._line_to_nodes:
                candidate_nodes.update(self._line_to_nodes[line_num])
        return candidate_nodes

    def _any_node_matches_pattern(
        self, nodes: set[ast.AST], start_line: int, end_line: int
    ) -> bool:
        """Check if any node matches single-statement pattern."""
        for node in nodes:
            if self._is_single_statement_pattern(node, start_line, end_line):
                return True
        return False

    def _check_nodes_via_walk(self, tree: ast.Module, start_line: int, end_line: int) -> bool:
        """Check nodes using ast.walk() fallback for tests or standalone calls."""
        for node in ast.walk(tree):
            if self._node_matches_via_walk(node, start_line, end_line):
                return True
        return False

    def _node_matches_via_walk(self, node: ast.AST, start_line: int, end_line: int) -> bool:
        """Check if a single node overlaps and matches pattern."""
        if not self._node_overlaps_range(node, start_line, end_line):
            return False
        return self._is_single_statement_pattern(node, start_line, end_line)

    @staticmethod
    def _node_overlaps_range(node: ast.AST, start_line: int, end_line: int) -> bool:
        """Check if node overlaps with the given line range."""
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            return False
        node_end = node.end_lineno
        node_start = node.lineno
        return not (node_end < start_line or node_start > end_line)

    def _node_overlaps_and_matches(self, node: ast.AST, start_line: int, end_line: int) -> bool:
        """Check if node overlaps with range and matches single-statement pattern."""
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            return False

        overlaps = not (node.end_lineno < start_line or node.lineno > end_line)
        if not overlaps:
            return False

        return self._is_single_statement_pattern(node, start_line, end_line)

    def _is_single_statement_pattern(self, node: ast.AST, start_line: int, end_line: int) -> bool:
        """Check if an AST node represents a single-statement pattern to filter.

        Args:
            node: AST node that overlaps with the line range
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)

        Returns:
            True if this node represents a single logical statement pattern
        """
        contains = self._node_contains_range(node, start_line, end_line)
        if contains is None:
            return False

        return self._dispatch_pattern_check(node, start_line, end_line, contains)

    def _node_contains_range(self, node: ast.AST, start_line: int, end_line: int) -> bool | None:
        """Check if node completely contains the range. Returns None if invalid."""
        if not self._has_valid_line_numbers(node):
            return None
        # Type narrowing: _has_valid_line_numbers ensures node has line numbers
        # Safe to cast after validation check above
        typed_node = cast(ASTWithLineNumbers, node)
        # Use type: ignore to suppress MyPy's inability to understand runtime validation
        return typed_node.lineno <= start_line and typed_node.end_lineno >= end_line  # type: ignore[operator]

    @staticmethod
    def _has_valid_line_numbers(node: ast.AST) -> bool:
        """Check if node has valid line number attributes."""
        if not (hasattr(node, "lineno") and hasattr(node, "end_lineno")):
            return False
        return node.lineno is not None and node.end_lineno is not None

    def _dispatch_pattern_check(
        self, node: ast.AST, start_line: int, end_line: int, contains: bool
    ) -> bool:
        """Dispatch to node-type-specific pattern checkers."""
        # Simple containment check for Expr nodes
        if isinstance(node, ast.Expr):
            return contains

        # Delegate to specialized checkers
        return self._check_specific_pattern(node, start_line, end_line, contains)

    def _check_specific_pattern(
        self, node: ast.AST, start_line: int, end_line: int, contains: bool
    ) -> bool:
        """Check specific node types with their pattern rules."""
        if isinstance(node, ast.ClassDef):
            return self._check_class_def_pattern(node, start_line, end_line)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return self._check_function_def_pattern(node, start_line, end_line)
        if isinstance(node, ast.Call):
            return self._check_call_pattern(node, start_line, end_line, contains)
        if isinstance(node, ast.Assign):
            return self._check_assign_pattern(node, start_line, end_line, contains)
        return False

    def _check_class_def_pattern(self, node: ast.ClassDef, start_line: int, end_line: int) -> bool:
        """Check if range is in class field definitions (not method bodies)."""
        first_method_line = self._find_first_method_line(node)
        class_start = self._get_class_start_with_decorators(node)
        return self._is_in_class_fields_area(
            class_start, start_line, end_line, first_method_line, node.end_lineno
        )

    @staticmethod
    def _find_first_method_line(node: ast.ClassDef) -> int | None:
        """Find line number of first method in class."""
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return item.lineno
        return None

    @staticmethod
    def _get_class_start_with_decorators(node: ast.ClassDef) -> int:
        """Get class start line, including decorators if present."""
        if node.decorator_list:
            return min(d.lineno for d in node.decorator_list)
        return node.lineno

    @staticmethod
    def _is_in_class_fields_area(
        class_start: int,
        start_line: int,
        end_line: int,
        first_method_line: int | None,
        class_end_line: int | None,
    ) -> bool:
        """Check if range is in class fields area (before methods)."""
        if first_method_line is not None:
            return class_start <= start_line and end_line < first_method_line
        if class_end_line is not None:
            return class_start <= start_line and class_end_line >= end_line
        return False

    def _check_function_def_pattern(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, start_line: int, end_line: int
    ) -> bool:
        """Check if range is in function decorator pattern."""
        if not node.decorator_list:
            return False

        first_decorator_line = min(d.lineno for d in node.decorator_list)
        first_body_line = self._get_function_body_start(node)

        if first_body_line is None:
            return False

        return start_line >= first_decorator_line and end_line < first_body_line

    @staticmethod
    def _get_function_body_start(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int | None:
        """Get the line number where function body starts."""
        if not node.body or not hasattr(node.body[0], "lineno"):
            return None
        return node.body[0].lineno

    def _check_call_pattern(
        self, node: ast.Call, start_line: int, end_line: int, contains: bool
    ) -> bool:
        """Check if range is part of a function/constructor call."""
        return self._check_multiline_or_contained(node, start_line, end_line, contains)

    def _check_assign_pattern(
        self, node: ast.Assign, start_line: int, end_line: int, contains: bool
    ) -> bool:
        """Check if range is part of a multi-line assignment."""
        return self._check_multiline_or_contained(node, start_line, end_line, contains)

    def _check_multiline_or_contained(
        self, node: ast.AST, start_line: int, end_line: int, contains: bool
    ) -> bool:
        """Check if node is multiline containing start, or single-line containing range."""
        if not self._has_valid_line_numbers(node):
            return False

        # Type narrowing: _has_valid_line_numbers ensures node has line numbers
        # Safe to cast after validation check above
        typed_node = cast(ASTWithLineNumbers, node)
        # Use type: ignore to suppress MyPy's inability to understand runtime validation
        is_multiline = typed_node.lineno < typed_node.end_lineno  # type: ignore[operator]
        if is_multiline:
            return typed_node.lineno <= start_line <= typed_node.end_lineno  # type: ignore[operator]
        return contains

    def _is_standalone_single_statement(
        self, lines: list[str], start_line: int, end_line: int
    ) -> bool:
        """Check if the exact range parses as a single statement on its own."""
        source_lines = lines[start_line - 1 : end_line]
        source_snippet = "\n".join(source_lines)

        try:
            tree = ast.parse(source_snippet)
            return len(tree.body) == 1
        except SyntaxError:
            return False

    def _check_ast_context(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        lines: list[str],
        start_line: int,
        end_line: int,
        lookback: int,
        lookforward: int,
        predicate: Callable[[ast.Module, int], bool],
    ) -> bool:
        """Generic helper for AST-based context checking.

        Args:
            lines: Source file lines
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)
            lookback: Number of lines to look backward
            lookforward: Number of lines to look forward
            predicate: Function that takes AST tree and returns bool

        Returns:
            True if predicate returns True for the parsed context
        """
        lookback_start = max(0, start_line - lookback)
        lookforward_end = min(len(lines), end_line + lookforward)

        context_lines = lines[lookback_start:lookforward_end]
        context = "\n".join(context_lines)

        try:
            tree = ast.parse(context)
            return predicate(tree, lookback_start)
        except SyntaxError:
            pass

        return False

    def _is_part_of_decorator(self, lines: list[str], start_line: int, end_line: int) -> bool:
        """Check if lines are part of a decorator + function definition.

        A decorator pattern is @something(...) followed by def/class.
        """

        def has_decorators(tree: ast.Module, _lookback_start: int) -> bool:
            """Check if any function or class in the tree has decorators."""
            for stmt in tree.body:
                if isinstance(stmt, (ast.FunctionDef, ast.ClassDef)) and stmt.decorator_list:
                    return True
            return False

        return self._check_ast_context(lines, start_line, end_line, 10, 10, has_decorators)

    def _is_part_of_function_call(self, lines: list[str], start_line: int, end_line: int) -> bool:
        """Check if lines are arguments inside a function/constructor call.

        Detects patterns like:
            obj = Constructor(
                arg1=value1,
                arg2=value2,
            )
        """

        def is_single_non_function_statement(tree: ast.Module, _lookback_start: int) -> bool:
            """Check if context has exactly one statement that's not a function/class def."""
            return len(tree.body) == 1 and not isinstance(
                tree.body[0], (ast.FunctionDef, ast.ClassDef)
            )

        return self._check_ast_context(
            lines, start_line, end_line, 10, 10, is_single_non_function_statement
        )

    def _is_part_of_class_body(self, lines: list[str], start_line: int, end_line: int) -> bool:
        """Check if lines are field definitions inside a class body.

        Detects patterns like:
            class Foo:
                field1: Type1
                field2: Type2
        """

        def is_within_class_body(tree: ast.Module, lookback_start: int) -> bool:
            """Check if flagged range falls within a class body."""
            class_defs = (s for s in tree.body if isinstance(s, ast.ClassDef))
            for stmt in class_defs:
                # Adjust line numbers: stmt.lineno is relative to context
                # We need to convert back to original file line numbers
                class_start_in_context = stmt.lineno
                class_end_in_context = stmt.end_lineno if stmt.end_lineno else stmt.lineno

                # Convert to original file line numbers (1-indexed)
                class_start_original = lookback_start + class_start_in_context
                class_end_original = lookback_start + class_end_in_context

                # Check if the flagged range overlaps with class body
                if start_line >= class_start_original and end_line <= class_end_original:
                    return True
            return False

        return self._check_ast_context(
            lines,
            start_line,
            end_line,
            AST_LOOKBACK_LINES,
            AST_LOOKFORWARD_LINES,
            is_within_class_body,
        )
