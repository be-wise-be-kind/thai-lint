"""Project root detection utility.

Purpose: Centralized project root detection for consistent file placement
Scope: Single source of truth for finding project root directory

Overview: Uses pyprojroot package to provide reliable project root detection across
    different environments (development, CI/CD, user installations). Delegates all
    project root detection logic to the industry-standard pyprojroot library which
    handles various project markers and edge cases that we cannot anticipate.

Dependencies: pyprojroot for robust project root detection

Exports: is_project_root(), get_project_root()

Interfaces: Path-based functions for checking and finding project roots

Implementation: Pure delegation to pyprojroot with fallback to start_path when no root found
"""

from pathlib import Path

from pyprojroot import find_root


def is_project_root(path: Path) -> bool:
    """Check if a directory is a project root.

    Uses pyprojroot to detect if the given path is a project root by checking
    if finding the root from this path returns the same path.

    Args:
        path: Directory path to check

    Returns:
        True if the directory is a project root, False otherwise

    Examples:
        >>> is_project_root(Path("/home/user/myproject"))
        True
        >>> is_project_root(Path("/home/user/myproject/src"))
        False
    """
    if not path.exists() or not path.is_dir():
        return False

    try:
        # Find root from this path - if it equals this path, it's a root
        found_root = find_root(path)
        return found_root == path.resolve()
    except (OSError, RuntimeError):
        # pyprojroot couldn't find a root
        return False


def get_project_root(start_path: Path | None = None) -> Path:
    """Find project root by walking up the directory tree.

    This is the single source of truth for project root detection.
    All code that needs to find the project root should use this function.

    Uses pyprojroot which searches for standard project markers defined by the
    pyprojroot library (git repos, Python projects, etc).

    Args:
        start_path: Directory to start searching from. If None, uses current working directory.

    Returns:
        Path to project root directory. If no root markers found, returns the start_path.

    Examples:
        >>> root = get_project_root()
        >>> config_file = root / ".thailint.yaml"
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    try:
        # Use pyprojroot to find the project root
        return find_root(current)
    except (OSError, RuntimeError):
        # No project markers found, return the start path
        return current
