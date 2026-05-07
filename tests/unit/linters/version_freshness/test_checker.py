"""
Purpose: Unit tests for version-freshness checker

Scope: EOL detection, outdated detection, unknown versions, polymorphic eol field

Overview: Tests the checker module that compares extracted versions against
    endoflife.date product data. Covers EOL detection with both date string
    and boolean eol fields, outdated version detection, unknown version handling,
    and cycle data lookup.
"""

from src.linters.version_freshness.checker import (
    VersionStatus,
    check_version,
    find_cycle_data,
)
from src.linters.version_freshness.product_mapper import ExtractedVersion

# Sample endoflife.date data for Python
PYTHON_DATA = [
    {"cycle": "3.13", "eol": "2029-10-31", "latest": "3.13.1"},
    {"cycle": "3.12", "eol": "2028-10-31", "latest": "3.12.7"},
    {"cycle": "3.11", "eol": "2027-10-31", "latest": "3.11.10"},
    {"cycle": "3.10", "eol": "2026-10-31", "latest": "3.10.15"},
    {"cycle": "3.9", "eol": "2025-10-31", "latest": "3.9.20"},
    {"cycle": "3.8", "eol": "2024-10-14", "latest": "3.8.20"},
    {"cycle": "3.7", "eol": "2023-06-27", "latest": "3.7.17"},
]

# Data with boolean eol field
BOOLEAN_EOL_DATA = [
    {"cycle": "2.0", "eol": False, "latest": "2.0.1"},
    {"cycle": "1.0", "eol": True, "latest": "1.0.5"},
]


def _make_extracted(product: str, version: str) -> ExtractedVersion:
    """Helper to create an ExtractedVersion."""
    return ExtractedVersion(
        product=product,
        version=version,
        file_path="Dockerfile",
        line=1,
        column=0,
        source="dockerfile",
    )


class TestFindCycleData:
    """Tests for cycle data lookup."""

    def test_finds_matching_cycle(self):
        """Should find cycle data by cycle string."""
        result = find_cycle_data("3.12", PYTHON_DATA)
        assert result is not None
        assert result["cycle"] == "3.12"

    def test_returns_none_for_unknown_cycle(self):
        """Should return None for cycle not in data."""
        result = find_cycle_data("2.7", PYTHON_DATA)
        assert result is None


class TestCheckVersionEol:
    """Tests for EOL detection."""

    def test_eol_by_past_date(self):
        """Should detect EOL when date is in the past."""
        extracted = _make_extracted("python", "3.7.17")
        status = check_version(extracted, PYTHON_DATA)
        assert status.is_eol is True
        assert status.eol_date == "2023-06-27"

    def test_not_eol_future_date(self):
        """Should not flag as EOL when date is in the future."""
        extracted = _make_extracted("python", "3.13.1")
        status = check_version(extracted, PYTHON_DATA)
        assert status.is_eol is False

    def test_eol_boolean_true(self):
        """Should detect EOL with boolean True."""
        extracted = _make_extracted("test", "1.0.5")
        # Use major-only cycle extraction for 'test' (not in major-only set)
        # cycle will be "1.0", matching the data
        status = check_version(extracted, BOOLEAN_EOL_DATA)
        assert status.is_eol is True

    def test_not_eol_boolean_false(self):
        """Should not flag as EOL with boolean False."""
        extracted = _make_extracted("test", "2.0.1")
        status = check_version(extracted, BOOLEAN_EOL_DATA)
        assert status.is_eol is False

    def test_unknown_version_treated_as_eol(self):
        """Should treat unknown versions as EOL."""
        extracted = _make_extracted("python", "2.7.18")
        status = check_version(extracted, PYTHON_DATA)
        assert status.is_eol is True
        assert status.eol_date is None


class TestCheckVersionOutdated:
    """Tests for outdated detection."""

    def test_outdated_supported_version(self):
        """Should flag supported but non-latest version as outdated."""
        extracted = _make_extracted("python", "3.11.10")
        status = check_version(extracted, PYTHON_DATA)
        assert status.is_outdated is True
        assert status.latest_cycle == "3.13"

    def test_latest_not_outdated(self):
        """Should not flag latest supported version."""
        extracted = _make_extracted("python", "3.13.1")
        status = check_version(extracted, PYTHON_DATA)
        assert status.is_outdated is False

    def test_eol_is_also_outdated(self):
        """Should mark EOL version as also outdated."""
        extracted = _make_extracted("python", "3.7.17")
        status = check_version(extracted, PYTHON_DATA)
        assert status.is_eol is True
        assert status.is_outdated is True


class TestVersionStatus:
    """Tests for VersionStatus dataclass."""

    def test_status_fields(self):
        """Should have all expected fields."""
        extracted = _make_extracted("python", "3.11")
        status = VersionStatus(
            extracted=extracted,
            is_eol=False,
            is_outdated=True,
            eol_date="2027-10-31",
            latest_cycle="3.13",
            cycle="3.11",
        )
        assert status.extracted is extracted
        assert status.is_eol is False
        assert status.is_outdated is True
        assert status.eol_date == "2027-10-31"
        assert status.latest_cycle == "3.13"
        assert status.cycle == "3.11"
