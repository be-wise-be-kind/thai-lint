"""
Purpose: Regex pattern validation for file placement linter configuration

Scope: Validates regex patterns in configuration files to ensure they are compilable

Overview: Provides validation functionality for regex patterns used in file placement rules.
    Validates patterns in allow/deny lists, directory-specific rules, and global patterns.
    Raises descriptive errors when patterns are invalid, helping users debug configuration
    issues early. Isolates pattern validation logic from rule checking and config loading.

Dependencies: re, typing

Exports: PatternValidator

Interfaces: validate_config(config) -> None (raises ValueError on invalid patterns)

Implementation: Uses re.compile() to test pattern validity, provides detailed error messages
"""

import re
from typing import Any


class PatternValidator:
    """Validates regex patterns in file placement configuration."""

    def __init__(self) -> None:
        """Initialize the pattern validator."""
        pass  # Stateless validator for regex patterns

    def validate_config(self, config: dict[str, Any]) -> None:
        """Validate all regex patterns in configuration.

        Args:
            config: Full configuration dict

        Raises:
            ValueError: If any regex pattern is invalid
        """
        fp_config = config.get("file-placement", {})
        self._validate_directory_patterns(fp_config)
        self._validate_global_patterns(fp_config)
        self._validate_global_deny_patterns(fp_config)

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
        """Validate allow patterns in a rules dict.

        Args:
            rules: Rules dictionary containing allow patterns
        """
        if "allow" in rules:
            for pattern in rules["allow"]:
                self._validate_pattern(pattern)

    def _validate_deny_patterns(self, rules: dict[str, Any]) -> None:
        """Validate deny patterns in a rules dict.

        Args:
            rules: Rules dictionary containing deny patterns
        """
        if "deny" in rules:
            for deny_item in rules["deny"]:
                pattern = deny_item.get("pattern", "")
                self._validate_pattern(pattern)

    def _validate_directory_patterns(self, fp_config: dict[str, Any]) -> None:
        """Validate all directory-specific patterns.

        Args:
            fp_config: File placement configuration section
        """
        if "directories" in fp_config:
            for _dir_path, rules in fp_config["directories"].items():
                self._validate_allow_patterns(rules)
                self._validate_deny_patterns(rules)

    def _validate_global_patterns(self, fp_config: dict[str, Any]) -> None:
        """Validate global patterns section.

        Args:
            fp_config: File placement configuration section
        """
        if "global_patterns" in fp_config:
            self._validate_allow_patterns(fp_config["global_patterns"])
            self._validate_deny_patterns(fp_config["global_patterns"])

    def _validate_global_deny_patterns(self, fp_config: dict[str, Any]) -> None:
        """Validate global_deny patterns.

        Args:
            fp_config: File placement configuration section
        """
        if "global_deny" in fp_config:
            for deny_item in fp_config["global_deny"]:
                pattern = deny_item.get("pattern", "")
                self._validate_pattern(pattern)
