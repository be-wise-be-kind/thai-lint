"""
Purpose: CLI commands for infrastructure linters (version-freshness)

Scope: Commands that detect infrastructure and runtime version issues

Overview: Provides CLI commands for infrastructure-level linting: version-freshness checks
    runtime and infrastructure versions against endoflife.date lifecycle data to detect
    EOL and outdated versions in Dockerfiles, GitHub Actions, version-pinning files, and
    Terraform configs. Integrates with the standard CLI framework and supports text, JSON,
    and SARIF output formats. Supports --check-eol and --check-outdated CLI flags to
    override config file settings.

Dependencies: click for CLI framework, src.cli.main for CLI group, src.cli.linters.shared
    for helper functions, src.linters.version_freshness for linter implementation

Exports: version_freshness command

Interfaces: Click CLI command registered to main CLI group

Implementation: Manual Click command with custom options for check_eol and check_outdated flags

Suppressions:
    - too-many-arguments,too-many-positional-arguments: Click commands require many parameters
        by framework design (ctx + paths + config + format + check_eol + check_outdated +
        recursive + parallel = 8 params)
"""

import sys
from pathlib import Path

import click
from loguru import logger

from src.cli.linters.shared import extract_command_context
from src.cli.main import cli
from src.cli.utils import format_option, parallel_option, validate_paths_exist
from src.core.cli_utils import format_violations


def _load_version_freshness_config(config_file: str | None, project_root: Path | None) -> dict:
    """Load version-freshness config from file.

    Args:
        config_file: Optional explicit config file path
        project_root: Optional project root for default config discovery

    Returns:
        Config dict for version-freshness section
    """
    import yaml

    config_path = _find_config_path(config_file, project_root)
    if config_path is None:
        return {}

    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            section = data.get("version-freshness", {})
            return dict(section) if isinstance(section, dict) else {}
    except (yaml.YAMLError, OSError) as exc:
        logger.debug("Failed to load config: %s", exc)

    return {}


def _find_config_path(config_file: str | None, project_root: Path | None) -> Path | None:
    """Find the config file path.

    Args:
        config_file: Explicit config file path
        project_root: Project root for default discovery

    Returns:
        Path to config file, or None
    """
    if config_file:
        return _resolve_explicit_config(config_file)
    return _discover_default_config(project_root)


def _resolve_explicit_config(config_file: str) -> Path | None:
    """Resolve an explicit config file path.

    Args:
        config_file: Config file path string

    Returns:
        Path if it exists, None otherwise
    """
    path = Path(config_file)
    return path if path.exists() else None


def _discover_default_config(project_root: Path | None) -> Path | None:
    """Discover default config file in project root.

    Args:
        project_root: Project root directory, or None for cwd

    Returns:
        Path to first found config file, or None
    """
    root = project_root if project_root is not None else Path.cwd()
    for name in (".thailint.yaml", ".thailint.yml"):
        candidate = root / name
        if candidate.exists():
            return candidate
    return None


@cli.command("version-freshness")
@click.argument("paths", nargs=-1, type=click.Path())
@click.option("--config", "-c", "config_file", type=click.Path(), help="Path to config file")
@format_option
@click.option(
    "--check-eol/--no-check-eol",
    default=None,
    help="Check for end-of-life versions (overrides config)",
)
@click.option(
    "--check-outdated/--no-check-outdated",
    default=None,
    help="Check for outdated (non-latest) versions (overrides config)",
)
@click.option("--recursive/--no-recursive", default=True, help="Scan directories recursively")
@parallel_option
@click.pass_context
def version_freshness(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ctx: click.Context,
    paths: tuple[str, ...],
    config_file: str | None,
    format: str,
    check_eol: bool | None,
    check_outdated: bool | None,
    recursive: bool,
    parallel: bool,
) -> None:
    """Check runtime/infrastructure versions for EOL and outdated versions.

    Checks Dockerfiles, GitHub Actions workflows, version-pinning files,
    and Terraform configs against endoflife.date lifecycle data.
    Detects end-of-life (EOL) and optionally outdated runtime versions.

    PATHS: Files or directories to lint (defaults to current directory if none provided)

    Examples:

        \b
        # Check current directory (all files recursively)
        thai-lint version-freshness

        \b
        # Check specific directory
        thai-lint version-freshness src/

        \b
        # Also flag outdated (non-latest) versions
        thai-lint version-freshness --check-outdated .

        \b
        # Only check for outdated versions, skip EOL check
        thai-lint version-freshness --no-check-eol --check-outdated .

        \b
        # Get JSON output
        thai-lint version-freshness --format json .

        \b
        # Use custom config file
        thai-lint version-freshness --config .thailint.yaml src/
    """
    from src.linters.version_freshness.config import VersionFreshnessConfig
    from src.linters.version_freshness.linter import VersionFreshnessRule

    cmd_ctx = extract_command_context(ctx, paths)
    validate_paths_exist(cmd_ctx.path_objs)

    config_dict = _load_version_freshness_config(config_file, cmd_ctx.project_root)
    config = (
        VersionFreshnessConfig.from_dict(config_dict) if config_dict else VersionFreshnessConfig()
    )

    # CLI flags override config file settings
    if check_eol is not None:
        config = VersionFreshnessConfig(
            enabled=config.enabled,
            check_eol=check_eol,
            check_outdated=config.check_outdated,
            cache_ttl_hours=config.cache_ttl_hours,
            ignore=config.ignore,
        )
    if check_outdated is not None:
        config = VersionFreshnessConfig(
            enabled=config.enabled,
            check_eol=config.check_eol,
            check_outdated=check_outdated,
            cache_ttl_hours=config.cache_ttl_hours,
            ignore=config.ignore,
        )

    rule = VersionFreshnessRule(config)
    violations = rule.check_paths(cmd_ctx.path_objs)

    logger.debug(f"Found {len(violations)} version-freshness violation(s)")

    format_violations(violations, format)
    sys.exit(1 if violations else 0)
