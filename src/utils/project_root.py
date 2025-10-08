"""Project root detection utility.

Purpose: Centralized project root detection for consistent file placement
Scope: Single source of truth for finding project root directory
"""

from pathlib import Path


def is_project_root(path: Path) -> bool:
    """Check if a directory is a project root.

    A directory is considered a project root if it contains:
    - .git directory (Git repository)
    - pyproject.toml file (Python project)

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

    return (path / ".git").exists() or (path / "pyproject.toml").exists()


def get_project_root(start_path: Path | None = None) -> Path:
    """Find project root by walking up the directory tree.

    This is the single source of truth for project root detection.
    All code that needs to find the project root should use this function.

    Args:
        start_path: Directory to start searching from. If None, uses current working directory.

    Returns:
        Path to project root directory. If no root markers found, returns the start_path.

    Examples:
        >>> root = get_project_root()
        >>> config_file = root / ".artifacts" / "generated-config.yaml"
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Walk up the directory tree looking for project markers
    while current != current.parent:  # Stop at filesystem root
        if is_project_root(current):
            return current
        current = current.parent

    # No project markers found, use the start path
    return start_path.resolve()
