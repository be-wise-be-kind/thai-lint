"""
Purpose: Package initialization for version-freshness linter

Scope: Exports for the version-freshness linter module

Overview: Provides the public API for the version-freshness linter that checks
    infrastructure and runtime versions against endoflife.date lifecycle data.
    Detects EOL and outdated versions in Dockerfiles, GitHub Actions workflows,
    version-pinning files (.python-version, .nvmrc), and Terraform configs.

Dependencies: config, cache, product_mapper, extractors, checker, scanner, linter submodules

Exports: VersionFreshnessConfig, VersionFreshnessRule, ExtractedVersion, VersionStatus

Interfaces: VersionFreshnessRule.check_paths(paths) -> list[Violation]

Implementation: Re-exports from submodules for convenient top-level imports
"""

from src.linters.version_freshness.checker import VersionStatus
from src.linters.version_freshness.config import VersionFreshnessConfig
from src.linters.version_freshness.linter import VersionFreshnessRule
from src.linters.version_freshness.product_mapper import ExtractedVersion

__all__ = [
    "VersionFreshnessConfig",
    "VersionFreshnessRule",
    "ExtractedVersion",
    "VersionStatus",
]
