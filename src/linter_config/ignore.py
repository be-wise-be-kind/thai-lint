"""
Purpose: Comprehensive 5-level ignore directive parser for suppressing linting violations

Scope: Multi-level ignore system across repository, directory, file, method, and line scopes

Overview: Implements a sophisticated ignore directive system that allows developers to suppress
    linting violations at five different granularity levels, from entire repository patterns down
    to individual lines of code. Repository level uses global ignore patterns from .thailint.yaml
    with gitignore-style glob patterns for excluding files like build artifacts and dependencies.
    File level scans the first 10 lines for ignore-file directives (performance optimization).
    Method level supports ignore-next-line directives placed before functions. Line level enables
    inline ignore comments at the end of code lines. All levels support rule-specific ignores
    using bracket syntax [rule-id] and wildcard rule matching (literals.* matches literals.magic-number).
    The should_ignore_violation() method provides unified checking across all levels, integrating
    with the violation reporting system to filter out suppressed violations before displaying
    results to users.

Dependencies: fnmatch for gitignore-style pattern matching, re for regex-based directive parsing,
    pathlib for file operations, Violation type for violation checking, yaml for config loading

Exports: IgnoreDirectiveParser class

Interfaces: is_ignored(file_path: Path) -> bool for repo-level checking,
    has_file_ignore(file_path: Path, rule_id: str | None) -> bool for file-level,
    has_line_ignore(code: str, line_num: int, rule_id: str | None) -> bool for line-level,
    should_ignore_violation(violation: Violation, file_content: str) -> bool for unified checking

Implementation: Gitignore-style pattern matching with fnmatch, YAML config loading for global patterns,
    first-10-lines scanning for performance, regex-based directive parsing with rule ID extraction,
    wildcard rule matching with prefix comparison, graceful error handling for malformed directives
"""

