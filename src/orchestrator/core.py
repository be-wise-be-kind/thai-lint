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
    configurable linting through .thailint.yaml configuration files. Includes parallel processing
    support for improved performance on multi-core systems. Serves as the primary interface between
    the linter framework and user-facing CLI/library APIs.

Dependencies: pathlib for file operations, BaseLintRule and BaseLintContext from core.base,
    Violation from core.types, RuleRegistry from core.registry, LinterConfigLoader from
    linter_config.loader, IgnoreDirectiveParser from linter_config.ignore, detect_language
    from language_detector, concurrent.futures for parallel processing

Exports: Orchestrator class, FileLintContext implementation class

Interfaces: Orchestrator(project_root: Path | None), lint_file(file_path: Path) -> list[Violation],
    lint_directory(dir_path: Path, recursive: bool) -> list[Violation],
    lint_files_parallel(file_paths, max_workers) -> list[Violation]

Implementation: Directory glob pattern matching for traversal (** for recursive, * for shallow),
    ignore pattern checking before file processing, dynamic context creation per file,
    rule filtering by applicability, violation collection and aggregation across files,
    ProcessPoolExecutor for parallel file processing

Suppressions:
    - srp: Orchestrator class coordinates multiple subsystems by design (registry, config, ignore,
        language detection). Splitting would fragment the core linting workflow.
