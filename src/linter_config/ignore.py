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

Dependencies: pathlib, yaml, rule_matcher module, directive_markers module, pattern_utils module

Exports: IgnoreDirectiveParser class, get_ignore_parser, clear_ignore_parser_cache

Interfaces: is_ignored(file_path) -> bool, has_file_ignore(file_path, rule_id) -> bool,
    has_line_ignore(code, line_num, rule_id) -> bool, should_ignore_violation(violation, content) -> bool

Implementation: Modular design with extracted pure functions for pattern matching and marker detection

Suppressions:
    - global-statement: Module-level singleton pattern for parser caching (performance optimization)
"""

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from src.core.constants import HEADER_SCAN_LINES
from src.linter_config.directive_markers import (
    check_general_ignore,
    has_ignore_directive_marker,
    has_ignore_end_marker,
    has_ignore_next_line_marker,
    has_ignore_start_marker,
    has_line_ignore_marker,
)
from src.linter_config.pattern_utils import extract_patterns_from_content, matches_pattern
from src.linter_config.rule_matcher import (
    check_bracket_rules,
    check_space_separated_rules,
    rules_match_violation,
)

if TYPE_CHECKING:
    from src.core.types import Violation

logger = logging.getLogger(__name__)


class IgnoreDirectiveParser:
    """Parse and check ignore directives at all 5 levels."""

    def __init__(self, project_root: Path | None = None):
        """Initialize parser with project root directory."""
        self.project_root = project_root or Path.cwd()
        self.repo_patterns = _load_repo_ignores(self.project_root)
        self._ignore_cache: dict[str, bool] = {}

    def is_ignored(self, file_path: Path) -> bool:
        """Check if file matches repository-level ignore patterns (cached)."""
        path_str = str(file_path)
        if path_str in self._ignore_cache:
            return self._ignore_cache[path_str]
        try:
            check_path = str(file_path.relative_to(self.project_root))
        except ValueError:
            check_path = path_str
        result = any(matches_pattern(check_path, p) for p in self.repo_patterns)
        self._ignore_cache[path_str] = result
        return result

    def has_file_ignore(self, file_path: Path, rule_id: str | None = None) -> bool:
        """Check for file-level ignore directive in first 10 lines."""
        first_lines = _read_file_first_lines(file_path)
        return any(_check_line_for_ignore(line, rule_id) for line in first_lines)

    def has_line_ignore(self, code: str, line_num: int, rule_id: str | None = None) -> bool:
        """Check for line-level ignore directive."""
        if not has_line_ignore_marker(code):
            return False
        if rule_id:
            return _check_specific_rule_in_line(code, rule_id)
        return True

    def should_ignore_violation(self, violation: "Violation", file_content: str) -> bool:
        """Check if a violation should be ignored based on all levels."""
        file_path = Path(violation.file_path)
        if self._is_ignored_at_file_level(file_path, violation.rule_id, file_content):
            return True
        return _is_ignored_in_content(file_content, violation)

    def _is_ignored_at_file_level(self, file_path: Path, rule_id: str, file_content: str) -> bool:
        """Check repository and file level ignores."""
        if self.is_ignored(file_path):
            return True
        if _has_file_ignore_in_content(file_content, rule_id):
            return True
        return self.has_file_ignore(file_path, rule_id)


# Module-level helper functions (don't need instance state)


def _load_repo_ignores(project_root: Path) -> list[str]:
    """Load global ignore patterns from .thailintignore or .thailint.yaml."""
    thailintignore = project_root / ".thailintignore"
    if thailintignore.exists():
        return _parse_thailintignore_file(thailintignore)
    config_file = project_root / ".thailint.yaml"
    if config_file.exists():
        return _parse_config_file(config_file)
    return []


def _parse_thailintignore_file(ignore_file: Path) -> list[str]:
    """Parse .thailintignore file (gitignore-style)."""
    try:
        content = ignore_file.read_text(encoding="utf-8")
        return extract_patterns_from_content(content)
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("Failed to read .thailintignore file %s: %s", ignore_file, e)
        return []


def _parse_config_file(config_file: Path) -> list[str]:
    """Parse YAML config file and extract ignore patterns."""
    try:
        config = yaml.safe_load(config_file.read_text(encoding="utf-8"))
        return _extract_ignore_patterns(config)
    except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
        logger.warning("Failed to parse config file %s: %s", config_file, e)
        return []


def _extract_ignore_patterns(config: dict | None) -> list[str]:
    """Extract ignore patterns from config dict."""
    if not config or not isinstance(config, dict):
        return []
    ignore_patterns = config.get("ignore", [])
    if isinstance(ignore_patterns, list):
        return [str(pattern) for pattern in ignore_patterns]
    return []


def _read_file_first_lines(file_path: Path) -> list[str]:
    """Read first lines of file for header scanning, return empty list on error."""
    if not file_path.exists():
        return []
    try:
        content = file_path.read_text(encoding="utf-8")
        return content.splitlines()[:HEADER_SCAN_LINES]
    except (UnicodeDecodeError, OSError) as e:
        logger.debug("Failed to read file %s: %s", file_path, e)
        return []


def _check_line_for_ignore(line: str, rule_id: str | None) -> bool:
    """Check if line has matching ignore directive."""
    if not has_ignore_directive_marker(line):
        return False
    if rule_id:
        return _check_specific_rule_ignore(line, rule_id)
    return check_general_ignore(line)


def _check_specific_rule_ignore(line: str, rule_id: str) -> bool:
    """Check if line ignores a specific rule."""
    bracket_match = re.search(r"ignore-file\[([^\]]+)\]", line, re.IGNORECASE)
    if bracket_match:
        return check_bracket_rules(bracket_match.group(1), rule_id)
    space_match = re.search(r"ignore-file\s+([^\s#]+(?:\s+[^\s#]+)*)", line, re.IGNORECASE)
    if space_match:
        return check_space_separated_rules(space_match.group(1), rule_id)
    return False


def _check_specific_rule_in_line(code: str, rule_id: str) -> bool:
    """Check if line's ignore directive matches specific rule."""
    bracket_match = re.search(r"ignore\[([^\]]+)\]", code, re.IGNORECASE)
    if bracket_match:
        return check_bracket_rules(bracket_match.group(1), rule_id)
    space_match = re.search(r"ignore\s+([^\s#]+(?:\s+[^\s#]+)*)", code, re.IGNORECASE)
    if space_match:
        return check_space_separated_rules(space_match.group(1), rule_id)
    return "ignore-all" in code.lower()


