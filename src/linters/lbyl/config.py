"""
Purpose: Configuration dataclass for LBYL linter

Scope: Pattern toggles, ignore patterns, and validation

Overview: Provides LBYLConfig dataclass with pattern-specific toggles for each LBYL
    pattern type (dict_key, hasattr, isinstance, file_exists, len_check, none_check,
    string_validation, division_check). Some patterns like isinstance and none_check
    are disabled by default due to many valid use cases. Configuration can be loaded
    from dictionary (YAML) with sensible defaults.

Dependencies: dataclasses, typing

Exports: LBYLConfig

Interfaces: LBYLConfig.from_dict() for YAML configuration loading

Implementation: Dataclass with factory defaults and conservative default settings

Suppressions:
    too-many-instance-attributes: Configuration dataclass requires many toggles
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LBYLConfig:  # pylint: disable=too-many-instance-attributes
    """Configuration for LBYL linter."""

    enabled: bool = True

    # Pattern toggles
    detect_dict_key: bool = True
    detect_hasattr: bool = True
    detect_isinstance: bool = False  # Disabled - many valid uses for type narrowing
    detect_file_exists: bool = True
    detect_len_check: bool = True
    detect_none_check: bool = False  # Disabled - many valid uses
    detect_string_validation: bool = True
    detect_division_check: bool = True

    # File patterns to ignore
    ignore: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, config: dict[str, Any], language: str | None = None) -> "LBYLConfig":
        """Load configuration from dictionary."""
        # Language parameter reserved for future multi-language support
        _ = language
        return cls(
            enabled=config.get("enabled", True),
            detect_dict_key=config.get("detect_dict_key", True),
            detect_hasattr=config.get("detect_hasattr", True),
            detect_isinstance=config.get("detect_isinstance", False),
            detect_file_exists=config.get("detect_file_exists", True),
            detect_len_check=config.get("detect_len_check", True),
            detect_none_check=config.get("detect_none_check", False),
            detect_string_validation=config.get("detect_string_validation", True),
            detect_division_check=config.get("detect_division_check", True),
            ignore=config.get("ignore", []),
        )
