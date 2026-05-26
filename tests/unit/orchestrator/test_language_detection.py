"""
Purpose: Test suite for programming language detection from files

Scope: Validation of language detection by extension, shebang, and content analysis

Overview: Validates the language detection system that determines programming language from
    file extensions. Tests verify detection of the file-header supported extensions that the
    orchestrator must route to language-specific parsers (.md -> markdown, .sh/.bash -> bash,
    .css/.scss -> css), including case-insensitive matching. Ensures the orchestrator can
    correctly route these files to language-specific analyzers and rules by accurately
    identifying the programming language of each file being linted.

Dependencies: pytest for testing framework, pathlib for Path objects

Exports: TestLanguageDetection test class

Interfaces: Tests detect_language(file_path: Path) -> str function with various file types

Implementation: Extension-based detection tests for markdown, bash, and css file types,
    plus case-insensitive matching
"""

from pathlib import Path

from src.orchestrator.language_detector import detect_language


class TestLanguageDetection:
    """Test language detection from files."""

    def test_detect_markdown_extension(self) -> None:
        """Test .md files detected as markdown."""
        assert detect_language(Path("README.md")) == "markdown"
        assert detect_language(Path("docs/guide.md")) == "markdown"

    def test_detect_markdown_case_insensitive(self) -> None:
        """Test .MD extension detected as markdown (case insensitive)."""
        assert detect_language(Path("README.MD")) == "markdown"

    def test_detect_bash_extension(self) -> None:
        """Test .sh and .bash files detected as bash."""
        assert detect_language(Path("deploy.sh")) == "bash"
        assert detect_language(Path("setup.bash")) == "bash"

    def test_detect_css_extension(self) -> None:
        """Test .css and .scss files detected as css."""
        assert detect_language(Path("styles.css")) == "css"
        assert detect_language(Path("theme.scss")) == "css"