def _has_file_ignore_in_content(file_content: str, rule_id: str | None) -> bool:
    """Check if file content has ignore-file directive."""
    lines = file_content.splitlines()[:HEADER_SCAN_LINES]
    return any(_check_line_for_ignore(line, rule_id) for line in lines)


def _is_ignored_in_content(file_content: str, violation: "Violation") -> bool:
    """Check content-based ignores (block, line, method level)."""
    lines = file_content.splitlines()
    if _check_block_ignore(lines, violation):
        return True
    if _check_prev_line_ignore(lines, violation):
        return True
    return _check_current_line_ignore(lines, violation)


def _check_block_ignore(lines: list[str], violation: "Violation") -> bool:
    """Check if violation is within an ignore-start/ignore-end block."""
    if not _is_valid_line_range(violation.line, len(lines)):
        return False
    state = _BlockState()
    for i, line in enumerate(lines, 1):
        result = _process_block_line(line, i, violation, state)
        if result is not None:
            return result
    return False


class _BlockState:
    """Mutable state for block ignore scanning."""

    def __init__(self) -> None:
        self.in_block = False
        self.rules: set[str] = set()


def _is_valid_line_range(line: int, max_lines: int) -> bool:
    """Check if line number is within valid range."""
    return 0 < line <= max_lines


