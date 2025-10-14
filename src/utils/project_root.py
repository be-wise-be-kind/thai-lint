"""Project root detection utility.

Purpose: Centralized project root detection for consistent file placement
Scope: Single source of truth for finding project root directory

Overview: Uses pyprojroot package to provide reliable project root detection across
    different environments (development, CI/CD, user installations). Falls back to
    manual detection if pyprojroot is not available (e.g., in test environments).
    Searches for standard project markers like .git, .thailint.yaml, and pyproject.toml.

Dependencies: pyprojroot (optional, with manual fallback)

Exports: is_project_root(), get_project_root()

Interfaces: Path-based functions for checking and finding project roots

Implementation: pyprojroot delegation with manual fallback for test environments
"""

from pathlib import Path

# Try to import pyprojroot, but don't fail if it's not available
try:
    from pyprojroot import find_root

    HAS_PYPROJROOT = True
except ImportError:
    HAS_PYPROJROOT = False


def _has_marker(path: Path, marker_name: str, is_dir: bool = False) -> bool:
    """Check if a directory contains a specific marker.

    Args:
        path: Directory path to check
        marker_name: Name of marker file or directory
        is_dir: True if marker is a directory, False if it's a file

    Returns:
        True if marker exists, False otherwise
    """
    marker_path = path / marker_name
    if is_dir:
        return marker_path.is_dir()
    return marker_path.is_file()


def is_project_root(path: Path) -> bool:
    """Check if a directory is a project root.

    Uses pyprojroot if available, otherwise checks for common project markers
    like .git, .thailint.yaml, or pyproject.toml.

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

    if HAS_PYPROJROOT:
        return _check_root_with_pyprojroot(path)

    return _check_root_with_markers(path)


def _check_root_with_pyprojroot(path: Path) -> bool:
    """Check if path is project root using pyprojroot.

    Args:
        path: Directory path to check

    Returns:
        True if path is a project root, False otherwise
    """
    try:
        # Find root from this path - if it equals this path, it's a root
        found_root = find_root(path)
        return found_root == path.resolve()
    except (OSError, RuntimeError):
        # pyprojroot couldn't find a root
        return False


def _check_root_with_markers(path: Path) -> bool:
    """Check if path contains project root markers.

    Args:
        path: Directory path to check

    Returns:
        True if path contains .git, .thailint.yaml, or pyproject.toml
    """
    return (
        _has_marker(path, ".git", is_dir=True)
        or _has_marker(path, ".thailint.yaml", is_dir=False)
        or _has_marker(path, "pyproject.toml", is_dir=False)
    )


def _try_find_with_criterion(criterion: object, start_path: Path) -> Path | None:
    """Try to find project root with a specific criterion.

    Args:
        criterion: pyprojroot criterion function (e.g., has_dir(".git"))
        start_path: Path to start searching from

    Returns:
        Found project root or None if not found
    """
    try:
        return find_root(criterion, start=start_path)  # type: ignore[arg-type]
    except (OSError, RuntimeError):
        return None


def _find_root_manual(start_path: Path) -> Path:
    """Manually find project root by walking up directory tree.

    Fallback implementation when pyprojroot is not available.

    Args:
        start_path: Directory to start searching from

    Returns:
        Path to project root, or start_path if no markers found
    """
    current = start_path.resolve()

    # Walk up the directory tree
    for parent in [current] + list(current.parents):
        # Check for project markers
        if (
            _has_marker(parent, ".git", is_dir=True)
            or _has_marker(parent, ".thailint.yaml", is_dir=False)
            or _has_marker(parent, "pyproject.toml", is_dir=False)
        ):
            return parent

    # No markers found, return start path
    return current


def get_project_root(start_path: Path | None = None) -> Path:
    """Find project root by walking up the directory tree.

    This is the single source of truth for project root detection.
    All code that needs to find the project root should use this function.

    Uses pyprojroot if available, otherwise uses manual detection searching for
    standard project markers (.git directory, pyproject.toml, .thailint.yaml, etc)
    starting from start_path and walking upward.

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

    if HAS_PYPROJROOT:
        return _find_root_with_pyprojroot(current)

    # Manual fallback for test environments
    return _find_root_manual(current)


def _find_root_with_pyprojroot(current: Path) -> Path:
    """Find project root using pyprojroot library.

    Args:
        current: Current path to start searching from

    Returns:
        Path to project root, or current if no markers found
    """
    from pyprojroot import has_dir, has_file

    # Search for project root markers in priority order
    # Try .git first (most reliable), then .thailint.yaml, then pyproject.toml
    for criterion in [has_dir(".git"), has_file(".thailint.yaml"), has_file("pyproject.toml")]:
        root = _try_find_with_criterion(criterion, current)
        if root is not None:
            return root

    # No markers found, return start path
    return current
