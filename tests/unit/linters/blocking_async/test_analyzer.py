"""
Purpose: Unit tests for RustBlockingAsyncAnalyzer detection logic

Scope: Tests for fs-in-async, sleep-in-async, and net-in-async pattern detection

Overview: Comprehensive test suite for the RustBlockingAsyncAnalyzer class covering all three
    detection categories: filesystem operations (std::fs::*) in async functions, thread sleep
    (std::thread::sleep) in async functions, and blocking network calls (std::net::*) in async
    functions. Validates line/column info, test-awareness, context extraction, short path
    detection, edge cases, and negative cases (sync functions not flagged, tokio equivalents
    not flagged).

Dependencies: pytest, src.analyzers.rust_base, src.linters.blocking_async.rust_analyzer

Exports: Test classes for each detection pattern and edge case category

Interfaces: Standard pytest test classes

Implementation: Direct analyzer instantiation with sample Rust code strings
"""

import pytest

from src.analyzers.rust_base import TREE_SITTER_RUST_AVAILABLE
from src.linters.blocking_async.rust_analyzer import RustBlockingAsyncAnalyzer

pytestmark = pytest.mark.skipif(
    not TREE_SITTER_RUST_AVAILABLE, reason="tree-sitter-rust not installed"
)


class TestFsInAsyncDetection:
    """Tests for filesystem blocking call detection in async functions."""

    def test_detects_fs_read_to_string_in_async(self) -> None:
        """Should detect std::fs::read_to_string inside async fn."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        fs_calls = [c for c in calls if c.pattern == "fs-in-async"]
        assert len(fs_calls) == 1

    def test_detects_fs_write_in_async(self) -> None:
        """Should detect std::fs::write inside async fn."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn write_file() {
    std::fs::write("output.txt", "data").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        fs_calls = [c for c in calls if c.pattern == "fs-in-async"]
        assert len(fs_calls) == 1

    def test_detects_short_path_fs_in_async(self) -> None:
        """Should detect fs::read_to_string (short path) inside async fn."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
use std::fs;

async fn read_file() {
    let content = fs::read_to_string("file.txt").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        fs_calls = [c for c in calls if c.pattern == "fs-in-async"]
        assert len(fs_calls) == 1

    def test_no_flag_fs_in_sync_function(self) -> None:
        """Should not flag std::fs calls in sync functions."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) == 0

    def test_no_flag_tokio_fs_in_async(self) -> None:
        """Should not flag tokio::fs calls in async functions."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn read_file() {
    let content = tokio::fs::read_to_string("file.txt").await.unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) == 0

    def test_detects_fs_metadata_in_async(self) -> None:
        """Should detect std::fs::metadata inside async fn."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn check_file() {
    let meta = std::fs::metadata("file.txt").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        fs_calls = [c for c in calls if c.pattern == "fs-in-async"]
        assert len(fs_calls) == 1

    def test_blocking_api_field_contains_path(self) -> None:
        """Should populate blocking_api field with the call path."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) >= 1
        assert "std::fs::read_to_string" in calls[0].blocking_api


class TestSleepInAsyncDetection:
    """Tests for std::thread::sleep detection in async functions."""

    def test_detects_thread_sleep_in_async(self) -> None:
        """Should detect std::thread::sleep inside async fn."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn slow_function() {
    std::thread::sleep(std::time::Duration::from_secs(1));
}
"""
        calls = analyzer.find_blocking_calls(code)
        sleep_calls = [c for c in calls if c.pattern == "sleep-in-async"]
        assert len(sleep_calls) == 1

    def test_detects_short_path_sleep_in_async(self) -> None:
        """Should detect thread::sleep (short path) inside async fn."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
use std::thread;

async fn slow_function() {
    thread::sleep(std::time::Duration::from_secs(1));
}
"""
        calls = analyzer.find_blocking_calls(code)
        sleep_calls = [c for c in calls if c.pattern == "sleep-in-async"]
        assert len(sleep_calls) == 1

    def test_no_flag_sleep_in_sync_function(self) -> None:
        """Should not flag std::thread::sleep in sync functions."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
