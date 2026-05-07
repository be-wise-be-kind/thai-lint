"""
Purpose: Test Python AST chain extraction and import tracking functions

Scope: AST-based chain extraction, import extraction, and chain deduplication

Overview: Validates the extract_chains() and extract_imports() functions that walk Python AST
    trees to find attribute/method chains meeting minimum depth, extract import information for
    the module-access filter, and deduplicate chains (keeping longest per line). Tests cover
    extract_chains() behavior with various code patterns and extract_imports() for both
    'import x' and 'from x import y' styles.

Dependencies: pytest, ast, src.linters.law_of_demeter.python_analyzer

Exports: TestExtractChains (6 tests), TestExtractImports (5 tests) - total 11 test cases

Interfaces: Tests extract_chains() and extract_imports() module-level functions

Implementation: Parses Python code strings via ast.parse(), calls module-level functions,
    verifies chain extraction results and import tracking
"""

import ast


class TestExtractChains:
    """Test chain extraction from Python AST."""

    def test_finds_depth_3_chain(self) -> None:
        """Should find chains of depth >= 3."""
        from src.linters.law_of_demeter.python_analyzer import extract_chains

        code = "x = a.b.c.d"
        tree = ast.parse(code)
        chains = extract_chains(tree, min_depth=3)
        assert len(chains) >= 1

    def test_skips_short_chains(self) -> None:
        """Should skip chains shorter than min_depth."""
        from src.linters.law_of_demeter.python_analyzer import extract_chains

        code = "x = a.b"
        tree = ast.parse(code)
        chains = extract_chains(tree, min_depth=3)
        assert len(chains) == 0

    def test_deduplicates_by_line(self) -> None:
        """Should keep only longest chain per line."""
        from src.linters.law_of_demeter.python_analyzer import extract_chains

        # a.b.c.d contains sub-chain a.b.c - should only report longest
        code = "x = a.b.c.d"
        tree = ast.parse(code)
        chains = extract_chains(tree, min_depth=3)
        assert len(chains) == 1

    def test_finds_chains_in_multiple_functions(self) -> None:
        """Should find chains across different functions."""
        from src.linters.law_of_demeter.python_analyzer import extract_chains

        code = """
def f1():
    a.b.c.d

def f2():
    x.y.z.w
"""
        tree = ast.parse(code)
        chains = extract_chains(tree, min_depth=3)
        assert len(chains) == 2

    def test_finds_chains_in_method_calls(self) -> None:
        """Should find chains involving method calls."""
        from src.linters.law_of_demeter.python_analyzer import extract_chains

        code = "x = a.b().c.d"
        tree = ast.parse(code)
        chains = extract_chains(tree, min_depth=3)
        assert len(chains) >= 1

    def test_empty_code_returns_no_chains(self) -> None:
        """Should return empty list for empty code."""
        from src.linters.law_of_demeter.python_analyzer import extract_chains

        tree = ast.parse("")
        chains = extract_chains(tree, min_depth=3)
        assert chains == []


class TestExtractImports:
    """Test import extraction from Python AST."""

    def test_extracts_import_module(self) -> None:
        """Should track 'import os' as module name."""
        from src.linters.law_of_demeter.python_analyzer import extract_imports

        tree = ast.parse("import os")
        imports = extract_imports(tree)
        assert "os" in imports.module_names

    def test_extracts_aliased_import(self) -> None:
        """Should track 'import numpy as np' using alias."""
        from src.linters.law_of_demeter.python_analyzer import extract_imports

        tree = ast.parse("import numpy as np")
        imports = extract_imports(tree)
        assert "np" in imports.module_names

    def test_extracts_from_import(self) -> None:
        """Should track 'from pathlib import Path' mapping."""
        from src.linters.law_of_demeter.python_analyzer import extract_imports

        tree = ast.parse("from pathlib import Path")
        imports = extract_imports(tree)
        assert "Path" in imports.from_imports
        assert imports.from_imports["Path"] == "pathlib"

    def test_extracts_aliased_from_import(self) -> None:
        """Should track 'from datetime import datetime as dt' using alias."""
        from src.linters.law_of_demeter.python_analyzer import extract_imports

        tree = ast.parse("from datetime import datetime as dt")
        imports = extract_imports(tree)
        assert "dt" in imports.from_imports

    def test_multiple_imports(self) -> None:
        """Should handle multiple import statements."""
        from src.linters.law_of_demeter.python_analyzer import extract_imports

        code = """
import os
import sys
from pathlib import Path
from typing import Any
"""
        tree = ast.parse(code)
        imports = extract_imports(tree)
        assert "os" in imports.module_names
        assert "sys" in imports.module_names
        assert "Path" in imports.from_imports
        assert "Any" in imports.from_imports
