"""
Purpose: Programming language detection from file extensions and content

Scope: Language identification for routing files to appropriate analyzers and rules

Overview: Detects programming language from files using multiple strategies including file
    extension mapping, shebang line parsing for scripts, and content analysis. Provides simple
    extension-to-language mapping for common file types (.py -> python, .js -> javascript,
    .ts -> typescript, .java -> java, .go -> go). Falls back to shebang parsing for extensionless
    scripts by reading first line and checking for language indicators. Returns 'unknown' for
    unrecognized files, allowing the orchestrator to skip or apply language-agnostic rules.
    Enables the multi-language architecture by accurately identifying file types for proper
    rule routing and analyzer selection.

Dependencies: pathlib for file path handling and content reading

Exports: detect_language(file_path: Path) -> str function, EXTENSION_MAP constant

Interfaces: detect_language(file_path: Path) -> str returns language identifier string
    (python, javascript, typescript, java, go, unknown)

Implementation: Dictionary-based extension lookup for O(1) detection, first-line shebang
    parsing with substring matching, lazy file reading only when extension unknown
"""

from pathlib import Path

# Extension to language mapping
EXTENSION_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".java": "java",
    ".go": "go",
}


def _detect_from_shebang(file_path: Path) -> str | None:
    """Detect language from shebang line."""
    try:
        first_line = _read_first_line(file_path)
        return _parse_shebang_language(first_line)
    except (UnicodeDecodeError, OSError):
        return None


def _read_first_line(file_path: Path) -> str:
    """Read the first line from a file."""
    return file_path.read_text(encoding="utf-8").split("\n")[0]


def _parse_shebang_language(line: str) -> str | None:
    """Parse language from shebang line."""
    if not line.startswith("#!"):
        return None
    if "python" in line:
        return "python"
    return None


def detect_language(file_path: Path) -> str:
    """Detect programming language from file.

    Args:
        file_path: Path to file to analyze.

    Returns:
        Language identifier (python, javascript, typescript, java, go, unknown).
    """
    ext = file_path.suffix.lower()
    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]

    if file_path.exists() and file_path.stat().st_size > 0:
        lang = _detect_from_shebang(file_path)
        if lang:
            return lang

    return "unknown"
