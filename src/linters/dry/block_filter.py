"""
Purpose: Extensible filter system for DRY duplicate detection

Scope: Filters out false positive duplications (API boilerplate, keyword arguments, etc.)

Overview: Provides an extensible architecture for filtering duplicate code blocks that are
    not meaningful duplications. Includes base filter interface and built-in filters for
    common false positive patterns like keyword-only function arguments, import groups,
    and API call boilerplate. New filters can be added by subclassing BaseBlockFilter.

Dependencies: ast, re, typing

Exports: BaseBlockFilter, BlockFilterRegistry, FilterCache, KeywordArgumentFilter,
    ImportGroupFilter, LoggerCallFilter, ExceptionReraiseFilter

Interfaces: BaseBlockFilter.should_filter(code_block, file_content, cache=None) -> bool

Implementation: Strategy pattern with filter registry for extensibility

Suppressions:
    - type:ignore[operator]: Tree-sitter Node comparison operations (optional dependency)
"""

import ast
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

# Default filter threshold constants
DEFAULT_KEYWORD_ARG_THRESHOLD = 0.8


class CodeBlock(Protocol):
    """Protocol for code blocks (matches cache.CodeBlock)."""

    file_path: Path
    start_line: int
    end_line: int
    snippet: str
    hash_value: int


@dataclass
class FilterCache:
    """Pre-computed whole-file data a caller can supply to avoid redundant work.

    Analyzers that call should_filter/should_filter_block once per candidate block
    can build these once per file and pass the same instance through every call,
    instead of every filter re-deriving them (re-parsing, re-walking, re-splitting
    the whole file) on every block. See issue #233.
    """

    ast_tree: ast.Module | None = None
    line_to_node_index: dict[int, list[ast.AST]] | None = None
    lines: list[str] | None = None


# Alias kept short so should_filter's signature fits on one line across every
# implementer - the multi-line form repeated identically per subclass was
# itself flagged as duplicate code.
Cache = FilterCache | None


def _block_lines(block: CodeBlock, file_content: str, cache: Cache) -> list[str]:
    """Get the lines spanned by a block, reusing cached pre-split lines if available."""
    lines = cache.lines if cache is not None else None
    if lines is None:
        lines = file_content.split("\n")
    return lines[block.start_line - 1 : block.end_line]


class BaseBlockFilter(ABC):
    """Base class for duplicate block filters."""

    @abstractmethod
    def should_filter(self, block: CodeBlock, file_content: str, cache: Cache = None) -> bool:
        """Determine if a code block should be filtered out.

        Args:
            block: Code block to evaluate
            file_content: Full file content for context
            cache: Pre-computed whole-file data, if the caller already has it
                (avoids re-parsing/re-walking/re-splitting the whole file per block)

        Returns:
            True if block should be filtered (not reported as duplicate)
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Filter name for configuration and logging."""
        pass


