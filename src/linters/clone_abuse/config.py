"""
Purpose: Configuration dataclass for Rust clone abuse detector

Scope: Pattern toggles, ignore patterns, and configuration for clone abuse detection

Overview: Provides CloneAbuseConfig dataclass with toggles for controlling detection of
    .clone() abuse patterns in Rust code. Supports toggling detection of clone-in-loop,
    clone-chain, and unnecessary-clone patterns independently. Includes configuration for
    allowing calls in test code, ignoring example and benchmark directories. Configuration
    loads from YAML with sensible defaults via from_dict() class method.

Dependencies: dataclasses, typing

Exports: CloneAbuseConfig

Interfaces: CloneAbuseConfig.from_dict() for YAML configuration loading

Implementation: Dataclass with factory defaults and conservative default settings
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CloneAbuseConfig:
    """Configuration for clone abuse detection."""

    enabled: bool = True

    # Allow .clone() in test functions and #[cfg(test)] modules
    allow_in_tests: bool = True

    # Toggle detection of .clone() inside loop bodies
    detect_clone_in_loop: bool = True

    # Toggle detection of chained .clone().clone() calls
    detect_clone_chain: bool = True

    # Toggle detection of unnecessary clones (clone before move)
    detect_unnecessary_clone: bool = True

    # File path patterns to ignore (e.g., examples/, benches/)
    ignore: list[str] = field(default_factory=lambda: ["examples/", "benches/"])

    @classmethod
    def from_dict(cls, config: dict[str, Any], language: str | None = None) -> "CloneAbuseConfig":
        """Load configuration from dictionary.

        Args:
            config: Configuration dictionary from YAML
            language: Language parameter (reserved for future use)

        Returns:
            Configured CloneAbuseConfig instance
        """
        _ = language
        return cls(
            enabled=config.get("enabled", True),
            allow_in_tests=config.get("allow_in_tests", True),
            detect_clone_in_loop=config.get("detect_clone_in_loop", True),
            detect_clone_chain=config.get("detect_clone_chain", True),
            detect_unnecessary_clone=config.get("detect_unnecessary_clone", True),
            ignore=config.get("ignore", ["examples/", "benches/"]),
        )
