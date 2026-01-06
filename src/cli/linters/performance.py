"""
Purpose: CLI commands for performance linters (string-concat-loop, regex-in-loop, perf)

Scope: Commands that detect performance anti-patterns in loops

Overview: Provides CLI commands for performance anti-pattern detection: string-concat-loop
    finds O(n^2) string concatenation using += in loops, regex-in-loop detects repeated
    regex compilation inside loops. The `perf` command runs all performance rules together
    with optional --rule flag to select specific rules. Each command supports standard options
    (config, format, recursive) and integrates with the orchestrator for execution.

Dependencies: click for CLI framework, src.cli.main for CLI group, src.cli.utils for shared utilities,
    src.cli.linters.shared for linter-specific helpers

Exports: string_concat_loop command, regex_in_loop command, perf command

Interfaces: Click CLI commands registered to main CLI group

Implementation: Click decorators for command definition, orchestrator-based linting execution

Suppressions:
    - too-many-arguments,too-many-positional-arguments: Click commands with custom options require
      additional parameters beyond the standard 5 (ctx + 4 standard options). The perf command adds
      --rule option for 6 total parameters - framework design requirement for CLI extensibility.
"""

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

import click

from src.cli.linters.shared import (
    ExecuteParams,
    create_linter_command,
    prepare_standard_command,
    run_linter_command,
    standard_linter_options,
)
from src.cli.main import cli
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


def _setup_and_validate(params: ExecuteParams) -> "Orchestrator":
    """Validate paths and set up orchestrator for linting.

    Common setup code extracted to avoid DRY violations across execute functions.
    """
    validate_paths_exist(params.path_objs)
    return _setup_performance_orchestrator(
        params.path_objs, params.config_file, params.verbose, params.project_root
    )


def _run_string_concat_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute string-concat-loop lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if v.rule_id == "performance.string-concat-loop"]


def _execute_string_concat_lint(params: ExecuteParams) -> NoReturn:
    """Execute string-concat-loop lint."""
    orchestrator = _setup_and_validate(params)
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
    orchestrator = _setup_and_validate(params)
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


# =============================================================================
# Combined Perf Command
# =============================================================================

# Valid rule names for the --rule option
PERF_RULES = {
    "string-concat": "performance.string-concat-loop",
    "regex-loop": "performance.regex-in-loop",
    # Also accept full rule names
    "string-concat-loop": "performance.string-concat-loop",
    "regex-in-loop": "performance.regex-in-loop",
}


def _filter_by_rule(violations: list[Violation], rule: str | None) -> list[Violation]:
    """Filter violations by rule name if specified.

    Args:
        violations: List of violations to filter
        rule: Optional rule name (string-concat, regex-loop, or full rule names)

    Returns:
        Filtered list of violations
    """
    if not rule:
        return violations

    rule_id = PERF_RULES.get(rule)
    if not rule_id:
        logger.warning(f"Unknown rule '{rule}'. Valid rules: {', '.join(PERF_RULES.keys())}")
        return violations

    return [v for v in violations if v.rule_id == rule_id]


def _run_all_perf_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool, rule: str | None
) -> list[Violation]:
    """Execute all performance lints on files or directories.

    Args:
        orchestrator: Configured orchestrator instance
        path_objs: List of paths to analyze
        recursive: Whether to scan directories recursively
        rule: Optional rule filter (string-concat, regex-loop, or full rule names)

    Returns:
        List of performance-related violations
    """
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    perf_violations = [v for v in all_violations if v.rule_id.startswith("performance.")]
    return _filter_by_rule(perf_violations, rule)


def _execute_perf_lint(params: ExecuteParams, rule: str | None) -> NoReturn:
    """Execute combined performance lint."""
    orchestrator = _setup_and_validate(params)
    violations = _run_all_perf_lint(orchestrator, params.path_objs, params.recursive, rule)

    if params.verbose:
        logger.info(f"Found {len(violations)} performance violation(s)")

    format_violations(violations, params.format)
    sys.exit(1 if violations else 0)


@cli.command(
    "perf",
    help="""Check for performance anti-patterns in code.

    Detects common performance issues in loops:
    - string-concat-loop: O(n^2) string building using += in loops
    - regex-in-loop: Regex recompilation on each loop iteration

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \\b
        # Check current directory for all performance issues
        thai-lint perf

        \\b
        # Check specific directory
        thai-lint perf src/

        \\b
        # Check only string concatenation issues
        thai-lint perf --rule string-concat src/

        \\b
        # Check only regex-in-loop issues
        thai-lint perf --rule regex-loop src/

        \\b
        # Get JSON output
        thai-lint perf --format json .

        \\b
        # Use custom config file
        thai-lint perf --config .thailint.yaml src/
    """,
)
@click.option(
    "--rule",
    "-r",
    "rule",
    type=click.Choice(["string-concat", "regex-loop"]),
    help="Run only a specific performance rule",
)
@standard_linter_options
def perf(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    recursive: bool,
    rule: str | None,
) -> None:
    """Run all performance linters.

    Args:
        ctx: Click context with global options
        paths: Files or directories to lint
        config_file: Optional path to config file
        format: Output format (text, json, sarif)
        recursive: Whether to scan directories recursively
        rule: Optional rule filter (string-concat or regex-loop)
    """
    params = prepare_standard_command(ctx, paths, config_file, format, recursive)

    def execute_with_rule(p: ExecuteParams) -> None:
        _execute_perf_lint(p, rule)

    run_linter_command(execute_with_rule, params)
