"""
Purpose: Rule checking logic for file placement linter

Scope: Executes file placement rules including directory-specific and global patterns

Overview: Provides core rule checking functionality for the file placement linter. Checks
    files against directory-specific allow/deny rules, global patterns, and global deny lists.
    Uses pattern matcher for regex matching, directory matcher for finding rules, and violation
    factory for creating violations. Implements deny-takes-precedence logic. Isolates rule
    execution logic from configuration, validation, and violation creation.

Dependencies: pathlib, typing, PatternMatcher, DirectoryMatcher, ViolationFactory, src.core.types

Exports: RuleChecker

Interfaces: check_all_rules(path_str, rel_path, fp_config) -> list[Violation]

Implementation: Checks deny before allow, delegates directory matching to DirectoryMatcher
"""

from pathlib import Path
from typing import Any

from src.core.types import Violation

from .directory_matcher import DirectoryMatcher
from .pattern_matcher import PatternMatcher
from .violation_factory import ViolationFactory


class RuleChecker:
    """Checks file placement rules and returns violations."""

    def __init__(self, pattern_matcher: PatternMatcher, violation_factory: ViolationFactory):
        """Initialize rule checker.

        Args:
            pattern_matcher: Pattern matcher for regex matching
            violation_factory: Factory for creating violations
        """
        self.pattern_matcher = pattern_matcher
        self.violation_factory = violation_factory
        self.directory_matcher = DirectoryMatcher()

    def check_all_rules(
        self, path_str: str, rel_path: Path, fp_config: dict[str, Any]
    ) -> list[Violation]:
        """Check all file placement rules.

        Args:
            path_str: Normalized path string
            rel_path: Relative path object
            fp_config: File placement configuration

        Returns:
            List of violations found
        """
        violations: list[Violation] = []

        if "directories" in fp_config:
            dir_violations = self._check_directory_rules(
                path_str, rel_path, fp_config["directories"]
            )
            violations.extend(dir_violations)

        if "global_deny" in fp_config:
            deny_violations = self._check_global_deny(path_str, rel_path, fp_config["global_deny"])
            violations.extend(deny_violations)

        if "global_patterns" in fp_config:
            global_violations = self._check_global_patterns(
                path_str, rel_path, fp_config["global_patterns"]
            )
            violations.extend(global_violations)

        return violations

    def _check_directory_deny_rules(
        self, path_str: str, rel_path: Path, dir_rule: dict[str, Any], matched_path: str
    ) -> Violation | None:
        """Check directory deny rules.

        Args:
            path_str: Normalized path string
            rel_path: Relative path object
            dir_rule: Directory rule config
            matched_path: Matched directory path

        Returns:
            Violation if denied, None otherwise
        """
        if "deny" not in dir_rule:
            return None

        is_denied, reason = self.pattern_matcher.match_deny_patterns(path_str, dir_rule["deny"])
        if is_denied:
            return self.violation_factory.create_deny_violation(
                rel_path, matched_path, reason or "Pattern denied"
            )
        return None

    def _check_directory_allow_rules(
        self, path_str: str, rel_path: Path, dir_rule: dict[str, Any], matched_path: str
    ) -> Violation | None:
        """Check directory allow rules.

        Args:
            path_str: Normalized path string
            rel_path: Relative path object
            dir_rule: Directory rule config
            matched_path: Matched directory path

        Returns:
            Violation if not allowed, None otherwise
        """
        if "allow" not in dir_rule:
            return None

        if not self.pattern_matcher.match_allow_patterns(path_str, dir_rule["allow"]):
            return self.violation_factory.create_allow_violation(rel_path, matched_path)
        return None

    def _check_directory_rules(
        self, path_str: str, rel_path: Path, directories: dict[str, Any]
    ) -> list[Violation]:
        """Check file against directory-specific rules.

        Args:
            path_str: Normalized path string
            rel_path: Relative path object
            directories: Directory rules config

        Returns:
            List of violations
        """
        dir_rule, matched_path = self.directory_matcher.find_matching_rule(path_str, directories)
        if not dir_rule or not matched_path:
            return []

        # Check deny patterns first (takes precedence)
        deny_violation = self._check_directory_deny_rules(
            path_str, rel_path, dir_rule, matched_path
        )
        if deny_violation:
            return [deny_violation]

        # Check allow patterns
        allow_violation = self._check_directory_allow_rules(
            path_str, rel_path, dir_rule, matched_path
        )
        if allow_violation:
            return [allow_violation]

        return []

    def _check_global_deny(
        self, path_str: str, rel_path: Path, global_deny: list[dict[str, str]]
    ) -> list[Violation]:
        """Check file against global deny patterns.

        Args:
            path_str: Normalized path string
            rel_path: Relative path object
            global_deny: Global deny patterns

        Returns:
            List of violations
        """
        is_denied, reason = self.pattern_matcher.match_deny_patterns(path_str, global_deny)
        if is_denied:
            violation = self.violation_factory.create_global_deny_violation(rel_path, reason)
            return [violation]
        return []

    def _check_global_patterns(
        self, path_str: str, rel_path: Path, global_patterns: dict[str, Any]
    ) -> list[Violation]:
        """Check file against global patterns.

        Args:
            path_str: Normalized path string
            rel_path: Relative path object
            global_patterns: Global patterns config

        Returns:
            List of violations
        """
        # Check deny patterns first
        if "deny" in global_patterns:
            is_denied, reason = self.pattern_matcher.match_deny_patterns(
                path_str, global_patterns["deny"]
            )
            if is_denied:
                violation = self.violation_factory.create_global_deny_violation(rel_path, reason)
                return [violation]

        # Check allow patterns
        if "allow" in global_patterns:
            if not self.pattern_matcher.match_allow_patterns(path_str, global_patterns["allow"]):
                violation = self.violation_factory.create_global_allow_violation(rel_path)
                return [violation]

        return []
