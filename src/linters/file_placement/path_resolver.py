"""
Purpose: Path resolution and normalization for file placement linter

Scope: Handles path operations including relative path calculation and normalization

Overview: Provides path resolution utilities for the file placement linter. Converts
    absolute paths to paths relative to project root, normalizes path separators for
    cross-platform compatibility, and handles edge cases like paths outside project root.
    Isolates path manipulation logic from rule checking and pattern matching.

Dependencies: pathlib

Exports: PathResolver

Interfaces: get_relative_path(file_path) -> Path, normalize_path_string(path) -> str

Implementation: Uses pathlib for robust path operations, handles ValueError for out-of-tree paths
"""

from pathlib import Path


class PathResolver:
    """Resolves and normalizes file paths for file placement linter."""

    def __init__(self, project_root: Path):
        """Initialize path resolver.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root

    def get_relative_path(self, file_path: Path) -> Path:
        """Get path relative to project root.

        Args:
            file_path: File path to convert

        Returns:
            Path relative to project root, or original path if outside project
        """
        try:
            if file_path.is_absolute():
                return file_path.relative_to(self.project_root)
            return file_path
        except ValueError:
            # If path is outside project root, return it as-is
            # This allows detection of absolute paths in global_deny patterns
            return file_path

    def normalize_path_string(self, path: Path) -> str:
        """Normalize path to forward slashes for cross-platform consistency.

        Args:
            path: Path to normalize

        Returns:
            Path string with forward slashes
        """
        return str(path).replace("\\", "/")
