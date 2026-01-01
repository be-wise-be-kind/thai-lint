"""
Purpose: CLI commands for code pattern linters (print-statements, method-property, stateless-class, lazy-ignores)

Scope: Commands that detect code patterns and anti-patterns in Python code

Overview: Provides CLI commands for code pattern linting: print-statements detects print() and
    console.log calls that should use proper logging, method-property finds methods that should be
    @property decorators, stateless-class detects classes without state that should be module
    functions, and lazy-ignores detects unjustified linting suppressions. Each command supports
    standard options (config, format, recursive) and integrates with the orchestrator for execution.

Dependencies: click for CLI framework, src.cli.main for CLI group, src.cli.utils for shared utilities

Exports: print_statements command, method_property command, stateless_class command, lazy_ignores command

Interfaces: Click CLI commands registered to main CLI group

Implementation: Click decorators for command definition, orchestrator-based linting execution
"""

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

from src.cli.linters.shared import ExecuteParams, create_linter_command
from src.cli.utils import execute_linting_on_paths, setup_base_orchestrator, validate_paths_exist
from src.core.cli_utils import format_violations
from src.core.types import Violation

if TYPE_CHECKING:
    from src.orchestrator.core import Orchestrator

# Configure module logger
logger = logging.getLogger(__name__)


# =============================================================================
# Print Statements Command
# =============================================================================


def _setup_print_statements_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for print-statements command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_print_statements_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute print-statements lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "print-statement" in v.rule_id]


def _execute_print_statements_lint(params: ExecuteParams) -> NoReturn:
    """Execute print-statements lint."""
    validate_paths_exist(params.path_objs)
    orchestrator = _setup_print_statements_orchestrator(
        params.path_objs, params.config_file, params.verbose, params.project_root
    )
    print_statements_violations = _run_print_statements_lint(
        orchestrator, params.path_objs, params.recursive
    )

    if params.verbose:
        logger.info(f"Found {len(print_statements_violations)} print statement violation(s)")

    format_violations(print_statements_violations, params.format)
    sys.exit(1 if print_statements_violations else 0)


print_statements = create_linter_command(
    "print-statements",
    _execute_print_statements_lint,
    "Check for print/console statements in code.",
    "Detects print() calls in Python and console.log/warn/error/debug/info calls\n"
    "    in TypeScript/JavaScript that should be replaced with proper logging.",
)


# =============================================================================
# Method Property Command
# =============================================================================


def _setup_method_property_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for method-property command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_method_property_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute method-property lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "method-property" in v.rule_id]


def _execute_method_property_lint(params: ExecuteParams) -> NoReturn:
    """Execute method-property lint."""
    validate_paths_exist(params.path_objs)
    orchestrator = _setup_method_property_orchestrator(
        params.path_objs, params.config_file, params.verbose, params.project_root
    )
    method_property_violations = _run_method_property_lint(
        orchestrator, params.path_objs, params.recursive
    )

    if params.verbose:
        logger.info(f"Found {len(method_property_violations)} method-property violation(s)")

    format_violations(method_property_violations, params.format)
    sys.exit(1 if method_property_violations else 0)


method_property = create_linter_command(
    "method-property",
    _execute_method_property_lint,
    "Check for methods that should be @property decorators.",
    "Detects Python methods that could be converted to properties following\n"
    "    Pythonic conventions: methods returning self._attribute, get_* prefixed\n"
    "    methods (Java-style getters), or simple computed values with no side effects.",
)


# =============================================================================
# Stateless Class Command
# =============================================================================


def _setup_stateless_class_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for stateless-class command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_stateless_class_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute stateless-class lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "stateless-class" in v.rule_id]


def _execute_stateless_class_lint(params: ExecuteParams) -> NoReturn:
    """Execute stateless-class lint."""
    validate_paths_exist(params.path_objs)
    orchestrator = _setup_stateless_class_orchestrator(
        params.path_objs, params.config_file, params.verbose, params.project_root
    )
    stateless_class_violations = _run_stateless_class_lint(
        orchestrator, params.path_objs, params.recursive
    )

    if params.verbose:
        logger.info(f"Found {len(stateless_class_violations)} stateless-class violation(s)")

    format_violations(stateless_class_violations, params.format)
    sys.exit(1 if stateless_class_violations else 0)


stateless_class = create_linter_command(
    "stateless-class",
    _execute_stateless_class_lint,
    "Check for stateless classes that should be module functions.",
    "Detects Python classes that have no constructor (__init__), no instance\n"
    "    state, and 2+ methods - indicating they should be refactored to module-level\n"
    "    functions instead of using a class as a namespace.",
)


# =============================================================================
# Lazy Ignores Command
# =============================================================================


def _setup_lazy_ignores_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for lazy-ignores command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_lazy_ignores_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute lazy-ignores lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if v.rule_id.startswith("lazy-ignores")]


def _execute_lazy_ignores_lint(params: ExecuteParams) -> NoReturn:
    """Execute lazy-ignores lint."""
    validate_paths_exist(params.path_objs)
    orchestrator = _setup_lazy_ignores_orchestrator(
        params.path_objs, params.config_file, params.verbose, params.project_root
    )
    lazy_ignores_violations = _run_lazy_ignores_lint(
        orchestrator, params.path_objs, params.recursive
    )

    if params.verbose:
        logger.info(f"Found {len(lazy_ignores_violations)} lazy-ignores violation(s)")

    format_violations(lazy_ignores_violations, params.format)
    sys.exit(1 if lazy_ignores_violations else 0)


lazy_ignores = create_linter_command(
    "lazy-ignores",
    _execute_lazy_ignores_lint,
    "Check for unjustified linting suppressions.",
    "Detects ignore directives (noqa, type:ignore, pylint:disable, nosec) that lack\n"
    "    corresponding entries in the file header's Suppressions section. Enforces a\n"
    "    header-based suppression model requiring human approval for all linting bypasses.",
)
