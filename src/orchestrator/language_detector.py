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


def detect_language(file_path: Path) -> str:
    """Detect programming language from file.

    Args:
        file_path: Path to file to analyze.

    Returns:
        Language identifier (python, javascript, typescript, java, go, unknown).
    """
    # Check extension first (fast path)
    ext = file_path.suffix.lower()
    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]

    # Check shebang for scripts without extension
    if file_path.exists() and file_path.stat().st_size > 0:
        try:
            first_line = file_path.read_text(encoding="utf-8").split("\n")[0]
            if first_line.startswith("#!"):
                if "python" in first_line:
                    return "python"
                # Add more shebang detections as needed
        except (UnicodeDecodeError, OSError):
            pass

    return "unknown"
