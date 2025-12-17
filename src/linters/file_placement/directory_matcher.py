"""
Purpose: Directory rule matching for file placement linter

Scope: Finds most specific directory rule matching a file path

Overview: Provides directory matching functionality for the file placement linter. Implements
    most-specific-directory matching logic by comparing path prefixes and calculating directory
    depth. Handles special case of root directory matching. Returns matched rule and path for
    further processing. Isolates directory matching logic from rule checking and pattern matching.

Dependencies: typing

Exports: DirectoryMatcher

Interfaces: find_matching_rule(path_str, directories) -> (rule_dict, matched_path)

Implementation: Prefix matching with depth-based precedence, root directory special case
"""

from typing import Any


class DirectoryMatcher:
    """Finds matching directory rules based on path prefixes."""

    def __init__(self) -> None:
        """Initialize the directory matcher."""
        pass  # Stateless matcher for directory rules

    def find_matching_rule(
        self, path_str: str, directories: dict[str, Any]
    ) -> tuple[dict[str, Any] | None, str | None]:
        """Find most specific directory rule matching the path.

        Args:
            path_str: File path string
            directories: Directory rules

        Returns:
            Tuple of (rule_dict, matched_path)
        """
        best_match = None
        best_path = None
        best_depth = -1

        for dir_path, rules in directories.items():
            matches, depth = self._check_path_match(dir_path, path_str)
            if matches and depth > best_depth:
                best_match = rules
                best_path = dir_path
                best_depth = depth

        return best_match, best_path

    def _check_path_match(self, dir_path: str, path_str: str) -> tuple[bool, int]:
        """Check if path matches directory rule.

        Args:
            dir_path: Directory path pattern
            path_str: File path string

        Returns:
            Tuple of (matches, depth) where depth is directory nesting level
        """
        if dir_path == "/":
            return self._check_root_match(dir_path, path_str)
        if path_str.startswith(dir_path):
            depth = len(dir_path.split("/"))
            return True, depth
        return False, -1

    def _check_root_match(self, dir_path: str, path_str: str) -> tuple[bool, int]:
        """Check if path matches root directory rule.

        Args:
            dir_path: Directory path (should be "/")
            path_str: File path string

        Returns:
            Tuple of (matches, depth)
        """
        if dir_path == "/" and "/" not in path_str:
            return True, 0
        return False, -1
