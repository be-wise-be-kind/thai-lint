"""
Purpose: Main linter rule for detecting blocking operations in async Rust code

Scope: Entry point for blocking-in-async detection implementing BaseLintRule interface

Overview: Provides BlockingAsyncRule class that implements the BaseLintRule interface for
    detecting blocking API calls inside async functions in Rust code. Validates that files
    are Rust with content, loads configuration, checks ignored paths, and delegates analysis
    to RustBlockingAsyncAnalyzer. Filters detected calls based on configuration (allow_in_tests,
    pattern toggles, ignored paths) and converts remaining calls to Violation objects via the
    violation builder. Supports disabling via configuration.

Dependencies: BaseLintRule, RustBlockingAsyncAnalyzer, BlockingAsyncConfig, violation_builder

Exports: BlockingAsyncRule

Interfaces: check(context: BaseLintContext) -> list[Violation]

Implementation: Single-file analysis with config-driven filtering and tree-sitter-based detection
"""

from src.core.base import BaseLintContext, BaseLintRule
from src.core.linter_utils import has_file_content, load_linter_config
from src.core.types import Violation

from .config import BlockingAsyncConfig
from .rust_analyzer import BlockingCall, RustBlockingAsyncAnalyzer
from .violation_builder import (
    build_fs_in_async_violation,
    build_net_in_async_violation,
    build_sleep_in_async_violation,
)

_PATTERN_BUILDERS = {
    "fs-in-async": build_fs_in_async_violation,
    "sleep-in-async": build_sleep_in_async_violation,
    "net-in-async": build_net_in_async_violation,
}

_PATTERN_CONFIG_KEYS = {
    "fs-in-async": "detect_fs_in_async",
    "sleep-in-async": "detect_sleep_in_async",
    "net-in-async": "detect_net_in_async",
}


class BlockingAsyncRule(BaseLintRule):
    """Detects blocking operations inside async functions in Rust code."""

    def __init__(self, config: BlockingAsyncConfig | None = None) -> None:
        """Initialize blocking-in-async rule.

        Args:
            config: Optional configuration override for testing
        """
        self._config_override = config
        self._analyzer = RustBlockingAsyncAnalyzer()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "blocking-async"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Rust Blocking in Async"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return (
            "Detects blocking operations inside async functions in Rust code including "
            "std::fs I/O, std::thread::sleep, and blocking std::net calls. Suggests "
            "async-compatible alternatives like tokio::fs, tokio::time::sleep, and tokio::net."
        )

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for blocking-in-async violations in a Rust file.

        Args:
            context: Lint context with file content and metadata

        Returns:
            List of violations found
        """
        config = self._get_config(context)
        if not self._should_analyze(context, config):
            return []

        file_path = _resolve_file_path(context)
        calls = self._analyzer.find_blocking_calls(context.file_content or "")
        return self._build_violations(calls, config, file_path)

    def _should_analyze(self, context: BaseLintContext, config: BlockingAsyncConfig) -> bool:
        """Determine if the file should be analyzed.

        Args:
            context: Lint context to check
            config: Blocking-in-async configuration

        Returns:
            True if the file should be analyzed
        """
        if context.language != "rust":
            return False
        if not has_file_content(context):
            return False
        if not config.enabled:
            return False
        return not _is_ignored_path(_resolve_file_path(context), config)

    def _get_config(self, context: BaseLintContext) -> BlockingAsyncConfig:
        """Load configuration from override or context metadata.

        Args:
            context: Lint context with metadata

        Returns:
            BlockingAsyncConfig instance
        """
        if self._config_override is not None:
            return self._config_override
        return load_linter_config(context, "blocking-async", BlockingAsyncConfig)

    def _build_violations(
        self,
        calls: list[BlockingCall],
        config: BlockingAsyncConfig,
        file_path: str,
    ) -> list[Violation]:
        """Convert blocking calls to violations with config filtering.

        Args:
            calls: Detected blocking calls from analyzer
            config: Configuration for filtering
            file_path: Path of the analyzed file

        Returns:
            List of filtered violations
        """
        return [
            _build_violation_for_call(call, file_path)
            for call in calls
            if not _should_skip_call(call, config)
        ]


def _resolve_file_path(context: BaseLintContext) -> str:
    """Resolve file path from context.

    Args:
        context: Lint context

    Returns:
        File path string, or "unknown" if not available
    """
    return str(context.file_path) if context.file_path else "unknown"


def _is_ignored_path(file_path: str, config: BlockingAsyncConfig) -> bool:
    """Check if file path matches any ignore pattern.

    Args:
        file_path: Path to check
        config: Configuration with ignore patterns

    Returns:
        True if the path should be ignored
    """
    return any(ignored in file_path for ignored in config.ignore)


def _should_skip_call(call: BlockingCall, config: BlockingAsyncConfig) -> bool:
    """Determine if a blocking call should be skipped based on config.

    Args:
        call: Detected blocking call
        config: Configuration for filtering

    Returns:
        True if the call should be skipped
    """
    if call.is_in_test and config.allow_in_tests:
        return True
    config_key = _PATTERN_CONFIG_KEYS.get(call.pattern)
    if config_key and not getattr(config, config_key):
        return True
    return False


def _build_violation_for_call(call: BlockingCall, file_path: str) -> Violation:
    """Build a violation for a specific blocking call.

    Args:
        call: Detected blocking call with pattern info
        file_path: Path of the analyzed file

    Returns:
        Violation instance
    """
    builder = _PATTERN_BUILDERS.get(call.pattern, build_fs_in_async_violation)
    return builder(file_path, call.line, call.column, call.context)