def _process_block_line(
    line: str, line_num: int, violation: "Violation", state: _BlockState
) -> bool | None:
    """Process a line for block ignore, returning True/False if decided, None to continue."""
    if has_ignore_start_marker(line):
        state.rules = _parse_ignore_start_rules(line)
        state.in_block = True
        return None
    if has_ignore_end_marker(line):
        return _handle_block_end(line_num, violation, state)
    if line_num == violation.line and state.in_block:
        return rules_match_violation(state.rules, violation.rule_id)
    return None


def _handle_block_end(line_num: int, violation: "Violation", state: _BlockState) -> bool | None:
    """Handle block end marker."""
    if state.in_block and line_num > violation.line:
        if rules_match_violation(state.rules, violation.rule_id):
            return True
    state.in_block = False
    state.rules = set()
    return None


def _parse_ignore_start_rules(line: str) -> set[str]:
    """Extract rule names from ignore-start directive."""
    match = re.search(r"ignore-start\s+([^\s#]+(?:\s+[^\s#]+)*)", line)
    if match:
        rules_text = match.group(1).strip()
        rules = [r.strip() for r in re.split(r"[,\s]+", rules_text) if r.strip()]
        return set(rules)
    return {"*"}


def _check_prev_line_ignore(lines: list[str], violation: "Violation") -> bool:
    """Check if previous line has ignore-next-line directive."""
    prev_line = _get_prev_line(lines, violation.line)
    if prev_line is None:
        return False
    if not has_ignore_next_line_marker(prev_line):
        return False
    return _matches_ignore_next_line_rules(prev_line, violation.rule_id)


def _get_prev_line(lines: list[str], violation_line: int) -> str | None:
    """Get previous line if it exists and is valid."""
    if violation_line <= 1:
        return None
    prev_idx = violation_line - 2
    if prev_idx < 0 or prev_idx >= len(lines):
        return None
    return lines[prev_idx]


def _matches_ignore_next_line_rules(prev_line: str, rule_id: str) -> bool:
    """Check if ignore-next-line directive matches the rule."""
    match = re.search(r"ignore-next-line\[([^\]]+)\]", prev_line)
    if match:
        return check_bracket_rules(match.group(1), rule_id)
    return True


def _check_current_line_ignore(lines: list[str], violation: "Violation") -> bool:
    """Check if current line has inline ignore directive."""
    if violation.line <= 0 or violation.line > len(lines):
        return False
    current_line = lines[violation.line - 1]
    if not has_line_ignore_marker(current_line):
        return False
    return (
        _check_specific_rule_in_line(current_line, violation.rule_id) if violation.rule_id else True
    )


# Alias for backwards compatibility
IgnoreParser = IgnoreDirectiveParser

# Singleton pattern for performance
_CACHED_PARSER: IgnoreDirectiveParser | None = None
_CACHED_PROJECT_ROOT: Path | None = None


def get_ignore_parser(project_root: Path | None = None) -> IgnoreDirectiveParser:
    """Get cached ignore parser instance (singleton pattern for performance)."""
    global _CACHED_PARSER, _CACHED_PROJECT_ROOT  # pylint: disable=global-statement
    effective_root = project_root or Path.cwd()
    if _CACHED_PARSER is None or _CACHED_PROJECT_ROOT != effective_root:
        _CACHED_PARSER = IgnoreDirectiveParser(effective_root)
        _CACHED_PROJECT_ROOT = effective_root
    return _CACHED_PARSER


def clear_ignore_parser_cache() -> None:
    """Clear cached parser for test isolation or project root changes."""
    global _CACHED_PARSER, _CACHED_PROJECT_ROOT  # pylint: disable=global-statement
    _CACHED_PARSER = None
    _CACHED_PROJECT_ROOT = None
