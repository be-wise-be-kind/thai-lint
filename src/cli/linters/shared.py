"""
Purpose: Shared utilities for linter CLI commands

Scope: Common helper functions and patterns used across all linter command modules

Overview: Provides reusable utilities for linter CLI commands including config section management,
    config value setting with logging, and rule ID filtering. Centralizes shared patterns to reduce
    duplication across linter command modules (code_quality, code_patterns, structure, documentation).
    All utilities are designed to work with the orchestrator configuration system.

Dependencies: logging for debug output, pathlib for Path type hints

Exports: ensure_config_section, set_config_value, filter_violations_by_prefix

Interfaces: Orchestrator config dict manipulation, violation list filtering

Implementation: Pure helper functions with no side effects beyond config mutation and logging
"""

import logging
from typing import TYPE_CHECKING, Any

from src.core.types import Violation

if TYPE_CHECKING:
    from src.orchestrator.core import Orchestrator

# Configure module logger
logger = logging.getLogger(__name__)


def ensure_config_section(orchestrator: "Orchestrator", section: str) -> dict[str, Any]:
    """Ensure a config section exists and return it.

    Args:
        orchestrator: Orchestrator instance with config dict
        section: Name of the config section to ensure exists

    Returns:
        The config section dict (created if it didn't exist)
    """
    if section not in orchestrator.config:
        orchestrator.config[section] = {}
    config_section: dict[str, Any] = orchestrator.config[section]
    return config_section


def set_config_value(config: dict[str, Any], key: str, value: Any, verbose: bool) -> None:
    """Set a config value with optional debug logging.

    Only sets the value if it is not None.

    Args:
        config: Config dict to update
        key: Config key to set
        value: Value to set (skipped if None)
        verbose: Whether to log the override
    """
    if value is None:
        return
    config[key] = value
    if verbose:
        logger.debug(f"Overriding {key} to {value}")


def filter_violations_by_prefix(violations: list[Violation], prefix: str) -> list[Violation]:
    """Filter violations to those matching a rule ID prefix.

    Args:
        violations: List of violation objects with rule_id attribute
        prefix: Prefix to match against rule_id

    Returns:
        Filtered list of violations where rule_id contains the prefix
    """
    return [v for v in violations if prefix in v.rule_id]


def filter_violations_by_startswith(violations: list[Violation], prefix: str) -> list[Violation]:
    """Filter violations to those with rule_id starting with prefix.

    Args:
        violations: List of violation objects with rule_id attribute
        prefix: Prefix that rule_id must start with

    Returns:
        Filtered list of violations where rule_id starts with the prefix
    """
    return [v for v in violations if v.rule_id.startswith(prefix)]
