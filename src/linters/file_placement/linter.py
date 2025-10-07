"""
Purpose: File placement linter implementation
Scope: Validate file organization against allow/deny patterns
Overview: Implements file placement validation using regex patterns from JSON/YAML config.
    Supports directory-specific rules, global patterns, and generates helpful suggestions.
Dependencies: src.core (base classes, types), pathlib, json, re
Exports: FilePlacementLinter, FilePlacementRule
Implementation: Pattern matching with deny-takes-precedence logic
"""

import json
import re
from pathlib import Path
from typing import Any

import yaml

from src.core.base import BaseLintContext, BaseLintRule
from src.core.types import Severity, Violation


class PatternMatcher:
    """Handles regex pattern matching for file paths."""

    def match_deny_patterns(
        self, path_str: str, deny_patterns: list[dict[str, str]]
    ) -> tuple[bool, str | None]:
        """Check if path matches any deny patterns.

        Args:
            path_str: File path to check
            deny_patterns: List of deny pattern dicts with 'pattern' and 'reason'

        Returns:
            Tuple of (is_denied, reason)
        """
        for deny_item in deny_patterns:
            pattern = deny_item["pattern"]
            if re.search(pattern, path_str, re.IGNORECASE):
                reason = deny_item.get("reason", "File not allowed in this location")
                return True, reason
        return False, None

    def match_allow_patterns(self, path_str: str, allow_patterns: list[str]) -> bool:
        """Check if path matches any allow patterns.

        Args:
            path_str: File path to check
            allow_patterns: List of regex patterns

        Returns:
            True if path matches any pattern
        """
        return any(re.search(pattern, path_str, re.IGNORECASE) for pattern in allow_patterns)


