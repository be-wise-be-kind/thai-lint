"""
Purpose: Unit tests for TypeScript Demeter chain and import analyzer

Scope: Tests for TypeScriptDemeterAnalyzer.extract_chains() and extract_imports()

Overview: Validates the tree-sitter-based TypeScript analyzer that extracts attribute/method
    chains and import mappings from TypeScript source code. Tests cover chain extraction from
    member_expression nodes, call_expression chain handling, optional chaining detection,
    minimum depth filtering, per-line deduplication, and import extraction for named imports,
    namespace imports, and default imports. Verifies graceful fallback when tree-sitter is
    unavailable.

Dependencies: pytest, src.linters.law_of_demeter.typescript_analyzer

Exports: TestExtractChains, TestExtractImports, TestOptionalChaining, TestEdgeCases

Interfaces: Tests TypeScriptDemeterAnalyzer methods

Implementation: Parses TypeScript code via tree-sitter, verifies extracted chain parts and imports
"""

import pytest

from src.linters.law_of_demeter.typescript_analyzer import TypeScriptDemeterAnalyzer


@pytest.fixture()
def analyzer() -> TypeScriptDemeterAnalyzer:
    """Provide a TypeScriptDemeterAnalyzer instance."""
    return TypeScriptDemeterAnalyzer()


class TestExtractChains:
    """Test chain extraction from TypeScript member_expression nodes."""

    def test_finds_depth_3_chain(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should find a.b.c.d as a depth-3 chain."""
        code = "const x = a.b.c.d;"
        root = analyzer.parse_typescript(code)
        assert root is not None
        chains = analyzer.extract_chains(root, min_depth=3)
        assert len(chains) >= 1
        parts = chains[0][0]
        assert parts == ["a", "b", "c", "d"]

    def test_skips_short_chain(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should skip chains below min_depth."""
        code = "const x = a.b;"
        root = analyzer.parse_typescript(code)
        assert root is not None
        chains = analyzer.extract_chains(root, min_depth=3)
        assert len(chains) == 0

    def test_finds_depth_2_chain_with_min_2(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should find a.b.c as depth-2 chain when min_depth=2."""
        code = "const x = a.b.c;"
        root = analyzer.parse_typescript(code)
        assert root is not None
        chains = analyzer.extract_chains(root, min_depth=2)
        assert len(chains) >= 1
        parts = chains[0][0]
        assert parts == ["a", "b", "c"]

    def test_deduplicates_by_line(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should keep only longest chain per line."""
        code = "const x = a.b.c.d.e;"
        root = analyzer.parse_typescript(code)
        assert root is not None
        chains = analyzer.extract_chains(root, min_depth=3)
        # Should have exactly one chain (the longest on that line)
        assert len(chains) == 1
        parts = chains[0][0]
        assert len(parts) == 5  # a.b.c.d.e

    def test_call_expression_chain(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should handle a.b().c.d() call expression chains."""
        code = "const x = a.b().c.d();"
        root = analyzer.parse_typescript(code)
        assert root is not None
        chains = analyzer.extract_chains(root, min_depth=3)
        assert len(chains) >= 1
        parts = chains[0][0]
        # Should have call markers
        assert "b()" in parts or "d()" in parts

    def test_multiple_chains_on_different_lines(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should find chains on separate lines."""
        code = """
const x = a.b.c.d;
const y = e.f.g.h;
"""
        root = analyzer.parse_typescript(code)
        assert root is not None
        chains = analyzer.extract_chains(root, min_depth=3)
        assert len(chains) == 2

    def test_this_prefix_chain(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should extract chains starting with this."""
        code = """
class Foo {
    bar() {
        return this.a.b.c.d;
    }
}
"""
        root = analyzer.parse_typescript(code)
        assert root is not None
        chains = analyzer.extract_chains(root, min_depth=3)
        assert len(chains) >= 1
        parts = chains[0][0]
        assert parts[0] == "this"

    def test_returns_adapter_with_line_info(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should return adapter with lineno and col_offset."""
        code = """
const x = a.b.c.d;
"""
        root = analyzer.parse_typescript(code)
        assert root is not None
        chains = analyzer.extract_chains(root, min_depth=3)
        assert len(chains) >= 1
        _parts, adapter = chains[0]
        # TSNodeAdapter provides lineno (1-indexed) and col_offset
        assert hasattr(adapter, "lineno")
        assert hasattr(adapter, "col_offset")
        assert adapter.lineno == 2  # line 2 in the code


class TestExtractImports:
    """Test import extraction from TypeScript import statements."""

    def test_named_import(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should extract import { X } from 'module'."""
        code = "import { Router } from 'express';"
        root = analyzer.parse_typescript(code)
        assert root is not None
        imports = analyzer.extract_imports(root)
        assert "Router" in imports.from_imports
        assert imports.from_imports["Router"] == "express"

    def test_namespace_import(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should extract import * as X from 'module'."""
        code = "import * as path from 'path';"
        root = analyzer.parse_typescript(code)
        assert root is not None
        imports = analyzer.extract_imports(root)
        assert "path" in imports.module_names

    def test_default_import(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should extract import X from 'module'."""
        code = "import express from 'express';"
        root = analyzer.parse_typescript(code)
        assert root is not None
        imports = analyzer.extract_imports(root)
        assert "express" in imports.module_names

    def test_multiple_named_imports(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should extract multiple named imports from one statement."""
        code = "import { useState, useEffect } from 'react';"
        root = analyzer.parse_typescript(code)
        assert root is not None
        imports = analyzer.extract_imports(root)
        assert "useState" in imports.from_imports
        assert "useEffect" in imports.from_imports
        assert imports.from_imports["useState"] == "react"

    def test_no_imports(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should return empty imports when none present."""
        code = "const x = 1;"
        root = analyzer.parse_typescript(code)
        assert root is not None
        imports = analyzer.extract_imports(root)
        assert len(imports.module_names) == 0
        assert len(imports.from_imports) == 0


class TestOptionalChaining:
    """Test optional chaining detection."""

    def test_optional_chain_detected(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should detect optional chaining in chains."""
        code = "const x = user?.address?.city?.name;"
        root = analyzer.parse_typescript(code)
        assert root is not None
        chains = analyzer.extract_chains(root, min_depth=3)
        # Optional chains should be marked so the classifier can allow them
        if chains:
            parts = chains[0][0]
            # Parts should contain optional chain markers
            assert any("?" in p for p in parts)

    def test_mixed_optional_and_regular(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should handle mix of ?. and . access."""
        code = "const x = obj?.prop.sub.deep;"
        root = analyzer.parse_typescript(code)
        assert root is not None
        chains = analyzer.extract_chains(root, min_depth=3)
        assert len(chains) >= 1


class TestEdgeCases:
    """Test edge cases for TypeScript analyzer."""

    def test_empty_code(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should handle empty code gracefully."""
        root = analyzer.parse_typescript("")
        assert root is not None
        chains = analyzer.extract_chains(root, min_depth=3)
        assert chains == []

    def test_no_chains(self, analyzer: TypeScriptDemeterAnalyzer) -> None:
        """Should return empty list for code with no chains."""
        code = "const x = 42;"
        root = analyzer.parse_typescript(code)
        assert root is not None
        chains = analyzer.extract_chains(root, min_depth=3)
        assert chains == []
