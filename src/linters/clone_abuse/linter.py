"""
Purpose: Main linter rule for detecting clone abuse in Rust code

Scope: Entry point for clone abuse detection implementing BaseLintRule interface

Overview: Provides CloneAbuseRule class that implements the BaseLintRule interface for
    detecting .clone() abuse patterns in Rust code. Validates that files are Rust with
    content, loads configuration, checks ignored paths, and delegates analysis to
    RustCloneAnalyzer. Filters detected calls based on configuration (allow_in_tests,
    pattern toggles, ignored paths) and converts remaining calls to Violation objects
    via the violation builder. Supports disabling via configuration.

Dependencies: BaseLintRule, RustCloneAnalyzer, CloneAbuseConfig, violation_builder

Exports: CloneAbuseRule

Interfaces: check(context: BaseLintContext) -> list[Violation]

Implementation: Single-file analysis with config-driven filtering and tree-sitter-based detection
"""

from src.core.base import BaseLintContext, BaseLintRule
from src.core.linter_utils import (
    has_file_content,
    is_ignored_path,
    load_linter_config,
    resolve_file_path,
)
from src.core.types import Violation

from .config import CloneAbuseConfig
from .rust_analyzer import CloneCall, RustCloneAnalyzer
from .violation_builder import (
    build_clone_chain_violation,
    build_clone_in_loop_violation,
    build_unnecessary_clone_violation,
)

_PATTERN_BUILDERS = {
    "clone-in-loop": build_clone_in_loop_violation,
    "clone-chain": build_clone_chain_violation,
    "unnecessary-clone": build_unnecessary_clone_violation,
}

_PATTERN_CONFIG_KEYS = {
    "clone-in-loop": "detect_clone_in_loop",
    "clone-chain": "detect_clone_chain",
    "unnecessary-clone": "detect_unnecessary_clone",
}


class CloneAbuseRule(BaseLintRule):
    """Detects clone abuse patterns in Rust code."""

    def __init__(self, config: CloneAbuseConfig | None = None) -> None:
        """Initialize clone abuse rule.

        Args:
            config: Optional configuration override for testing
        """
        self._config_override = config
        self._analyzer = RustCloneAnalyzer()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "clone-abuse"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Rust Clone Abuse"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return (
            "Detects .clone() abuse patterns in Rust code including clone in loops, "
            "chained clones, and unnecessary clones. Suggests safer alternatives like "
            "borrowing, Rc/Arc, or Cow patterns."
        )

    def check(self, context: BaseLintContext) -> list[Violation]:
        """Check for clone abuse violations in a Rust file.

        Args:
            context: Lint context with file content and metadata

        Returns:
            List of violations found
        """
        config = self._get_config(context)
        if not self._should_analyze(context, config):
            return []

        file_path = resolve_file_path(context)
        calls = self._analyzer.find_clone_calls(context.file_content or "")
        return self._build_violations(calls, config, file_path)

    def _should_analyze(self, context: BaseLintContext, config: CloneAbuseConfig) -> bool:
        """Determine if the file should be analyzed.

        Args:
            context: Lint context to check
            config: Clone abuse configuration

        Returns:
            True if the file should be analyzed
        """
        if context.language != "rust":
            return False
        if not has_file_content(context):
            return False
        if not config.enabled:
            return False
        return not is_ignored_path(resolve_file_path(context), config.ignore)

    def _get_config(self, context: BaseLintContext) -> CloneAbuseConfig:
        """Load configuration from override or context metadata.

        Args:
            context: Lint context with metadata

        Returns:
            CloneAbuseConfig instance
        """
        if self._config_override is not None:
            return self._config_override
        return load_linter_config(context, "clone-abuse", CloneAbuseConfig)

    def _build_violations(
        self,
        calls: list[CloneCall],
        config: CloneAbuseConfig,
        file_path: str,
    ) -> list[Violation]:
        """Convert clone calls to violations with config filtering.

        Args:
            calls: Detected clone calls from analyzer
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


def _should_skip_call(call: CloneCall, config: CloneAbuseConfig) -> bool:
    """Determine if a clone call should be skipped based on config.

    Args:
        call: Detected clone call
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


def _build_violation_for_call(call: CloneCall, file_path: str) -> Violation:
    """Build a violation for a specific clone call.

    Args:
        call: Detected clone call with pattern info
        file_path: Path of the analyzed file

    Returns:
        Violation instance
    """
    builder = _PATTERN_BUILDERS.get(call.pattern, build_clone_in_loop_violation)
    return builder(file_path, call.line, call.column, call.context)
