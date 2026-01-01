"""
Purpose: CLI commands for performance linters (string-concat-loop, regex-in-loop)

Scope: Commands that detect performance anti-patterns in loops

Overview: Provides CLI commands for performance anti-pattern detection: string-concat-loop
    finds O(n^2) string concatenation using += in loops, regex-in-loop detects repeated
    regex compilation inside loops. Each command supports standard options (config, format,
    recursive) and integrates with the orchestrator for execution.

Dependencies: click for CLI framework, src.cli.main for CLI group, src.cli.utils for shared utilities,
    src.cli.linters.shared for linter-specific helpers

Exports: string_concat_loop command, regex_in_loop command

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
# String Concat Loop Command
# =============================================================================


def _setup_performance_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for performance linting."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_string_concat_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute string-concat-loop lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if v.rule_id == "performance.string-concat-loop"]


def _execute_string_concat_lint(params: ExecuteParams) -> NoReturn:
    """Execute string-concat-loop lint."""
    validate_paths_exist(params.path_objs)
    orchestrator = _setup_performance_orchestrator(
        params.path_objs, params.config_file, params.verbose, params.project_root
    )
    violations = _run_string_concat_lint(orchestrator, params.path_objs, params.recursive)

    if params.verbose:
        logger.info(f"Found {len(violations)} string-concat-loop violation(s)")

    format_violations(violations, params.format)
    sys.exit(1 if violations else 0)


string_concat_loop = create_linter_command(
    "string-concat-loop",
    _execute_string_concat_lint,
    "Check for string concatenation in loops.",
    "Detects O(n^2) string building patterns using += in for/while loops.\n"
    "    This is a common performance anti-pattern in Python and TypeScript.",
)


# =============================================================================
# Regex In Loop Command
# =============================================================================


def _run_regex_in_loop_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute regex-in-loop lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if v.rule_id == "performance.regex-in-loop"]


def _execute_regex_in_loop_lint(params: ExecuteParams) -> NoReturn:
    """Execute regex-in-loop lint."""
    validate_paths_exist(params.path_objs)
    orchestrator = _setup_performance_orchestrator(
        params.path_objs, params.config_file, params.verbose, params.project_root
    )
    violations = _run_regex_in_loop_lint(orchestrator, params.path_objs, params.recursive)

    if params.verbose:
        logger.info(f"Found {len(violations)} regex-in-loop violation(s)")

    format_violations(violations, params.format)
    sys.exit(1 if violations else 0)


regex_in_loop = create_linter_command(
    "regex-in-loop",
    _execute_regex_in_loop_lint,
    "Check for regex compilation in loops.",
    "Detects re.match(), re.search(), re.sub(), re.findall(), re.split(), and\n"
    "    re.fullmatch() calls inside loops. These recompile the regex pattern on\n"
    "    each iteration instead of compiling once with re.compile().",
)
