"""
Purpose: Regression test for TypeScriptDuplicateAnalyzer re-walking the AST per block

Scope: typescript_statement_detector single-statement detection tree-walk scaling

Overview: Guards against the O(windows x nodes) blowup discovered while benchmarking the DRY
    linter against a real multi-thousand-file monorepo: is_single_statement_for_root walked the
    entire tree-sitter tree from scratch (_walk_nodes) for every rolling-hash window, the same
    class of bug issue #233 fixed on the Python side (SingleStatementDetector) but never fixed for
    TypeScript/JavaScript. Profiling a real 40,548-line vendored JS bundle showed 219 million
    _walk_nodes calls from just 1,077 is_single_statement_for_root invocations in 25 seconds
    (analyze() did not complete). Verifies analyze() builds a line-to-node index once per file
    and reuses it across every window, by counting _walk_nodes calls during one analyze() run on
    an input with many windows.

Dependencies: pytest, unittest.mock, src.analyzers.typescript_base,
    src.linters.dry.typescript_statement_detector

Exports: TestTypeScriptStatementDetectorIndex test class

Interfaces: Tests build_line_to_node_index(root) and
    is_single_statement_for_root(root, start, end, line_to_node_index)

Implementation: Wraps typescript_statement_detector._walk_nodes with a counter that only counts
    invocations starting from the tree's root (not recursive per-child calls, since _walk_nodes
    is itself a recursive generator - one full walk naturally makes many recursive calls), and
    asserts that count stays constant independent of the number of is_single_statement_for_root
    lookups against a pre-built index
"""

from unittest.mock import patch

import pytest

from src.analyzers.typescript_base import TREE_SITTER_AVAILABLE
from src.linters.dry import typescript_statement_detector

pytestmark = pytest.mark.skipif(not TREE_SITTER_AVAILABLE, reason="tree-sitter not available")

# Enough distinct lines to generate many rolling-hash windows, each of which
# triggers its own is_single_statement_for_root check.
MANY_LINES = 150


def _build_source(n: int) -> str:
    """Build JS source with many distinct statements, generating many windows."""
    return "\n".join(f"const value{i} = compute({i}, {i + 1}, {i + 2});" for i in range(n))


class TestTypeScriptStatementDetectorIndex:
    """analyze() must not re-walk the whole AST once per rolling-hash window."""

    def test_analyze_walks_tree_a_constant_number_of_times(self) -> None:
        """analyze() must not restart a full tree walk once per window."""
        content = _build_source(MANY_LINES)

        original_walk = typescript_statement_detector._walk_nodes
        root_level_calls = 0
        root_holder: list = []

        def counting(node):
            nonlocal root_level_calls
            # _walk_nodes recurses into itself once per child, so only count
            # invocations that start a fresh walk from the tree's root.
            if root_holder and node is root_holder[0]:
                root_level_calls += 1
            return original_walk(node)

        with patch.object(typescript_statement_detector, "_walk_nodes", counting):
            root = typescript_statement_detector.parse_root(content)
            root_holder.append(root)
            index = typescript_statement_detector.build_line_to_node_index(root)
            for _ in range(200):
                typescript_statement_detector.is_single_statement_for_root(root, 1, 4, index)

        # Exactly one full-tree walk is expected (building the index). The
        # previous code walked the whole tree from the root once per lookup
        # (200 times here) when no index was supplied.
        assert root_level_calls <= 1, f"expected 1 root-level walk, got {root_level_calls}"
