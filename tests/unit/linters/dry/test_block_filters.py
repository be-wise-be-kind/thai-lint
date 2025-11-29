"""
Purpose: Unit tests for extensible block filter system

Scope: Testing block filters for excluding false positive duplications

Overview: Comprehensive test suite ensuring filters correctly identify and exclude false positive
    duplications such as keyword arguments in function calls, import statement groups, and other
    API boilerplate patterns from DRY violation detection. Tests filter registry management
    including enabling and disabling filters, and validates each filter type independently.

Dependencies: pytest, pathlib.Path, src.linters.dry.block_filter, src.linters.dry.cache.CodeBlock

Exports: TestKeywordArgumentFilter, TestImportGroupFilter, TestBlockFilterRegistry test classes

Interfaces: test_filters_import_only_blocks, test_can_disable_filters, and other test methods

Implementation: Creates CodeBlock instances for testing, uses filter registry for configuration,
    validates filter application logic
"""

from pathlib import Path

from src.linters.dry.block_filter import (
    ImportGroupFilter,
    create_default_registry,
)
from src.linters.dry.cache import CodeBlock


class TestKeywordArgumentFilter:
    """Test keyword argument filter with real-world examples."""


class TestImportGroupFilter:
    """Test import group filter."""

    def test_filters_import_only_blocks(self):
        """Test filter catches blocks of only import statements."""
        file_content = """
import os
import sys
from pathlib import Path
"""

        block = CodeBlock(
            file_path=Path("test.py"),
            start_line=1,
            end_line=3,
            snippet="import os\nimport sys\nfrom pathlib import Path",
            hash_value=22222,
        )

        filter_instance = ImportGroupFilter()
        assert filter_instance.should_filter(block, file_content)


class TestBlockFilterRegistry:
    """Test filter registry management."""

    def test_can_disable_filters(self):
        """Test that filters can be disabled."""
        registry = create_default_registry()
        registry.disable_filter("keyword_argument_filter")

        enabled = registry.get_enabled_filters()
        assert "keyword_argument_filter" not in enabled
        assert "import_group_filter" in enabled

    def test_disabled_filter_does_not_run(self):
        """Test that disabled filters don't filter blocks."""
        file_content = """
obj = Constructor(
    param1=value1,
    param2=value2,
)
"""

        block = CodeBlock(
            file_path=Path("test.py"),
            start_line=2,
            end_line=3,
            snippet="param1=value1,\nparam2=value2,",
            hash_value=44444,
        )

        # With filter enabled
        registry_enabled = create_default_registry()
        assert registry_enabled.should_filter_block(block, file_content)

        # With filter disabled
        registry_disabled = create_default_registry()
        registry_disabled.disable_filter("keyword_argument_filter")
        assert not registry_disabled.should_filter_block(block, file_content)
