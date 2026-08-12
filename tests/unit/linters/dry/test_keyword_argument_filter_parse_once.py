"""
Purpose: Regression test for KeywordArgumentFilter re-parsing/re-walking the file per block (issue #233)

Scope: PythonDuplicateAnalyzer.analyze AST parsing and walking when KeywordArgumentFilter evaluates blocks

Overview: Guards against the O(blocks x filesize) blow-up reported in issue #233, where
    KeywordArgumentFilter._is_inside_function_call called ast.parse(file_content) and
    ast.walk(tree) once per candidate keyword-argument-shaped block, re-parsing and re-walking
    the entire file's AST for every such block instead of once per file. Verifies analyze()
    parses a file's AST a single time and also avoids re-walking the whole tree per block, by
    counting ast.parse and ast.walk calls during one analyze() run on an input with many
    qualifying blocks.

Dependencies: pytest, unittest.mock, ast, pathlib.Path, src.linters.dry.config,
    src.linters.dry.python_analyzer

Exports: TestKeywordArgumentFilterParseOnce test class

Interfaces: Tests PythonDuplicateAnalyzer.analyze(file_path, content, config) -> list[CodeBlock]

Implementation: Wraps ast.parse and ast.walk with call counters and asserts each runs a
    constant number of times independent of the number of keyword-argument-shaped candidate
    blocks
"""

import ast
from pathlib import Path
from unittest.mock import patch

from src.linters.dry.config import DRYConfig
from src.linters.dry.python_analyzer import PythonDuplicateAnalyzer

# Enough keyword-shaped attribute groups to generate many rolling-hash windows
# that qualify for KeywordArgumentFilter's expensive AST-containment check.
MANY_KWARG_GROUPS = 50


def _build_kwarg_heavy_source(n: int) -> str:
    """Build Python source with many single-line "key = value" attribute groups.

    Placed after a dummy method so SingleStatementDetector's class-fields-area
    check does not intercept these windows before they reach the block filters
    (each attribute is also single-line, so no Assign node spans a whole window
    either) - matching the "config-dict-heavy module" shape from issue #233's
    real-world repro rather than a single multiline call.
    """
    lines = ["class Config:", "    def _dummy():", "        pass", ""]
    for i in range(n):
        lines.append(f'    message_{i} = "value_{i}"')
        lines.append(f'    severity_{i} = "ERROR"')
        lines.append(f'    suggestion_{i} = "fix_{i}"')
    return "\n".join(lines)


class TestKeywordArgumentFilterParseOnce:
    """KeywordArgumentFilter must not re-parse the whole file's AST per candidate block."""

    def test_analyze_parses_ast_a_constant_number_of_times(self) -> None:
        """analyze() must not re-parse the whole file per keyword-argument block."""
        content = _build_kwarg_heavy_source(MANY_KWARG_GROUPS)
        analyzer = PythonDuplicateAnalyzer()
        config = DRYConfig(enabled=True, min_duplicate_lines=3)

        original_parse = ast.parse
        parse_calls = 0

        def counting(*args, **kwargs):
            nonlocal parse_calls
            parse_calls += 1
            return original_parse(*args, **kwargs)

        with patch("ast.parse", counting):
            analyzer.analyze(Path("big.py"), content, config)

        # A small constant number of parses is expected (cached-AST reuse plus one
        # independent docstring-range scan). The previous code parsed once per
        # qualifying keyword-argument block (dozens here).
        assert parse_calls <= 3, f"expected a constant number of parses, got {parse_calls}"

    def test_analyze_walks_ast_a_constant_number_of_times(self) -> None:
        """analyze() must not re-walk the whole AST tree per keyword-argument block."""
        content = _build_kwarg_heavy_source(MANY_KWARG_GROUPS)
        analyzer = PythonDuplicateAnalyzer()
        config = DRYConfig(enabled=True, min_duplicate_lines=3)

        original_walk = ast.walk
        walk_calls = 0

        def counting(*args, **kwargs):
            nonlocal walk_calls
            walk_calls += 1
            return original_walk(*args, **kwargs)

        with patch("ast.walk", counting):
            analyzer.analyze(Path("big.py"), content, config)

        # A small constant number of full-tree walks is expected (the line-to-node
        # index build plus incidental use elsewhere). The previous code walked the
        # whole tree once per qualifying keyword-argument block (dozens here).
        assert walk_calls <= 3, f"expected a constant number of walks, got {walk_calls}"