fn slow_function() {
    std::thread::sleep(std::time::Duration::from_secs(1));
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) == 0

    def test_no_flag_tokio_sleep_in_async(self) -> None:
        """Should not flag tokio::time::sleep in async functions."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn wait() {
    tokio::time::sleep(std::time::Duration::from_secs(1)).await;
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) == 0


class TestNetInAsyncDetection:
    """Tests for blocking network call detection in async functions."""

    def test_detects_tcp_stream_connect_in_async(self) -> None:
        """Should detect std::net::TcpStream::connect inside async fn."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn connect() {
    let stream = std::net::TcpStream::connect("127.0.0.1:8080").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        net_calls = [c for c in calls if c.pattern == "net-in-async"]
        assert len(net_calls) == 1

    def test_detects_tcp_listener_bind_in_async(self) -> None:
        """Should detect std::net::TcpListener::bind inside async fn."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn listen() {
    let listener = std::net::TcpListener::bind("127.0.0.1:8080").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        net_calls = [c for c in calls if c.pattern == "net-in-async"]
        assert len(net_calls) == 1

    def test_detects_udp_socket_bind_in_async(self) -> None:
        """Should detect std::net::UdpSocket::bind inside async fn."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn bind_udp() {
    let socket = std::net::UdpSocket::bind("127.0.0.1:0").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        net_calls = [c for c in calls if c.pattern == "net-in-async"]
        assert len(net_calls) == 1

    def test_no_flag_net_in_sync_function(self) -> None:
        """Should not flag std::net calls in sync functions."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
fn connect() {
    let stream = std::net::TcpStream::connect("127.0.0.1:8080").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) == 0


class TestBlockingAsyncLineInfo:
    """Tests for correct line and column reporting."""

    def test_correct_line_for_blocking_call(self) -> None:
        """Should report the correct line number for blocking call."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """async fn read_file() {
    let x = "preamble";
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) >= 1
        assert calls[0].line == 3

    def test_correct_column_is_non_negative(self) -> None:
        """Should report a non-negative column number."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) >= 1
        assert calls[0].column >= 0


class TestBlockingAsyncTestAwareness:
    """Tests for test code detection."""

    def test_detects_blocking_in_test_function(self) -> None:
        """Should mark blocking calls inside a #[test] function as test code."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
#[test]
async fn test_read() {
    let content = std::fs::read_to_string("test.txt").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) >= 1
        assert all(c.is_in_test for c in calls)

    def test_detects_blocking_in_cfg_test(self) -> None:
        """Should mark blocking calls inside a #[cfg(test)] module as test code."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
#[cfg(test)]
mod tests {
    async fn test_helper() {
        let content = std::fs::read_to_string("test.txt").unwrap();
    }
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) >= 1
        assert all(c.is_in_test for c in calls)

    def test_non_test_code_not_marked(self) -> None:
        """Should not mark blocking calls in non-test code as test code."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) >= 1
        assert all(not c.is_in_test for c in calls)


class TestBlockingAsyncContext:
    """Tests for code context extraction."""

    def test_extracts_context_line(self) -> None:
        """Should extract a context line containing the blocking call."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn read_file() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) >= 1
        assert "read_to_string" in calls[0].context


class TestBlockingAsyncEdgeCases:
    """Tests for edge cases."""

    def test_empty_code(self) -> None:
        """Should return no findings for empty code input."""
        analyzer = RustBlockingAsyncAnalyzer()
        calls = analyzer.find_blocking_calls("")
        assert len(calls) == 0

    def test_no_blocking_calls(self) -> None:
        """Should return no findings when code contains no blocking calls."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn process(data: &str) {
    let result = data.to_uppercase();
    println!("{}", result);
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) == 0

    def test_empty_async_function(self) -> None:
        """Should return no findings for empty async function."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn noop() {}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) == 0

    def test_blocking_without_tree_sitter(self) -> None:
        """Should return no findings when tree-sitter is unavailable."""
        analyzer = RustBlockingAsyncAnalyzer()
        original = analyzer.tree_sitter_available
        analyzer.tree_sitter_available = False
        calls = analyzer.find_blocking_calls('async fn read() { std::fs::read_to_string("f"); }')
        assert len(calls) == 0
        analyzer.tree_sitter_available = original

    def test_multiple_patterns_detected(self) -> None:
        """Should detect multiple distinct patterns in the same async function."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
async fn do_stuff() {
    let content = std::fs::read_to_string("file.txt").unwrap();
    std::thread::sleep(std::time::Duration::from_secs(1));
}
"""
        calls = analyzer.find_blocking_calls(code)
        patterns = {c.pattern for c in calls}
        assert "fs-in-async" in patterns
        assert "sleep-in-async" in patterns

    def test_mixed_async_and_sync_functions(self) -> None:
        """Should only flag blocking calls in async functions, not sync."""
        analyzer = RustBlockingAsyncAnalyzer()
        code = """
fn sync_read() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}

async fn async_read() {
    let content = std::fs::read_to_string("file.txt").unwrap();
}
"""
        calls = analyzer.find_blocking_calls(code)
        assert len(calls) == 1
        assert calls[0].pattern == "fs-in-async"
