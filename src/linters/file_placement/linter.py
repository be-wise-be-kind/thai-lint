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

    def _validate_pattern(self, pattern: str) -> None:
        """Validate a single regex pattern.

        Args:
            pattern: Regex pattern to validate

        Raises:
            ValueError: If pattern is invalid
        """
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{pattern}': {e}") from e

    def _validate_allow_patterns(self, rules: dict[str, Any]) -> None:
        """Validate allow patterns in a rules dict."""
        if "allow" in rules:
            for pattern in rules["allow"]:
                self._validate_pattern(pattern)

    def _validate_deny_patterns(self, rules: dict[str, Any]) -> None:
        """Validate deny patterns in a rules dict."""
        if "deny" in rules:
            for deny_item in rules["deny"]:
                pattern = deny_item.get("pattern", "")
                self._validate_pattern(pattern)

    def _validate_directory_patterns(self, fp_config: dict[str, Any]) -> None:
        """Validate all directory-specific patterns."""
        if "directories" in fp_config:
            for _dir_path, rules in fp_config["directories"].items():
                self._validate_allow_patterns(rules)
                self._validate_deny_patterns(rules)

    def _validate_global_patterns(self, fp_config: dict[str, Any]) -> None:
        """Validate global patterns section."""
        if "global_patterns" in fp_config:
            self._validate_allow_patterns(fp_config["global_patterns"])
            self._validate_deny_patterns(fp_config["global_patterns"])

    def _validate_global_deny_patterns(self, fp_config: dict[str, Any]) -> None:
        """Validate global_deny patterns."""
        if "global_deny" in fp_config:
            for deny_item in fp_config["global_deny"]:
                pattern = deny_item.get("pattern", "")
                self._validate_pattern(pattern)

    def _validate_regex_patterns(self) -> None:
        """Validate all regex patterns in config.

        Raises:
            re.error: If any regex pattern is invalid
        """
        fp_config = self.config.get("file-placement", {})

        self._validate_directory_patterns(fp_config)
        self._validate_global_patterns(fp_config)
        self._validate_global_deny_patterns(fp_config)

    def _resolve_config_path(self, config_file: str) -> Path:
        """Resolve config file path relative to project root."""
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = self.project_root / config_path
        return config_path

    def _parse_config_file(self, config_path: Path) -> dict[str, Any]:
        """Parse config file based on extension."""
        with config_path.open(encoding="utf-8") as f:
            if config_path.suffix in [".yaml", ".yml"]:
                return yaml.safe_load(f) or {}
            if config_path.suffix == ".json":
                return json.load(f)
            raise ValueError(f"Unsupported config format: {config_path.suffix}")

    def _load_config_file(self, config_file: str) -> dict[str, Any]:
        """Load configuration from file.

        Args:
            config_file: Path to config file

        Returns:
            Loaded configuration dict

        Raises:
            Exception: If file cannot be loaded or parsed
        """
        config_path = self._resolve_config_path(config_file)
        if not config_path.exists():
            return {}
        return self._parse_config_file(config_path)

    def _get_relative_path(self, file_path: Path) -> Path:
        """Get path relative to project root, or return as-is."""
        try:
            if file_path.is_absolute():
                return file_path.relative_to(self.project_root)
            return file_path
        except ValueError:
            # If path is outside project root, return it as-is
            # This allows detection of absolute paths in global_deny patterns
            return file_path

    def _check_all_rules(
        self, path_str: str, rel_path: Path, fp_config: dict[str, Any]
    ) -> list[Violation]:
        """Check all file placement rules."""
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

    def lint_path(self, file_path: Path) -> list[Violation]:
        """Lint a single file path.

        Args:
            file_path: File to lint

        Returns:
            List of violations found
        """
        rel_path = self._get_relative_path(file_path)
        path_str = str(rel_path).replace("\\", "/")
        fp_config = self.config.get("file-placement", {})
        return self._check_all_rules(path_str, rel_path, fp_config)

    def _create_deny_violation(self, rel_path: Path, matched_path: str, reason: str) -> Violation:
        """Create violation for denied file."""
        message = f"File '{rel_path}' not allowed in {matched_path}: {reason}"
        suggestion = self._get_suggestion(rel_path.name, matched_path)
        return Violation(
            rule_id="file-placement",
            file_path=str(rel_path),
            line=1,
            column=0,
            message=message,
            severity=Severity.ERROR,
            suggestion=suggestion,
        )

    def _create_allow_violation(self, rel_path: Path, matched_path: str) -> Violation:
        """Create violation for file not matching allow patterns."""
        message = f"File '{rel_path}' does not match allowed patterns for {matched_path}"
        suggestion = f"Move to {matched_path} or ensure file type is allowed"
        return Violation(
            rule_id="file-placement",
            file_path=str(rel_path),
            line=1,
            column=0,
            message=message,
            severity=Severity.ERROR,
            suggestion=suggestion,
        )

    def _check_deny_patterns(
        self, path_str: str, rel_path: Path, dir_rule: dict[str, Any], matched_path: str
    ) -> list[Violation]:
        """Check deny patterns and return violations if denied."""
        if "deny" not in dir_rule:
            return []

        is_denied, reason = self.pattern_matcher.match_deny_patterns(path_str, dir_rule["deny"])
        if is_denied:
            return [self._create_deny_violation(rel_path, matched_path, reason or "Pattern denied")]
        return []

    def _check_allow_patterns(
        self, path_str: str, rel_path: Path, dir_rule: dict[str, Any], matched_path: str
    ) -> list[Violation]:
        """Check allow patterns and return violations if not allowed."""
        if "allow" not in dir_rule:
            return []

        if not self.pattern_matcher.match_allow_patterns(path_str, dir_rule["allow"]):
            return [self._create_allow_violation(rel_path, matched_path)]
        return []

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
        dir_rule, matched_path = self._find_matching_directory_rule(path_str, directories)
        if not dir_rule or not matched_path:
            return []

        deny_violations = self._check_deny_patterns(path_str, rel_path, dir_rule, matched_path)
        if deny_violations:
            return deny_violations

        return self._check_allow_patterns(path_str, rel_path, dir_rule, matched_path)

    def _check_root_match(self, dir_path: str, path_str: str) -> tuple[bool, int]:
        """Check if path matches root directory rule."""
        if dir_path == "/" and "/" not in path_str:
            return True, 0
        return False, -1

    def _check_path_match(self, dir_path: str, path_str: str) -> tuple[bool, int]:
        """Check if path matches directory rule."""
        if dir_path == "/":
            return self._check_root_match(dir_path, path_str)
        if path_str.startswith(dir_path):
            depth = len(dir_path.split("/"))
            return True, depth
        return False, -1

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
            matches, depth = self._check_path_match(dir_path, path_str)
            if matches and depth > best_depth:
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

    def _check_global_deny_patterns(
        self, path_str: str, rel_path: Path, global_patterns: dict[str, Any]
    ) -> list[Violation]:
        """Check global deny patterns."""
        if "deny" not in global_patterns:
            return []

        is_denied, reason = self.pattern_matcher.match_deny_patterns(
            path_str, global_patterns["deny"]
        )
        if is_denied:
            return [
                Violation(
                    rule_id="file-placement",
                    file_path=str(rel_path),
                    line=1,
                    column=0,
                    message=reason or f"File '{rel_path}' matches denied pattern",
                    severity=Severity.ERROR,
                    suggestion=self._get_suggestion(rel_path.name, None),
                )
            ]
        return []

    def _check_global_allow_patterns(
        self, path_str: str, rel_path: Path, global_patterns: dict[str, Any]
    ) -> list[Violation]:
        """Check global allow patterns."""
        if "allow" not in global_patterns:
            return []

        if not self.pattern_matcher.match_allow_patterns(path_str, global_patterns["allow"]):
            return [
                Violation(
                    rule_id="file-placement",
                    file_path=str(rel_path),
                    line=1,
                    column=0,
                    message=f"File '{rel_path}' does not match any allowed patterns",
                    severity=Severity.ERROR,
                    suggestion="Ensure file matches project structure patterns",
                )
            ]
        return []

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
        deny_violations = self._check_global_deny_patterns(path_str, rel_path, global_patterns)
        if deny_violations:
            return deny_violations

        return self._check_global_allow_patterns(path_str, rel_path, global_patterns)

    def _suggest_for_test_file(self, filename: str) -> str | None:
        """Get suggestion for test files."""
        if "test" in filename.lower():
            return "Move to tests/ directory"
        return None

    def _suggest_for_typescript_file(self, filename: str) -> str | None:
        """Get suggestion for TypeScript/JSX files."""
        if filename.endswith((".ts", ".tsx", ".jsx")):
            if "component" in filename.lower():
                return "Move to src/components/"
            return "Move to src/"
        return None

    def _suggest_for_other_files(self, filename: str) -> str:
        """Get suggestion for other file types."""
        if filename.endswith(".py"):
            return "Move to src/"
        if filename.startswith(("debug", "temp")):
            return "Move to debug/ or remove if not needed"
        if filename.endswith(".log"):
            return "Move to logs/ or add to .gitignore"
        return "Review file organization and move to appropriate directory"

    def _get_suggestion(self, filename: str, current_location: str | None) -> str:
        """Get suggestion for file placement.

        Args:
            filename: File name
            current_location: Current directory location

        Returns:
            Suggestion string
        """
        suggestion = self._suggest_for_test_file(filename)
        if suggestion:
            return suggestion

        suggestion = self._suggest_for_typescript_file(filename)
        if suggestion:
            return suggestion

        return self._suggest_for_other_files(filename)

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
        self._linter_cache: dict[Path, FilePlacementLinter] = {}

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

    def _get_layout_path(self, project_root: Path) -> Path:
        """Get layout config file path."""
        layout_file = self.config.get("layout_file")
        if layout_file:
            return project_root / layout_file

        yaml_path = project_root / ".ai" / "layout.yaml"
        json_path = project_root / ".ai" / "layout.json"
        if yaml_path.exists():
            return yaml_path
        if json_path.exists():
            return json_path
        return yaml_path

    def _load_layout_config(self, layout_path: Path) -> dict[str, Any]:
        """Load layout configuration from file."""
        try:
            with layout_path.open(encoding="utf-8") as f:
                if str(layout_path).endswith((".yaml", ".yml")):
                    return yaml.safe_load(f) or {}
                return json.load(f)
        except Exception:
            return {}

    def _get_or_create_linter(self, project_root: Path) -> FilePlacementLinter:
        """Get cached linter or create new one."""
        if project_root not in self._linter_cache:
            layout_path = self._get_layout_path(project_root)
            layout_config = self._load_layout_config(layout_path)
            self._linter_cache[project_root] = FilePlacementLinter(
                config_obj=layout_config, project_root=project_root
            )
        return self._linter_cache[project_root]

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check file placement.

        Args:
            context: Lint context

        Returns:
            List of violations
        """
        if not context.file_path:
            return []

        project_root = self._find_project_root(context.file_path)
        linter = self._get_or_create_linter(project_root)
        return linter.lint_path(context.file_path)

    def _find_project_root(self, file_path: Path) -> Path:
        """Find project root by looking for .ai directory.

        Args:
            file_path: File being linted

        Returns:
            Project root directory
        """
        current = file_path.parent if file_path.is_file() else file_path

        # Walk up directory tree looking for .ai directory
        while current != current.parent:
            if (current / ".ai").exists():
                return current
            current = current.parent

        # Fallback to current directory if no .ai found
        return Path.cwd()
