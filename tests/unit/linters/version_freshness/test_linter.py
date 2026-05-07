"""
Purpose: Unit tests for version-freshness linter (end-to-end with mocked cache)

Scope: End-to-end linting, config options, violation messages, ignore integration

Overview: Tests the VersionFreshnessRule end-to-end with mocked cache data.
    Covers EOL violation generation, outdated violation generation, config
    option behavior, violation message formatting, and basic ignore integration.
"""

from pathlib import Path
from unittest.mock import patch

from src.linters.version_freshness.config import VersionFreshnessConfig
from src.linters.version_freshness.linter import (
    RULE_EOL,
    RULE_OUTDATED,
    VersionFreshnessRule,
)

# Sample Python lifecycle data
PYTHON_DATA = [
    {"cycle": "3.13", "eol": "2029-10-31"},
    {"cycle": "3.12", "eol": "2028-10-31"},
    {"cycle": "3.11", "eol": "2027-10-31"},
    {"cycle": "3.9", "eol": "2025-10-31"},
    {"cycle": "3.8", "eol": "2024-10-14"},
    {"cycle": "3.7", "eol": "2023-06-27"},
]


def _create_dockerfile(tmp_path: Path, content: str) -> Path:
    """Create a temporary Dockerfile."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text(content)
    return dockerfile


class TestVersionFreshnessRuleProperties:
    """Tests for rule properties."""

    def test_rule_id(self):
        """Should have correct rule ID."""
        rule = VersionFreshnessRule()
        assert rule.rule_id == "version-freshness"

    def test_rule_name(self):
        """Should have human-readable name."""
        rule = VersionFreshnessRule()
        assert rule.rule_name == "Version Freshness"

    def test_check_noop(self):
        """check() should be a no-op returning empty list."""
        rule = VersionFreshnessRule()
        assert rule.check(None) == []  # type: ignore[arg-type]


class TestVersionFreshnessEolDetection:
    """Tests for EOL version detection."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_detects_eol_version(self, mock_cache, tmp_path):
        """Should detect EOL Python version in Dockerfile."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = _create_dockerfile(tmp_path, "FROM python:3.7-slim\n")

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([dockerfile])

        assert len(violations) == 1
        assert violations[0].rule_id == RULE_EOL
        assert "3.7" in violations[0].message
        assert "end of life" in violations[0].message

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_no_violation_for_supported_version(self, mock_cache, tmp_path):
        """Should not flag supported version."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = _create_dockerfile(tmp_path, "FROM python:3.13-slim\n")

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([dockerfile])

        assert len(violations) == 0


class TestVersionFreshnessOutdatedDetection:
    """Tests for outdated version detection."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_detects_outdated_version(self, mock_cache, tmp_path):
        """Should detect outdated but supported version when check_outdated=True."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = _create_dockerfile(tmp_path, "FROM python:3.11-slim\n")

        config = VersionFreshnessConfig(check_eol=False, check_outdated=True)
        rule = VersionFreshnessRule(config)
        violations = rule.check_paths([dockerfile])

        assert len(violations) == 1
        assert violations[0].rule_id == RULE_OUTDATED
        assert "3.13" in violations[0].message

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_no_outdated_when_disabled(self, mock_cache, tmp_path):
        """Should not flag outdated when check_outdated=False (default)."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = _create_dockerfile(tmp_path, "FROM python:3.11-slim\n")

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_outdated=False))
        violations = rule.check_paths([dockerfile])

        assert len(violations) == 0


class TestVersionFreshnessConfig:
    """Tests for config behavior."""

    def test_disabled_linter_returns_empty(self, tmp_path):
        """Should return empty when linter is disabled."""
        dockerfile = _create_dockerfile(tmp_path, "FROM python:3.7-slim\n")
        rule = VersionFreshnessRule(VersionFreshnessConfig(enabled=False))
        violations = rule.check_paths([dockerfile])
        assert len(violations) == 0

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_cache_returns_none(self, mock_cache, tmp_path):
        """Should handle None from cache (no data available)."""
        mock_cache.return_value = None
        dockerfile = _create_dockerfile(tmp_path, "FROM python:3.7-slim\n")

        rule = VersionFreshnessRule()
        violations = rule.check_paths([dockerfile])
        assert len(violations) == 0


class TestVersionFreshnessDirectoryScan:
    """Tests for directory scanning."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_scans_directory(self, mock_cache, tmp_path):
        """Should scan directory and find versions in files."""
        mock_cache.return_value = PYTHON_DATA
        _create_dockerfile(tmp_path, "FROM python:3.7-slim\n")

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([tmp_path])

        assert len(violations) >= 1

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_handles_empty_directory(self, mock_cache, tmp_path):
        """Should handle empty directory."""
        mock_cache.return_value = PYTHON_DATA
        rule = VersionFreshnessRule()
        violations = rule.check_paths([tmp_path])
        assert len(violations) == 0


class TestVersionFreshnessViolationMessages:
    """Tests for violation message formatting."""

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_eol_violation_includes_date(self, mock_cache, tmp_path):
        """Should include EOL date in violation message."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = _create_dockerfile(tmp_path, "FROM python:3.7-slim\n")

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([dockerfile])

        assert len(violations) == 1
        assert "2023-06-27" in violations[0].message

    @patch("src.linters.version_freshness.linter.cache.get_product_data")
    def test_eol_violation_has_suggestion(self, mock_cache, tmp_path):
        """Should suggest upgrade in EOL violation."""
        mock_cache.return_value = PYTHON_DATA
        dockerfile = _create_dockerfile(tmp_path, "FROM python:3.7-slim\n")

        rule = VersionFreshnessRule(VersionFreshnessConfig(check_eol=True))
        violations = rule.check_paths([dockerfile])

        assert violations[0].suggestion is not None
        assert "3.13" in violations[0].suggestion
