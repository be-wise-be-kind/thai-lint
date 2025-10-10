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
