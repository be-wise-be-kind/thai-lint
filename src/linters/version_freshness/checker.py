"""
Purpose: Check extracted versions against endoflife.date lifecycle data

Scope: EOL detection, outdated version detection, and version status reporting

Overview: Compares extracted version cycles against endoflife.date product data to determine
    if versions are end-of-life or outdated. Handles the polymorphic eol field from
    endoflife.date (boolean True or date string). Determines latest supported cycle for
    outdated detection. Returns structured VersionStatus results.

Dependencies: datetime, dataclasses, packaging.version

Exports: VersionStatus dataclass, check_version, find_cycle_data

Interfaces: check_version(extracted, product_data) -> VersionStatus

Implementation: Date comparison for EOL detection, cycle ordering for outdated detection
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from src.linters.version_freshness.product_mapper import ExtractedVersion, extract_cycle


@dataclass
class VersionStatus:
    """Result of checking a version against lifecycle data."""

    extracted: ExtractedVersion
    """The version that was checked."""

    is_eol: bool
    """Whether this version has reached end of life."""

    is_outdated: bool
    """Whether this version is supported but not the latest cycle."""

    eol_date: str | None
    """EOL date string if known, None otherwise."""

    latest_cycle: str | None
    """Latest supported cycle if known."""

    cycle: str
    """The cycle string that was matched."""


def check_version(extracted: ExtractedVersion, product_data: list[dict[str, Any]]) -> VersionStatus:
    """Check a version against endoflife.date product data.

    Args:
        extracted: The extracted version to check
        product_data: List of cycle dicts from endoflife.date

    Returns:
        VersionStatus with EOL and outdated information
    """
    cycle = extract_cycle(extracted.product, extracted.version)
    cycle_data = find_cycle_data(cycle, product_data)
    latest = _find_latest_supported_cycle(product_data)

    if cycle_data is None:
        return VersionStatus(
            extracted=extracted,
            is_eol=True,
            is_outdated=True,
            eol_date=None,
            latest_cycle=latest,
            cycle=cycle,
        )

    is_eol = _is_eol(cycle_data)
    eol_date = _get_eol_date_string(cycle_data)
    is_outdated = _is_outdated(cycle, latest)

    return VersionStatus(
        extracted=extracted,
        is_eol=is_eol,
        is_outdated=is_outdated,
        eol_date=eol_date,
        latest_cycle=latest,
        cycle=cycle,
    )


def find_cycle_data(cycle: str, product_data: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Find the cycle entry matching a version cycle.

    Args:
        cycle: Cycle string (e.g., "3.11", "18")
        product_data: List of cycle dicts from endoflife.date

    Returns:
        Matching cycle dict, or None if not found
    """
    for entry in product_data:
        entry_cycle = str(entry.get("cycle", ""))
        if entry_cycle == cycle:
            return entry
    return None


def _is_eol(cycle_data: dict[str, Any]) -> bool:
    """Determine if a cycle is end-of-life.

    Handles endoflife.date's polymorphic eol field:
    - boolean True means EOL
    - boolean False means still supported
    - date string means EOL after that date

    Args:
        cycle_data: Cycle dict from endoflife.date

    Returns:
        True if version is EOL
    """
    eol = cycle_data.get("eol")
    if isinstance(eol, bool):
        return eol
    if isinstance(eol, str):
        return _is_date_past(eol)
    return False


def _is_date_past(date_str: str) -> bool:
    """Check if a date string is in the past.

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        True if the date is before today
    """
    try:
        eol_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return eol_date < date.today()
    except ValueError:
        return False


def _get_eol_date_string(cycle_data: dict[str, Any]) -> str | None:
    """Extract EOL date as string from cycle data.

    Args:
        cycle_data: Cycle dict from endoflife.date

    Returns:
        EOL date string, or None if not a date
    """
    eol = cycle_data.get("eol")
    if isinstance(eol, str):
        return eol
    return None


def _find_latest_supported_cycle(product_data: list[dict[str, Any]]) -> str | None:
    """Find the latest cycle that is still supported.

    endoflife.date returns cycles ordered from newest to oldest,
    so the first non-EOL cycle is the latest supported.

    Args:
        product_data: List of cycle dicts from endoflife.date

    Returns:
        Latest supported cycle string, or None if all are EOL
    """
    for entry in product_data:
        if not _is_eol(entry):
            return str(entry.get("cycle", ""))
    return None


def _is_outdated(cycle: str, latest_cycle: str | None) -> bool:
    """Check if a cycle is outdated (not the latest supported).

    Args:
        cycle: The cycle to check
        latest_cycle: The latest supported cycle

    Returns:
        True if cycle is supported but not the latest
    """
    if latest_cycle is None:
        return False
    return cycle != latest_cycle
