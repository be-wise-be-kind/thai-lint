"""
Purpose: File placement linter implementation

Scope: Validate file organization against allow/deny patterns

Overview: Implements file placement validation using regex patterns from JSON/YAML config.
    Orchestrates configuration loading, pattern validation, path resolution, rule checking,
    and violation creation through focused helper classes. Supports directory-specific rules,
    global patterns, and generates helpful suggestions. Main linter class acts as coordinator
    using composition pattern with specialized helper classes for configuration loading,
    path resolution, pattern matching, and violation creation.

Dependencies: src.core (base classes, types), pathlib, typing, json, yaml modules

Exports: FilePlacementLinter, FilePlacementRule

Interfaces: lint_path(file_path) -> list[Violation], check_file_allowed(file_path) -> bool,
    lint_directory(dir_path) -> list[Violation]

Implementation: Composition pattern with helper classes for each responsibility
    (ConfigLoader, PathResolver, PatternMatcher, PatternValidator, RuleChecker,
    ViolationFactory)
"""

import json
from pathlib import Path
from typing import Any

import yaml

from src.core.base import BaseLintContext, BaseLintRule
from src.core.types import Violation

from .config_loader import ConfigLoader
from .path_resolver import PathResolver
from .pattern_matcher import PatternMatcher
from .pattern_validator import PatternValidator
from .rule_checker import RuleChecker
from .violation_factory import ViolationFactory


class _Components:
    """Container for linter components to reduce instance attributes."""

    def __init__(self, project_root: Path):
        self.config_loader = ConfigLoader(project_root)
        self.path_resolver = PathResolver(project_root)
        self.pattern_matcher = PatternMatcher()
        self.pattern_validator = PatternValidator()
        self.violation_factory = ViolationFactory()
        self.rule_checker = RuleChecker(self.pattern_matcher, self.violation_factory)


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
        self._components = _Components(self.project_root)

        # Load and validate config
        if config_obj:
            # Handle both wrapped and unwrapped config formats
            # Wrapped: {"file-placement": {...}} or {"file_placement": {...}}
            # Unwrapped: {"directories": {...}, "global_deny": [...], ...}
            # Try both hyphenated and underscored keys for backward compatibility
            self.config = config_obj.get(
                "file-placement", config_obj.get("file_placement", config_obj)
            )
        elif config_file:
            self.config = self._components.config_loader.load_config_file(config_file)
        else:
            self.config = {}

        # Validate regex patterns in config
        self._components.pattern_validator.validate_config(self.config)

    def lint_path(self, file_path: Path) -> list[Violation]:
        """Lint a single file path.

        Args:
            file_path: File to lint

        Returns:
            List of violations found
        """
        rel_path = self._components.path_resolver.get_relative_path(file_path)
        path_str = self._components.path_resolver.normalize_path_string(rel_path)
        # Config is already unwrapped from file-placement key in _load_layout_config
        fp_config = self.config
        return self._components.rule_checker.check_all_rules(path_str, rel_path, fp_config)

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
        valid_files = self._get_valid_files(dir_path, recursive)
        return self._lint_files(valid_files)

    def _get_valid_files(self, dir_path: Path, recursive: bool) -> list[Path]:
        """Get list of valid files to lint from directory.

        Args:
            dir_path: Directory to scan
            recursive: Scan recursively

        Returns:
            List of file paths to lint
        """
        from src.linter_config.ignore import IgnoreDirectiveParser

        ignore_parser = IgnoreDirectiveParser(self.project_root)
        pattern = "**/*" if recursive else "*"

        return [
            f for f in dir_path.glob(pattern) if f.is_file() and not ignore_parser.is_ignored(f)
        ]

    def _lint_files(self, file_paths: list[Path]) -> list[Violation]:
        """Lint multiple files and collect violations.

        Args:
            file_paths: List of file paths to lint

        Returns:
            List of all violations found
        """
        violations = []
        for file_path in file_paths:
            violations.extend(self.lint_path(file_path))
        return violations