"""

from __future__ import annotations

import logging
import multiprocessing
import os
from concurrent.futures import Future, ProcessPoolExecutor, as_completed
from pathlib import Path

from src.core.base import BaseLintContext, BaseLintRule
from src.core.registry import RuleRegistry
from src.core.types import Violation
from src.linter_config.ignore import get_ignore_parser
from src.linter_config.loader import LinterConfigLoader

from .language_detector import detect_language

logger = logging.getLogger(__name__)

# Default max workers for parallel processing (capped to avoid resource contention)
DEFAULT_MAX_WORKERS = 8

# Hardcoded exclusions for files/directories that should never be linted
# These are always skipped regardless of configuration to improve performance
_HARDCODED_EXCLUDE_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".pyc",
        ".pyo",
        ".pyd",  # Python bytecode
        ".so",
        ".dll",
        ".dylib",  # Compiled libraries
        ".class",  # Java bytecode
        ".o",
        ".obj",  # Object files
    }
)
_HARDCODED_EXCLUDE_DIRS: frozenset[str] = frozenset(
    {
        "__pycache__",
        "node_modules",
        ".git",
        ".svn",
        ".hg",
        ".venv",
        "venv",
        ".tox",
        ".eggs",
        "*.egg-info",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
        "htmlcov",
    }
)


def _is_hardcoded_excluded(file_path: Path) -> bool:
    """Check if file should be excluded based on hardcoded patterns.

    Args:
        file_path: Path to check

    Returns:
        True if file should be skipped (compiled file, cache directory, etc.)
    """
    # Check file extension
    if file_path.suffix in _HARDCODED_EXCLUDE_EXTENSIONS:
        return True

    # Check if any parent directory is in the exclude list
    for part in file_path.parts:
        if part in _HARDCODED_EXCLUDE_DIRS:
            return True
        # Handle wildcard patterns like *.egg-info
        if part.endswith(".egg-info"):
            return True

    return False


def _should_include_dir(dirname: str) -> bool:
    """Check if directory should be traversed (not excluded)."""
    return dirname not in _HARDCODED_EXCLUDE_DIRS and not dirname.endswith(".egg-info")


def _collect_files_from_walk(root: str, filenames: list[str]) -> list[Path]:
    """Collect non-excluded files from a single directory."""
    root_path = Path(root)
    return [root_path / f for f in filenames if Path(f).suffix not in _HARDCODED_EXCLUDE_EXTENSIONS]


def _collect_files_fast(dir_path: Path, recursive: bool = True) -> list[Path]:
    """Collect files, skipping excluded directories entirely.

    Uses os.walk() instead of glob to avoid traversing into excluded
    directories like .venv, node_modules, __pycache__, etc.

    Args:
        dir_path: Directory to collect files from.
        recursive: Whether to traverse subdirectories.

    Returns:
        List of file paths, excluding hardcoded exclusions.
    """
    files: list[Path] = []
    for root, dirs, filenames in os.walk(dir_path):
        dirs[:] = [d for d in dirs if _should_include_dir(d)]
        files.extend(_collect_files_from_walk(root, filenames))
        if not recursive:
            break
    return files


def _lint_file_worker(args: tuple[Path, Path, dict]) -> list[dict]:
    """Worker function for parallel file linting.

    This function runs in a separate process and creates its own Orchestrator
    instance to lint a single file. Results are returned as dicts to avoid
    pickling issues with Violation dataclass.

    Args:
        args: Tuple of (file_path, project_root, config)

    Returns:
        List of violation dicts (serializable for cross-process transfer)
    """
    file_path, project_root, config = args
    try:
        # Create isolated orchestrator for this worker process
        orchestrator = Orchestrator(project_root=project_root, config=config)
        violations = orchestrator.lint_file(file_path)
        # Convert to dicts for pickling
        return [v.to_dict() for v in violations]
    except Exception:
        logger.exception("Worker error processing file: %s", file_path)
        return []


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
        self._lines: list[str] | None = None  # Cached line split
        self.metadata = metadata or {}

    @property
    def file_path(self) -> Path | None:
        """Get file path being analyzed."""
        return self._path

    @property
    def file_content(self) -> str | None:
        """Get file content being analyzed."""
        if self._content is not None:
            return self._content
        if not self._path or not self._path.exists():
            return None
        try:
            self._content = self._path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            self._content = None
        return self._content

    @property
    def language(self) -> str:
        """Get programming language of file."""
        return self._language

    @property
    def file_lines(self) -> list[str]:
        """Get file content as list of lines (cached).

        Returns:
            List of lines from file content, empty list if no content.
        """
        if self._lines is None:
            content = self.file_content
            self._lines = content.split("\n") if content else []
        return self._lines


class Orchestrator:  # thailint: ignore[srp]
    """Main linter orchestrator coordinating rule execution.

    Integrates rule registry, configuration loading, ignore patterns, and language
    detection to provide comprehensive linting of files and directories.

    SRP Exception: Method count (12) exceeds guideline (8) because this is the
    central orchestration point. Methods are organized into logical groups:
    - Core linting: lint_file, lint_files, lint_directory
    - Parallel linting: lint_files_parallel, lint_directory_parallel
    - Helper methods: _execute_rules, _safe_check_rule, _ensure_rules_discovered, etc.
    All methods support the single responsibility of coordinating lint operations.
    """

    def __init__(self, project_root: Path | None = None, config: dict | None = None):
        """Initialize orchestrator.

        Args:
            project_root: Root directory of project. Defaults to current directory.
            config: Optional pre-loaded configuration dict. If provided, skips config file loading.
        """
        self.project_root = project_root or Path.cwd()
        self.registry = RuleRegistry()
        self.config_loader = LinterConfigLoader()
        self.ignore_parser = get_ignore_parser(self.project_root)

        # Performance optimization: Defer rule discovery until first file is linted
        # This eliminates ~0.077s overhead for commands that don't need rules (--help, config, etc.)
        self._rules_discovered = False

        # Use provided config or load from project root
        if config is not None:
            self.config = config
        else:
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
        # Fast path: skip compiled files and common excluded directories
        if _is_hardcoded_excluded(file_path):
            return []

        if self.ignore_parser.is_ignored(file_path):
            return []

        language = detect_language(file_path)
        rules = self._get_rules_for_file(file_path, language)

        # Add project_root to metadata for rules that need it (e.g., DRY linter cache)
        metadata = {**self.config, "_project_root": self.project_root}
        context = FileLintContext(file_path, language, metadata=metadata)

        return self._execute_rules(rules, context)

    def lint_files(self, file_paths: list[Path]) -> list[Violation]:
        """Lint multiple files.

        Args:
            file_paths: List of file paths to lint.

        Returns:
            List of violations found across all files.
        """
        violations = []

        for file_path in file_paths:
            violations.extend(self.lint_file(file_path))

        # Call finalize() on all rules after processing all files
        for rule in self.registry.list_all():
            violations.extend(rule.finalize())

        return violations

    def _execute_rules(
        self, rules: list[BaseLintRule], context: BaseLintContext
    ) -> list[Violation]:
        """Execute rules and collect violations.

        Args:
            rules: List of rules to execute.
            context: Lint context to pass to rules.

        Returns:
            List of violations found.
        """
        violations = []
        for rule in rules:
            rule_violations = self._safe_check_rule(rule, context)
            violations.extend(rule_violations)
        return violations

    def _safe_check_rule(self, rule: BaseLintRule, context: BaseLintContext) -> list[Violation]:
        """Safely check a rule, returning empty list on error."""
        try:
            return rule.check(context)
        except ValueError:
            # Re-raise configuration validation errors (these are user-facing)
            raise
        except Exception:
            logger.exception("Rule %s failed on %s", rule.rule_id, context.file_path)
            return []

    def lint_directory(self, dir_path: Path, recursive: bool = True) -> list[Violation]:
        """Lint all files in a directory.

        Args:
            dir_path: Path to directory to lint.
            recursive: Whether to traverse subdirectories recursively.

        Returns:
            List of all violations found across all files.
        """
        violations = []
        # Use fast file collection that skips excluded directories entirely
        file_paths = _collect_files_fast(dir_path, recursive)

        for file_path in file_paths:
            violations.extend(self.lint_file(file_path))

        # Call finalize() on all rules after processing all files
        for rule in self.registry.list_all():
            violations.extend(rule.finalize())

        return violations

    def lint_files_parallel(
        self, file_paths: list[Path], max_workers: int | None = None
    ) -> list[Violation]:
        """Lint multiple files in parallel using process pool.

        Uses ProcessPoolExecutor to distribute file linting across multiple
        CPU cores. Each worker process creates its own Orchestrator instance.

        Args:
            file_paths: List of file paths to lint.
            max_workers: Maximum worker processes. Defaults to min(DEFAULT_MAX_WORKERS, cpu_count).

        Returns:
            List of violations found across all files.
        """
        if not file_paths:
            return []

        effective_workers = max_workers or min(DEFAULT_MAX_WORKERS, multiprocessing.cpu_count())

        # For small file counts, sequential is faster due to process overhead
        if len(file_paths) < effective_workers * 2:
            return self.lint_files(file_paths)

        violations = self._execute_parallel_linting(file_paths, effective_workers)
        violations.extend(self._finalize_rules())
        return violations

    def _execute_parallel_linting(
        self, file_paths: list[Path], max_workers: int
    ) -> list[Violation]:
        """Execute parallel linting using process pool."""
        work_items = [(fp, self.project_root, self.config) for fp in file_paths]

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(_lint_file_worker, item) for item in work_items]
            return self._collect_parallel_results(futures)

    def _collect_parallel_results(self, futures: list[Future[list[dict]]]) -> list[Violation]:
        """Collect results from parallel futures."""
        violations: list[Violation] = []
        for future in as_completed(futures):
            violations.extend(self._extract_violations_from_future(future))
        return violations

    def _extract_violations_from_future(self, future: Future[list[dict]]) -> list[Violation]:
        """Extract violations from a completed future, handling errors."""
        try:
            return [Violation.from_dict(d) for d in future.result()]
        except Exception:
            logger.exception("Error extracting violations from worker future")
            return []

    def _finalize_rules(self) -> list[Violation]:
        """Call finalize() on all rules for cross-file analysis."""
        self._ensure_rules_discovered()
        violations: list[Violation] = []
        for rule in self.registry.list_all():
            violations.extend(rule.finalize())
        return violations

    def lint_directory_parallel(
        self, dir_path: Path, recursive: bool = True, max_workers: int | None = None
    ) -> list[Violation]:
        """Lint all files in a directory using parallel processing.

        Args:
            dir_path: Path to directory to lint.
            recursive: Whether to traverse subdirectories recursively.
            max_workers: Maximum worker processes. Defaults to min(DEFAULT_MAX_WORKERS, cpu_count).

        Returns:
            List of all violations found across all files.
        """
        # Use fast file collection that skips excluded directories entirely
        file_paths = _collect_files_fast(dir_path, recursive)
        return self.lint_files_parallel(file_paths, max_workers=max_workers)

    def _ensure_rules_discovered(self) -> None:
        """Ensure rules have been discovered and registered (lazy initialization)."""
        if not self._rules_discovered:
            self.registry.discover_rules("src.linters")
            self._rules_discovered = True

    def _get_rules_for_file(self, file_path: Path, language: str) -> list[BaseLintRule]:
        """Get rules applicable to this file.

        Args:
            file_path: Path to file being linted.
            language: Detected programming language.

        Returns:
            List of rules to execute against this file.
        """
        # Lazy initialization: discover rules on first lint operation
        self._ensure_rules_discovered()

        # For now, return all registered rules
        # Future: filter by language, configuration, etc.
        return self.registry.list_all()