class FilePlacementLinter:
    """File placement linter for validating file organization."""

    def __init__(
        self,
        config_file: str | None = None,
        config_obj: dict[str, Any] | None = None,
        project_root: Path | None = None,
    ):
        """Initialize file placement linter.

        Args:
            config_file: Path to layout config file (JSON/YAML)
            config_obj: Config object (alternative to config_file)
            project_root: Project root directory
        """
        self.project_root = project_root or Path.cwd()
        self.pattern_matcher = PatternMatcher()

        # Load config
        if config_obj:
            self.config = config_obj
        elif config_file:
            self.config = self._load_config_file(config_file)
        else:
            self.config = {}

        # Validate regex patterns in config
        self._validate_regex_patterns()

    def _validate_regex_patterns(self) -> None:
        """Validate all regex patterns in config.

        Raises:
            re.error: If any regex pattern is invalid
        """
        fp_config = self.config.get("file_placement", {})

        # Validate directory allow patterns
        if "directories" in fp_config:
            for _dir_path, rules in fp_config["directories"].items():
                if "allow" in rules:
                    for pattern in rules["allow"]:
                        try:
                            re.compile(pattern)
                        except re.error as e:
                            raise ValueError(f"Invalid regex pattern '{pattern}': {e}") from e

                if "deny" in rules:
                    for deny_item in rules["deny"]:
                        pattern = deny_item.get("pattern", "")
                        try:
                            re.compile(pattern)
                        except re.error as e:
                            raise ValueError(f"Invalid regex pattern '{pattern}': {e}") from e

        # Validate global patterns
        if "global_patterns" in fp_config:
            if "allow" in fp_config["global_patterns"]:
                for pattern in fp_config["global_patterns"]["allow"]:
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        raise ValueError(f"Invalid regex pattern '{pattern}': {e}") from e

            if "deny" in fp_config["global_patterns"]:
                for deny_item in fp_config["global_patterns"]["deny"]:
                    pattern = deny_item.get("pattern", "")
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        raise ValueError(f"Invalid regex pattern '{pattern}': {e}") from e

        # Validate global_deny patterns
        if "global_deny" in fp_config:
            for deny_item in fp_config["global_deny"]:
                pattern = deny_item.get("pattern", "")
                try:
                    re.compile(pattern)
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern '{pattern}': {e}") from e

    def _load_config_file(self, config_file: str) -> dict[str, Any]:
        """Load configuration from file.

        Args:
            config_file: Path to config file

        Returns:
            Loaded configuration dict

        Raises:
            Exception: If file cannot be loaded or parsed
        """
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = self.project_root / config_path

        if not config_path.exists():
            # Missing file - return empty config (will use defaults)
            return {}

        with config_path.open(encoding="utf-8") as f:
            if config_path.suffix in [".yaml", ".yml"]:
                return yaml.safe_load(f) or {}
            if config_path.suffix == ".json":
                return json.load(f)
            raise ValueError(f"Unsupported config format: {config_path.suffix}")

    def lint_path(self, file_path: Path) -> list[Violation]:
        """Lint a single file path.

        Args:
            file_path: File to lint

        Returns:
            List of violations found
        """
        violations = []

        # Get relative path
        try:
            if file_path.is_absolute():
                rel_path = file_path.relative_to(self.project_root)
            else:
                rel_path = file_path
        except ValueError:
            # File outside project root - skip
            return violations

        # Convert to string for pattern matching
        path_str = str(rel_path).replace("\\", "/")

        # Get file placement config
        fp_config = self.config.get("file_placement", {})

        # Check directory-specific rules
        if "directories" in fp_config:
            dir_violations = self._check_directory_rules(
                path_str, rel_path, fp_config["directories"]
            )
            violations.extend(dir_violations)

        # Check global deny patterns (always check)
        if "global_deny" in fp_config:
            deny_violations = self._check_global_deny(path_str, rel_path, fp_config["global_deny"])
            violations.extend(deny_violations)

        # Check global patterns
        if "global_patterns" in fp_config:
            global_violations = self._check_global_patterns(
                path_str, rel_path, fp_config["global_patterns"]
            )
            violations.extend(global_violations)

        return violations

    def _check_directory_rules(
        self, path_str: str, rel_path: Path, directories: dict[str, Any]
    ) -> list[Violation]:
        """Check file against directory-specific rules.

        Args:
            path_str: File path string
            rel_path: Relative path
            directories: Directory rules config

        Returns:
            List of violations
        """
        violations = []

        # Find matching directory rule (most specific)
        dir_rule, matched_path = self._find_matching_directory_rule(path_str, directories)
        if not dir_rule:
            return violations

        # Check deny patterns first (they take precedence)
        if "deny" in dir_rule:
            is_denied, reason = self.pattern_matcher.match_deny_patterns(path_str, dir_rule["deny"])
            if is_denied:
                message = f"File '{rel_path}' not allowed in {matched_path}: {reason}"
                suggestion = self._get_suggestion(rel_path.name, matched_path)
                violations.append(
                    Violation(
                        rule_id="file-placement",
                        file_path=str(rel_path),
                        line=1,
                        column=0,
                        message=message,
                        severity=Severity.ERROR,
                        suggestion=suggestion,
                    )
                )
                return violations  # Deny found, stop checking

        # Check allow patterns
        if "allow" in dir_rule:
            if not self.pattern_matcher.match_allow_patterns(path_str, dir_rule["allow"]):
                message = f"File '{rel_path}' does not match allowed patterns for {matched_path}"
                suggestion = f"Move to {matched_path} or ensure file type is allowed"
                violations.append(
                    Violation(
                        rule_id="file-placement",
                        file_path=str(rel_path),
                        line=1,
                        column=0,
                        message=message,
                        severity=Severity.ERROR,
                        suggestion=suggestion,
                    )
                )

        return violations

    def _find_matching_directory_rule(
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
            matches = False

            # Special handling for root directory
            if dir_path == "/":
                # Match files at root level (no slash in path)
                if "/" not in path_str:
                    matches = True
                    depth = 0
            elif path_str.startswith(dir_path):
                matches = True
                depth = len(dir_path.split("/"))

            if matches:
                depth = len(dir_path.split("/"))
                if depth > best_depth:
                    best_match = rules
                    best_path = dir_path
                    best_depth = depth

        return best_match, best_path

    def _check_global_deny(
        self, path_str: str, rel_path: Path, global_deny: list[dict[str, str]]
    ) -> list[Violation]:
        """Check file against global deny patterns.

        Args:
            path_str: File path string
            rel_path: Relative path
            global_deny: Global deny patterns

        Returns:
            List of violations
        """
        violations = []
        is_denied, reason = self.pattern_matcher.match_deny_patterns(path_str, global_deny)
        if is_denied:
            violations.append(
                Violation(
                    rule_id="file-placement",
                    file_path=str(rel_path),
                    line=1,
                    column=0,
                    message=reason or f"File '{rel_path}' matches denied pattern",
                    severity=Severity.ERROR,
                    suggestion=self._get_suggestion(rel_path.name, None),
                )
            )
        return violations

    def _check_global_patterns(
        self, path_str: str, rel_path: Path, global_patterns: dict[str, Any]
    ) -> list[Violation]:
        """Check file against global patterns.

        Args:
            path_str: File path string
            rel_path: Relative path
            global_patterns: Global patterns config

        Returns:
            List of violations
        """
        violations = []

        # Check deny first
        if "deny" in global_patterns:
            is_denied, reason = self.pattern_matcher.match_deny_patterns(
                path_str, global_patterns["deny"]
            )
            if is_denied:
                violations.append(
                    Violation(
                        rule_id="file-placement",
                        file_path=str(rel_path),
                        line=1,
                        column=0,
                        message=reason or f"File '{rel_path}' matches denied pattern",
                        severity=Severity.ERROR,
                        suggestion=self._get_suggestion(rel_path.name, None),
                    )
                )
                return violations

        # Check allow
        if "allow" in global_patterns:
            if not self.pattern_matcher.match_allow_patterns(path_str, global_patterns["allow"]):
                violations.append(
                    Violation(
                        rule_id="file-placement",
                        file_path=str(rel_path),
                        line=1,
                        column=0,
                        message=f"File '{rel_path}' does not match any allowed patterns",
                        severity=Severity.ERROR,
                        suggestion="Ensure file matches project structure patterns",
                    )
                )

        return violations

    def _get_suggestion(self, filename: str, current_location: str | None) -> str:
        """Get suggestion for file placement.

        Args:
            filename: File name
            current_location: Current directory location

        Returns:
            Suggestion string
        """
        if "test" in filename.lower():
            return "Move to tests/ directory"

        if filename.endswith((".ts", ".tsx", ".jsx")):
            if "component" in filename.lower():
                return "Move to src/components/"
            return "Move to src/"

        if filename.endswith(".py"):
            return "Move to src/"

        if filename.startswith(("debug", "temp")):
            return "Move to debug/ or remove if not needed"

        if filename.endswith(".log"):
            return "Move to logs/ or add to .gitignore"

        return "Review file organization and move to appropriate directory"

    def check_file_allowed(self, file_path: Path) -> bool:
        """Check if file is allowed (no violations).

        Args:
            file_path: File to check

        Returns:
            True if file is allowed (no violations)
        """
        violations = self.lint_path(file_path)
        return len(violations) == 0

    def lint_directory(self, dir_path: Path, recursive: bool = True) -> list[Violation]:
        """Lint all files in directory.

        Args:
            dir_path: Directory to scan
            recursive: Scan recursively

        Returns:
            List of all violations found
        """
        violations = []
        pattern = "**/*" if recursive else "*"

        from src.linter_config.ignore import IgnoreDirectiveParser

        ignore_parser = IgnoreDirectiveParser(self.project_root)

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                # Check ignore patterns
                if not ignore_parser.is_ignored(file_path):
                    violations.extend(self.lint_path(file_path))

        return violations


class FilePlacementRule(BaseLintRule):
    """File placement linting rule (integrates with framework)."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize rule with config.

        Args:
            config: Rule configuration
        """
        self.config = config or {}
        layout_file = self.config.get("layout_file", ".ai/layout.yaml")

        # Load layout config
        try:
            layout_path = Path(layout_file)
            with layout_path.open(encoding="utf-8") as f:
                if layout_file.endswith((".yaml", ".yml")):
                    layout_config = yaml.safe_load(f)
                else:
                    layout_config = json.load(f)
        except Exception:
            layout_config = {}

        # Create linter
        self.linter = FilePlacementLinter(config_obj=layout_config)

    @property
    def rule_id(self) -> str:
        """Return rule ID."""
        return "file-placement"

    @property
    def rule_name(self) -> str:
        """Return rule name."""
        return "File Placement"

    @property
    def description(self) -> str:
        """Return rule description."""
        return "Validate file organization against project structure rules"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check file placement.

        Args:
            context: Lint context

        Returns:
            List of violations
        """
        if not context.file_path:
            return []

        return self.linter.lint_path(context.file_path)
