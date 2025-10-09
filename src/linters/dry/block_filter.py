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

    @abstractmethod
    def get_name(self) -> str:
        """Get filter name for configuration and logging."""
        pass


class KeywordArgumentFilter(BaseBlockFilter):
    """Filters blocks that are primarily keyword arguments in function calls.

    Detects patterns like:
        message=message,
        severity=Severity.ERROR,
        suggestion=suggestion,

    These are common in builder patterns and API calls.
    """

    def __init__(self, threshold: float = 0.8):
        """Initialize filter.

        Args:
            threshold: Minimum percentage of lines that must be keyword args (0.0-1.0)
        """
        self.threshold = threshold
        # Pattern: optional whitespace, identifier, =, value, optional comma
        self._kwarg_pattern = re.compile(r'^\s*\w+\s*=\s*.+,?\s*$')

    def should_filter(self, block: CodeBlock, file_content: str) -> bool:
        """Check if block is primarily keyword arguments.

        Args:
            block: Code block to evaluate
            file_content: Full file content for context

        Returns:
            True if block should be filtered
        """
        lines = file_content.split('\n')[block.start_line - 1:block.end_line]

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
        """Verify the block is inside a function call, not standalone code.

        Args:
            block: Code block to evaluate
            file_content: Full file content

        Returns:
            True if block is inside a function/constructor call
        """
        try:
            tree = ast.parse(file_content)
        except SyntaxError:
            return False

        # Find Call nodes that contain this block
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            if not (hasattr(node, 'lineno') and hasattr(node, 'end_lineno')):
                continue

            # Check if call spans multiple lines and contains the block
            is_multiline = node.lineno < node.end_lineno
            contains_block = node.lineno <= block.start_line and node.end_lineno >= block.end_line

            if is_multiline and contains_block:
                return True

        return False

    def get_name(self) -> str:
        """Get filter name."""
        return "keyword_argument_filter"


class ImportGroupFilter(BaseBlockFilter):
    """Filters blocks that are just import statements.

    Import organization often creates similar patterns that aren't meaningful duplication.
    """

    def should_filter(self, block: CodeBlock, file_content: str) -> bool:
        """Check if block is only import statements.

        Args:
            block: Code block to evaluate
            file_content: Full file content

        Returns:
            True if block should be filtered
        """
        lines = file_content.split('\n')[block.start_line - 1:block.end_line]

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if not (stripped.startswith('import ') or stripped.startswith('from ')):
                return False

        return True

    def get_name(self) -> str:
        """Get filter name."""
        return "import_group_filter"


class BlockFilterRegistry:
    """Registry for managing duplicate block filters."""

    def __init__(self):
        """Initialize empty registry."""
        self._filters: list[BaseBlockFilter] = []
        self._enabled_filters: set[str] = set()

    def register(self, filter_instance: BaseBlockFilter) -> None:
        """Register a filter.

        Args:
            filter_instance: Filter to register
        """
        self._filters.append(filter_instance)
        self._enabled_filters.add(filter_instance.get_name())

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
        for filter_instance in self._filters:
            if filter_instance.get_name() not in self._enabled_filters:
                continue

            if filter_instance.should_filter(block, file_content):
                return True

        return False

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
    registry.register(KeywordArgumentFilter(threshold=0.8))
    registry.register(ImportGroupFilter())

    return registry
