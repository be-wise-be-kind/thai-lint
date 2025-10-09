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
from .block_filter import BlockFilterRegistry, create_default_registry
from .cache import CodeBlock
from .config import DRYConfig


class PythonDuplicateAnalyzer(BaseTokenAnalyzer):
    """Analyzes Python code for duplicate blocks, excluding docstrings."""

    def __init__(self, filter_registry: BlockFilterRegistry | None = None):
        """Initialize analyzer with optional custom filter registry.

        Args:
            filter_registry: Custom filter registry (uses defaults if None)
        """
        super().__init__()
        self._filter_registry = filter_registry or create_default_registry()

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

            # Apply extensible filters (keyword arguments, imports, etc.)
            if self._filter_registry.should_filter_block(block, content):
                continue

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

        Uses AST to find nodes that overlap with the line range and determines if they
        represent single logical statements that shouldn't be flagged as duplicates.

        Args:
            content: Original source code
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)

        Returns:
            True if the line range is part of a single statement (shouldn't be flagged)
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return False

        # Walk the AST to find nodes that overlap with this line range
        for node in ast.walk(tree):
            if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
                continue

            # Check if this node overlaps with the line range
            overlaps = not (node.end_lineno < start_line or node.lineno > end_line)
            if overlaps:
                # Check if this is a single-statement pattern we should filter
                if self._is_single_statement_pattern(node, start_line, end_line):
                    return True

        return False

    def _is_single_statement_pattern(self, node: ast.AST, start_line: int, end_line: int) -> bool:
        """Check if an AST node represents a single-statement pattern to filter.

        Args:
            node: AST node that overlaps with the line range
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (1-indexed)

        Returns:
            True if this node represents a single logical statement pattern
        """
        # Check if node completely contains the range
        # (This ensures the entire flagged range is part of one statement)
        contains = node.lineno <= start_line and node.end_lineno >= end_line

        # ClassDef: Class field definitions (but NOT method bodies)
        if isinstance(node, ast.ClassDef):
            # Only filter if the flagged range is in the class header/fields area,
            # not in method bodies
            # Find where the first method starts
            first_method_line = None
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    first_method_line = item.lineno
                    break

            # For classes with decorators, extend the range to include decorators
            class_start = node.lineno
            if node.decorator_list:
                class_start = min(d.lineno for d in node.decorator_list)

            # Only filter if the range is before the first method (i.e., in the fields area)
            if first_method_line is not None:
                # There are methods - only filter if range is before them
                if class_start <= start_line and end_line < first_method_line:
                    return True
            else:
                # No methods - filter if in class range (all fields)
                extended_contains = class_start <= start_line and node.end_lineno >= end_line
                if extended_contains:
                    return True

        # FunctionDef/AsyncFunctionDef: Decorator patterns
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # If decorators exist and the range overlaps with decorators
            if node.decorator_list:
                # Get the first decorator's line
                first_decorator_line = min(d.lineno for d in node.decorator_list)
                # The function body starts after the def line
                if node.body and hasattr(node.body[0], "lineno"):
                    first_body_line = node.body[0].lineno
                    # If the range is between first decorator and first body line,
                    # it's part of the decorator pattern
                    if start_line >= first_decorator_line and end_line < first_body_line:
                        return True
            return False

        # Call: Function/constructor call (including multiline arguments)
        # For multi-line calls, filter if the call contains the start of the range
        # This handles cases where a 3-line window includes the end of a constructor
        # plus some trailing code
        if isinstance(node, ast.Call):
            is_multiline = node.lineno < node.end_lineno
            if is_multiline and node.lineno <= start_line <= node.end_lineno:
                return True
            # For single-line calls, require full containment
            if not is_multiline and contains:
                return True

        # Expr: Expression statement (could be a single multiline expression)
        # Only filter if this Expr completely contains the flagged range
        if isinstance(node, ast.Expr) and contains:
            return True

        # Single assignment
        # For multi-line assignments, filter if the assignment contains the start of the range
        # This handles cases where constructor arguments span into the flagged range
        if isinstance(node, ast.Assign):
            is_multiline = node.lineno < node.end_lineno
            if is_multiline and node.lineno <= start_line <= node.end_lineno:
                return True
            # For single-line assignments, require full containment
            if not is_multiline and contains:
                return True

        return False

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

    def _is_part_of_decorator(self, lines: list[str], start_line: int, end_line: int) -> bool:
        """Check if lines are part of a decorator + function definition.

        A decorator pattern is @something(...) followed by def/class.
        """
        # Look backwards for @ symbol, forwards for def/class
        lookback_start = max(0, start_line - 10)
        lookforward_end = min(len(lines), end_line + 10)

        # Extract expanded context
        context_lines = lines[lookback_start:lookforward_end]
        context = "\n".join(context_lines)

        try:
            tree = ast.parse(context)
            # Find a function or class with decorators in the context
            for stmt in tree.body:
                if isinstance(stmt, (ast.FunctionDef, ast.ClassDef)) and stmt.decorator_list:
                    return True
        except SyntaxError:
            pass

        return False

    def _is_part_of_function_call(self, lines: list[str], start_line: int, end_line: int) -> bool:
        """Check if lines are arguments inside a function/constructor call.

        Detects patterns like:
            obj = Constructor(
                arg1=value1,
                arg2=value2,
            )
        """
        # Look backwards for opening paren, forwards for closing paren
        lookback_start = max(0, start_line - 10)
        lookforward_end = min(len(lines), end_line + 10)

        context_lines = lines[lookback_start:lookforward_end]
        context = "\n".join(context_lines)

        try:
            tree = ast.parse(context)
            # If the expanded context has exactly 1 statement (and it's not a function def),
            # the flagged lines are part of it
            if len(tree.body) == 1 and not isinstance(
                tree.body[0], (ast.FunctionDef, ast.ClassDef)
            ):
                return True
        except SyntaxError:
            pass

        return False

    def _is_part_of_class_body(self, lines: list[str], start_line: int, end_line: int) -> bool:
        """Check if lines are field definitions inside a class body.

        Detects patterns like:
            class Foo:
                field1: Type1
                field2: Type2
        """
        # Look backwards for class definition
        lookback_start = max(0, start_line - 10)
        lookforward_end = min(len(lines), end_line + 5)

        context_lines = lines[lookback_start:lookforward_end]
        context = "\n".join(context_lines)

        try:
            tree = ast.parse(context)
            # Check if any statement is a class definition and the flagged lines
            # fall within the class body range
            for stmt in tree.body:
                if isinstance(stmt, ast.ClassDef):
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
        except SyntaxError:
            pass

        return False
