"""
Purpose: Main linter rule for detecting unwrap/expect abuse in Rust code

Scope: Entry point for unwrap abuse detection implementing BaseLintRule interface

Overview: Provides UnwrapAbuseRule class that implements the BaseLintRule interface for
    detecting .unwrap() and .expect() abuse in Rust code. Validates that files are Rust
    with content, loads configuration, checks ignored paths, and delegates analysis to
    RustUnwrapAnalyzer. Filters detected calls based on configuration (allow_in_tests,
    allow_expect, ignored paths) and converts remaining calls to Violation objects via
    the violation builder. Supports disabling via configuration.

Dependencies: BaseLintRule, RustUnwrapAnalyzer, UnwrapAbuseConfig, violation_builder

Exports: UnwrapAbuseRule

Interfaces: check(context: BaseLintContext) -> list[Violation]

Implementation: Single-file analysis with config-driven filtering and tree-sitter-based detection
"""

from src.core.base import BaseLintContext, BaseLintRule
from src.core.linter_utils import has_file_content, load_linter_config
from src.core.types import Violation

from .config import UnwrapAbuseConfig
from .rust_analyzer import RustUnwrapAnalyzer, UnwrapCall
from .violation_builder import build_expect_violation, build_unwrap_violation


class UnwrapAbuseRule(BaseLintRule):
    """Detects unwrap/expect abuse in Rust code."""

    def __init__(self, config: UnwrapAbuseConfig | None = None) -> None:
        """Initialize the unwrap abuse rule.

        Args:
            config: Optional configuration override for testing
        """
        self._config_override = config
        self._analyzer = RustUnwrapAnalyzer()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "unwrap-abuse"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Rust Unwrap Abuse"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return (
            "Detects .unwrap() and .expect() calls in Rust code that may panic at runtime. "
            "Suggests safer alternatives like the ? operator, unwrap_or(), unwrap_or_default(), "
            "or match/if-let expressions."
        )

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for unwrap/expect abuse in Rust code.

        Args:
            context: The lint context containing file information.

        Returns:
            List of violations found.
        """
        config = self._get_config(context)
        if not self._should_analyze(context, config):
            return []

        file_path = _resolve_file_path(context)
        calls = self._analyzer.find_unwrap_calls(context.file_content or "")
        return self._build_violations(calls, config, file_path)

    def _should_analyze(self, context: BaseLintContext, config: UnwrapAbuseConfig) -> bool:
        """Check if context should be analyzed.

        Args:
            context: Lint context to check
            config: Active configuration

        Returns:
            True if file is Rust with content and rule is enabled
        """
        if context.language != "rust":
            return False
        if not has_file_content(context):
            return False
        if not config.enabled:
            return False
        return not _is_ignored_path(_resolve_file_path(context), config)

    def _get_config(self, context: BaseLintContext) -> UnwrapAbuseConfig:
        """Get configuration, using override if provided.

        Args:
            context: Lint context for loading config from metadata

        Returns:
            Configuration instance
        """
        if self._config_override is not None:
            return self._config_override
        return load_linter_config(context, "unwrap-abuse", UnwrapAbuseConfig)

    def _build_violations(
        self,
        calls: list[UnwrapCall],
        config: UnwrapAbuseConfig,
        file_path: str,
    ) -> list[Violation]:
        """Convert filtered unwrap calls to violations.

        Args:
            calls: Detected unwrap/expect calls
            config: Active configuration
            file_path: Path to the file being analyzed

        Returns:
            List of violations for non-excluded calls
        """
        return [
            _build_violation_for_call(call, file_path)
            for call in calls
            if not self._should_skip_call(call, config)
        ]

    def _should_skip_call(self, call: UnwrapCall, config: UnwrapAbuseConfig) -> bool:
        """Determine if a detected call should be skipped based on config.

        Args:
            call: Detected unwrap/expect call
            config: Active configuration

        Returns:
            True if the call should be excluded from violations
        """
        if call.is_in_test and config.allow_in_tests:
            return True
        if call.method == "expect" and config.allow_expect:
            return True
        return False


def _resolve_file_path(context: BaseLintContext) -> str:
    """Extract file path string from context.

    Args:
        context: Lint context containing file information

    Returns:
        File path as string, or "unknown" if not available
    """
    return str(context.file_path) if context.file_path else "unknown"


def _is_ignored_path(file_path: str, config: UnwrapAbuseConfig) -> bool:
    """Check if file path matches any ignored patterns.

    Args:
        file_path: File path to check
        config: Configuration with ignore patterns

    Returns:
        True if the path should be ignored
    """
    return any(ignored in file_path for ignored in config.ignore)


def _build_violation_for_call(call: UnwrapCall, file_path: str) -> Violation:
    """Build the appropriate violation for a detected call.

    Args:
        call: Detected unwrap/expect call
        file_path: Path to the file

    Returns:
        Violation object for the call
    """
    if call.method == "unwrap":
        return build_unwrap_violation(file_path, call.line, call.column, call.context)
    return build_expect_violation(file_path, call.line, call.column, call.context)
