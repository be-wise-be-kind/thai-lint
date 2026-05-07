"""
Purpose: Main linter rule for version freshness checking

Scope: Orchestrates scanning, checking, and violation reporting for version freshness

Overview: Implements VersionFreshnessRule which inherits from BaseLintRule for
    compatibility with the framework. The check() method is a no-op since this linter
    does not use the orchestrator's language-dispatch pipeline. Instead, check_paths()
    is the real entry point: it scans paths for version declarations, fetches lifecycle
    data from endoflife.date (via cache), checks versions, and returns Violation objects.
    Integrates with the standard ignore system via IgnoreDirectiveParser for line-level,
    block-level, file-level, and repository-level suppression.

Dependencies: BaseLintRule, Violation, VersionFreshnessConfig, cache, scanner, checker,
    IgnoreDirectiveParser

Exports: VersionFreshnessRule class

Interfaces: check_paths(paths) -> list[Violation], check(context) -> list[Violation] (no-op)

Implementation: Path-based scanning with per-product API data fetching, ignore integration
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from src.core.base import BaseLintContext, BaseLintRule
from src.core.types import Violation
from src.linters.version_freshness import cache, checker, scanner
from src.linters.version_freshness.checker import VersionStatus
from src.linters.version_freshness.config import VersionFreshnessConfig
from src.linters.version_freshness.product_mapper import ExtractedVersion

if TYPE_CHECKING:
    from src.linter_config.ignore import IgnoreDirectiveParser

logger = logging.getLogger(__name__)

RULE_EOL = "version-freshness.eol-version"
RULE_OUTDATED = "version-freshness.outdated-runtime"


class VersionFreshnessRule(BaseLintRule):
    """Check infrastructure/runtime versions against endoflife.date lifecycle data."""

    def __init__(self, config: VersionFreshnessConfig | None = None) -> None:
        """Initialize with configuration.

        Args:
            config: Linter configuration, uses defaults if None
        """
        self._config = config or VersionFreshnessConfig()
        self._ignore_parser = _get_lazy_ignore_parser()

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "version-freshness"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Version Freshness"

    @property
    def description(self) -> str:
        """Description of what this rule checks."""
        return "Checks runtime/infrastructure versions against endoflife.date lifecycle data"

    def check(self, context: BaseLintContext) -> list[Violation]:
        """No-op: this linter uses check_paths() instead of the orchestrator pipeline.

        Args:
            context: Unused lint context

        Returns:
            Empty list (always)
        """
        return []

    def check_paths(self, paths: list[Path]) -> list[Violation]:
        """Scan paths for version declarations and check against lifecycle data.

        Args:
            paths: Files or directories to scan

        Returns:
            List of violations found
        """
        if not self._config.enabled:
            return []

        versions = self._scan_all_paths(paths)
        return self._check_all_versions(versions)

    def _scan_all_paths(self, paths: list[Path]) -> list[ExtractedVersion]:
        """Scan all paths and collect extracted versions.

        Args:
            paths: Files or directories to scan

        Returns:
            List of all extracted versions
        """
        results: list[ExtractedVersion] = []
        for path in paths:
            if path.is_dir():
                results.extend(scanner.scan_directory(path, self._config.ignore))
            elif path.is_file():
                results.extend(scanner.scan_file(path))
        return results

    def _check_all_versions(self, versions: list[ExtractedVersion]) -> list[Violation]:
        """Check all extracted versions and build violations.

        Args:
            versions: Extracted versions to check

        Returns:
            List of violations
        """
        violations: list[Violation] = []
        product_data_cache: dict[str, list[dict] | None] = {}

        for extracted in versions:
            product_data = self._get_product_data(extracted.product, product_data_cache)
            if product_data is None:
                continue
            status = checker.check_version(extracted, product_data)
            self._add_violations_for_status(status, violations)

        return violations

    def _get_product_data(
        self, product: str, data_cache: dict[str, list[dict] | None]
    ) -> list[dict] | None:
        """Get product data with local caching per scan run.

        Args:
            product: endoflife.date product name
            data_cache: Local cache dict for this scan run

        Returns:
            Product lifecycle data, or None if unavailable
        """
        if product not in data_cache:
            data_cache[product] = cache.get_product_data(product, self._config.cache_ttl_hours)
        return data_cache[product]

    def _add_violations_for_status(
        self, status: VersionStatus, violations: list[Violation]
    ) -> None:
        """Create violations from a version status check.

        Args:
            status: Result of checking a version
            violations: List to append violations to
        """
        self._check_eol_violation(status, violations)
        self._check_outdated_violation(status, violations)

    def _check_eol_violation(self, status: VersionStatus, violations: list[Violation]) -> None:
        """Check and add EOL violation if applicable.

        Args:
            status: Result of checking a version
            violations: List to append violations to
        """
        if self._config.check_eol and status.is_eol:
            self._append_if_not_ignored(_build_eol_violation(status), status.extracted, violations)

    def _check_outdated_violation(self, status: VersionStatus, violations: list[Violation]) -> None:
        """Check and add outdated violation if applicable.

        Args:
            status: Result of checking a version
            violations: List to append violations to
        """
        if self._config.check_outdated and status.is_outdated and not status.is_eol:
            self._append_if_not_ignored(
                _build_outdated_violation(status), status.extracted, violations
            )

    def _append_if_not_ignored(
        self, violation: Violation, extracted: ExtractedVersion, violations: list[Violation]
    ) -> None:
        """Append violation to list if not suppressed by ignore directives.

        Args:
            violation: Violation to potentially add
            extracted: Extracted version for file context
            violations: List to append to
        """
        if not self._should_ignore(violation, extracted):
            violations.append(violation)

    def _should_ignore(self, violation: Violation, extracted: ExtractedVersion) -> bool:
        """Check if a violation should be suppressed by ignore directives.

        Args:
            violation: The violation to check
            extracted: The extracted version for file context

        Returns:
            True if violation should be suppressed
        """
        try:
            file_content = Path(extracted.file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return False
        return self._ignore_parser.should_ignore_violation(violation, file_content)


def _build_eol_violation(status: VersionStatus) -> Violation:
    """Build a violation for an EOL version.

    Args:
        status: Version status with EOL information

    Returns:
        Violation object
    """
    eol_info = f" (EOL: {status.eol_date})" if status.eol_date else ""
    suggestion = f"Upgrade to {status.latest_cycle}" if status.latest_cycle else None
    return Violation(
        rule_id=RULE_EOL,
        file_path=status.extracted.file_path,
        line=status.extracted.line,
        column=status.extracted.column,
        message=(f"{status.extracted.product} {status.cycle} has reached end of life{eol_info}"),
        suggestion=suggestion,
    )


def _build_outdated_violation(status: VersionStatus) -> Violation:
    """Build a violation for an outdated (but supported) version.

    Args:
        status: Version status with outdated information

    Returns:
        Violation object
    """
    return Violation(
        rule_id=RULE_OUTDATED,
        file_path=status.extracted.file_path,
        line=status.extracted.line,
        column=status.extracted.column,
        message=(
            f"{status.extracted.product} {status.cycle} is not the latest supported version"
            f" (latest: {status.latest_cycle})"
        ),
        suggestion=f"Consider upgrading to {status.latest_cycle}",
    )


def _get_lazy_ignore_parser() -> IgnoreDirectiveParser:
    """Get ignore parser with lazy import to avoid circular dependencies.

    Returns:
        IgnoreDirectiveParser instance
    """
    from src.linter_config.ignore import get_ignore_parser

    return get_ignore_parser()
