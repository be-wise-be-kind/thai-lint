"""
Purpose: Test suite for RustBaseAnalyzer tree-sitter parsing functionality

Scope: Validation of Rust AST parsing, tree walking, and Rust-specific utilities

Overview: Tests the RustBaseAnalyzer class which provides tree-sitter parsing infrastructure
    for Rust code. Validates initialization, parsing behavior with and without tree-sitter-rust
    installed, tree walking to find specific node types, text extraction from nodes, and
    Rust-specific utilities like test detection and async function detection. Uses skipif
    markers for tests that require tree-sitter-rust to be installed.

Dependencies: pytest for testing framework, src.analyzers.rust_base module

Exports: TestRustBaseAnalyzer test class

Interfaces: Tests parse_rust(code), walk_tree(node, type), extract_node_text(node),
    is_inside_test(node), is_async_function(node)

Implementation: Unit tests with fixture code samples, skipif for optional dependency tests
"""

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE, RustBaseAnalyzer


class TestRustBaseAnalyzer:
    """Test suite for RustBaseAnalyzer."""

    def test_init(self) -> None:
        """Test analyzer initialization tracks tree-sitter availability."""
        analyzer = RustBaseAnalyzer()
        assert analyzer.tree_sitter_available == TREE_SITTER_RUST_AVAILABLE

    @pytest.mark.skipif(not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed")
    def test_parse_rust_simple(self) -> None:
        """Test parsing simple Rust code returns AST root."""
        analyzer = RustBaseAnalyzer()
        code = 'fn main() { println!("Hello"); }'
        node = analyzer.parse_rust(code)
        assert node is not None
        assert node.type == "source_file"

    @pytest.mark.skipif(not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed")
    def test_walk_tree_finds_functions(self) -> None:
        """Test walking tree to find function items."""
        analyzer = RustBaseAnalyzer()
        code = """
        fn foo() {}
        fn bar() {}
        fn baz() {}
        """
        node = analyzer.parse_rust(code)
        functions = analyzer.walk_tree(node, "function_item")
        assert len(functions) == 3

    @pytest.mark.skipif(not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed")
    def test_extract_node_text(self) -> None:
        """Test extracting text content from a node."""
        analyzer = RustBaseAnalyzer()
        code = "fn hello() {}"
        node = analyzer.parse_rust(code)
        functions = analyzer.walk_tree(node, "function_item")
        assert len(functions) == 1
        text = analyzer.extract_node_text(functions[0])
        assert "fn hello()" in text

    @pytest.mark.skipif(not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed")
    def test_extract_identifier_name(self) -> None:
        """Test extracting identifier name from function node."""
        analyzer = RustBaseAnalyzer()
        code = "fn my_function() {}"
        node = analyzer.parse_rust(code)
        functions = analyzer.walk_tree(node, "function_item")
        assert len(functions) == 1
        name = analyzer.extract_identifier_name(functions[0])
        assert name == "my_function"

    @pytest.mark.skipif(not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed")
    def test_is_async_function_detects_async(self) -> None:
        """Test detection of async functions."""
        analyzer = RustBaseAnalyzer()
        code = """
        async fn async_func() {}
        fn sync_func() {}
        """
        node = analyzer.parse_rust(code)
        functions = analyzer.walk_tree(node, "function_item")
        assert len(functions) == 2

        # Find async and sync functions by name
        async_fn = None
        sync_fn = None
        for fn in functions:
            name = analyzer.extract_identifier_name(fn)
            if name == "async_func":
                async_fn = fn
            elif name == "sync_func":
                sync_fn = fn

        assert async_fn is not None
        assert sync_fn is not None
        assert analyzer.is_async_function(async_fn) is True
        assert analyzer.is_async_function(sync_fn) is False

    def test_parse_rust_without_tree_sitter(self) -> None:
        """Test graceful handling when tree-sitter-rust not available."""
        analyzer = RustBaseAnalyzer()
        if not TREE_SITTER_RUST_AVAILABLE:
            result = analyzer.parse_rust("fn main() {}")
            assert result is None

    def test_walk_tree_with_none_node(self) -> None:
        """Test walk_tree returns empty list for None node."""
        analyzer = RustBaseAnalyzer()
        result = analyzer.walk_tree(None, "function_item")
        assert result == []


class TestRustTestDetection:
    """Test suite for Rust test detection utilities."""

    @pytest.mark.skipif(not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed")
    def test_is_inside_test_detects_test_attribute(self) -> None:
        """Test detection of #[test] attribute on functions."""
        analyzer = RustBaseAnalyzer()
        code = """
        #[test]
        fn test_something() {
            assert!(true);
        }

        fn regular_function() {
            assert!(true);
        }
        """
        node = analyzer.parse_rust(code)
        functions = analyzer.walk_tree(node, "function_item")

        # Find test and regular functions
        test_fn = None
        regular_fn = None
        for fn in functions:
            name = analyzer.extract_identifier_name(fn)
            if name == "test_something":
                test_fn = fn
            elif name == "regular_function":
                regular_fn = fn

        assert test_fn is not None
        assert regular_fn is not None
        # The function itself should be detected as being inside a test
        assert analyzer.is_inside_test(test_fn) is True
        assert analyzer.is_inside_test(regular_fn) is False
