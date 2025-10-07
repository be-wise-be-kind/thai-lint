"""
Purpose: Comprehensive 5-level ignore directive parser for suppressing linting violations

Scope: Multi-level ignore system across repository, directory, file, method, and line scopes

Overview: Implements a sophisticated ignore directive system that allows developers to suppress
    linting violations at five different granularity levels, from entire repository patterns down
    to individual lines of code. Repository level uses .thailintignore file with gitignore-style
    glob patterns for excluding files like build artifacts and dependencies. File level scans the
    first 10 lines for ignore-file directives (performance optimization). Method level supports
    ignore-next-line directives placed before functions. Line level enables inline ignore comments
    at the end of code lines. All levels support rule-specific ignores using bracket syntax
    [rule-id] and wildcard rule matching (literals.* matches literals.magic-number). The
    should_ignore_violation() method provides unified checking across all levels, integrating
    with the violation reporting system to filter out suppressed violations before displaying
    results to users.

Dependencies: fnmatch for gitignore-style pattern matching, re for regex-based directive parsing,
    pathlib for file operations, Violation type for violation checking

Exports: IgnoreDirectiveParser class

Interfaces: is_ignored(file_path: Path) -> bool for repo-level checking,
    has_file_ignore(file_path: Path, rule_id: str | None) -> bool for file-level,
    has_line_ignore(code: str, line_num: int, rule_id: str | None) -> bool for line-level,
    should_ignore_violation(violation: Violation, file_content: str) -> bool for unified checking

Implementation: Gitignore-style pattern matching with fnmatch, first-10-lines scanning for
    performance, regex-based directive parsing with rule ID extraction, wildcard rule matching
    with prefix comparison, graceful error handling for malformed directives
"""
import fnmatch
import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.types import Violation