import fnmatch
import re
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

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
        """Load global ignore patterns from .thailintignore or .thailint.yaml."""
        # First, try to load from .thailintignore (gitignore-style)
        thailintignore = self.project_root / ".thailintignore"
        if thailintignore.exists():
            return self._parse_thailintignore_file(thailintignore)

        # Fall back to .thailint.yaml
        config_file = self.project_root / ".thailint.yaml"
        if config_file.exists():
            return self._parse_config_file(config_file)

        return []

    def _parse_thailintignore_file(self, ignore_file: Path) -> list[str]:
        """Parse .thailintignore file (gitignore-style).

        Args:
            ignore_file: Path to .thailintignore file

        Returns:
            List of ignore patterns
        """
        try:
            content = ignore_file.read_text(encoding="utf-8")
            patterns = []
            for line in content.splitlines():
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    patterns.append(line)
            return patterns
        except (OSError, UnicodeDecodeError):
            return []

    def _parse_config_file(self, config_file: Path) -> list[str]:
        """Parse YAML config file and extract ignore patterns."""
        try:
            config = yaml.safe_load(config_file.read_text(encoding="utf-8"))
            return self._extract_ignore_patterns(config)
        except (yaml.YAMLError, OSError, UnicodeDecodeError):
            return []

    @staticmethod
    def _extract_ignore_patterns(config: dict | None) -> list[str]:
        """Extract ignore patterns from config dict."""
        if not config or not isinstance(config, dict):
            return []

        ignore_patterns = config.get("ignore", [])
        if isinstance(ignore_patterns, list):
            return [str(pattern) for pattern in ignore_patterns]
        return []

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

    def _has_ignore_directive_marker(self, line: str) -> bool:
        """Check if line contains an ignore directive marker."""
        line_lower = line.lower()
        return "# thailint: ignore-file" in line_lower or "# design-lint: ignore-file" in line_lower

    def _check_specific_rule_ignore(self, line: str, rule_id: str) -> bool:
        """Check if line ignores a specific rule."""
        # Check for bracket syntax: # thailint: ignore-file[rule1, rule2]
        if self._check_bracket_syntax_file_ignore(line, rule_id):
            return True

        # Check for space-separated syntax: # thailint: ignore-file rule1 rule2
        return self._check_space_syntax_file_ignore(line, rule_id)

    def _check_bracket_syntax_file_ignore(self, line: str, rule_id: str) -> bool:
        """Check bracket syntax for file-level ignore."""
        bracket_match = re.search(r"ignore-file\[([^\]]+)\]", line, re.IGNORECASE)
        if bracket_match:
            ignored_rules = [r.strip() for r in bracket_match.group(1).split(",")]
            return any(self._rule_matches(rule_id, r) for r in ignored_rules)
        return False

    def _check_space_syntax_file_ignore(self, line: str, rule_id: str) -> bool:
        """Check space-separated syntax for file-level ignore."""
        space_match = re.search(r"ignore-file\s+([^\s#]+(?:\s+[^\s#]+)*)", line, re.IGNORECASE)
        if space_match:
            ignored_rules = [
                r.strip() for r in re.split(r"[,\s]+", space_match.group(1)) if r.strip()
            ]
            return any(self._rule_matches(rule_id, r) for r in ignored_rules)
        return False

    def _check_general_ignore(self, line: str) -> bool:
        """Check if line has general ignore directive (no specific rules)."""
        return "ignore-file[" not in line

    def _read_file_first_lines(self, file_path: Path) -> list[str]:
        """Read first 10 lines of file, return empty list on error."""
        if not file_path.exists():
            return []
        try:
            content = file_path.read_text(encoding="utf-8")
            return content.splitlines()[:10]
        except (UnicodeDecodeError, OSError):
            return []

    def _check_line_for_ignore(self, line: str, rule_id: str | None) -> bool:
        """Check if line has matching ignore directive."""
        if not self._has_ignore_directive_marker(line):
            return False
        if rule_id:
            return self._check_specific_rule_ignore(line, rule_id)
        return self._check_general_ignore(line)

    def has_file_ignore(self, file_path: Path, rule_id: str | None = None) -> bool:
        """Check for file-level ignore directive.

        Scans the first 10 lines of the file for ignore directives.

        Args:
            file_path: Path to file to check.
            rule_id: Optional specific rule ID to check for.

        Returns:
            True if file has ignore directive (general or for specific rule).
        """
        first_lines = self._read_file_first_lines(file_path)
        return any(self._check_line_for_ignore(line, rule_id) for line in first_lines)

    def _has_line_ignore_marker(self, code: str) -> bool:
        """Check if code line has ignore marker."""
        code_lower = code.lower()
        return (
            "# thailint: ignore" in code_lower
            or "# design-lint: ignore" in code_lower
            or "// thailint: ignore" in code_lower
            or "// design-lint: ignore" in code_lower
        )

    def _check_specific_rule_in_line(self, code: str, rule_id: str) -> bool:
        """Check if line's ignore directive matches specific rule."""
        # Check for bracket syntax: # thailint: ignore[rule1, rule2]
        bracket_match = re.search(r"ignore\[([^\]]+)\]", code, re.IGNORECASE)
        if bracket_match:
            return self._check_bracket_rules(bracket_match.group(1), rule_id)

        # Check for space-separated syntax: # thailint: ignore rule1 rule2
        space_match = re.search(r"ignore\s+([^\s#]+(?:\s+[^\s#]+)*)", code, re.IGNORECASE)
        if space_match:
            return self._check_space_separated_rules(space_match.group(1), rule_id)

        # No specific rules - check for "ignore-all"
        return "ignore-all" in code.lower()

    def _check_bracket_rules(self, rules_text: str, rule_id: str) -> bool:
        """Check if bracketed rules match the rule ID."""
        ignored_rules = [r.strip() for r in rules_text.split(",")]
        return any(self._rule_matches(rule_id, r) for r in ignored_rules)

    def _check_space_separated_rules(self, rules_text: str, rule_id: str) -> bool:
        """Check if space-separated rules match the rule ID."""
        ignored_rules = [r.strip() for r in re.split(r"[,\s]+", rules_text) if r.strip()]
        return any(self._rule_matches(rule_id, r) for r in ignored_rules)

    def has_line_ignore(self, code: str, line_num: int, rule_id: str | None = None) -> bool:
        """Check for line-level ignore directive.

        Args:
            code: Line of code to check.
            line_num: Line number (currently unused, for API compatibility).
            rule_id: Optional specific rule ID to check for.

        Returns:
            True if line has ignore directive.
        """
        if not self._has_line_ignore_marker(code):
            return False

        if rule_id:
            return self._check_specific_rule_in_line(code, rule_id)
        return True

    def _rule_matches(self, rule_id: str, pattern: str) -> bool:
        """Check if rule ID matches pattern (supports wildcards and prefixes).

        Args:
            rule_id: Rule ID to check (e.g., "nesting.excessive-depth").
            pattern: Pattern with optional wildcard (e.g., "nesting.*" or "nesting").

        Returns:
            True if rule matches pattern.
        """
        # Case-insensitive comparison
        rule_id_lower = rule_id.lower()
        pattern_lower = pattern.lower()

        if pattern_lower.endswith("*"):
            # Wildcard match: literals.* matches literals.magic-number
            prefix = pattern_lower[:-1]
            return rule_id_lower.startswith(prefix)

        # Exact match
        if rule_id_lower == pattern_lower:
            return True

        # Prefix match: "nesting" matches "nesting.excessive-depth"
        if rule_id_lower.startswith(pattern_lower + "."):
            return True

        return False

    def _has_ignore_next_line_marker(self, prev_line: str) -> bool:
        """Check if line has ignore-next-line marker."""
        return (
            "# thailint: ignore-next-line" in prev_line
            or "# design-lint: ignore-next-line" in prev_line
        )

    def _matches_ignore_next_line_rules(self, prev_line: str, rule_id: str) -> bool:
        """Check if ignore-next-line directive matches the rule."""
        match = re.search(r"ignore-next-line\[([^\]]+)\]", prev_line)
        if match:
            ignored_rules = [r.strip() for r in match.group(1).split(",")]
            return any(self._rule_matches(rule_id, r) for r in ignored_rules)
        return True

    def _is_valid_prev_line_index(self, lines: list[str], violation: "Violation") -> bool:
        """Check if previous line index is valid."""
        if violation.line <= 1 or violation.line > len(lines) + 1:
            return False
        prev_line_idx = violation.line - 2
        return 0 <= prev_line_idx < len(lines)

    def _check_prev_line_ignore(self, lines: list[str], violation: "Violation") -> bool:
        """Check if previous line has ignore-next-line directive."""
        if not self._is_valid_prev_line_index(lines, violation):
            return False

        prev_line_idx = violation.line - 2
        prev_line = lines[prev_line_idx]
        if not self._has_ignore_next_line_marker(prev_line):
            return False

        return self._matches_ignore_next_line_rules(prev_line, violation.rule_id)

    def _check_current_line_ignore(self, lines: list[str], violation: "Violation") -> bool:
        """Check if current line has inline ignore directive."""
        if violation.line <= 0 or violation.line > len(lines):
            return False

        current_line = lines[violation.line - 1]  # Convert to 0-indexed
        return self.has_line_ignore(current_line, violation.line, violation.rule_id)

    def should_ignore_violation(self, violation: "Violation", file_content: str) -> bool:
        """Check if a violation should be ignored based on all levels."""
        file_path = Path(violation.file_path)

        # Repository and file level checks
        if self._is_ignored_at_file_level(file_path, violation.rule_id, file_content):
            return True

        # Line-based checks
        return self._is_ignored_in_content(file_content, violation)

    def _is_ignored_at_file_level(self, file_path: Path, rule_id: str, file_content: str) -> bool:
        """Check repository and file level ignores."""
        if self.is_ignored(file_path):
            return True
        # Check content first (for tests with in-memory content)
        if self._has_file_ignore_in_content(file_content, rule_id):
            return True
        # Fall back to reading from disk if file exists
        return self.has_file_ignore(file_path, rule_id)

    def _has_file_ignore_in_content(self, file_content: str, rule_id: str | None) -> bool:
        """Check if file content has ignore-file directive."""
        lines = file_content.splitlines()[:10]  # Check first 10 lines
        return any(self._check_line_for_ignore(line, rule_id) for line in lines)

    def _is_ignored_in_content(self, file_content: str, violation: "Violation") -> bool:
        """Check content-based ignores (block, line, method level)."""
        lines = file_content.splitlines()

        if self._check_block_ignore(lines, violation):
            return True
        if self._check_prev_line_ignore(lines, violation):
            return True
        if self._check_current_line_ignore(lines, violation):
            return True

        return False

    def _check_block_ignore(self, lines: list[str], violation: "Violation") -> bool:
        """Check if violation is within an ignore-start/ignore-end block."""
        if violation.line <= 0 or violation.line > len(lines):
            return False

        block_state = {"in_block": False, "rules": set()}

        for i, line in enumerate(lines):
            if self._process_block_line(line, i + 1, violation, block_state):
                return True

        return False

    def _process_block_line(
        self, line: str, line_num: int, violation: "Violation", block_state: dict
    ) -> bool:
        """Process a single line for block ignore checking."""
        if "ignore-start" in line:
            block_state["rules"] = self._parse_ignore_start_rules(line)
            block_state["in_block"] = True
            return False

        if self._is_block_end_matching(
            line, block_state["in_block"], line_num, violation, block_state["rules"]
        ):
            return True

        if self._is_violation_line_ignored(
            line_num, violation, block_state["in_block"], block_state["rules"]
        ):
            return True

        if "ignore-end" in line:
            block_state["in_block"] = False
            block_state["rules"] = set()

        return False

    def _is_block_end_matching(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        line: str,
        in_ignore_block: bool,
        line_num: int,
        violation: "Violation",
        current_ignored_rules: set[str],
    ) -> bool:
        """Check if ignore-end matches and violation was in the block."""
        if "ignore-end" not in line:
            return False
        if not in_ignore_block or line_num <= violation.line:
            return False
        return self._rules_match_violation(current_ignored_rules, violation.rule_id)

    def _is_violation_line_ignored(
        self,
        line_num: int,
        violation: "Violation",
        in_ignore_block: bool,
        current_ignored_rules: set[str],
    ) -> bool:
        """Check if current line is the violation line in an ignore block."""
        if line_num != violation.line or not in_ignore_block:
            return False
        return self._rules_match_violation(current_ignored_rules, violation.rule_id)

    def _parse_ignore_start_rules(self, line: str) -> set[str]:
        """Extract rule names from ignore-start directive."""
        match = re.search(r"ignore-start\s+([^\s#]+(?:\s+[^\s#]+)*)", line)
        if match:
            rules_text = match.group(1).strip()
            rules = [r.strip() for r in re.split(r"[,\s]+", rules_text) if r.strip()]
            return set(rules)
        return {"*"}

    def _rules_match_violation(self, ignored_rules: set[str], rule_id: str) -> bool:
        """Check if any of the ignored rules match the violation rule ID."""
        if "*" in ignored_rules:
            return True
        return any(self._rule_matches(rule_id, pattern) for pattern in ignored_rules)


# Alias for backwards compatibility
IgnoreParser = IgnoreDirectiveParser
