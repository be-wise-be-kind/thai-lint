"""
Purpose: Regression test for TypeScript DRY analyzer per-window re-parsing (issue #222)

Scope: TypeScriptDuplicateAnalyzer.analyze tree-sitter parse + interface-range scaling

Overview: Guards against the O(windows x filesize) blow-up reported in issue #222, where the
    TypeScript block analyzer re-parsed the entire file with tree-sitter (and re-scanned the whole
    file for interface ranges) once per rolling-hash window, pegging a core for minutes on large or
    minified JS bundles. Verifies the analyzer now parses each file's AST a single time and computes
    interface ranges a single time, reused across every window, by counting tree-sitter parse calls
    during one analyze() run on a multi-window input. Pairs with the existing TypeScript DRY suite,
    which pins the unchanged detection behavior.

Dependencies: pytest, unittest.mock, pathlib.Path, src.analyzers.typescript_base,
    src.linters.dry.typescript_analyzer, src.linters.dry.config

Exports: TestTypeScriptParseOnce test class

Interfaces: Tests TypeScriptDuplicateAnalyzer.analyze(file_path, content, config) -> list[CodeBlock]

Implementation: Wraps TypeScriptBaseAnalyzer.parse_typescript with a call counter and asserts it runs
    a constant number of times independent of the number of rolling-hash windows
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.analyzers.typescript_base import TREE_SITTER_AVAILABLE, TypeScriptBaseAnalyzer
from src.linters.dry.config import DRYConfig
from src.linters.dry.typescript_analyzer import TypeScriptDuplicateAnalyzer

pytestmark = pytest.mark.skipif(not TREE_SITTER_AVAILABLE, reason="tree-sitter not available")

# Enough distinct lines to generate many rolling-hash windows from one file.
MANY_LINES = 120


class TestTypeScriptParseOnce:
    """The TS analyzer must parse each file once, not once per window (issue #222)."""

    def test_analyze_parses_file_a_constant_number_of_times(self) -> None:
        """analyze() must not re-parse the whole file per rolling-hash window."""
        content = "\n".join(
            f"const value{i} = compute({i}, {i + 1}, {i + 2});" for i in range(MANY_LINES)
        )
        analyzer = TypeScriptDuplicateAnalyzer()
        config = DRYConfig(enabled=True, min_duplicate_lines=4)

        original = TypeScriptBaseAnalyzer.parse_typescript
        parse_calls = 0

        def counting(self, code):  # noqa: ANN001
            nonlocal parse_calls
            parse_calls += 1
            return original(self, code)

        with patch.object(TypeScriptBaseAnalyzer, "parse_typescript", counting):
            analyzer.analyze(Path("big.ts"), content, config)

        # One parse for the file is enough; the previous code parsed once per window
        # (~117 windows here). Allow a small constant for incidental parses.
        assert parse_calls <= 2, f"expected a constant number of parses, got {parse_calls}"
