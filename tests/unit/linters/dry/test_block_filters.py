"""
Purpose: Unit tests for extensible block filter system

Scope: Tests for KeywordArgumentFilter, ImportGroupFilter, and BlockFilterRegistry

Overview: TDD tests ensuring filters correctly identify and filter false positive duplications
    like keyword arguments in function calls, import groups, and other API boilerplate patterns.
"""

from pathlib import Path

from src.linters.dry.block_filter import (
    ImportGroupFilter,
    KeywordArgumentFilter,
    create_default_registry,
)
from src.linters.dry.cache import CodeBlock


class TestKeywordArgumentFilter:
    """Test keyword argument filter with real-world examples."""

    def test_filters_violation_builder_pattern(self):
        """Test that the filter catches the violation_builder.py pattern.

        This is the exact pattern reported as a false positive:
        src/linters/srp/violation_builder.py:58:1 - lines 58-60
        """
        # Exact code from violation_builder.py lines 53-61
        # Lines are numbered starting at 1 in this test content
        file_content = """from typing import Any

from src.core.base import BaseLintContext
from src.core.types import Severity, Violation
from src.core.violation_builder import BaseViolationBuilder, ViolationInfo


class ViolationBuilder(BaseViolationBuilder):
    def build_violation(
        self,
        metrics: dict[str, Any],
        issues: list[str],
        rule_id: str,
        context: BaseLintContext,
    ) -> Violation:
        message = f"Class '{metrics['class_name']}' may violate SRP: {', '.join(issues)}"
        suggestion = self._generate_suggestion(issues)

        info = ViolationInfo(
            rule_id=rule_id,
            file_path=str(context.file_path or ""),
            line=metrics["line"],
            column=metrics["column"],
            message=message,
            severity=Severity.ERROR,
            suggestion=suggestion,
        )
        return self.build(info)
"""

        # Lines 24-26 in THIS content correspond to the keyword arguments
        # (message=, severity=, suggestion=) inside ViolationInfo() call
        block = CodeBlock(
            file_path=Path("src/linters/srp/violation_builder.py"),
            start_line=24,
            end_line=26,
            snippet="message=message,\nseverity=Severity.ERROR,\nsuggestion=suggestion,",
            hash_value=12345,
        )

        filter_instance = KeywordArgumentFilter(threshold=0.8)

        # This should be filtered (return True) because:
        # 1. All 3 lines are keyword arguments (100% >= 80%)
        # 2. They're inside the ViolationInfo() constructor call
        assert filter_instance.should_filter(block, file_content), (
            "Filter should detect keyword arguments inside function call"
        )

    def test_filters_violation_factory_pattern(self):
        """Test filter catches violation_factory.py pattern (lines 57-59)."""
        file_content = """from pathlib import Path
from src.core.types import Severity, Violation
from src.core.violation_builder import BaseViolationBuilder


class ViolationFactory(BaseViolationBuilder):
    def create_deny_violation(self, rel_path: Path, matched_path: str, reason: str) -> Violation:
        message = f"File '{rel_path}' not allowed in {matched_path}: {reason}"
        suggestion = self._get_suggestion(rel_path.name)
        return self.build_from_params(
            rule_id="file-placement",
            file_path=str(rel_path),
            line=1,
            column=0,
            message=message,
            severity=Severity.ERROR,
            suggestion=suggestion,
        )
"""

        # Lines 15-17 in THIS test content (corresponds to actual file lines 57-59)
        block = CodeBlock(
            file_path=Path("src/linters/file_placement/violation_factory.py"),
            start_line=15,
            end_line=17,
            snippet="message=message,\nseverity=Severity.ERROR,\nsuggestion=suggestion,",
            hash_value=12345,
        )

        filter_instance = KeywordArgumentFilter(threshold=0.8)
        assert filter_instance.should_filter(block, file_content), (
            "Should filter keyword arguments in build_from_params call"
        )

    def test_does_not_filter_similar_looking_code(self):
        """Test that filter doesn't incorrectly filter non-keyword-arg code."""
        file_content = """
def process_data():
    result = calculate()
    value = transform(result)
    output = format(value)
    return output
"""

        block = CodeBlock(
            file_path=Path("test.py"),
            start_line=2,
            end_line=4,
            snippet="result = calculate()\nvalue = transform(result)\noutput = format(value)",
            hash_value=99999,
        )

        filter_instance = KeywordArgumentFilter(threshold=0.8)
        # These are assignments, not keyword arguments - should NOT filter
        assert not filter_instance.should_filter(block, file_content), (
            "Should not filter regular assignments"
        )

    def test_threshold_filters_all_keyword_args(self):
        """Test that 100% keyword arguments gets filtered with default threshold."""
        file_content = """obj = Constructor(
    param1=value1,
    param2=value2,
    param3=value3,
)
"""

        # Lines 2-4: All 3 lines are keyword args = 100%
        block = CodeBlock(
            file_path=Path("test.py"),
            start_line=2,
            end_line=4,
            snippet="param1=value1,\nparam2=value2,\nparam3=value3,",
            hash_value=11111,
        )

        # With default 0.8 threshold (80%), SHOULD filter (100% >= 80%)
        filter_instance = KeywordArgumentFilter(threshold=0.8)
        assert filter_instance.should_filter(block, file_content)


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

    def test_does_not_filter_mixed_content(self):
        """Test filter doesn't catch blocks with imports and code."""
        file_content = """import os
import sys
x = 5
"""

        block = CodeBlock(
            file_path=Path("test.py"),
            start_line=1,
            end_line=3,
            snippet="import os\nimport sys\nx = 5",
            hash_value=33333,
        )

        filter_instance = ImportGroupFilter()
        assert not filter_instance.should_filter(block, file_content)


class TestBlockFilterRegistry:
    """Test filter registry management."""

    def test_default_registry_has_filters(self):
        """Test that default registry includes built-in filters."""
        registry = create_default_registry()
        enabled = registry.get_enabled_filters()

        assert "keyword_argument_filter" in enabled
        assert "import_group_filter" in enabled

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
