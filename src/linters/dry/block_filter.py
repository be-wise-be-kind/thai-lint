"""
Purpose: Extensible filter system for DRY duplicate detection

Scope: Filters out false positive duplications (API boilerplate, keyword arguments, etc.)

Overview: Provides an extensible architecture for filtering duplicate code blocks that are
    not meaningful duplications. Includes base filter interface and built-in filters for
    common false positive patterns like keyword-only function arguments, import groups,
    and API call boilerplate. New filters can be added by subclassing BaseBlockFilter.

Dependencies: ast, re, typing

Exports: BaseBlockFilter, BlockFilterRegistry, KeywordArgumentFilter, ImportGroupFilter

Interfaces: BaseBlockFilter.should_filter(code_block, file_content) -> bool

Implementation: Strategy pattern with filter registry for extensibility
"""

import ast
import re
from abc import ABC, abstractmethod
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


class BaseBlockFilter(ABC):
    """Base class for duplicate block filters."""

    @abstractmethod
    def should_filter(self, block: CodeBlock, file_content: str) -> bool:
        """Determine if a code block should be filtered out.

        Args:
            block: Code block to evaluate
            file_content: Full file content for context

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

    def should_filter(self, block: CodeBlock, file_content: str) -> bool:
        """Check if block is primarily keyword arguments.

        Args:
            block: Code block to evaluate
            file_content: Full file content for context

        Returns:
            True if block should be filtered
        """
        lines = file_content.split("\n")[block.start_line - 1 : block.end_line]

        if not lines:
            return False

        # Count lines that match keyword argument pattern
        kwarg_lines = sum(1 for line in lines if self._kwarg_pattern.match(line))

        # Filter if most lines are keyword arguments
        ratio = kwarg_lines / len(lines)
        if ratio >= self.threshold:
            return self._is_inside_function_call(block, file_content)

        return False

    def _is_inside_function_call(self, block: CodeBlock, file_content: str) -> bool:
        """Verify the block is inside a function call, not standalone code."""
        try:
            tree = ast.parse(file_content)
        except SyntaxError:
            return False

        # Find if any Call node contains the block
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._check_multiline_containment(node, block):
                return True
        return False

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

    def should_filter(self, block: CodeBlock, file_content: str) -> bool:
        """Check if block is only import statements.

        Args:
            block: Code block to evaluate
            file_content: Full file content

        Returns:
            True if block should be filtered
        """
        lines = file_content.split("\n")[block.start_line - 1 : block.end_line]

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

    def should_filter_block(self, block: CodeBlock, file_content: str) -> bool:
        """Check if any enabled filter wants to filter this block.

        Args:
            block: Code block to evaluate
            file_content: Full file content

        Returns:
            True if block should be filtered out
        """
        enabled_filters = (f for f in self._filters if f.name in self._enabled_filters)
        return any(f.should_filter(block, file_content) for f in enabled_filters)

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

    return registry
