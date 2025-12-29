"""
Purpose: Configuration for lazy-ignores linter

Scope: All configurable options for ignore detection

Overview: Provides LazyIgnoresConfig dataclass with pattern-specific toggles for each
    ignore type (noqa, type:ignore, pylint, nosec, typescript, eslint, thailint). Includes
    orphaned detection toggle and file pattern ignores. Configuration can be loaded from
    dictionary (YAML) with sensible defaults for all options.

Dependencies: dataclasses, typing

Exports: LazyIgnoresConfig

Interfaces: LazyIgnoresConfig.from_dict() for YAML configuration loading

Implementation: Dataclass with factory defaults and validation in from_dict

Suppressions:
    too-many-instance-attributes: Configuration dataclass requires many toggles
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LazyIgnoresConfig:  # pylint: disable=too-many-instance-attributes
    """Configuration for the lazy-ignores linter."""

    # Pattern detection toggles
    check_noqa: bool = True
    check_type_ignore: bool = True
    check_pylint_disable: bool = True
    check_nosec: bool = True
    check_ts_ignore: bool = True
    check_eslint_disable: bool = True
    check_thailint_ignore: bool = True
    check_test_skips: bool = True

    # Orphaned detection
    check_orphaned: bool = True  # Header entries without matching ignores

    # File patterns to ignore
    ignore_patterns: list[str] = field(
        default_factory=lambda: [
            "tests/**",  # Don't enforce in test files by default
            "**/__pycache__/**",
        ]
    )

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "LazyIgnoresConfig":
        """Create config from dictionary."""
        return cls(
            check_noqa=config_dict.get("check_noqa", True),
            check_type_ignore=config_dict.get("check_type_ignore", True),
            check_pylint_disable=config_dict.get("check_pylint_disable", True),
            check_nosec=config_dict.get("check_nosec", True),
            check_ts_ignore=config_dict.get("check_ts_ignore", True),
            check_eslint_disable=config_dict.get("check_eslint_disable", True),
            check_thailint_ignore=config_dict.get("check_thailint_ignore", True),
            check_test_skips=config_dict.get("check_test_skips", True),
            check_orphaned=config_dict.get("check_orphaned", True),
            ignore_patterns=config_dict.get("ignore_patterns", []),
        )
