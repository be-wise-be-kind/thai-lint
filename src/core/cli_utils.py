"""
Purpose: Shared CLI utilities for common Click command patterns across all linters

Scope: CLI command decorators, config loading, and violation output formatting

Overview: Provides reusable utilities for CLI commands to eliminate duplication across linter
    commands (dry, srp, nesting, file-placement). Includes common option decorators for consistent
    CLI interfaces, configuration file loading helpers, and violation output formatting for both
    text and JSON formats. Standardizes CLI patterns across all linter commands for maintainability
    and consistency.

Dependencies: click for CLI framework, pathlib for file paths, json for JSON output

Exports: common_linter_options decorator, load_linter_config, format_violations

Interfaces: Click decorators, config dict, violation list formatting

Implementation: Decorator composition for Click options, shared formatting logic for CLI output
"""

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import click


def common_linter_options(func: Callable) -> Callable:
    """Add common linter CLI options to command.

    Decorator that adds standard options used by all linter commands:
    - path argument (defaults to current directory)
    - --config/-c option for custom config file
    - --format/-f option for output format (text or json)
    - --recursive/--no-recursive option for directory traversal

    Args:
        func: Click command function to decorate

    Returns:
        Decorated function with common CLI options added
    """
    func = click.argument("path", type=click.Path(exists=True), default=".")(func)
    func = click.option(
        "--config", "-c", "config_file", type=click.Path(), help="Path to config file"
    )(func)
    func = click.option(
        "--format",
        "-f",
        type=click.Choice(["text", "json"]),
        default="text",
        help="Output format",
    )(func)
    func = click.option(
        "--recursive/--no-recursive", default=True, help="Scan directories recursively"
    )(func)
    return func


def load_linter_config(config_path: str | None) -> dict[str, Any]:
    """Load linter configuration from file or return empty dict.

    Args:
        config_path: Path to config file (optional)

    Returns:
        Configuration dictionary, empty dict if no config provided

    Raises:
        SystemExit: If config file path provided but file not found
    """
    if not config_path:
        return {}

    config_file = Path(config_path)
    _validate_config_file_exists(config_file, config_path)
    return _load_config_by_format(config_file)


def _validate_config_file_exists(config_file: Path, config_path: str) -> None:
    """Validate config file exists, exit if not found.

    Args:
        config_file: Path object for config file
        config_path: Original config path string for error message

    Raises:
        SystemExit: If config file not found
    """
    if not config_file.exists():
        click.echo(f"Error: Config file not found: {config_path}", err=True)
        sys.exit(2)


def _load_config_by_format(config_file: Path) -> dict[str, Any]:
    """Load config based on file extension.

    Args:
        config_file: Path to config file

    Returns:
        Loaded configuration dictionary
    """
    if config_file.suffix in {".yaml", ".yml"}:
        return _load_yaml_config(config_file)
    if config_file.suffix == ".json":
        return _load_json_config(config_file)
    # Fallback: attempt YAML
    return _load_yaml_config(config_file)


def _load_yaml_config(config_file: Path) -> dict[str, Any]:
    """Load YAML config file.

    Args:
        config_file: Path to YAML file

    Returns:
        Loaded configuration, empty dict if null
    """
    import yaml

    with config_file.open("r", encoding="utf-8") as f:
        result = yaml.safe_load(f)
        return dict(result) if result is not None else {}


def _load_json_config(config_file: Path) -> dict[str, Any]:
    """Load JSON config file.

    Args:
        config_file: Path to JSON file

    Returns:
        Loaded configuration
    """
    with config_file.open("r", encoding="utf-8") as f:
        result = json.load(f)
        return dict(result) if isinstance(result, dict) else {}


def format_violations(violations: list, output_format: str) -> None:
    """Format and print violations to console.

    Args:
        violations: List of violation objects with rule_id, file_path, line, column, message, severity
        output_format: Output format ("text", "json", or "sarif")
    """
    if output_format == "json":
        _output_json(violations)
    elif output_format == "sarif":
        _output_sarif(violations)
    else:
        _output_text(violations)


def _output_json(violations: list) -> None:
    """Output violations in JSON format.

    Args:
        violations: List of violation objects
    """
    output = {
        "violations": [
            {
                "rule_id": v.rule_id,
                "file_path": str(v.file_path),
                "line": v.line,
                "column": v.column,
                "message": v.message,
                "severity": v.severity.name,
            }
            for v in violations
        ],
        "total": len(violations),
    }
    click.echo(json.dumps(output, indent=2))


def _output_sarif(violations: list) -> None:
    """Output violations in SARIF v2.1.0 format.

    Args:
        violations: List of violation objects
    """
    from src.formatters.sarif import SarifFormatter

    formatter = SarifFormatter()
    sarif_doc = formatter.format(violations)
    click.echo(json.dumps(sarif_doc, indent=2))


def _output_text(violations: list) -> None:
    """Output violations in human-readable text format.

    Args:
        violations: List of violation objects
    """
    if not violations:
        click.echo("✓ No violations found")
        return

    click.echo(f"Found {len(violations)} violation(s):\n")
    for v in violations:
        _print_violation(v)


def _print_violation(v: Any) -> None:
    """Print single violation in text format.

    Args:
        v: Violation object with file_path, line, column, severity, rule_id, message
    """
    location = f"{v.file_path}:{v.line}" if v.line else str(v.file_path)
    if v.column:
        location += f":{v.column}"
    click.echo(f"  {location}")
    click.echo(f"    [{v.severity.name}] {v.rule_id}: {v.message}")
    click.echo()
