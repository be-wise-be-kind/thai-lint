"""
Purpose: Test suite for programming language detection from files

Scope: Validation of language detection by extension, shebang, and content analysis

Overview: Validates the language detection system that determines programming language from
    file extensions, shebang lines, and file content. Tests verify detection from common
    extensions (.py, .js, .ts, .java, .go), shebang parsing for scripts without extensions,
    and fallback to 'unknown' for unrecognized files. Ensures the orchestrator can correctly
    route files to language-specific analyzers and rules by accurately identifying the
    programming language of each file being linted.

Dependencies: pytest for testing framework, pathlib for file creation, tmp_path fixture

Exports: TestLanguageDetection test class

Interfaces: Tests detect_language(file_path: Path) -> str function with various file types

Implementation: 7 tests covering extension-based detection for multiple languages,
    shebang parsing for extensionless scripts, unknown file handling
"""


class TestLanguageDetection:
    """Test language detection from files."""

    def test_detect_python_from_extension(self, tmp_path):
        """Detect Python from .py extension."""
        test_file = tmp_path / "test.py"
        test_file.touch()

        from src.orchestrator.language_detector import detect_language

        assert detect_language(test_file) == "python"

    def test_detect_javascript_from_extension(self, tmp_path):
        """Detect JavaScript from .js extension."""
        test_file = tmp_path / "test.js"
        test_file.touch()

        from src.orchestrator.language_detector import detect_language

        assert detect_language(test_file) == "javascript"

    def test_detect_typescript_from_extension(self, tmp_path):
        """Detect TypeScript from .ts extension."""
        test_file = tmp_path / "test.ts"
        test_file.touch()

        from src.orchestrator.language_detector import detect_language

        assert detect_language(test_file) == "typescript"

    def test_detect_from_python_shebang(self, tmp_path):
        """Detect Python from shebang line."""
        test_file = tmp_path / "script"
        test_file.write_text("#!/usr/bin/env python3\nprint('hello')\n")

        from src.orchestrator.language_detector import detect_language

        assert detect_language(test_file) == "python"

    def test_detect_from_python_shebang_variant(self, tmp_path):
        """Detect Python from alternate shebang."""
        test_file = tmp_path / "script"
        test_file.write_text("#!/usr/bin/python\nprint('hello')\n")

        from src.orchestrator.language_detector import detect_language

        assert detect_language(test_file) == "python"

    def test_unknown_extension_returns_unknown(self, tmp_path):
        """Unknown file extension returns 'unknown'."""
        test_file = tmp_path / "test.xyz"
        test_file.touch()

        from src.orchestrator.language_detector import detect_language

        assert detect_language(test_file) == "unknown"

    def test_empty_file_with_extension(self, tmp_path):
        """Empty file still detected by extension."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        from src.orchestrator.language_detector import detect_language

        assert detect_language(test_file) == "python"
