"""
Purpose: Test suite for Rust Single Responsibility Principle violation detection

Scope: Rust struct + impl block SRP analysis using tree-sitter parsing

Overview: Tests for Rust SRP violation detection covering method count violations in
    Rust structs with impl blocks, methods aggregated across multiple impl blocks,
    responsibility keyword detection in struct names, LOC violations, and language
    filtering. Validates that Rust structs are treated analogously to classes for SRP
    analysis purposes.

Dependencies: pytest, SRPRule, TREE_SITTER_RUST_AVAILABLE, pathlib, unittest.mock

Exports: TestRustMethodCount, TestRustMultipleImplBlocks, TestRustKeywords,
    TestRustLanguageFiltering, TestRustEdgeCases

Interfaces: Tests SRPRule.check(context) -> list[Violation] with Rust code samples

Implementation: Uses inline Rust code strings as test fixtures, sets language="rust",
    verifies SRP detection for struct + impl patterns
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE
from src.linters.srp.linter import SRPRule

pytestmark = pytest.mark.skipif(
    not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed"
)


def _create_context(code: str, filename: str = "main.rs", language: str = "rust") -> Mock:
    """Create mock lint context for testing."""
    context = Mock()
    context.file_content = code
    context.file_path = Path(filename)
    context.language = language
    context.metadata = {}
    return context


class TestRustMethodCount:
    """Test SRP violations based on method count in Rust structs."""

    def test_struct_with_few_methods_passes(self) -> None:
        """Struct with 3 methods should not violate."""
        code = """
struct Foo {}

impl Foo {
    fn method1(&self) {}
    fn method2(&self) {}
    fn method3(&self) {}
}
"""
        rule = SRPRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0

    def test_struct_with_many_methods_violates(self) -> None:
        """Struct with 8+ methods should violate (default max is 7)."""
        methods = "\n    ".join([f"fn method{i}(&self) {{}}" for i in range(8)])
        code = f"""
struct BigStruct {{}}

impl BigStruct {{
    {methods}
}}
"""
        rule = SRPRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0
        assert "BigStruct" in violations[0].message

    def test_struct_at_threshold_passes(self) -> None:
        """Struct with exactly 7 methods should not violate."""
        methods = "\n    ".join([f"fn method{i}(&self) {{}}" for i in range(7)])
        code = f"""
struct ExactStruct {{}}

impl ExactStruct {{
    {methods}
}}
"""
        rule = SRPRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0


class TestRustMultipleImplBlocks:
    """Test SRP with methods spread across multiple impl blocks."""

    def test_methods_aggregated_across_impl_blocks(self) -> None:
        """Methods across multiple impl blocks should be aggregated."""
        code = """
struct MultiImpl {}

impl MultiImpl {
    fn method1(&self) {}
    fn method2(&self) {}
    fn method3(&self) {}
    fn method4(&self) {}
}

impl MultiImpl {
    fn method5(&self) {}
    fn method6(&self) {}
    fn method7(&self) {}
    fn method8(&self) {}
}
"""
        rule = SRPRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0, "8 methods across 2 impl blocks should violate"

    def test_different_structs_analyzed_independently(self) -> None:
        """Multiple structs should be analyzed independently."""
        code = """
struct SmallStruct {}
impl SmallStruct {
    fn method1(&self) {}
}

struct BigManager {}
impl BigManager {
    fn method1(&self) {}
    fn method2(&self) {}
    fn method3(&self) {}
    fn method4(&self) {}
    fn method5(&self) {}
    fn method6(&self) {}
    fn method7(&self) {}
    fn method8(&self) {}
}
"""
        rule = SRPRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0
        violation_names = [v.message for v in violations]
        assert any("BigManager" in msg for msg in violation_names)


class TestRustKeywords:
    """Test SRP violations based on struct name keywords."""

    def test_struct_with_manager_keyword_flagged(self) -> None:
        """Struct with 'Manager' in name should be flagged with keyword issue."""
        code = """
struct ConnectionManager {}
impl ConnectionManager {
    fn connect(&self) {}
}
"""
        rule = SRPRule()
        violations = rule.check(_create_context(code))
        assert len(violations) > 0
        assert (
            "keyword" in violations[0].message.lower()
            or "ConnectionManager" in violations[0].message
        )

    def test_struct_without_keyword_not_flagged_for_keywords(self) -> None:
        """Struct without responsibility keywords should not be flagged for keywords."""
        code = """
struct Connection {}
impl Connection {
    fn connect(&self) {}
}
"""
        rule = SRPRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0


class TestRustLanguageFiltering:
    """Test that SRP Rust checking only processes Rust files."""

    def test_ignores_python_files(self) -> None:
        """Should not process Python files."""
        code = "class Foo:\n    pass"
        context = _create_context(code, filename="test.py", language="python")
        rule = SRPRule()
        violations = rule.check(context)
        # Python violations may occur, but Rust analyzer should not be invoked
        # This just verifies no crash
        assert isinstance(violations, list)

    def test_processes_rust_files(self) -> None:
        """Should process .rs files."""
        methods = "\n    ".join([f"fn method{i}(&self) {{}}" for i in range(8)])
        code = f"""
struct Violator {{}}
impl Violator {{
    {methods}
}}
"""
        context = _create_context(code, filename="src/lib.rs", language="rust")
        rule = SRPRule()
        violations = rule.check(context)
        assert len(violations) > 0


class TestRustEdgeCases:
    """Test edge cases for Rust SRP analysis."""

    def test_empty_file(self) -> None:
        """Should handle empty files gracefully."""
        rule = SRPRule()
        violations = rule.check(_create_context(""))
        assert len(violations) == 0

    def test_struct_without_impl(self) -> None:
        """Struct with no impl blocks should not violate."""
        code = """
struct DataOnly {
    field1: i32,
    field2: String,
}
"""
        rule = SRPRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0

    def test_impl_without_matching_struct(self) -> None:
        """Impl block without matching struct declaration should not crash."""
        code = """
impl ExternalType {
    fn method1(&self) {}
    fn method2(&self) {}
    fn method3(&self) {}
    fn method4(&self) {}
    fn method5(&self) {}
    fn method6(&self) {}
    fn method7(&self) {}
    fn method8(&self) {}
}
"""
        rule = SRPRule()
        violations = rule.check(_create_context(code))
        # Should not crash; impl without struct is fine
        assert isinstance(violations, list)

    def test_none_content(self) -> None:
        """Should handle None content gracefully."""
        context = _create_context("")
        context.file_content = None
        rule = SRPRule()
        violations = rule.check(context)
        assert len(violations) == 0

    def test_private_methods_excluded(self) -> None:
        """Methods starting with _ should not be counted."""
        code = """
struct WithPrivate {}
impl WithPrivate {
    fn public1(&self) {}
    fn public2(&self) {}
    fn _private1(&self) {}
    fn _private2(&self) {}
    fn _private3(&self) {}
    fn _private4(&self) {}
    fn _private5(&self) {}
    fn _private6(&self) {}
}
"""
        rule = SRPRule()
        violations = rule.check(_create_context(code))
        assert len(violations) == 0, "Private methods should not count toward SRP"
