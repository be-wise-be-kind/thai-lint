"""
Purpose: High-level Library API providing clean programmatic interface for thailint

Scope: Public API for library usage without CLI, supporting configuration and linting operations

Overview: Provides high-level Linter class that serves as the primary entry point for using
    thailint as a library in other Python applications. Wraps the Orchestrator with a clean,
    user-friendly API that handles configuration loading, path normalization, rule filtering,
    and violation collection. Supports initialization with config files or project roots,
    autodiscovery of .thailint.yaml/.thailint.json in project directory, and flexible linting
    with optional rule filtering. Designed for embedding in editors, CI/CD pipelines, testing
    frameworks, and automation tools. Maintains backwards compatibility with existing direct
    imports while providing improved ergonomics for library users.

Dependencies: pathlib for path handling, Orchestrator from orchestrator.core for linting engine,
    LinterConfigLoader from linter_config.loader for configuration, Violation from core.types

Exports: Linter class as primary library API

Interfaces: Linter(config_file=None, project_root=None) initialization,
    lint(path, rules=None) -> list[Violation] method

Implementation: Thin wrapper around Orchestrator with enhanced configuration handling,
    path normalization (str/Path support), rule filtering by name, and graceful error handling
"""

from pathlib import Path

from src.core.types import Violation
from src.linter_config.loader import LinterConfigLoader
from src.orchestrator.core import Orchestrator


class Linter:
    """High-level linter API for programmatic usage.

    Provides clean interface for using thailint as a library without CLI.
    Supports configuration files, project root detection, and rule filtering.

    Example:
        >>> from src import Linter
        >>> linter = Linter(config_file='.thailint.yaml')
        >>> violations = linter.lint('src/', rules=['file-placement'])
    """

    def __init__(
        self,
        config_file: str | Path | None = None,
        project_root: str | Path | None = None,
    ):
        """Initialize linter with configuration.

        Args:
            config_file: Path to config file (.thailint.yaml or .thailint.json).
                If not provided, will autodiscover in project_root.
            project_root: Root directory of project. Defaults to current directory.
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.config_loader = LinterConfigLoader()

        config_path = self._resolve_config_path(config_file)
        self.config = self.config_loader.load(config_path)
        self.orchestrator = Orchestrator(project_root=self.project_root, config=self.config)

    def _resolve_config_path(self, config_file: str | Path | None) -> Path:
        """Resolve configuration file path."""
        if config_file:
            return Path(config_file)

        yaml_path = self.project_root / ".thailint.yaml"
        if yaml_path.exists():
            return yaml_path
        return self.project_root / ".thailint.json"

    def lint(
        self,
        path: str | Path,
        rules: list[str] | None = None,
    ) -> list[Violation]:
        """Lint a file or directory.

        Args:
            path: Path to file or directory to lint. Accepts string or Path.
            rules: Optional list of rule names to run. If None, runs all rules.
                Example: ['file-placement']

        Returns:
            List of violations found.

        Example:
            >>> linter = Linter()
            >>> violations = linter.lint('src/', rules=['file-placement'])
            >>> for v in violations:
            ...     print(f"{v.file_path}: {v.message}")
        """
        path_obj = Path(path) if isinstance(path, str) else path

        if not path_obj.exists():
            return []

        violations = self._lint_path(path_obj)
        return self._filter_violations(violations, rules)

    def _lint_path(self, path_obj: Path) -> list[Violation]:
        """Lint a path (file or directory)."""
        if path_obj.is_file():
            return self.orchestrator.lint_file(path_obj)
        if path_obj.is_dir():
            return self.orchestrator.lint_directory(path_obj, recursive=True)
        return []

    def _filter_violations(
        self, violations: list[Violation], rules: list[str] | None
    ) -> list[Violation]:
        """Filter violations by rule names."""
        if rules:
            return [v for v in violations if v.rule_id in rules]
        return violations
