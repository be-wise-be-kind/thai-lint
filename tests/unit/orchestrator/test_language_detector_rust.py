"""
Purpose: Test suite for Rust language detection functionality

Scope: Validation of .rs file detection in the language detector

Overview: Tests the language detection system's ability to identify Rust files by their
    .rs extension. Validates both lowercase and uppercase extension detection to ensure
    the orchestrator can correctly route Rust files to Rust-specific analyzers and rules.
    Complements the existing test_language_detection.py tests for other languages.

Dependencies: pytest for testing framework, pathlib for Path objects

Exports: TestRustLanguageDetection test class

Interfaces: Tests detect_language(file_path: Path) -> str for Rust files

Implementation: Extension-based tests with Path objects, case-insensitivity validation
"""

from pathlib import Path

from src.orchestrator.language_detector import detect_language


class TestRustLanguageDetection:
    """Test Rust file detection."""

    def test_detect_rs_extension(self) -> None:
        """Test .rs files detected as rust."""
        assert detect_language(Path("main.rs")) == "rust"
        assert detect_language(Path("lib.rs")) == "rust"
        assert detect_language(Path("src/module.rs")) == "rust"

    def test_detect_rs_nested_path(self) -> None:
        """Test .rs detection works with nested paths."""
        assert detect_language(Path("src/handlers/auth.rs")) == "rust"
        assert detect_language(Path("crates/my_crate/src/lib.rs")) == "rust"

    def test_detect_rs_case_insensitive(self) -> None:
        """Test .RS extension detected as rust (case insensitive)."""
        assert detect_language(Path("MAIN.RS")) == "rust"
        assert detect_language(Path("file.Rs")) == "rust"

    def test_rust_not_confused_with_similar_extensions(self) -> None:
        """Test that similar extensions are not detected as rust."""
        # .rss is not Rust
        assert detect_language(Path("feed.rss")) != "rust"
        # .rst is not Rust
        assert detect_language(Path("README.rst")) != "rust"