class KeywordArgumentFilter(BaseBlockFilter):
    """Filters blocks that are primarily keyword arguments in function calls.

    Detects patterns like:
        message=message,
        severity=Severity.ERROR,
        suggestion=suggestion,

    These are common in builder patterns and API calls.
    """

    def __init__(self, threshold: float = DEFAULT_KEYWORD_ARG_THRESHOLD):
        """Initialize filter.

        Args:
            threshold: Minimum percentage of lines that must be keyword args (0.0-1.0)
        """
        self.threshold = threshold
        # Pattern: optional whitespace, identifier, =, value, optional comma
        self._kwarg_pattern = re.compile(r"^\s*\w+\s*=\s*.+,?\s*$")

    def should_filter(self, block: CodeBlock, file_content: str, cache: Cache = None) -> bool:
        """Check if block is primarily keyword arguments.

        Args:
            block: Code block to evaluate
            file_content: Full file content for context
            cache: Pre-computed whole-file data, if available

        Returns:
            True if block should be filtered
        """
        lines = _block_lines(block, file_content, cache)

        if not lines:
            return False

        # Count lines that match keyword argument pattern
        kwarg_lines = sum(1 for line in lines if self._kwarg_pattern.match(line))

        # Filter if most lines are keyword arguments
        ratio = kwarg_lines / len(lines)
        if ratio >= self.threshold:
            return self._is_inside_function_call(block, file_content, cache)

        return False

    def _is_inside_function_call(
        self, block: CodeBlock, file_content: str, cache: Cache = None
    ) -> bool:
        """Verify the block is inside a function call, not standalone code."""
        if cache is not None and cache.line_to_node_index is not None:
            return self._contains_call_via_index(block, cache.line_to_node_index)
        return self._contains_call_via_walk(block, file_content, cache)

    def _contains_call_via_index(
        self, block: CodeBlock, line_to_node_index: dict[int, list[ast.AST]]
    ) -> bool:
        """Check for a containing Call node using the pre-built line index."""
        candidates = line_to_node_index.get(block.start_line, [])
        return any(
            isinstance(node, ast.Call) and self._check_multiline_containment(node, block)
            for node in candidates
        )

    def _contains_call_via_walk(self, block: CodeBlock, file_content: str, cache: Cache) -> bool:
        """Check for a containing Call node by parsing/walking the whole tree."""
        tree = self._resolve_tree(file_content, cache)
        if tree is None:
            return False

        return any(
            isinstance(node, ast.Call) and self._check_multiline_containment(node, block)
            for node in ast.walk(tree)
        )

    @staticmethod
    def _resolve_tree(file_content: str, cache: Cache) -> ast.Module | None:
        """Get the cached AST if available, otherwise parse file_content."""
        if cache is not None and cache.ast_tree is not None:
            return cache.ast_tree
        try:
            return ast.parse(file_content)
        except SyntaxError:
            return None

    @staticmethod
    def _check_multiline_containment(node: ast.Call, block: CodeBlock) -> bool:
        """Check if Call node is multiline and contains block."""
        if not KeywordArgumentFilter._has_valid_line_info(node):
            return False

        # After validation, these are guaranteed to be non-None integers
        # Use type: ignore to suppress MyPy's inability to understand runtime validation
        is_multiline = node.lineno < node.end_lineno  # type: ignore[operator]
        contains_block = (
            node.lineno <= block.start_line and node.end_lineno >= block.end_line  # type: ignore[operator]
        )
        return is_multiline and contains_block

    @staticmethod
    def _has_valid_line_info(node: ast.Call) -> bool:
        """Check if node has valid line information.

        Args:
            node: AST Call node to check

        Returns:
            True if node has valid line number attributes
        """
        if not hasattr(node, "lineno"):
            return False
        if not hasattr(node, "end_lineno"):
            return False
        if node.lineno is None:
            return False
        if node.end_lineno is None:
            return False
        return True

    @property
    def name(self) -> str:
        """Filter name."""
        return "keyword_argument_filter"


class ImportGroupFilter(BaseBlockFilter):
    """Filters blocks that are just import statements.

    Import organization often creates similar patterns that aren't meaningful duplication.
    """

    def __init__(self) -> None:
        """Initialize the import group filter."""
        pass  # Stateless filter for import blocks

    def should_filter(self, block: CodeBlock, file_content: str, cache: Cache = None) -> bool:
        """Check if block is only import statements.

        Args:
            block: Code block to evaluate
            file_content: Full file content
            cache: Pre-computed whole-file data, if available

        Returns:
            True if block should be filtered
        """
        lines = _block_lines(block, file_content, cache)

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if not (stripped.startswith("import ") or stripped.startswith("from ")):
                return False

        return True

    @property
    def name(self) -> str:
        """Filter name."""
        return "import_group_filter"


