"""
Purpose: Cache layer for endoflife.date API data

Scope: Fetching, caching, and serving product lifecycle data from endoflife.date

Overview: Manages local filesystem cache of endoflife.date API responses. Stores one JSON
    file per product under ~/.cache/thailint/endoflife/. Checks cache freshness against
    configurable TTL before fetching. Falls back to stale cache when offline. Uses deferred
    import of requests to avoid import-time overhead.

Dependencies: json, pathlib, time, logging, requests (deferred import)

Exports: get_product_data, get_cache_dir, is_cache_fresh

Interfaces: get_product_data(product, ttl_hours) -> list[dict] | None

Implementation: Pure functions with filesystem caching, no class needed. Deferred requests import.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_ENDOFLIFE_API_BASE = "https://endoflife.date/api"
_SECONDS_PER_HOUR = 3600
_DEFAULT_TTL_HOURS = 24


def get_cache_dir() -> Path:
    """Get the cache directory path.

    Returns:
        Path to ~/.cache/thailint/endoflife/
    """
    return Path.home() / ".cache" / "thailint" / "endoflife"


def is_cache_fresh(cache_path: Path, ttl_hours: int) -> bool:
    """Check if a cache file is still fresh.

    Args:
        cache_path: Path to the cache file
        ttl_hours: Maximum age in hours

    Returns:
        True if cache exists and is within TTL
    """
    if not cache_path.exists():
        return False
    age_seconds = time.time() - cache_path.stat().st_mtime
    return age_seconds < (ttl_hours * _SECONDS_PER_HOUR)


def get_product_data(
    product: str, ttl_hours: int = _DEFAULT_TTL_HOURS
) -> list[dict[str, Any]] | None:
    """Get lifecycle data for a product, using cache when possible.

    Fetches from endoflife.date API if cache is stale. Falls back to stale
    cache if the network request fails. Returns None if no data is available.

    Args:
        product: Product name on endoflife.date (e.g., "python", "nodejs")
        ttl_hours: Cache freshness threshold in hours

    Returns:
        List of cycle dicts from endoflife.date, or None if unavailable
    """
    cache_dir = get_cache_dir()
    cache_path = cache_dir / f"{product}.json"

    if is_cache_fresh(cache_path, ttl_hours):
        return _load_cache(cache_path)

    fetched = _fetch_from_api(product)
    if fetched is not None:
        _save_cache(cache_path, fetched)
        return fetched

    return _load_stale_cache(cache_path)


def _load_cache(cache_path: Path) -> list[dict[str, Any]] | None:
    """Load data from cache file.

    Args:
        cache_path: Path to cache JSON file

    Returns:
        Parsed JSON data, or None on error
    """
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError) as exc:
        logger.debug("Failed to load cache %s: %s", cache_path, exc)
    return None


def _load_stale_cache(cache_path: Path) -> list[dict[str, Any]] | None:
    """Load stale cache as fallback when API is unreachable.

    Args:
        cache_path: Path to cache JSON file

    Returns:
        Parsed JSON data, or None if no cache exists
    """
    if not cache_path.exists():
        return None
    logger.debug("Using stale cache for %s (API unreachable)", cache_path.stem)
    return _load_cache(cache_path)


def _fetch_from_api(product: str) -> list[dict[str, Any]] | None:
    """Fetch product data from endoflife.date API.

    Args:
        product: Product name on endoflife.date

    Returns:
        List of cycle dicts, or None on failure
    """
    import requests  # Deferred import to avoid import-time overhead

    url = f"{_ENDOFLIFE_API_BASE}/{product}.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
    except (requests.RequestException, ValueError) as exc:
        logger.debug("Failed to fetch %s: %s", url, exc)
    return None


def _save_cache(cache_path: Path, data: list[dict[str, Any]]) -> None:
    """Save data to cache file.

    Args:
        cache_path: Path to write cache JSON
        data: Data to cache
    """
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(data), encoding="utf-8")
    except OSError as exc:
        logger.debug("Failed to save cache %s: %s", cache_path, exc)
