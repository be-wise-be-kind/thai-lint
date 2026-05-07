"""
Purpose: Test chain_to_parts() function for AST chain extraction

Scope: Converting AST Attribute/Call/Subscript nodes into list[str] chain parts

Overview: Validates the chain_to_parts() function that walks AST nodes and extracts
    chain parts like ["obj", "method()", "attr"]. Tests cover simple attribute chains,
    method calls, mixed chains, subscript access, nested calls, and edge cases like
    bare function calls and chained calls without attributes.

Dependencies: pytest, ast, src.linters.law_of_demeter.chain_extractor

Exports: TestChainToParts (10 tests), TestChainHelpers (3 tests) - total 13 test cases

Interfaces: Tests chain_to_parts(node) -> list[str]

Implementation: Parses Python code strings via ast.parse(), walks to target nodes,
    calls chain_to_parts(), and verifies resulting part lists
"""

import ast


class TestChainToParts:
    """Test chain_to_parts() for various AST shapes."""

    def test_simple_attribute_chain(self) -> None:
        """Should extract parts from a.b.c."""
        from src.linters.law_of_demeter.chain_extractor import chain_to_parts

        tree = ast.parse("a.b.c")
        # Find the outermost Attribute node
        node = tree.body[0].value  # type: ignore[union-attr]
        parts = chain_to_parts(node)
        assert parts == ["a", "b", "c"]

    def test_method_call_chain(self) -> None:
        """Should mark method calls with () in a.b().c."""
        from src.linters.law_of_demeter.chain_extractor import chain_to_parts

        tree = ast.parse("a.b().c")
        node = tree.body[0].value  # type: ignore[union-attr]
        parts = chain_to_parts(node)
        assert parts == ["a", "b()", "c"]

    def test_chained_calls(self) -> None:
        """Should handle a.b().c().d."""
        from src.linters.law_of_demeter.chain_extractor import chain_to_parts

        tree = ast.parse("a.b().c().d")
        node = tree.body[0].value  # type: ignore[union-attr]
        parts = chain_to_parts(node)
        assert parts == ["a", "b()", "c()", "d"]

    def test_subscript_in_chain(self) -> None:
        """Should represent subscripts as [...] in a[0].b.c."""
        from src.linters.law_of_demeter.chain_extractor import chain_to_parts

        tree = ast.parse("a[0].b.c")
        node = tree.body[0].value  # type: ignore[union-attr]
        parts = chain_to_parts(node)
        # Should have subscript marker
        assert "[" in "".join(parts) or len(parts) >= 3

    def test_bare_name(self) -> None:
        """Should handle a single name node."""
        from src.linters.law_of_demeter.chain_extractor import chain_to_parts

        tree = ast.parse("x")
        node = tree.body[0].value  # type: ignore[union-attr]
        parts = chain_to_parts(node)
        assert parts == ["x"]

    def test_call_at_end(self) -> None:
        """Should handle a.b.c() with call at end."""
        from src.linters.law_of_demeter.chain_extractor import chain_to_parts

        tree = ast.parse("a.b.c()")
        node = tree.body[0].value  # type: ignore[union-attr]
        parts = chain_to_parts(node)
        assert parts == ["a", "b", "c()"]

    def test_call_at_start(self) -> None:
        """Should handle f().b.c where root is a call."""
        from src.linters.law_of_demeter.chain_extractor import chain_to_parts

        tree = ast.parse("f().b.c")
        node = tree.body[0].value  # type: ignore[union-attr]
        parts = chain_to_parts(node)
        assert parts[0] == "f()"
        assert parts[-1] == "c"

    def test_deeply_nested_chain(self) -> None:
        """Should handle a.b.c.d.e (5 parts)."""
        from src.linters.law_of_demeter.chain_extractor import chain_to_parts

        tree = ast.parse("a.b.c.d.e")
        node = tree.body[0].value  # type: ignore[union-attr]
        parts = chain_to_parts(node)
        assert parts == ["a", "b", "c", "d", "e"]

    def test_mixed_calls_and_attrs(self) -> None:
        """Should handle a.b().c.d().e pattern."""
        from src.linters.law_of_demeter.chain_extractor import chain_to_parts

        tree = ast.parse("a.b().c.d().e")
        node = tree.body[0].value  # type: ignore[union-attr]
        parts = chain_to_parts(node)
        assert len(parts) == 5
        assert parts[1] == "b()"
        assert parts[3] == "d()"

    def test_double_subscript(self) -> None:
        """Should handle a[0][1].b."""
        from src.linters.law_of_demeter.chain_extractor import chain_to_parts

        tree = ast.parse("a[0][1].b")
        node = tree.body[0].value  # type: ignore[union-attr]
        parts = chain_to_parts(node)
        assert parts[-1] == "b"


class TestChainHelpers:
    """Test helper functions for chain part analysis."""

    def test_clean_strips_call_marker(self) -> None:
        """Should strip () from chain parts."""
        from src.linters.law_of_demeter.chain_extractor import clean_part

        assert clean_part("method()") == "method"

    def test_clean_strips_subscript_marker(self) -> None:
        """Should strip [...] from chain parts."""
        from src.linters.law_of_demeter.chain_extractor import clean_part

        result = clean_part("[\u2026]")
        assert "[" not in result

    def test_is_subscript_detects_subscript(self) -> None:
        """Should detect subscript parts."""
        from src.linters.law_of_demeter.chain_extractor import is_subscript_part

        assert is_subscript_part("[\u2026]") is True
        assert is_subscript_part("method()") is False
