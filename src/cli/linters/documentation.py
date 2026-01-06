"""
Purpose: CLI commands for documentation linters (file-header)

Scope: Commands that validate documentation standards in source files

Overview: Provides CLI commands for documentation linting: file-header validates that source files
    have proper documentation headers with required fields (Purpose, Scope, Overview, etc.) and
    detects temporal language patterns (dates, temporal qualifiers, state change references).
    Supports Python, TypeScript, JavaScript, Bash, Markdown, and CSS files. Integrates with the
    orchestrator for execution.

Dependencies: click for CLI framework, src.cli.main for CLI group, src.cli.utils for shared utilities

Exports: file_header command

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
# File Header Command
# =============================================================================


def _setup_file_header_orchestrator(
    path_objs: list[Path], config_file: str | None, verbose: bool, project_root: Path | None = None
) -> "Orchestrator":
    """Set up orchestrator for file-header command."""
    return setup_base_orchestrator(path_objs, config_file, verbose, project_root)


def _run_file_header_lint(
    orchestrator: "Orchestrator", path_objs: list[Path], recursive: bool
) -> list[Violation]:
    """Execute file-header lint on files or directories."""
    all_violations = execute_linting_on_paths(orchestrator, path_objs, recursive)
    return [v for v in all_violations if "file-header" in v.rule_id]


def _execute_file_header_lint(params: ExecuteParams) -> NoReturn:
    """Execute file-header lint."""
    validate_paths_exist(params.path_objs)
    orchestrator = _setup_file_header_orchestrator(
        params.path_objs, params.config_file, params.verbose, params.project_root
    )
    file_header_violations = _run_file_header_lint(orchestrator, params.path_objs, params.recursive)

    if params.verbose:
        logger.info(f"Found {len(file_header_violations)} file header violation(s)")

    format_violations(file_header_violations, params.format)
    sys.exit(1 if file_header_violations else 0)


file_header = create_linter_command(
    "file-header",
    _execute_file_header_lint,
    "Check file headers for mandatory fields and atemporal language.",
    "Validates that source files have proper documentation headers containing\n"
    "    required fields (Purpose, Scope, Overview, etc.) and don't use temporal\n"
    "    language (dates, 'currently', 'now', etc.). Supports Python, TypeScript,\n"
    "    JavaScript, Bash, Markdown, and CSS files.",
)