class LoggerCallFilter(BaseBlockFilter):
    """Filters single-line logger calls that are idiomatic but appear similar.

    Detects patterns like:
        logger.debug(f"Command: {cmd}")
        logger.info("Starting process...")
        logging.warning("...")

    These are contextually different despite structural similarity.
    """

    def __init__(self) -> None:
        """Initialize the logger call filter."""
        # Pattern matches: logger.level(...) or logging.level(...)
        self._logger_pattern = re.compile(
            r"^\s*(self\.)?(logger|logging|log)\."
            r"(debug|info|warning|error|critical|exception|log)\s*\("
        )

    def should_filter(self, block: CodeBlock, file_content: str, cache: Cache = None) -> bool:
        """Check if block is primarily single-line logger calls.

        Args:
            block: Code block to evaluate
            file_content: Full file content
            cache: Pre-computed whole-file data, if available

        Returns:
            True if block should be filtered
        """
        lines = _block_lines(block, file_content, cache)
        non_empty = [s for line in lines if (s := line.strip())]

        if not non_empty:
            return False

        # Filter if it's a single line that's a logger call
        if len(non_empty) == 1:
            return bool(self._logger_pattern.match(non_empty[0]))

        return False

    @property
    def name(self) -> str:
        """Filter name."""
        return "logger_call_filter"


class ExceptionReraiseFilter(BaseBlockFilter):
    """Filters idiomatic exception re-raising patterns.

    Detects patterns like:
        except SomeError as e:
            raise NewError(...) from e

    These are Python best practices for exception chaining.
    """

    def __init__(self) -> None:
        """Initialize the exception reraise filter."""
        pass  # Stateless filter

    def should_filter(self, block: CodeBlock, file_content: str, cache: Cache = None) -> bool:
        """Check if block is an exception re-raise pattern.

        Args:
            block: Code block to evaluate
            file_content: Full file content
            cache: Pre-computed whole-file data, if available

        Returns:
            True if block should be filtered
        """
        lines = _block_lines(block, file_content, cache)
        stripped_lines = [s for line in lines if (s := line.strip())]

        if len(stripped_lines) != 2:
            return False

        return self._is_except_raise_pattern(stripped_lines)

    @staticmethod
    def _is_except_raise_pattern(lines: list[str]) -> bool:
        """Check if lines form an except/raise pattern."""
        first, second = lines[0], lines[1]
        is_except = first.startswith("except ") and first.endswith(":")
        is_raise = second.startswith("raise ") and " from " in second
        return is_except and is_raise

    @property
    def name(self) -> str:
        """Filter name."""
        return "exception_reraise_filter"


class BlockFilterRegistry:
    """Registry for managing duplicate block filters."""

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._filters: list[BaseBlockFilter] = []
        self._enabled_filters: set[str] = set()

    def register(self, filter_instance: BaseBlockFilter) -> None:
        """Register a filter.

        Args:
            filter_instance: Filter to register
        """
        self._filters.append(filter_instance)
        self._enabled_filters.add(filter_instance.name)

    def enable_filter(self, filter_name: str) -> None:
        """Enable a specific filter by name.

        Args:
            filter_name: Name of filter to enable
        """
        self._enabled_filters.add(filter_name)

    def disable_filter(self, filter_name: str) -> None:
        """Disable a specific filter by name.

        Args:
            filter_name: Name of filter to disable
        """
        self._enabled_filters.discard(filter_name)

    def should_filter_block(self, block: CodeBlock, file_content: str, cache: Cache = None) -> bool:
        """Check if any enabled filter wants to filter this block.

        Args:
            block: Code block to evaluate
            file_content: Full file content
            cache: Pre-computed whole-file data, if the caller already has it
                (passed through to filters that need it)

        Returns:
            True if block should be filtered out
        """
        enabled_filters = (f for f in self._filters if f.name in self._enabled_filters)
        return any(f.should_filter(block, file_content, cache) for f in enabled_filters)

    def get_enabled_filters(self) -> list[str]:
        """Get list of enabled filter names.

        Returns:
            List of enabled filter names
        """
        return sorted(self._enabled_filters)


def create_default_registry() -> BlockFilterRegistry:
    """Create registry with default filters.

    Returns:
        BlockFilterRegistry with common filters registered
    """
    registry = BlockFilterRegistry()

    # Register built-in filters
    registry.register(KeywordArgumentFilter(threshold=DEFAULT_KEYWORD_ARG_THRESHOLD))
    registry.register(ImportGroupFilter())
    registry.register(LoggerCallFilter())
    registry.register(ExceptionReraiseFilter())

    return registry
