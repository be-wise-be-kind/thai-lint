"""
Purpose: CLI commands for Rust-specific linters (unwrap-abuse)

Scope: Commands that detect Rust-specific anti-patterns and code smells

Overview: Provides CLI commands for Rust code linting: unwrap-abuse detects .unwrap() and
    .expect() calls that may panic at runtime and suggests safer alternatives. Each command
    supports standard options (config, format, recursive) and integrates with the orchestrator
    for execution. Designed to be extended with additional Rust linter commands (clone-abuse,
    blocking-async) as they are implemented.

Dependencies: click for CLI framework, src.cli.main for CLI group, src.cli.utils for shared utilities

Exports: unwrap_abuse command

Interfaces: Click CLI commands registered to main CLI group

Implementation: Click decorators for command definition, orchestrator-based linting execution
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

from loguru import logger

from src.cli.linters.shared import ExecuteParams, create_linter_command
from src.cli.utils import execute_linting_on_paths, setup_base_orchestrator, validate_paths_exist
from src.core.cli_utils import format_violations
from src.core.types import Violation

if TYPE_CHECKING:
    from src.orchestrator.core import Orchestrator


# =============================================================================
# Unwrap Abuse Command
# =============================================================================


def _setup_unwrap_abuse_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for unwrap-abuse command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_unwrap_abuse_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool, parallel: bool = False
) -> list[Violation]:
    """Execute unwrap-abuse lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive, parallel)
    return [v for v in all_violations if v.rule_id.startswith("unwrap-abuse")]


def _execute_unwrap_abuse_lint(params: ExecuteParams) -> NoReturn:
    """Execute unwrap-abuse lint."""
    validate_paths_exist(params.path_objs)
    orchestrator = _setup_unwrap_abuse_orchestrator(
        params.path_objs, params.config_file, params.verbose, params.project_root
    )
    unwrap_abuse_violations = _run_unwrap_abuse_lint(
        orchestrator, params.path_objs, params.recursive, params.parallel
    )

    logger.debug(f"Found {len(unwrap_abuse_violations)} unwrap abuse violation(s)")

    format_violations(unwrap_abuse_violations, params.format)
    sys.exit(1 if unwrap_abuse_violations else 0)


unwrap_abuse = create_linter_command(
    "unwrap-abuse",
    _execute_unwrap_abuse_lint,
    "Check for .unwrap() and .expect() abuse in Rust code.",
    "Detects .unwrap() and .expect() calls in Rust code that may panic at runtime.\n"
    "    Suggests safer alternatives like the ? operator, unwrap_or(),\n"
    "    unwrap_or_default(), or match/if-let expressions.\n"
    "    Ignores calls in #[test] functions and #[cfg(test)] modules by default.",
)
