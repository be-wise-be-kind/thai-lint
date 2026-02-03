"""
Purpose: Configuration dataclass for Rust unwrap abuse detector

Scope: Pattern toggles, ignore patterns, and configuration for unwrap/expect detection

Overview: Provides UnwrapAbuseConfig dataclass with toggles for controlling detection of
    .unwrap() and .expect() calls in Rust code. Supports configuration for allowing calls
    in test code, example files, and benchmark directories. Includes an option to allow
    .expect() calls (which provide error context) while still flagging bare .unwrap() calls.
    Configuration loads from YAML with sensible defaults via from_dict() class method.

Dependencies: dataclasses, typing

Exports: UnwrapAbuseConfig

Interfaces: UnwrapAbuseConfig.from_dict() for YAML configuration loading

Implementation: Dataclass with factory defaults and conservative default settings
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UnwrapAbuseConfig:
    """Configuration for unwrap abuse detection."""

    enabled: bool = True

    # Allow .unwrap()/.expect() in test functions and #[cfg(test)] modules
    allow_in_tests: bool = True

    # Allow .expect() calls (they provide error context unlike bare .unwrap()).
    # Defaults to True because .expect("reason") is the Rust community recommended
    # alternative to bare .unwrap(), providing panic context.
    allow_expect: bool = True

    # File path patterns to ignore (e.g., examples/, benches/)
    ignore: list[str] = field(default_factory=lambda: ["examples/", "benches/", "tests/"])

    @classmethod
    def from_dict(cls, config: dict[str, Any], language: str | None = None) -> "UnwrapAbuseConfig":
        """Load configuration from dictionary.

        Args:
            config: Configuration dictionary from YAML
            language: Language parameter (reserved for future use)

        Returns:
            Configured UnwrapAbuseConfig instance
        """
        _ = language
        return cls(
            enabled=config.get("enabled", True),
            allow_in_tests=config.get("allow_in_tests", True),
            allow_expect=config.get("allow_expect", True),
            ignore=config.get("ignore", ["examples/", "benches/", "tests/"]),
        )
