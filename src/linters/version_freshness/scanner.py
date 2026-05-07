"""
Purpose: Scan directories and files to discover and extract version declarations

Scope: File discovery and dispatch to appropriate version extractors

Overview: Walks directory trees to identify target files (Dockerfiles, GitHub Actions
    workflows, version-pinning files, Terraform configs) and dispatches them to the
    appropriate extractor functions. Respects ignore patterns from configuration.

Dependencies: pathlib, fnmatch, extractors module

Exports: scan_directory, scan_file

Interfaces: scan_directory(path, ignore_patterns) -> list[ExtractedVersion],
    scan_file(path) -> list[ExtractedVersion]

Implementation: Filename-based dispatch to extractor functions, recursive directory walking
"""

import logging
from collections.abc import Callable
from pathlib import Path

from src.linters.version_freshness.extractors import (
    extract_from_dockerfile,
    extract_from_github_actions,
    extract_from_mise_toml,
    extract_from_nvmrc,
    extract_from_pyproject_toml,
    extract_from_python_version_file,
    extract_from_terraform,
    extract_from_tool_versions,
)
from src.linters.version_freshness.product_mapper import ExtractedVersion

logger = logging.getLogger(__name__)

Extractor = Callable[[str, str], list[ExtractedVersion]]

# Directories to always skip
_SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".eggs",
    "htmlcov",
    ".thailint-cache",
}


def scan_directory(path: Path, ignore_patterns: list[str] | None = None) -> list[ExtractedVersion]:
    """Scan a directory tree for version declarations.

    Args:
        path: Root directory to scan
        ignore_patterns: File/directory patterns to skip

    Returns:
        List of all extracted versions found
    """
    ignore = ignore_patterns or []
    files = [item for item in _walk_files(path) if not _should_skip_file(item, path, ignore)]

    results: list[ExtractedVersion] = []
    for item in files:
        results.extend(scan_file(item))
    return results


def scan_file(path: Path) -> list[ExtractedVersion]:
    """Scan a single file for version declarations.

    Dispatches to the appropriate extractor based on filename.

    Args:
        path: Path to the file

    Returns:
        List of extracted versions
    """
    extractor = _get_extractor(path)
    if extractor is None:
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        logger.debug("Failed to read %s: %s", path, exc)
        return []

    return extractor(content, str(path))


def _walk_files(path: Path) -> list[Path]:
    """Walk directory tree yielding files, skipping common non-project dirs.

    Args:
        path: Root directory

    Returns:
        List of file paths
    """
    if path.is_file():
        return [path]

    files: list[Path] = []
    try:
        for item in sorted(path.iterdir()):
            files.extend(_collect_entry(item))
    except PermissionError:
        logger.debug("Permission denied: %s", path)
    return files


def _collect_entry(item: Path) -> list[Path]:
    """Collect files from a single directory entry.

    Args:
        item: Path to a file or directory

    Returns:
        List of files (recursively for directories)
    """
    if item.is_dir():
        return _walk_files(item) if item.name not in _SKIP_DIRS else []
    if item.is_file():
        return [item]
    return []


def _should_skip_file(file_path: Path, root: Path, ignore_patterns: list[str]) -> bool:
    """Check if a file should be skipped based on ignore patterns.

    Args:
        file_path: Path to check
        root: Root directory for relative path computation
        ignore_patterns: Glob patterns to match against

    Returns:
        True if file should be skipped
    """
    if not ignore_patterns:
        return False

    from fnmatch import fnmatch

    try:
        relative = str(file_path.relative_to(root))
    except ValueError:
        relative = str(file_path)

    return any(
        fnmatch(relative, pattern) or fnmatch(file_path.name, pattern)
        for pattern in ignore_patterns
    )


_EXACT_NAME_EXTRACTORS: dict[str, Extractor] = {
    ".python-version": extract_from_python_version_file,
    ".nvmrc": extract_from_nvmrc,
    ".node-version": extract_from_nvmrc,
    ".tool-versions": extract_from_tool_versions,
    "mise.toml": extract_from_mise_toml,
    "pyproject.toml": extract_from_pyproject_toml,
}


def _get_extractor(path: Path) -> Extractor | None:
    """Get the appropriate extractor function for a file.

    Args:
        path: Path to the file

    Returns:
        Extractor function, or None if file type is not handled
    """
    name = path.name.lower()

    if name.startswith("dockerfile"):
        return extract_from_dockerfile

    extractor = _EXACT_NAME_EXTRACTORS.get(name)
    if extractor:
        return extractor

    if path.suffix == ".tf":
        return extract_from_terraform

    if _is_github_actions_workflow(path):
        return extract_from_github_actions

    return None


def _is_github_actions_workflow(path: Path) -> bool:
    """Check if a path is a GitHub Actions workflow file.

    Args:
        path: File path to check

    Returns:
        True if file is under .github/workflows/ and is a YAML file
    """
    parts = path.parts
    if path.suffix not in (".yml", ".yaml"):
        return False
    return ".github" in parts and "workflows" in parts