class FilePlacementRule(BaseLintRule):  # thailint: ignore[srp.violation]
    """File placement linting rule (integrates with framework).

    SRP suppression: Framework adapter class requires 13 methods to bridge
    BaseLintRule interface with FilePlacementLinter. See file header for justification.
    """

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

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check file placement.

        Args:
            context: Lint context

        Returns:
            List of violations
        """
        if not context.file_path:
            return []

        project_root = self._get_project_root(context)
        linter = self._get_or_create_linter(project_root, context)
        return linter.lint_path(context.file_path)

    def _get_project_root(self, context: BaseLintContext) -> Path:
        """Get project root from context or detect it.

        Args:
            context: Lint context

        Returns:
            Project root directory path
        """
        # Use project root from orchestrator metadata if available
        metadata_root = self._get_root_from_metadata(context)
        if metadata_root is not None:
            return metadata_root

        # Otherwise detect it from file path
        return self._detect_project_root(context)

    def _get_root_from_metadata(self, context: BaseLintContext) -> Path | None:
        """Extract project root from context metadata.

        Args:
            context: Lint context

        Returns:
            Project root from metadata, or None if not available
        """
        if not hasattr(context, "metadata"):
            return None
        if not context.metadata:
            return None
        if "_project_root" not in context.metadata:
            return None
        return context.metadata["_project_root"]

    def _detect_project_root(self, context: BaseLintContext) -> Path:
        """Detect project root from file path.

        Args:
            context: Lint context

        Returns:
            Detected project root directory path
        """
        from src.utils.project_root import get_project_root

        if context.file_path is None:
            return Path.cwd()

        start_path = context.file_path.parent if context.file_path.is_file() else context.file_path
        return get_project_root(start_path)

    def _extract_inline_config(self, context: BaseLintContext | None) -> dict[str, Any] | None:
        """Extract file-placement config from context metadata.

        Handles both wrapped format: {"file-placement": {...}}
        and unwrapped format: {"global_deny": [...], "directories": {...}, ...}

        Args:
            context: Lint context

        Returns:
            File placement config dict, or None if no config in metadata
        """
        if not self._has_valid_metadata(context):
            return None

        # Type narrowing: _has_valid_metadata ensures context is not None
        # by checking: context and hasattr(context, "metadata") and context.metadata
        if context is None:
            return None  # Should never happen after _has_valid_metadata check

        # Check for wrapped format first
        wrapped_config = self._get_wrapped_config(context)
        if wrapped_config is not None:
            return wrapped_config

        # Check for unwrapped format
        return self._get_unwrapped_config(context)

    def _has_valid_metadata(self, context: BaseLintContext | None) -> bool:
        """Check if context has valid metadata.

        Args:
            context: Lint context

        Returns:
            True if context has metadata dict
        """
        return bool(context and hasattr(context, "metadata") and context.metadata)

    @staticmethod
    def _get_wrapped_config(context: BaseLintContext) -> dict[str, Any] | None:
        """Get config from wrapped format: {"file-placement": {...}} or {"file_placement": {...}}.

        Supports both hyphenated and underscored keys for backward compatibility.

        Args:
            context: Lint context with metadata

        Returns:
            Config dict or None if not in wrapped format
        """
        if not hasattr(context, "metadata"):
            return None
        # Try hyphenated format first (original format)
        if "file-placement" in context.metadata:
            return context.metadata["file-placement"]
        # Try underscored format (normalized format)
        if "file_placement" in context.metadata:
            return context.metadata["file_placement"]
        return None

    @staticmethod
    def _get_unwrapped_config(context: BaseLintContext) -> dict[str, Any] | None:
        """Get config from unwrapped format: {"directories": {...}, ...}.

        Args:
            context: Lint context with metadata

        Returns:
            Config dict or None if not in unwrapped format
        """
        if not hasattr(context, "metadata"):
            return None

        config_keys = {"directories", "global_deny", "global_allow", "global_patterns"}
        matching_keys = {k: v for k, v in context.metadata.items() if k in config_keys}
        return matching_keys if matching_keys else None

    def _get_or_create_linter(
        self, project_root: Path, context: BaseLintContext | None = None
    ) -> FilePlacementLinter:
        """Get cached linter or create new one.

        Args:
            project_root: Project root directory
            context: Lint context (to extract inline config if present)

        Returns:
            FilePlacementLinter instance
        """
        # Check if cached linter exists for this project root
        if project_root in self._linter_cache:
            return self._linter_cache[project_root]

        # Try to get config from context metadata (orchestrator passes config here)
        config_from_metadata = self._extract_inline_config(context) if context else None

        if config_from_metadata:
            # Use config from orchestrator's metadata
            linter = FilePlacementLinter(config_obj=config_from_metadata, project_root=project_root)
        else:
            # Fall back to loading from file
            layout_path = self._get_layout_path(project_root)
            layout_config = self._load_layout_config(layout_path)
            linter = FilePlacementLinter(config_obj=layout_config, project_root=project_root)

        # Cache the linter
        self._linter_cache[project_root] = linter
        return linter

    def _get_layout_path(self, project_root: Path) -> Path:
        """Get layout config file path.

        Args:
            project_root: Project root directory

        Returns:
            Path to layout config file
        """
        layout_file = self.config.get("layout_file")
        if layout_file:
            return project_root / layout_file

        # Check for standard config files at project root
        thailint_yaml = project_root / ".thailint.yaml"
        thailint_json = project_root / ".thailint.json"

        for path in [thailint_yaml, thailint_json]:
            if path.exists():
                return path

        # Return default path if no config exists
        return thailint_yaml

    def _load_layout_config(self, layout_path: Path) -> dict[str, Any]:
        """Load layout configuration from file.

        Args:
            layout_path: Path to layout file

        Returns:
            Layout configuration dict (unwrapped from file-placement key), or empty dict on error
        """
        try:
            config = self._parse_layout_file(layout_path)

            # Unwrap file-placement key if present (try both formats for backward compatibility)
            if "file-placement" in config:
                return config["file-placement"]
            if "file_placement" in config:
                return config["file_placement"]

            return config
        except Exception:
            return {}

    def _parse_layout_file(self, layout_path: Path) -> dict[str, Any]:
        """Parse layout file based on extension.

        Args:
            layout_path: Path to layout file

        Returns:
            Parsed configuration dict
        """
        with layout_path.open(encoding="utf-8") as f:
            if str(layout_path).endswith((".yaml", ".yml")):
                return yaml.safe_load(f) or {}
            return json.load(f)
