"""
Purpose: Test suite for Jinja/HTML template language detection functionality

Scope: Validation of .html/.htm/.jinja/.j2 file detection in the language detector

Overview: Tests the language detection system's ability to identify Jinja/HTML template
    files by their extension. Validates .html, .htm, .jinja, and .j2 extensions map to the
    html language, plus case-insensitivity, so the orchestrator can route templates to the
    file header linter's HTML parser. Complements existing language detection tests.

Dependencies: pytest for testing framework, pathlib for Path objects

Exports: TestHtmlLanguageDetection test class

Interfaces: Tests detect_language(file_path: Path) -> str for template files

Implementation: Extension-based tests with Path objects, case-insensitivity validation
"""

from pathlib import Path

from src.orchestrator.language_detector import detect_language


class TestHtmlLanguageDetection:
    """Test Jinja/HTML template file detection."""

    def test_detect_html_extensions(self) -> None:
        """Test .html and .htm files detected as html."""
        assert detect_language(Path("index.html")) == "html"
        assert detect_language(Path("page.htm")) == "html"

    def test_detect_jinja_extensions(self) -> None:
        """Test .jinja and .j2 files detected as html."""
        assert detect_language(Path("page.jinja")) == "html"
        assert detect_language(Path("email.j2")) == "html"

    def test_detect_html_case_insensitive(self) -> None:
        """Test uppercase extensions detected as html (case insensitive)."""
        assert detect_language(Path("INDEX.HTML")) == "html"
        assert detect_language(Path("page.Jinja")) == "html"