class IgnoreDirectiveParser:
    """Parse and check ignore directives at all 5 levels.

    Provides comprehensive ignore checking for repository-level patterns,
    file-level directives, and inline code comments.
    """

    def __init__(self, project_root: Path | None = None):
        """Initialize parser.

        Args:
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.project_root = project_root or Path.cwd()
        self.repo_patterns = self._load_repo_ignores()

    def _load_repo_ignores(self) -> list[str]:
        """Load .thailintignore file patterns.

        Returns:
            List of gitignore-style patterns.
        """
        ignore_file = self.project_root / ".thailintignore"
        if not ignore_file.exists():
            return []

        patterns = []
        for line in ignore_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            # Skip comments and blank lines
            if line and not line.startswith("#"):
                patterns.append(line)
        return patterns

    def is_ignored(self, file_path: Path) -> bool:
        """Check if file matches repository-level ignore patterns.

        Args:
            file_path: Path to check against ignore patterns.

        Returns:
            True if file should be ignored.
        """
        # Convert to string relative to project root if possible
        try:
            relative_path = file_path.relative_to(self.project_root)
            path_str = str(relative_path)
        except ValueError:
            # Path is not relative to project root
            path_str = str(file_path)

        for pattern in self.repo_patterns:
            if self._matches_pattern(path_str, pattern):
                return True
        return False

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches gitignore-style pattern.

        Args:
            path: File path to check.
            pattern: Gitignore-style pattern.

        Returns:
            True if path matches pattern.
        """
        # Handle directory patterns (trailing /)
        if pattern.endswith("/"):
            # Match directory and all its contents
            dir_pattern = pattern.rstrip("/")
            # Check if path starts with the directory
            path_parts = Path(path).parts
            if dir_pattern in path_parts:
                return True
            # Also check direct match
            if fnmatch.fnmatch(path, dir_pattern + "*"):
                return True

        # Standard fnmatch for file patterns
        return fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(str(Path(path)), pattern)

    def has_file_ignore(self, file_path: Path, rule_id: str | None = None) -> bool:
        """Check for file-level ignore directive.

        Scans the first 10 lines of the file for ignore directives.

        Args:
            file_path: Path to file to check.
            rule_id: Optional specific rule ID to check for.

        Returns:
            True if file has ignore directive (general or for specific rule).
        """
        if not file_path.exists():
            return False

        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return False

        first_lines = content.splitlines()[:10]  # Only scan first 10 lines

        for line in first_lines:
            if "# thailint: ignore-file" in line or "# design-lint: ignore-file" in line:
                if rule_id:
                    # Check for specific rule ignore
                    match = re.search(r"ignore-file\[([^\]]+)\]", line)
                    if match:
                        ignored_rules = [r.strip() for r in match.group(1).split(",")]
                        if any(self._rule_matches(rule_id, r) for r in ignored_rules):
                            return True
                    else:
                        # No specific rules, so doesn't apply
                        continue
                else:
                    # General ignore-file (no brackets)
                    if "ignore-file[" not in line:
                        return True

        return False

    def has_line_ignore(self, code: str, line_num: int, rule_id: str | None = None) -> bool:
        """Check for line-level ignore directive.

        Args:
            code: Line of code to check.
            line_num: Line number (currently unused, for API compatibility).
            rule_id: Optional specific rule ID to check for.

        Returns:
            True if line has ignore directive.
        """
        # Check for ignore directive in the line
        if "# thailint: ignore" not in code and "# design-lint: ignore" not in code:
            return False

        # Check for specific rule ignore
        if rule_id:
            # Pattern: # thailint: ignore[rule-id] or ignore[rule1,rule2]
            match = re.search(r"ignore\[([^\]]+)\]", code)
            if match:
                ignored_rules = [r.strip() for r in match.group(1).split(",")]
                return any(self._rule_matches(rule_id, r) for r in ignored_rules)
            else:
                # No brackets means general ignore
                return "ignore[" not in code
        else:
            # No specific rule requested, any ignore works
            return True

    def _rule_matches(self, rule_id: str, pattern: str) -> bool:
        """Check if rule ID matches pattern (supports wildcards).

        Args:
            rule_id: Rule ID to check (e.g., "literals.magic-number").
            pattern: Pattern with optional wildcard (e.g., "literals.*").

        Returns:
            True if rule matches pattern.
        """
        if pattern.endswith("*"):
            # Wildcard match: literals.* matches literals.magic-number
            prefix = pattern[:-1]
            return rule_id.startswith(prefix)
        else:
            # Exact match
            return rule_id == pattern

    def should_ignore_violation(self, violation: "Violation", file_content: str) -> bool:
        """Check if a violation should be ignored based on all levels.

        Checks:
        1. Repository level (.thailintignore)
        2. File level (ignore-file directive)
        3. Line level (inline ignore)
        4. Method level (ignore-next-line)

        Args:
            violation: Violation to check.
            file_content: Content of the file containing the violation.

        Returns:
            True if violation should be ignored.
        """
        file_path = Path(violation.file_path)

        # Level 1: Repository level ignore
        if self.is_ignored(file_path):
            return True

        # Level 2 & 3: File level ignore
        if self.has_file_ignore(file_path, violation.rule_id):
            return True

        # Level 4: Method level (ignore-next-line on previous line)
        lines = file_content.splitlines()
        if violation.line > 1 and violation.line <= len(lines) + 1:
            prev_line_idx = violation.line - 2  # Convert to 0-indexed
            if prev_line_idx >= 0 and prev_line_idx < len(lines):
                prev_line = lines[prev_line_idx]
                if "# thailint: ignore-next-line" in prev_line or "# design-lint: ignore-next-line" in prev_line:
                    # Check if specific rule matches
                    match = re.search(r"ignore-next-line\[([^\]]+)\]", prev_line)
                    if match:
                        ignored_rules = [r.strip() for r in match.group(1).split(",")]
                        if any(self._rule_matches(violation.rule_id, r) for r in ignored_rules):
                            return True
                    else:
                        # General ignore-next-line
                        return True

        # Level 5: Line level (inline ignore)
        if violation.line > 0 and violation.line <= len(lines):
            current_line = lines[violation.line - 1]  # Convert to 0-indexed
            if self.has_line_ignore(current_line, violation.line, violation.rule_id):
                return True

        return False
