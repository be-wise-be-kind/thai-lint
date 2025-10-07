"""
Purpose: Package initialization and version definition for CLI application

Scope: Package-level exports and metadata

Overview: Initializes the CLI application package, defines version number using semantic versioning,
    and exports the public API. Provides single source of truth for version information used by
    setup tools, CLI help text, and documentation. Exports main CLI entry point, high-level Linter
    class for library usage, configuration utilities, and direct linter imports for advanced usage.
    Includes nesting depth linter exports for convenient access to nesting analysis functionality.

Dependencies: None (minimal imports for package initialization)

Exports: __version__, Linter (high-level API), cli (CLI entry point), load_config, save_config,
    ConfigError, Orchestrator (advanced usage), file_placement_lint, nesting_lint, NestingDepthRule

Interfaces: Package version string, Linter class API, CLI command group, configuration functions
"""

__version__ = "0.1.0"

# High-level Library API (primary interface)
from src.api import Linter

# CLI interface
from src.cli import cli
from src.config import ConfigError, load_config, save_config

# Advanced/direct imports (backwards compatibility)
from src.linters.file_placement import lint as file_placement_lint
from src.linters.nesting import NestingDepthRule
from src.linters.nesting import lint as nesting_lint
from src.orchestrator.core import Orchestrator

__all__ = [
    "__version__",
    # Primary Library API
    "Linter",
    # CLI
    "cli",
    "load_config",
    "save_config",
    "ConfigError",
    # Advanced/direct usage (backwards compatibility)
    "Orchestrator",
    "file_placement_lint",
    "nesting_lint",
    "NestingDepthRule",
]
