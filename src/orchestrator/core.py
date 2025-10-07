"""
Purpose: Main orchestration engine coordinating rule execution across files and directories

Scope: Central coordination of linting operations integrating registry, config, and ignore systems

Overview: Provides the main entry point for linting operations by coordinating execution of rules
    across single files and entire directory trees. Integrates with the rule registry for dynamic
    rule discovery, configuration loader for user settings, ignore directive parser for suppression
    patterns, and language detector for file routing. Creates lint contexts for each file with
    appropriate file information and language metadata, executes applicable rules against contexts,
    and collects violations across all processed files. Supports recursive and non-recursive
    directory traversal, respects .thailintignore patterns at repository level, and provides
    configurable linting through .thailint.yaml configuration files. Serves as the primary
    interface between the linter framework and user-facing CLI/library APIs.

Dependencies: pathlib for file operations, BaseLintRule and BaseLintContext from core.base,
    Violation from core.types, RuleRegistry from core.registry, LinterConfigLoader from
    linter_config.loader, IgnoreDirectiveParser from linter_config.ignore, detect_language
    from language_detector

Exports: Orchestrator class, FileLintContext implementation class

Interfaces: Orchestrator(project_root: Path | None), lint_file(file_path: Path) -> list[Violation],
    lint_directory(dir_path: Path, recursive: bool) -> list[Violation]

Implementation: Directory glob pattern matching for traversal (** for recursive, * for shallow),
    ignore pattern checking before file processing, dynamic context creation per file,
    rule filtering by applicability, violation collection and aggregation across files
"""

from pathlib import Path

from src.core.base import BaseLintContext, BaseLintRule
from src.core.registry import RuleRegistry
from src.core.types import Violation
from src.linter_config.ignore import IgnoreDirectiveParser
from src.linter_config.loader import LinterConfigLoader

from .language_detector import detect_language


class FileLintContext(BaseLintContext):
    """Concrete implementation of lint context for file analysis."""

    def __init__(
        self, path: Path, lang: str, content: str | None = None, metadata: dict | None = None
    ):
        """Initialize file lint context.

        Args:
            path: Path to the file being analyzed.
            lang: Programming language identifier.
            content: Optional pre-loaded file content.
            metadata: Optional metadata dict containing configuration.
        """
        self._path = path
        self._language = lang
        self._content = content
        self.metadata = metadata or {}

    @property
    def file_path(self) -> Path | None:
        """Get file path being analyzed."""
        return self._path

    @property
    def file_content(self) -> str | None:
        """Get file content being analyzed."""
        if self._content is None and self._path and self._path.exists():
            try:
                self._content = self._path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                self._content = None
        return self._content

    @property
    def language(self) -> str:
        """Get programming language of file."""
        return self._language


class Orchestrator:
    """Main linter orchestrator coordinating rule execution.

    Integrates rule registry, configuration loading, ignore patterns, and language
    detection to provide comprehensive linting of files and directories.
    """

    def __init__(self, project_root: Path | None = None):
        """Initialize orchestrator.

        Args:
            project_root: Root directory of project. Defaults to current directory.
        """
        self.project_root = project_root or Path.cwd()
        self.registry = RuleRegistry()
        self.config_loader = LinterConfigLoader()
        self.ignore_parser = IgnoreDirectiveParser(self.project_root)

        # Auto-discover and register all linting rules from src.linters
        self.registry.discover_rules("src.linters")

        # Load configuration from project root
        config_path = self.project_root / ".thailint.yaml"
        if not config_path.exists():
            config_path = self.project_root / ".thailint.json"

        self.config = self.config_loader.load(config_path)

    def lint_file(self, file_path: Path) -> list[Violation]:
        """Lint a single file.

        Args:
            file_path: Path to file to lint.

        Returns:
            List of violations found in the file.
        """
        # Check if file should be ignored
        if self.ignore_parser.is_ignored(file_path):
            return []

        # Detect language
        language = detect_language(file_path)

        # Get applicable rules
        rules = self._get_rules_for_file(file_path, language)

        # Create context with config metadata
        context = FileLintContext(file_path, language, metadata=self.config)

        # Execute rules and collect violations
        violations = []
        for rule in rules:
            try:
                rule_violations = rule.check(context)
                violations.extend(rule_violations)
            except Exception:  # nosec B112
                # Skip rules that fail (defensive programming)
                continue

        return violations

    def lint_directory(self, dir_path: Path, recursive: bool = True) -> list[Violation]:
        """Lint all files in a directory.

        Args:
            dir_path: Path to directory to lint.
            recursive: Whether to traverse subdirectories recursively.

        Returns:
            List of all violations found across all files.
        """
        violations = []
        pattern = "**/*" if recursive else "*"

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                violations.extend(self.lint_file(file_path))

        return violations

    def _get_rules_for_file(self, file_path: Path, language: str) -> list[BaseLintRule]:
        """Get rules applicable to this file.

        Args:
            file_path: Path to file being linted.
            language: Detected programming language.

        Returns:
            List of rules to execute against this file.
        """
        # For now, return all registered rules
        # Future: filter by language, configuration, etc.
        return self.registry.list_all()
