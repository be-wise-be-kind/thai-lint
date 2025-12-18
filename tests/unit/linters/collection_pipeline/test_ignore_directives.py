"""
Purpose: Test suite for collection-pipeline linter ignore directive system

Scope: 5-level ignore directive testing for collection-pipeline rule

Overview: TDD test suite for collection-pipeline linter ignore support
    covering file-level ignore directives (# thailint: ignore-file),
    line-level ignore directives (# thailint: ignore-next-line and inline),
    block-level ignore directives (# thailint: ignore-start/ignore-end),
    and config-based ignore patterns. Tests define expected behavior
    following Red-Green-Refactor methodology.

Dependencies: pytest for testing framework, src.linters.collection_pipeline,
    pathlib for Path handling, unittest.mock for Mock contexts

Exports: TestFileLevelIgnore, TestLineLevelIgnore, TestBlockLevelIgnore test classes

Interfaces: Tests CollectionPipelineRule with ignore directives

Implementation: TDD approach - tests written to fail initially, then implementation
    makes them pass. Uses inline Python code strings as test fixtures with mock contexts.
"""

from pathlib import Path
from unittest.mock import Mock


class TestFileLevelIgnore:
    """Test file-level ignore directives."""

    def test_ignores_file_with_ignore_file_directive(self) -> None:
        """Should ignore entire file with # thailint: ignore-file directive."""
        code = """# thailint: ignore-file
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore file with ignore-file directive"

    def test_ignores_file_with_rule_specific_ignore_file(self) -> None:
        """Should ignore file with rule-specific ignore directive."""
        code = """# thailint: ignore-file[collection-pipeline]
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore file with rule-specific directive"

    def test_does_not_ignore_file_with_different_rule_ignore(self) -> None:
        """Should not ignore file if ignore directive is for different rule."""
        code = """# thailint: ignore-file[srp]
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 1, "Should detect violation when ignore is for different rule"


class TestLineLevelIgnore:
    """Test line-level ignore directives."""

    def test_ignores_loop_with_inline_ignore_directive(self) -> None:
        """Should ignore loop with inline # thailint: ignore comment."""
        code = """
for item in items:  # thailint: ignore
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore loop with inline ignore"

    def test_ignores_loop_with_rule_specific_inline_ignore(self) -> None:
        """Should ignore loop with rule-specific inline ignore."""
        code = """
for item in items:  # thailint: ignore[collection-pipeline]
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore loop with rule-specific inline ignore"

    def test_does_not_ignore_loop_with_different_rule_inline_ignore(self) -> None:
        """Should not ignore loop if inline ignore is for different rule."""
        code = """
for item in items:  # thailint: ignore[srp]
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 1, "Should detect violation when ignore is for different rule"

    def test_ignores_loop_with_ignore_next_line_directive(self) -> None:
        """Should ignore loop with # thailint: ignore-next-line above it."""
        code = """
# thailint: ignore-next-line
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore loop with ignore-next-line directive"

    def test_ignores_loop_with_rule_specific_ignore_next_line(self) -> None:
        """Should ignore loop with rule-specific ignore-next-line."""
        code = """
# thailint: ignore-next-line[collection-pipeline]
for item in items:
    if not item.is_valid():
        continue
    process(item)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore loop with rule-specific ignore-next-line"


class TestBlockLevelIgnore:
    """Test block-level ignore directives."""

    def test_ignores_loop_within_ignore_block(self) -> None:
        """Should ignore loop within ignore-start/ignore-end block."""
        code = """
# thailint: ignore-start
for item in items:
    if not item.is_valid():
        continue
    process(item)
# thailint: ignore-end

for other in others:
    if not other.is_valid():
        continue
    process(other)
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 1, "Should only flag loop outside ignore block"
        # The second loop (for other in others) should be flagged
        assert violations[0].line > 7, "Violation should be on second loop"

    def test_ignores_loop_within_rule_specific_block(self) -> None:
        """Should ignore loop within rule-specific ignore block."""
        code = """
# thailint: ignore-start collection-pipeline
for item in items:
    if not item.is_valid():
        continue
    process(item)
# thailint: ignore-end
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 0, "Should ignore loop in rule-specific ignore block"

    def test_does_not_ignore_loop_with_different_rule_block(self) -> None:
        """Should not ignore loop if block is for different rule."""
        code = """
# thailint: ignore-start srp
for item in items:
    if not item.is_valid():
        continue
    process(item)
# thailint: ignore-end
"""
        from src.linters.collection_pipeline.linter import CollectionPipelineRule

        rule = CollectionPipelineRule()
        context = Mock()
        context.file_path = Path("test.py")
        context.file_content = code
        context.language = "python"
        context.metadata = {}
        context.config = None

        violations = rule.check(context)
        assert len(violations) == 1, "Should detect violation when block is for different rule"
