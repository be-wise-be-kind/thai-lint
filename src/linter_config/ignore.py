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

Exports: IgnoreDirectiveParser class, get_ignore_parser, clear_ignore_parser_cache,
    should_ignore_violation_for_context

Interfaces: is_ignored(file_path) -> bool, is_dir_ignored(dir_path) -> bool,
    has_file_ignore(file_path, rule_id) -> bool,
    has_line_ignore(code, line_num, rule_id) -> bool, should_ignore_violation(violation, content) -> bool,
    should_ignore_violation_for_context(ignore_parser, violation, context) -> bool

Implementation: Modular design with extracted pure functions for pattern matching and marker detection

Suppressions:
    - global-statement: Module-level singleton pattern for parser caching (performance optimization)
"""

import logging
import re
from contextlib import suppress
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
    from src.core.base import BaseLintContext
    from src.core.types import Violation

logger = logging.getLogger(__name__)


class IgnoreDirectiveParser:
    """Parse and check ignore directives at all 5 levels."""

    def __init__(self, project_root: Path | None = None):
        """Initialize parser with project root directory."""
        self.project_root = project_root or Path.cwd()
        self.repo_patterns = _load_repo_ignores(self.project_root)
        self._ignore_cache: dict[str, bool] = {}
        self._dir_ignore_cache: dict[str, bool] = {}
        # Keyed by id(file_content), but each entry also stores the object the id was
        # taken from so a lookup can verify (via `is`) it's still the same object before
        # trusting it. CPython's id() is only unique among *simultaneously live* objects -
        # "two objects with non-overlapping lifetimes may have the same id() value" - and
        # a long-lived --parallel worker processes many short-lived per-file content
        # strings in sequence, exactly the pattern where a freed string's address gets
        # recycled for a later, unrelated file. Without the stored reference to check
        # against, a collision would silently serve a previous file's cached lines/index.
        self._lines_cache: dict[int, tuple[str, list[str]]] = {}
        self._block_index_cache: dict[int, tuple[list[str], _BlockIndex]] = {}

    def is_ignored(self, file_path: Path) -> bool:
        """Check if file matches repository-level ignore patterns (cached)."""
        path_str = str(file_path)
        with suppress(KeyError):
            return self._ignore_cache[path_str]
        try:
            check_path = str(file_path.relative_to(self.project_root))
        except ValueError:
            check_path = path_str
        result = any(matches_pattern(check_path, p) for p in self.repo_patterns)
        self._ignore_cache[path_str] = result
        return result

    def is_dir_ignored(self, dir_path: Path) -> bool:
        """Check if a directory is fully covered by repo-level ignore patterns (cached).

        Used to prune directory traversal before it happens (see
        Orchestrator._collect_files_fast), not just to filter already-collected files.
        Tests the directory as a path prefix (trailing "/") rather than as a bare name,
        so patterns that only describe a directory's *contents* (e.g. "**/name/**")
        still match here - anything under the directory would be ignored anyway, so
        it's safe (and much faster) to skip descending into it at all.
        """
        path_str = str(dir_path)
        with suppress(KeyError):
            return self._dir_ignore_cache[path_str]
        try:
            check_path = str(dir_path.relative_to(self.project_root))
        except ValueError:
            check_path = path_str
        probe = check_path.rstrip("/") + "/"
        result = any(matches_pattern(probe, p) for p in self.repo_patterns)
        self._dir_ignore_cache[path_str] = result
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
        lines = self._get_cached_lines(file_content)
        if self._check_block_ignore(violation, lines):
            return True
        if _check_prev_line_ignore(lines, violation):
            return True
        return _check_current_line_ignore(lines, violation)

    def _get_cached_lines(self, file_content: str) -> list[str]:
        """Split file_content into lines once per distinct content, then reuse.

        Cached by content identity so repeated calls for the same file (the
        common case: many violations against one file) return the same list
        object, which also keeps the block-index cache keyed off it stable.
        Verifies the cached entry is still `is` the requested object before
        trusting it, since id() alone can collide across a colliding freed
        object's recycled address (see __init__ docstring).
        """
        key = id(file_content)
        cached = self._lines_cache.get(key)
        if cached is not None and cached[0] is file_content:
            return cached[1]
        lines = file_content.splitlines()
        self._lines_cache[key] = (file_content, lines)
        return lines

    def _is_ignored_at_file_level(self, file_path: Path, rule_id: str, file_content: str) -> bool:
        """Check repository and file level ignores.

        When file_content is already available, the disk-read fallback
        (has_file_ignore) is redundant with the content-based check and is
        skipped - re-reading the file from disk per violation was a real
        performance issue on files with many violations. See issue [TBD].
        """
        if self.is_ignored(file_path):
            return True
        if file_content:
            return _has_file_ignore_in_content(file_content, rule_id)
        return self.has_file_ignore(file_path, rule_id)

    def _check_block_ignore(self, violation: "Violation", lines: list[str]) -> bool:
        """Check if violation is within an ignore-start/ignore-end block.

        Builds the block index once per distinct file content (cached by
        content identity) instead of re-scanning every line of the file for
        every violation. See issue [TBD].
        """
        if not _is_valid_line_range(violation.line, len(lines)):
            return False
        index = self._get_block_index(lines)
        return index.is_ignored(violation.line, violation.rule_id)

    def _get_block_index(self, lines: list[str]) -> "_BlockIndex":
        """Get the cached block index for these lines, building it if needed.

        Verifies the cached entry is still `is` the requested list before
        trusting it (see _get_cached_lines and __init__ docstring).
        """
        key = id(lines)
        cached = self._block_index_cache.get(key)
        if cached is not None and cached[0] is lines:
            return cached[1]
        index = _BlockIndex.build(lines)
        self._block_index_cache[key] = (lines, index)
        return index


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


def _is_valid_line_range(line: int, max_lines: int) -> bool:
    """Check if line number is within valid range."""
    return 0 < line <= max_lines


class _BlockIndex:
    """Precomputed ignore-start/ignore-end block data for O(1)-ish per-violation lookup.

    Built once per file (see IgnoreDirectiveParser._get_block_index) instead of
    re-scanning every line of the file for every violation. Replays the same
    line-by-line state machine the original per-violation scan used, but
    records every outcome instead of stopping at one target line.

    The original scan terminates the instant it reaches the violation's own
    line while inside an open block (returning whatever that block's rules
    say, win or lose) - later blocks are never considered for that violation
    once that happens. Otherwise, it only reconsiders the violation
    retroactively once a later ignore-end marker is reached. `_open_lines`
    captures the first case; `_closed_spans` captures the second.
    """

    def __init__(
        self, open_lines: dict[int, frozenset[str]], closed_spans: list[tuple[int, frozenset[str]]]
    ) -> None:
        self._open_lines = open_lines
        self._closed_spans = closed_spans

    @classmethod
    def build(cls, lines: list[str]) -> "_BlockIndex":
        """Scan lines once, recording every open-line and closed-span outcome."""
        open_lines: dict[int, frozenset[str]] = {}
        closed_spans: list[tuple[int, frozenset[str]]] = []
        state = _BlockScanState()
        for i, line in enumerate(lines, 1):
            _scan_line(line, i, state, open_lines, closed_spans)
        return cls(open_lines, closed_spans)

    def is_ignored(self, violation_line: int, rule_id: str) -> bool:
        """Check whether a violation at this line/rule is block-ignored."""
        rules_at_line = self._open_lines.get(violation_line)
        if rules_at_line is not None:
            return rules_match_violation(rules_at_line, rule_id)
        return any(
            violation_line < end_line and rules_match_violation(rules, rule_id)
            for end_line, rules in self._closed_spans
        )


class _BlockScanState:
    """Mutable state carried across lines while building a _BlockIndex."""

    def __init__(self) -> None:
        self.in_block = False
        self.rules: set[str] = set()


def _scan_line(
    line: str,
    line_num: int,
    state: _BlockScanState,
    open_lines: dict[int, frozenset[str]],
    closed_spans: list[tuple[int, frozenset[str]]],
) -> None:
    """Process one line's effect on block-scan state, recording index entries."""
    if has_ignore_start_marker(line):
        state.rules = _parse_ignore_start_rules(line)
        state.in_block = True
        return
    if has_ignore_end_marker(line):
        _close_block(line_num, state, closed_spans)
        return
    if state.in_block:
        open_lines[line_num] = frozenset(state.rules)


def _close_block(
    line_num: int, state: _BlockScanState, closed_spans: list[tuple[int, frozenset[str]]]
) -> None:
    """Record a closed-span entry (if a block was open) and reset scan state."""
    if state.in_block:
        closed_spans.append((line_num, frozenset(state.rules)))
    state.in_block = False
    state.rules = set()


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


def should_ignore_violation_for_context(
    ignore_parser: IgnoreDirectiveParser, violation: "Violation", context: "BaseLintContext"
) -> bool:
    """Check if a violation should be ignored, using a lint context's file content.

    Shared by the check-ignore-append pattern every architectural linter's rule class
    follows: analyze, build a violation, check it against ignore directives, append it
    if not ignored.

    Args:
        ignore_parser: Parser to check inline/file/directory ignore directives against
        violation: Violation to check
        context: Lint context providing file content (falls back to "" if None)

    Returns:
        True if violation should be ignored
    """
    return ignore_parser.should_ignore_violation(violation, context.file_content or "")
