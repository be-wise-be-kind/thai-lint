"""
Purpose: Configuration dataclass for Rust blocking-in-async detector

Scope: Pattern toggles, ignore patterns, and configuration for blocking-in-async detection

Overview: Provides BlockingAsyncConfig dataclass with toggles for controlling detection of
    blocking operations inside async functions in Rust code. Supports toggling detection of
    std::fs operations, std::thread::sleep, and blocking network calls independently. Includes
    configuration for allowing calls in test code, ignoring example and benchmark directories.
    Configuration loads from YAML with sensible defaults via from_dict() class method.

Dependencies: dataclasses, typing

Exports: BlockingAsyncConfig

Interfaces: BlockingAsyncConfig.from_dict() for YAML configuration loading

Implementation: Dataclass with factory defaults and conservative default settings
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BlockingAsyncConfig:
    """Configuration for blocking-in-async detection."""

    enabled: bool = True

    # Allow blocking calls in test functions and #[cfg(test)] modules
    allow_in_tests: bool = True

    # Toggle detection of std::fs operations in async functions
    detect_fs_in_async: bool = True

    # Toggle detection of std::thread::sleep in async functions
    detect_sleep_in_async: bool = True

    # Toggle detection of std::net blocking calls in async functions
    detect_net_in_async: bool = True

    # File path patterns to ignore (e.g., examples/, benches/)
    ignore: list[str] = field(default_factory=lambda: ["examples/", "benches/", "tests/"])

    @classmethod
    def from_dict(
        cls, config: dict[str, Any], language: str | None = None
    ) -> "BlockingAsyncConfig":
        """Load configuration from dictionary.

        Args:
            config: Configuration dictionary from YAML
            language: Language parameter (reserved for future use)

        Returns:
            Configured BlockingAsyncConfig instance
        """
        _ = language
        return cls(
            enabled=config.get("enabled", True),
            allow_in_tests=config.get("allow_in_tests", True),
            detect_fs_in_async=config.get("detect_fs_in_async", True),
            detect_sleep_in_async=config.get("detect_sleep_in_async", True),
            detect_net_in_async=config.get("detect_net_in_async", True),
            ignore=config.get("ignore", ["examples/", "benches/", "tests/"]),
        )
